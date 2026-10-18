"""Dense-polar-law small-T gain screen.

Model (DreamingOfClouds, PR 2125 / PR 2228 / #1590): a configuration is a list of
root lines t = 1..v with vectors p(t) = q(t) in Q^T. The full-orthogonal-pattern
pairing B has unit diagonal and B_ts = 1 exactly where dot(p(t), p(s)) = 0. The
exact coordinate Gram decoder M = sum_j p_j q_j^T = Gram is priced
cost = sum_j rank_F2 B[R_j, A_j] (Theorem C without the floor w), where
R_j = supp p_j and A_j = supp q_j. A gain is cost < v.

Question screened (discussion 1166 comment 18934590 item 3): does any T <= 6
configuration have cost < v?

Everything here is exact integer / rational / F2 arithmetic, standard library
only. Independent reimplementation; PR 2125's files are pinned only as the
source of the table values and of the stored E6 basis/pairing.
"""
import itertools
import json
import hashlib
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


# ------------------------------------------------------------------ controls

def expect(name, got, want, fails):
    ok = got == want
    print("CTRL %-38s got=%s want=%s %s" % (name, got, want, "OK" if ok else "MISMATCH"))
    if not ok:
        fails.append((name, got, want))
    return ok


def controls(fails):
    tab = {}
    for nm in ("D4", "D5", "D6"):
        L = {"D4": D(4), "D5": D(5), "D6": D(6)}[nm]
        P, Q = decoder_std(L)
        c, br = config_cost(L, P, Q)
        tab[nm] = (len(L), c, br)
        expect("%s standard B0 cost" % nm, c, {"D4": 12, "D5": 20, "D6": 30}[nm], fails)
    for nm, want in (("A4", 16), ("A5", 25), ("A6", 36)):
        L = {"A4": A(4), "A5": A(5), "A6": A(6)}[nm]
        P, Q = decoder_basis(L, first_basis(L))
        c, br = config_cost(L, P, Q)
        tab[nm] = (len(L), c, br)
        expect("%s first-basis B0 cost" % nm, c, want, fails)
    L7, L8 = E7(), E8()
    P7, Q7 = decoder_basis(L7, first_basis(L7))
    c7, br7 = config_cost(L7, P7, Q7)
    tab["E7"] = (len(L7), c7, br7)
    expect("E7 first-basis B0 cost", c7, 49, fails)
    P8, Q8 = decoder_basis(L8, first_basis(L8))
    c8, br8 = config_cost(L8, P8, Q8)
    tab["E8"] = (len(L8), c8, br8)
    expect("E8 first-basis B0 cost", c8, 72, fails)
    # E6: stored basis + stored pairing (PR 2125 data/e6_best.json), then B0
    L6 = E6()
    with open(E6_BEST_PATH, encoding="utf-8") as f:
        e6 = json.load(f)
    P6, Q6 = decoder_basis(L6, e6["basis"])
    Bstored = [e6["rows"][t] for t in range(len(L6))]
    cs, brs = config_cost(L6, P6, Q6, Bstored)
    expect("E6 stored basis + stored B cost", cs, e6["cost"], fails)
    cb, brb = config_cost(L6, P6, Q6)
    tab["E6"] = (len(L6), cs, brs)
    P6f, Q6f = decoder_basis(L6, first_basis(L6))
    cf, brf = config_cost(L6, P6f, Q6f)
    expect("E6 first-basis B0 cost", cf, 37, fails)
    tab["E6_firstB0"] = (len(L6), cf, brf)
    tab["E6_storedB0"] = (len(L6), cb, brb)
    # F4: record-only. PR 2125 reports 24 as a recorded (searched) value, not a
    # checked B0 value; standard coordinates with B0 give another upper bound.
    Lf = F4()
    Pf, Qf = decoder_std(Lf)
    cff, brff = config_cost(Lf, Pf, Qf)
    tab["F4"] = (len(Lf), cff, brff)
    print("CTRL %-38s got=%s (record-only; PR 2125 recorded 24 from a searched pairing)" % ("F4 standard B0 cost", cff))
    # mutation control: B = identity must differ from B0 on D5 and E7
    L5 = D(5)
    P5, Q5 = decoder_std(L5)
    v = len(L5)
    Bi = [1 << t for t in range(v)]
    ci, _ = config_cost(L5, P5, Q5, Bi)
    expect("D5 mutated B=I cost differs from 20", ci != 20, True, fails)
    ci7, _ = config_cost(L7, P7, Q7, [1 << t for t in range(len(L7))])
    expect("E7 mutated B=I cost differs from 49", ci7 != 49, True, fails)
    return tab


# ------------------------------------------------------- exhaustive punctures

