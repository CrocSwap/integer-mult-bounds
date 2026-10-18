#!/usr/bin/env python3
"""Independent integer-bitset replay of pinned complete-word rewrites.

Prepared by ToikY with substantial OpenAI Codex assistance; Apache-2.0.
Does not import the discovery implementation. Source formula/interface checks
follow the credited PR1122 verifier; formal-column replay is independent.
"""
import argparse
import ast
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = '1b59b624d21924f8e3537cdc1ac52d3be6eda2fe'
CHECKER = 'research/e8-bit-p111-tuned/code/xcheck_p.py'
FORMULA = ('research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/'
           'vendor/e8-r715-eleven-stage-whole/code/global_k.py')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def same(a, b, message):
    need(canonical(a) == canonical(b), message)


def pairs(items):
    out = {}
    for key, value in items:
        need(key not in out, 'duplicate key ' + key)
        out[key] = value
    return out


def invalid(value):
    raise ValueError('nonfinite JSON ' + value)


def load(path):
    raw = Path(path).read_bytes()
    if str(path).endswith('.gz'):
        raw = gzip.decompress(raw)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


def write(path, value):
    Path(path).write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n')


def pins():
    manifest = load(HERE / 'SOURCES.json')
    need(manifest['base_commit'] == BASE, 'base pin')
    for directory, key in ((ROOT, 'repository_files'), (HERE, 'package_sources')):
        for name, expected in manifest[key].items():
            need(hashlib.sha256((directory / name).read_bytes()).hexdigest() == expected,
                 'source pin ' + name)
    need(hashlib.sha256((ROOT / 'research/community-frontier1094-audit/ASSEMBLY.json').read_bytes()).hexdigest()
         == manifest['selected_certificate_sha256'], 'selected certificate pin')
    syntax = ast.parse((ROOT / FORMULA).read_text())
    target = ast.parse('(1 << nb) * cf ** (K + 1) * cb ** K', mode='eval').body
    formulas = [n.value for n in ast.walk(syntax) if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == 'prefix' for t in n.targets)]
    need(len(formulas) == 1 and ast.dump(formulas[0]) == ast.dump(target), 'prefix formula')
    bridge = ast.parse('nb == 6 * (K - 1)', mode='eval').body
    need(any(isinstance(n, ast.Compare) and ast.dump(n) == ast.dump(bridge)
             for n in ast.walk(syntax)), 'bridge exponent')
    need(load(ROOT / 'research/e8-bit-p111-tuned/tune/EXPECTED.json')['nine']['bit']
         ['charged_prefix_bits'] == 192, 'nine precision charge')
    return manifest


def stream(word):
    n, v = 2 * word['v'] + word['R'], word['v']
    result = []
    for phase in ('D', 'A', 'scatter', 'B', 'C'):
        if phase == 'scatter':
            need(len(word['ret']) == 9, 'nine centers')
            for j, center in enumerate(word['ret']):
                need(type(center) is int and 0 <= center < n, 'center domain')
                result.append(('copy', n, center))
                for i, uses in enumerate(word['scatter']):
                    need(len(set(uses)) == len(uses) and all(type(k) is int and 0 <= k < 9 for k in uses),
                         'scatter domain')
                    if j in uses:
                        result.append(('add', v + i, n))
                result.append(('erase', n, center))
        else:
            for f, d, donors in word[phase]:
                need(type(f) is int and 0 <= f < len(word['frames']), 'frame domain')
                need(type(d) is int and 0 <= d < n, 'destination domain')
                need(type(donors) is list and len(set(donors)) == len(donors), 'distinct donors')
                need(all(type(s) is int and 0 <= s < n and s != d for s in donors), 'donor domain')
                result.extend(('add', d, s) for s in donors)
    return result


def execute(word, reverse=False, records=None):
    n, v = 2 * word['v'] + word['R'], word['v']
    rows, bound = [1 << i for i in range(n)] + [0], [1] * n + [0]
    records = stream(word) if records is None else records
    active, peak, adds, copies, erasures = False, 1, 0, 0, 0
    for kind, d, s in reversed(records) if reverse else records:
        if reverse and kind != 'add':
            kind = 'erase' if kind == 'copy' else 'copy'
        if kind == 'add':
            need(d < n and (s != n or active), 'private COPY lifetime')
            rows[d] ^= rows[s]
            bound[d] += bound[s]
            adds += 1
        elif kind == 'copy':
            need(d == n and not active and rows[n] == bound[n] == 0, 'COPY not empty')
            rows[n], bound[n], active = rows[s], bound[s], True
            copies += 1
        elif kind == 'erase':
            need(d == n and active and rows[n] == rows[s], 'ERASE original')
            rows[n], bound[n], active = 0, 0, False
            erasures += 1
        else:
            raise ValueError('instruction kind')
        peak = max(peak, bound[d])
    expected = [1 << i for i in range(n)]
    for i in range(v):
        expected[v + i] ^= 1 << i
    need(rows[:-1] == expected, 'dirty endpoint')
    need(not active and rows[n] == bound[n] == 0 and copies == erasures == 9, 'complete COPY bill')
    return dict(ADDs=adds, bound=peak, columns=n, copies=copies, erasures=erasures)


