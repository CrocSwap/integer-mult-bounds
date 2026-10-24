#!/usr/bin/env python3
"""Independent check of PR #4554 (Dugongue) NATIVE-BANDED-INVERSE.md, written from the vendored text only.

Nothing is imported from #4554's band_solve.py, periodic_solve.py or gaussian_inverse.py.
  A. Band theorem. Exact Gaussian-rational elimination without pivoting on random and adversarial (rho = 1/2)
     complex near-identity band matrices: pivots >= 1/2, row sums <= 3/2, multipliers <= 3, ||A^-1|| <= 2.
     Rounded elimination with explicit rounding (complex error < u, every multiplier, Schur entry and solved
     coordinate rounded once; dot products accumulated exactly): row sums < 2, pivots >= 1/4, multipliers <= 8,
     ||Lhat Uhat - A|| <= 6H^2 u, ||Lhat|| <= 9H, ||Uhat|| <= 2, ||yhat|| <= 8(||b||+u), ||xhat|| <= 4(||b||+19Hu),
     and the final ||xhat - x|| <= 1000 H^4 u (||b||+1), for u from 1/(1000H^2) down to 2^-30.
  B. Periodic Gaussian inverse. The per-summand bound |r(l-i)+beta_i| >= d - 1/2; the tail
     2 sum_{d>h} exp(-pi a^2 d(d-1)) <= 4 exp(-pi a^2 h(h+1)) (log domain); the choice of h against 2^-P/4; then on
     actual instances of N (s > 2h, ||N - I|| <= 1/8): row tails, ||A - I|| <= 1/4, the corner split A = A0 + UV
     with ||A0 - I|| <= 1/4, ||U|| <= 1/4, ||S - I|| <= 1/3, and the Woodbury solve x = y - Xz satisfying A x = b
     exactly in rational arithmetic.
Norms are infinity norms with complex absolute values (floats, for comparisons with stated slack only); all matrix
arithmetic is exact. Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Fr
import hashlib
import json
import math
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
SPEC = HERE / "PR4554-NATIVE-BANDED-INVERSE.md"  # #4554 head 4f46c6a9, research/native-word-fft/NATIVE-BANDED-INVERSE.md, blob 8be8f992
SPEC_SHA256 = "1259b4242ebf6ac7f14bfe72e371afb8dc530b2755d1fd82228d9dc6f01634ba"
ZERO = (Fr(0), Fr(0))
ONE = (Fr(1), Fr(0))


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def cadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def csub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def cmul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def cdiv(a, b):
    den = b[0] * b[0] + b[1] * b[1]
    return ((a[0] * b[0] + a[1] * b[1]) / den, (a[1] * b[0] - a[0] * b[1]) / den)


def cabs(a):
    return math.hypot(float(a[0]), float(a[1]))


def rnd(a, u):
    """Round each part to the grid u/2: complex error at most u*sqrt(2)/4 < u."""
    g = u / 2
    return (Fr(round(a[0] / g)) * g, Fr(round(a[1] / g)) * g)


def norm_mat(M):
    return max(sum(cabs(x) for x in row) for row in M)


def norm_vec(v):
    return max(cabs(x) for x in v)


def matvec(M, x):
    out = []
    for row in M:
        acc = ZERO
        for a, b in zip(row, x):
            if a != ZERO:
                acc = cadd(acc, cmul(a, b))
        out.append(acc)
    return out


def random_band(rng, s, h, rho, adversarial):
    A = [[ZERO] * s for _ in range(s)]
    for i in range(s):
        cols = [j for j in range(max(0, i - h), min(s, i + h + 1))]
        raw = []
        for j in cols:
            if adversarial:
                z = (-1.0, 0.0) if j != i else (-1.0, 0.0)
            else:
                ang = rng.uniform(0, 2 * math.pi)
                z = (math.cos(ang) * rng.random(), math.sin(ang) * rng.random())
            raw.append(z)
        tot = sum(math.hypot(*z) for z in raw)
        scale = rho * 0.999999 / tot if tot else 0
        for j, z in zip(cols, raw):
            e = (Fr(z[0] * scale).limit_denominator(1 << 30), Fr(z[1] * scale).limit_denominator(1 << 30))
            A[i][j] = cadd(ONE, e) if i == j else e
        need(sum(cabs(A[i][j] if j != i else csub(A[i][j], ONE)) for j in cols) <= rho, "||E|| <= rho")
    return A


def exact_elimination(A, h):
    s = len(A)
    M = [row[:] for row in A]
    worst = {"pivot_min": 9.0, "rowsum_max": 0.0, "mult_max": 0.0}
    for k in range(s):
        piv = M[k][k]
        worst["pivot_min"] = min(worst["pivot_min"], cabs(piv))
        for i in range(k + 1, min(s, k + h + 1)):
            if M[i][k] == ZERO:
                continue
            l = cdiv(M[i][k], piv)
            worst["mult_max"] = max(worst["mult_max"], cabs(l))
            for j in range(k + 1, min(s, k + h + 1)):
                M[i][j] = csub(M[i][j], cmul(l, M[k][j]))
            M[i][k] = ZERO
            worst["rowsum_max"] = max(worst["rowsum_max"], sum(cabs(x) for x in M[i][k + 1:]))
    return worst


def exact_solve(A, b):
    s = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for k in range(s):
        for i in range(k + 1, s):
            if M[i][k] != ZERO:
                l = cdiv(M[i][k], M[k][k])
                M[i] = [csub(x, cmul(l, y)) for x, y in zip(M[i], M[k])]
    x = [ZERO] * s
    for i in range(s - 1, -1, -1):
        acc = M[i][s]
        for j in range(i + 1, s):
            acc = csub(acc, cmul(M[i][j], x[j]))
        x[i] = cdiv(acc, M[i][i])
    return x


def rounded_solve(A, b, h, u):
    s = len(A)
    H = h + 1
    U = [row[:] for row in A]
    L = [[ZERO] * s for _ in range(s)]
    st = {"pivot_min": 9.0, "mult_max": 0.0, "rowsum_max": 0.0}
    for k in range(s):
        piv = U[k][k]
        st["pivot_min"] = min(st["pivot_min"], cabs(piv))
        for i in range(k + 1, min(s, k + h + 1)):
            l = rnd(cdiv(U[i][k], piv), u)
            st["mult_max"] = max(st["mult_max"], cabs(l))
            L[i][k] = l
            for j in range(k + 1, min(s, k + h + 1)):
                U[i][j] = rnd(csub(U[i][j], cmul(l, U[k][j])), u)
            U[i][k] = ZERO
            st["rowsum_max"] = max(st["rowsum_max"], sum(cabs(x) for x in U[i][k + 1:]))
    for i in range(s):
        L[i][i] = ONE
    LU = [[ZERO] * s for _ in range(s)]
    for i in range(s):
        for j in range(s):
            acc = ZERO
            for k in range(max(0, i - h, j - h), min(i, j) + 1):
                acc = cadd(acc, cmul(L[i][k], U[k][j]))
            LU[i][j] = acc
    resid = norm_mat([[csub(LU[i][j], A[i][j]) for j in range(s)] for i in range(s)])
    y = [ZERO] * s
    for i in range(s):
        acc = b[i]
        for k in range(max(0, i - h), i):
            acc = csub(acc, cmul(L[i][k], y[k]))
        y[i] = rnd(acc, u)
    x = [ZERO] * s
    for i in range(s - 1, -1, -1):
        acc = y[i]
        for j in range(i + 1, min(s, i + h + 1)):
            acc = csub(acc, cmul(U[i][j], x[j]))
        x[i] = rnd(cdiv(acc, U[i][i]), u)
    st.update(resid=resid, Lnorm=norm_mat(L), Unorm=norm_mat(U), ynorm=norm_vec(y), xnorm=norm_vec(x))
    return x, st


def check_band(rng):
    runs, worst_ratio = 0, 0.0
    for s, h in ((12, 0), (16, 1), (20, 2), (24, 3), (18, 4)):
        H = h + 1
        for adversarial in (False, True):
            for trial in range(3 if not adversarial else 1):
                A = random_band(rng, s, h, Fr(1, 2), adversarial)
                ex = exact_elimination(A, h)
                need(ex["pivot_min"] >= 0.5 - 1e-12 and ex["rowsum_max"] <= 1.5 + 1e-12 and ex["mult_max"] <= 3 + 1e-12,
                     "exact pivots, row sums, multipliers")
                b = [(Fr(rng.randint(-9, 9), 4), Fr(rng.randint(-9, 9), 4)) for _ in range(s)]
                x = exact_solve(A, b)
                need(norm_vec(x) <= 2 * norm_vec(b) + 1e-12, "||A^-1|| <= 2 on b")
                for u in (Fr(1, 1000 * H * H), Fr(1, 2 ** 14), Fr(1, 2 ** 30)):
                    xh, st = rounded_solve(A, b, h, u)
                    uf, nb = float(u), norm_vec(b)
                    need(st["rowsum_max"] < 2 and st["pivot_min"] >= 0.25 and st["mult_max"] <= 8, "rounded invariants")
                    need(st["resid"] <= 6 * H * H * uf and st["Lnorm"] <= 9 * H and st["Unorm"] <= 2, "factor bounds")
                    need(st["ynorm"] <= 8 * (nb + uf) and st["xnorm"] <= 4 * (nb + 19 * H * uf), "solve growth")
                    err = norm_vec([csub(p, q) for p, q in zip(xh, x)])
                    bound = 1000 * H ** 4 * uf * (nb + 1)
                    need(err <= bound, "final error bound")
                    worst_ratio = max(worst_ratio, err / bound)
                    runs += 1
    return runs, worst_ratio


def check_gaussian_tail():
    rng = random.Random(7)
    for _ in range(2000):  # |r(l-i) + beta_i| >= d - 1/2 for r > 1, |beta| <= 1/2
        r = 1 + rng.random() * 3
        d = rng.randint(1, 20) * rng.choice((-1, 1))
        beta = rng.uniform(-0.5, 0.5)
        need(abs(r * d + beta) >= abs(d) - 0.5, "per-summand distance")
    tails = 0
    for a10 in range(20, 61, 5):
        a = a10 / 10
        for h in range(1, 9):
            logs = [-math.pi * a * a * d * (d - 1) for d in range(h + 1, h + 60)]
            m = max(logs)
            lhs = math.log(2) + m + math.log(sum(math.exp(v - m) for v in logs))
            rhs = math.log(4) - math.pi * a * a * h * (h + 1)
            need(lhs <= rhs and math.exp(-2 * math.pi * a * a * (h + 1)) < 0.5, "tail bound")
            tails += 1
        for P in range(1, 4097, 7):
            h = math.ceil(math.sqrt((P * math.log(2) + math.log(16)) / (math.pi * a * a))) + 1
            need(math.pi * a * a * h * (h + 1) > P * math.log(2) + math.log(16), "h choice gives tail < 2^-P/4")
            tails += 1
    return tails


def gaussian_N(s, t, a):
    r = t / s
    beta = [r * i - math.floor(r * i + 0.5) for i in range(s)]
    N = [[0.0] * s for _ in range(s)]
    for i in range(s):
        for l in range(i - 14, i + 15):
            j = l % s
            N[i][j] += math.exp(-math.pi * a * a * (r * (l - i) + beta[i]) ** 2 + math.pi * a * a * beta[j] ** 2)
    return N, beta


def check_periodic(rng):
    instances = 0
    for s, t, a in ((24, 37, 2.0), (30, 47, 2.0), (40, 61, 2.5), (33, 70, 2.0), (28, 45, 3.0), (32, 38, 2.0), (40, 50, 2.0)):
        N, beta = gaussian_N(s, t, a)
        nI = max(sum(abs(N[i][j] - (1 if i == j else 0)) for j in range(s)) for i in range(s))
        need(nI <= 0.125, "instance in the stated regime ||N - I|| <= 1/8")
        h = 2
        need(s > 2 * h, "s > 2h")
        r = t / s
        A = [[ZERO] * s for _ in range(s)]
        tail_max = 0.0
        for i in range(s):
            full = sum(N[i])
            kept = 0.0
            for l in range(i - h, i + h + 1):
                j = l % s
                v = math.exp(-math.pi * a * a * (r * (l - i) + beta[i]) ** 2 + math.pi * a * a * beta[j] ** 2)
                A[i][j] = (Fr(v), Fr(0))
                kept += v
            tail_max = max(tail_max, full - kept)
        need(tail_max <= 4 * math.exp(-math.pi * a * a * h * (h + 1)) + 1e-15, "row tail")
        need(norm_mat([[csub(A[i][j], ONE if i == j else ZERO) for j in range(s)] for i in range(s)]) <= 0.25, "||A-I||")
        # Corner split: A0 keeps |i-j| <= h; the corner part has columns only in the first and last h coordinates.
        A0 = [[A[i][j] if abs(i - j) <= h else ZERO for j in range(s)] for i in range(s)]
        corner_cols = list(range(h)) + list(range(s - h, s))
        Ucols = [[A[i][j] if abs(i - j) > h else ZERO for j in corner_cols] for i in range(s)]
        for i in range(s):
            for j in range(s):
                if abs(i - j) > h and A[i][j] != ZERO:
                    need(j in corner_cols, "corner entries lie in the first/last h columns")
        need(norm_mat([[csub(A0[i][j], ONE if i == j else ZERO) for j in range(s)] for i in range(s)]) <= 0.25, "||A0-I||")
        need(norm_mat(Ucols) <= 0.25, "||U|| <= 1/4")
        b = [(Fr(rng.randint(-5, 5)), Fr(rng.randint(-5, 5))) for _ in range(s)]
        y = exact_solve(A0, b)
        Xcols = [exact_solve(A0, [Ucols[i][c] for i in range(s)]) for c in range(2 * h)]
        X = [[Xcols[c][i] for c in range(2 * h)] for i in range(s)]
        VX = [X[j] for j in corner_cols]
        S = [[cadd(VX[p][q], ONE if p == q else ZERO) for q in range(2 * h)] for p in range(2 * h)]
        need(norm_mat([[VX[p][q] for q in range(2 * h)] for p in range(2 * h)]) <= 1 / 3, "||S - I|| <= 1/3")
        z = exact_solve(S, [y[j] for j in corner_cols])
        Xz = matvec(X, z)
        x = [csub(y[i], Xz[i]) for i in range(s)]
        need(matvec(A, x) == b, "Woodbury solve: A x = b exactly")
        instances += 1
    return instances


def check_binding():
    raw = SPEC.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == SPEC_SHA256, "vendored NATIVE-BANDED-INVERSE.md bytes")
    text = raw.decode("utf-8")
    for s in ("1000 H^4 u (||b||_infinity+1),", "||Lhat Uhat-A||_infinity <= 6 H^2 u.", "||e_f+Lhat e_b|| <=19H u,",
              "||xhat|| <=4(||b||+19H u).", "<=4 exp[-pi alpha^2 h(h+1)].",
              "h = ceil(sqrt((P ln 2+ln 16)/(pi alpha^2)))+1", "S=I+V X", "return x=y-Xz"):
        need(s in text, f"spec states: {s}")
    return 8


def main():
    rng = random.Random(4554)
    runs, ratio = check_band(rng)
    report = {"status": "PASS_PR4554_BANDED_INVERSE_CHECK", "rounded_band_solves": runs,
              "worst_error_over_bound": f"{ratio:.3e}", "gaussian_tail_and_h_checks": check_gaussian_tail(),
              "periodic_woodbury_instances": check_periodic(rng), "spec_statements_bound": check_binding(),
              "new_kappa_claimed": False}
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    sys.exit(main())