def exhaustive_punctures(L, P, Q, label, min_v=1):
    """All subsets of L (decoder and B0 restricted to the subset)."""
    n = len(L)
    Bfull = b0_rows(L)
    Pnz = [[j for j in range(len(P[0])) if P[t][j] != 0] for t in range(n)]
    Qnz = [[j for j in range(len(Q[0])) if Q[s][j] != 0] for s in range(n)]
    T = len(P[0])
    best = None  # (cost - v, mask)
    gains, ties = [], 0
    checked = 0
    for mask in range(1, 1 << n):
        vs = mask.bit_count()
        if vs < min_v:
            continue
        checked += 1
        br = []
        for j in range(T):
            rows = [Bfull[t] & mask for t in range(n) if (mask >> t) & 1 and j in Pnz[t]]
            if not rows:
                br.append(0)
                continue
            cols = 0
            for s in range(n):
                if (mask >> s) & 1 and j in Qnz[s]:
                    cols |= 1 << s
            br.append(rank2([rw & cols for rw in rows]))
        c = sum(br)
        d = c - vs
        if best is None or d < best[0]:
            best = (d, mask, vs, c)
        if c < vs:
            gains.append((mask, vs, c))
        elif c == vs:
            ties += 1
    return {
        "label": label,
        "lines": n,
        "subsets_checked": checked,
        "min_cost_minus_v": best[0],
        "best_mask": best[1],
        "best_v": best[2],
        "best_cost": best[3],
        "gains": gains[:10],
        "gain_count": len(gains),
        "tie_count": ties,
    }


# -------------------------------------------------------- bounded searchers

def greedy_search(L, P, Q, rng, restarts=12, steps=250, vmin=2):
    """Hill-climb on subsets: add/remove one line, minimize cost - v."""
    n = len(L)
    Bfull = b0_rows(L)
    T = len(P[0])

    def cost_of(mask):
        br = 0
        for j in range(T):
            rows = [Bfull[t] & mask for t in range(n) if (mask >> t) & 1 and P[t][j] != 0]
            cols = 0
            for s in range(n):
                if (mask >> s) & 1 and Q[s][j] != 0:
                    cols |= 1 << s
            br += rank2([rw & cols for rw in rows]) if rows else 0
        return br

    best = None
    for _ in range(restarts):
        vs = rng.randint(vmin, n)
        mask = 0
        for t in rng.sample(range(n), vs):
            mask |= 1 << t
        cur = cost_of(mask) - mask.bit_count()
        if best is None or cur < best[0]:
            best = (cur, mask)
        for _ in range(steps):
            t = rng.randrange(n)
            cand = mask ^ (1 << t)
            if cand.bit_count() < vmin:
                continue
            d = cost_of(cand) - cand.bit_count()
            if d <= cur:
                mask, cur = cand, d
                if d < best[0]:
                    best = (d, mask)
    return {"min_cost_minus_v": best[0], "mask": best[1],
            "v": best[1].bit_count(), "cost": best[0] + best[1].bit_count()}


def basis_pivot_search(L, rng, trials=150, bidx0=None):
    """Bounded search over bases of the line span: pick T independent lines as
    the basis, build the exact coordinate decoder, price B0. Reports the min."""
    n = len(L)
    T = frac_rank(L)
    best = None
    idxs = list(range(n))
    cands = []
    if bidx0 is not None:
        cands.append(list(bidx0))
    for _ in range(trials):
        rng.shuffle(idxs)
        pick, cur = [], []
        for i in idxs:
            if len(pick) >= T:
                break
            if frac_rank(cur + [L[i]]) > len(cur):
                pick.append(i)
                cur.append(L[i])
        if len(pick) == T:
            cands.append(pick)
    for bidx in cands:
        try:
            P, Q = decoder_basis(L, bidx)
        except ValueError:
            continue
        c, _ = config_cost(L, P, Q)
        d = c - n
        if best is None or d < best[0]:
            best = (d, c, list(bidx))
    return {"min_cost_minus_v": best[0], "cost": best[1], "basis": best[2], "bases_tried": len(cands)}