def admission(p):
    need(int(p['local_upper']) < 2**104, 'local precision cap')
    need(int(p['nine_upper']) < 2**192, 'nine precision cap')


def price(word):
    f, b = execute(word), execute(word, True)
    need(f['ADDs'] == b['ADDs'], 'reverse bill')
    F, B = f['bound'], b['bound']
    local, nine = 2**6 * F**3 * B**2, 2**18 * F**5 * B**4
    return dict(ADDs=f['ADDs'], F=F, B=B, local_upper=str(local), nine_upper=str(nine),
                local_bits=local.bit_length(), nine_bits=nine.bit_length(),
                admitted=local < 2**104 and nine < 2**192)


def cleanup(word):
    full = [i for i, f in enumerate(word['frames']) if sorted(f) == list(range(word['v']))]
    need(len(full) == 1, 'unique full frame')
    return [[full[0], d, list(ss)] for phase in ('B', 'A')
            for _, d, ss in reversed(word[phase]) if not word['v'] <= d < 2 * word['v']]


def phase_map(word, phase):
    rows = [1 << i for i in range(2 * word['v'] + word['R'])]
    if phase == 'scatter':
        for i, uses in enumerate(word['scatter']):
            for j in uses:
                rows[word['v'] + i] ^= 1 << word['ret'][j]
    else:
        for _, d, ss in word[phase]:
            for s in ss:
                rows[d] ^= rows[s]
    return rows


def replay_moves(base, moves):
    word = copy.deepcopy(base)
    v = word['v']
    for m in moves:
        need(m['sec'] in ('A', 'B'), 'rewrite section')
        a, b, x = (m[k] for k in ('a', 'b', 'x'))
        need(len({a, b, x}) == 3 and all(type(t) is int and (0 <= t < v or 2*v <= t < 2*v+word['R'])
                                        for t in (a, b, x)), 'rewrite roles')
        gates = word[m['sec']]
        chosen = []
        for label, d, s in (('bx', b, x), ('ba', b, a), ('ax', a, x)):
            matches = [i for i, g in enumerate(gates) if g == m['g_' + label]]
            occ = m['occ_' + label]
            need(type(occ) is int and 0 <= occ < len(matches), 'rewrite occurrence')
            index = matches[occ]
            need(gates[index][1] == d and s in gates[index][2], 'rewrite edge')
            chosen.append((index, gates[index], s))
        need(len({g[0] for _, g, _ in chosen}) == 1, 'triangle common frame')
        edges = []
        for i, (_, d, ss) in enumerate(gates):
            edges.extend((i, d, s) for s in ss)
        positions = [edges.index((i, g[1], s)) for i, g, s in chosen]
        lo, hi = min(positions), max(positions)
        def commutes(d, s, e, t):
            return d == e or (d != t and e != s)
        for j in range(lo + 1, hi):
            if j not in positions:
                _, d, s = edges[j]
                need(all(commutes(d, s, e, t) for e, t in ((b,x), (b,a), (a,x))), 'noncommuting window')
        need(m['mapA'] is (positions[1] < positions[2]), 'rewrite order')
        # All accepted moves here stay in one physical frame, including every
        # whole gate crossed when extracting a member of a donor group.
        i0, i1 = sorted((chosen[1][0], chosen[2][0]))
        need(all(g[0] == chosen[2][1][0] for g in gates[i0:i1+1]), 'cross-frame rewrite')
        bx, ba, ax = [g for _, g, _ in chosen]
        bx[2].remove(x)
        if not bx[2]:
            gates.pop(next(i for i, g in enumerate(gates) if g is bx))
        ax[2].remove(x)
        if not ax[2]:
            gates.pop(next(i for i, g in enumerate(gates) if g is ax))
        anchor = next(i for i, g in enumerate(gates) if g is ba)
        gates.insert(anchor if m['mapA'] else anchor + 1, [ax[0], a, [x]])
        word['C'] = cleanup(word)
    return word


