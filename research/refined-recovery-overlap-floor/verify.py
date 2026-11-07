"""Exact checks for the overlap floor on refined recovery chains (stdlib only).

Prints PASS_REFINED_RECOVERY_OVERLAP_FLOOR on success.
"""
import hashlib
import json
import math
import pathlib
from fractions import Fraction

HERE = pathlib.Path(__file__).resolve().parent
FIXTURE = HERE.parent / "precision-state-frontier" / "FIXTURE.json"
FIXTURE_SHA = "2ca4d7550fcae5b757ec500f87aee1d2ef9f64b59e4abe2bda93319521304af8"
RESULT = HERE / "RESULT.json"
N, MODES = 112, 8
F = (13**8 + 14 * 13**4 + 1) // 16
DIM_CAP = 104  # #6660 Theorem (c): every N_j lies in one space of dimension <= 104


def fail(msg):
    raise SystemExit("FAIL: " + msg)


def check(cond, msg):
    if not cond:
        fail(msg)


def wt(u):
    return bin(u).count("1")


def load_rows():
    raw = FIXTURE.read_bytes()
    check(hashlib.sha256(raw).hexdigest() == FIXTURE_SHA, "fixture hash")
    cols = json.loads(raw)["mode_columns"]
    check(len(cols) == MODES and all(len(c) == N for c in cols), "fixture shape")
    return [tuple(cols[j][i] for j in range(MODES)) for i in range(N)]


def code_from_rows(rows):
    """C = {q in F2^8 : M q = 0 mod 2}, as 8-bit masks."""
    code = [q for q in range(256)
            if all(sum(r[k] for k in range(MODES) if q >> k & 1) % 2 == 0 for r in rows)]
    check(len(code) == 16, "|C| = 16")
    check(all(wt(a & b) % 2 == 0 for a in code for b in code), "C self-orthogonal (so self-dual)")
    check(sorted(wt(c) for c in code) == [0] + [4] * 14 + [8], "C is the [8,4,4] code")
    return code


def coset_ratios(code):
    """rho(a) = S(a)/F on the 16 cosets, S(a) = sum_{u in a} 7^(8-wt) 6^wt."""
    w = lambda u: 7 ** (8 - wt(u)) * 6 ** wt(u)
    reps = sorted({min(u ^ c for c in code) for u in range(256)})
    check(len(reps) == 16, "16 cosets")
    S = {a: sum(w(a ^ c) for c in code) for a in reps}
    check(S[0] == F, "S(C) = W_C(7,6) = F")
    rho = {a: Fraction(S[a], F) for a in reps}
    odd = {S[a] for a in reps if wt(a) % 2}
    even = {S[a] for a in reps if a and wt(a) % 2 == 0}
    check(odd == {50983170} and even == {50979600}, "two nonzero coset sums")
    return reps, rho, Fraction(50983170, F), Fraction(50979600, F)


def quotient_subspaces(code, reps):
    """All subspaces of F2^8/C, as frozensets of coset representatives."""
    rep = lambda u: min(u ^ c for c in code)
    subs = {frozenset([0])}
    frontier = list(subs)
    while frontier:
        nxt = []
        for s in frontier:
            for a in reps:
                if a in s:
                    continue
                t = frozenset(s | {rep(x ^ a) for x in s})
                if t not in subs:
                    subs.add(t)
                    nxt.append(t)
        frontier = nxt
    check(sorted(len(s) for s in subs).count(8) == 15 and len(subs) == 67, "67 subspaces of F2^4")
    return subs


def mu(d, subs, rho):
    """min over linear l: F2^d -> F2^8/C of prod_{x != 0} rho(l x).

    A rank-k map with image I hits each point of I exactly 2^(d-k) times on
    F2^d, so the product is (prod_{a in I, a != 0} rho(a))^(2^(d-k)).
    """
    best = None
    for s in subs:
        k = len(s).bit_length() - 1
        if k > d:
            continue
        p = Fraction(1)
        for a in s:
            if a:
                p *= rho[a]
        val = p ** (2 ** (d - k))
        if best is None or val < best[0]:
            best = (val, k, s)
    return best


def certified_floor(t, d, m, places=6):
    """Largest L = 1 + (2^d - 1) * y with y = floor(10^places * m^(t/(2^d-1)))/10^places.

    Returned exactly: ((L - 1)/(2^d - 1))^(2^d - 1) <= m^t is checked.
    """
    n = 2 ** d - 1
    target = m ** t
    lo, hi = 0, 10 ** places
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if Fraction(mid, 10 ** places) ** n <= target:
            lo = mid
        else:
            hi = mid - 1
    y = Fraction(lo, 10 ** places)
    check(y ** n <= target, "certified root")
    return 1 + n * y


def zero_fiber_ratio(maps, rho, d):
    """sum_{x in F2^d} prod_j rho(l_j x) for maps given as images of the basis."""
    total = Fraction(0)
    for x in range(2 ** d):
        p = Fraction(1)
        for basis_imgs, rep in maps:
            a = 0
            for i in range(d):
                if x >> i & 1:
                    a ^= basis_imgs[i]
            p *= rho[rep(a)]
        total += p
    return total


