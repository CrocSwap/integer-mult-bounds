#!/usr/bin/env python3
"""Verifier for the best-quotient staircase of the sharp net splitting tax.

Standard library only; no files are read or written.  Every check prints into
one JSON receipt and the command exits nonzero on the first failure.

Notation (see PROOF.md).  For 0<t<1, sigma>1 and a real q>0,
    F_q(s)   = (q + s^t - (q+s)^t) / (q+s)^sigma          (0 <= s <= 1),
    g_sigma(q) = max_s F_q(s),
    H_q(s)   = t q s^(t-1) + (t-sigma) s^t - sigma q + (sigma-t)(q+s)^t,
    a        = t^(1/(1-t)),   W(x) = (x+a)^t - a^t,
    zeta(x)  = (x - t W(x)) / (x - W(x)).
The unique maximizing remainder s_q solves H_q(s)=0 (published in PR #6769).
For integer q>=1 the tie threshold tau_q is the unique sigma with
g_sigma(q) = g_sigma(q+1).

Checks
  A. exact t=1/2 closed form of zeta and the #6769 attaining family;
  B. float grid: the ratio g_sigma(q)/g_sigma(q') increases in sigma; the
     envelope slope -log(q+s_q), the convex kinks at the thresholds and the
     convexity of log N in sigma agree with finite differences;
  C. enclosure table: for five rational t and q<=Q, a tiny sigma interval
     around tau_q with rho_q<1 at its left end and rho_q>1 at its right end,
     the window zeta(q+1) < tau_q < zeta(q), and zeta(q+1/2) < tau_q;
  D. float brute force: the best integer quotient over 1..Qmax matches the
     staircase read from the thresholds;
  E. rejection controls: the false claims tau_q < zeta(q+1/2), and tau_q
     outside its window, fail the enclosure test, and a nearest-integer
     witness is certified.

The enclosure arithmetic widens every exp/ln result by a relative 4e-70 and
treats the 100-digit rounding of + - * / as exact.  Every inequality it
certifies has a relative margin above 1e-15 (reported in the receipt), so the
omitted rounding (relative 1e-98) cannot change a verdict.  It relies on the
documented correct rounding of Decimal.exp and Decimal.ln.
"""

import json
import math
import sys
from decimal import Decimal, getcontext

getcontext().prec = 100
D = Decimal
MARGIN = D("4e-70")

T_LIST = ["0.1", "0.25", "0.5", "0.75", "0.9"]
Q_MAX_TABLE = 30
FLOAT_Q_MAX = 200


