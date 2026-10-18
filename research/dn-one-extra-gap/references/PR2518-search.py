"""Dense-polar threshold screens at T >= 7 and an overcomplete (m = T + 1) census.

Model (DreamingOfClouds, PR 2125 / PR 2228 / PR 2111; screen convention of
PR 2272): a configuration is a list of root lines t = 1..v with vectors
p(t) = q(t) in Q^T. The full-orthogonal-pattern pairing B0 has unit diagonal
and B_ts = 1 exactly where dot(p(t), p(s)) = 0. An exact coordinate Gram
decoder M = sum_j p_j q_j^T = Gram is priced
cost = sum_j rank_F2 B[R_j, A_j] (Theorem C without the floor w), where
R_j = supp p_j and A_j = supp q_j. A gain is cost < v.

Stages:
  controls   - positive control: reproduce PR 2272's checked table
               D4/D5/D6 = 12/20/30, E6 = 36/37, E7 = 49, E8 = 72.
  t7t8       - exact full-system screens at T = 7 and T = 8.
  searches   - seeded bounded basis pivots and puncture searches at T = 7/8.
  overfull   - overcomplete one-extra rank-one family on full sets (small T).
  overpunc   - overcomplete one-extra rank-one family on every puncture of the
               declared small-T configurations (shardable).

Everything is exact integer / rational / F2 arithmetic, standard library only.
Independent reimplementation; predecessor heads are recorded in SOURCES.json.
"""
import itertools
import json
import os
import random
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
E6_BEST_PATH = os.path.join(HERE, "sources", "e6_best.json")

# ---------------------------------------------------------------- root lines

def canon(r):
    f = next(x for x in r if x)
    return tuple(r) if f > 0 else tuple(-x for x in r)


def lines(R):
    seen, out = set(), []
    for r in R:
        c = canon(r)
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def A(n):
    R = []
    for i in range(n + 1):
        for j in range(i + 1, n + 1):
            v = [0] * (n + 1)
            v[i], v[j] = 2, -2
            R.append(v)
    return lines(R)


def D(n):
    R = []
    for i in range(n):
        for j in range(i + 1, n):
            for s in (2, -2):
                v = [0] * n
                v[i], v[j] = 2, s
                R.append(v)
    return lines(R)


def Bn(n):
    R = []
    for i in range(n):
        v = [0] * n
        v[i] = 2
        R.append(v)
        for j in range(i + 1, n):
            for s in (2, -2):
                w = [0] * n
                w[i], w[j] = 2, s
                R.append(w)
    return lines(R)


def Cn(n):
    R = []
    for i in range(n):
        v = [0] * n
        v[i] = 4
        R.append(v)
        for j in range(i + 1, n):
            for s in (2, -2):
                w = [0] * n
                w[i], w[j] = 2, s
                R.append(w)
    return lines(R)


def F4():
    R = []
    for i in range(4):
        v = [0] * 4
        v[i] = 2
        R.append(v)
        for j in range(i + 1, 4):
            for s in (2, -2):
                w = [0] * 4
                w[i], w[j] = 2, s
                R.append(w)
    for sg in itertools.product((1, -1), repeat=4):
        R.append(list(sg))
    return lines(R)


def E8():
    R = [list(r) for r in D(8)]
    for sg in itertools.product((1, -1), repeat=8):
        if sg.count(-1) % 2 == 0:
            R.append(list(sg))
    return lines(R)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def E7():
    return [r for r in E8() if sum(r) == 0]


def E6():
    r1 = [2, -2, 0, 0, 0, 0, 0, 0]
    r2 = [0, 2, -2, 0, 0, 0, 0, 0]
    return [r for r in E8() if dot(r, r1) == 0 and dot(r, r2) == 0]


def pm1_lines(T):
    """All lines with coordinates in {0, +1, -1}, canonical sign."""
    R = []
    for r in itertools.product((1, 0, -1), repeat=T):
        if any(r):
            R.append(list(r))
    return lines(R)


# ------------------------------------------------------------ F2 machinery

def rank2(rows):
    piv = []
    for x in rows:
        for p in piv:
            x = min(x, x ^ p)
        if x:
            piv.append(x)
            piv.sort(reverse=True)
    return len(piv)


