#!/usr/bin/env python3
"""Exact structural corroboration; not a census or proof of the common-J lemma."""
from fractions import Fraction
from itertools import product
import json

D = 9
ZERO = frozenset()
ONE = frozenset({(0,) * D})


def need(ok, message):
    if not ok:
        raise ValueError(message)


def add(a, b):
    return a ^ b


def mul(a, b):
    out = set()
    for x in a:
        for y in b:
            z = tuple(u + v for u, v in zip(x, y))
            if z in out:
                out.remove(z)
            else:
                out.add(z)
    return frozenset(out)


def mono(i, amount=1):
    return frozenset({tuple(amount if j == i else 0 for j in range(D))})


def identity(n):
    return tuple(tuple(ONE if i == j else ZERO for j in range(n)) for i in range(n))


def mm(a, b):
    return tuple(tuple(sum_poly(mul(a[i][k], b[k][j]) for k in range(len(b)))
                       for j in range(len(b[0]))) for i in range(len(a)))


def sum_poly(polys):
    out = ZERO
    for p in polys:
        out ^= p
    return out


def factor(n, z):
    return tuple(tuple((ONE if i == j else ZERO) ^ (z ^ ONE if n[i][j] else ZERO)
                       for j in range(len(n))) for i in range(len(n)))


def sub(a, indices):
    return tuple(tuple(a[i][j] for j in indices) for i in indices)


def unit(i, n=4):
    return tuple(tuple(int(r == c == i) for c in range(n)) for r in range(n))


def binary_mul(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(len(a))) % 2
                       for j in range(len(a))) for i in range(len(a)))


def projectors():
    outer = set()
    for x in product((0, 1), repeat=4):
        for y in product((0, 1), repeat=4):
            if sum(a*b for a, b in zip(x, y)) % 2:
                outer.add(tuple(tuple(a*b for b in y) for a in x))
    brute = set()
    for bits in range(1 << 16):
        rows = tuple(tuple((bits >> (4*i+j)) & 1 for j in range(4)) for i in range(4))
        nonzero = {r for r in rows if any(r)}
        if len(nonzero) == 1 and binary_mul(rows, rows) == rows:
            brute.add(rows)
    need(outer == brute and len(outer) == 120, 'projector census disagrees')
    return sorted(outer)


def cyclic(n):
    reach = [[bool(n[i][j]) and i != j for j in range(4)] for i in range(4)]
    for k in range(4):
        for i in range(4):
            for j in range(4):
                reach[i][j] |= reach[i][k] and reach[k][j]
    return any(reach[i][i] for i in range(4))


def off(n):
    return tuple(n[i][j] for i in range(4) for j in range(4) if i != j)


def block_check():
    all_n = projectors()
    cycles = [n for n in all_n if cyclic(n)]
    need(len(cycles) == 12, 'cyclic count')
    shapes = {'none': 0, 'incoming': 0, 'outgoing': 0}
    products_checked = 0
    for n in cycles:
        need(sum(off(p) == off(n) for p in all_n) == 1, 'cyclic lift uniqueness')
        s = [i for i in range(4) if n[i][i]]
        need(len(s) == 3, 'intersection must have size three')
        t, = set(range(4)) - set(s)
        need(sub(n, s) == ((1, 1, 1),) * 3, 'literal core is not J')
        upper = [n[i][t] for i in s]
        lower = [n[t][i] for i in s]
        need(upper in ([0]*3, [1]*3) and lower in ([0]*3, [1]*3), 'tail not uniform')
        need(not (any(upper) and any(lower)), 'feedback makes invalid block split')
        shape = 'incoming' if any(upper) else 'outgoing' if any(lower) else 'none'
        shapes[shape] += 1
        alphabet = [n] + [unit(i) for i in range(4)]
        for a, b in product(alphabet, repeat=2):
            aa, bb = factor(a, mono(0)), factor(b, mono(1))
            full = mm(aa, bb)
            need(sub(full, s) == mm(sub(aa, s), sub(bb, s)), 'core product projection')
            need(sub(full, [t]) == mm(sub(aa, [t]), sub(bb, [t])), 'singleton projection')
            products_checked += 1
        # Ordered eight-factor fixture, with unrelated formal addresses.
        word = [alphabet[i] for i in (0, 1, 0, 2, 3, 0, 4, 1)]
        full, core, single = identity(4), identity(3), identity(1)
        for j, p in enumerate(word):
            f = factor(p, mono(j))
            full, core, single = mm(full, f), mm(core, sub(f, s)), mm(single, sub(f, [t]))
        need(sub(full, s) == core and sub(full, [t]) == single, 'ordered projection')
    need(shapes == {'none': 4, 'incoming': 4, 'outgoing': 4}, 'tail shape census')
    # Mutating the common projector to opposite tails supplies actual feedback.
    upper = ((1, 1, 1, 1),)*3 + ((0, 0, 0, 0),)
    lower = tuple(tuple(upper[j][i] for j in range(4)) for i in range(4))
    a, b = factor(upper, mono(0)), factor(lower, mono(1))
    need(sub(mm(a, b), [0, 1, 2]) != mm(sub(a, [0, 1, 2]), sub(b, [0, 1, 2])),
         'opposite-tail mutant failed to expose missing hypothesis')
    return shapes, products_checked


