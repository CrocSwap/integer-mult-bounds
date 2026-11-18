"""Check exact factors, operation certificates and an independent scalar rank.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import importlib.util
from itertools import product
import json
from pathlib import Path
import random

import factor as f

PACKAGE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load_source():
    for row in json.loads((PACKAGE/'SOURCE-PINS.json').read_text()):
        need(hashlib.sha256((PACKAGE/row['path']).read_bytes()).hexdigest() == row['sha256'], 'source hash')
    spec = importlib.util.spec_from_file_location('lipschitz_source', PACKAGE/'retained/pr7745/verify.py')
    source = importlib.util.module_from_spec(spec); spec.loader.exec_module(source)
    return source


def encoded(value):
    return json.dumps(value, default=str, sort_keys=True, separators=(',', ':'))


def matmul(a, b, width, multiply):
    return [[tuple(sum(multiply(a[i][k], b[k][j])[t] for k in range(len(b)))
                   for t in range(4)) for j in range(width)] for i in range(len(a))]


def scalar_rank(matrix):
    a = [[F(x) for x in row] for row in matrix]; r = 0
    for col in range(len(a[0])):
        pivot = next((i for i in range(r, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]; q = a[r][col]
        a[r] = [x/q for x in a[r]]
        for i in range(r+1, len(a)):
            q = a[i][col]
            if q:
                a[i] = [x-q*y for x, y in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def block_rank(a, source):
    basis = [tuple(F(i == j) for i in range(4)) for j in range(4)]
    rows = []
    for row in a:
        blocks = [[source.multiply(q, v) for v in basis] for q in row]
        rows.extend([[block[col][lane] for block in blocks for col in range(4)]
                     for lane in range(4)])
    rank = scalar_rank(rows)
    need(rank % 4 == 0, 'quaternion block rank multiple')
    return rank // 4


def check_certificate(a, result, source):
    a = f.matrix(a, f.dyadic); m, n = len(a), len(a[0]); r = result['rank']
    s = result['input_scale']; cleared = [[f.scale(q, 1 << s) for q in row] for row in a]
    e, u, v = deepcopy(cleared), f.identity(m), f.identity(m)
    for step in result['steps']:
        if step[0] == 'swap':
            _, i, j = step
            e[i], e[j] = e[j], e[i]; u[i], u[j] = u[j], u[i]
            for row in v:
                row[i], row[j] = row[j], row[i]
        else:
            _, i, j, col, q, before, after = step
            need(f.hurwitz(q) and f.norm(e[j][col]) == before and before > 0, 'division premise')
            for rows in (e, u):
                rows[i] = [tuple(x-y for x, y in zip(left, source.multiply(q, right)))
                           for left, right in zip(rows[i], rows[j])]
            for row in v:
                row[j] = source.add(row[j], source.multiply(row[i], q))
            need(f.norm(e[i][col]) == after and 0 <= after <= before/2, 'division remainder')
    need((e, u, v) == (result['echelon'], result['left_transform'], result['inverse_transform']), 'operation replay')
    need(all(f.hurwitz(q) for rows in (e, u, v) for row in rows for q in row), 'Hurwitz closure')
    mul = source.multiply
    need(matmul(u, cleared, n, mul) == e, 'left transform product')
    need(matmul(u, v, m, mul) == f.identity(m) == matmul(v, u, m, mul), 'two-sided inverse')
    need(matmul(v, e, n, mul) == cleared, 'inverse reconstruction')
    pivots = result['pivots']; need(len(pivots) == r and pivots == sorted(set(pivots)), 'pivot list')
    for i, col in enumerate(pivots):
        need(f.norm(e[i][col]) > 0 and not any(f.norm(q) for q in e[i][:col]), 'pivot row')
        need(not any(f.norm(e[j][col]) for j in range(i+1, m)), 'pivot column')
    need(not any(f.norm(q) for row in e[r:] for q in row), 'zero row tail')
    left, right = result['left'], result['right']
    need(len(left) == m and all(len(row) == r for row in left), 'left factor shape')
    need(len(right) == r and all(len(row) == n for row in right), 'right factor shape')
    need(matmul(left, right, n, mul) == a, 'factor product')
    need(all(f.hurwitz(q) for row in left for q in row), 'left denominator')
    need(all(f.hurwitz(f.scale(q, 1 << s)) for row in right for q in row), 'right denominator')
    need(r == block_rank(a, source), 'independent rational block rank')
    return sum(step[0] == 'reduce' for step in result['steps'])


def calculate():
    source = load_source()
    old = dict(responses=source.check_responses(), parity=source.check_parity(), divisors=source.check_right_divisors())
    basis = [tuple(F(i == j) for i in range(4)) for j in range(4)]
    omega = (F(1, 2),)*4
    for a, b in product(basis, repeat=2):
        need(f.multiply(a, b) == source.multiply(a, b), 'Hamilton multiplication table')
    order_basis = basis[:3]+[omega]
    for a, b in product(order_basis, repeat=2):
        need(f.hurwitz(f.multiply(a, b)), 'Hurwitz basis closure')
    rounding = Counter()
    for numerators in product(range(8), repeat=4):
        x = tuple(F(v, 8) for v in numerators); q = f.nearest_hurwitz(x)
        distance = f.norm(f.sub(x, q)); need(f.hurwitz(q) and distance <= F(1, 2), 'rounding radius')
        rounding[str(distance)] += 1
    need(rounding['1/2'] > 0, 'sharp rounding witness')
    trace = hashlib.sha256(); ranks = Counter(); cases = divisions = 0

    def check(a):
        nonlocal cases, divisions
        result = f.factor_dyadic(a); divisions += check_certificate(a, result, source)
        cases += 1; ranks[result['rank']] += 1
        trace.update(encoded([a, result]).encode())
        return result

    alphabet = [f.ZERO, f.ONE, basis[1], basis[2], omega]
    for entries in product(alphabet, repeat=4):
        check([list(entries[:2]), list(entries[2:])])
    exhaustive = cases
    rng = random.Random(20261118)

    def random_q():
        return tuple(F(rng.randrange(-7, 8), 1 << rng.randrange(4)) for _ in range(4))

    structured = 0
    for m, n in [(1, 1), (1, 5), (5, 1), (2, 3), (3, 2), (3, 4), (4, 3), (4, 4), (5, 4), (4, 5)]:
        for r in range(min(m, n)+1):
            c = [[(f.ONE if i == k else f.ZERO) if i < r else random_q() for k in range(r)] for i in range(m)]
            b = [[(f.ONE if k == j else f.ZERO) if j < r else random_q() for j in range(n)] for k in range(r)]
            a = matmul(c, b, n, source.multiply)
            for _ in range(3):
                if m > 1:
                    i, j = rng.sample(range(m), 2); q = random_q()
                    a[i] = [source.add(x, source.multiply(q, y)) for x, y in zip(a[i], a[j])]
                if n > 1:
                    i, j = rng.sample(range(n), 2); q = random_q()
                    for row in a:
                        row[i] = source.add(row[i], source.multiply(row[j], q))
            result = check(a); need(result['rank'] == r, 'constructed rank family'); structured += 1
    dense = 0
    for m, n in [(2, 5), (5, 2), (3, 3), (4, 4), (5, 5)]:
        check([[random_q() for _ in range(n)] for _ in range(m)]); dense += 1
    witness_inputs = dict(source_gap=source.RESPONSE,
                          odd_pivot=[[(9,0,0,0),(15,0,0,0)],[(15,0,0,0),(25,0,0,0)]],
                          zero_rectangular=[[f.ZERO]*3 for _ in range(2)],
                          quarter_scalar=[[(F(1,4),0,0,0)]])
    witnesses = {name: dict(input=a, certificate=check(a)) for name, a in witness_inputs.items()}
    a, b = (F(1),F(0),F(1),F(0)), (F(1),F(1),F(0),F(0))
    quotient = f.multiply(a, f.inverse(b)); q = f.nearest_hurwitz(quotient)
    need(f.norm(f.sub(a, f.multiply(q, b))) == 0, 'left quotient witness')
    wrong = f.nearest_hurwitz(f.multiply(f.inverse(b), a))
    need(f.norm(f.sub(a, f.multiply(wrong, b))) > f.norm(b)/2, 'wrong product order not detected')
    integral = tuple(F((x+F(1,2)).numerator//(x+F(1,2)).denominator) for x in quotient)
    need(f.norm(f.sub(a, f.multiply(integral, b))) == f.norm(b), 'integral-only stagnation')
    bad = [[], [[]], [1], [[(1,0,0)]], [[(1.0,0,0,0)]], [[(F(1,3),0,0,0)]], [[f.ONE],[f.ONE,f.ZERO]]]
    for value in bad:
        try:
            f.factor_dyadic(value)
        except ValueError:
            pass
        else:
            raise ValueError('invalid factor input accepted')
    try:
        f.reduce_hurwitz([[(F(1,2),0,0,0)]])
    except ValueError:
        pass
    else:
        raise ValueError('mixed half-integer order accepted')
    for kind in ('quotient', 'factor', 'width'):
        item = deepcopy(witnesses['source_gap']['certificate'])
        if kind == 'quotient':
            i = next(i for i, step in enumerate(item['steps']) if step[0] == 'reduce')
            step = list(item['steps'][i]); step[4] = f.scale(step[4], -1); item['steps'][i] = tuple(step)
        elif kind == 'factor':
            item['left'][0][0] = f.add(item['left'][0][0], f.ONE)
        else:
            item['rank'] = 0; item['left'] = [[] for _ in item['left']]; item['right'] = []
        try:
            check_certificate(witness_inputs['source_gap'], item, source)
        except ValueError:
            pass
        else:
            raise ValueError('changed certificate accepted')
    return dict(exhaustive_two_by_two=exhaustive, structured_rectangular=structured,
                dense_rectangular=dense, total_matrices=cases, rank_histogram=dict(sorted(ranks.items())),
                euclidean_divisions=divisions, certificate_trace_sha256=trace.hexdigest(),
                rounding_grid=4096, rounding_distance_histogram=dict(sorted(rounding.items())),
                multiplication_basis_pairs=16, order_basis_products=16, source_replay=old,
                rejection_controls=len(bad)+1, certificate_mutations=3,
                order_and_integral_stagnation_controls=2, witnesses=witnesses)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args(); result = json.loads(encoded(calculate()))
    if args.write_result:
        (PACKAGE/'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(result == json.loads((PACKAGE/'RESULT.json').read_text()), 'receipt mismatch')
    print('PASS_DYADIC_QUATERNION_RANK_FACTORIZATION exact rank and denominator certificates')


if __name__ == '__main__':
    main()
