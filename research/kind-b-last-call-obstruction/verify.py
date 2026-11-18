#!/usr/bin/env python3
"""Check the all-width kind B finishing obstruction.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction
from random import Random
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COEFFICIENTS = (Fraction(1), Fraction(-1), Fraction(2), Fraction(1, 2), Fraction(-2, 3))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def unit(n):
    return tuple(1 << i for i in range(n))


def mul(a, b):
    rows = []
    for row in a:
        value = 0
        while row:
            bit = row & -row
            value ^= b[bit.bit_length()-1]
            row ^= bit
        rows.append(value)
    return tuple(rows)


def transpose(a):
    return tuple(sum(((row >> j) & 1) << i for i, row in enumerate(a)) for j in range(len(a)))


def inv(a):
    n = len(a)
    rows = [row | (1 << (n+i)) for i, row in enumerate(a)]
    for i in range(n):
        j = next(j for j in range(i, n) if rows[j] & (1 << i))
        rows[i], rows[j] = rows[j], rows[i]
        for j in range(n):
            if j != i and rows[j] & (1 << i):
                rows[j] ^= rows[i]
    return tuple(row >> n for row in rows)


def rank2(rows):
    pivots = {}
    for row in rows:
        while row:
            i = row.bit_length()-1
            if i not in pivots:
                pivots[i] = row
                break
            row ^= pivots[i]
    return len(pivots)


def is_free(g):
    m = len(g)//2
    return all(row >> m == 0 for row in g[:m])


def level(g):
    m = len(g)//2
    return rank2(row >> m for row in g[:m])


def call(m, normal):
    paired = ((normal & ((1 << m)-1)) << m) | (normal >> m)
    return tuple((1 << i) ^ (paired if normal & (1 << i) else 0) for i in range(2*m))


def all_free(m):
    def bases(rows):
        if len(rows) == m:
            yield tuple(rows)
        else:
            for x in range(1, 1 << m):
                if rank2([*rows, x]) > len(rows):
                    yield from bases([*rows, x])
    places = [(i, j) for i in range(m) for j in range(i, m)]
    form = tuple(1 << ((i+m) % (2*m)) for i in range(2*m))
    result = []
    for a in bases([]):
        b = transpose(inv(a))
        for mask in range(1 << len(places)):
            s = [0]*m
            for bit, (i, j) in enumerate(places):
                if mask & (1 << bit):
                    s[i] |= 1 << j
                    s[j] |= 1 << i
            lower = mul(b, s)
            g = a + tuple(lower[i] | (b[i] << m) for i in range(m))
            need(is_free(g) and mul(mul(g, form), transpose(g)) == form, 'free symplectic matrix')
            result.append(g)
    need(len(result) == len(set(result)) == 10752, 'three-bit free group')
    return result


def orbit(start, step):
    points = [start]
    point = mul(start, step)
    while point != start:
        need(point not in points, 'orbit closure')
        points.append(point)
        point = mul(point, step)
    return points


def in_span(columns, target):
    pivots = {}
    for v in columns:
        row = list(map(Fraction, v))
        for i in range(len(row)):
            coefficient = row[i]
            if coefficient == 0:
                continue
            if i in pivots:
                row = [x-coefficient*y for x, y in zip(row, pivots[i], strict=True)]
            else:
                pivots[i] = [x/coefficient for x in row]
                break
    row = list(map(Fraction, target))
    for i, pivot in sorted(pivots.items()):
        coefficient = row[i]
        row = [x-coefficient*y for x, y in zip(row, pivot, strict=True)]
    return all(x == 0 for x in row)


def singleton(g, first, last):
    tg = mul(last, g)
    return any(is_free(h) for h in (g, mul(g, first), tg, mul(tg, first)))


def separator(first, shared, last, gamma):
    middle, extra = mul(shared, first), mul(shared, gamma)
    need(is_free(gamma) and level(middle) == 2 and level(mul(last, middle)) == 3, 'finishing premises')
    need(not is_free(mul(extra, first)), 'nonplain extra term')
    mi, ei = inv(middle), inv(extra)
    target, second = mul(last, middle), mul(last, extra)
    q = mul(second, mi)
    if is_free(q):
        third = mul(q, extra)
        weights = {target: (2, 1), second: (1, -1), third: (0, 1)}
        expected = {(target, second), (second, third)}
    else:
        weights = {target: (1, 1), second: (0, -1)}
        expected = {(target, second)}
    need(len(weights) == len(expected)+1, 'distinct support')
    columns = set()
    for point in weights:
        need(not singleton(point, first, last), 'singleton hits separator')
        for paid in (False, True):
            x = mul(last, point) if paid else point
            for inverse in (mi, ei):
                p = mul(x, inverse)
                if is_free(p):
                    left = mul(last, p) if paid else p
                    columns.add((mul(left, middle), mul(left, extra)))
    need(columns == expected, 'complete incident columns')
    for a, b in columns:
        polynomial = Counter()
        for point, shift in ((a, 0), (b, 1)):
            if point in weights:
                exponent, coefficient = weights[point]
                polynomial[exponent+shift] += coefficient
        need(all(x == 0 for x in polynomial.values()), 'separator annihilates every column')
    need(weights[target][1] == 1, 'nonzero target monomial')
    return len(weights), weights, columns


def full_span(first, shared, last, gamma, coefficient):
    middle, extra = mul(shared, first), mul(shared, gamma)
    mi = inv(middle)
    points = orbit(mul(last, middle), mul(mi, extra))
    n = len(points)
    columns = []
    for j, point in enumerate(points):
        if singleton(point, first, last):
            row = [Fraction(0)]*n; row[j] = 1; columns.append(row)
        old = is_free(mul(point, mi))
        paid = is_free(mul(mul(last, point), mi))
        if old or paid:
            row = [Fraction(0)]*n; row[j] = 1; row[(j+1) % n] += coefficient; columns.append(row)
    target = [Fraction(0)]*n; target[0] = 1
    return in_span(columns, target), n


def census():
    first, shared = call(3, 1), call(3, 2)
    middle = mul(shared, first)
    finishing = [(u, call(3, u)) for u in range(1, 64) if u & 7 and level(mul(call(3, u), middle)) == 3]
    need(len(finishing) == 32, 'all finishing calls')
    counts = Counter(); examples = {}; plain_example = None
    for gamma in all_free(3):
        extra = mul(shared, gamma)
        if is_free(mul(extra, first)):
            counts['plain_elements_excluded'] += 1
            plain_example = gamma
            continue
        counts['nonplain_elements'] += 1
        for normal, last in finishing:
            size, _, _ = separator(first, shared, last, gamma)
            counts[f'support_{size}_pairs'] += 1
            examples.setdefault(size, (gamma, normal))
    need(counts['plain_elements_excluded'] == 768 and counts['nonplain_elements'] == 9984, 'part inventory')
    need(counts['support_2_pairs']+counts['support_3_pairs'] == 9984*32, 'complete pair inventory')
    counts['free_elements'] = 10752
    counts['finishing_calls'] = 32
    counts['part_call_pairs'] = 9984*32
    return dict(counts), examples, plain_example


def embed(g, m):
    positions = [0, 1, 2, m, m+1, m+2]
    out = list(unit(2*m))
    for old, new in enumerate(positions):
        out[new] = sum(((g[old] >> j) & 1) << positions[j] for j in range(6))
    return tuple(out)


def random_free(m, rng):
    a = list(unit(m))
    for _ in range(8*m):
        i, j = rng.sample(range(m), 2)
        a[i] ^= a[j]
    a = tuple(a); b = transpose(inv(a)); s = [0]*m
    for i in range(m):
        for j in range(i, m):
            if rng.randrange(2):
                s[i] ^= 1 << j
                if i != j:
                    s[j] ^= 1 << i
    lower = mul(b, s)
    return a+tuple(lower[i] | (b[i] << m) for i in range(m))


def wider(examples):
    exact = Counter(); rng = Random(260018)
    for m in (3, 4, 5, 6):
        for gamma3, normal3 in examples.values():
            base = [embed(g, m) for g in (call(3, 1), call(3, 2), call(3, normal3), gamma3)]
            for h in (unit(2*m), random_free(m, rng)):
                hi = inv(h)
                first, shared, last, gamma = [mul(mul(h, g), hi) for g in base]
                separator(first, shared, last, gamma)
                for c in COEFFICIENTS:
                    got, length = full_span(first, shared, last, gamma, c)
                    need(not got, 'full orbit obstruction')
                    exact['full_orbit_contracts'] += 1
                    exact['maximum_orbit_length'] = max(exact['maximum_orbit_length'], length)
    # These cases change all call directions and the free map, not only the width.
    for m in (4, 5, 6):
        for _ in range(80):
            while True:
                normals = [rng.randrange(1, 1 << (2*m)) for _ in range(3)]
                if rank2(u & ((1 << m)-1) for u in normals) == 3:
                    break
            first, shared, last = [call(m, u) for u in normals]
            while True:
                gamma = random_free(m, rng)
                if not is_free(mul(mul(shared, gamma), first)):
                    break
            size, _, _ = separator(first, shared, last, gamma)
            exact[f'varied_support_{size}'] += 1
            exact['varied_direction_contracts'] += 1
            exact['noncommuting_first_shared'] += mul(first, shared) != mul(shared, first)
    return dict(exact)


def controls(examples, plain):
    first, shared, last = call(3, 1), call(3, 2), call(3, 4)
    for c in COEFFICIENTS:
        need(full_span(first, shared, last, plain, c)[0], 'plain extra must finish')
    gamma, normal = examples[3]
    final = call(3, normal)
    need(full_span(first, shared, final, gamma, Fraction(0))[0], 'zero coefficient must finish')
    need(full_span(first, shared, first, unit(6), Fraction(2))[0], 'lower-level call must finish control')
    _, weights, columns = separator(first, shared, final, gamma)
    third = next(g for g, value in weights.items() if value == (0, 1))
    corrupted = {g: Fraction(2)**power*sign for g, (power, sign) in weights.items() if g != third}
    need(any(corrupted.get(a, 0)+2*corrupted.get(b, 0) for a, b in columns), 'missing tail weight must fail')
    need(in_span([[1, 1], [1, 2]], [0, 1]), 'positive span control')
    need(not in_span([[1, 1]], [1, 2]), 'negative span control')
    return {'plain_positive_coefficients': len(COEFFICIENTS), 'zero_coefficient_positive': 1,
            'lower_target_level_positive': 1, 'corrupt_separator_rejected': 1, 'span_controls': 2}


def compute():
    counts, examples, plain = census()
    return {'status': 'PASS_KIND_B_LAST_CALL_OBSTRUCTION', 'census': counts,
            'separators': {str(size): {'gamma_rows': list(gamma), 'last_normal': normal}
                           for size, (gamma, normal) in examples.items()},
            'wider': wider(examples), 'controls': controls(examples, plain),
            'scope': 'Nonplain kind B, every nonzero rational coefficient, level-three final target; no post-call free step or joint output decoder.'}


if __name__ == '__main__':
    result = compute()
    need(json.loads((ROOT/'RESULT.json').read_text()) == result, 'retained result')
    print(json.dumps(result, indent=2, sort_keys=True))
