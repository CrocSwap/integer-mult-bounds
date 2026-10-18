#!/usr/bin/env python3
"""Exact receiver census for one frozen PR555/589 helper construction.

Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.
The construction formulas are adapted from eumemic's gen_p3.py; see NOTICE.md.
"""
import collections
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys

sys.dont_write_bytecode = True  # Preserve hash-inventoried predecessor packages.

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = '007664306fff84fbb1c9a1b4053b69f439764034'
REQUIRED = tuple(sorted([
    'research/e8-bit-carrier-skeleton/code/skeleton/' + name
    for name in ('e8.py', 'gen.py', 'geom.py', 'wordkit.py')
] + [
    'research/e8-bit-p111-tuned/code/' + name
    for name in ('gen_p3.py', 'nodeopt.py', 'planio.py', 'pwordl.py')
] + [
    'research/e8-bit-carrier-skeleton/data/skeleton/d4part-pairs.json',
    'research/e8-bit-p111-tuned/data/plan-l3.json',
    'research/e8-bit-p111-tuned/data/punct.json',
    'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz',
]))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def check_sources(root=ROOT, here=HERE):
    manifest = json.loads((here / 'SOURCES.json').read_text())
    need(manifest['base_commit'] == BASE, 'wrong source base')
    need(sorted(row['path'] for row in manifest['files']) == list(REQUIRED),
         'missing, duplicate or unexpected source pin')
    for row in manifest['files']:
        data = (root / row['path']).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row['sha256'], 'source SHA256: ' + row['path'])
        blob = b'blob ' + str(len(data)).encode() + b'\0' + data
        need(hashlib.sha1(blob).hexdigest() == row['git_blob'], 'source Git blob: ' + row['path'])


def echelon(vectors):
    basis = {}
    for value in vectors:
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
    return basis


def residual(value, vectors):
    basis = echelon(vectors)
    for pivot in sorted(basis, reverse=True):
        if value >> pivot & 1:
            value ^= basis[pivot]
    return value


def junk_count(targets, rank, reusable):
    need(0 <= rank <= targets and reusable >= 0, 'invalid rank or reuse count')
    return max(0, targets - rank - reusable)


