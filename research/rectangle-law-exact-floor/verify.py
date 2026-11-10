#!/usr/bin/env python3
"""Verifier for the exact odd-rectangle rank floor (standard library only).

Claim checked (proof in PROOF.md).  Fix a field K of characteristic not 2,
sizes u, h >= 1, and signs s_dc, s_df, s_ec, s_ef in {+1,-1} with product -1.
For A_d, A_e in K^{u x h} and B_c, B_f in K^{h x u} put C_xy = s_xy I_u - A_x B_y.
Then the least value of rank C_dc + rank C_df + rank C_ec + rank C_ef is

    f(u, h) = max(0, 2u - h, 3u - 2h, 4u - 4h).

The lower bound is a proof (PROOF.md); this script checks the attaining
constructions exactly over Q, minimises exhaustively over small finite
fields, checks the 18-stage grid corollary and binds the quoted source text.

Run:  python3 -I -B research/rectangle-law-exact-floor/verify.py
      python3 -I -B research/rectangle-law-exact-floor/verify.py --write   (regenerate RESULT.json)
"""
import hashlib
import itertools
import json
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RESULT_PATH = os.path.join(HERE, "RESULT.json")
SOURCE_REL = "research/p104-root-cut-laws/THEOREM.md"
MAX_DIM = 8          # construction range: 1 <= u, h <= MAX_DIM
GRID_L = 18          # number of stages in Theorem S of the source package
RHO_RANGE = (1, 2, 3, 4)
SIGN_PATTERNS = [s for s in itertools.product((1, -1), repeat=4) if s[0] * s[1] * s[2] * s[3] == -1]
CANONICAL = (1, -1, 1, 1)   # (s_dc, s_df, s_ec, s_ef); every odd pattern is switching-equivalent to it


def need(condition, message):
    """Fail loudly; unlike assert this survives python -O."""
    if not condition:
        raise AssertionError(message)


def formula(u, h):
    return max(0, 2 * u - h, 3 * u - 2 * h, 4 * u - 4 * h)


# ---------------------------------------------------------------- linear algebra

def zeros(m, n):
    return [[Fraction(0)] * n for _ in range(m)]


def matmul(a, b):
    need(len(a[0]) == len(b), "shape mismatch in matmul")
    cols = list(zip(*b))
    return [[sum(x * y for x, y in zip(row, col)) for col in cols] for row in a]


def block_sign_matrix(g, size, transpose=False):
    """Kronecker product of the 2x2 sign matrix g (or its transpose) with I_size."""
    out = zeros(2 * size, 2 * size)
    for x in range(2):
        for y in range(2):
            sign = g[y][x] if transpose else g[x][y]
            for i in range(size):
                out[x * size + i][y * size + i] = Fraction(sign)
    return out


def rank_q(rows):
    """Rank over Q by exact Gaussian elimination."""
    m = [[Fraction(x) for x in r] for r in rows]
    rank = 0
    for c in range(len(m[0]) if m else 0):
        piv = next((r for r in range(rank, len(m)) if m[r][c] != 0), None)
        if piv is None:
            continue
        m[rank], m[piv] = m[piv], m[rank]
        lead = m[rank][c]
        m[rank] = [x / lead for x in m[rank]]
        for r in range(len(m)):
            if r != rank and m[r][c] != 0:
                f = m[r][c]
                m[r] = [x - f * y for x, y in zip(m[r], m[rank])]
        rank += 1
    return rank


def rank_mod(rows, p):
    """Rank over the prime field F_p."""
    m = [[x % p for x in r] for r in rows]
    rank = 0
    for c in range(len(m[0]) if m else 0):
        piv = next((r for r in range(rank, len(m)) if m[r][c]), None)
        if piv is None:
            continue
        m[rank], m[piv] = m[piv], m[rank]
        inv = pow(m[rank][c], -1, p)
        m[rank] = [(x * inv) % p for x in m[rank]]
        for r in range(len(m)):
            if r != rank and m[r][c]:
                f = m[r][c]
                m[r] = [(x - f * y) % p for x, y in zip(m[r], m[rank])]
        rank += 1
    return rank