def common_j_terminal():
    # Corroborates only the final two-run calculation of the inherited lemma.
    j = ((1, 1, 1),)*3
    b, c = mono(0), mono(1)
    ds = [mono(i+2) for i in range(3)]
    diagonal = tuple(tuple(ds[i] if i == k else ZERO for k in range(3)) for i in range(3))
    p = mm(mm(factor(j, b), diagonal), factor(j, c))
    for i in range(3):
        for k in range(3):
            if i != k:
                want = mul(b ^ ONE, ds[k]) ^ mul(c ^ ONE, ds[i])
                want ^= mul(mul(b ^ ONE, c ^ ONE), sum_poly(ds))
                need(p[i][k] == want, 'two-run off-diagonal formula')
    need(p[1][0] ^ p[2][0] == mul(c ^ ONE, ds[1] ^ ds[2]), 'row difference 1')
    need(p[0][2] ^ p[1][2] == mul(c ^ ONE, ds[0] ^ ds[1]), 'row difference 2')
    scalar = tuple(tuple(mono(2) if i == k else ZERO for k in range(3)) for i in range(3))
    need(mm(mm(factor(j, b), scalar), factor(j, mono(0, -1))) == scalar, 'inverse runs')
    need(mm(mm(factor(j, b), diagonal), factor(j, mono(0, -1))) != diagonal,
         'unequal-diagonal mutant incorrectly accepted')


def endpoint_controls():
    p = identity(4)
    for i in range(3):
        for axis in range(3):
            p = mm(p, factor(unit(i), mono(3*axis+axis)))
    target_address = frozenset({(1, 0, 0, 0, 1, 0, 0, 0, 1)})
    target = tuple(tuple((target_address if i < 3 else ONE) if i == j else ZERO
                         for j in range(4)) for i in range(4))
    need(p == target, 'nine-call exact arbitrary-input endpoint')
    damaged = mm(p, factor(unit(2), mono(8, -1)))
    need(damaged != target, 'deleted call not detected')
    # [2E00] != [0] over torsion-free addresses, despite equality modulo 2.
    alias = mm(factor(unit(0), mono(0)), factor(unit(0), mono(0)))
    need(alias != identity(4), 'torsion-free double address lost')
    mod_two = tuple(tuple(frozenset(tuple(v % 2 for v in exponent) for exponent in cell)
                         for cell in row) for row in alias)
    need(mod_two == identity(4), 'torsion quotient control fixture')
    # A proper GL change need not preserve a diagonal target: forbidden shortcut.
    s = [list(row) for row in identity(4)]
    s[0][3] = ONE
    s = tuple(tuple(row) for row in s)
    need(mm(mm(s, target), s) != target, 'noncoordinate target-conjugation control')


def rational_rank(rows):
    rows = [[Fraction(x) for x in row] for row in rows]
    pivot = 0
    for column in range(len(rows[0])):
        found = next((i for i in range(pivot, len(rows)) if rows[i][column]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        scale = rows[pivot][column]
        rows[pivot] = [x / scale for x in rows[pivot]]
        for i in range(len(rows)):
            if i != pivot:
                scale = rows[i][column]
                rows[i] = [x - scale*y for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
    return pivot


def mixed_relation_projection():
    # Six independent matrix units and two same-row rank-one sums.
    frames = [tuple(int(i == j) for j in range(9)) for i in range(6)]
    frames += [tuple(frames[0][j] + frames[k][j] for j in range(9)) for k in (1, 2)]
    need(all(rational_rank([f[0:3], f[3:6], f[6:9]]) == 1 for f in frames),
         'fixture must use rational rank-one frames')
    need(len(frames) - rational_rank(frames) == 2, 'original relation nullity')
    # E_tt is assigned frame zero; BOTH independent relations meet this call.
    relations = ((-1, -1, 0, 0, 0, 0, 1, 0), (-1, 0, -1, 0, 0, 0, 0, 1))
    need(all(all(sum(r[i]*frames[i][j] for i in range(8)) == 0 for j in range(9))
             for r in relations), 'mixed relation fixture')
    retained = frames[1:]
    need(len(retained) - rational_rank(retained) == 1, 'subset relation kernel')
    need(all(r[0] != 0 for r in relations), 'relations must meet removed singleton')
    # One relation survives, obtained by subtracting the two mixed relations.
    surviving = tuple(relations[0][i] - relations[1][i] for i in range(1, 8))
    need(all(sum(surviving[i]*retained[i][j] for i in range(7)) == 0 for j in range(9)),
         'zero-extension relation injection calibration')


def main():
    shapes, pairs = block_check()
    common_j_terminal()
    endpoint_controls()
    mixed_relation_projection()
    print(json.dumps({'status': 'PASS_AUXILIARY_SPAN_SIX_CYCLIC_LINE',
                      'cyclic_projectors': 12, 'shapes': shapes,
                      'symbolic_pair_products': pairs, 'ordered_eight_call_fixtures': 12,
                      'negative_controls': 5, 'mixed_relation_subset_nullities': [2, 1],
                      'scope': 'structural corroboration; inherited common-J lemma not reproved'}))


if __name__ == '__main__':
    main()
