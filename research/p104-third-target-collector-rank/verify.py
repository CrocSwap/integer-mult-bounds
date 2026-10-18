#!/usr/bin/env python3
"""Exact literal replay, no producer imports. ywz65 + OpenAI Codex, Apache-2.0."""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
INPUT = HERE.parent / 'p104-native-channel' / 'inputs'
PINS = {'LOWRANK-WITNESS.json': '0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e',
        'P104-FIXTURE.json': '516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4'}


def need(p, msg):
    if not p:
        raise ValueError(msg)


def frame(xs):
    seen = {0}
    for x in xs:
        need(type(x) is int and 0 < x < 512 and x not in seen, 'invalid basis')
        seen |= {v ^ x for v in tuple(seen)}
    return frozenset(seen)


def rank(a):
    a = [list(map(Q, row)) for row in a]
    r = 0
    for j in range(len(a[0])):
        p = next((i for i in range(r, len(a)) if a[i][j]), None)
        if p is None:
            continue
        a[p], a[r] = a[r], a[p]
        q = a[r][j]
        a[r] = [x/q for x in a[r]]
        for i in range(len(a)):
            if i != r:
                q = a[i][j]
                a[i] = [x-q*y for x, y in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def geometry(word, fixture):
    roots = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0]*8
            row[i], row[j] = 2, 2*sign
            roots.append(tuple(row))
    roots.extend((1, *s) for s in product((-1, 1), repeat=7) if sum(s) % 4 == 3)
    p = fixture['section4_explicit_P104']
    ports = sorted(set(roots) - set(map(tuple, p['F0']+p['C'])))
    need(len(ports) == 104, 'root count')
    half = [[Q(sum(x*y for x, y in zip(a, b)), 8) for b in ports] for a in ports]
    corr = [[Q(t == s)-half[t][s] for s in range(104)] for t in range(3)]
    supports = [{s for s in range(104) if corr[t][s]} for t in range(3)]
    need(list(map(len, supports)) == [48]*3, 'support sizes')
    ends = [frame(word['final_frames'][f'Y{t}']) for t in range(3)]
    need(all(len(x) == 256 for x in ends) and len(set(ends)) == 3, 'endpoint incomparability')
    paths = {r: [frame(f)] for r, f in word['initial_frames'].items()}
    for e in word['program']:
        if e[0] == 'transport' and e[1] in paths:
            need(paths[e[1]][-1] == frame(e[2]), 'source path binding')
            paths[e[1]].append(frame(e[3]))
        if e[0] in ('add', 'copy'):
            need(not e[1].startswith('X') and not e[2].startswith('Y'), 'original data contract')
    for r, path in paths.items():
        if r.startswith(('X', 'Y')):
            need(all(a <= b for a, b in zip(path, path[1:])), 'data monotonicity')
    union = set.union(*supports)
    need(len({paths[f'X{s}'][0] for s in union}) == 90, '90 distinct acquisition lines')
    escapes, late = [], []
    for t in range(3):
        for s in sorted(supports[t]):
            xp, yp = paths[f'X{s}'], paths[f'Y{t}']
            line = xp[0]
            need(len(line) == 2 and line <= ends[t], 'initial source access')
            escaped = sorted(xp[1]-ends[t])
            if not escaped:
                late.append([t, s, len(xp[1]).bit_length()-1])
            else:
                escapes.append([t, s, next(x for x in line if x), escaped[0]])
            if t < 2:
                need(escaped and all(x == line for x in xp if x <= ends[t]), 'two-target escape')
                need(all(x != line for x in yp), 'two-target direct access')
    groups = []
    for mask in range(1, 8):
        targets = [t for t in range(3) if mask >> t & 1]
        sources = [s for s in range(104) if [t for t in range(3) if corr[t][s]] == targets]
        common = set.intersection(*(set(ends[t]) for t in targets))
        r = rank([[corr[t][s] for s in sources] for t in targets])
        need(all(paths[f'X{s}'][0] <= common for s in sources), 'common-frame source access')
        groups.append({'targets': targets, 'sources': sources, 'coefficient_rank': r,
                       'common_dimension': len(common).bit_length()-1,
                       'extra_collector_floor': len(targets)-r})
    need(sum(len(g['sources']) for g in groups) == 90, 'union size')
    need(sum(g['extra_collector_floor'] for g in groups) == 4, 'collector deficit')
    return half, {'groups': groups, 'escape_witnesses': escapes, 'first_expansion_still_contained': late,
                  'union_support_size': 90, 'separated_collector_minimum': 94}


