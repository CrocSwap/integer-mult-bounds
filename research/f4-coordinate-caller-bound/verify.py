"""Check the fixed F4 coordinate decoder and its declared caller bound.

The power intervals use zxv's unchanged source. No discovery solver is used.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SAVING = Q('0.00310045')
T = 1 - SAVING


def need(condition, message):
    if not condition:
        raise ValueError(message)


def reject(function, message):
    try:
        function()
    except ValueError:
        return message
    raise ValueError('Control accepted: ' + message)


def authenticate(raw, expected):
    need(sha256(raw).hexdigest() == expected, 'Changed interval source')


source = next(row for row in json.loads((HERE / 'SOURCES.json').read_text())['files']
              if row['usage'] == 'input')
source_path = ROOT / source['path']
source_bytes = source_path.read_bytes()
authenticate(source_bytes, source['sha256'])
engine = {'__file__': str(source_path), '__name__': 'pinned_interval_source'}
exec(compile(source_bytes, str(source_path), 'exec'), engine)
power, moment, display = (engine[name] for name in ('power', 'moment', 'display'))


def roots():
    rows = {tuple(int(i == j) for j in range(4)) for i in range(4)}
    for i, j in combinations(range(4), 2):
        for sign in (-1, 1):
            row = [0] * 4
            row[i], row[j] = 1, sign
            rows.add(tuple(row))
    rows.update((1,) + signs for signs in product((-1, 1), repeat=3))
    return sorted(rows)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def binary_rank(rows):
    pivots = {}
    for row in rows:
        value = sum(entry << i for i, entry in enumerate(row))
        while value:
            bit = value.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
    return len(pivots)


def check_clique(rays, coordinate, indices):
    need(len(indices) == len(set(indices)) == 5, 'Five distinct rays')
    need(all(0 <= i < 24 for i in indices), 'Valid ray index')
    need(all(rays[i][coordinate] != 0 for i in indices), 'Query support')
    need(all(dot(rays[i], rays[j]) != 0 for i, j in combinations(indices, 2)),
         'Nonorthogonal clique')


def check_fitting(rays, matrix):
    need(len(matrix) == 24 and all(len(row) == 24 for row in matrix), 'Matrix size')
    for i, row in enumerate(matrix):
        need(row[i] == 1, 'Unit diagonal')
        for j, entry in enumerate(row):
            need(entry in (0, 1), 'Binary entries')
            need(i == j or dot(rays[i], rays[j]) == 0 or entry == 0,
                 'Required zero at a nonorthogonal pair')


def linear(terms, constant=0):
    lower = upper = Q(constant)
    for coefficient, base, exponent in terms:
        lo, hi = power(base, exponent)
        lower += coefficient * (lo if coefficient >= 0 else hi)
        upper += coefficient * (hi if coefficient >= 0 else lo)
    return lower, upper


def histogram_bill(p, a, w=6):
    targets = Counter({1 + w * (p + 2): 48})
    paid = Counter({w: 48 * (p + 2), 5: 4 * (p + 2)})
    paid[1] += 24 * (p - 1)
    for k in list(range(2, a + 2)) + list(range(2, p - a + 1)):
        targets[1 + w * k] += 48
        paid[w * k] += 48
    lo, hi = moment(targets, T)
    cost_lo, cost_hi = moment(paid, T)
    return lo - cost_hi, hi - cost_lo


def main():
    witness = json.loads((HERE / 'WITNESS.json').read_text())
    rays = roots()
    need(len(rays) == 24 and rays == [tuple(row) for row in witness['rays']],
         'Exact F4 ray list')
    cliques = witness['coordinate_cliques']
    need(len(cliques) == 4, 'Four separate coordinate queries')
    for j, clique in enumerate(cliques):
        check_clique(rays, j, clique)

    dense = [[int(i == j or dot(x, y) == 0) for j, y in enumerate(rays)]
             for i, x in enumerate(rays)]
    check_fitting(rays, dense)
    query_ranks = []
    for coordinate, clique in enumerate(cliques):
        principal = [[dense[i][j] for j in clique] for i in clique]
        need(principal == [[int(i == j) for j in range(5)] for i in range(5)],
             'Forced identity minor')
        need(binary_rank(principal) == 5, 'Identity minor rank')
        support = [i for i, ray in enumerate(rays) if ray[coordinate]]
        query_ranks.append(binary_rank([[dense[i][j] for j in support] for i in support]))

    # Prefix intervals also check every split through p=100.
    prefixes = [(Q(0), Q(0))] * 102
    for k in range(2, 102):
        inc = linear([(1, 1 + 6 * k, T), (-1, 6 * k, T)])
        old = prefixes[k - 1]
        prefixes[k] = (old[0] + inc[0], old[1] + inc[1])
    best = None
    all_splits = 0
    for p in range(1, 101):
        base = linear([(48, 1 + 6 * (p + 2), T), (-48 * (p + 2), 6, T),
                       (-4 * (p + 2), 5, T)], -24 * (p - 1))
        for a in range(p):
            left, right = prefixes[a + 1], prefixes[p - a]
            bound = (base[0] + 48 * (left[0] + right[0]),
                     base[1] + 48 * (left[1] + right[1]))
            need(bound[1] < 0, 'Negative finite margin')
            all_splits += 1
        balanced = histogram_bill(p, (p - 1) // 2)
        need(balanced[1] < 0, 'Negative balanced histogram margin')
        if best is None or balanced[1] > best[0]:
            best = (balanced[1], p, balanced)

    p = 100
    tail = linear([(48, 1 + 6 * (p + 2), T), (-48 * (p + 2), 6, T),
                   (-4 * (p + 2), 5, T), (48 * (p - 1), 13, T),
                   (-48 * (p - 1), 12, T)], -24 * (p - 1))
    derivative = linear([(288 * T, 1 + 6 * (p + 2), T - 1), (-48, 6, T),
                         (-4, 5, T), (48, 13, T), (-48, 12, T)], -24)
    need(tail[1] < 0 and derivative[1] < 0, 'Negative tail and derivative')

    controls = []
    bad_support = [0] + cliques[0][1:]
    controls.append(reject(lambda: check_clique(rays, 0, bad_support), 'outside query support'))
    controls.append(reject(lambda: check_clique(rays, 0, cliques[0][:-1] + [cliques[0][0]]),
                           'repeated ray'))
    support = [i for i, ray in enumerate(rays) if ray[0]]
    i, j = next((i, j) for i, j in combinations(support, 2) if dot(rays[i], rays[j]) == 0)
    orthogonal = [i, j] + [k for k in support if k not in (i, j)][:3]
    controls.append(reject(lambda: check_clique(rays, 0, orthogonal), 'orthogonal pair'))
    missing_diagonal = [row[:] for row in dense]
    missing_diagonal[cliques[0][0]][cliques[0][0]] = 0
    controls.append(reject(lambda: check_fitting(rays, missing_diagonal), 'missing diagonal'))
    false_pair = [row[:] for row in dense]
    false_pair[cliques[0][0]][cliques[0][1]] = 1
    controls.append(reject(lambda: check_fitting(rays, false_pair), 'forbidden off-diagonal'))
    controls.append(reject(lambda: authenticate(source_bytes + b'\n', source['sha256']),
                           'changed interval source'))

    scientific = {
        'query_rank_floor': [5, 5, 5, 5], 'dense_fixture_query_ranks': query_ranks,
        'finite_pair_range': [1, 100], 'finite_splits_checked': all_splits,
        'greatest_balanced_upper_bound_at_p': best[1], 'greatest_balanced_margin': display(best[2]),
        'tail_upper_at_100': display(tail), 'tail_derivative_at_100': display(derivative),
        'controls': controls,
    }
    if sys.argv[1:] == ['--write']:
        (HERE / 'EXPECTED.json').write_text(json.dumps(scientific, indent=2) + '\n')
    else:
        need(not sys.argv[1:], 'Use no arguments or --write')
        need(scientific == json.loads((HERE / 'EXPECTED.json').read_text()), 'Frozen scientific receipt')
    print(json.dumps({'status': 'PASS_F4_COORDINATE_ALL_P_BOUND', 'new_kappa': False,
                      'tested_saving': str(SAVING), **scientific}, indent=2))


if __name__ == '__main__':
    main()
