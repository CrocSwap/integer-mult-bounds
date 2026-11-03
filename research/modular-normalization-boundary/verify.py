#!/usr/bin/env python3
"""Check modular metrics and the complete paid query word.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
Nick Petalas supplied the released metric and three-coordinate proposals.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent


def need(ok, why):
    if not ok:
        raise ValueError(why)


def distance(x, y, n):
    r = (x-y) % n
    return min(r, n-r)


def det(q):
    return q[0][0]*q[1][1]-q[0][1]*q[1][0]


def inverse(q, n):
    a = pow(det(q), -1, n)
    return [[a*q[1][1] % n, -a*q[0][1] % n],
            [-a*q[1][0] % n, a*q[0][0] % n]]


def mv(q, v, n):
    return [sum(a*b for a, b in zip(row, v)) % n for row in q]


def word(n, expanded=False):
    a = pow(3, -1, n)
    prefix = [('add', 0, 2, 1), ('add', 1, 2, -1),
              ('add', 2, 0, 1), ('add', 2, 0, 1), ('add', 2, 1, -1)]
    encode = [('add', 1, 0, 1), ('scale', 0, 3),
              ('add', 0, 1, -1), ('swap', 0, 1)]
    decode = [('swap', 0, 1), ('add', 0, 1, 1),
              ('scale', 0, a), ('add', 1, 0, -1)]
    undo = [('add', dst, src, -c) for _, dst, src, c in reversed(prefix)]
    ops = prefix+encode+[('query', 0)]+decode+undo
    if expanded:
        result = []
        for op in ops:
            if op[0] == 'swap':
                _, x, y = op
                result += [('add', x, y, 1), ('add', y, x, -1),
                           ('add', x, y, 1), ('negate', y)]
            else:
                result.append(op)
        ops = result
    return ops


def execute(state, ops, q, n):
    state = [list(v) for v in state]
    counts = Counter()
    reductions = moves = 0
    for op in ops:
        kind, target, *args = op
        counts[kind] += 1
        if kind == 'add':
            source, coefficient = args
            state[target] = [(x+coefficient*y) % n
                             for x, y in zip(state[target], state[source])]
            reductions += len(state[target])
        elif kind == 'scale':
            state[target] = [x*args[0] % n for x in state[target]]
            reductions += len(state[target])
        elif kind == 'negate':
            state[target] = [-x % n for x in state[target]]
            reductions += len(state[target])
        elif kind == 'swap':
            source = args[0]
            for j in range(len(state[target])):
                saved = state[target][j]
                state[target][j] = state[source][j]
                state[source][j] = saved
                moves += 3
        elif kind == 'query':
            state[target] = mv(q, state[target], n)
        else:
            raise ValueError('Unknown operation')
        need(all(type(x) is int and 0 <= x < n for v in state for x in v),
             'Residue boundary')
    return state, dict(counts), reductions, moves


def reverse_word(ops, n):
    result = []
    for op in reversed(ops):
        if op[0] == 'add':
            result.append((*op[:3], -op[3]))
        elif op[0] == 'scale':
            result.append((*op[:2], pow(op[2], -1, n)))
        else:
            result.append(op)
    return result


def endpoint(state, q, n):
    x, y, z = state
    a = pow(3, -1, n)
    total = [(u+v) % n for u, v in zip(x, y)]
    changed = mv(q, total, n)
    delta = [(u-v)*a % n for u, v in zip(changed, total)]
    return [[(u+v) % n for u, v in zip(x, delta)],
            [(u+2*v) % n for u, v in zip(y, delta)], list(z)]


def basis(d):
    return [[[int(row*d+j == k) for j in range(d)] for row in range(3)]
            for k in range(3*d)]


def metric_checks():
    pairs = contexts = lifts = 0
    records = []
    for b in range(1, 7):
        n = 1 << b
        for p in range(1, n, 2):
            a = pow(p, -1, n)
            m = min(a, n-a)
            s = a if a <= n//2 else a-n
            ratios, lifted = [], []
            for x in range(n):
                for y in range(x+1, n):
                    d = distance(x, y, n)
                    ratios.append(F(distance(a*x, a*y, n), d))
                    lifted.append(F(abs(a*x % n-a*y % n), d))
                    need(abs(s*x-s*y) == m*abs(x-y), 'Affine line lift')
                    pairs += 1
            need(max(ratios) == m, 'Exact quotient constant')
            need(max(lifted) == n-m, 'Exact periodic attainer')
            if 1 < p < n:
                need(p*m >= n-1, 'Fixed odd normalization lower bound')
            records.append([b, p, a, m, n-m])
            contexts += 1
    # This finite lift search is independent of the affine construction.
    for n in (2, 4, 8):
        for a in range(1, n, 2):
            best = None
            for shifts in product((-1, 0, 1), repeat=n-1):
                values = [0]+[(a*x % n)+k*n for x, k in enumerate(shifts, 1)]
                cost = max(abs(values[(x+1) % n]-values[x]) for x in range(n))
                best = cost if best is None else min(best, cost)
                lifts += 1
            need(best == n-min(a, n-a), 'Enumerated periodic lifts')
    for b in range(2, 257):
        n = 1 << b
        a = pow(3, -1, n)
        need(min(a, n-a) == (n-(-1)**b)//3, 'Inverse-three parity formula')
    return dict(contexts=contexts, unordered_pairs=pairs, bounded_periodic_lifts=lifts,
                inverse_three_precisions=255, constants=records)


def program_checks():
    contexts = columns = dirty = 0
    digest = sha256()
    for n in (2, 4, 8):
        for entries in product(range(n), repeat=4):
            q = [list(entries[:2]), list(entries[2:])]
            if not det(q) & 1:
                continue
            qi = inverse(q, n)
            for expanded in (False, True):
                ops = word(n, expanded)
                need(len(ops) == (25 if expanded else 19), 'Complete word length')
                for state in basis(2):
                    out, counts, reductions, moves = execute(state, ops, q, n)
                    need(out == endpoint(state, q, n), 'Independent full endpoint')
                    back, _, _, _ = execute(out, reverse_word(ops, n), qi, n)
                    need(back == state and out[2] == state[2], 'Inverse and outside dirt')
                    expected = ({'add': 20, 'scale': 2, 'negate': 2, 'query': 1}
                                if expanded else {'add': 14, 'scale': 2, 'swap': 2, 'query': 1})
                    need(counts == expected and reductions == (48 if expanded else 32)
                         and moves == (0 if expanded else 12), 'Every paid instruction')
                    digest.update(json.dumps(out, separators=(',', ':')).encode())
                    columns += 1
                if n == 2:
                    for bits in product(range(2), repeat=6):
                        state = [list(bits[i:i+2]) for i in range(0, 6, 2)]
                        out, _, _, _ = execute(state, ops, q, n)
                        need(out == endpoint(state, q, n), 'Exhaustive binary dirt')
                        dirty += 1
            contexts += 1
    rng = random.Random(314159)
    wider = 0
    for b in (4, 5, 16, 64, 257):
        n = 1 << b
        for d in (1, 3, 5):
            q = [[int(i == j)+(rng.randrange(n) if i < j else 0)
                  for j in range(d)] for i in range(d)]
            state = [[rng.randrange(n) for _ in range(d)] for _ in range(3)]
            for expanded in (False, True):
                out, _, _, _ = execute(state, word(n, expanded), q, n)
                need(out == endpoint(state, q, n), 'Wide dirty endpoint')
                wider += 1
    return dict(invertible_queries=contexts, basis_forward_inverse_checks=columns,
                binary_dirty_cases=dirty, wide_cases=wider, full_output_sha256=digest.hexdigest())


def controls():
    n, q = 32, [[0, 1], [1, 0]]
    omissions = 0
    for expanded in (False, True):
        ops = word(n, expanded)
        for j in range(len(ops)):
            bad = ops[:j]+ops[j+1:]
            need(any(execute(v, bad, q, n)[0] != endpoint(v, q, n) for v in basis(2)),
                 'Instruction omission detected')
            omissions += 1
    three = [('add', 0, 1, 1), ('add', 1, 0, -1), ('add', 0, 1, 1)]
    v = [[1], [2], [3]]
    need(execute(v, three, [[1]], n)[0] == [[2], [31], [3]], 'Signed swap control')
    need(execute(v, three+[('negate', 1)], [[1]], n)[0] == [[2], [1], [3]],
         'Paid SWAP expansion')
    need(distance(7, 0, 8) == 1 and abs(3*7-0) == 21, 'Lift domain control')
    need(max(abs(3*((x+1) % 8) % 8-(3*x % 8)) for x in range(8)) == 5,
         'Periodic constant is five, not three')
    a = pow(3, -1, n)
    out = execute([[0, 0], [1, 0], [0, 0]], word(n), q, n)[0]
    need(out[0][1] == a and distance(a, 0, n) == 11, 'Full endpoint expansion')
    observed = F(1, 2*n)
    need(abs(observed) == abs(observed-F(1, n)), 'Ambiguous observation')
    need(F(distance(a, 0, n), n)/2 == F(11, 64), 'Output ambiguity')
    try:
        pow(2, -1, n)
    except ValueError:
        pass
    else:
        raise ValueError('Nonunit accepted')
    need(a*3 % n == 1 and F(1, 3) != a, 'Residue inverse is not a real coefficient')
    return dict(instruction_omissions=omissions, paid_swap=True, lift_domain=True,
                periodic_constant=True, full_query_expansion=True,
                numerical_ambiguity=True, nonunit=True, real_division=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    receipt = dict(schema_version=1, metrics=metric_checks(),
                   query_word=program_checks(), controls=controls())
    if args.output:
        with args.output.open('x', encoding='utf-8') as stream:
            json.dump(receipt, stream, indent=2, sort_keys=True)
            stream.write('\n')
    else:
        need(receipt == json.loads((HERE/'RESULT.json').read_text()), 'Stored receipt mismatch')
    print('PASS_MODULAR_NORMALIZATION_BOUNDARY', receipt['metrics']['contexts'],
          'metric contexts;', receipt['query_word']['invertible_queries'],
          'complete invertible queries;', receipt['controls']['instruction_omissions'],
          'instruction controls')


if __name__ == '__main__':
    main()