def b0_rows(L):
    """Full orthogonal pattern as bitset rows: unit diagonal + orth pairs."""
    v = len(L)
    out = []
    for t in range(v):
        bits = 1 << t
        for s in range(v):
            if s != t and dot(L[t], L[s]) == 0:
                bits |= 1 << s
        out.append(bits)
    return out


def supports(P):
    """Column supports of the coefficient matrix P (nonzero test over Q)."""
    v = len(P)
    T = len(P[0]) if P else 0
    return [frozenset(t for t in range(v) if P[t][j] != 0) for j in range(T)]


def cost_from_supports(Brows, RS, AS):
    out = []
    for R, A in zip(RS, AS):
        if not R or not A:
            out.append(0)
            continue
        amask = 0
        for s in A:
            amask |= 1 << s
        rows = [Brows[t] & amask for t in R]
        out.append(rank2(rows))
    return out


def cost_from_masks(Brows, RS, AS):
    """Same cost with supports given as bitmasks."""
    out = []
    n = len(Brows)
    for R, A in zip(RS, AS):
        if not R or not A:
            out.append(0)
            continue
        rows = [Brows[t] & A for t in range(n) if (R >> t) & 1]
        out.append(rank2(rows))
    return out


def sup_mask(S):
    m = 0
    for s in S:
        m |= 1 << s
    return m


# ------------------------------------------------- exact coordinate decoder

def solve_coords(basis, r):
    n = len(basis)
    m = len(r)
    M = [[F(basis[i][k]) for i in range(n)] + [F(r[k])] for k in range(m)]
    piv, row = [], 0
    for c in range(n):
        p = next((i for i in range(row, m) if M[i][c] != 0), None)
        if p is None:
            raise ValueError("dependent basis")
        M[row], M[p] = M[p], M[row]
        inv = M[row][c]
        M[row] = [x / inv for x in M[row]]
        for i in range(m):
            if i != row and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[row])]
        row += 1
    return [M[i][n] for i in range(n)]


def frac_rank(rows):
    M = [[F(x) for x in r] for r in rows]
    rk = 0
    if not M:
        return 0
    for c in range(len(M[0])):
        p = next((i for i in range(rk, len(M)) if M[i][c] != 0), None)
        if p is None:
            continue
        M[rk], M[p] = M[p], M[rk]
        for i in range(rk + 1, len(M)):
            if M[i][c] != 0:
                f = M[i][c] / M[rk][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[rk])]
        rk += 1
    return rk


def first_basis(L):
    idx, cur = [], []
    for i, r in enumerate(L):
        if frac_rank(cur + [r]) > len(cur):
            idx.append(i)
            cur.append(r)
    return idx


def decoder_std(L):
    return [[F(x) for x in r] for r in L], [[F(x) for x in r] for r in L]


def decoder_basis(L, bidx):
    basis = [L[i] for i in bidx]
    n = len(basis)
    C = [[dot(basis[i], basis[k]) for k in range(n)] for i in range(n)]
    P = [solve_coords(basis, r) for r in L]
    Q = [[sum(P[t][i] * C[i][k] for i in range(n)) for k in range(n)] for t in range(len(L))]
    return P, Q


def config_cost(L, P, Q, Brows=None):
    if Brows is None:
        Brows = b0_rows(L)
    RS, AS = supports(P), supports(Q)
    br = cost_from_supports(Brows, RS, AS)
    return sum(br), br


# ------------------------------------------------------ one-extra rank-one

def ternary_dirs(T):
    """All projective directions a in Q^T with entries in {0, +1, -1}."""
    out = set()
    for r in itertools.product((1, 0, -1), repeat=T):
        if any(r):
            out.add(tuple(F(x) for x in canon(list(r))))
    return sorted(out)


