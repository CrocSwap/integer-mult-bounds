#!/usr/bin/env python3
"""Independent check of PR #4554 (Dugongue) PHASE-TABLES.md section 2 (finite-precision lowering of linear
straight-line programs) and section 4 (perturbed shear denominators), from the vendored text only.

  1. Induction steps, exactly in rationals for every depth h <= 200 and C0 in a grid: with C = max(2, C0),
     2 N^b C^(h-1) <= N^b C^h and C0 N^b C^(h-1) <= N^b C^h; with X = C0 + 3 and the closed form
     B_h = eps (V+1) X^(h+1): 2 B_(h-1) + eps <= B_h (add) and (C0+1) B_(h-1) + eps V + eps <= B_h (scale).
  2. Random layered programs (ADD, SUB, SCALE by prepared complex scalars |c| <= C0 whose prepared values carry an
     error <= eps; inputs |x| <= N^b; depth <= a log2(N+2)) run in exact rationals and in a rounded copy (prepared
     scalars perturbed, every data gate rounded toward zero to 2^-P): at every node the error is <= eps(V+1)(C0+3)^(h+1)
     and the exact value is <= N^b C^h, where h is the node's data depth.
  3. Instantiation on radix-2 FFT DAGs (depth 2 log2 N, C0 = 1, inputs <= beta): the theorem's bound and the sharper
     FFT-ERROR.md chain (checked in #4557) both dominate the observed rounded-twiddle FFT error.
  4. The bilinear product extension |a_hat b_hat - a b| <= |a| E_b + |b| E_a + E_a E_b (+ one rounding), and section 4:
     approximate shear denominators within 1/4 keep |t1| >= 3/4 and |t2| >= 1/2.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Fr
import cmath
import hashlib
import json
import math
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
SPEC = HERE / "PR4554-PHASE-TABLES.md"  # #4554 head 4f46c6a9, research/native-word-fft/PHASE-TABLES.md, blob 2dab8f3e
SPEC_SHA256 = "9a5844176b67f81ad8468b77d0049935d05517a80e80586edfa8401f400917f8"


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def check_induction():
    cases = 0
    for C0 in (Fr(1, 2), Fr(1), Fr(3, 2), Fr(2), Fr(7, 3), Fr(10)):
        C = max(Fr(2), C0)
        X = C0 + 3
        for h in range(1, 201):
            need(2 * C ** (h - 1) <= C ** h and C0 * C ** (h - 1) <= C ** h, "magnitude induction")
            # With eps and V scaled out (eps = 1, V >= 0 arbitrary): check for V = 0 and a large V.
            for V in (Fr(0), Fr(10 ** 6)):
                Bh, Bp = (V + 1) * X ** (h + 1), (V + 1) * X ** h
                need(2 * Bp + 1 <= Bh, "add-error induction")
                need((C0 + 1) * Bp + V + 1 <= Bh, "scale-error induction")
            cases += 1
    return cases


def tz(v, P):
    S = 1 << P
    n = v * S
    q = n.numerator // n.denominator if n >= 0 else -((-n.numerator) // n.denominator)
    return Fr(q, S)


def cabs(z):
    return math.hypot(float(z[0]), float(z[1]))


def cadd(x, y, sign=1):
    return (x[0] + sign * y[0], x[1] + sign * y[1])


def cmul(x, y):
    return (x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def check_random_programs(rng):
    runs, worst = 0, 0.0
    for _ in range(60):
        N = rng.choice((4, 8, 16, 32))
        b = rng.choice((0, 1))
        C0 = rng.choice((Fr(1, 2), Fr(1), Fr(2)))
        a = rng.choice((1, 2))
        depth = int(a * math.log2(N + 2))
        P = rng.choice((16, 24, 32))
        eps = Fr(1, 1 << (P - 1))  # covers the complex rounding of both parts (sqrt(2)/2^P < 2^(1-P))
        width = rng.randint(2, 5)
        nb = Fr(N) ** b
        layer = [(Fr(rng.randint(-int(nb) * 8, int(nb) * 8), 8), Fr(rng.randint(-int(nb) * 8, int(nb) * 8), 8))
                 for _ in range(width)]
        layer = [(max(min(x, nb / 2), -nb / 2), max(min(y, nb / 2), -nb / 2)) for x, y in layer]
        exact = list(layer)
        approx = list(layer)
        h_of = [0] * width
        C = max(Fr(2), C0)
        V = nb * C ** depth
        for d in range(1, depth + 1):
            new_e, new_a, new_h = [], [], []
            for _ in range(width):
                op = rng.choice(("ADD", "SUB", "SCALE"))
                i, j = rng.randrange(width), rng.randrange(width)
                if op == "SCALE":
                    ang = rng.uniform(0, 2 * math.pi)
                    r = float(C0) * rng.random()
                    c = (Fr(r * math.cos(ang)).limit_denominator(1 << 20), Fr(r * math.sin(ang)).limit_denominator(1 << 20))
                    if cabs(c) > float(C0):
                        c = (c[0] / 2, c[1] / 2)
                    ch = (c[0] + Fr(rng.randint(-1000, 1000), 1000) * eps / 2, c[1] + Fr(rng.randint(-1000, 1000), 1000) * eps / 2)
                    ve, va = cmul(c, exact[i]), cmul(ch, approx[i])
                else:
                    sign = 1 if op == "ADD" else -1
                    ve, va = cadd(exact[i], exact[j], sign), cadd(approx[i], approx[j], sign)
                va = (tz(va[0], P), tz(va[1], P))
                new_e.append(ve)
                new_a.append(va)
                new_h.append(d)
            exact, approx, h_of = new_e, new_a, new_h
            for k in range(width):
                bound = float(eps * (V + 1)) * float(C0 + 3) ** (h_of[k] + 1)
                err = math.hypot(float(approx[k][0] - exact[k][0]), float(approx[k][1] - exact[k][1]))
                need(err <= bound, "error <= eps (V+1)(C0+3)^(h+1)")
                need(cabs(exact[k]) <= float(nb * C ** h_of[k]) * (1 + 1e-12), "magnitude <= N^b C^h")
                worst = max(worst, err / bound)
        runs += 1
    return runs, worst


def check_fft(rng):
    rows = []
    for logN in (3, 5, 7, 9):
        N = 1 << logN
        beta = 15
        P = 30
        eps = 2.0 ** (1 - P)
        x = [complex(rng.randint(0, beta), 0) for _ in range(N)]

        def fft(a, perturb):
            a = list(a)
            j = 0
            for i in range(1, N):
                bit = N >> 1
                while j & bit:
                    j ^= bit
                    bit >>= 1
                j |= bit
                if i < j:
                    a[i], a[j] = a[j], a[i]
            m = 2
            while m <= N:
                for st in range(0, N, m):
                    for k in range(m // 2):
                        w = cmath.exp(-2j * math.pi * k / m)
                        if perturb:
                            w += complex(rng.uniform(-1, 1), rng.uniform(-1, 1)) * eps / 2
                            q = 2.0 ** P
                            t = w * a[st + k + m // 2]
                            t = complex(math.trunc(t.real * q) / q, math.trunc(t.imag * q) / q)
                        else:
                            t = w * a[st + k + m // 2]
                        u = a[st + k]
                        a[st + k], a[st + k + m // 2] = u + t, u - t
                m *= 2
            return a

        err = max(abs(p - q) for p, q in zip(fft(x, True), fft(x, False)))
        depth = 2 * logN
        V = beta * 2 ** depth  # N^b C^h with C = 2 for unit twiddles, inputs <= beta
        theorem = eps * (V + 1) * 4 ** (depth + 1)
        chain = 36 * N ** 3 * beta * 2.0 ** (-P) * 4  # FFT-ERROR (1) at S = 2^(P-2) (coordinate error eps/2)
        need(err <= chain <= theorem, "observed <= FFT-ERROR chain <= section-2 theorem")
        rows.append({"N": N, "observed": err, "fft_error_chain": chain, "section2_theorem": theorem})
    return rows


def check_bilinear_and_shear(rng):
    cases = 0
    for _ in range(2000):
        a = complex(rng.uniform(-50, 50), rng.uniform(-50, 50))
        b = complex(rng.uniform(-50, 50), rng.uniform(-50, 50))
        Ea, Eb = rng.uniform(0, 1), rng.uniform(0, 1)
        ah = a + Ea * cmath.exp(2j * math.pi * rng.random())
        bh = b + Eb * cmath.exp(2j * math.pi * rng.random())
        need(abs(ah * bh - a * b) <= abs(a) * Eb + abs(b) * Ea + Ea * Eb + 1e-9, "bilinear extension")
        mu = complex(rng.uniform(-20, 20), rng.uniform(-20, 20))
        t1 = 1 + abs(mu) ** 2
        t2 = mu - t1
        for _ in range(3):
            e1 = 0.25 * rng.random() * cmath.exp(2j * math.pi * rng.random())
            e2 = 0.25 * rng.random() * cmath.exp(2j * math.pi * rng.random())
            need(abs(t1 + e1) >= 0.75 - 1e-12 and abs(t2 + e2) >= 0.5 - 1e-12, "perturbed shear denominators")
        cases += 1
    return cases


def check_binding():
    raw = SPEC.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == SPEC_SHA256, "vendored PHASE-TABLES.md")
    text = raw.decode("utf-8")
    for s in ("E_new<=E_left+E_right+epsilon.", "E_new <= (C0+1)*E_input + epsilon*V + epsilon.",
              "E_at_depth_h <= epsilon*(V+1)*(C0+3)^(h+1).", "|a|*E_b+|b|*E_a+E_a*E_b",
              "absolute values at least 3/4 and 1/2."):
        need(s in text, f"spec states: {s}")
    return 5


def main():
    rng = random.Random(45546)
    runs, worst = check_random_programs(rng)
    report = {"status": "PASS_PR4554_LOWERING_CHECK", "induction_cases": check_induction(),
              "random_programs": runs, "worst_error_over_bound": worst, "fft_instances": check_fft(rng),
              "bilinear_and_shear_cases": check_bilinear_and_shear(rng), "spec_statements_bound": check_binding(),
              "new_kappa_claimed": False}
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    sys.exit(main())
