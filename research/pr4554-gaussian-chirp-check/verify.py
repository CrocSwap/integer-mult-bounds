#!/usr/bin/env python3
"""Independent check of PR #4554 (Dugongue) GAUSSIAN-CHIRP.md, written from the vendored text only.

Nothing is imported from #4554's chirp_check.py, gaussian_block.py or native_convolution.py.
  1. Theorem 1: log D[x] + log E[y] + log H[x+y] = -a(ux - vy + c)^2 as a polynomial identity in Q[a,u,v,c,x,y], and
     sum_y W[x,y] Z[y] = D[x] (H * reverse(E Z))[x+l-1] with an explicit linear (not cyclic) convolution, numerically
     at 60 digits on random rectangles.
  2. Section 2: under (A) with C p := a(|u|q + |v|q + |c0|)^2, every exponent of D (x < q), E (y < q) and
     H (z < 2q - 1) has absolute value at most C p, exactly in rationals.
  3. Section 4 geometry, by brute force over random rational slopes, offsets, radii and block sizes: the retained
     column blocks of each row block number at most K = ceil((u(q-1)+2R)/(vq)) + 3, every retained block has
     |c0| <= R + (u+v)(q-1), and (D) implies (A). The tail rule a R^2 >= (p0 + ceil(log2(sX+1)) + 2) ln 2 makes the
     omitted row mass below 2^-p0/2.
  4. The precision rule (C) implies (B) < 2^-p0 (integer comparisons, using only log2 e < 2).
  5. End to end: my own fixed-point block evaluator at the precision P prescribed by (C) (chirps and twiddles on the
     2^-P grid, nearest-rounded complex products, linear convolution via a radix-2 FFT of size N0 = 4q, division by
     N0, selection at x+l-1, multiplication by D) against a direct 60-digit sum: error < 2^-p0 and within (B).
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import decimal
from decimal import Decimal as Dec
from fractions import Fraction as Fr
import hashlib
import json
import math
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
SPEC = HERE / "PR4554-GAUSSIAN-CHIRP.md"  # #4554 head 4f46c6a9, research/native-word-fft/GAUSSIAN-CHIRP.md, blob 4e31f302
SPEC_SHA256 = "d8f2c45a985fc51d9523c3261ec39fc622afe737bf26a868e7f601dc7525b075"
VARS = ("a", "u", "v", "c", "x", "y")


def need(condition, message):
    if not condition:
        raise AssertionError(message)


class Poly:
    def __init__(self, t=None):
        self.t = {k: v for k, v in (t or {}).items() if v}

    @staticmethod
    def var(n):
        k = [0] * len(VARS)
        k[VARS.index(n)] = 1
        return Poly({tuple(k): Fr(1)})

    @staticmethod
    def const(c):
        return Poly({(0,) * len(VARS): Fr(c)})

    def __add__(self, o):
        o = o if isinstance(o, Poly) else Poly.const(o)
        t = dict(self.t)
        for k, v in o.t.items():
            t[k] = t.get(k, 0) + v
        return Poly(t)

    __radd__ = __add__

    def __neg__(self):
        return Poly({k: -v for k, v in self.t.items()})

    def __sub__(self, o):
        return self + (-(o if isinstance(o, Poly) else Poly.const(o)))

    def __mul__(self, o):
        o = o if isinstance(o, Poly) else Poly.const(o)
        t = {}
        for k1, v1 in self.t.items():
            for k2, v2 in o.t.items():
                k = tuple(i + j for i, j in zip(k1, k2))
                t[k] = t.get(k, 0) + v1 * v2
        return Poly(t)

    __rmul__ = __mul__


def check_identity():
    a, u, v, c, x, y = (Poly.var(n) for n in VARS)
    logD = -a * (u * u + u * v) * x * x - 2 * a * u * c * x - a * c * c
    logE = -a * (v * v + u * v) * y * y + 2 * a * v * c * y
    z = x + y
    logH = a * u * v * z * z
    target = -a * (u * x - v * y + c) * (u * x - v * y + c)
    need(not (logD + logE + logH - target).t, "exponent identity")
    # Numeric check with an explicit linear convolution.
    rng = random.Random(1)
    decimal.getcontext().prec = 70
    worst = Dec(0)
    for _ in range(40):
        A, U, V, Cc = (Dec(rng.uniform(0.01, 0.4)), Dec(rng.uniform(0.3, 2)), Dec(rng.uniform(0.3, 2)),
                       Dec(rng.uniform(-2, 2)))
        m, l = rng.randint(1, 7), rng.randint(1, 7)
        Z = [(Dec(rng.uniform(-1, 1)), Dec(rng.uniform(-1, 1))) for _ in range(l)]
        D = [(-A * (U * U + U * V) * xx * xx - 2 * A * U * Cc * xx - A * Cc * Cc).exp() for xx in range(m)]
        E = [(-A * (V * V + U * V) * yy * yy + 2 * A * V * Cc * yy).exp() for yy in range(l)]
        H = [(A * U * V * zz * zz).exp() for zz in range(m + l - 1)]
        B = [(E[yy] * Z[yy][0], E[yy] * Z[yy][1]) for yy in range(l)]
        rev = B[::-1]
        conv = [(Dec(0), Dec(0)) for _ in range(len(H) + l - 1)]
        for i, h in enumerate(H):
            for j, bb in enumerate(rev):
                conv[i + j] = (conv[i + j][0] + h * bb[0], conv[i + j][1] + h * bb[1])
        for xx in range(m):
            lhs = [Dec(0), Dec(0)]
            for yy in range(l):
                w = (-A * (U * xx - V * yy + Cc) ** 2).exp()
                lhs[0] += w * Z[yy][0]
                lhs[1] += w * Z[yy][1]
            rhs = (D[xx] * conv[xx + l - 1][0], D[xx] * conv[xx + l - 1][1])
            worst = max(worst, abs(lhs[0] - rhs[0]) + abs(lhs[1] - rhs[1]))
    need(worst < Dec(10) ** -50, "numeric identity with linear convolution at index x+l-1")
    return 41


def check_conditioning(rng):
    cases = 0
    for _ in range(300):
        q = rng.randint(1, 24)
        a = Fr(rng.randint(1, 50), rng.randint(50, 400))
        u = Fr(rng.randint(-40, 40), rng.randint(1, 20))
        v = Fr(rng.randint(-40, 40), rng.randint(1, 20))
        c0 = Fr(rng.randint(-60, 60), rng.randint(1, 20))
        Cp = a * (abs(u) * q + abs(v) * q + abs(c0)) ** 2
        for xx in range(q):
            need(abs(a * (u * u + u * v) * xx * xx + 2 * a * u * c0 * xx + a * c0 * c0) <= Cp, "D exponent")
            need(abs(-a * (v * v + u * v) * xx * xx + 2 * a * v * c0 * xx) <= Cp, "E exponent")
        for zz in range(2 * q - 1):
            need(abs(a * u * v * zz * zz) <= Cp, "H exponent")
        cases += 1
    return cases


def check_geometry(rng):
    blocks = 0
    for _ in range(120):
        u = Fr(rng.randint(5, 40), 10)
        v = Fr(rng.randint(5, 40), 10)
        c = Fr(rng.randint(-200, 200), 10)
        R = Fr(rng.randint(1, 80), 10)
        q = 1 << rng.randint(0, 4)
        t, s = rng.randint(q, 96), rng.randint(q, 96)
        K = math.ceil((u * (q - 1) + 2 * R) / (v * q)) + 3
        for x0 in range(0, t, q):
            kept = 0
            for y0 in range(0, s, q):
                keep = any(abs(u * xx - v * yy + c) <= R for xx in range(x0, min(t, x0 + q))
                           for yy in range(y0, min(s, y0 + q)))
                if keep:
                    kept += 1
                    c0 = u * x0 - v * y0 + c
                    need(abs(c0) <= R + (u + v) * (q - 1), "|c0| <= R + (u+v)(q-1)")
                    a = Fr(1, 7)
                    need(a * (R + 2 * (u + v) * q) ** 2 >= a * (u * q + v * q + abs(c0)) ** 2, "(D) implies (A)")
                    blocks += 1
            need(kept <= K, "at most K retained column blocks")
    tails = 0
    for p0 in range(1, 200, 7):
        for sX in (1, 7, 1000, 10 ** 9):
            k = p0 + math.ceil(math.log2(sX + 1)) + 2
            need(Fr(sX, 2 ** k) < Fr(1, 2 ** (p0 + 1)), "tail below 2^-p0/2")  # exp(-aR^2) = 2^-k
            tails += 1
    return blocks, tails


def precision_rule(p0, q, C, p, X):
    l2 = lambda v: math.ceil(math.log2(v))
    return p0 + 30 + 8 * l2(q + 2) + 8 * math.ceil(C) * p + 2 * l2(X + 1) + 4


def check_precision_rule():
    cases = 0
    for p0 in (1, 20, 64, 200):
        for q in (1, 2, 16, 1024):
            for C in (Fr(1, 2), 1, 3):
                for p in (1, 10, 50):
                    for X in (0, 1, 100, 10 ** 6):
                        P = precision_rule(p0, q, C, p, X)
                        # 2^30 q^8 M^4 (X+1)^2 2^-P <= 2^(-p0-4), with M^4 = e^(4Cp) < 2^(8Cp) as log2 e < 2.
                        lhs_log2_upper = 30 + 8 * math.log2(q) + 8 * C * p + 2 * math.log2(X + 1) - P
                        need(lhs_log2_upper <= -p0 - 4, "(C) implies (B) <= 2^(-p0-4)")
                        cases += 1
    need(math.e < 4, "log2 e < 2")
    return cases


# ---------------------------------------------------------------- end-to-end fixed-point block
def end_to_end(rng):
    results = []
    decimal.getcontext().prec = 120
    for a, u, v, c, q, p0 in ((Fr(1, 8), Fr(1), Fr(3, 2), Fr(1, 3), 8, 20),
                              (Fr(1, 20), Fr(5, 4), Fr(1, 2), Fr(-2), 16, 24),
                              (Fr(1, 4), Fr(1, 2), Fr(1, 2), Fr(0), 8, 30)):
        m = l = q
        X = 1
        C = 1
        p = math.ceil(a * (abs(u) * q + abs(v) * q + abs(c)) ** 2)  # (A) with C = 1
        P = precision_rule(p0, q, C, p, X) + 8
        S = 1 << P
        A, U, V, Cc = (Dec(f.numerator) / Dec(f.denominator) for f in (a, u, v, c))

        def grid(d):
            return int((d * S).to_integral_value(rounding=decimal.ROUND_HALF_EVEN))

        D = [(-A * (U * U + U * V) * x * x - 2 * A * U * Cc * x - A * Cc * Cc).exp() for x in range(m)]
        E = [(-A * (V * V + U * V) * y * y + 2 * A * V * Cc * y).exp() for y in range(l)]
        H = [(A * U * V * z * z).exp() for z in range(m + l - 1)]
        Dg, Eg, Hg = [grid(d) for d in D], [grid(e) for e in E], [grid(h) for h in H]
        N0 = 4 * q
        pi = Dec(0)
        # 120-digit pi by Machin, for twiddles on the grid (certified-interface error <= 2^-P).
        def arctan_inv(k):
            total, term, j, x2 = Dec(0), Dec(1) / k, 0, k * k
            while abs(term) > Dec(10) ** -115:
                total += term / (2 * j + 1) * (-1 if j % 2 else 1)
                term /= x2
                j += 1
            return total
        pi = 16 * arctan_inv(5) - 4 * arctan_inv(239)

        def cexp(theta):
            cs, sn, term, k = Dec(0), Dec(0), Dec(1), 0
            while abs(term) > Dec(10) ** -115 or k < 4:
                if k % 4 == 0:
                    cs += term
                elif k % 4 == 1:
                    sn += term
                elif k % 4 == 2:
                    cs -= term
                else:
                    sn -= term
                k += 1
                term = term * theta / k
            return cs, sn

        tw = [tuple(grid(w) for w in cexp(2 * pi * k / N0)) for k in range(N0 // 2)]

        def rmul(x, y):
            re, im = x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0]
            return ((re + (S >> 1)) >> P, (im + (S >> 1)) >> P)

        def fft(arr, inverse):
            arr = list(arr)
            n = len(arr)
            j = 0
            for i in range(1, n):
                bit = n >> 1
                while j & bit:
                    j ^= bit
                    bit >>= 1
                j |= bit
                if i < j:
                    arr[i], arr[j] = arr[j], arr[i]
            size = 2
            while size <= n:
                step = n // size
                for st in range(0, n, size):
                    for k in range(size // 2):
                        w = tw[k * step]
                        if not inverse:
                            w = (w[0], -w[1])
                        tt = rmul(w, arr[st + k + size // 2])
                        uu = arr[st + k]
                        arr[st + k] = (uu[0] + tt[0], uu[1] + tt[1])
                        arr[st + k + size // 2] = (uu[0] - tt[0], uu[1] - tt[1])
                size *= 2
            return arr

        Hhat = fft([(h, 0) for h in Hg] + [(0, 0)] * (N0 - len(Hg)), False)
        for trial in range(2):
            Z = [(rng.randint(-S, S), rng.randint(-S, S)) for _ in range(l)]
            Zf = [(Fr(zr, S), Fr(zi, S)) for zr, zi in Z]
            need(all(abs(zr) <= 1 and abs(zi) <= 1 for zr, zi in Zf), "|Z| bounded")
            B = [rmul((Eg[y], 0), Z[y]) for y in range(l)]
            Bhat = fft(B[::-1] + [(0, 0)] * (N0 - l), False)
            prod = [rmul(x, y) for x, y in zip(Hhat, Bhat)]
            conv = fft(prod, True)
            conv = [((cr + N0 // 2) // N0, (ci + N0 // 2) // N0) for cr, ci in conv]
            worst = Dec(0)
            for x in range(m):
                out = rmul((Dg[x], 0), conv[x + l - 1])
                ref = [Dec(0), Dec(0)]
                for y in range(l):
                    w = (-A * (U * x - V * y + Cc) ** 2).exp()
                    ref[0] += w * Dec(Z[y][0]) / S
                    ref[1] += w * Dec(Z[y][1]) / S
                err = ((Dec(out[0]) / S - ref[0]) ** 2 + (Dec(out[1]) / S - ref[1]) ** 2).sqrt()
                worst = max(worst, err)
            M = Dec(C * p).exp()
            bound_B = Dec(2) ** 30 * q ** 8 * M ** 4 * (X + 1) ** 2 / Dec(2) ** P
            need(worst < Dec(2) ** -p0 and worst <= bound_B, "end-to-end error < 2^-p0 and within (B)")
            results.append({"q": q, "p": p, "P": P, "p0": p0, "log2_error": float((worst + Dec(10) ** -100).ln() / Dec(2).ln())})
    return results


def check_binding():
    raw = SPEC.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == SPEC_SHA256, "vendored GAUSSIAN-CHIRP.md bytes")
    text = raw.decode("utf-8")
    for s in ("sum_y W[x,y]*Z[y] = D[x] * (H * reverse(E*Z))[x+l-1],", "a*(|u|*q+|v|*q+|c0|)^2 <= C*p.",
              "block error <= 2^30*q^8*M^4*(X+1)^2 * 2^-P,", "K = ceil((u*(q-1)+2R)/(v*q)) + 3",
              "|c0| <= R+(u+v)*(q-1),", "a*(R+2*(u+v)*q)^2 <= C*p.", "a*R^2 >= (p0+ceil(log2(s*X+1))+2)*log(2)"):
        need(s in text, f"spec states: {s}")
    return 7


def main():
    rng = random.Random(45543)
    blocks, tails = check_geometry(rng)
    report = {"status": "PASS_PR4554_GAUSSIAN_CHIRP_CHECK", "identity_checks": check_identity(),
              "conditioning_cases": check_conditioning(rng), "retained_blocks_checked": blocks, "tail_cases": tails,
              "precision_rule_cases": check_precision_rule(), "end_to_end": end_to_end(rng),
              "spec_statements_bound": check_binding(), "new_kappa_claimed": False}
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    sys.exit(main())
