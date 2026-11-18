#!/usr/bin/env python3
"""Check the common post-map restriction and the relaxed-span counterexample.

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


def algebra_sum(*terms):
    result = {}
    for coefficient, word in terms:
        for g, value in word.items():
            total = result.get(g, 0)+coefficient*value
            if total:
                result[g] = total
            else:
                result.pop(g, None)
    return result


def algebra_product(a, b):
    result = {}
    for g, x in a.items():
        for h, y in b.items():
            term = mul(g, h)
            total = result.get(term, 0)+x*y
            if total:
                result[term] = total
            else:
                result.pop(term, None)
    return result


def inverse_binomial(h, coefficient):
    powers = orbit(unit(len(h)), h)
    divisor = 1-(-coefficient)**len(powers)
    need(divisor != 0, 'singular binomial')
    return {g: Fraction((-coefficient)**j, divisor) for j, g in enumerate(powers)}


def in_intersection(g, last):
    return is_free(g) and is_free(mul(mul(last, g), last))


def unit_checks(last, inside, outside):
    identity = {unit(len(last)): Fraction(1)}
    a = algebra_sum((1, identity), (2, {inside: Fraction(1)}))
    f = inverse_binomial(inside, 2)
    need(algebra_product(f, a) == algebra_product(a, f) == identity, 'two-sided free inverse')
    need(all(in_intersection(g, last) for g in f), 'inverse stays in intersection')
    pushed = {mul(mul(last, g), last): value for g, value in f.items()}
    need(all(is_free(g) for g in pushed), 'pushed input map is free')
    need(algebra_product(f, {last: 1}) == algebra_product({last: 1}, pushed), 'common post-map fold')
    kernel = {g: Fraction(1) for g in orbit(unit(len(last)), inside)}
    singular = algebra_sum((1, identity), (-1, {inside: Fraction(1)}))
    need(kernel and not algebra_product(singular, kernel), 'singular projection has a nonzero kernel')
    outside_inverse = inverse_binomial(outside, 2)
    need(any(not in_intersection(g, last) for g in outside_inverse), 'outside inverse cannot be a projection')
    return {'inside_order': len(kernel), 'outside_order': len(outside_inverse)}


def projection_census(group):
    first, shared = call(3, 1), call(3, 2)
    middle = mul(shared, first)
    counts = Counter(); witnesses = []
    for normal in range(1, 64):
        last = call(3, normal)
        target = mul(last, middle)
        if level(target) != 3:
            continue
        target_inverse = inv(target)
        intersection = []
        outside = None
        for p in group:
            tp = mul(last, p)
            need(level(tp) == 1 and level(mul(tp, first)) <= 2, 'earlier paid inputs stay below target')
            need(level(mul(tp, shared)) <= 2, 'every kind B extra stays below target')
            point = mul(tp, middle)
            relative = mul(point, target_inverse)
            conjugate = mul(tp, last)
            need(relative == conjugate, 'target-coset coefficient')
            if is_free(relative):
                need(in_intersection(relative, last), 'projection is in subgroup algebra')
                intersection.append(relative)
            else:
                outside = p
            counts['preparation_call_pairs'] += 1
        need(len(intersection) == len(set(intersection)) == 768, 'complete intersection')
        inside = next(g for g in intersection if g != unit(6))
        unit_checks(last, inside, outside)
        witnesses.append((last, inside, outside))
        counts['finishing_calls'] += 1
        counts['surviving_projection_columns'] += len(intersection)
    need(counts['finishing_calls'] == 32 and counts['preparation_call_pairs'] == 344064, 'complete projection domain')
    counts['unit_and_nonunit_checks'] = len(witnesses)
    return dict(counts), witnesses


def relaxed_span_control(group):
    first, shared, last = call(3, 1), call(3, 2), call(3, 5)
    gamma = (1, 2, 5, 40, 16, 32)
    post = (5, 4, 2, 8, 40, 16)
    prep = (3, 5, 2, 40, 32, 56)
    middle, extra = mul(shared, first), mul(shared, gamma)
    target, second, third = mul(last, middle), mul(last, extra), mul(gamma, extra)
    need(all(is_free(g) for g in (gamma, post, prep)), 'relaxed maps are free')
    need(level(target) == 3 and not is_free(mul(extra, first)), 'nonplain relaxed example')
    need(mul(mul(mul(post, last), prep), first) == second, 'second independently postprocessed column')
    # The complete call-alone separator is checked once, as a polynomial in c.
    weights = {target: (2, 1), second: (1, -1), third: (0, 1)}
    for p in group:
        tp = mul(last, p)
        need(all(g not in weights for g in (p, mul(p, first), tp, mul(tp, first))), 'relaxed control singleton')
        for left in (p, tp):
            polynomial = Counter()
            for g, shift in ((mul(left, middle), 0), (mul(left, extra), 1)):
                if g in weights:
                    power, sign = weights[g]
                    polynomial[power+shift] += sign
            need(all(x == 0 for x in polynomial.values()), 'relaxed control exact separator')
    for c in COEFFICIENTS:
        y = {middle: Fraction(1), extra: c}
        first_column = algebra_product({last: 1}, y)
        second_column = algebra_product({post: 1}, algebra_product({last: 1}, {mul(prep, first): 1}))
        need(algebra_sum((1, first_column), (-c, second_column)) == {target: 1}, 'relaxed two-column identity')
    return {'gamma_rows': list(gamma), 'last_normal': 5, 'post_rows': list(post), 'prep_rows': list(prep),
            'nonzero_coefficients_checked': len(COEFFICIENTS), 'separator_columns_checked': 2*len(group),
            'meaning': 'The relaxed span accepts two independently prepared/postprocessed columns; the common-map theorem excludes one call.'}


def kind_a_control():
    first, shared, last = call(3, 1), call(3, 2), call(3, 4)
    gamma = (1, 2, 6, 8, 52, 34)
    middle = mul(shared, first)
    extra = mul(mul(shared, gamma), first)
    target = mul(last, middle)
    h = mul(mul(last, extra), inv(target))
    need(is_free(gamma) and is_free(h) and level(extra) == 2, 'kind A higher extra term')
    need(not is_free(mul(extra, inv(middle))) and not in_intersection(h, last), 'kind A breaks the projection restriction')
    a = {unit(6): Fraction(1), h: Fraction(2)}
    f = inverse_binomial(h, 2)
    y = {middle: Fraction(1), extra: Fraction(2)}
    need(algebra_product({last: 1}, y) == algebra_product(a, {target: 1}), 'kind A same post-call frame')
    need(algebra_product(f, algebra_product({last: 1}, y)) == {target: 1}, 'actual one-call post-map control')
    return {'gamma_rows': list(gamma), 'post_binomial_rows': list(h), 'post_binomial_order': len(f),
            'coefficient': '2', 'extra_level': 2, 'actual_one_call_finish': True}


def embed(g, m):
    places = [0, 1, 2, m, m+1, m+2]
    out = list(unit(2*m))
    for old, new in enumerate(places):
        out[new] = sum(((g[old] >> j) & 1) << places[j] for j in range(6))
    return tuple(out)


def wider(witnesses):
    count = 0
    for m in (4, 5, 6):
        h = call(m, (1 << m) | (1 << (2*m-1)))
        need(is_free(h), 'spare-bit conjugation')
        for triple in witnesses:
            changed = [mul(mul(h, embed(g, m)), h) for g in triple]
            unit_checks(*changed)
            count += 1
    return count


def compute():
    group = all_free(3)
    counts, witnesses = projection_census(group)
    return {'status': 'PASS_LAST_CALL_COMMON_POSTMAP', 'projection_census': counts,
            'wider_unit_contracts': wider(witnesses), 'relaxed_span_counterexample': relaxed_span_control(group),
            'higher_term_positive_control': kind_a_control(),
            'scope': 'One common free post-map on one call output, with a unique level-two leading term and only lower-level companions; no joint decoder or kappa.'}


if __name__ == '__main__':
    result = compute()
    need(json.loads((ROOT/'RESULT.json').read_text()) == result, 'retained result')
    print(json.dumps(result, indent=2, sort_keys=True))
