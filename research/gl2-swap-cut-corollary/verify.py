#!/usr/bin/env python3
"""Exact GL2/S3 model bridge; imports no predecessor implementation.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
The all-parameter lower bound is the written corollary in README.md.
"""
import argparse
import itertools
import json
from pathlib import Path


def require(ok, why):
    if not ok:
        raise ValueError(why)


def action(g, v):
    x, y = v & 1, v >> 1
    return (((g & 1) * x) ^ (((g >> 1) & 1) * y)) | (
        ((((g >> 2) & 1) * x) ^ (((g >> 3) & 1) * y)) << 1)


def mm(g, h):
    c, d = action(g, action(h, 1)), action(g, action(h, 2))
    return (c & 1) | ((d & 1) << 1) | ((c >> 1) << 2) | ((d >> 1) << 3)


GROUP = tuple(g for g in range(16)
              if (((g & 1) * ((g >> 3) & 1)) ^
                  (((g >> 1) & 1) * ((g >> 2) & 1))) == 1)
INDEX = {g: i for i, g in enumerate(GROUP)}
E, A, B, S = 9, 11, 13, 6
UNIT = 1 << INDEX[E]
VECTORS = (2, 3, 1)
PHI = {g: tuple(VECTORS.index(action(g, v)) for v in VECTORS) for g in GROUP}
TABLE = tuple(tuple(INDEX[mm(g, h)] for h in GROUP) for g in GROUP)
PAIRS = tuple(itertools.permutations(range(3), 2))
H = tuple(p for p in PAIRS if p[0] < p[1])
K = tuple(p for p in PAIRS if p[0] > p[1])


def convolution(x, y):
    ans = 0
    for i in range(6):
        if (x >> i) & 1:
            for j in range(6):
                if (y >> j) & 1:
                    ans ^= 1 << TABLE[i][j]
    return ans


RING = tuple(tuple(convolution(x, y) for y in range(64)) for x in range(64))


def ident(r):
    return tuple(tuple(UNIT if i == j else 0 for j in range(r)) for i in range(r))


def matmul(x, y):
    r = len(x)
    out = [[0] * r for _ in range(r)]
    for i in range(r):
        for k in range(r):
            if x[i][k]:
                for j in range(r):
                    out[i][j] ^= RING[x[i][k]][y[k][j]]
    return tuple(map(tuple, out))


def factor(r, label, u, v):
    out = [list(row) for row in ident(r)]
    for i in range(r):
        for j in range(r):
            if ((u >> i) & 1) and ((v >> j) & 1):
                out[i][j] ^= UNIT ^ (1 << INDEX[label])
    return tuple(map(tuple, out))


def endpoint(r, t):
    return tuple(tuple((1 << INDEX[S] if i < t else UNIT) if i == j else 0
                       for j in range(r)) for i in range(r))


def evaluate(r, word):
    out = ident(r)
    for g, u, v in word:  # chronological, column matrices act rightmost first
        out = matmul(factor(r, g, u, v), out)
    return out


def rank(rows):
    pivots = {}
    for x in rows:
        while x:
            p = x.bit_length() - 1
            if p not in pivots:
                pivots[p] = x
                break
            x ^= pivots[p]
    return len(pivots)


def crossing(matrix):
    r = len(matrix)
    rows = [0] * (3 * r)
    for dst in range(r):
        for src in range(r):
            coeff = matrix[dst][src]
            for gi, g in enumerate(GROUP):
                if (coeff >> gi) & 1:
                    p = PHI[g]
                    for j, (a, b) in enumerate(H):
                        q = (p[a], p[b])
                        if q in K:
                            rows[3 * dst + K.index(q)] ^= 1 << (3 * src + j)
    return rank(rows)


def exact_endpoint(matrix, r, t):
    require(matrix == endpoint(r, t), "complete formal endpoint")


def expect_rejection(fn, reason):
    try:
        fn()
    except ValueError as exc:
        require(str(exc) == reason, "unexpected rejection: " + str(exc))
    else:
        raise RuntimeError("control unexpectedly accepted: " + reason)


