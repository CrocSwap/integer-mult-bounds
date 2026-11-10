#!/usr/bin/env python3
"""Exact controls for PAIRED-DEFECT-ADDENDUM.md; no external dependencies.

The universal result is the written proof, not a finite search conclusion.
By @CubeJerry with substantial OpenAI GPT-6 Astra Pro assistance.
"""
from fractions import Fraction as Q
from itertools import combinations
import json


def need(condition, message):
    if not condition:
        raise ValueError(message)


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def mm(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def add(a, b, scale=1):
    return [[x + scale * y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def tensor2(a):
    return [[x * Q(i == j) for x in row for j in range(2)] for row in a for i in range(2)]


def rank(a, modulus=None):
    a = [[int(x) % modulus if modulus else Q(x) for x in row] for row in a]
    r = 0
    for c in range(len(a[0]) if a else 0):
        p = next((i for i in range(r, len(a)) if a[i][c]), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        inv = pow(a[r][c], -1, modulus) if modulus else 1 / a[r][c]
        a[r] = [(x * inv) % modulus if modulus else x * inv for x in a[r]]
        for i in range(r + 1, len(a)):
            factor = a[i][c]
            if factor:
                a[i] = [((x - factor * y) % modulus if modulus else x - factor * y)
                        for x, y in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def same(a, b, modulus=None):
    return all((x - y) % modulus == 0 if modulus else x == y
               for ar, br in zip(a, b) for x, y in zip(ar, br))


def canonical(n):
    need(n > 0 and n % 2 == 0, "even canonical dimension")
    result = []
    for i in range(n + 1):
        x = [Q(i == j) for j in range(n)] if i < n else [Q((-1) ** (j + 1)) for j in range(n)]
        y = [Q((i > j) - (i < j)) for j in range(n)]
        result.append((tensor2([[v] for v in x]), tensor2([y])))
    return result


def check_root(queries):
    n = len(queries[0][0])
    prefix = eye(n)
    for x, y in queries:
        need(rank(x) == rank(y) == 2, "rank-two query factors")
        need(mm(y, x) == [[0, 0], [0, 0]], "square-zero query")
        prefix = add(prefix, mm(x, mm(y, prefix)), -2)
    need(prefix == [[-v for v in row] for row in eye(n)], "literal root endpoint")


def support(x, y, p, modulus=None):
    need(rank(p, modulus) == 4, "rank-four stage")
    need(same(mm(p, p), p, modulus), "idempotent stage")
    need(same(mm(p, x), x, modulus), "left query support")
    need(same(mm(y, p), y, modulus), "right query support")


def rejected(fn, message):
    try:
        fn()
    except ValueError:
        return
    raise ValueError("Negative control was accepted: " + message)


def sign_gram():
    s = [[Q((i > j) - (i < j)) for j in range(6)] for i in range(6)]
    inv = [[((-1) ** (i + j)) * s[i][j] for j in range(6)] for i in range(6)]
    need(mm(s, inv) == eye(6) and mm(inv, s) == eye(6), "integer sign-matrix inverse")
    need(rank(tensor2(s)) == 12, "six-query block Gram rank")
    bad = [row[:] for row in inv]
    bad[0][1] *= -1
    rejected(lambda: need(mm(s, bad) == eye(6), "corrupt inverse"), "inverse sign")
    return {"scalar_order": 6, "block_width": 2, "block_gram_rank": 12}


def matching(edges):
    vertices = set().union(*edges) if edges else set()
    if not vertices:
        return 0
    v = min(vertices)
    best = matching([e for e in edges if v not in e])
    for edge in edges:
        if v in edge:
            best = max(best, 1 + matching([e for e in edges if not e & edge]))
    return best


def set_controls():
    c0, c1, a = {0, 1, 2, 3}, {0, 1, 4, 5}, {0, 1}
    count = 0
    for e0 in combinations(range(7), 4):
        e = set(e0)
        if a <= e or len(e & c0) < 2 or len(e & c1) < 2:
            continue
        t = c0 | c1 | e
        need(len(t) <= 7, "three-set union bound")
        for d0 in combinations(range(9), 4):
            d = set(d0)
            if min(len(d & c0), len(d & c1), len(d & e)) < 2:
                continue
            need(len(d - t) <= 1, "each extension adds at most one coordinate")
            count += 1
    no_pair = [c0, c1, {0, 2, 4, 6}, {0, 2, 4, 7}, {0, 2, 4, 8}, {0, 2, 4, 9}]
    outside = [{2, 3}, {2, 4}, {2, 5}, {6, 7}, {6, 8}, {6, 9}]
    common_pair = [a | e for e in outside]
    for family in (no_pair, common_pair):
        need(all(len(x & y) >= 2 for x, y in combinations(family, 2)), "pair intersections")
        need(len(set().union(*family)) == 10, "sharp combinatorial union bound")
    need(len(set.intersection(*no_pair)) == 1, "first extremal family has no common pair")
    need(set.intersection(*common_pair) == a and matching(outside) == 2,
         "second extremal family has outside matching two")
    repeated = outside + [outside[0]]
    need(matching(repeated) == 2 and len(set().union(*repeated)) <= len(repeated) + 2,
         "repeated supports retain the edge bound")
    sunflower = [{2 + 2 * i, 3 + 2 * i} for i in range(6)]
    need(matching(sunflower) == 6 and len(a | set().union(*sunflower)) == 14,
         "pair intersections alone do not imply the small-union bound")
    return {"normalized_extension_checks": count,
            "no_common_pair_extremal_union": 10, "common_pair_extremal_union": 10,
            "repeated_support_control": True, "sunflower_union_without_sign_obstruction": 14}


def positive_three_block_root():
    queries = canonical(2)
    check_root(queries)
    for x, y in queries:
        support(x, y, eye(4))
    return {"full_blocks": 3, "ambient_dimension": 4, "defect": 2,
            "all_three_stages": "I4; commute and satisfy every prefix"}


def noncommuting_boundary():
    queries = canonical(6)
    check_root(queries)
    projectors = []
    for i in range(6):
        j = 0 if i else 1
        x = [Q(i == k) for k in range(6)]
        y = [Q((i > k) - (i < k)) for k in range(6)]
        w = [Q(k == j) * y[j] for k in range(6)]
        p = [[x[a] * x[b] + w[a] * y[b] for b in range(6)] for a in range(6)]
        p = tensor2(p)
        support(*queries[i], p)
        projectors.append(p)
    bad_pairs = sum(mm(p, q) != mm(q, p) for p, q in combinations(projectors, 2))
    need(bad_pairs > 0, "support alone does not imply commuting stages")
    rejected(lambda: need(bad_pairs == 0, "stage commutation"), "commutation omitted")
    return {"root_blocks": 7, "selected_full_blocks": 6, "ambient_dimension": 12,
            "defect": 2, "selected_stage_ranks": [4] * 6,
            "noncommuting_stage_pairs": bad_pairs}


def characteristic_two_boundary():
    xs, ys, ps = [], [], []
    for i in range(6):
        x = [[Q((r == c) or (r == 2 + 2 * i + c)) for c in range(2)] for r in range(14)]
        y = [list(row) for row in zip(*x)]
        mask = {0, 1, 2 + 2 * i, 3 + 2 * i}
        p = [[Q(r == c and r in mask) for c in range(14)] for r in range(14)]
        support(x, y, p, 2)
        need(rank(x, 2) == rank(y, 2) == 2, "characteristic-two query rank")
        need(same(mm(y, x), [[0, 0], [0, 0]], 2), "characteristic-two square zero")
        xs.append(x); ys.append(y); ps.append(p)
    for i, j in combinations(range(6), 2):
        need(same(mm(ys[i], xs[j]), eye(2), 2) and same(mm(ys[j], xs[i]), eye(2), 2),
             "ordered signs coincide in characteristic two")
        need(mm(ps[i], ps[j]) == mm(ps[j], ps[i]), "coordinate stages commute")
    xall = [[v for x in xs for v in x[r]] for r in range(14)]
    yall = [row for y in ys for row in y]
    need(rank(mm(yall, xall), 2) == 12, "characteristic-two Gram rank")
    return {"field": "F2", "selected_full_blocks": 6, "stage_union_dimension": 14,
            "block_gram_rank": 12, "isolated_Gram_support_lemma_only": True,
            "purpose": "the characteristic restriction cannot be dropped from the sign contradiction"}


def main():
    result = {"status": "PASS_PAIRED_DEFECT_TWO_STAGE_CAP",
              "claim": "at most five rank-two full blocks with commuting rank-four stages in defect two",
              "sign_gram": sign_gram(), "set_controls": set_controls(),
              "positive_three_full_block_root": positive_three_block_root(),
              "commutation_boundary": noncommuting_boundary(),
              "characteristic_boundary": characteristic_two_boundary(),
              "negative_controls": ["corrupt inverse rejected", "noncommuting stages rejected",
                                    "characteristic-two counterexample outside declared scope"],
              "new_kappa": False}
    print(json.dumps(result, indent=2))
    print(result["status"])


if __name__ == "__main__":
    main()