def replay(word, circuit, half):
    new = circuit['initial_frames'] if circuit else {}
    need(not set(new) & set(word['initial_frames']), 'new alias')
    fs = {r: frame(f) for r, f in {**word['initial_frames'], **new}.items()}
    names = sorted(fs)
    rows = {r: {r: Q(1)} for r in names}
    full = frozenset(range(512))
    need(all(fs[r] == {0} for r in new), 'dirty entrance')
    profile, added, counts = Counter(), Counter(), Counter()
    max_l1, max_denom = Q(1), 1
    insert = {i['completed_cut']: i['events'] for i in circuit['insertions']} if circuit else {}
    need(not circuit or (len(circuit['insertions']) == 2 and set(insert) == {0, len(word['program'])}), 'insertion cuts')

    def event(e, is_new):
        nonlocal max_l1, max_denom
        op, dst = e[:2]
        counts['events'] += 1
        if is_new:
            need(op in ('add', 'transport') and dst in set(new) | {'Y0', 'Y1', 'Y2'}, 'new alphabet')
        if op == 'add':
            _, dst, src, coefficient, basis = e
            need(dst != src and src in rows and dst in rows, 'ADD roles')
            need(fs[dst] == fs[src] == frame(basis), 'ADD frame')
            q = Q(coefficient)
            need(q and q.denominator & (q.denominator-1) == 0, 'dyadic ADD')
            if is_new:
                need(src in new or src.startswith('X'), 'forbidden read')
                need(dst in new or src in new, 'direct target read')
                counts['added_ADDs'] += 1
                counts['source_reads'] += int(src.startswith('X'))
            for col, v in rows[src].items():
                value = rows[dst].get(col, Q(0)) + q*v
                if value:
                    rows[dst][col] = value
                else:
                    rows[dst].pop(col, None)
        elif op == 'transport':
            _, dst, old, newf, cost = e
            a, b = frame(old), frame(newf)
            need(dst in rows and fs[dst] == a, 'transport entrance')
            need(a < b or b < a, 'nested frame')
            need(type(cost) is int and cost == abs(len(old)-len(newf)), 'transport invoice')
            if is_new:
                need(dst in new and a < b, 'new monotonicity')
                added[cost] += 1
            else:
                need(a < b or dst == 'C', 'original descent')
            profile[cost] += 1
            fs[dst] = b
        elif op == 'zero':
            need(dst == 'C' and dst not in rows, 'private allocation')
            rows[dst], fs[dst] = {}, frame(e[2])
        elif op == 'copy':
            _, dst, src, b = e
            need(dst == 'C' and rows[dst] == {} and fs[dst] == fs[src] == frame(b), 'private copy')
            rows[dst] = dict(rows[src])
        elif op == 'erase':
            need(dst == 'C' and fs[dst] == frame(e[2]), 'private discard')
            del rows[dst], fs[dst]
            return
        else:
            raise ValueError('unknown operation')
        max_l1 = max(max_l1, sum(map(abs, rows[dst].values()), Q(0)))
        max_denom = max([max_denom] + [v.denominator for v in rows[dst].values()])

    for cut in range(len(word['program'])+1):
        for e in insert.get(cut, []):
            event(e, True)
        if cut < len(word['program']):
            event(word['program'][cut], False)
    expected_frames = {**word['final_frames'], **(circuit['final_frames'] if circuit else {})}
    need(set(rows) == set(names) == set(expected_frames), 'final roles')
    for r in names:
        need(fs[r] == frame(expected_frames[r]), 'final frame')
        if r in new:
            need(fs[r] == full, 'dirty exit')
        expected = {r: Q(1)}
        if r.startswith('Y'):
            t = int(r[1:])
            cs = [Q(t == s) for s in range(104)] if circuit and t < 3 else half[t]
            expected.update({f'X{s}': q for s, q in enumerate(cs) if q})
        need(rows[r] == expected, 'endpoint '+r)
    return {**dict(counts), 'columns': len(names), 'helpers': len(new),
            'added_profile': dict(sorted(added.items())), 'full_profile': dict(sorted(profile.items())),
            'added_transports': sum(added.values()), 'added_rank_mass': sum(k*v for k, v in added.items()),
            'full_rank_mass': sum(k*v for k, v in profile.items()),
            'logical_prefix_l1': str(max_l1), 'logical_denominator': max_denom}


