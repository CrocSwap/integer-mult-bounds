#!/usr/bin/env python3
"""Independent free-algebra replay; imports no search/lowering implementation.

The support lower bound in README.md, not the search's reported distances,
certifies optimality. All checks remain active under python -I -O.
"""
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def root_ops(word):
    need(type(word) is str and all(c in '012345' for c in word), 'root alphabet')
    return [(int(c), int(c) if int(c) < 3 else 6,
             6 if int(c) < 3 else int(c)) for c in word]


def rows(mask):
    return [[(mask >> (3*i+j)) & 1 for j in range(3)] for i in range(3)]


def active(mask):
    a = rows(mask)
    return [any(a[i][j] for i in range(3)) for j in range(3)] + [any(r) for r in a]


def free_run(ops, arrays):
    """Sparse free noncommuting polynomials over F2, not the BFS state."""
    out = [set(v) for v in arrays]
    for op, source, target in ops:
        need(type(op) is int and op >= 0, 'operator label')
        need(type(source) is int and type(target) is int and
             0 <= source < len(out) and 0 <= target < len(out) and source != target,
             'literal ports')
        out[target].symmetric_difference_update((op,)+term for term in out[source])
    return out


def free_identity(mask, ops, factors=None, count=7):
    initial = [{('input', i)} for i in range(count)]
    expected = [set(v) for v in initial]
    for i, row in enumerate(rows(mask)):
        for j, yes in enumerate(row):
            if yes:
                left = (i+3,) if factors is None else tuple(reversed(factors[i+3]))
                right = (j,) if factors is None else tuple(reversed(factors[j]))
                expected[i+3].add(left+right+('input', j))
    actual = free_run(ops, initial)
    need(actual == expected, 'free product identity or restoration')
    need(free_run(list(reversed(ops)), actual) == initial, 'literal inverse')


def star_word(mask, by_column):
    a = rows(mask)
    word = []
    for k in range(3):
        if by_column:
            neighbors = [i+3 for i in range(3) if a[i][k]]
            if neighbors:
                word += [k]+neighbors+[k]+neighbors[::-1]
        else:
            neighbors = [j for j in range(3) if a[k][j]]
            if neighbors:
                word += neighbors+[k+3]+neighbors[::-1]+[k+3]
    return ''.join(map(str, word))


def dense_run(ops, matrices, initial, modulus=2):
    arrays = [list(v) for v in initial]
    for op, source, target in ops:
        value = [sum(x*y for x, y in zip(row, arrays[source])) % modulus
                 for row in matrices[op]]
        arrays[target] = [(x+y) % modulus for x, y in zip(arrays[target], value)]
    return arrays


def dense_expected(mask, matrices, initial, modulus=2):
    def apply(m, x):
        return [sum(a*b for a, b in zip(r, x)) % modulus for r in m]
    expected = [list(v) for v in initial]
    for i, row in enumerate(rows(mask)):
        for j, yes in enumerate(row):
            if yes:
                value = apply(matrices[i+3], apply(matrices[j], initial[j]))
                expected[i+3] = [(x+y) % modulus for x, y in zip(expected[i+3], value)]
    return expected


def invoice(ops, width, roles, factor_count):
    """Literal dense one-data-tape trace, returning home after every call."""
    travel = 0
    for factor, source, target in ops:
        position = 0
        for i in range(width):
            for j in range(width):
                for nxt in (roles*width+factor*width*width+i*width+j, source*width+j):
                    travel += abs(nxt-position)
                    position = nxt
            nxt = target*width+i
            travel += abs(nxt-position)
            position = nxt
        travel += position
    calls = len(ops)
    return dict(calls=calls, coefficient_reads=calls*width*width,
                source_reads=calls*width*width, target_read_writes=calls*width,
                and_operations=calls*width*width, xor_operations=calls*width*(width+1),
                head_moves_in_bit_cells=travel, data_bits=roles*width,
                coefficient_bits=factor_count*width*width,
                instruction_records=calls, input_bit_checks=roles*width+factor_count*width*width)


def check_tape_formula():
    """Closed-form sum for disjoint rows, independent of the access trace loop."""
    cases = 0
    for width in range(1, 6):
        for factor in range(6):
            for source, target in ((0, 6), (2, 6), (6, 3), (6, 5)):
                base = 7*width+factor*width*width
                coeff_sum = width*width*base + width*width*(width*width-1)//2
                source_sum = width*source*width + width*(width-1)//2
                if target > source:
                    boundary = 2*(target*width+width-1)
                else:
                    previous_targets = (width-1)*target*width+(width-1)*(width-2)//2
                    boundary = 2*width*(source*width+width-1)-2*previous_targets
                expected = 2*coeff_sum-2*width*source_sum+boundary
                need(invoice([(factor, source, target)], width, 7, 6)['head_moves_in_bit_cells']
                     == expected, 'closed-form tape return invoice')
                cases += 1
    return cases