class Fail(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise Fail(msg)


# ---------------------------------------------------------------- floats
def f_h(t, sig, q, s):
    return (t * q * s ** (t - 1) + (t - sig) * s**t - sig * q
            + (sig - t) * (q + s) ** t)


def f_s(t, sig, q):
    lo, hi = 1e-18, 1.0
    for _ in range(120):
        mid = 0.5 * (lo + hi)
        if f_h(t, sig, q, mid) > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def f_g(t, sig, q):
    s = f_s(t, sig, q)
    return (q + s**t - (q + s) ** t) / (q + s) ** sig


def f_zeta(t, x):
    a = t ** (1.0 / (1.0 - t))
    w = (x + a) ** t - a**t
    return (x - t * w) / (x - w)


def f_z_of_sigma(t, sig):
    a = t ** (1.0 / (1.0 - t))
    lo, hi = 1e-9, 1e13
    for _ in range(400):
        mid = 0.5 * (lo + hi)
        if (sig - t) * ((mid + a) ** t - a**t) - (sig - 1) * mid > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def f_tau(t, q):
    lo, hi = f_zeta(t, q + 1), f_zeta(t, q)
    for _ in range(120):
        mid = 0.5 * (lo + hi)
        if f_g(t, mid, q) > f_g(t, mid, q + 1):
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


# ------------------------------------------------------- enclosures (Decimal)
def pw(x, e):
    """Enclosure of x**e for Decimals x>0 and e."""
    v = (e * x.ln()).exp()
    m = v * MARGIN
    return (v - m, v + m)


def h_enc(t, q, sig, s):
    """Interval for H_q(s) at an exact Decimal s in (0,1)."""
    p1 = pw(s, t - 1)
    p2 = pw(s, t)
    p3 = pw(q + s, t)
    c1 = t * q
    c2 = t - sig
    c4 = sig - t
    lo = c1 * p1[0] + c2 * p2[1] - sig * q + c4 * p3[0]
    hi = c1 * p1[1] + c2 * p2[0] - sig * q + c4 * p3[1]
    return (lo, hi)


def h_mid(t, q, sig, s):
    return (t * q * (((t - 1) * s.ln()).exp()) + (t - sig) * ((t * s.ln()).exp())
            - sig * q + (sig - t) * ((t * (q + s).ln()).exp()))


def dh_mid(t, q, sig, s):
    return (-t * (1 - t) * q * (((t - 2) * s.ln()).exp())
            + t * (sig - t) * ((((t - 1) * (q + s).ln()).exp())
                               - (((t - 1) * s.ln()).exp())))


def s_hat(t, q, sig):
    s = D(repr(f_s(float(t), float(sig), q)))
    for _ in range(7):
        s = s - h_mid(t, q, sig, s) / dh_mid(t, q, sig, s)
    return s


def g_enc(t, q, sig):
    """Rigorous (lo, hi) for g_sigma(q), q a positive integer."""
    s = s_hat(t, q, sig)
    need(D(0) < s < D(1), "maximizer outside (0,1)")
    for w in (D("1e-40"), D("1e-30"), D("1e-20"), D("1e-12")):
        s1, s2 = s - w, s + w
        if (h_enc(t, q, sig, s1)[0] > 0) and (h_enc(t, q, sig, s2)[1] < 0):
            break
    else:
        raise Fail("could not certify a sign change of H bracketing s_q")
    x = q + s
    num_lo = q + pw(s, t)[0] - pw(x, t)[1]
    need(num_lo > 0, "numerator lower bound not positive")
    g_lo = num_lo / pw(x, sig)[1]
    num_hi = q + pw(s2, t)[1] - pw(q + s1, t)[0]
    g_hi = num_hi / pw(q + s1, sig)[0]
    need(g_lo <= g_hi, "inverted enclosure of g")
    return (g_lo, g_hi)


def rho_enc(t, q, sig):
    a = g_enc(t, q, sig)
    b = g_enc(t, q + 1, sig)
    return (a[0] / b[1], a[1] / b[0])


def a_enc(t):
    return pw(t, D(1) / (D(1) - t))


def zeta_enc(t, x):
    a = a_enc(t)
    p_lo = pw(x + a[0], t)[0]
    p_hi = pw(x + a[1], t)[1]
    at_lo = pw(a[0], t)[0]
    at_hi = pw(a[1], t)[1]
    w_lo, w_hi = p_lo - at_hi, p_hi - at_lo
    den_lo, den_hi = x - w_hi, x - w_lo
    need(den_lo > 0, "x - W(x) not positive")
    num_lo, num_hi = x - t * w_hi, x - t * w_lo
    return (num_lo / den_hi, num_hi / den_lo)


def dec(x, digits=16):
    return D(format(x, "." + str(digits) + "f"))


# --------------------------------------------------------------------- A
def check_a():
    # t = 1/2: zeta(x) = 1 + 1/(sqrt(4x+1) - 1) (closed form), and the #6769
    # family z = n(n+1) at sigma = 1 + 1/(2n).
    half = D("0.5")
    worst = D(0)
    for n in range(1, 17):
        x = D(n * (n + 1))
        z = zeta_enc(half, x)
        exact = D(1) + D(1) / (D(2 * n))
        need(z[0] - D("1e-60") <= exact <= z[1] + D("1e-60"),
             "zeta(n(n+1)) != 1+1/(2n) at t=1/2, n=%d" % n)
        worst = max(worst, z[1] - z[0])
    for x in (D("1.45"), D("2.5"), D("7.25"), D("30.5")):
        closed = D(1) + D(1) / ((D(4) * x + D(1)).sqrt() - D(1))
        z = zeta_enc(half, x)
        need(z[0] - D("1e-60") <= closed <= z[1] + D("1e-60"),
             "t=1/2 closed form of zeta fails at x=%s" % x)
    return {"family_n": 16, "max_enclosure_width": "%.3e" % float(worst)}


# --------------------------------------------------------------------- B
def check_b():
    ts = [0.1, 0.25, 0.5, 0.75, 0.9]
    pairs = [(1, 2), (1, 3), (2, 3), (3, 4), (5, 9), (10, 11), (30, 31), (7, 40)]
    sigmas = [1.001, 1.01, 1.05, 1.1, 1.3, 1.5, 2.0, 3.0, 5.0, 9.0]
    n = 0
    for t in ts:
        for q, qp in pairs:
            prev = None
            for sig in sigmas:
                r = f_g(t, sig, q) / f_g(t, sig, qp)
                if prev is not None:
                    need(r > prev, "ratio not increasing t=%s q=%d q'=%d" % (t, q, qp))
                prev = r
                n += 1
    return {"ratio_evaluations": n}


def check_b2():
    """Envelope slope: d/dsigma log g_sigma(q) = -log(q + s_q) (PROOF.md, section 5)."""
    n = 0
    worst = 0.0
    for t in (0.1, 0.5, 0.9):
        for q in (1, 2, 7, 25):
            for sig in (1.05, 1.3, 2.0, 4.0):
                h = 1e-5
                num = math.log(f_g(t, sig + h, q)) - math.log(f_g(t, sig - h, q))
                slope = num / (2 * h)
                exact = -math.log(q + f_s(t, sig, q))
                err = abs(slope - exact)
                worst = max(worst, err)
                need(err < 1e-7, "envelope slope mismatch t=%s q=%d sigma=%s" % (t, q, sig))
                n += 1
    # one-sided slopes at a tie: left branch q+1, right branch q (convex kink)
    kinks = 0
    for t in (0.1, 0.5, 0.9):
        for q in (1, 2, 3, 6):
            tau = f_tau(t, q)
            h = 1e-6

            def log_n(sig):
                return max(math.log(f_g(t, sig, k)) for k in range(1, 40))

            right = (log_n(tau + 2 * h) - log_n(tau + h)) / h
            left = (log_n(tau - h) - log_n(tau - 2 * h)) / h
            exp_right = -math.log(q + f_s(t, tau, q))
            exp_left = -math.log(q + 1 + f_s(t, tau, q + 1))
            need(abs(right - exp_right) < 2e-4, "right slope mismatch at tau t=%s q=%d" % (t, q))
            need(abs(left - exp_left) < 2e-4, "left slope mismatch at tau t=%s q=%d" % (t, q))
            need(right - left > 1e-3, "no convex kink at tau t=%s q=%d" % (t, q))
            kinks += 1
    # log N is convex in sigma: second differences are nonnegative
    convex_pts = 0
    for t in (0.1, 0.25, 0.5, 0.75, 0.9):
        h = 1e-3

        def log_n2(sig):
            return max(math.log(f_g(t, sig, k)) for k in range(1, 80))

        sig = f_zeta(t, 60.0)
        while sig < 3.0:
            d2 = log_n2(sig + h) - 2 * log_n2(sig) + log_n2(sig - h)
            need(d2 > -1e-11, "log N not convex at t=%s sigma=%.5f" % (t, sig))
            convex_pts += 1
            sig += 0.037
    return {"slope_checks": n, "max_abs_error": "%.2e" % worst,
            "kinks_checked": kinks, "convexity_points": convex_pts}


# --------------------------------------------------------------------- C
def certify_pair(t_str, q):
    t = D(t_str)
    tf = float(t)
    tau = f_tau(tf, q)
    for delta in (1e-12, 1e-11, 1e-10, 1e-9, 1e-8):
        s_lo, s_hi = dec(tau - delta), dec(tau + delta)
        r_lo = rho_enc(t, q, s_lo)
        r_hi = rho_enc(t, q, s_hi)
        if r_lo[1] < 1 < r_hi[0]:
            break
    else:
        raise Fail("no certified tie bracket for t=%s q=%d" % (t_str, q))
    z_up = zeta_enc(t, D(q))
    z_dn = zeta_enc(t, D(q + 1))
    z_half = zeta_enc(t, D(q) + D("0.5"))
    window = (z_dn[1] < s_lo) and (s_hi < z_up[0])
    below_half = z_half[1] < s_lo
    margins = [float(1 - r_lo[1]), float(r_hi[0] - 1),
               float((s_lo - z_dn[1]) / s_lo), float((z_up[0] - s_hi) / s_hi),
               float((s_lo - z_half[1]) / s_lo)]
    return {"t": t_str, "q": q, "tau": tau, "delta": delta, "window": window,
            "below_half": below_half, "margins": margins, "s_lo": s_lo,
            "s_hi": s_hi}


def check_c():
    rows = []
    min_margin = 1.0
    max_delta = 0.0
    for t_str in T_LIST:
        for q in range(1, Q_MAX_TABLE + 1):
            r = certify_pair(t_str, q)
            need(r["window"], "window failed t=%s q=%d" % (t_str, q))
            need(r["below_half"], "zeta(q+1/2) < tau_q failed t=%s q=%d" % (t_str, q))
            min_margin = min(min_margin, min(r["margins"]))
            max_delta = max(max_delta, r["delta"])
            rows.append(r)
        taus = [r["tau"] for r in rows if r["t"] == t_str]
        need(all(a > b for a, b in zip(taus, taus[1:])), "tau_q not decreasing t=%s" % t_str)
    need(min_margin > 1e-15, "certified margin too small")
    table = {}
    for t_str in T_LIST:
        table[t_str] = {
            str(r["q"]): "%.10f" % r["tau"]
            for r in rows
            if r["t"] == t_str and q_in(r["q"])
        }
    offsets = {}
    for t_str in T_LIST:
        tf = float(D(t_str))
        offsets[t_str] = {
            str(r["q"]): round(f_z_of_sigma(tf, r["tau"]) - r["q"], 6)
            for r in rows
            if r["t"] == t_str and q_in(r["q"])
        }
    return {"pairs_certified": len(rows), "min_relative_margin": "%.3e" % min_margin,
            "max_bracket_half_width": max_delta, "tau": table, "theta": offsets}


def q_in(q):
    return q in (1, 2, 3, 5, 10, 20, 30)


# --------------------------------------------------------------------- D
def check_d():
    checked = 0
    for t in (0.1, 0.25, 0.5, 0.75, 0.9):
        qcap = 40
        taus = {m: f_tau(t, m) for m in range(1, qcap + 1)}
        top = f_zeta(t, qcap - 5)
        lo_sig = f_zeta(t, 0.4)
        grid = [top + (lo_sig - top) * (k + 0.5) / 60.0 for k in range(60)]
        for sig in grid:
            gs = [f_g(t, sig, q) for q in range(1, FLOAT_Q_MAX + 1)]
            best = max(range(len(gs)), key=lambda i: gs[i]) + 1
            predicted = 1 + sum(1 for m in range(1, qcap + 1) if taus[m] > sig)
            need(best == predicted,
                 "staircase mismatch t=%s sigma=%.9f best=%d predicted=%d"
                 % (t, sig, best, predicted))
            checked += 1
    return {"sigma_points": checked, "q_range": FLOAT_Q_MAX}


# --------------------------------------------------------------------- E
def check_e():
    out = {}
    # (1) the false claim "tie at z >= q+1/2" must fail the enclosure test
    t = D("0.5")
    bad = 0
    for q in (1, 2, 5, 12):
        r = certify_pair("0.5", q)
        false_claim = r["s_hi"] < zeta_enc(t, D(q) + D("0.5"))[0]
        need(not false_claim, "false 'tie before z=q+1/2 is wrong' claim passed")
        outside = r["s_hi"] < zeta_enc(t, D(q + 1))[0] or r["s_lo"] > zeta_enc(t, D(q))[1]
        need(not outside, "bracket outside its window")
        bad += 2
    out["rejected_false_claims"] = bad
    # (2) nearest-integer witness: z = 1.45 rounds to 1, but quotient 2 is
    # strictly better at that sigma (t = 1/2 and t = 1/4).
    wit = {}
    for t_str in ("0.5", "0.25"):
        tt = D(t_str)
        z = zeta_enc(tt, D("1.45"))
        sig = dec(float((z[0] + z[1]) / 2))
        r = rho_enc(tt, 1, sig)
        need(r[1] < 1, "nearest-integer witness failed t=%s" % t_str)
        wit[t_str] = {"sigma": str(sig), "rho_upper": "%.6f" % float(r[1])}
    out["nearest_integer_witness_z_1.45"] = wit
    # (3) a mutated rho (the smaller quotient given the larger remainder cap)
    # would not be increasing: the ratio g(q+1)/g(q) is decreasing.
    t = 0.5
    vals = [f_g(t, s, 2) / f_g(t, s, 1) for s in (1.2, 1.5, 2.0, 3.0)]
    need(all(a > b for a, b in zip(vals, vals[1:])), "inverse ratio control failed")
    out["inverse_ratio_decreasing"] = True
    return out


def main():
    receipt = {"status": "FAIL"}
    try:
        receipt["A_closed_forms"] = check_a()
        receipt["B_ratio_grid"] = check_b()
        receipt["B2_envelope_slope"] = check_b2()
        receipt["C_enclosure_table"] = check_c()
        receipt["D_staircase_bruteforce"] = check_d()
        receipt["E_controls"] = check_e()
        receipt["status"] = "PASS_NET_SPLIT_QUOTIENT_STAIRCASE"
    except Fail as exc:
        receipt["failure"] = str(exc)
        print(json.dumps(receipt, indent=1, sort_keys=True))
        return 1
    print(json.dumps(receipt, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