def verify():
    require(len(GROUP) == 6 and len(set(PHI.values())) == 6, "group bijection")
    require(PHI[A] == (1, 0, 2) and PHI[B] == (0, 2, 1), "adjacent label binding")
    require(mm(mm(A, B), A) == S and PHI[S] == (2, 1, 0), "SWAP target binding")
    for g, h in itertools.product(GROUP, repeat=2):
        require(PHI[mm(g, h)] == tuple(PHI[g][PHI[h][i]] for i in range(3)),
                "composition convention")
    # Independent S3-symbol multiplication, for all algebra coefficient pairs.
    for x, y in itertools.product(range(64), repeat=2):
        terms = set()
        for i, g in enumerate(GROUP):
            for j, h in enumerate(GROUP):
                if ((x >> i) & 1) and ((y >> j) & 1):
                    p = tuple(PHI[g][PHI[h][k]] for k in range(3))
                    terms.symmetric_difference_update({p})
        mapped = {PHI[g] for i, g in enumerate(GROUP) if (RING[x][y] >> i) & 1}
        require(mapped == terms, "full group algebra map")

    paid = 0
    for r in range(1, 6):
        for u, v in itertools.product(range(1, 1 << r), repeat=2):
            if (u & v).bit_count() % 2:
                for g in (A, B):
                    f = factor(r, g, u, v)
                    require(crossing(f) == 1, "paid crossing rank")
                    require(matmul(f, f) == ident(r), "paid involution")
                    paid += 1

    fixtures = omissions = 0
    for t in range(9):
        for r in range(t, t + 3):
            word = [(g, 1 << j, 1 << j) for j in range(t) for g in (A, B, A)]
            out = evaluate(r, word)
            exact_endpoint(out, r, t)
            require(crossing(out) == 3 * t, "target crossing rank")
            exact_endpoint(evaluate(r, list(reversed(word))), r, t)
            for i in range(len(word)):
                expect_rejection(lambda i=i: exact_endpoint(
                    evaluate(r, word[:i] + word[i+1:]), r, t), "complete formal endpoint")
                omissions += 1
            fixtures += 1

    # Every two-factor pair on three roles, including noncommuting projectors.
    gens = [factor(3, g, u, v) for g in (A, B)
            for u, v in itertools.product(range(1, 8), repeat=2)
            if (u & v).bit_count() % 2]
    hist = {}
    for x, y in itertools.product(gens, repeat=2):
        q = crossing(matmul(x, y))
        require(q <= crossing(x) + crossing(y), "cut subadditivity fixture")
        hist[q] = hist.get(q, 0) + 1

    # A legal word with explicitly noncommuting paid projectors still closes.
    word = [(g, 1 << j, 1 << j) for j in range(2) for g in (A, B, A)]
    extra = (A, 3, 1)
    exact_endpoint(evaluate(3, [extra, extra] + word), 3, 2)
    x, y = factor(3, A, 3, 1), factor(3, B, 1, 1)
    require(matmul(x, y) != matmul(y, x), "noncommuting fixture")
    wrong = list(word)
    wrong[1] = (A, 1, 1)
    expect_rejection(lambda: exact_endpoint(evaluate(3, wrong), 3, 2),
                     "complete formal endpoint")
    dirty = [list(row) for row in endpoint(3, 2)]
    dirty[0][2] ^= UNIT
    expect_rejection(lambda: exact_endpoint(tuple(map(tuple, dirty)), 3, 2),
                     "complete formal endpoint")

    # The natural 2D address image is not an endpoint certificate.
    norm, natural = 63, 0
    for g in GROUP:
        natural ^= g
    require(norm != 0 and natural == 0, "natural representation alias")
    alias = [list(row) for row in endpoint(3, 2)]
    alias[0][2] ^= norm
    expect_rejection(lambda: exact_endpoint(tuple(map(tuple, alias)), 3, 2),
                     "complete formal endpoint")
    # Expanded alphabet/rank-two unit pricing invalidate one crossing/call.
    require(crossing(factor(1, S, 1, 1)) == 3, "expanded label price control")
    rank2 = tuple(tuple((1 << INDEX[A]) if i == j else 0 for j in range(2))
                  for i in range(2))
    require(crossing(rank2) == 2, "rank-two price control")
    scalar = ((UNIT, UNIT, 0), (0, UNIT, UNIT), (0, 0, UNIT))
    require(crossing(scalar) == 0, "free scalar cut")
    return {
        "status": "PASS_GL2_SWAP_CUT_COROLLARY", "no_new_kappa": True,
        "group_elements": 6, "group_products": 36, "algebra_products": 4096,
        "paid_factors_R1_through_R5": paid,
        "full_formal_endpoints_t0_through_t8_R_t_through_tplus2": fixtures,
        "omission_rejections": omissions, "two_factor_pairs_R3": len(gens)**2,
        "two_factor_crossing_histogram": hist,
        "five_swap_minimum": 15, "four_swap_minimum_any_dirty_workspace": 12,
        "all_parameter_basis": "credited PR1989 theorem and explicit model isomorphism",
        "scope": "formal F2[GL2(F2)], labels a,b, rank-one idempotents, finite restored dirty roles",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(verify(), indent=2, sort_keys=True) + "\n"
    if args.output:
        with args.output.open("x") as f:
            f.write(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