def factor_q(p_mat, r):
    """Return (M, N) with p_mat = M N, M of width exactly r, N of height exactly r."""
    rows, cols = len(p_mat), len(p_mat[0])
    m = [[Fraction(x) for x in row] for row in p_mat]
    pivots, rank = [], 0
    for c in range(cols):
        piv = next((i for i in range(rank, rows) if m[i][c] != 0), None)
        if piv is None:
            continue
        m[rank], m[piv] = m[piv], m[rank]
        lead = m[rank][c]
        m[rank] = [x / lead for x in m[rank]]
        for i in range(rows):
            if i != rank and m[i][c] != 0:
                f = m[i][c]
                m[i] = [x - f * y for x, y in zip(m[i], m[rank])]
        pivots.append(c)
        rank += 1
    need(rank <= r, "rank %d exceeds factor width %d" % (rank, r))
    left = [[Fraction(p_mat[i][c]) for c in pivots] + [Fraction(0)] * (r - rank) for i in range(rows)]
    right = [m[k][:] for k in range(rank)] + [[Fraction(0)] * cols for _ in range(r - rank)]
    return left, right


# ---------------------------------------------------------------- constructions

def cells(u, signs, a_d, a_e, b_c, b_f):
    s_dc, s_df, s_ec, s_ef = signs
    out = {}
    for name, s, a, b in (("dc", s_dc, a_d, b_c), ("df", s_df, a_d, b_f),
                          ("ec", s_ec, a_e, b_c), ("ef", s_ef, a_e, b_f)):
        prod = matmul(a, b)
        out[name] = [[Fraction(s if i == j else 0) - prod[i][j] for j in range(u)] for i in range(u)]
    return out


def construct_primal(u, h, signs):
    """Case h >= u: one perturbed block of S = G (x) I_u, then rank factorisation."""
    s_dc, s_df, s_ec, s_ef = signs
    g = [[s_dc, s_df], [s_ec, s_ef]]
    k = max(0, 2 * u - h)
    p_mat = block_sign_matrix(g, u)
    for i in range(k):
        p_mat[i][i] -= 2 * s_dc          # block (d,c) of S - W, W = 2 s_dc Pi, rank Pi = k
    left, right = factor_q(p_mat, h)
    a_d, a_e = left[:u], left[u:]
    b_c = [row[:u] for row in right]
    b_f = [row[u:] for row in right]
    return a_d, a_e, b_c, b_f


def construct_dual(u, h, signs):
    """Case h < u: build B_y A_x first (an h-dimensional problem through width u)."""
    s_dc, s_df, s_ec, s_ef = signs
    g = [[s_dc, s_df], [s_ec, s_ef]]
    k2 = max(0, 2 * h - u)
    p_mat = block_sign_matrix(g, h, transpose=True)   # rows (c,f), columns (d,e)
    for i in range(k2):
        p_mat[i][i] -= 2 * s_dc
    n_mat, m_mat = factor_q(p_mat, u)                 # p_mat = n_mat m_mat, widths u
    a_d = [row[:h] for row in m_mat]
    a_e = [row[h:] for row in m_mat]
    b_c, b_f = n_mat[:h], n_mat[h:]
    return a_d, a_e, b_c, b_f


def construct(u, h, signs):
    return construct_primal(u, h, signs) if h >= u else construct_dual(u, h, signs)


def check_construction(u, h, signs):
    a_d, a_e, b_c, b_f = construct(u, h, signs)
    need(len(a_d) == u and len(a_d[0]) == h and len(b_c) == h and len(b_c[0]) == u, "factor shapes")
    total = sum(rank_q(c) for c in cells(u, signs, a_d, a_e, b_c, b_f).values())
    need(total == formula(u, h), "construction (%d,%d,%s) gives %d, formula %d" % (u, h, signs, total, formula(u, h)))
    return total


def check_all_constructions():
    table = {}
    for u in range(1, MAX_DIM + 1):
        for h in range(1, MAX_DIM + 1):
            totals = {check_construction(u, h, s) for s in SIGN_PATTERNS}
            need(totals == {formula(u, h)}, "attainment (%d,%d)" % (u, h))
            table["%d,%d" % (u, h)] = formula(u, h)
    return table


def check_formula_identities():
    for u in range(1, 40):
        for h in range(1, 40):
            need(formula(u, h) == 4 * (u - h) + formula(h, u), "duality %d %d" % (u, h))
            need(formula(u, h) >= max(0, 2 * u - h), "block bound")
            if h >= 2 * u:
                need(formula(u, h) == 0, "zero region")
    for u in range(1, 40):
        need(formula(u, u) == u, "diagonal value")
    return True


