"""Exact checks for explicit near-optimal refined-recovery frames at depths 28-30.

Prints PASS_REFINED_RECOVERY_EXPLICIT_FRAMES on success (stdlib only).
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
CAP = 104                                        # #6660 Theorem (c)
EPS_STAR = Fraction(1, 13) / (Fraction(23, 12) ** 8 - 1)  # #6848 threshold


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


def weight(u):
    return 7 ** (8 - wt(u)) * 6 ** wt(u)


def coset_data(code):
    rep = lambda u: min(u ^ c for c in code)
    reps = sorted({rep(u) for u in range(256)})
    S = {a: sum(weight(a ^ c) for c in code) for a in reps}
    check(S[0] == F, "S(C) = F")
    check({S[a] for a in reps if wt(a) % 2} == {50983170}, "odd coset sum")
    check({S[a] for a in reps if a and wt(a) % 2 == 0} == {50979600}, "even coset sum")
    for h in code:  # Fourier transform of the [-6,6] box weight
        check(sum(weight(u) * (-1) ** wt(h & u) for u in range(256)) == 13 ** (8 - wt(h)),
              "hat w(h) = 13^(8 - wt h)")
    return reps, S


def rank2(vecs):
    basis = []
    for v in vecs:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return len(basis)


EIDX = (0, 1, 2, 4)  # rows of E, as in PR6327 / PR6660
RPRIME_DIM = 100


def integer_kernel(rows):
    """Integer kernel of M^T restricted to rows outside E; ranks of its mod-2 reduction
    alone and together with the columns of M mod 2."""
    free = [i for i in range(N) if i not in EIDX]
    A = [[rows[i][k] for i in free] for k in range(MODES)]
    n = len(free)
    U = [[int(i == j) for j in range(n)] for i in range(n)]

    def colop(c1, c2, f):
        for r in A:
            r[c1] -= f * r[c2]
        for r in U:
            r[c1] -= f * r[c2]

    def swap(c1, c2):
        for r in A + U:
            r[c1], r[c2] = r[c2], r[c1]

    piv = 0
    for k in range(MODES):
        while True:
            nz = [c for c in range(piv, n) if A[k][c] != 0]
            if len(nz) <= 1:
                break
            c0 = min(nz, key=lambda c: abs(A[k][c]))
            for c in nz:
                if c != c0:
                    colop(c, c0, A[k][c] // A[k][c0])
        nz = [c for c in range(piv, n) if A[k][c] != 0]
        if nz:
            swap(piv, nz[0])
            piv += 1
    check(piv == MODES, "M^T has rank 8 on the free rows")
    kern = []
    for c in range(MODES, n):
        v = [0] * N
        for i, x in zip(free, (U[r][c] for r in range(n))):
            v[i] = x
        check(all(sum(rows[i][k] * v[i] for i in range(N)) == 0 for k in range(MODES)), "M^T v = 0")
        check(all(v[i] == 0 for i in EIDX), "E v = 0")
        kern.append(v)
    mcols = [sum((rows[i][k] & 1) << i for i in range(N)) for k in range(MODES)]
    return kern, mcols


FRAMES = {t: HERE / ("FRAMES%d.json" % t) for t in (28, 29, 30)}
THETA27 = None  # set in main from #6828's closed form
SIG0 = Fraction(16 * F, 13 ** 8)
SIGE = Fraction(16 * 50979600, 13 ** 8)
SIGO = Fraction(16 * 50983170, 13 ** 8)


def F2_kernel(cols):
    """Basis (as bitmasks over column indices) of {x : sum x_i cols_i = 0 over F2}."""
    piv, ker = {}, []
    for i, c in enumerate(cols):
        v, comb = c, 1 << i
        while v:
            p = v.bit_length() - 1
            if p in piv:
                v ^= piv[p][0]
                comb ^= piv[p][1]
            else:
                piv[p] = (v, comb)
                break
        if not v:
            ker.append(comb)
    return ker


def build_frames(rows, kern, spec):
    """Integer V_j (4 columns each) from kernel-basis subsets; V_1 = 0."""
    V = []
    for masks in spec:
        cols = []
        for msk in masks:
            v = [0] * N
            for b, kv in enumerate(kern):
                if msk >> b & 1:
                    v = [x + y for x, y in zip(v, kv)]
            cols.append(v)
        V.append(cols)
    for cols in V:
        for v in cols:
            check(all(sum(rows[i][k] * v[i] for i in range(N)) == 0 for k in range(MODES)), "M^T V = 0")
            check(all(v[i] == 0 for i in EIDX), "E V = 0")
    return V


def stage_columns(rows, V, code):
    """Columns of phi_j = W_j M mod 2 on a basis of Q, read directly from W_j M = M + V_j E M."""
    basis = []
    for u in range(1, 256):  # greedy basis of F2^8 / C
        if rank2([b for b in basis] + list(code[1:]) + [u]) > rank2(basis + list(code[1:])):
            basis.append(u)
        if len(basis) == 4:
            break
    EM = [[rows[e][k] for k in range(MODES)] for e in EIDX]
    out = []
    for cols in V:
        for u in basis:
            Mu = [sum(rows[i][k] for k in range(MODES) if u >> k & 1) for i in range(N)]
            EMu = [sum(EM[r][k] for k in range(MODES) if u >> k & 1) for r in range(4)]
            WMu = [Mu[i] + sum(cols[r][i] * EMu[r] for r in range(4)) for i in range(N)]
            out.append(sum((x & 1) << i for i, x in enumerate(WMu)))
    return basis, out


def exact_S(rows, code, V, t):
    basis, cols = stage_columns(rows, V, code)
    check(len(cols) == 4 * t, "4 columns per stage")
    check(rank2(cols) == CAP, "rank 104 (dimension cap attained)")
    ker = F2_kernel(cols)
    check(len(ker) == 4 * t - CAP, "dim D = 4t - 104")
    cls = {}
    for a in range(16):
        u = 0
        for b in range(4):
            if a >> b & 1:
                u ^= basis[b]
        cls[a] = 0 if u in code else (1 if wt(u) % 2 == 0 else 2)
    elems = [0]
    for g in ker:
        elems += [e ^ g for e in elems]
    comp = {}
    for x in elems:
        z = e = o = 0
        for j in range(t):
            c = cls[(x >> (4 * j)) & 15]
            if c == 0:
                z += 1
            elif c == 1:
                e += 1
            else:
                o += 1
        comp[(z, e, o)] = comp.get((z, e, o), 0) + 1
    total = sum(n * SIG0 ** z * SIGE ** e * SIGO ** o for (z, e, o), n in comp.items())
    S = total * Fraction(2 ** CAP, 2 ** (4 * t)) - 1
    zero_fiber = F ** t * sum(n * Fraction(50979600, F) ** e * Fraction(50983170, F) ** o
                              for (z, e, o), n in comp.items())
    check(zero_fiber == Fraction(13 ** (8 * t), 2 ** CAP) * (1 + S), "Poisson identity on the frames")
    return S, comp


def main():
    rows = load_rows()
    code = code_from_rows(rows)
    coset_data(code)
    check(SIG0 + 8 * SIGO + 7 * SIGE == 16, "sigma averages to 1")
    kern, mcols = integer_kernel(rows)
    check(len(kern) == RPRIME_DIM, "100 kernel vectors")
    rho2 = Fraction(50979600, F)
    theta = (1 + 12 * rho2 ** 25 + 3 * rho2 ** 26) * F ** 27 * 2 ** CAP / 13 ** 216 - 1
    q = SIG0 / 16
    out = []
    for t, path in FRAMES.items():
        spec = json.loads(path.read_text())
        check(spec["t"] == t and len(spec["stage_masks"]) == t and spec["stage_masks"][0] == [0] * 4,
              "frame file shape, W_1 = I")
        V = build_frames(rows, kern, spec["stage_masks"])
        S, comp = exact_S(rows, code, V, t)
        check(0 < S < EPS_STAR, "below the #6848 threshold at t=%d" % t)
        E_t = (2 ** CAP - 16) * q ** t + 14 * Fraction(1, 13 ** (4 * t)) + Fraction(1, 13 ** (8 * t))
        prev = theta if t == 28 else E_t
        check(S * 10 < prev, "explicit S beats the previous bound tenfold at t=%d" % t)
        out.append({"t": t, "S": float(S), "previous_bound": float(prev),
                    "previous_source": "#6850 theta" if t == 28 else "#6851 E_t (existential)",
                    "improvement_factor": round(float(prev / S), 1),
                    "dim_D": 4 * t - CAP, "compositions": len(comp)})
    result = {"frames": out}
    text = json.dumps(result, indent=1) + "\n"
    if __debug__ and not RESULT.exists():
        RESULT.write_text(text)
    check(RESULT.read_text() == text, "RESULT.json matches recomputation")
    for row in out:
        print("t=%d  S=%.4e  (previous %.3e, x%.1f)" % (row["t"], row["S"], row["previous_bound"],
                                                        row["improvement_factor"]))
    print("PASS_REFINED_RECOVERY_EXPLICIT_FRAMES")


if __name__ == "__main__":
    main()