def main():
    rows = load_rows()
    code = code_from_rows(rows)
    reps, rho, r1, r2 = coset_ratios(code)
    rep = lambda u: min(u ^ c for c in code)
    even = frozenset(a for a in reps if wt(a) % 2 == 0)
    check(len(even) == 8, "even cosets form E (3-dimensional)")
    subs = quotient_subspaces(code, reps)
    check(even in subs, "E is a subspace")
    check(r2 < r1 < 1, "0 < rho2 < rho1 < 1")
    check(r2 ** 7 < r1 ** 8, "rho2^7 < rho1^8: a map onto E beats an injective map")

    # mu_d: the minimizer is the rank-3 map onto E for every d >= 3
    mus = {}
    for d in range(1, 9):
        val, k, s = mu(d, subs, rho)
        mus[d] = val
        if d >= 3:
            check(k == 3 and s == even and val == r2 ** (2 ** d - 2 ** (d - 3)), "mu_%d closed form" % d)
    check(mus[1] == r2 and mus[2] == r2 ** 3, "mu_1, mu_2")

    # Theorem at t = 27, d = 4
    L27 = certified_floor(27, 4, mus[4])
    check(L27 == Fraction(157898, 10000) or L27 > Fraction(15789, 1000), "t=27 floor > 15.789")
    check(L27 > 15, "t=27 floor exceeds 15")

    # Near-attainment of the d = 4 bound by an abstract configuration (not frames):
    # 27 rank-3 maps onto E with kernels distributed 2,2,...,2,1,1,1 over the 15 lines.
    # Coordinates: F2^8/C basis b0..b3 with E spanned by three even cosets.
    ev = [a for a in sorted(even) if a]
    e_basis = []
    for a in ev:
        span = {0}
        for b in e_basis:
            span |= {s ^ b for s in span}
        span = {rep(s) for s in span}
        if a not in span:
            e_basis.append(a)
    check(len(e_basis) == 3, "basis of E")
    maps = []
    lines = list(range(1, 16))
    kernels = lines * 2
    kernels = kernels[:27]
    for kvec in kernels:
        # choose l: F2^4 -> E with kernel spanned by kvec: send a basis of a complement to e_basis
            # build basis {kvec, c1, c2, c3} of F2^4 and images {0, e1, e2, e3}
        basis = [kvec]
        for v in (1, 2, 4, 8):
            span = {0}
            for b in basis:
                span |= {s ^ b for s in span}
            if v not in span and len(basis) < 4:
                basis.append(v)
        imgs_on_basis = [0] + e_basis
        # express standard basis vectors in terms of `basis`
        std_imgs = []
        for v in (1, 2, 4, 8):
            for coeffs in range(16):
                s = 0
                img = 0
                for i in range(4):
                    if coeffs >> i & 1:
                        s ^= basis[i]
                        img ^= imgs_on_basis[i]
                if s == v:
                    std_imgs.append(rep(img))
                    break
        maps.append((std_imgs, rep))
    attained = zero_fiber_ratio(maps, rho, 4)
    check(attained == 1 + 12 * r2 ** 25 + 3 * r2 ** 26, "abstract configuration value")
    check(attained > L27 and attained - L27 < Fraction(1, 10 ** 4), "d=4 AM-GM bound nearly attained")

    # Table for t = 27..40: best certified d, floor, bits; identity-frame upper bound A_t
    table = []
    for t in range(27, 41):
        best = None
        for d in range(1, min(4 * t - DIM_CAP, 8) + 1):
            L = certified_floor(t, d, mus[d] if d in mus else r2 ** (2 ** d - 2 ** (d - 3)))
            if best is None or L > best[1]:
                best = (d, L)
        d, L = best
        lower = F ** t * L
        A_t = (13 ** (8 * t) + 14 * 13 ** (4 * t) + 1) // 16
        check(lower < A_t, "floor below identity-frame fiber A_%d" % t)
        bits_lo = math.ceil(math.log2(lower.numerator) - math.log2(lower.denominator) - 1e-9)
        check(Fraction(2) ** (bits_lo - 1) < lower, "certified bit floor t=%d" % t)
        table.append({
            "t": t, "d": d, "floor_over_F_t": str(L), "floor_over_F_t_float": float(L),
            "min_tag_bits_at_least": bits_lo,
            "direct_sum_bits_t_log2F": math.ceil(t * math.log2(F)),
            "identity_frame_bits_log2_A_t": math.ceil(math.log2(A_t)),
        })
    check(table[0]["d"] == 4, "t=27 uses d=4")

    result = {
        "rho1": str(r1), "rho2": str(r2),
        "mu_d": {str(d): str(mus[d]) for d in (1, 2, 3, 4)},
        "t27_floor_over_F27": str(L27),
        "t27_abstract_attained_over_F27": float(attained),
        "table": table,
    }
    if RESULT.exists():
        check(json.loads(RESULT.read_text()) == result, "RESULT.json matches recomputation")
    else:
        RESULT.write_text(json.dumps(result, indent=1) + "\n")

    # controls: a wrong ratio or a too-large floor must fail
    check(not (r1 ** 8 < r2 ** 7), "control: ordering is strict the other way")
    check(not (((L27 + Fraction(15, 10 ** 6) - 1) / 15) ** 15 <= mus[4] ** 27), "control: floor is the certified maximum at 6 places")
    print("PASS_REFINED_RECOVERY_OVERLAP_FLOOR")


if __name__ == "__main__":
    main()