def one_extra_cells(X, H, a):
    """All exact lambda support cells of PR 2240's identity for direction a.

    p_i = X e_i, q_i = X(H e_i - lambda a_i a), i = 1..T
    p_{T+1} = X a, q_{T+1} = lambda X a.
    Returns a list of tuples (cell_id, [term supports (R_j, A_j) masks]).
    Supports are constant on each cell; cells are the open intervals between
    consecutive breakpoints plus the breakpoints themselves (lambda != 0).
    """
    T = len(X[0])
    n = len(X)
    alpha = [dot(X[t], a) for t in range(n)]           # p(t) . a
    beta = [[dot(X[t], [H[i][k] for k in range(T)]) for i in range(T)] for t in range(n)]
    # p(t) . q_i = beta[t][i] - lambda * a[i] * alpha[t]
    brk = set()
    for t in range(n):
        for i in range(T):
            ai = a[i]
            if ai != 0 and alpha[t] != 0:
                brk.add(F(beta[t][i], 1) / (F(ai) * F(alpha[t])))
    brk = sorted(b for b in brk if b != 0)
    samples = [("at", b) for b in brk]
    cuts = sorted(set([F(0)] + brk))
    # Open cells between consecutive cut points, plus the two unbounded cells.
    edges = [None] + cuts + [None]
    for lo, hi in zip(edges, edges[1:]):
        if lo is None and hi is None:
            continue
        if lo is None:
            samples.append(("in", hi - 1))
        elif hi is None:
            samples.append(("in", lo + 1))
        else:
            samples.append(("in", (lo + hi) / 2))
    S = [sup_mask(t for t in range(n) if X[t][i] != 0) for i in range(T)]
    Ta = sup_mask(t for t in range(n) if alpha[t] != 0)
    out = []
    for cid, lam in samples:
        AS = []
        for i in range(T):
            if a[i] == 0:
                c = [H[i][k] for k in range(T)]
            else:
                c = [F(H[i][k]) - F(lam) * F(a[i]) * F(a[k]) for k in range(T)]
            AS.append(sup_mask(t for t in range(n) if dot(X[t], c) != 0))
        terms = [(S[i], AS[i]) for i in range(T)] + [(Ta, Ta)]
        out.append((cid, lam, terms))
    return out


def verify_identity(X, H, a, lam):
    """Exact check that the one-extra identity sums to G = X H X^T at (a, lam),
    and that the recorded supports match the constructed p_j, q_j."""
    T = len(X[0])
    n = len(X)
    G = [[sum(X[t][i] * H[i][k] * X[s][k] for i in range(T) for k in range(T))
          for s in range(n)] for t in range(n)]
    P, Q = [], []
    for i in range(T):
        pi = [X[t][i] for t in range(n)]
        qi = [sum(X[t][k] * (F(H[i][k]) - F(lam) * F(a[i]) * F(a[k])) for k in range(T))
              for t in range(n)]
        P.append(pi)
        Q.append(qi)
    P.append([sum(X[t][k] * F(a[k]) for k in range(T)) for t in range(n)])
    Q.append([F(lam) * sum(X[t][k] * F(a[k]) for k in range(T)) for t in range(n)])
    for t in range(n):
        for s in range(n):
            lhs = sum(P[j][t] * Q[j][s] for j in range(T + 1))
            if lhs != G[t][s]:
                return False, "identity mismatch at (%d,%d)" % (t, s)
    for t in range(n):
        if G[t][t] == 0:
            return False, "zero diagonal at %d" % t
    return True, "ok"