def architecture(word, circuit, half, geo):
    """Bind the attaining word to the restricted class used by the lower bound."""
    groups, owners, expected_deliveries = {}, {}, Counter()
    for g in geo['groups']:
        key = tuple(g['targets'])
        rec = next(x for x in circuit['groups'] if x['targets'] == list(key))
        need(rec['sources'] == g['sources'], 'group source binding')
        need(len(rec['extra_helpers']) == g['extra_collector_floor'], 'group collector count')
        common = frozenset.intersection(*(frame(word['final_frames'][f'Y{t}']) for t in key))
        need(frame(rec['common_frame']) == common, 'common frame binding')
        groups[key] = common
        regs = [f'N{s}' for s in g['sources']] + rec['extra_helpers']
        need(len(set(regs)) == len(regs) and not set(regs) & set(owners), 'group alias')
        owners.update({r: key for r in regs})
        need(sorted(t for t, _, _ in rec['collectors']) == list(key), 'one collector per target')
        need(len({r for _, r, _ in rec['collectors']}) == len(key), 'disjoint collector rows')
        for t, r, q in rec['collectors']:
            need(r in regs and Q(q), 'group collector')
            expected_deliveries[(f'Y{t}', r, str(Q(q)))] += 1
    need(set(owners) == set(circuit['initial_frames']), 'complete group inventory')
    captures, cleanups, deliveries = Counter(), Counter(), Counter()
    for part, insertion in enumerate(circuit['insertions']):
        for e in insertion['events']:
            if e[0] != 'add':
                continue
            _, dst, src, q, f = e
            q = Q(q)
            if src.startswith('X'):
                s = int(src[1:])
                need(dst == f'N{s}' and dst in owners, 'one source per acquisition role')
                t = owners[dst][0]
                capture = Q(t == s)-half[t][s]
                need(q == (capture if part == 0 else -capture), 'capture coefficient')
                need(frame(f) == (frame(word['initial_frames'][src]) if part == 0 else frozenset(range(512))), 'capture stage')
                (captures if part == 0 else cleanups)[s] += 1
            elif dst.startswith('Y'):
                t = int(dst[1:])
                need(src in owners and t in owners[src], 'target belongs to incidence group')
                if part:
                    deliveries[(dst, src, str(q))] += 1
                else:
                    need(frame(f) == {0}, 'initial dirty compensation')
            else:
                need(dst in owners and src in owners and owners[dst] == owners[src], 'cross-group mixing')
                need(frame(f) == (groups[owners[dst]] if part == 0 else frozenset(range(512))), 'mixing stage')
    expected = Counter({s: 1 for g in geo['groups'] for s in g['sources']})
    need(captures == cleanups == expected, 'exactly one capture and cleanup')
    need(deliveries == expected_deliveries, 'declared deliveries')