class Model:
    def __init__(self):
        # Source checks precede the import of every predecessor implementation.
        check_sources()
        sys.path.insert(0, str(ROOT / 'research/e8-bit-p111-tuned/code'))
        import gen_p3 as gen
        self.gen = gen
        self.G = G = gen.Geom()
        self.sol = sol = gen.load_plan(ROOT / 'research/e8-bit-p111-tuned/data/plan-l3.json')
        self.params = json.loads((ROOT / 'research/e8-bit-p111-tuned/data/punct.json').read_text())
        self.P = P = self.params['punctured']
        need(P == [10, 15, 51, 53, 56, 66, 72, 89, 111], 'wrong puncture set')
        self.live = live = ((1 << 120) - 1) ^ sum(1 << p for p in P)
        self.freeline, self.thirds = gen.plan_thirds(G, sol, random.Random(self.params['thirds_seed']))
        self.dcell, self.keep, self.home, self.qhost, self.zz = gen.derive(G, sol, self.freeline)
        self.ex = {H: (gen.ex_part(G, sol, G.d6quads[H][0], H)
                       ^ gen.ex_part(G, sol, G.d6quads[H][1], H)) & live for H in G.cells}
        self.hyp = [int(x) for x in gen.e8.HYP]
        self.zzp = {p: sorted(H for H in self.zz if G.phi[H[0]] == G.phi[p]) for p in P}
        need(len({G.phi[p] for p in P}) == 9, 'receiver frames overlap')
        need(all(len(hs) == 2 and all(p in H for H in hs) for p, hs in self.zzp.items()),
             'receiver domain is not nine independent pairs')
        branch, helper = {}, 240
        for source in range(120):
            for cell in G.cells_of[source]:
                if cell == self.home[source]:
                    branch[source, cell] = source if live >> source & 1 else None
                else:
                    branch[source, cell] = helper
                    helper += 1
        need(helper == 480, 'fixed carrier count changed')
        self.fk = {H: branch[self.keep[self.thirds[H]], self.thirds[H]] for H in self.zz}
        self.initial = {self.fk[H]: (1 << self.keep[self.thirds[H]]) & live for H in self.zz}
        self.groups = {b: [p for p in P if G.comp[G.blk[p]] == b] for b in range(10)}
        self.baseline = [self.params['receivers'][str(p)] for p in P]

    def local(self, block, masks):
        G, P, live = self.G, self.P, self.live
        ps, complement = self.groups[block], G.comp[block]
        need(len(masks) == len(ps) and all(type(x) is int and 1 <= x <= 3 for x in masks),
             'invalid receiver vector')
        receiver = dict(self.sol['rcv'])
        for p, choice in zip(ps, masks):
            for i, H in enumerate(self.zzp[p]):
                receiver[H] = p if choice >> i & 1 else (H[0] if H[1] == p else H[1])
        keepers = sorted({self.fk[H] for H in self.zz if G.cblk[H] == complement})
        freed = [self.keep[self.dcell[q]] for q in P
                 if G.blk[q] == block and live >> self.keep[self.dcell[q]] & 1]
        extras, rounds = [], 0
        while True:
            rounds += 1
            content = {w: self.initial[w] for w in keepers}
            # These identifiers preserve the original relative carrier/source order.
            extra_wires = {s: 1000 + s for s in extras}
            content.update({extra_wires[s]: 1 << s for s in extras})
            content.update({s: 1 << s for s in freed})
            wires = keepers + [extra_wires[s] for s in extras] + freed
            missing = 0
            for p in ps:
                wanted = (self.hyp[p] & live) ^ (1 << self.keep[self.dcell[p]]) ^ self.ex[self.qhost[p]]
                for H in self.zzp[p]:
                    wanted ^= self.ex[H]
                mine = [H for H in self.zzp[p] if receiver[H] == p]
                destination = self.fk[mine[0]]
                for H in mine[1:]:
                    wanted ^= self.initial[self.fk[H]]
                remainder = residual(wanted ^ content[destination],
                                     [content[w] for w in wires if w != destination])
                if remainder:
                    missing |= remainder  # A failed predecessor write is skipped.
                else:
                    content[destination] = wanted
            if not missing:
                break
            new = sorted(set(extras) | {i for i in range(120) if missing >> i & 1})
            need(new != extras and rounds < 20, 'missing-carrier closure did not finish')
            extras = new
        targets = [t for t in range(120) if G.blk[t] == complement and live >> t & 1]
        needs = []
        for t in targets:
            value = self.hyp[t] & live
            line = self.keep[self.dcell[t]]
            if live >> line & 1:
                value ^= 1 << line
            for x in G.phi[t]:
                if x == t:
                    continue
                H = tuple(sorted((t, x)))
                value ^= self.ex[H]
                if H in receiver and receiver[H] == t:
                    value ^= content[self.fk[H]]
            need(value & ~(G.blocks[block] & live) == 0, 'delivery escapes its supplying block')
            needs.append(value)
        dual = set(self.home.values())
        sources = [self.keep[c] for c in G.cells if c in dual and G.cblk[c] == block
                   and live >> self.keep[c] & 1]
        reusable = sum(s in sources for s in extras)
        rank = len(echelon(needs))
        junk = junk_count(len(needs), rank, reusable)
        return dict(block=block, receivers=list(masks), extras=extras, junk=junk, rank=rank,
                    target_count=len(needs), reusable_extras=reusable, cost=len(extras) + junk,
                    closure_rounds=rounds, needs=[hex(n) for n in needs])

    def census(self):
        tables = {b: [self.local(b, masks) for masks in itertools.product((1, 2, 3),
                  repeat=len(self.groups[b]))] for b in range(10)}
        lookup = {b: {tuple(row['receivers']): row for row in tables[b]} for b in tables}
        histogram, digest = collections.Counter(), hashlib.sha256()
        minimum, minimizers, baseline = 999, 0, None
        for masks in itertools.product((1, 2, 3), repeat=9):
            selection = dict(zip(self.P, masks))
            rows = [lookup[b][tuple(selection[p] for p in self.groups[b])] for b in range(10)]
            extra, junk = sum(len(r['extras']) for r in rows), sum(r['junk'] for r in rows)
            total = 429 + extra + junk
            record = [list(masks), total, extra, junk,
                      [[b, row['extras']] for b, row in enumerate(rows) if row['extras']],
                      [row['rank'] for row in rows]]
            digest.update((json.dumps(record, separators=(',', ':')) + '\n').encode())
            histogram[total] += 1
            if total < minimum:
                minimum, minimizers = total, 0
            if total == minimum:
                minimizers += 1
            if list(masks) == self.baseline:
                baseline = record
        shipped = json.loads(gzip.decompress((ROOT / 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz').read_bytes()))
        need(shipped['R'] == baseline[1] and shipped['v'] == 111, 'selected word calibration failed')
        return dict(case_count=sum(histogram.values()), record_sha256=digest.hexdigest(),
                    minimum_R=minimum, minimizers=minimizers, histogram=dict(sorted(histogram.items())),
                    baseline=baseline, groups=self.groups, local_tables=tables)


def main():
    need(__debug__, 'ordinary Python required: pinned predecessor setup uses assertions; omit -O')
    actual = Model().census()
    expected = json.loads((HERE / 'EXPECTED.json').read_text())
    need(canonical(actual) == canonical(expected), 'complete census receipt mismatch')
    print('PASS_P111_RECEIVER_CENSUS cases=19683 local_rows=60 min_helpers=439 minimizers=2646 no_new_kappa')


if __name__ == '__main__':
    main()