# ---------------------------------------------------------------- finite-field minima

def all_matrices(rows, cols, p):
    for flat in itertools.product(range(p), repeat=rows * cols):
        yield tuple(tuple(flat[r * cols:(r + 1) * cols]) for r in range(rows))


def rank_table(u, h, p, mats_a, mats_b, signs_needed):
    """T[s][i][j] = rank over F_p of s I - A_i B_j, cached on the product matrix."""
    cache = {}
    tables = {s: [[0] * len(mats_b) for _ in mats_a] for s in signs_needed}
    for i, a in enumerate(mats_a):
        for j, b in enumerate(mats_b):
            prod = tuple(tuple(sum(a[r][t] * b[t][c] for t in range(h)) % p for c in range(u)) for r in range(u))
            for s in signs_needed:
                key = (prod, s)
                if key not in cache:
                    cache[key] = rank_mod([[((s if r == c else 0) - prod[r][c]) % p for c in range(u)]
                                           for r in range(u)], p)
                tables[s][i][j] = cache[key]
    return tables


def normal_forms(u, h):
    forms = []
    for r in range(min(u, h) + 1):
        forms.append(tuple(tuple(1 if (i == j and i < r) else 0 for j in range(h)) for i in range(u)))
    return forms


def exhaustive_minimum(u, h, p, signs=CANONICAL, reduce_by_symmetry=False):
    """Exact minimum over F_p; the sum separates once A_d and A_e are fixed."""
    mats = list(all_matrices(u, h, p))
    mats_b = list(all_matrices(h, u, p))
    s_dc, s_df, s_ec, s_ef = signs
    sign_values = sorted({s % p for s in signs})
    tab = rank_table(u, h, p, mats, mats_b, sign_values)
    index = {m: i for i, m in enumerate(mats)}
    firsts = [index[m] for m in normal_forms(u, h)] if reduce_by_symmetry else range(len(mats))
    best = None
    for i_d in firsts:
        for i_e in range(len(mats)):
            via_c = min(tab[s_dc % p][i_d][j] + tab[s_ec % p][i_e][j] for j in range(len(mats_b)))
            via_f = min(tab[s_df % p][i_d][j] + tab[s_ef % p][i_e][j] for j in range(len(mats_b)))
            if best is None or via_c + via_f < best:
                best = via_c + via_f
    return best


EXHAUSTIVE_FULL = [(1, 1, 3), (1, 2, 3), (2, 1, 3), (1, 3, 3), (3, 1, 3), (2, 2, 3), (1, 1, 5), (1, 2, 5),
                   (2, 1, 5), (1, 1, 7), (2, 1, 7), (1, 2, 7)]
EXHAUSTIVE_REDUCED = [(1, 4, 3), (4, 1, 3), (2, 3, 3), (3, 2, 3)]


def check_exhaustive():
    found = {}
    for (u, h, p) in EXHAUSTIVE_FULL:
        got = exhaustive_minimum(u, h, p)
        need(got == formula(u, h), "exhaustive F_%d (%d,%d): %d vs %d" % (p, u, h, got, formula(u, h)))
        found["F%d:%d,%d" % (p, u, h)] = got
    for (u, h, p) in EXHAUSTIVE_REDUCED:
        got = exhaustive_minimum(u, h, p, reduce_by_symmetry=True)
        need(got == formula(u, h), "exhaustive reduced F_%d (%d,%d): %d vs %d" % (p, u, h, got, formula(u, h)))
        found["F%d:%d,%d*" % (p, u, h)] = got
    for s in SIGN_PATTERNS:      # all eight odd patterns agree (switching lemma), small cases
        for (u, h) in ((1, 1), (2, 1), (1, 2)):
            need(exhaustive_minimum(u, h, 3, signs=s) == formula(u, h), "pattern %s (%d,%d)" % (s, u, h))
    return found


