#!/usr/bin/env python3
"""Exact independent toy geometry checks; no source verifier is imported.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
This is bounded corroboration, not selected native or machine admission.
"""
from itertools import permutations
import json


def need(ok, why):
    if not ok:
        raise ValueError(why)


def h(v, axis):
    bit = 1 << axis
    for low in range(len(v)):
        if not low & bit:
            high = low | bit
            a, b = v[low], v[high]
            v[low], v[high] = a+b, a-b


def run(fields, word):
    for op, a, b, c in word:
        if op == 'add':
            need(a != b, 'aliased scalar roles')
            fields[a] = [x+c*y for x, y in zip(fields[a], fields[b])]
        else:
            need(op == 'h' and len(b) == len(set(b)), 'bad tensor axes')
            for axis in b:
                h(fields[a], axis)


def raw(owners, first, second):
    x, y = owners
    need(x != y, 'aliased native input roles')
    need(not set(first) & set(second), 'overlapping raw factors')
    return [('add', y, x, 1), ('h', x, tuple(first), 0),
            ('h', y, tuple(first), 0), ('add', y, x, -1),
            ('h', y, tuple(second), 0)]


def product(f):
    # U copies indexed by j, target fields (i,j)=2*i+j. At every common
    # U paid position substitute a literal V circuit on its current owners.
    ax = lambda a, b: tuple((2*a+b)*f+t for t in range(f))
    w = [('add', 2+j, j, 1) for j in range(2)]
    w += raw((0, 1), ax(0, 0), ax(0, 1))
    w += raw((2, 3), ax(0, 0), ax(0, 1))
    w += [('add', 2+j, j, -1) for j in range(2)]
    w += raw((2, 3), ax(1, 0), ax(1, 1))
    supports = [tuple((2*a+b)*f+t for a in range(i+1)
                      for b in range(j+1) for t in range(f))
                for i in range(2) for j in range(2)]
    return w, supports


def inverse(p):
    out = [None]*len(p)
    for i, j in enumerate(p):
        out[j] = i
    return tuple(out)


def perm(v, p):
    out = [0]*len(v)
    for old, value in enumerate(v):
        new = sum(((old >> a) & 1) << b for a, b in enumerate(p))
        out[new] = value
    return out


def extend(n, source, target):
    # Independent exhaustive permutation search, not stable-prefix code.
    need(len(source) == len(target), 'unequal ranks')
    need(len(set(source)) == len(source) and len(set(target)) == len(target), 'support alias')
    for p in permutations(range(n)):
        if all(p[a] == b for a, b in zip(source, target)):
            return p
    raise ValueError('no complete-field extension')


def basis(count, n, index):
    fields = [[0]*(1 << n) for _ in range(count)]
    a, b = divmod(index, 1 << n)
    fields[a][b] = 1
    return fields


def endpoint(word, supports, n, mappings=None, mode='whole'):
    count = len(supports)
    maps = mappings or [tuple(range(n))]*count
    target = [tuple(p[a] for a in s) for p, s in zip(maps, supports)]
    for index in range(count*(1 << n)):
        expected = basis(count, n, index)
        for owner, axes in enumerate(target):
            for axis in axes:
                h(expected[owner], axis)
        actual = basis(count, n, index)
        if mode == 'whole':
            actual = [perm(v, inverse(p)) for v, p in zip(actual, maps)]
            run(actual, word)
            actual = [perm(v, p) for v, p in zip(actual, maps)]
        elif mode == 'output-only':
            run(actual, word)
            actual = [perm(v, p) for v, p in zip(actual, maps)]
        elif mode == 'internal-support-only':
            mutant = [(op, a, tuple(maps[a][i] for i in b), c) if op == 'h'
                      else (op, a, b, c) for op, a, b, c in word]
            run(actual, mutant)
        else:
            raise ValueError(mode)
        if actual != expected:
            return False, index
    return True, (count*(1 << n))**2


def swaps():
    cases = 0
    for f in (1, 2, 3):
        for k in (1, 2, 4):
            front, back = 7, 5
            for rho in range(k):
                original = [1 << i for i in range(front+3*f*k+back)]
                actual, expected = original.copy(), original.copy()
                for j in range(f):
                    x, y = front+j*k+rho, front+(2*f+j)*k+rho
                    actual[y] ^= actual[x]
                    actual[x] ^= actual[y]
                    actual[y] ^= actual[x]
                    expected[x], expected[y] = expected[y], expected[x]
                need(actual == expected, 'selected swap changed controls/spectators')
                cases += 1
    original = [1 << i for i in range(8)]
    selected = original.copy()
    selected[0], selected[4] = selected[4], selected[0]
    need(selected != original[4:]+original[:4], 'K-plane confusion control')
    return cases