def owning(base, candidate):
    spec = importlib.util.spec_from_file_location('seed16_owning', ROOT / CHECKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    first = mod.Word(base)
    labels = first.labels()
    reports = {}
    for name, word in (('baseline', base), ('candidate', candidate)):
        current = copy.copy(first)
        current.w = word
        full, totals = current.full(), current.totals()
        h, k, _ = current.interface()
        need(full['columns'] == 661 and [t['rank'] for t in totals] == [7]*9, 'owning coverage')
        need(all(t['hyperplane_of_punctured_line'] for t in totals), 'total geometry')
        need(all(value is (key != 'H2_D_frame0_targets_from_helpers') for key,value in h.items()), 'owning H')
        need(all(value is (key != 'K_equals_D') for key,value in k.items()), 'owning K')
        reports[name] = dict(full=full, totals=totals, hypotheses=h, conclusions=k)
    for key in ('totals', 'hypotheses', 'conclusions'):
        same(reports['baseline'][key], reports['candidate'][key], 'owning contract unchanged ' + key)
    return dict(labels=labels, words=reports)


def controls(base, candidate, moves):
    rejected = []
    def reject(name, fn):
        try:
            fn()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('control accepted: ' + name)
    bad = copy.deepcopy(moves)
    bad[0]['mapA'] = not bad[0]['mapA']
    reject('wrong retained-edge order', lambda: replay_moves(base, bad))
    bad = copy.deepcopy(moves)
    bad[0]['occ_bx'] = 1000000
    reject('wrong duplicate occurrence', lambda: replay_moves(base, bad))
    bad_base = copy.deepcopy(base)
    first = moves[0]
    i = min(first['index_bx'], first['index_ba'], first['index_ax']) + 1
    bad_base[first['sec']].insert(i, [first['g_ax'][0], first['x'], [first['b']]])
    reject('intervening noncommuting gate', lambda: replay_moves(bad_base, moves))
    bad = copy.deepcopy(candidate)
    bad['C'] = base['C']
    execute(bad)  # The predecessor inverse remains semantically exact.
    reject('semantically exact stale literal cleanup', lambda: same(bad['C'], cleanup(bad), 'literal cleanup'))
    records = stream(candidate)
    for kind in ('copy', 'erase'):
        index = next(i for i, row in enumerate(records) if row[0] == kind)
        reject('omitted ' + kind, lambda i=index: execute(candidate, records=records[:i]+records[i+1:]))
    bad = copy.deepcopy(candidate)
    del bad['D'][0]
    reject('omitted paid D gate', lambda: execute(bad))
    bad = copy.deepcopy(candidate)
    bad['A'][0][0] = True
    reject('boolean frame ID', lambda: execute(bad))
    for field, cap in (('local_upper',104), ('nine_upper',192)):
        bad = price(candidate)
        bad[field] = str(1 << cap)
        reject('strict cap equality ' + field, lambda p=bad: admission(p))
    reject('duplicate JSON key', lambda: json.loads('{"a":1,"a":2}', object_pairs_hook=pairs))
    return rejected


def run():
    pins()
    base = load(HERE / 'vendor/pr1122/candidate.json.gz')
    candidate = load(HERE / 'CANDIDATE-WORD.json')
    witness = load(HERE / 'MOVES.json')
    same(replay_moves(base, witness['moves']), candidate, 'independent witness reconstruction')
    need((candidate['v'], candidate['R']) == (111,439), 'dimensions')
    same(sorted(base), sorted(candidate), 'payload keys')
    for key in base:
        if key not in ('A','B','C'):
            same(base[key], candidate[key], 'unchanged ' + key)
    maps = {}
    for phase in ('D','A','scatter','B','C'):
        same(phase_map(base,phase),phase_map(candidate,phase), 'phase map ' + phase)
        maps[phase] = digest(phase_map(candidate,phase))
    same(candidate['C'], cleanup(candidate), 'literal cleanup')
    prices = {name: price(word) for name,word in (('baseline',base),('candidate',candidate))}
    for p in prices.values():
        admission(p)
    need(prices['baseline']['ADDs']-prices['candidate']['ADDs'] == 2*len(witness['moves']), 'complete saving')
    concurrent = load(HERE / 'vendor/pr1188/candidate.json.gz')
    concurrent_price = price(concurrent)
    admission(concurrent_price)
    comparison = dict(pr1188_head=load(HERE / 'SOURCES.json')['predecessor_heads']['1188_comparison'],
                      canonical_word_sha256=digest(concurrent), price=concurrent_price,
                      scope='Independent complete literal endpoints and precision invoice; no GL5 optimality or native replay claimed here')
    need(prices['candidate']['ADDs'] > concurrent_price['ADDs'], 'concurrent circuit has fewer ADDs')
    need(int(prices['candidate']['local_upper']) < int(concurrent_price['local_upper'])
         and int(prices['candidate']['nine_upper']) < int(concurrent_price['nine_upper']), 'distinct precision tradeoff')
    return dict(status='PASS_COMPLETE_WORD_REWRITE_AND_PRECISION', base_commit=BASE,
                concurrent_pr1188=comparison,
                base_word_sha256=digest(base), candidate_word_sha256=digest(candidate),
                moves=len(witness['moves']), phase_map_sha256=maps, prices=prices,
                owning=owning(base,candidate), negative_controls=controls(base,candidate,witness['moves']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-certificate', action='store_true')
    args = parser.parse_args()
    report = run()
    if args.write_certificate:
        write(HERE / 'CERTIFICATE.json', report)
    else:
        same(report, load(HERE / 'CERTIFICATE.json'), 'certificate regeneration')
    print(report['status'], 'moves', report['moves'], 'ADDs', report['prices']['candidate']['ADDs'])