def check_controls():
    """The hypotheses are needed: characteristic 2 and even sign products break the floor.

    Also a discriminating control: at (u, h) = (3, 2) the two single-argument bounds both give 4,
    but the exhaustive minimum over F_3 is 5, so the third term 3u - 2h is not removable.
    """
    weak = max(0, 2 * 3 - 2, 4 * (3 - 2))
    need(weak == 4 and exhaustive_minimum(3, 2, 3, reduce_by_symmetry=True) == 5 > weak, "weak bound control")
    need(exhaustive_minimum(1, 1, 2, signs=(1, 1, 1, 1)) == 0 < formula(1, 1), "char 2 control (1,1)")
    need(exhaustive_minimum(2, 2, 2, signs=(1, 1, 1, 1)) == 0 < formula(2, 2), "char 2 control (2,2)")
    need(exhaustive_minimum(1, 1, 3, signs=(1, 1, 1, 1)) == 0, "even product control")
    need(exhaustive_minimum(2, 2, 3, signs=(1, 1, 1, 1)) == 0, "even product control (2,2)")
    return True


# ---------------------------------------------------------------- the two proof identities

def check_rank_identity(trials=300, seed=20261110):
    """rank(sI_u - AB) = u - h + rank(sI_h - BA) for s != 0 (used in the proof)."""
    rng = random.Random(seed)
    for _ in range(trials):
        u, h = rng.randint(1, 5), rng.randint(1, 5)
        p = rng.choice((3, 5, 7, 11))
        s = rng.choice((1, p - 1))
        a = [[rng.randrange(p) if rng.random() < 0.7 else 0 for _ in range(h)] for _ in range(u)]
        b = [[rng.randrange(p) if rng.random() < 0.7 else 0 for _ in range(u)] for _ in range(h)]
        ab = [[sum(a[i][t] * b[t][j] for t in range(h)) % p for j in range(u)] for i in range(u)]
        ba = [[sum(b[i][t] * a[t][j] for t in range(u)) % p for j in range(h)] for i in range(h)]
        left = rank_mod([[(s if i == j else 0) - ab[i][j] for j in range(u)] for i in range(u)], p)
        right = rank_mod([[(s if i == j else 0) - ba[i][j] for j in range(h)] for i in range(h)], p)
        need(left == u - h + right, "rank identity failed")
    return trials


# ---------------------------------------------------------------- the 18-stage grid

def sgn(x):
    return (x > 0) - (x < 0)


def packing_rectangles():
    rects = []
    for i in range(1, 10):
        for j in range(i + 1, 10):
            rects.append(((i, j), (i + 9, j), (i + 9, j + 9), (i, j + 9)))
            rects.append(((j, i), (j + 9, i), (j + 9, i + 9), (j, i + 9)))
    return rects


def check_packing():
    rects = packing_rectangles()
    need(len(rects) == 72, "72 rectangles")
    used = set()
    for rect in rects:
        prod = 1
        for (d, c) in rect:
            need(1 <= d <= GRID_L and 1 <= c <= GRID_L and d != c, "off-diagonal cell")
            prod *= sgn(d - c)
        need(prod == -1, "odd sign product")
        need(len({d for d, _ in rect}) == 2 and len({c for _, c in rect}) == 2, "rectangle shape")
        for cell in rect:
            need(cell not in used, "cells overlap")
            used.add(cell)
    need(len(used) == 288, "288 cells")
    return len(rects)


def best_sign_vectors(length):
    """Least number of off-diagonal cells where x_d y_c != sgn(d-c); returns (count, x, y)."""
    full = (1 << length) - 1
    pats = [sum(1 << d for d in range(length) if d > c) for c in range(length)]
    masks = [full & ~(1 << c) for c in range(length)]
    best, best_x = None, 0
    for x in range(1 << length):
        total = 0
        for c in range(length):
            a = bin((x ^ pats[c]) & masks[c]).count("1")
            total += min(a, length - 1 - a)
            if best is not None and total >= best:
                break
        else:
            best, best_x = total, x
    y = []
    for c in range(length):
        a = bin((best_x ^ pats[c]) & masks[c]).count("1")
        y.append(1 if a <= length - 1 - a else -1)
    xs = [1 if (best_x >> d) & 1 else -1 for d in range(length)]
    return best, xs, y


def grid_total(rho, xs, ys):
    """Sum over d != c of rank(s_dc I - x_d y_c I_rho) for the block-diagonal configuration."""
    total = 0
    for d in range(len(xs)):
        for c in range(len(ys)):
            if d != c:
                cell = [[Fraction(sgn(d - c) - xs[d] * ys[c]) if i == j else Fraction(0) for j in range(rho)]
                        for i in range(rho)]
                total += rank_q(cell)
    return total


