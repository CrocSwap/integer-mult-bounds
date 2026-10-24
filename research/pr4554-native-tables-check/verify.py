#!/usr/bin/env python3
"""Independent check of PR #4554 (Dugongue) paid native tables: PHASE-TABLES.md section 1 and NATIVE-EXP-TABLE.md.

Written from the vendored texts only; nothing is imported from #4554's phase_tables.py or exp_table.py.
  1. Root-power tables. z_j by t rounded squarings per level, T_j[a] = round(T_j[a-1] z_j), queries multiply the d
     digit-selected entries starting from exact 1; nearest rounding to the 1/Q grid (half away from zero). Seeds are
     all four floor/ceil grid neighbours of exp(2 pi i/D), so each coordinate error is < 1/Q. For Q >= 64(E+d), every
     query error is compared with 16(E+d)/Q against a high-precision decimal reference (AGM pi), and coordinates,
     products and sums are checked against 2Q, 4Q^2, 8Q^2 (2p+8 signed bits). The leaf/node count 2E+d and the
     inequality (1+eta)^(2E+d) - 1 <= 16(E+d)/Q are checked exactly.
  2. Exp table, with concrete (c, C, eta) = (1, 2, 1/4), odd d = 13 (eta(d+1) = 3.5 > c+eta+2 = 3.25) and c0 = 6:
     h = 2^-floor(eta log2(n+2)), J = ceil(C log2(n+2)/h), S = p + ceil(log2(J+1)) + c0. The base qhat is the exact
     rational Taylor polynomial rounded down to S bits; 0 <= qhat <= e^-h and e^-h - qhat <= C_d 2^-S are checked, and
     every table entry satisfies 0 <= e^(-jh) - Ehat_j <= j(C_d+1)2^-S. Queries x in [0, C log2(n+2)] (edges, multiples
     of h, random) have error < 2^-p. The cutoff above which h^(d+1)/(d+1)! <= 2^-S holds is located exactly.
     The reciprocal corollary for exp(+x) is checked with the stated budgets.
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
SPECS = {"PR4554-PHASE-TABLES.md": "9a5844176b67f81ad8468b77d0049935d05517a80e80586edfa8401f400917f8", "PR4554-NATIVE-EXP-TABLE.md": "c9be6814a81e0bfe6b041f1a259a32369f7c030ca22eaa5c71c15911c888c6ff"}  # #4554 head 4f46c6a9; blobs 2dab8f3e (phase), ee6e734c (exp)


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def agm_pi(digits):
    decimal.getcontext().prec = digits + 10
    a, b, t, pw = Dec(1), Dec(1) / Dec(2).sqrt(), Dec(1) / Dec(4), Dec(1)
    for _ in range(int(math.log2(digits)) + 4):
        an = (a + b) / 2
        b = (a * b).sqrt()
        t -= pw * (a - an) ** 2
        a = an
        pw *= 2
    return (a + b) ** 2 / (4 * t)


def dec_cos_sin(x, digits):
    decimal.getcontext().prec = digits + 10
    c, s, term, k = Dec(0), Dec(0), Dec(1), 0
    eps = Dec(10) ** (-(digits + 8))
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
    return c, s


def dec_exp(x, digits):
    decimal.getcontext().prec = digits + 10
    return Dec(x).exp() if not isinstance(x, Fr) else (Dec(x.numerator) / Dec(x.denominator)).exp()


# ---------------------------------------------------------------- 1. root-power tables
class Mag:
    def __init__(self, Q, p):
        self.Q, self.p = Q, p
        self.coord = self.prod = self.sum = 0

    def mul(self, a, b):
        Q = self.Q
        pr = (a[0] * b[0], a[1] * b[1], a[0] * b[1], a[1] * b[0])
        self.prod = max(self.prod, *(abs(v) for v in pr))
        re, im = pr[0] - pr[1], pr[2] + pr[3]
        self.sum = max(self.sum, abs(re), abs(im))
        need(max(abs(re), abs(im)) < 1 << (2 * self.p + 7), "signed sums fit 2p+8 bits")

        def rnd(v):
            return (v + Q // 2) >> self.p if v >= 0 else -((-v + Q // 2) >> self.p)

        out = (rnd(re), rnd(im))
        self.coord = max(self.coord, abs(out[0]), abs(out[1]))
        return out


def phase_case(D, t, extra_bits, seed_choice, ref_digits):
    R = 1 << t
    d = 1
    while R ** d < D:
        d += 1
    E = R ** d
    p = (64 * (E + d)).bit_length() + extra_bits
    Q = 1 << p
    need(Q >= 64 * (E + d), "Q >= 64(E+d)")
    pi = agm_pi(ref_digits)
    decimal.getcontext().prec = ref_digits + 10
    c, s = dec_cos_sin(2 * pi / D, ref_digits)
    fx, fy = int((c * Q).to_integral_value(rounding=decimal.ROUND_FLOOR)), int((s * Q).to_integral_value(rounding=decimal.ROUND_FLOOR))
    z0 = (fx + (seed_choice & 1), fy + (seed_choice >> 1 & 1))
    need(abs(Dec(z0[0]) / Q - c) < Dec(1) / Q and abs(Dec(z0[1]) / Q - s) < Dec(1) / Q, "seed coordinate error < 1/Q")
    M = Mag(Q, p)
    zj = z0
    tables = []
    for j in range(d):
        if j:
            for _ in range(t):
                zj = M.mul(zj, zj)
        row = [(Q, 0)]
        for a in range(1, R):
            row.append(M.mul(row[-1], zj))
        tables.append(row)
    bound = Dec(16 * (E + d)) / Q
    worst = Dec(0)
    es = range(D) if D <= 4096 else sorted(set([0, 1, D - 1] + [random.Random(D + t).randrange(D) for _ in range(300)]))
    for e in es:
        acc, rest = (Q, 0), e
        for j in range(d):
            acc = M.mul(acc, tables[j][rest & (R - 1)])
            rest >>= t
        ce, se = dec_cos_sin(2 * pi * e / D, ref_digits) if e else (Dec(1), Dec(0))
        err = ((Dec(acc[0]) / Q - ce) ** 2 + (Dec(acc[1]) / Q - se) ** 2).sqrt()
        need(err <= bound, "query error <= 16(E+d)/Q")
        worst = max(worst, err / bound)
    need(M.coord <= 2 * Q and M.prod <= 4 * Q * Q and M.sum <= 8 * Q * Q, "magnitude envelope")
    # The multiplicative argument: at most 2E+d factors of (1+eta), eta = 2/Q.
    eta = Fr(2, Q)
    x = (2 * E + d) * eta
    need(x <= Fr(1, 16) and 2 * x <= Fr(16 * (E + d), Q), "(1+eta)^(2E+d)-1 <= 2(2E+d)eta <= 16(E+d)/Q")
    return len(es), float(worst)


def check_phase():
    queries, worst = 0, 0.0
    for D, t in ((12, 1), (97, 2), (1000, 3), (4096, 4), (65537, 4), (1 << 20, 4)):
        for choice in range(4):
            q, w = phase_case(D, t, 0, choice, 40)
            queries += q
            worst = max(worst, w)
    # Leaf/node count by literal unfolding of the computation tree.
    for t in (1, 2, 3):
        R = 1 << t
        for d in (1, 2, 3):
            leaves = {}
            nodes = {}
            for j in range(d):
                zl, zn = R ** j, R ** j - 1  # t squarings per level: R^j leaves, R^j - 1 products
                for a in range(R):
                    leaves[(j, a)] = a * zl
                    nodes[(j, a)] = a * (zn + 1)  # a products by z_j (the first one by the exact 1)
            E = R ** d
            for e in range(E):
                digits = [(e >> (t * j)) & (R - 1) for j in range(d)]
                lv = sum(leaves[(j, a)] for j, a in enumerate(digits))
                nd = sum(nodes[(j, a)] for j, a in enumerate(digits)) + d
                need(lv == e and nd <= e + d and lv + nd <= 2 * E + d, "at most 2E+d error factors")
    return queries, worst


# ---------------------------------------------------------------- 2. exp table
def floor_S(v, S):
    return Fr((v * (1 << S)).__floor__(), 1 << S)


def exp_case(n, c=1, C=2, eta=Fr(1, 4), d=13, c0=6, queries=200):
    need(d % 2 == 1 and eta * (d + 1) > c + eta + 2, "odd d with eta(d+1) > c+eta+2")
    lg = (n + 2).bit_length() - 1  # floor(log2(n+2)); p <= c log2(n+2)
    p = c * lg
    h = Fr(1, 1 << math.floor(eta * math.log2(n + 2)))
    J = math.ceil(C * math.log2(n + 2) / h)
    S = p + (J + 1 - 1).bit_length() + c0  # ceil(log2(J+1)) = bitlength(J) for J >= 1
    need((1 << (S - p - c0)) >= J + 1, "ceil(log2(J+1)) bits")
    tail = h ** (d + 1) / math.factorial(d + 1)
    tail_ok = tail <= Fr(1, 1 << S)
    q0 = sum((-h) ** k / math.factorial(k) for k in range(d + 1))
    qhat = floor_S(q0, S)
    digits = S // 3 + 30
    e_h = dec_exp(-h, digits)
    decimal.getcontext().prec = digits + 10
    need(Dec(qhat.numerator) / qhat.denominator <= e_h and qhat >= 0, "0 <= qhat <= e^-h")
    Cd = (e_h - Dec(qhat.numerator) / qhat.denominator) * (1 << S)
    if tail_ok:
        need(Cd <= 2, "C_d <= 2 when the tail is below 2^-S")
        need(3 * J <= 1 << (S - p - 4), "(C_d+1) J 2^-S <= 2^-(p+4)")
    Ehat = Fr(1)
    ref = Dec(1)
    worst_table = Dec(0)
    table = [Ehat]
    for j in range(1, J + 1):
        Ehat = floor_S(Ehat * qhat, S)
        ref = ref * e_h
        gap = ref - Dec(Ehat.numerator) / Ehat.denominator
        need(gap >= -Dec(10) ** (-digits + 5) and gap <= j * (Cd + 1) / (1 << S) + Dec(10) ** (-digits + 5),
             "0 <= e^(-jh) - Ehat_j <= j(C_d+1)2^-S")
        worst_table = max(worst_table, gap * (1 << S) / (j * (Cd + 1)))
        table.append(Ehat)
    rng = random.Random(n)
    xmax = Fr(C * math.log2(n + 2)).limit_denominator(1 << 30)
    frac_bits = p + 8
    xs = [Fr(0), h, 5 * h, Fr(int(xmax * (1 << frac_bits)), 1 << frac_bits)]
    xs += [Fr(rng.randrange(int(xmax * (1 << frac_bits))), 1 << frac_bits) for _ in range(queries)]
    worst_q = Dec(0)
    for x in xs:
        j = int(x / h)  # shifts: h is a power of two
        u = x - j * h
        need(0 <= u < h and j <= J, "range reduction")
        pu = floor_S(sum((-u) ** k / math.factorial(k) for k in range(d + 1)), S)
        val = floor_S(table[j] * pu, S)
        err = abs(Dec(val.numerator) / val.denominator - dec_exp(-x, digits))
        need(err < Dec(1) / (1 << p), "query error < 2^-p")
        worst_q = max(worst_q, err * (1 << p))
    return {"n": n, "p": p, "J": J, "S": S, "tail_below_2^-S": tail_ok, "C_d": float(Cd),
            "table_worst_over_bound": float(worst_table), "query_worst_over_2^-p": float(worst_q)}


def cutoff(c=1, C=2, eta=Fr(1, 4), d=13, c0=6):
    """Smallest k such that the Taylor tail is below 2^-S for every n = 2^m - 2, k <= m <= 4096 (1: no cutoff needed)."""
    last_bad = 0
    for m in range(2, 4097):
        lg = m
        h_exp = math.floor(eta * m)
        J = math.ceil(C * m * (1 << h_exp))
        S = c * lg + J.bit_length() + c0
        # tail = 2^(-h_exp(d+1)) / (d+1)! <= 2^-S
        if Fr(1, 1 << (h_exp * (d + 1))) / math.factorial(d + 1) > Fr(1, 1 << S):
            last_bad = m
    return last_bad + 1


def check_reciprocal(n=1 << 12, C=2):
    """exp(+x) = 1/exp(-x): request eps <= 2^(-p-3) e^(-2 C log2(n+2)), round the reciprocal within 2^(-p-2)."""
    p = (n + 2).bit_length() - 1
    L = C * math.log2(n + 2)
    k = math.ceil(2 * L * math.log2(math.e)) + p + 3  # 2^-k <= 2^(-p-3) e^(-2L)
    digits = k // 3 + 40
    rng = random.Random(7)
    worst = Dec(0)
    for _ in range(100):
        x = Fr(rng.randrange(int(L * 2 ** 20)), 2 ** 20)
        decimal.getcontext().prec = digits + 10
        true_neg = dec_exp(-x, digits)
        approx = true_neg + Dec(rng.uniform(-1, 1)) / Dec(2) ** k  # any approximation within eps
        need(approx >= Dec(-L).exp() / 2, "approximation stays above half the lower bound")
        recip = (Dec(1) / approx * Dec(2) ** (p + 2)).to_integral_value() / Dec(2) ** (p + 2)
        err = abs(recip - dec_exp(x, digits))
        need(err < Dec(1) / Dec(2) ** p, "exp(+x) error < 2^-p")
        worst = max(worst, err * Dec(2) ** p)
    return float(worst)


def check_binding():
    bound = 0
    for name, sha in SPECS.items():
        need(hashlib.sha256((HERE / name).read_bytes()).hexdigest() == sha, f"vendored {name}")
        bound += 1
    ph = (HERE / "PR4554-PHASE-TABLES.md").read_text(encoding="utf-8")
    for s in ("Q>=64(E+d)", "absolute error at most 16(E+d)/Q", "(1+eta)^(2E+d) - 1", "w>=2p+8 bits"):
        need(s in ph, f"PHASE-TABLES.md states: {s}")
        bound += 1
    ex = (HERE / "PR4554-NATIVE-EXP-TABLE.md").read_text(encoding="utf-8")
    for s in ("eta(d+1)>c+eta+2", "0<=exp(-jh)-Ehat_j<=j(C_d+1)2^-S.", "S=p+ceil(log2(J+1))+c0",
              "epsilon<=2^(-p-3) exp(-2C log2(n+2))"):
        need(s in ex, f"NATIVE-EXP-TABLE.md states: {s}")
        bound += 1
    return bound


def main():
    q, w = check_phase()
    report = {"status": "PASS_PR4554_TABLES_CHECK", "phase_queries": q, "phase_worst_error_over_bound": w,
              "exp_cases": [exp_case(n) for n in (1 << 16, 1 << 20, 1 << 24)],
              "exp_tail_cutoff_log2n": cutoff(), "exp_reciprocal_worst_over_2^-p": check_reciprocal(),
              "spec_statements_bound": check_binding(), "new_kappa_claimed": False}
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    sys.exit(main())