def random_subsets(L, P, Q, rng, trials=300, vmin=2):
    n = len(L)
    Bfull = b0_rows(L)
    T = len(P[0])
    best = None
    for _ in range(trials):
        vs = rng.randint(vmin, n)
        mask = 0
        for t in rng.sample(range(n), vs):
            mask |= 1 << t
        br = 0
        for j in range(T):
            rows = [Bfull[t] & mask for t in range(n) if (mask >> t) & 1 and P[t][j] != 0]
            cols = 0
            for s in range(n):
                if (mask >> s) & 1 and Q[s][j] != 0:
                    cols |= 1 << s
            br += rank2([rw & cols for rw in rows]) if rows else 0
        d = br - vs
        if best is None or d < best[0]:
            best = (d, mask, vs, br)
    return {"min_cost_minus_v": best[0], "mask": best[1], "v": best[2], "cost": best[3]}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    fails = []
    cert = {
        "screen": "dense-polar small-T gain screen (discussion 1166 comment 18934590 item 3)",
        "model": "full-orthogonal-pattern pairing B0, exact coordinate Gram decoder, cost = sum_j rank_F2 B[R_j, A_j]",
        "python": sys.version.split()[0],
    }
    print("== controls (PR 2125 table) ==")
    tab = controls(fails)
    cert["controls"] = {k: {"v": v, "cost": c, "block_ranks": br} for k, (v, c, br) in tab.items()}

    print("== exhaustive punctures ==")
    ex = []
    for lab, L, P, Q in (
        ("T3_pm1_all_subsets", pm1_lines(3), *decoder_std(pm1_lines(3))),
        ("D4_all_subsets", D(4), *decoder_std(D(4))),
        ("D5_all_subsets", D(5), *decoder_std(D(5))),
    ):
        r = exhaustive_punctures(L, P, Q, lab)
        ex.append(r)
        print("EX %-24s subsets=%d min(cost-v)=%d best v=%d cost=%d gains=%d ties=%d"
              % (lab, r["subsets_checked"], r["min_cost_minus_v"], r["best_v"], r["best_cost"],
                 r["gain_count"], r["tie_count"]))
    cert["exhaustive"] = ex

    print("== full configurations at T <= 6 ==")
    full = {}
    for nm, L in (("A4", A(4)), ("A5", A(5)), ("A6", A(6)),
                  ("B5", Bn(5)), ("B6", Bn(6)), ("C6", Cn(6)),
                  ("D4", D(4)), ("D5", D(5)), ("D6", D(6)), ("F4", F4()),
                  ("pm1_T4", pm1_lines(4)), ("pm1_T5", pm1_lines(5)), ("pm1_T6", pm1_lines(6))):
        P, Q = decoder_std(L)
        c, br = config_cost(L, P, Q)
        full[nm] = {"v": len(L), "T": len(L[0]), "cost": c, "cost_minus_v": c - len(L), "block_ranks": br}
        print("FULL %-8s v=%3d T=%d cost=%4d cost-v=%d" % (nm, len(L), len(L[0]), c, c - len(L)))
    for nm, L in (("E6_stored_basis", None),):
        L = E6()
        with open(E6_BEST_PATH, encoding="utf-8") as f:
            e6 = json.load(f)
        P, Q = decoder_basis(L, e6["basis"])
        c, br = config_cost(L, P, Q)
        full[nm] = {"v": len(L), "T": 6, "cost": c, "cost_minus_v": c - len(L), "block_ranks": br}
        print("FULL %-8s v=%3d T=6 cost=%4d cost-v=%d (B0; stored B costs 36)" % (nm, len(L), c, c - len(L)))
    cert["full_configs"] = full

    print("== bounded searches (seeded) ==")
    rng = random.Random(20261015)
    bounded = {}
    for nm, L, basis in (("E6_greedy", E6(), "stored"), ("D6_greedy", D(6), "std"),
                         ("B6_greedy", Bn(6), "std"), ("A6_greedy", A(6), "std"),
                         ("pm1T4_greedy", pm1_lines(4), "std"), ("pm1T5_greedy", pm1_lines(5), "std"),
                         ("pm1T6_greedy", pm1_lines(6), "std")):
        if basis == "stored":
            with open(E6_BEST_PATH, encoding="utf-8") as f:
                e6 = json.load(f)
            P, Q = decoder_basis(L, e6["basis"])
        else:
            P, Q = decoder_std(L)
        g = greedy_search(L, P, Q, rng)
        s = random_subsets(L, P, Q, rng, trials=200)
        bounded[nm] = {"greedy": g, "random": s}
        print("BND %-12s greedy min(cost-v)=%d (v=%d)  random min=%d (v=%d)"
              % (nm, g["min_cost_minus_v"], g["v"], s["min_cost_minus_v"], s["v"]))
    cert["bounded"] = bounded

    print("== bounded basis pivots (seeded; cost depends on basis) ==")
    pivots = {}
    with open(E6_BEST_PATH, encoding="utf-8") as f:
        e6 = json.load(f)
    for nm, L, b0 in (("E6_pivot", E6(), e6["basis"]), ("D6_pivot", D(6), None),
                      ("B6_pivot", Bn(6), None), ("pm1T4_pivot", pm1_lines(4), None),
                      ("pm1T5_pivot", pm1_lines(5), None)):
        r = basis_pivot_search(L, rng, trials=120, bidx0=b0)
        pivots[nm] = r
        print("PIV %-12s bases=%d min(cost-v)=%d cost=%d" % (nm, r["bases_tried"], r["min_cost_minus_v"], r["cost"]))
    cert["basis_pivots"] = pivots

    cert["control_failures"] = fails
    cert["any_gain_found"] = any(r["gain_count"] for r in ex) or any(
        g["greedy"]["min_cost_minus_v"] < 0 or g["random"]["min_cost_minus_v"] < 0
        for g in bounded.values()) or any(
        r["min_cost_minus_v"] < 0 for r in pivots.values())
    out = os.path.join(HERE, "CERTIFICATE.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(cert, f, indent=1, sort_keys=True)
    print("ANY_GAIN_FOUND:", cert["any_gain_found"])
    print("CERTIFICATE:", out)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
