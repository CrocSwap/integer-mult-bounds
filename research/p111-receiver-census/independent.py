#!/usr/bin/env python3
"""Independent set-valued receiver census, frozen PR555 geometry/thirds.

Prepared for ToikY with substantial OpenAI Codex assistance; Apache-2.0.
Credits eumemic's PR555 generator and its retained construction lineage.
Shares geometry and frozen plan_thirds setup with the historical generator,
but implements source-form propagation and F2 linear algebra independently.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys

sys.dont_write_bytecode = True  # Preserve hash-inventoried predecessor packages.
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def check_sources():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    if manifest['base_commit'] != '007664306fff84fbb1c9a1b4053b69f439764034':
        raise RuntimeError('unexpected source base')
    required = {'research/e8-bit-p111-tuned/' + p for p in
                ('code/gen_p3.py', 'code/pwordl.py', 'code/planio.py', 'code/nodeopt.py',
                 'data/plan-l3.json', 'data/punct.json', 'tune/bitE8mut-p111-tuned.json.gz')}
    required |= {'research/e8-bit-carrier-skeleton/code/skeleton/' + p
                 for p in ('e8.py', 'geom.py', 'gen.py', 'wordkit.py')}
    required.add('research/e8-bit-carrier-skeleton/data/skeleton/d4part-pairs.json')
    paths = [item['path'] for item in manifest['files']]
    if len(paths) != len(set(paths)) or required != set(paths):
        raise RuntimeError('duplicate, missing, or unexpected source pin')
    for item in manifest['files']:
        path = ROOT / item['path']
        path.resolve().relative_to(ROOT.resolve())
        payload = path.read_bytes()
        blob = b'blob ' + str(len(payload)).encode() + b'\0' + payload
        if (hashlib.sha256(payload).hexdigest() != item['sha256'] or
                hashlib.sha1(blob).hexdigest() != item['git_blob']):
            raise RuntimeError('source pin mismatch: ' + item['path'])


def reduce_row(row, pivots):
    row = set(row)
    for pivot in sorted(pivots, reverse=True):
        if pivot in row:
            row.symmetric_difference_update(pivots[pivot])
    return frozenset(row)


def make_span(rows):
    pivots = {}
    for row in rows:
        residual = reduce_row(row, pivots)
        if residual:
            pivots[max(residual)] = residual
    return pivots


class Census:
    def __init__(self, repo):
        self.repo = Path(repo)
        self.data = self.repo / 'research/e8-bit-p111-tuned/data'
        code = self.repo / 'research/e8-bit-p111-tuned/code'
        sys.path.insert(0, str(code))
        import gen_p3
        self.gen = gen_p3
        self.g = g = gen_p3.Geom()
        self.sol = sol = gen_p3.load_plan(str(self.data / 'plan-l3.json'))
        self.prm = json.loads((self.data / 'punct.json').read_text())
        self.ps = tuple(sorted(self.prm['punctured']))
        self.live = frozenset(range(120)) - set(self.ps)
        fl, self.assign = gen_p3.plan_thirds(g, sol, random.Random(self.prm['thirds_seed']))
        self.freeline = fl
        self.dcell = {}
        self.keepline = {}
        self.home = {}
        self.host = {}
        for f in g.frames4:
            for t in f:
                c = tuple(sorted(set(f) - {t, sol['partner'][t]}))
                self.dcell[t] = c
                self.keepline[c] = sol['kline'][t]
                self.home[sol['kline'][t]] = c
                self.host[t] = tuple(sorted((t, sol['qhost'][t])))
            for c in itertools.combinations(f, 2):
                if c not in self.keepline:
                    self.keepline[c] = c[fl.get(c, 0)]
        self.zz = tuple(c for c in g.cells if c not in set(self.host.values()))
        self.zzp = {p: tuple(sorted(c for c in self.zz if g.phi[c[0]] == g.phi[p])) for p in self.ps}
        # Reproduce stable branch identifiers: their numeric ordering affects
        # the generator's residual-carrier selection, although not span rank.
        branch = {}
        next_wire = 240
        for s in range(120):
            for c in g.cells_of[s]:
                if c == self.home[s]:
                    branch[s, c] = s if s in self.live else None
                else:
                    branch[s, c] = next_wire
                    next_wire += 1
        assert next_wire == 480
        self.keepers = {c: branch[self.keepline[c], c] for c in g.cells}
        self.original = {w: frozenset({self.keepline[c]}) & self.live
                         for c, w in self.keepers.items() if w is not None}
        self.fk = {h: self.keepers[self.assign[h]] for h in self.zz}
        self.ex = {}
        for h in g.cells:
            e = frozenset()
            for q in g.d6quads[h]:
                all_lines = frozenset(x for c in g.qcells[q] for x in c)
                d, qc = frozenset(g.dcell[h]), frozenset(g.qcell[q, h])
                extra = {'D': d, 'Q': qc, '0': frozenset()}[sol['ext'][q, h]]
                e ^= all_lines ^ d ^ qc ^ extra
            self.ex[h] = e & self.live
        self.hyp = {t: frozenset(gen_p3.e8.bits(gen_p3.e8.HYP[t])) & self.live for t in range(120)}
        self.taub = {b: tuple(p for p in self.ps if g.comp[g.blk[p]] == b) for b in range(10)}
        self.free_wires = {b: tuple(sorted({self.fk[h] for h in self.zz if g.cblk[h] == g.comp[b]})) for b in range(10)}
        self.freed = {b: tuple(self.keepline[self.dcell[q]] for q in self.ps
                              if g.blk[q] == b and self.keepline[self.dcell[q]] in self.live) for b in range(10)}
        self.src = {b: frozenset(self.keepline[c] for c in g.cells
                                if c in set(self.home.values()) and g.cblk[c] == b
                                and self.keepers[c] is not None and self.keepline[c] in self.live)
                    for b in range(10)}
        self.targets = {b: tuple(t for t in sorted(self.live) if g.blk[t] == g.comp[b]) for b in range(10)}

    def evaluate(self, masks):
        g = self.g
        rcv = dict(self.sol['rcv'])
        for p, mask in zip(self.ps, masks):
            for i, h in enumerate(self.zzp[p]):
                rcv[h] = p if mask & (1 << i) else next(t for t in h if t != p)
        extras = {b: set() for b in range(10)}
        for iteration in range(20):
            rewritten = dict(self.original)
            missing = {b: set() for b in range(10)}
            for b in range(10):
                if not self.taub[b]:
                    continue
                # Extra-carrier identity is distinct from its source line.
                wires = list(self.free_wires[b]) + [('extra', s) for s in sorted(extras[b])] + list(self.freed[b])
                cont = {w: (frozenset({w[1]}) if isinstance(w, tuple)
                            else self.original.get(w, frozenset({w}))) for w in wires}
                planned = []
                for p in self.taub[b]:
                    lp = self.keepline[self.dcell[p]]
                    wanted = self.hyp[p] ^ {lp} ^ self.ex[self.host[p]]
                    for h in self.zzp[p]:
                        wanted ^= self.ex[h]
                    mine = [h for h in self.zzp[p] if rcv[h] == p]
                    for h in mine[1:]:
                        wanted ^= self.original[self.fk[h]]
                    planned.append((self.fk[mine[0]], wanted))
                for dest, wanted in planned:
                    span = make_span(cont[w] for w in wires if w != dest)
                    residual = reduce_row(wanted ^ cont[dest], span)
                    if residual:
                        missing[b].update(residual)
                    else:
                        cont[dest] = wanted
                        rewritten[dest] = wanted
            if not any(missing.values()):
                break
            for b in range(10):
                extras[b].update(missing[b])
        else:
            raise RuntimeError('historical 20-pass carrier rule did not terminate')
        rank = []
        deficits = []
        junk = []
        for b in range(10):
            forms = []
            for t in self.targets[b]:
                wanted = self.hyp[t]
                c = self.dcell[t]
                if self.keepers[c] is not None and self.keepline[c] in self.live:
                    wanted ^= self.original[self.keepers[c]]
                for x in g.phi[t]:
                    if x == t:
                        continue
                    h = tuple(sorted((t, x)))
                    wanted ^= self.ex[h]
                    if h in self.fk and rcv[h] == t:
                        wanted ^= rewritten[self.fk[h]]
                if not wanted <= self.src[b]:
                    raise RuntimeError(('Q need outside live source block', b, t, sorted(wanted - self.src[b])))
                forms.append(wanted)
            r = len(make_span(forms))
            deficit = len(forms) - r
            reusable = len(extras[b] & self.src[b])
            rank.append(r)
            deficits.append(deficit)
            junk.append(max(0, deficit - reusable))
        nextra, njunk = sum(map(len, extras.values())), sum(junk)
        return {'masks': list(masks), 'R': 429 + nextra + njunk,
                'extra_carriers': nextra, 'junk_wires': njunk,
                'extras': [[b, sorted(extras[b])] for b in range(10) if extras[b]],
                'ranks': rank, 'deficits': deficits, 'passes': iteration + 1}

    def direct_check(self, masks):
        expected = self.evaluate(masks)
        gen = self.gen
        gen.NODEOPT[0] = 1
        extras = {}
        for _ in range(20):
            result = gen.build(self.g, self.sol, self.ps, self.freeline, self.assign,
                               extras=extras, verbose=False, rcvsel=dict(zip(self.ps, masks)))
            if result[0] != 'missing':
                break
            for b, ls in result[1].items():
                extras[b] = sorted(set(extras.get(b, [])) | set(ls))
        else:
            raise RuntimeError('direct build did not finish')
        word = result[1]
        actual = (word['R'], word['stats']['extra_carriers'], word['stats']['junk_wires'],
                  [[b, ls] for b, ls in sorted(extras.items())])
        wanted = (expected['R'], expected['extra_carriers'], expected['junk_wires'], expected['extras'])
        if actual != wanted:
            raise RuntimeError(('direct comparison failure', masks, wanted, actual))
        return expected


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output')
    args = p.parse_args()
    if not __debug__:
        raise SystemExit('Run without -O: inherited generator setup and direct controls use assertions.')
    check_sources()
    start = time.monotonic()
    census = Census(ROOT)
    controls = [(1,) * 9, (2,) * 9, (3,) * 9,
                tuple(census.prm['receivers'][str(x)] for x in census.ps),
                tuple(random.Random(15 + i).choice((1, 2, 3)) for i in range(9))]
    for masks in controls:
        census.direct_check(masks)
    direct_count = len(controls)
    for ps in census.taub.values():
        if not ps:
            continue
        for combo in itertools.product((1, 2, 3), repeat=len(ps)):
            masks = [1] * 9
            for puncture, mask in zip(ps, combo):
                masks[census.ps.index(puncture)] = mask
            census.direct_check(tuple(masks))
            direct_count += 1
    digest = hashlib.sha256()
    histogram, best = {}, None
    out = open(args.output, 'w') if args.output else None
    try:
        for masks in itertools.product((1, 2, 3), repeat=9):
            record = census.evaluate(masks)
            wire_record = [record['masks'], record['R'], record['extra_carriers'], record['junk_wires'], record['extras'], record['ranks']]
            line = json.dumps(wire_record, separators=(',', ':')) + '\n'
            digest.update(line.encode())
            if out:
                out.write(line)
            r = record['R']
            histogram[r] = histogram.get(r, 0) + 1
            if best is None or r < best['R']:
                best = record
    finally:
        if out:
            out.close()
    baseline = census.evaluate(controls[3])
    baseline_record = [baseline['masks'], baseline['R'], baseline['extra_carriers'],
                       baseline['junk_wires'], baseline['extras'], baseline['ranks']]
    receipt = {'case_count': sum(histogram.values()), 'record_sha256': digest.hexdigest(),
               'minimum_R': min(histogram), 'minimizers': histogram[min(histogram)],
               'histogram': {str(k): v for k, v in sorted(histogram.items())},
               'baseline': baseline_record}
    expected = json.loads((HERE / 'EXPECTED.json').read_text())
    actual_json = json.dumps(receipt, sort_keys=True, separators=(',', ':'))
    expected_json = json.dumps({k: expected[k] for k in receipt}, sort_keys=True, separators=(',', ':'))
    if actual_json != expected_json:
        raise RuntimeError('independent receipt mismatch: ' + actual_json)
    print('PASS_INDEPENDENT_RECEIVER_CENSUS', actual_json,
          'original_full_word_controls=' + str(direct_count),
          'elapsed_s=' + str(round(time.monotonic() - start, 3)))


if __name__ == '__main__':
    main()