def validate(cert, dense=True):
    need(cert['format'] == 'binary-connector-walk-v1', 'certificate format')
    need(cert['seed'] == 51 and cert['dimension'] == 3, 'fixed search domain')
    need(cert['base_commit'] == '91a2094f2e022930069e8cfdc810a3ea1b81cd09', 'base pin')
    words = cert['witnesses']
    need(set(words) == {str(i) for i in range(512)}, 'complete 512-mask coverage')
    histogram, savings = Counter(), 0
    dense_cases = 0
    rng = random.Random(51)
    fixtures = {}
    for width in (1, 2, 3):
        fixtures[width] = [[[rng.randrange(2) for _ in range(width)] for _ in range(width)]
                           for _ in range(6)]
    for mask in range(512):
        word = words[str(mask)]
        ops = root_ops(word)
        free_identity(mask, ops)
        support = active(mask)
        counts = Counter(map(int, word))
        need(all(counts[f] == 2*support[f] for f in range(6)), 'support lower bound equality')
        stars = [star_word(mask, mode) for mode in (False, True)]
        for star in stars:
            free_identity(mask, root_ops(star))
        baseline = min(map(len, stars))
        savings += len(word) < baseline
        histogram[(baseline, len(word))] += 1
        if dense:
            for width, matrices in fixtures.items():
                # Every input column includes arbitrary connector and output dirt.
                for bit in range(7*width):
                    initial = [[0]*width for _ in range(7)]
                    initial[bit//width][bit % width] = 1
                    out = dense_run(ops, matrices, initial)
                    need(out == dense_expected(mask, matrices, initial), 'dense basis identity')
                    need(dense_run(ops[::-1], matrices, out) == initial, 'dense inverse')
                    dense_cases += 1
                initial = [[rng.randrange(2) for _ in range(width)] for _ in range(7)]
                need(dense_run(ops, matrices, initial) == dense_expected(mask, matrices, initial),
                     'dense combined dirty input')
                dense_cases += 1
    cycle = cert['cycle']
    need(cycle['mask'] == 371 and cycle['word'] == words['371'], 'cycle binding')
    factors = cycle['factor_lists_in_application_order']
    need(factors == [[0], [1, 2], [3, 4, 5], [6, 7, 8, 9],
                     [10, 11, 12, 13, 14], [15, 16, 17, 18, 19, 20]], 'factor lists')
    leaves = cycle['lowered_word']
    need(cycle['data_arrays'] == 10 and cycle['dirty_arrays'] == 4, 'space invoice')
    need(all(type(f) is int and 0 <= f < 21 for f, _, _ in leaves), 'leaf alphabet')
    free_identity(371, leaves, factors, 10)
    multiplicities = Counter(str(f) for f, _, _ in leaves)
    need(dict(multiplicities) == cycle['lowered_factor_multiplicities'], 'all children paid')
    need(len(leaves) == 198, 'lowered leaf count')
    # Independent recurrence, no import of product() or its emitted tree.
    def count(n):
        return 1 if n == 1 else 2*(count(n//2)+count(n-n//2))
    prices = [count(n) for n in range(1, 7)]
    lower_stars = [sum(prices[int(c)] for c in star_word(371, mode)) for mode in (False, True)]
    need(sum(2*c for c in prices) == len(leaves), 'recursive count recurrence')
    selected_ops = root_ops(words['371'])
    summary = {
        'status': 'PASS_BINARY_CONNECTOR_WALK', 'targets': 512,
        'free_identity_replays': 1536, 'dense_cases': dense_cases,
        'closed_form_tape_cases': check_tape_formula(),
        'improved_over_best_row_or_column_stars': savings,
        'comparison_histogram': [{'stars': a, 'walk': b, 'matrices': number}
                                 for (a, b), number in sorted(histogram.items())],
        'cycle': {'word': cycle['word'], 'calls': len(selected_ops),
                  'row_star_calls': len(star_word(371, False)),
                  'column_star_calls': len(star_word(371, True)),
                  'factor_leaf_prices': prices, 'lowered_calls': len(leaves),
                  'lowered_row_and_column_star_calls': lower_stars,
                  'root_dense_invoice': invoice(selected_ops, 3, 7, 6),
                  'root_row_star_invoice': invoice(root_ops(star_word(371, False)), 3, 7, 6),
                  'root_column_star_invoice': invoice(root_ops(star_word(371, True)), 3, 7, 6),
                  'lowered_dense_invoice': invoice(leaves, 3, 10, 21)},
    }
    return summary


def rejection_controls(cert):
    mutations = {}
    c = copy.deepcopy(cert); del c['witnesses']['51']
    mutations['missing_mask'] = (c, 'complete 512-mask coverage')
    c = copy.deepcopy(cert); c['witnesses']['371'] = c['witnesses']['371'][:-1]
    mutations['missing_restore'] = (c, 'free product identity or restoration')
    c = copy.deepcopy(cert); w = c['witnesses']['371']
    # Swap an A/B pair, not two commuting readouts. Keep the duplicate word
    # binding coherent below so the mathematical control must detect the error.
    c['witnesses']['371'] = w[0]+w[2]+w[1]+w[3:]
    mutations['wrong_query_order'] = (c, 'free product identity or restoration')
    c = copy.deepcopy(cert); c['witnesses']['371'] += '00'
    mutations['valid_but_not_optimal'] = (c, 'support lower bound equality')
    c = copy.deepcopy(cert); c['witnesses']['371'] = c['witnesses']['370']
    mutations['wrong_product_mask'] = (c, 'free product identity or restoration')
    c = copy.deepcopy(cert); c['cycle']['lowered_word'][-1][0] = 0
    mutations['wrong_leaf_factor'] = (c, 'free product identity or restoration')
    c = copy.deepcopy(cert); c['cycle']['lowered_word'][0][2] = c['cycle']['lowered_word'][0][1]
    mutations['aliased_leaf'] = (c, 'literal ports')
    c = copy.deepcopy(cert); c['cycle']['lowered_factor_multiplicities']['0'] -= 1
    mutations['unpaid_leaf'] = (c, 'all children paid')
    c = copy.deepcopy(cert); c['cycle']['dirty_arrays'] = 3
    mutations['underpriced_scratch'] = (c, 'space invoice')
    for name, (bad, reason) in mutations.items():
        bad['cycle']['word'] = bad['witnesses']['371']
        try:
            validate(bad, dense=False)
        except ValueError as exc:
            need(str(exc) == reason, 'wrong control failure: '+name+': '+str(exc))
            continue
        raise ValueError('control escaped: '+name)
    ops = root_ops(cert['cycle']['word'])
    # The identical unsigned word does not have the claimed characteristic-3 map.
    matrices = [[[1]] for _ in range(6)]
    initial = [[1] for _ in range(7)]
    need(dense_run(ops, matrices, initial, 3) != dense_expected(371, matrices, initial, 3),
         'odd-characteristic control')
    # A deterministic nonlinear A need not distribute over the connector sum.
    # z=(1,0), Bx=(0,1), A(a,b)=a*b: A(z+Bx)+A(z)=1 != A(Bx)=0.
    need(((1 ^ 0) & (0 ^ 1)) ^ (1 & 0) != (0 & 1), 'nonlinear control')
    return sorted(mutations)+['odd_characteristic', 'nonlinear_readout']


def verify_sources():
    pins = json.loads((ROOT/'SOURCES.json').read_text())
    need(pins['base_commit'] == '91a2094f2e022930069e8cfdc810a3ea1b81cd09', 'source base')
    need(len(pins['retained_references']) == 2 and
         {s['local_path'] for s in pins['retained_references']} ==
         {'references/PR889-README.md', 'references/PR889-NOTICE.md'}, 'reference inventory')
    for source in pins['retained_references']:
        path = ROOT/source['local_path']
        need(path.parent == ROOT/'references', 'reference path')
        need(hashlib.sha256(path.read_bytes()).hexdigest() == source['sha256'], 'reference digest')


if __name__ == '__main__':
    import sys
    need(sys.argv[1:] in ([], ['--write-summary']), 'arguments')
    verify_sources()
    certificate = json.loads((ROOT/'CERTIFICATE.json').read_text())
    result = validate(certificate)
    result['negative_controls'] = rejection_controls(certificate)
    if sys.argv[1:] == ['--write-summary']:
        (ROOT/'EXPECTED.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(result == json.loads((ROOT/'EXPECTED.json').read_text()), 'expected summary')
    print('PASS_BINARY_CONNECTOR_WALK targets=512 dense_cases='+str(result['dense_cases'])+
          ' controls='+str(len(result['negative_controls']))+' cycle=18->12 lowered=228->198')
