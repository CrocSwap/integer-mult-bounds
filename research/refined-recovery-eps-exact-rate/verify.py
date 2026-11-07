"""Exact checks for the decay rate 4 log2 13 of the refined-recovery second-order term.

Prints PASS_REFINED_RECOVERY_EPS_EXACT_RATE on success (stdlib only).
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


DEPTHS = (40, 60, 100, 200, 400, 1000)
R_GRID = [Fraction(k, 100) for k in range(1, 100)]


def m(r):
    """E[r^X], X = weight of a uniform word of C (0 once, 4 fourteen times, 8 once)."""
    return (1 + 14 * r ** 4 + r ** 8) / 16


def check_C_weights(code):
    check(sorted(wt(c) for c in code) == [0] + [4] * 14 + [8], "weights of C")
    check(Fraction(sum(wt(c) for c in code), 16) == 4, "mean weight 4")
    check(m(Fraction(1, 13)) == Fraction(16 * F, 13 ** 8) / 16, "m(1/13) = q of #6851")


def chernoff_ok(t, w, r):
    """(2^104 - 16) r^(-w) m(r)^(t-1) < 1, exactly."""
    return (2 ** CAP - 16) * m(r) ** (t - 1) < r ** w


def best_w(t):
    best, wit = 0, None
    w = 4
    while w < 4 * t:
        r = next((r for r in R_GRID if chernoff_ok(t, w, r)), None)
        if r is None:
            break
        best, wit = w, r
        w += 4
    return best, wit


def cramer_rate(c):
    """Some rational r < 1 with r^(-c) m(r) < 1, certifying exponential decay at slope c < 4."""
    for k in range(999, 0, -1):
        r = Fraction(k, 1000)
        # r^(-c) m(r) < 1  <=>  m(r)^den < r^num for c = num/den
        if m(r) ** c.denominator < r ** c.numerator:
            return r
    return None


def main():
    rows = load_rows()
    code = code_from_rows(rows)
    coset_data(code)
    check_C_weights(code)
    table = []
    for t in DEPTHS:
        w, r = best_w(t)
        check(w > 0 and chernoff_ok(t, w, r), "Chernoff certificate at t=%d" % t)
        up = math.log2(2 ** CAP - 1) - w * math.log2(13)
        lo = math.log2(2 ** CAP - 1) - 4 * t * (2 ** CAP / (2 ** CAP - 1)) * math.log2(13)
        check(lo <= up, "Jensen below the upper bound")
        table.append({"t": t, "w_t": w, "r": str(r), "w_over_t": round(w / t, 4),
                      "log2_eps_upper": round(up, 1), "log2_eps_lower": round(lo, 1)})
    check([row["w_t"] for row in table] == sorted(row["w_t"] for row in table), "monotone")
    check(table[-1]["w_over_t"] > Fraction(34, 10), "w_t/t > 3.4 at t = 1000")
    # Cramer: every slope c < 4 has a certificate r^(-c) m(r) < 1
    certs = {}
    for c in (Fraction(3), Fraction(7, 2), Fraction(39, 10), Fraction(399, 100)):
        r = cramer_rate(c)
        check(r is not None, "Cramer certificate for slope %s" % c)
        certs[str(c)] = str(r)
    check(cramer_rate(Fraction(4)) is None, "control: no certificate at the mean slope 4")
    result = {
        "rate_bits_per_stage": round(4 * math.log2(13), 6),
        "cramer_certificates_slope_to_r": certs,
        "table": table,
    }
    text = json.dumps(result, indent=1) + "\n"
    if __debug__ and not RESULT.exists():
        RESULT.write_text(text)
    check(RESULT.read_text() == text, "RESULT.json matches recomputation")
    print("w_t/t:", [row["w_over_t"] for row in table], "-> 4; rate 4 log2 13 = %.4f" % (4 * math.log2(13)))
    print("PASS_REFINED_RECOVERY_EPS_EXACT_RATE")


if __name__ == "__main__":
    main()
