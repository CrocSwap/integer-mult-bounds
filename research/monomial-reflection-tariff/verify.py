#!/usr/bin/env python3
"""Exact finite corroboration of the monomial-reflection register tariff."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import permutations, product
import json
from math import factorial
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return tuple(range(n)), (0,) * n


def compose(g, h, m):
    p, a = g
    q, b = h
    return tuple(p[q[j]] for j in range(len(p))), tuple(
        (b[j] + a[q[j]]) % m for j in range(len(p)))


def inverse(g, m):
    p, a = g
    q, b = [0] * len(p), [0] * len(p)
    for j, k in enumerate(p):
        q[k], b[k] = j, -a[j] % m
    return tuple(q), tuple(b)


def reflections(m, n):
    out = []
    for i in range(n):
        for a in range(1, m):
            phase = [0] * n
            phase[i] = a
            out.append((tuple(range(n)), tuple(phase)))
        for j in range(i + 1, n):
            for a in range(m):
                p, phase = list(range(n)), [0] * n
                p[i], p[j], phase[i], phase[j] = j, i, a, -a % m
                out.append((tuple(p), tuple(phase)))
    need(len(set(out)) == n * (m - 1) + m * n * (n - 1) // 2,
         'reflection alphabet cardinality')
    return tuple(out)


def balanced_cycles(g, m):
    p, a = g
    seen, count = set(), 0
    for start in range(len(p)):
        if start in seen:
            continue
        j, phase = start, 0
        for _ in range(len(p)):
            seen.add(j)
            phase = (phase + a[j]) % m
            j = p[j]
            if j == start:
                break
        else:
            raise ValueError('cycle did not close')
        count += phase == 0
    return count


def factor(g, m):
    n, current, word = len(g[0]), g, []
    for _ in range(n):
        i = next((i for i in range(n) if current[0][i] != i), None)
        if i is None:
            break
        j, phase = current[0][i], current[1][i]
        p, a = list(range(n)), [0] * n
        p[i], p[j], a[i], a[j] = j, i, phase, -phase % m
        t = tuple(p), tuple(a)
        current = compose(current, t, m)
        need(current[0][j] == j and current[1][j] == 0, 'peel fixed coordinate')
        word.append(inverse(t, m))
    for i in range(n):
        phase = current[1][i]
        if phase:
            a = [0] * n
            a[i] = -phase % m
            t = tuple(range(n)), tuple(a)
            current = compose(current, t, m)
            word.append(inverse(t, m))
    need(current == identity(n), 'peeling endpoint')
    return tuple(word)


def dense(g, prime, root):
    p, a = g
    return [[pow(root, a[j], prime) if p[j] == i else 0
             for j in range(len(p))] for i in range(len(p))]


def multiply(a, b, prime):
    n = len(a)
    return [[sum(a[i][k] * b[k][j] for k in range(n)) % prime
             for j in range(n)] for i in range(n)]


def rank(a, prime):
    a = [[v % prime for v in row] for row in a]
    rows, cols, r = len(a), len(a[0]), 0
    for col in range(cols):
        pivot = next((i for i in range(r, rows) if a[i][col]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        scale = pow(a[r][col], -1, prime)
        a[r] = [v * scale % prime for v in a[r]]
        for i in range(r + 1, rows):
            scale = a[i][col]
            a[i] = [(x - scale * y) % prime for x, y in zip(a[i], a[r])]
        r += 1
    return r


def domain(m, n, prime, root):
    need(1 <= m <= 6 and 1 <= n <= 4, 'finite verification domain')
    need(prime in (5, 7, 11) and pow(root, m, prime) == 1,
         'root domain')
    need(all(pow(root, k, prime) != 1 for k in range(1, m)), 'primitive root')
    e, generators = identity(n), reflections(m, n)
    order, queue, distance = factorial(n) * m ** n, [e], {e: 0}
    transitions = 0
    for cursor in range(order):
        need(cursor < len(queue), 'Cayley search exhausted too soon')
        g = queue[cursor]
        for t in generators:
            h = compose(t, g, m)
            transitions += 1
            if h not in distance:
                need(len(queue) < order, 'Cayley search exceeded group order')
                distance[h] = distance[g] + 1
                queue.append(h)
    expected = {(p, a) for p in permutations(range(n)) for a in product(range(m), repeat=n)}
    need(set(queue) == expected, 'complete independent object enumeration')
    for g in queue:
        length = n - balanced_cycles(g, m)
        need(distance[g] == length, 'exact shortest address tariff')
        matrix = dense(g, prime, root)
        need(rank([[matrix[i][j] - (i == j) for j in range(n)]
                   for i in range(n)], prime) == length, 'displacement rank')
        word, state, represented = factor(g, m), e, dense(e, prime, root)
        need(len(word) == length and all(t in generators for t in word), 'attaining word')
        for t in word:
            state = compose(t, state, m)
            represented = multiply(dense(t, prime, root), represented, prime)
        need(state == g and represented == matrix, 'formal label and dense endpoints')
    for t in generators:
        a = dense(t, prime, root)
        need(rank([[a[i][j] - (i == j) for j in range(n)]
                   for i in range(n)], prime) == 1, 'paid displacement rank one')
    return {'m': m, 'n': n, 'prime': prime, 'root': root, 'objects': order,
            'transitions': transitions, 'distance_histogram': dict(sorted(Counter(distance.values()).items()))}


def scalar_state(b, e):
    return [[{e: Fraction(v)} if v else {} for v in row] for row in b]


def scalar_left(b, state):
    size, out = len(b), [[{} for _ in b] for _ in b]
    for i, j, k in product(range(size), repeat=3):
        for g, coefficient in state[k][j].items():
            out[i][j][g] = out[i][j].get(g, 0) + b[i][k] * coefficient
    return [[{g: v for g, v in cell.items() if v} for cell in row] for row in out]


def paid_left(state, t, u, v, m):
    size, out = len(state), [[dict(cell) for cell in row] for row in state]
    for i, j, k in product(range(size), repeat=3):
        scale = u[i] * v[k]
        if not scale:
            continue
        for g, coefficient in state[k][j].items():
            h, value = compose(t, g, m), scale * coefficient
            out[i][j][h] = out[i][j].get(h, 0) + value
            out[i][j][g] = out[i][j].get(g, 0) - value
    return [[{g: c for g, c in cell.items() if c} for cell in row] for row in out]


def endpoint(targets, e):
    return [[{targets[i]: Fraction(1)} if i == j else {}
             for j in range(len(targets))] for i in range(len(targets))]


def formal_fixtures():
    m, n, e = 3, 2, identity(2)
    b = ((1, 1, 0), (0, 1, 1), (1, 0, 1))
    c = tuple(tuple(Fraction(v, 2) for v in row) for row in
              ((1, -1, 1), (1, 1, -1), (-1, 1, 1)))
    need(all(sum(b[i][k] * c[k][j] for k in range(3)) == (i == j)
             for i, j in product(range(3), repeat=2)), 'scalar gauge inverse')
    group = tuple((p, a) for p in permutations(range(n)) for a in product(range(m), repeat=n))
    fixtures, events, omissions, inverses = 0, 0, 0, 0
    for g, h in product(group, repeat=2):
        calls = tuple((j, t) for j, target in enumerate((g, h)) for t in factor(target, m))
        state = scalar_state(b, e)
        for j, t in calls:
            u, v = tuple(b[i][j] for i in range(3)), c[j]
            need(sum(x * y for x, y in zip(u, v)) == 1, 'idempotent call')
            state = paid_left(state, t, u, v, m)
        state = scalar_left(c, state)
        need(state == endpoint((g, h, e), e), 'complete rational formal dirty endpoint')
        state = scalar_left(b, state)
        for j, t in reversed(calls):
            u, v = tuple(b[i][j] for i in range(3)), c[j]
            state = paid_left(state, inverse(t, m), u, v, m)
        state = scalar_left(c, state)
        need(state == endpoint((e, e, e), e), 'formal inverse restoration')
        inverses += 1
        fixtures, events = fixtures + 1, events + len(calls)
        if calls:
            state = scalar_state(b, e)
            for j, t in calls[1:]:
                state = paid_left(state, t, tuple(b[i][j] for i in range(3)), c[j], m)
            need(scalar_left(c, state) != endpoint((g, h, e), e), 'omitted call detection')
            omissions += 1
    return {'ordered_target_pairs': fixtures, 'paid_events': events,
            'complete_inverse_checks': inverses, 'omitted_first_calls_rejected': omissions}


def controls():
    e = identity(2)
    g = ((1, 0), (1, 0))
    need(2 - balanced_cycles(g, 3) == 2, 'unbalanced two-cycle costs two')
    need(factor(g, 3) != tuple(reversed(factor(g, 3))), 'noncommuting order witness')
    need(compose(*factor(g, 3), 3) != g, 'wrong chronological order rejected')
    all_group = tuple((p, a) for p in permutations(range(2)) for a in product(range(3), repeat=2))
    norm = [[sum(dense(h, 7, 2)[i][j] for h in all_group) % 7
             for j in range(2)] for i in range(2)]
    need(norm == [[0, 0], [0, 0]], 'representation-kernel fixture')
    leaked = endpoint((g, e), e)
    leaked[0][1] = {h: Fraction(1) for h in all_group}
    need(leaked != endpoint((g, e), e), 'formal norm leak must remain nonzero')
    try:
        domain(3, 2, 7, 1)
    except ValueError as error:
        need(str(error) == 'primitive root', 'wrong root rejection reason')
    else:
        raise ValueError('nonprimitive root accepted')
    return {'controls': ['unbalanced_cycle', 'noncommuting_fixture', 'wrong_order',
                         'zero_represented_norm', 'nonzero_formal_leak', 'nonprimitive_root'],
            'norm_terms': len(all_group)}


def main():
    package = Path(__file__).resolve().parent
    root = package.parent.parent
    sources = json.loads((package / 'SOURCES.json').read_text())
    for source in sources['files']:
        if source['usage'] == 'input':
            need(sha256((root / source['path']).read_bytes()).hexdigest() == source['sha256'],
                 'source hash: ' + source['path'])
    cases = ((1, 4, 5, 1), (2, 4, 5, 4), (3, 3, 7, 2), (3, 4, 7, 2),
             (4, 3, 5, 2), (5, 3, 11, 3), (6, 3, 7, 3))
    results = [domain(*case) for case in cases]
    result = {'marker': 'PASS_MONOMIAL_REFLECTION_TARIFF', 'domains': results,
              'objects': sum(row['objects'] for row in results),
              'transitions': sum(row['transitions'] for row in results),
              'formal': formal_fixtures(), 'controls': controls()}
    names = ('README.md', 'PROOF.md', 'TASK.json', 'SOURCES.json', 'VERIFY.json', 'verify.py')
    result['package_sha256'] = {name: sha256((package / name).read_bytes()).hexdigest() for name in names}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
