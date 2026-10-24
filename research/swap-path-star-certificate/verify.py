#!/usr/bin/env python3
"""Check two exact cut certificates. Ali Romman with Codex assistance.

Apache-2.0. No predecessor code or numerical solver is used.
"""
from fractions import Fraction as F
from itertools import permutations
from pathlib import Path
import hashlib
import json
import sys

ORDERS = tuple(permutations(range(4)))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pattern(text):
    require(type(text) is str and len(text) == 4 and set(text) == set('0123'),
            'invalid pattern')
    return tuple(map(int, text))


def relabel(order, mapping):
    return tuple(mapping[x] for x in order)


def transposition(a, b):
    return tuple(b if x == a else a if x == b else x for x in range(4))


def counts(cut):
    writes = []
    for row in range(4):
        total = 0
        for order in cut:
            tail = tuple(x for x in order if x != row)
            total += sum(tail[:k] + (row,) + tail[k:] not in cut for k in range(4))
        writes.append(total)
    swaps = {f'{a}{b}': sum(relabel(order, transposition(a, b)) not in cut for order in cut)
             for a in range(4) for b in range(a+1, 4)}
    return writes, swaps


def independent_counts(cut):
    # The new row vector has label 4. Count all 120 orders directly.
    writes = [0] * 4
    for order in permutations(range(5)):
        before = tuple(x for x in order if x != 4)
        if before not in cut:
            continue
        for row in range(4):
            after = tuple(row if x == 4 else x for x in order if x != row)
            writes[row] += after not in cut
    return writes


def certificate(case):
    targets = [tuple(edge) for edge in case['targets']]
    expected_targets = {'path': [(0,1),(1,2),(2,3)], 'star': [(0,1),(0,2),(0,3)]}
    require(targets == expected_targets[case['name']], 'wrong target graph')
    maps = tuple(pattern(s) for s in case['automorphisms'])
    required_maps = (tuple(permutations((1,2,3))) if case['name'] == 'star' else None)
    expected_maps = {(0,)+p for p in required_maps} if required_maps else {(0,1,2,3)}
    require(set(maps) == expected_maps and len(set(maps)) == len(maps), 'wrong symmetry orbit')
    loads = [F(0)] * 4
    target = F(0)
    rows = []
    for entry in case['cuts']:
        base = {pattern(s) for s in entry['patterns']}
        require(len(base) == len(entry['patterns']) and 0 < len(base) < 24, 'invalid cut')
        weight = F(entry['weight'])
        require(weight > 0, 'nonpositive cut weight')
        raw, raw_swaps = counts(base)
        require(raw == independent_counts(base), 'reinsertion count differs')
        for mapping in maps:
            require({tuple(sorted((mapping[a],mapping[b]))) for a,b in targets}
                    == set(targets), 'mapping changes target graph')
            cut = {relabel(o, mapping) for o in base}
            paid, swaps = counts(cut)
            require(paid == independent_counts(cut), 'orbit count differs')
            for j in range(4):
                loads[j] += weight * paid[j] / len(maps)
            target += 5 * weight * sum(swaps[f'{a}{b}'] for a,b in targets) / len(maps)
        rows.append({'patterns': len(base), 'write_counts': raw,
                     'target_count': sum(raw_swaps[f'{a}{b}'] for a,b in targets),
                     'weight': str(weight)})
    require(loads == [F(1)] * 4, 'paid load is not one')
    require(target == F(case['lower_bound']) and 8 < target <= 9, 'lower bound differs')
    require(type(case['minimum']) is int and case['minimum'] == 9, 'wrong minimum')
    return {'name': case['name'], 'cuts': rows, 'loads': list(map(str,loads)),
            'lower_bound': str(target), 'minimum': 9, 'orbit_size': len(maps)}


def word_check(edges, n, registers, omitted=None):
    # Each register entry remains one formal group basis element.
    state = [[1 << i for i in range(n)] for _ in range(registers)]
    gates = [(r,i,j) for r,(a,b) in enumerate(edges) for i,j in ((a,b),(b,a),(a,b))]
    for index,(r,i,j) in enumerate(gates):
        if index != omitted:
            state[r][i] ^= state[r][j]
    expected = [[1 << i for i in range(n)] for _ in range(registers)]
    for r,(a,b) in enumerate(edges):
        expected[r][a], expected[r][b] = expected[r][b], expected[r][a]
    return state == expected


def controls(cases):
    rejected = 0
    for case in cases:
        mutations = []
        wrong = json.loads(json.dumps(case));wrong['cuts'][0]['weight'] = str(2*F(wrong['cuts'][0]['weight']));mutations.append(wrong)
        wrong = json.loads(json.dumps(case));wrong['lower_bound'] = '9';mutations.append(wrong)
        wrong = json.loads(json.dumps(case));wrong['automorphisms'] = ['1023'];mutations.append(wrong)
        wrong = json.loads(json.dumps(case));wrong['cuts'][0]['patterns'][0] = '0000';mutations.append(wrong)
        for wrong in mutations:
            try:
                certificate(wrong)
            except ValueError:
                rejected += 1
            else:
                raise ValueError('invalid certificate accepted')
    return rejected


def evidence():
    here = Path(__file__).resolve().parent
    supplied = json.loads((here/'CUTS.json').read_text(encoding='utf-8'))
    require(supplied['schema'] == 'swap-path-star-certificate/v1', 'schema differs')
    cases = supplied['cases']
    require([c['name'] for c in cases] == ['path','star'], 'case inventory differs')
    rows = [certificate(c) for c in cases]
    endpoints = omissions = 0
    for case in cases:
        for n in (4,5,6):
            for registers in (3,5):
                require(word_check(case['targets'],n,registers), 'nine-call endpoint differs')
                endpoints += 1
                for omit in range(9):
                    require(not word_check(case['targets'],n,registers,omit), 'call omission accepted')
                    omissions += 1
    result = {'schema':'swap-path-star-result/v1', 'cases':rows, 'formal_diagonal_endpoints':endpoints,
              'call_omission_controls':omissions, 'certificate_controls':controls(cases),
              'relative_orders_per_orbit_cut':120, 'no_new_kappa':True}
    result['source_sha256'] = {name:hashlib.sha256((here/name).read_bytes()).hexdigest()
                              for name in ('README.md','CUTS.json','verify.py','TASK.json','VERIFY.json','SOURCES.json')}
    return result


def main():
    encoded = json.dumps(evidence(),indent=2,sort_keys=True)+'\n'
    if sys.argv[1:] == ['--emit-receipt']:
        print(encoded,end='')
    else:
        require(not sys.argv[1:], 'unexpected argument')
        require(Path(__file__).with_name('RESULT.json').read_text(encoding='utf-8') == encoded,
                'receipt differs')
        print('PASS_SWAP_PATH_STAR_CERTIFICATE path=9 star=9 no_new_kappa')


if __name__ == '__main__':
    main()
