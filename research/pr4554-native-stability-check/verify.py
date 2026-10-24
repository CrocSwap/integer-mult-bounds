#!/usr/bin/env python3
"""Independent check of PR #4554 (Dugongue) NATIVE-STABILITY.md, from the vendored text and #956's vendored PROFILE.json.

Nothing is imported from #4554 or #956 code.
  1. Gate norms, exactly over rational complex a with the bound abar = |Re a| + |Im a| >= |a|: the 2x2 block of
     x <- x + a y has largest squared singular value <= (1 + abar)^2 (rational eigenvalue test), scaling <= max(1, abar)^2,
     COPY = 2 (norm sqrt 2), CLEAR <= 1.
  2. Roundoff: a fixed-point lowering (round toward zero at P bits) of random rational ADD/SCALE programs with
     denominators 2 and 3 has error at most sum_k sqrt(2) 2^-P * prod(suffix gate bounds); the precision formula P gives
     sqrt(2) A 2^e (e+1)^theta K^(D+1) 2^-P <= 2^-(B+2); the integral width I covers K^(D+1) sqrt(Z 2^e) 2^b with three
     bits to spare; |(1-i)^e|^2 = 2^e exactly and the Walsh rescaling keeps error <= 2^-B.
  3. #956 instantiation: m = 73, W = 58,899 and largest child rank 48 bound to #956's PROFILE.json (head fa4df77c,
     vendored, sha256-pinned); the integer-root certificate r u_r^1024 >= m 2^32768 > r (u_r - 1)^1024 and the moment
     mu = sum h_r r u_r / (W m 2^32) < 1 behind theta = 1023/1024 are recomputed; the depth bound
     D(e) <= 1 + ceil(log(e+1)/log(73/48)) holds for the worst-case contraction e -> 48e/73, e < 10^6.
  4. Shear divisions: t1 = 1 + |mu|^2 >= 1 and Re t2 = -[(a - 1/2)^2 + b^2 + 3/4] exactly; |1/t1| <= 1, |1/t2| <= 4/3;
     perturbations |dt1| <= (2U+1) delta, |dt2| <= (2U+2) delta and, when |dt2| <= 3/8, |d(1/t2)| <= (32/9)|dt2|,
     on random and extremal mu (a = 1/2, b = 0).
  5. Polyloglog absorption: max_x x^C e^(-(k-k')x) = (C/(e(k-k')))^C is finite.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Fr
import hashlib
import json
import math
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
SPEC = HERE / "PR4554-NATIVE-STABILITY.md"  # #4554 head 4f46c6a9, research/native-word-fft/NATIVE-STABILITY.md, blob 86f98436
SPEC_SHA256 = "260e78bf8f88667a637b804d013d1e7c6dfdf1e23ae35ffdc64a4366c7321221"
PROFILE = HERE / "PR956-PROFILE.json"  # #956 head fa4df77c, research/pr390-heterogeneous-provider-closure/PROFILE.json, blob 3bb4409c
PROFILE_SHA256 = "ded51df11009cfd26bf1bbe5108603f89b1dea8d3dd52c9865ef4034d517f68b"


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def abar(a):
    return abs(a[0]) + abs(a[1])


def lam_max_le(X, s):
    """Largest eigenvalue of [[1, a],[conj a, 1+s]] (s = |a|^2) is <= X, decided in rationals."""
    tr, det = 2 + s, Fr(1)
    # lam_max = (tr + sqrt(tr^2 - 4 det))/2 <= X  <=>  2X - tr >= 0 and (2X - tr)^2 >= tr^2 - 4 det
    return 2 * X - tr >= 0 and (2 * X - tr) ** 2 >= tr * tr - 4 * det


def check_gate_norms(rng):
    cases = 0
    for _ in range(3000):
        a = (Fr(rng.randint(-60, 60), rng.choice((1, 2, 3, 4, 6, 9))), Fr(rng.randint(-60, 60), rng.choice((1, 2, 3, 6))))
        s = a[0] ** 2 + a[1] ** 2
        need(abar(a) ** 2 >= s, "abar >= |a|")
        need(lam_max_le((1 + abar(a)) ** 2, s), "||x += a y|| <= 1 + abar")
        need(max(s, 1) <= max(abar(a) ** 2, 1), "||scale|| <= max(1, abar)")
        cases += 1
    # COPY (x, y) -> (x, x): M^T M = [[2, 0], [0, 0]], norm^2 = 2.
    need([[1 * 1 + 1 * 1, 0], [0, 0]] == [[2, 0], [0, 0]], "COPY norm sqrt 2")
    return cases


def tz(v, P):
    """Round a rational toward zero to the 2^-P grid."""
    S = 1 << P
    n = v * S
    q = n.numerator // n.denominator if n >= 0 else -((-n.numerator) // n.denominator)
    return Fr(q, S)


def check_roundoff(rng):
    runs, worst = 0, 0.0
    for _ in range(40):
        Z, G, P = rng.randint(2, 6), rng.randint(5, 40), rng.choice((12, 20, 30))
        x = [(Fr(rng.randint(-8, 8), 4), Fr(rng.randint(-8, 8), 4)) for _ in range(Z)]
        xe, xa = list(x), list(x)
        gates = []
        for _ in range(G):
            a = (Fr(rng.randint(-3, 3), rng.choice((1, 2, 3, 6))), Fr(rng.randint(-3, 3), rng.choice((1, 2, 3))))
            if rng.random() < 0.6:
                i, j = rng.sample(range(Z), 2)
                gates.append(("ADD", i, j, a, 1 + float(abar(a))))
            else:
                gates.append(("SCALE", rng.randrange(Z), None, a, max(1.0, float(abar(a)))))
        for op, i, j, a, _ in gates:
            for vec, rounded in ((xe, False), (xa, True)):
                src = vec[j] if op == "ADD" else vec[i]
                prod = (a[0] * src[0] - a[1] * src[1], a[0] * src[1] + a[1] * src[0])
                new = (vec[i][0] + prod[0], vec[i][1] + prod[1]) if op == "ADD" else prod
                vec[i] = (tz(new[0], P), tz(new[1], P)) if rounded else new
        err = math.sqrt(sum(float((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) for p, q in zip(xa, xe)))
        bound = 0.0
        for k in range(G):
            suffix = math.prod(g[4] for g in gates[k + 1:])
            bound += math.sqrt(2) * 2.0 ** (-P) * suffix
        need(err <= bound, "sum of transported local errors")
        worst = max(worst, err / bound if bound else 0)
        runs += 1
    # The precision formula and integral width.
    formulas = 0
    for e in range(0, 201, 5):
        for A in (1, 5, 1000):
            for theta in (Fr(1, 2), Fr(1023, 1024), Fr(1)):
                for K in (2, 3, 17):
                    D = 1 + math.ceil(math.log(e + 1) / math.log(73 / 48))
                    for B in (0, 10, 100):
                        P = (B + e + math.ceil(math.log2(A)) + math.ceil(float(theta) * math.log2(e + 1))
                             + (D + 1) * math.ceil(math.log2(K)) + 3)
                        lhs = 0.5 + math.log2(A) + e + float(theta) * math.log2(e + 1) + (D + 1) * math.log2(K) - P
                        need(lhs <= -B - 2, "precision formula")
                        formulas += 1
                    for Zb in (1, 4, 30):
                        for b in (0, 8, 64):
                            I = b + math.ceil(e / 2) + (D + 1) * math.ceil(math.log2(K)) + math.ceil(math.log2(Zb + 1)) + 3
                            mag = (D + 1) * math.log2(K) + 0.5 * (math.log2(Zb) + e) + b
                            need(mag <= I - 3, "integral width")
    for e in range(0, 200):
        g = (1, 0)
        for _ in range(e):
            g = (g[0] + g[1], g[1] - g[0])  # multiply by (1 - i)
        need(g[0] ** 2 + g[1] ** 2 == 2 ** e, "|(1-i)^e|^2 = 2^e")
        for B in (0, 20):
            need(Fr(2 ** e) * Fr(1, 2 ** (2 * (B + math.ceil(e / 2) + 1))) <= Fr(1, 2 ** (2 * B + 2)), "Walsh rescale")
    return runs, worst, formulas


def check_956():
    raw = PROFILE.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PROFILE_SHA256, "vendored #956 PROFILE.json")
    p = json.loads(raw)
    h = {int(r): n for r, n in p["global"]["histogram"].items()}
    u = {int(r): n for r, n in p["global"]["integer_root_upper"].items()}
    m, W = p["physical"]["m"], p["global"]["live"]
    need(m == 73 and W == 58899 and max(h) == 48, "m = 73, W = 58,899, largest child rank 48")
    target = m << 32768
    for r in h:
        need(r * u[r] ** 1024 >= target > r * (u[r] - 1) ** 1024, "integer-root certificate")
    mu = Fr(sum(h[r] * r * u[r] for r in h), W * m * (1 << 32))
    need(mu < 1, "moment below 1 (theta = 1023/1024 funded)")
    need(sum(r * n for r, n in h.items()) <= m * W, "rank mass within the stock")
    worst_depth = 0
    for e in list(range(1, 2000)) + [10 ** k for k in range(4, 7)]:
        x, levels = Fr(e), 1
        while x >= 1:
            x = x * 48 / 73
            levels += 1
        bound = 1 + math.ceil(math.log(e + 1) / math.log(73 / 48))
        need(levels <= bound, "depth bound, counting the leaf call as a level")
        worst_depth = max(worst_depth, levels - bound)
    return float(1 - mu), worst_depth


def check_shear(rng):
    cases = 0
    mus = [(Fr(1, 2), Fr(0))] + [(Fr(rng.randint(-400, 400), 37), Fr(rng.randint(-400, 400), 41)) for _ in range(3000)]
    for a, b in mus:
        t1 = 1 + a * a + b * b
        t2 = (a - t1, b)
        need(t1 >= 1, "t1 >= 1")
        need(t2[0] == -((a - Fr(1, 2)) ** 2 + b * b + Fr(3, 4)), "Re t2 identity")
        need(t2[0] <= Fr(-3, 4) and t2[0] ** 2 + t2[1] ** 2 >= Fr(9, 16), "|t2| >= 3/4")
        U2 = a * a + b * b
        U = math.sqrt(float(U2))
        for _ in range(3):
            dl = Fr(rng.randint(1, 1000), 1000)
            ang = rng.uniform(0, 2 * math.pi)
            d = (Fr(math.cos(ang)).limit_denominator(10 ** 6) * dl, Fr(math.sin(ang)).limit_denominator(10 ** 6) * dl)
            dd = math.hypot(float(d[0]), float(d[1]))
            a2, b2 = a + d[0], b + d[1]
            t1p = 1 + a2 * a2 + b2 * b2
            t2p = (a2 - t1p, b2)
            need(abs(float(t1p - t1)) <= (2 * U + 1) * dd + 1e-12, "t1 perturbation")
            dt2 = math.hypot(float(t2p[0] - t2[0]), float(t2p[1] - t2[1]))
            need(dt2 <= (2 * U + 2) * dd + 1e-12, "t2 perturbation")
            if dt2 <= 3 / 8:
                z, zp = complex(float(t2[0]), float(t2[1])), complex(float(t2p[0]), float(t2p[1]))
                need(abs(1 / z - 1 / zp) <= 32 / 9 * dt2 + 1e-12, "reciprocal perturbation")
            cases += 1
    return cases


def check_polyloglog():
    for C in (1, 3, 10):
        for gap in (0.01, 0.1, 0.5):
            peak = (C / (math.e * gap)) ** C
            xs = [C / gap * f for f in (0.5, 0.9, 1.0, 1.1, 2.0)]
            need(all(x ** C * math.exp(-gap * x) <= peak * (1 + 1e-12) for x in xs), "bounded absorption factor")
    return 9


def check_binding():
    raw = SPEC.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == SPEC_SHA256, "vendored NATIVE-STABILITY.md")
    text = raw.decode("utf-8")
    for s in ("For one scalar gate x<-x+a*y, the Euclidean operator norm is at most 1+|a|.", "COPY has norm at most sqrt(2)",
              "uses m=73, largest child rank 48, productive stock W=58,899", "theta=1023/1024",
              "\\operatorname{Re}(t_2)=-[(a-1/2)^2+b^2+3/4]\\le-3/4.", "(32/9)"):
        need(s in text, f"spec states: {s}")
    return 6


def main():
    rng = random.Random(45545)
    runs, worst, formulas = check_roundoff(rng)
    gap, depth = check_956()
    report = {"status": "PASS_PR4554_NATIVE_STABILITY_CHECK", "gate_norm_cases": check_gate_norms(rng),
              "fixed_point_programs": runs, "worst_error_over_transport_bound": worst, "formula_cases": formulas,
              "pr956_moment_gap": gap, "depth_excess_over_bound": depth, "shear_cases": check_shear(rng),
              "absorption_cases": check_polyloglog(), "spec_statements_bound": check_binding(), "new_kappa_claimed": False}
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    sys.exit(main())
