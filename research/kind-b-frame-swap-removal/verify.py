#!/usr/bin/env python3
"""Check the kind B removal criterion with binary row matrices.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction
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


def flags(points, first, middle, last, keep_identity=False):
    middle_inverse = inv(middle)
    singles, starts = [], []
    for g in points:
        tg = mul(last, g)
        singles.append(any(is_free(h) for h in (g, mul(g, first), tg, mul(tg, first))))
        old = is_free(mul(g, middle_inverse)) and (keep_identity or g != middle)
        paid = is_free(mul(tg, middle_inverse))
        starts.append(old or paid)
    return singles, starts


def span_check(points, c, first, middle, last, keep_identity=False, remove_start=None):
    singles, starts = flags(points, first, middle, last, keep_identity)
    n = len(points)
    columns = []
    for j in range(n):
        if singles[j]:
            row = [Fraction(0)]*n
            row[j] = 1
            columns.append(row)
        if starts[j] and j != remove_start:
            row = [Fraction(0)]*n
            row[j] = 1
            row[(j+1) % n] += c
            columns.append(row)
    target = [Fraction(0)]*n
    target[0] = 1
    target[1] = c
    return in_span(columns, target)


def endpoint_certificate(first, middle, extra, last, a, ai):
    # A nonzero target coefficient absent from every available column proves failure.
    out = []
    for g, relative, previous in ((middle, unit(len(middle)), ai), (extra, a, unit(len(middle)))):
        tg = mul(last, g)
        single = any(is_free(h) for h in (g, mul(g, first), tg, mul(tg, first)))
        old_start = g != middle and is_free(relative)
        old_previous = previous != unit(len(middle)) and is_free(previous)
        paid_start = is_free(mul(last, relative))
        paid_previous = is_free(mul(last, previous))
        out.append(not (single or old_start or old_previous or paid_start or paid_previous))
    return out


def census():
    first, shared = call(3, 1), call(3, 2)
    middle = mul(shared, first)
    mi = inv(middle)
    group = all_free(3)
    removing = [(normal, call(3, normal)) for normal in range(1, 64)
                if normal & 7 and level(mul(call(3, normal), shared)) == 2]
    need(len(removing) == 48 and level(middle) == 2, 'admissible calls')
    element_counts = {str(c): 0 for c in COEFFICIENTS}
    pair_counts = {str(c): 0 for c in COEFFICIENTS}
    plain = 0
    orphan_pairs = 0
    cycle_pairs = 0
    order_counts = Counter()
    representatives = {}
    for gamma in group:
        extra = mul(shared, gamma)
        if is_free(mul(extra, first)):
            plain += 1
            continue
        a = mul(extra, mi)
        ai = inv(a)
        step = mul(mi, extra)
        reached = {str(c): False for c in COEFFICIENTS}
        for normal, last in removing:
            exchange = (is_free(mul(last, ai)), is_free(mul(last, a)))
            orphan = endpoint_certificate(first, middle, extra, last, a, ai)
            if any(orphan):
                need(not all(exchange), 'swap cannot have an orphan endpoint')
                orphan_pairs += 1
                if sum(exchange) == 1:
                    representatives.setdefault('one_direction_only', (gamma, normal))
                else:
                    representatives.setdefault('neither_direction', (gamma, normal))
                continue
            need(all(exchange), 'uncovered endpoint configuration')
            points = orbit(middle, step)
            n = len(points)
            need(n % 2 == 0, 'exchange cycle must be even')
            singles, starts = flags(points, first, middle, last)
            need(not any(singles) and starts == [False]+[True]*(n-1), 'complete missing-column cycle')
            cycle_pairs += 1
            order_counts[n] += 1
            representatives.setdefault('cycle_'+str(n), (gamma, normal))
            for c in COEFFICIENTS:
                got = span_check(points, c, first, middle, last)
                need(got == (c in (1, -1)), 'exact cycle span')
                if got:
                    relation = [Fraction(0)]*n
                    for j in range(n):
                        relation[j] += (-c)**j
                        relation[(j+1) % n] += c*(-c)**j
                    need(not any(relation), 'explicit alternating relation')
                    pair_counts[str(c)] += 1
                    reached[str(c)] = True
        for c in COEFFICIENTS:
            element_counts[str(c)] += reached[str(c)]
    need(plain == 768 and element_counts['1'] == element_counts['-1'] == 128, 'source nonplain domain')
    need(orphan_pairs+cycle_pairs == (10752-plain)*48, 'complete pair domain')
    return {'free_elements': 10752, 'plain_elements_excluded': plain, 'nonplain_elements': 10752-plain,
            'admissible_calls': len(removing), 'element_call_pairs': orphan_pairs+cycle_pairs,
            'coefficient_contracts': (orphan_pairs+cycle_pairs)*len(COEFFICIENTS),
            'orphan_endpoint_pairs': orphan_pairs, 'complete_cycle_pairs': cycle_pairs,
            'cycle_order_counts': {str(k): v for k, v in sorted(order_counts.items())},
            'removable_parts_by_coefficient': element_counts, 'removable_pairs_by_coefficient': pair_counts}, representatives


def embed(g, m):
    positions = [0, 1, 2, m, m+1, m+2]
    out = list(unit(2*m))
    for old, new in enumerate(positions):
        out[new] = sum(((g[old] >> j) & 1) << positions[j] for j in range(6))
    return tuple(out)


def wider(representatives):
    total, positives = 0, 0
    for m in (4, 5, 6):
        for gamma3, normal3 in representatives.values():
            d0, w0, t0 = (embed(g, m) for g in (call(3, 1), call(3, 2), call(3, normal3)))
            gamma0 = embed(gamma3, m)
            for h in (unit(2*m), call(m, (1 << m) | (1 << (2*m-1)))):
                first, shared, last, gamma = (mul(mul(h, g), h) for g in (d0, w0, t0, gamma0))
                middle, extra = mul(shared, first), mul(shared, gamma)
                need(level(middle) == level(mul(last, shared)) == 2 and is_free(gamma), 'wider premises')
                a = mul(extra, inv(middle))
                exchange = is_free(mul(last, a)) and is_free(mul(last, inv(a)))
                points = orbit(middle, mul(inv(middle), extra))
                for c in COEFFICIENTS:
                    got = span_check(points, c, first, middle, last)
                    need(got == (exchange and c in (1, -1)), 'wider full span')
                    total += 1
                    positives += got
    return {'contracts': total, 'removable': positives, 'nontrivial_spare_conjugations': True}


def controls(representatives):
    first, shared = call(3, 1), call(3, 2)
    middle = mul(shared, first)
    gamma, normal = representatives['one_direction_only']
    last, extra = call(3, normal), mul(shared, gamma)
    points = orbit(middle, mul(inv(middle), extra))
    need(not span_check(points, Fraction(1), first, middle, last), 'one exchange direction is insufficient')
    need(span_check(points, Fraction(1), first, middle, last, True), 'identity preparation control')
    cycle_key = max((key for key in representatives if key.startswith('cycle_')), key=lambda key: int(key[6:]))
    gamma, normal = representatives[cycle_key]
    last, extra = call(3, normal), mul(shared, gamma)
    points = orbit(middle, mul(inv(middle), extra))
    need(span_check(points, Fraction(1), first, middle, last), 'positive control')
    need(not span_check(points, Fraction(2), first, middle, last), 'coefficient control')
    need(not span_check(points, Fraction(1), first, middle, last, remove_start=1), 'missing cyclic column control')
    need(not span_check(points, Fraction(0), first, middle, last), 'zero coefficient boundary')
    return {'controls': 5, 'positive_cycle_length': len(points)}


def verify():
    need(in_span([[1, 1], [1, 2]], [0, 1]), 'row-reduction positive control')
    need(not in_span([[1, 1]], [1, 2]), 'row-reduction negative control')
    data, reps = census()
    result = {'status': 'PASS_KIND_B_FRAME_SWAP_REMOVAL', 'census': data, 'linear_solver_controls': 2,
              'wider_checks': wider(reps), 'boundary_controls': controls(reps),
              'representatives': {key: {'gamma_rows': list(g), 'removing_normal': n}
                                  for key, (g, n) in sorted(reps.items())}}
    need(json.loads((ROOT/'RESULT.json').read_text()) == result, 'retained receipt')
    return result


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2, sort_keys=True))