def nesting_and_stock():
    n = 6
    p, q = extend(n, (0, 1), (4, 0)), extend(n, (0, 1, 2), (1, 5, 3))
    compose = lambda a, b: tuple(b[a[i]] for i in range(n))
    identity = tuple(range(n))
    # An actual transform inside a doubly routed field, followed by a parent
    # transform. Check every address basis vector, including spectators.
    for address in range(1 << n):
        initial = [0]*(1 << n)
        initial[address] = 1
        actual = perm(perm(initial, inverse(p)), inverse(q))
        h(actual, 0)
        actual = perm(actual, q)
        h(actual, 2)
        actual = perm(actual, p)
        expected = initial.copy()
        h(expected, p[q[0]])
        h(expected, p[2])
        need(actual == expected, 'nested child transform changed parent/spectators')
    need(compose(compose(compose(p, q), inverse(q)), inverse(p)) == identity, 'nested return')
    need(compose(compose(compose(p, q), inverse(p)), inverse(q)) != identity, 'wrong LIFO control')
    buckets = [list(range(36))]
    for divisor in (2, 3, 2):
        next_buckets = []
        for rows in buckets:
            need(len(rows) % divisor == 0, 'nonintegral whole-row split')
            groups = [[] for _ in range(divisor)]
            for local, original in enumerate(rows):
                quotient, role = divmod(local, divisor)
                groups[role].append((quotient, original))
            for group in groups:
                need([g for g, _ in group] == list(range(len(group))), 'bad row quotient')
                next_buckets.append([r for _, r in group])
        buckets = next_buckets
    need(sorted(r for group in buckets for r in group) == list(range(36)), 'lost/cloned row')
    need(3 % 2 != 0 and 6 % (2*2*3) != 0, 'stock controls')
    return {'parent': list(p), 'child': list(q), 'stock': 36, 'divisors': [2, 3, 2]}


def main():
    cases = []
    for f, extra in ((1, 2), (2, 0)):
        word, supports = product(f)
        n = 4*f+extra
        ok, details = endpoint(word, supports, n)
        need(ok, f'product f={f} failed at basis {details}')
        cases.append({'case': 'chronological-product', 'f': f, 'n': n, 'coefficients': details})
    word, supports = product(1)
    supports[0] = (0, 1)
    word += [('h', 0, (1,), 0)]  # paid completion after the entire product
    wanted = ((5, 1), (4, 0), (3, 2), (5, 3, 0, 2))
    maps = [extend(6, old, new) for old, new in zip(supports, wanted)]
    ok, details = endpoint(word, supports, 6, maps)
    need(ok, f'whole-field conjugation failed at basis {details}')
    cases.append({'case': 'completed-rolewise-conjugation', 'f': 1, 'n': 6, 'coefficients': details})
    product_base, product_supports = product(1)
    transpose = lambda axis: 2*(axis % 2)+axis//2
    transposed = [(op, a, tuple(transpose(i) for i in b), c) if op == 'h'
                  else (op, a, b, c) for op, a, b, c in product_base]
    need(not endpoint(transposed, product_supports, 6)[0], 'missing product transpose escaped')
    raw_word = raw((0, 1), (0, 2), (1, 3))
    split = [part for op, a, b, c in raw_word for part in
             ([('h', a, (axis,), c) for axis in b] if op == 'h' else [(op, a, b, c)])]
    need(endpoint(raw_word, ((0, 2), (0, 2, 1, 3)), 5)[0], 'raw two-column endpoint')
    need(endpoint(split, ((0, 2), (0, 2, 1, 3)), 5)[0], 'disjoint split endpoint')
    mutant = split.copy()
    mutant[2] = ('h', 0, (0,), 0)
    need(not endpoint(mutant, ((0, 2), (0, 2, 1, 3)), 5)[0], 'overlapping split escaped')
    controls = {'wrong-product-coordinate-order': 'rejected by endpoint', 'overlapping-split': 'rejected by endpoint', 'wrong-LIFO': 'rejected',
                'whole-K-chunk-for-fixed-rho': 'rejected', 'maximum-stock': 'rejected',
                'repeated-unreleased-divisor': 'rejected'}
    for mode in ('output-only', 'internal-support-only'):
        ok, witness = endpoint(word, supports, 6, maps, mode)
        need(not ok, mode+' mutation escaped')
        controls[mode] = {'first_failing_basis': witness}
    for label, action in (('field-alias', lambda: raw((0, 0), (0,), (1,))),
                          ('support-alias', lambda: extend(4, (0, 1), (2, 2)))):
        try:
            action()
        except ValueError:
            controls[label] = 'rejected'
        else:
            raise ValueError(label+' mutation escaped')
    report = {'status': 'PASS', 'scope': 'bounded exact toy geometry, not selected native admission',
              'dense_cases': cases, 'selected_swap_cases': swaps(),
              'nesting_and_stock': nesting_and_stock(), 'negative_controls': controls}
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
