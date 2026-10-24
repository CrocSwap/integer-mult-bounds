#!/usr/bin/env python3
"""Independent check of PR #4554 (Dugongue) ROOTS-RECOVERY.md, written from the vendored text only.

Nothing is imported from #4554's root_seed.py or recover.py.
  1. Root seed. My own implementation of the stated construction (P = 8(p+16), S = 2^P, K = 128(p+1); Machin pi by
     floored alternating terms while q^(2j+1) <= S; t = floor(2A/D); K-term fixed-point complex Taylor with truncation
     toward zero; nearest rounding to p bits). For small p every term is compared with the exact rational Taylor term
     at theta = t/S: per-term error <= the recurrence E_k <= (8/k)E_(k-1) + 1/S < e^8/S, summed error <= 4096K/S;
     |A/S - pi| <= 20(P+2)/S and |t/S - 2pi/D| <= [40(P+2)+1]/S against a separate AGM pi; the final coordinate error
     < 2^-p against exact algebraic values (D = 1, 2, 3, 4, 6, 8, 12, by integer square comparisons) and against a
     separate high-precision decimal reference for other D up to 2^40+87; observed magnitudes stay below 2^(2P+20).
  2. Lemmas, exactly: Machin's tangent identity (tan 2a = 5/12, tan 4a = 120/119, tan(4a - b) = 1); e < 11/4 from the
     stated partial sum and geometric tail; (11/4)^8 < 4096; the Taylor tail 2*8^(K+1)/(K+1)! <= 2^(-K/2-3) <= 32/S
     and [40(P+2)+1+4096K+32]*2^(p+1) < S for every p <= 4096.
  3. Recovery: Garner CRT with Fermat inverses (unsigned and signed representatives) and the linear carry invariant,
     including the bound carry <= min(a,b)(beta-1), on random and extremal digit arrays.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import decimal
from fractions import Fraction as Fr
import hashlib
import json
import math
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
SPEC = HERE / "PR4554-ROOTS-RECOVERY.md"  # #4554 head 4f46c6a9, research/native-word-fft/ROOTS-RECOVERY.md, blob 5791526c
SPEC_SHA256 = "5e115c3ded1734dbcb119c889755a13ce9e9357598ec20a3eb1d3cdd727638f4"


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def trunc_div(a, b):
    """Integer division truncating toward zero (b > 0)."""
    return a // b if a >= 0 else -((-a) // b)


class Track:
    def __init__(self, P):
        self.limit = 1 << (2 * P + 20)
        self.peak = 0

    def __call__(self, v):
        self.peak = max(self.peak, abs(v))
        need(abs(v) < self.limit, "magnitude below 2^(2P+20)")
        return v


def machin(P, T):
    S = 1 << P

    def arctan_inv(q):
        total, j, power = 0, 0, q
        while power <= S:
            term = T(S // T((2 * j + 1) * power))
            total += -term if j % 2 else term
            power = T(power * q * q)
            j += 1
        need(j <= P + 1, "at most P+1 terms")
        return total

    return 16 * arctan_inv(5) - 4 * arctan_inv(239)


def seed(D, p, exact_terms=False):
    P = 8 * (p + 16)
    S = 1 << P
    K = 128 * (p + 1)
    T = Track(P)
    A = machin(P, T)
    t = T(2 * A // D)
    need(0 <= t <= 8 * S, "0 <= t <= 8S")
    a, b = S, 0
    sx, sy = S, 0
    errs = []
    if exact_terms:
        theta = Fr(t, S)
        ex = (Fr(1), Fr(0))
    for k in range(1, K + 1):
        a, b = T(trunc_div(T(-b * t), S * k)), T(trunc_div(T(a * t), S * k))
        sx, sy = T(sx + a), T(sy + b)
        if exact_terms:
            ex = (-ex[1] * theta / k, ex[0] * theta / k)
            errs.append(max(abs(Fr(a, S) - ex[0]), abs(Fr(b, S) - ex[1])))
    shift = P - p
    x = (sx + (1 << (shift - 1))) >> shift  # nearest at p bits
    y = (sy + (1 << (shift - 1))) >> shift
    return x, y, A, t, S, K, errs, T.peak


def agm_pi(prec):
    decimal.getcontext().prec = prec + 10
    D = decimal.Decimal
    a, b, t, pw = D(1), D(1) / D(2).sqrt(), D(1) / D(4), D(1)
    for _ in range(int(math.log2(prec)) + 4):
        an = (a + b) / 2
        b = (a * b).sqrt()
        t -= pw * (a - an) ** 2
        a = an
        pw *= 2
    return (a + b) ** 2 / (4 * t)


def ref_cos_sin(D, digits):
    decimal.getcontext().prec = digits + 20
    pi = agm_pi(digits + 20)
    x = 2 * pi / D
    while x > pi:
        x -= 2 * pi
    c, s, term, k = decimal.Decimal(0), decimal.Decimal(0), decimal.Decimal(1), 0
    eps = decimal.Decimal(10) ** (-(digits + 15))
    while abs(term) > eps or k < 4:
        if k % 4 == 0:
            c += term
        elif k % 4 == 1:
            s += term
        elif k % 4 == 2:
            c -= term
        else:
            s -= term
        k += 1
        term = term * x / k
    return c, s, pi


def within_sqrt(x, p, num, den):
    """|x/2^p - sqrt(num/den)| < 2^-p for x >= 1, via integer comparisons: (x-1)^2 den < num 4^p < (x+1)^2 den."""
    return (x - 1) ** 2 * den < num * 4 ** p < (x + 1) ** 2 * den


def check_seeds():
    out = {"exact_term_runs": 0, "algebraic_checks": 0, "reference_checks": 0, "worst_term_err_times_S": 0.0,
           "worst_sum_err_over_4096K": 0.0, "peak_bits_over_2P20": 0.0}
    for p in (1, 2, 4):
        for D in (1, 3, 7, 16):
            x, y, A, t, S, K, errs, peak = seed(D, p, exact_terms=True)
            P = 8 * (p + 16)
            E = Fr(0)
            for k, e in enumerate(errs, start=1):
                E = Fr(8, k) * E + Fr(1, S)
                need(e <= E and e < Fr(4096, S), "per-term rounding recurrence")
            out["worst_term_err_times_S"] = max(out["worst_term_err_times_S"], float(max(errs) * S))
            need(sum(errs) <= Fr(4096 * K, S), "summed rounding error")
            out["worst_sum_err_over_4096K"] = max(out["worst_sum_err_over_4096K"], float(sum(errs) * S / (4096 * K)))
            out["peak_bits_over_2P20"] = max(out["peak_bits_over_2P20"], peak.bit_length() / (2 * P + 20))
            out["exact_term_runs"] += 1
    # Machin and angle bounds against a separate AGM pi.
    for p in (1, 8, 32, 64):
        P = 8 * (p + 16)
        S = 1 << P
        pi = agm_pi(P // 3 + 60)
        A = machin(P, Track(P))
        need(abs(decimal.Decimal(A) / decimal.Decimal(S) - pi) <= decimal.Decimal(20 * (P + 2)) / S, "Machin bound")
        for D in (1, 3, 1000, (1 << 40) + 87):
            t = 2 * A // D
            need(abs(decimal.Decimal(t) / S - 2 * pi / D) <= decimal.Decimal(40 * (P + 2) + 1) / S, "angle bound")
    # Final error: exact algebraic values.
    for p in (1, 2, 3, 8, 16, 33, 64, 128):
        P2 = 1 << p
        for D, (cx, cy) in {1: ((1, 1), (0, 1)), 2: ((-1, 1), (0, 1)), 4: ((0, 1), (1, 1)), 8: ("r2", "r2"),
                            3: ((-1, 2), "r3"), 6: ((1, 2), "r3"), 12: ("r3", (1, 2))}.items():
            x, y = seed(D, p)[:2]
            for v, c in ((x, cx), (y, cy)):
                if c == "r2":
                    need(within_sqrt(v, p, 1, 2), "sqrt(2)/2 within 2^-p")
                elif c == "r3":
                    need(within_sqrt(v, p, 3, 4), "sqrt(3)/2 within 2^-p")
                else:
                    need(abs(Fr(v, P2) - Fr(*c)) < Fr(1, P2), "rational value within 2^-p")
                out["algebraic_checks"] += 1
    # Final error: decimal reference for general orders.
    for p in (1, 5, 17, 40, 64, 128):
        for D in (5, 7, 10, 97, 1 << 20, (1 << 40) + 87):
            x, y = seed(D, p)[:2]
            c, s, _ = ref_cos_sin(D, int(p * 0.302) + 30)
            P2 = decimal.Decimal(1 << p)
            need(abs(decimal.Decimal(x) / P2 - c) < 1 / P2 and abs(decimal.Decimal(y) / P2 - s) < 1 / P2, "final < 2^-p")
            out["reference_checks"] += 1
    return out


def check_lemmas():
    def tan_add(u, v):
        return (u + v) / (1 - u * v)

    a = Fr(1, 5)
    t2 = tan_add(a, a)
    t4 = tan_add(t2, t2)
    need(t2 == Fr(5, 12) and t4 == Fr(120, 119), "tan 2a, tan 4a")
    need((t4 - Fr(1, 239)) / (1 + t4 * Fr(1, 239)) == 1, "tan(4a - b) = 1")
    partial = sum(Fr(1, math.factorial(k)) for k in range(4))  # through 1/3!
    tail = Fr(1, 24) * Fr(1, 1 - Fr(1, 5))  # (1/24) sum_j 5^-j bounds sum_{k>=4} 1/k!
    need(sum(Fr(1, math.factorial(k)) for k in range(4, 40)) < tail, "tail bound for e")
    need(partial + tail < Fr(11, 4) and Fr(11, 4) ** 8 < 4096, "e < 11/4, (11/4)^8 < 4096")
    checked = 0
    for p in range(1, 4097):
        P, K = 8 * (p + 16), 128 * (p + 1)
        need(8 * 2 < K + 2, "tail ratio 8/(K+2) < 1/2")
        need(K // 2 + 1 <= K + 1 - 127, "last K/2+1 factors are at least 128")
        need(K // 2 + 3 >= P - 5, "2^(-K/2-3) <= 32/S")
        need((40 * (P + 2) + 1 + 4096 * K + 32) << (p + 1) < 1 << P, "numerator * 2^(p+1) < S")
        checked += 1
    for K in (256, 384, 512):  # the factorial tail itself, exactly
        need(Fr(2 * 8 ** (K + 1), math.factorial(K + 1)) <= Fr(1, 2 ** (K // 2 + 3)), "factorial tail")
    return checked


def check_recovery(rng):
    primes = [1000003, 1000033, 1000037, 1000039]
    for q in primes:
        need(all(q % d for d in range(2, int(q ** 0.5) + 1)), "trial-division primality")
    coeffs = 0
    for trial in range(300):
        h = rng.choice((1, 2, 4, 8, 16))
        beta = 1 << h
        a, b = rng.randint(1, 40), rng.randint(1, 40)
        extremal = trial % 5 == 0
        u = [beta - 1 if extremal else rng.randrange(beta) for _ in range(a)]
        v = [beta - 1 if extremal else rng.randrange(beta) for _ in range(b)]
        c = [0] * (a + b - 1)
        for i, x in enumerate(u):
            for k, y in enumerate(v):
                c[i + k] += x * y
        C = min(a, b) * (beta - 1) ** 2
        need(all(0 <= x <= C for x in c), "coefficient range")
        mods = []
        Q = 1
        for q in primes:
            mods.append(q)
            Q *= q
            if Q > 2 * C:
                break
        need(Q > 2 * C, "enough moduli")
        for j, cj in enumerate(c):
            for signed in (False, True):
                val = -cj if signed and j % 2 else cj
                x, M = 0, 1
                for q in mods:
                    r = val % q
                    inv = pow(M % q, q - 2, q)
                    tt = ((r + q - (x % q)) % q) * inv % q
                    x, M = x + M * tt, M * q
                    need(0 <= x < M, "Garner invariant")
                rec = x - M if signed and x > M // 2 else x
                need(rec == val, "CRT recovery")
                coeffs += 1
        # Carry propagation.
        cc = c + [0]
        carry, digits = 0, []
        for j in range(len(cc)):
            tt = cc[j] + carry
            need(tt <= min(a, b) * beta * (beta - 1), "t bound")
            digits.append(tt & (beta - 1))
            carry = tt >> h
            need(carry <= min(a, b) * (beta - 1), "carry bound")
            need(sum(d << (h * i) for i, d in enumerate(digits)) + (carry << (h * (j + 1)))
                 == sum(x << (h * i) for i, x in enumerate(cc[:j + 1])), "carry invariant")
        need(carry == 0, "final carry")
        U = sum(x << (h * i) for i, x in enumerate(u))
        V = sum(x << (h * i) for i, x in enumerate(v))
        need(sum(d << (h * i) for i, d in enumerate(digits)) == U * V, "exact product")
    return coeffs


def check_binding():
    raw = SPEC.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == SPEC_SHA256, "vendored ROOTS-RECOVERY.md bytes")
    text = raw.decode("utf-8")
    for s in ("Take P=8(p+16), S=2^P, K=128(p+1).", "|A/S - pi| <= 20(P+2)/S.", "|t/S - 2pi/D| <= [40(P+2)+1]/S.",
              "E_k <= (8/k) E_(k-1)+1/S", "E_internal <= [40(P+2)+1+4096K+32]/S.", "x <- x + M*t,   M <- M*p_i.",
              "t <= min(a,b) beta(beta-1),"):
        need(s in text, f"spec states: {s}")
    return 7


def main():
    rng = random.Random(45542)
    report = {"status": "PASS_PR4554_ROOTS_RECOVERY_CHECK", "seeds": check_seeds(), "lemma_p_values": check_lemmas(),
              "crt_coefficients_recovered": check_recovery(rng), "spec_statements_bound": check_binding(),
              "new_kappa_claimed": False}
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    sys.exit(main())