def one_extra_census_full(L, X, H, dirs, label):
    """Exact census of the one-extra rank-one family on one full configuration."""
    n = len(L)
    T = len(X[0])
    Brows = b0_rows(L)
    best = None
    hist = {}
    cells_total = 0
    ident_ok = 0
    for a in dirs:
        cells = one_extra_cells(X, H, a)
        for k, (cid, lam, terms) in enumerate(cells):
            cells_total += 1
            if k in (0, len(cells) // 2, len(cells) - 1):
                ok, why = verify_identity(X, H, a, lam)
                if not ok:
                    raise AssertionError("identity failed for %s dir=%s cell=%s: %s" % (label, a, cid, why))
                ident_ok += 1
            br = cost_from_masks(Brows, [R for R, _ in terms], [A for _, A in terms])
            c = sum(br)
            hist[c] = hist.get(c, 0) + 1
            if best is None or c < best[0]:
                best = (c, list(a), cid, str(lam))
    return {
        "label": label,
        "v": n,
        "T": T,
        "directions": len(dirs),
        "cells": cells_total,
        "identity_checks": ident_ok,
        "min_cost": best[0],
        "min_cost_minus_v": best[0] - n,
        "min_witness": {"dir": [str(x) for x in best[1]], "cell": best[2], "lambda": str(best[3])},
        "hist": {str(k): hist[k] for k in sorted(hist)},
    }


def one_extra_punctures(L, X, H, dirs, label, mask_range=None):
    """Exhaustive puncture census: every nonempty subset U of lines, with the
    family restricted to U (supports and B0 intersected with U).

    The per-subset live-count prefilter is validated against unfiltered exact
    minima on a deterministic sample of subsets (brute_masks)."""
    n = len(L)
    T = len(X[0])
    Brows = b0_rows(L)
    # Precompute the global family term-support tuples once.
    fam = []
    for a in dirs:
        for cid, lam, terms in one_extra_cells(X, H, a):
            fam.append([(R, A) for R, A in terms])
    lo, hi = (1, (1 << n) - 1) if mask_range is None else mask_range
    brute_masks = {lo, hi, lo + 1, hi - 1, (lo + hi) // 2}
    brute_mismatches = []
    gains = []
    best = None
    ties = 0
    checked = 0
    for mask in range(lo, hi + 1):
        vs = mask.bit_count()
        checked += 1
        cache = {}

        def block_rank(R, A):
            key = (R & mask, A & mask)
            v = cache.get(key)
            if v is None:
                k, l = key
                if not k or not l:
                    v = 0
                else:
                    rows = [Brows[t] & l for t in range(n) if (k >> t) & 1]
                    v = rank2(rows)
                cache[key] = v
            return v

        best_u = None
        for terms in fam:
            live = 0
            for R, A in terms:
                k, l = R & mask, A & mask
                if not k or not l:
                    continue
                for t in range(n):
                    if (k >> t) & 1 and Brows[t] & l:
                        live += 1
                        break
            if best_u is not None and live >= best_u:
                continue
            c = sum(block_rank(R, A) for R, A in terms)
            if best_u is None or c < best_u:
                best_u = c
            if best_u == 0:
                break
        d = best_u - vs
        if mask in brute_masks:
            brute = min(sum(block_rank(R, A) for R, A in terms) for terms in fam)
            if brute != best_u:
                brute_mismatches.append((mask, best_u, brute))
        if best is None or d < best[0]:
            best = (d, mask, vs, best_u)
        if best_u < vs:
            gains.append((mask, vs, best_u))
        elif best_u == vs:
            ties += 1
    return {
        "label": label,
        "lines": n,
        "subsets_checked": checked,
        "directions": len(dirs),
        "family_members_per_subset": len(fam),
        "min_cost_minus_v": best[0],
        "best_mask": best[1],
        "best_v": best[2],
        "best_cost": best[3],
        "gain_count": len(gains),
        "gains": gains[:10],
        "tie_count": ties,
        "brute_masks_checked": sorted(m for m in brute_masks if lo <= m <= hi),
        "brute_mismatches": brute_mismatches,
    }


# ------------------------------------------------------------------ controls

def expect(name, got, want, fails):
    ok = got == want
    print("CTRL %-42s got=%s want=%s %s" % (name, got, want, "OK" if ok else "MISMATCH"))
    if not ok:
        fails.append((name, got, want))
    return ok


def stage_controls(fails, cert):
    """Positive control: PR 2272's checked table (PR 2125 values)."""
    tab = {}
    for nm in ("D4", "D5", "D6"):
        L = {"D4": D(4), "D5": D(5), "D6": D(6)}[nm]
        P, Q = decoder_std(L)
        c, br = config_cost(L, P, Q)
        tab[nm] = {"v": len(L), "T": len(L[0]), "cost": c, "block_ranks": br}
        expect("%s std B0 cost" % nm, c, {"D4": 12, "D5": 20, "D6": 30}[nm], fails)
    L6 = E6()
    with open(E6_BEST_PATH, encoding="utf-8") as f:
        e6 = json.load(f)
    P6, Q6 = decoder_basis(L6, e6["basis"])
    Bstored = [e6["rows"][t] for t in range(len(L6))]
    cs, brs = config_cost(L6, P6, Q6, Bstored)
    expect("E6 stored basis + stored B cost", cs, 36, fails)
    expect("E6 stored cost matches e6_best.json", cs, e6["cost"], fails)
    cb, brb = config_cost(L6, P6, Q6)
    P6f, Q6f = decoder_basis(L6, first_basis(L6))
    cf, brf = config_cost(L6, P6f, Q6f)
    expect("E6 first-basis B0 cost", cf, 37, fails)
    tab["E6"] = {"v": 36, "T": 6, "cost": cs, "block_ranks": brs}
    tab["E6_firstB0"] = {"v": 36, "T": 6, "cost": cf, "block_ranks": brf}
    tab["E6_storedB0"] = {"v": 36, "T": 6, "cost": cb, "block_ranks": brb}
    L7, L8 = E7(), E8()
    P7, Q7 = decoder_basis(L7, first_basis(L7))
    c7, br7 = config_cost(L7, P7, Q7)
    expect("E7 first-basis B0 cost", c7, 49, fails)
    tab["E7"] = {"v": len(L7), "T": 7, "cost": c7, "block_ranks": br7}
    P8, Q8 = decoder_basis(L8, first_basis(L8))
    c8, br8 = config_cost(L8, P8, Q8)
    expect("E8 first-basis B0 cost", c8, 72, fails)
    tab["E8"] = {"v": len(L8), "T": 8, "cost": c8, "block_ranks": br8}
    for nm, want in (("A4", 16), ("A5", 25), ("A6", 36)):
        L = {"A4": A(4), "A5": A(5), "A6": A(6)}[nm]
        P, Q = decoder_basis(L, first_basis(L))
        c, br = config_cost(L, P, Q)
        tab[nm + "_firstBasis"] = {"v": len(L), "T": len(P[0]), "cost": c, "block_ranks": br}
        expect("%s first-basis B0 cost" % nm, c, want, fails)
    # mutation control: B = identity must change the cost on D5 and E7
    L5 = D(5)
    P5, Q5 = decoder_std(L5)
    ci, _ = config_cost(L5, P5, Q5, [1 << t for t in range(len(L5))])
    expect("D5 mutated B=I cost differs from 20", ci != 20, True, fails)
    ci7, _ = config_cost(L7, P7, Q7, [1 << t for t in range(len(L7))])
    expect("E7 mutated B=I cost differs from 49", ci7 != 49, True, fails)
    cert["controls"] = tab
    return tab


# ------------------------------------------------------------- T = 7, 8

def stage_t7t8(cert):
    full = {}
    jobs = (("A7", A(7), "first"), ("B7", Bn(7), "std"), ("C7", Cn(7), "std"),
            ("D7", D(7), "std"), ("E7", E7(), "first"),
            ("pm1_T7", pm1_lines(7), "std"),
            ("A8", A(8), "first"), ("B8", Bn(8), "std"), ("C8", Cn(8), "std"),
            ("D8", D(8), "std"), ("E8", E8(), "first"),
            ("pm1_T8", pm1_lines(8), "std"))
    for nm, L, kind in jobs:
        if kind == "std":
            P, Q = decoder_std(L)
        else:
            P, Q = decoder_basis(L, first_basis(L))
        c, br = config_cost(L, P, Q)
        v = len(L)
        width = len(P[0])
        full[nm] = {"v": v, "T_width": width, "ambient": len(L[0]), "cost": c,
                    "cost_minus_v": c - v, "gain": c < v,
                    "v_over_Tsq": v > width * width, "block_ranks": br}
        print("T78 %-8s v=%4d width=%d ambient=%d cost=%5d cost-v=%+d gain=%s v>T^2=%s"
              % (nm, v, width, len(L[0]), c, c - v, c < v, v > width * width))
    cert["t7t8_full"] = full


def stage_searches(cert):
    rng = random.Random(20261015)
    out = {}
    jobs = (("A7", A(7)), ("B7", Bn(7)), ("D7", D(7)), ("E7", E7()),
            ("A8", A(8)), ("B8", Bn(8)), ("D8", D(8)))
    for nm, L in jobs:
        T = frac_rank(L)
        best = None
        idxs = list(range(len(L)))
        for _ in range(300):
            rng.shuffle(idxs)
            pick, cur = [], []
            for i in idxs:
                if len(pick) >= T:
                    break
                if frac_rank(cur + [L[i]]) > len(cur):
                    pick.append(i)
                    cur.append(L[i])
            if len(pick) != T:
                continue
            try:
                P, Q = decoder_basis(L, pick)
            except ValueError:
                continue
            c, _ = config_cost(L, P, Q)
            if best is None or c < best[0]:
                best = (c, list(pick))
        stdc, _ = config_cost(L, *decoder_std(L)) if frac_rank(L) == len(L[0]) else (None, None)
        out[nm + "_basis_pivot"] = {"trials": 300, "min_cost": best[0], "v": len(L),
                                    "min_cost_minus_v": best[0] - len(L),
                                    "std_cost": stdc, "basis": best[1]}
        print("PIV %-8s bases=300 min=%d v=%d min-v=%+d" % (nm, best[0], len(L), best[0] - len(L)))
    # seeded greedy/random puncture searches at T = 7/8 (small systems only)
    for nm, L in (("A7", A(7)), ("B7", Bn(7)), ("D7", D(7))):
        P, Q = decoder_std(L) if frac_rank(L) == len(L[0]) else decoder_basis(L, first_basis(L))
        n = len(L)
        Brows = b0_rows(L)
        T = len(P[0])
        Pnz = [frozenset(j for j in range(T) if P[t][j] != 0) for t in range(n)]
        Qnz = [frozenset(j for j in range(T) if Q[t][j] != 0) for t in range(n)]

        def cost_of(mask):
            br = 0
            for j in range(T):
                rows = [Brows[t] & mask for t in range(n) if (mask >> t) & 1 and j in Pnz[t]]
                cols = sup_mask(s for s in range(n) if (mask >> s) & 1 and j in Qnz[s])
                br += rank2([rw & cols for rw in rows]) if rows else 0
            return br

        best = None
        for _ in range(12):
            vs = rng.randint(2, n)
            mask = 0
            for t in rng.sample(range(n), vs):
                mask |= 1 << t
            cur = cost_of(mask) - mask.bit_count()
            if best is None or cur < best[0]:
                best = (cur, mask)
            for _ in range(250):
                t = rng.randrange(n)
                cand = mask ^ (1 << t)
                if cand.bit_count() < 2:
                    continue
                d = cost_of(cand) - cand.bit_count()
                if d <= cur:
                    mask, cur = cand, d
                    if d < best[0]:
                        best = (d, mask)
        for _ in range(200):
            vs = rng.randint(2, n)
            mask = 0
            for t in rng.sample(range(n), vs):
                mask |= 1 << t
            d = cost_of(mask) - mask.bit_count()
            if d < best[0]:
                best = (d, mask)
        out[nm + "_puncture_search"] = {"greedy_restarts": 12, "greedy_steps": 250,
                                        "random_trials": 200, "min_cost_minus_v": best[0],
                                        "mask": best[1], "v": best[1].bit_count(),
                                        "cost": best[0] + best[1].bit_count()}
        print("SRCH %-8s min(cost-v)=%+d (v=%d)" % (nm, best[0], best[1].bit_count()))
    cert["t7t8_searches"] = out


# ------------------------------------------------------------ overcomplete

def configs_smallT():
    """(label, L, X, H) for the overcomplete census.

    Uses standard coordinates (H = I) where the line span is the full ambient
    space (D/B/C/F4/{0,+/-1} families, the PR 2125 D-series convention) and the
    first-independent span basis otherwise (A family)."""
    out = []
    for nm, L in (("A3", A(3)), ("B3", Bn(3)), ("pm1_T3", pm1_lines(3)),
                  ("A4", A(4)), ("B4", Bn(4)), ("C4", Cn(4)), ("D4", D(4)), ("F4", F4()),
                  ("pm1_T4", pm1_lines(4)),
                  ("A5", A(5)), ("B5", Bn(5)), ("C5", Cn(5)), ("D5", D(5))):
        if frac_rank(L) == len(L[0]):
            P, Q = decoder_std(L)
            H = [[1 if i == k else 0 for k in range(len(L[0]))] for i in range(len(L[0]))]
        else:
            bidx = first_basis(L)
            P, Q = decoder_basis(L, bidx)
            basis = [L[i] for i in bidx]
            T = len(basis)
            H = [[dot(basis[i], basis[k]) for k in range(T)] for i in range(T)]
        out.append((nm, L, P, H))
    return out


def stage_overfull(cert):
    res = {}
    for nm, L, X, H in configs_smallT():
        T = len(X[0])
        dirs = sorted(set(ternary_dirs(T)) | set(canon([x for x in r]) for r in X))
        dirs = [tuple(F(x) for x in a) for a in dirs]
        r = one_extra_census_full(L, X, H, dirs, nm)
        res[nm] = r
        print("OVF %-8s v=%3d T=%d dirs=%d cells=%d min=%d min-v=%+d"
              % (nm, r["v"], r["T"], r["directions"], r["cells"], r["min_cost"], r["min_cost_minus_v"]))
    cert["overcomplete_full"] = res


def stage_overpunc(cert, only=None, mask_range=None):
    res = {}
    for nm, L, X, H in configs_smallT():
        if only is not None and nm not in only:
            continue
        if nm not in ("A3", "B3", "pm1_T3", "A4", "B4", "C4", "D4"):
            continue
        T = len(X[0])
        dirs = sorted(set(ternary_dirs(T)) | set(canon([x for x in r]) for r in X))
        dirs = [tuple(F(x) for x in a) for a in dirs]
        r = one_extra_punctures(L, X, H, dirs, nm, mask_range=mask_range)
        if r["brute_mismatches"]:
            raise AssertionError("prefilter mismatch on %s: %s" % (nm, r["brute_mismatches"]))
        res[nm] = r
        print("OVP %-8s subsets=%d dirs=%d members=%d min(cost-v)=%+d gains=%d ties=%d"
              % (nm, r["subsets_checked"], r["directions"], r["family_members_per_subset"],
                 r["min_cost_minus_v"], r["gain_count"], r["tie_count"]))
    cert.setdefault("overcomplete_punctures", {}).update(res)


# ----------------------------------------------------------------- driver

def compute(stage, fails, cert, only=None, mask_range=None):
    if stage == "controls":
        stage_controls(fails, cert)
    elif stage == "t7t8":
        stage_t7t8(cert)
    elif stage == "searches":
        stage_searches(cert)
    elif stage == "overfull":
        stage_overfull(cert)
    elif stage == "overpunc":
        stage_overpunc(cert, only=only, mask_range=mask_range)
    else:
        raise SystemExit("unknown stage: " + stage)


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    args = argv[1:]
    emit = "--emit" in args
    args = [a for a in args if a != "--emit"]
    stage = "all"
    only = None
    mask_range = None
    if "--stage" in args:
        stage = args[args.index("--stage") + 1]
    if "--only" in args:
        only = set(args[args.index("--only") + 1].split(","))
    if "--mask-range" in args:
        lo, hi = args[args.index("--mask-range") + 1].split(":")
        mask_range = (int(lo), int(hi))
    fails = []
    cert_path = os.path.join(HERE, "CERTIFICATE.json")
    cert = {"screen": "polar-law T >= 7 threshold screens and small-T overcomplete census",
            "model": "full-orthogonal-pattern pairing B0, exact coordinate Gram decoder(s), cost = sum_j rank_F2 B[R_j, A_j]",
            "python": sys.version.split()[0]}
    stages = ["controls", "t7t8", "searches", "overfull", "overpunc"] if stage == "all" else [stage]
    for st in stages:
        print("== stage %s ==" % st)
        compute(st, fails, cert, only=only, mask_range=mask_range)
    cert["control_failures"] = fails
    if emit:
        # Merge with any existing certificate so shard runs accumulate.
        if os.path.exists(cert_path):
            old = json.load(open(cert_path, encoding="utf-8"))
            for k, v in cert.items():
                if k in ("overcomplete_punctures", "overcomplete_full", "t7t8_full", "t7t8_searches") and isinstance(v, dict):
                    merged = dict(old.get(k, {}))
                    merged.update(v)
                    old[k] = merged
                else:
                    old[k] = v
            cert = old
        with open(cert_path, "w", encoding="utf-8") as f:
            json.dump(cert, f, indent=1, sort_keys=True)
        print("CERTIFICATE:", cert_path)
    print("CONTROL_FAILURES:", len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