def check_grid():
    mins = {}
    for length in range(2, GRID_L + 1):
        best, xs, ys = best_sign_vectors(length)
        need(best == (length - 1) ** 2 // 4, "grid minimum L=%d" % length)
        mins[str(length)] = best
    best, xs, ys = best_sign_vectors(GRID_L)
    need(best == 72, "18-stage scalar minimum")
    for rho in RHO_RANGE:
        need(grid_total(rho, xs, ys) == 72 * rho, "block-diagonal attainment rho=%d" % rho)
    return mins


def random_grid_floor(trials=40, seed=7):
    """Random (A_d, B_c) over F_p never beat 72 f(u,h) on the 18-stage grid (corroboration only)."""
    rng = random.Random(seed)
    floor_rects = len(packing_rectangles())
    for _ in range(trials):
        u, h = rng.randint(1, 4), rng.randint(1, 4)
        p = rng.choice((3, 5))
        mats_a = [[[rng.randrange(p) for _ in range(h)] for _ in range(u)] for _ in range(GRID_L + 1)]
        mats_b = [[[rng.randrange(p) for _ in range(u)] for _ in range(h)] for _ in range(GRID_L + 1)]
        total = 0
        for d in range(1, GRID_L + 1):
            for c in range(1, GRID_L + 1):
                if d != c:
                    ab = [[sum(mats_a[d][i][t] * mats_b[c][t][j] for t in range(h)) % p for j in range(u)]
                          for i in range(u)]
                    total += rank_mod([[(sgn(d - c) if i == j else 0) - ab[i][j] for j in range(u)]
                                       for i in range(u)], p)
        need(total >= floor_rects * formula(u, h), "random grid below the floor")
    return trials


# ---------------------------------------------------------------- source binding

QUOTES = [
    "R_dc + R_ec + R_ef + R_df >= min(rho, 2)",
    "the 72 quadruples",
    "Then sum over d != c of R_dc >= 144.",
    "Not claimed: any statement for stages of more than two units, or for rho > 2 beyond Lemma 1.",
    "R_dc = rank(s I - A_d B_c)",
]


def check_source():
    with open(os.path.join(ROOT, SOURCE_REL), "rb") as handle:
        raw = handle.read()
    with open(os.path.join(HERE, "SOURCES.json")) as handle:
        sources = json.load(handle)
    pinned = {row["path"]: row["sha256"] for row in sources["files"]}
    digest = hashlib.sha256(raw).hexdigest()
    need(pinned.get(SOURCE_REL) == digest, "THEOREM.md bytes differ from the pin")
    text = raw.decode("utf-8")
    for quote in QUOTES:
        need(quote in text, "quote missing from the source: %r" % quote)
    return digest


# ---------------------------------------------------------------- driver

def compute_result():
    result = {
        "claim": "exact odd-rectangle rank floor f(u,h) = max(0, 2u-h, 3u-2h, 4u-4h)",
        "source_sha256": check_source(),
        "formula_identities": check_formula_identities(),
        "constructions_range": MAX_DIM,
        "constructions": check_all_constructions(),
        "rank_identity_trials": check_rank_identity(),
        "exhaustive_minima": check_exhaustive(),
        "controls": check_controls(),
        "packing_rectangles": check_packing(),
        "scalar_grid_minima": check_grid(),
        "random_grid_trials": random_grid_floor(),
    }
    return result


def main(argv):
    write = "--write" in argv
    result = compute_result()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if write:
        with open(RESULT_PATH, "w") as handle:
            handle.write(text)
        print("wrote", RESULT_PATH)
    else:
        with open(RESULT_PATH) as handle:
            need(handle.read() == text, "RESULT.json differs from the recomputed result")
    print("PASS_FORMULA_IDENTITIES_AND_DUALITY")
    print("PASS_CONSTRUCTIONS_ALL_SIGN_PATTERNS_%dx%d" % (MAX_DIM, MAX_DIM))
    print("PASS_EXHAUSTIVE_FINITE_FIELD_MINIMA")
    print("PASS_CHARACTERISTIC_TWO_AND_EVEN_SIGN_CONTROLS")
    print("PASS_GRID_72_RECTANGLES_AND_SCALAR_MINIMUM_72")
    print("PASS_RECTANGLE_LAW_EXACT_FLOOR")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