def controls(word, circuit, half):
    passed = []
    def reject(label, edit, reason):
        c = deepcopy(circuit)
        edit(c)
        try:
            replay(word, c, half)
        except ValueError as e:
            need(reason in str(e), label + ' wrong failure: '+str(e))
            passed.append(label)
        else:
            raise ValueError('accepted mutation '+label)
    def remove(c, cut, test):
        es = c['insertions'][cut]['events']
        es.pop(next(i for i, e in enumerate(es) if test(e)))
    reject('dirty-compensation', lambda c: c['insertions'][0]['events'].pop(0), 'endpoint')
    reject('source-capture', lambda c: remove(c, 0, lambda e: e[0]=='add' and e[2].startswith('X')), 'endpoint')
    reject('extra-dirty-compensation', lambda c: remove(c, 0, lambda e: e[0]=='add' and e[2].startswith('E')), 'endpoint')
    reject('rank-one-fanout', lambda c: remove(c, 0, lambda e: e[0]=='add' and e[1].startswith('E')), 'endpoint')
    reject('third-target-delivery', lambda c: remove(c, 1, lambda e: e[0]=='add' and e[1]=='Y2'), 'endpoint')
    reject('unmerge', lambda c: remove(c, 1, lambda e: e[0]=='add' and e[1] in c['initial_frames'] and e[2] in c['initial_frames']), 'endpoint')
    reject('source-cleanup', lambda c: c['insertions'][1]['events'].pop(), 'endpoint')
    def bill(c):
        next(e for e in c['insertions'][0]['events'] if e[0]=='transport')[4] += 1
    reject('transport-bill', bill, 'transport invoice')
    reject('chronological-cut', lambda c: c['insertions'][1].update(completed_cut=1), 'insertion cuts')
    def forbidden(c):
        c['insertions'][0]['events'][0][2] = 'Q0'
    reject('original-helper-access', forbidden, 'forbidden read')
    equivalent = deepcopy(circuit)
    for item in equivalent['insertions']:
        for e in item['events']:
            if e[0]=='transport':
                e[2].reverse(); e[3].reverse()
            else:
                e[4].reverse()
    need(replay(word, equivalent, half) == replay(word, circuit, half), 'basis-order positive control')
    need(rank([[1, 1, 0], [1, 1, 1]]) == 2, 'one-extra positive rank control')
    need(rank([[1, 1], [1, 1]]) == 1, 'zero-extra rank rejection')
    return passed


def run():
    for name, digest in PINS.items():
        need(sha256((INPUT/name).read_bytes()).hexdigest() == digest, 'source pin '+name)
    word = json.loads((INPUT/'LOWRANK-WITNESS.json').read_text())
    fixture = json.loads((INPUT/'P104-FIXTURE.json').read_text())
    circuit = json.loads((HERE/'CIRCUIT.json').read_text())
    half, geo = geometry(word, fixture)
    architecture(word, circuit, half, geo)
    return {'geometry': geo, 'baseline': replay(word, None, half),
            'circuit': replay(word, circuit, half), 'rejected_controls': controls(word, circuit, half)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--emit-result', type=Path)
    p.add_argument('--regenerate', action='store_true')
    args = p.parse_args()
    result = json.loads(json.dumps(run()))
    if args.emit_result:
        with args.emit_result.open('x', encoding='utf-8', newline='\n') as out:
            json.dump(result, out, indent=2); out.write('\n')
    else:
        need(result == json.loads((HERE/'RESULT.json').read_text()), 'receipt mismatch')
    if args.regenerate:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)/'circuit.json'
            subprocess.run([sys.executable, '-I', '-B', str(HERE/'build.py'), '--out', str(dest)], check=True)
            need(json.loads(dest.read_text()) == json.loads((HERE/'CIRCUIT.json').read_text()), 'regeneration')
    print('PASS_P104_THIRD_TARGET_COLLECTOR_RANK helpers=94 union=90 rank_deficit=4 controls=10')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, IndexError, TypeError) as e:
        print('FAIL_P104_THIRD_TARGET_COLLECTOR_RANK: '+str(e), file=sys.stderr)
        sys.exit(1)
