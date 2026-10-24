#!/usr/bin/env python3
"""Sharper witnesses for #4483's adaptive-height compiler at unchanged uniform saving and kappa.

    p16 (kappa .00302015): H = 1,587,000,000 instead of 2,800,000,000  (t0 .99697984, p 3/5, c 400, M 768, ell0 140,
        s 3/100, lambda 3/25; guards U .9848, V .9609, Q 1.0017, d 1.04, beta .5632, eta .982, t_hi .9974293)
    p7  (kappa .00268647): H = 2,253,000,000 instead of 3,040,000,000  (t0 .99731352, p 1/10, c 40, M 288, ell0 44,
        s 3/25, lambda 2/5; guards U .9436, V .7921, Q 1.0012, d 1.72, beta .321, eta .9845, t_hi .9976537)
    native4453 (kappa .00300120): H = 713,000,000 instead of 1,300,000,000, and the matched-uniform case
        2,580,000,000 instead of 4,300,000,000 (t0 29909963/30000000, p 2/5, c 200, M 768, ell0 140, s 1/20,
        lambda 3/20; guards U .9817, V .9417, Q 1.0013, d 1.02, beta .5743, eta .982, t_hi .9973512)
Each witness keeps #4483's raw profile, uniform saving and kappa; only the free geometry changes. This verifier
re-certifies every finite gate of #4483's PROOF.md (guards (18), mirror (4), recurrence (20), funding (17)) with its
own interval arithmetic (from research/rank-convergence-gates), shows H - 10^6 fails (17), and cross-checks each
witness with #4483's own compiler.certify on main.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise AssertionError(message)


GRID = Q(1, 10**50)


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def down(x):
    return (x / GRID).__floor__() * GRID


def up(x):
    return (x / GRID).__ceil__() * GRID


def ln_bounds(n):
    """certified ln n for integer n >= 1 (reduction to [1, 2) and the atanh series)"""
    if n == 1:
        return Q(0), Q(0)
    k = n.bit_length() - 1
    y = Q(n, 2 ** k)
    out = [Q(0), Q(0)]
    for part, scale in ((y, 1), (Q(2), k)):
        if part == 1 or scale == 0:
            continue
        u = (part - 1) / (part + 1)
        s, term, j = Q(0), u, 0
        while True:
            s += term / (2 * j + 1)
            j += 1
            term *= u * u
            tail = term / (2 * j + 1) / (1 - u * u)
            if tail < GRID:
                break
        out[0] += scale * down(2 * s)
        out[1] += scale * up(2 * (s + tail))
    return out[0], out[1]


def exp_bounds(x_lo, x_hi):
    """certified exp on a small interval (|x| < 1)"""
    def series(x):
        s, term = Q(0), Q(1)
        for i in range(70):
            s += term
            term = term * x / (i + 1)
        return s, abs(term) * 2
    a, ea = series(x_lo)
    b, eb = series(x_hi)
    return down(a - ea), up(b + eb)


LN = {}


def ln(n):
    if n not in LN:
        LN[n] = ln_bounds(n)
    return LN[n]


def moment(hist, C):
    """bounds of sum count * k^(1-C)"""
    lo = hi = Q(0)
    for k, w in hist.items():
        e = exp_bounds(-C * ln(k)[1], -C * ln(k)[0])
        lo, hi = lo + w * k * e[0], hi + w * k * e[1]
    return lo, hi


def lnq(x):
    a, b = ln(x.numerator), ln(x.denominator)
    return a[0] - b[1], a[1] - b[0]


def powq(base, e):
    """certified base^e for integer base >= 1 and rational exponent e (|e ln base| < 1.2)"""
    l = ln(base)
    lo, hi = (e * l[0], e * l[1]) if e >= 0 else (e * l[1], e * l[0])
    return exp_bounds(lo, hi)




def rat(x):
    return Q(x)


def ln_real(lo, hi):
    """certified ln on a positive rational interval [lo, hi]"""
    return lnq(Q(lo))[0], lnq(Q(hi))[1]


def expi(lo, hi):
    """certified exp on an interval, reducing large |x| by halving and squaring"""
    k = 0
    while max(abs(lo), abs(hi)) > Q(1, 2):
        lo, hi, k = lo / 2, hi / 2, k + 1
    a, b = exp_bounds(lo, hi)
    for _ in range(k):
        a, b = down(a * a), up(b * b)
    return a, b


def mgf(h, t):
    """certified sum_k w k^t"""
    lo = hi = Q(0)
    for k, w in h.items():
        l = ln(k)
        a, b = expi(t * l[0], t * l[1])
        lo, hi = lo + w * a, hi + w * b
    return lo, hi


def logmean(h, t):
    nlo = nhi = Q(0)
    for k, w in h.items():
        l = ln(k)
        a, b = expi(t * l[0], t * l[1])
        nlo, nhi = nlo + w * a * l[0], nhi + w * b * l[1]
    dlo, dhi = mgf(h, t)
    return nlo / dhi, nhi / dlo


def profile(case):
    d = json.loads((ROOT / case["source"]).read_text(encoding="utf-8"))
    if case["profile_key"]:
        d = d[case["profile_key"]]
    return {int(k): v for k, v in d["targets"].items()}, {int(k): v for k, v in d["paid"].items()}


def check(case):
    T, P = profile(case)
    w, g = case["witness"], case["witness"]["guards"]
    t0, th, p, c, s, lam = (rat(w[x]) for x in ("t0", "t_upper", "p", "c", "s", "lambda"))
    a, b, M, ell0, slices = w["a"], w["b"], w["height_base"], w["ell0"], w["mirror_slices"]
    U, V, Qg, d, beta, eta = (rat(g[x]) for x in ("U", "V", "Q", "d", "beta", "eta"))
    gg, m = a + b, max(T)
    need(min(T) >= 2 and max(P) < m and 1 in P, "profile premises")
    need(mgf(T, t0)[0] > mgf(P, t0)[1], "T_t0 > P_t0")
    need(logmean(T, t0)[0] - logmean(P, th)[1] >= d, "derivative guard d")
    need(mgf(T, th)[1] / mgf(P, t0)[0] <= Qg, "Q guard")
    lnM = ln(M)
    Ms = expi(-s * lnM[1], -s * lnM[0])[1]
    rT, rP = mgf(T, th + s)[1] / mgf(T, th)[0], mgf(P, th + s)[1] / mgf(P, th)[0]
    need(Ms * rT ** a * rP ** b <= U, "U guard")
    Ml = expi(lam * lnM[0], lam * lnM[1])[1]
    need(Ml * (mgf(T, th - lam)[1] / mgf(P, t0)[0]) ** gg <= V, "V guard")
    need(mgf(T, t0 + s)[0] / mgf(T, t0)[1] >= mgf(P, th + s)[1] / mgf(P, th)[0], "ratio ordering")
    lm = ln(m)
    need(t0 * expi((t0 - 1) * lm[1], (t0 - 1) * lm[0])[0] >= eta, "eta_min <= t0 m^(t0-1)")
    need(c >= p / (1 - t0), "c >= p/(1-t0)")
    ln_n0 = (lm[0] + ell0 * lnM[0], lm[1] + ell0 * lnM[1])
    tau_hi = t0 + p / (c + ln_n0[0])
    need(tau_hi <= th, "tau(n0) <= t_hi")
    # mirror windows over t-slices
    pts = sorted({Q(1, x) for x in list(T) + list(P)})
    worst = Q(0)
    for i in range(slices):
        ta, tb = t0 + (th - t0) * i / slices, t0 + (th - t0) * (i + 1) / slices
        pw = {}
        for r in P:
            for k in T:
                l = ln(r * k)
                pw[r, k] = (expi(ta * l[0], ta * l[1])[0], expi(tb * l[0], tb * l[1])[1])
        for lo, hi in zip(pts, pts[1:]):
            mid = (lo + hi) / 2
            E = sum(P[r] * T[k] * pw[r, k][1] for r in P for k in T if r > k and Q(1, r) < mid <= Q(1, k))
            S = sum(P[r] * T[k] * pw[r, k][0] for r in P for k in T if k > r and Q(1, k) < mid <= Q(1, r))
            if E:
                need(S > 0 and E <= beta * S, f"mirror window slice {i}")
                worst = max(worst, E / S)
    # recurrence inequality (20)
    l2 = ln(2)
    den_hi = c + lm[1] + (ell0 + 1) * lnM[1] + l2[1]
    x_lo = d * p * (a * ell0 + 1) / den_hi
    e_lo = expi(x_lo, x_lo)[0]
    D_lo = (1 - U ** ell0) * (e_lo - 1) - Qg * Ml * V ** ell0
    req = (1 - eta) / (eta - beta)
    need(D_lo >= req, "recurrence inequality (20)")
    # final funding (17)
    z = 1 - rat(w["uniform_saving"])
    H = w["H"]
    lnN = (H * l2[0], H * l2[1])
    lnc0 = ln_real(down(c + ln_n0[0]), up(c + ln_n0[1]))
    lnA0_hi = (1 - t0) * ln_n0[1] - p * lnc0[0]
    lncN = ln_real(down(c + lnN[0]), up(c + lnN[1]))
    margin_lo = (z - t0) * lnN[0] - (lnA0_hi + p * lncN[1])
    need(margin_lo > 0, "final funding (17)")
    return {"D_lower": f"{float(D_lo):.8f}", "required": f"{float(req):.8f}", "mirror_worst": f"{float(worst):.5f}",
            "tau_n0_upper": f"{float(tau_hi):.10f}", "t_hi": str(w["t_upper"]), "final_margin_lower": f"{float(margin_lo):.8f}"}


def main():
    for row in json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]:
        need(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"], row["path"])
    cases = {c["name"]: c for c in json.loads((ROOT / "research/rank-convergence/BENCHMARKS.json").read_text(encoding="utf-8"))["cases"]}
    spec = importlib.util.spec_from_file_location("rank_convergence_compiler", ROOT / "research/rank-convergence/compiler.py")
    comp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(comp)
    out = {}
    wanted = set(sys.argv[1:])
    for name, old_H, new_H in (("p16", 2800000000, 1587000000), ("p7", 3040000000, 2253000000),
                               ("native4453", 1300000000, 713000000), ("native4453-matched-uniform", 4300000000, 2580000000)):
        if wanted and name not in wanted:
            continue
        base = cases[name]
        need(base["witness"]["H"] == old_H, f"#4483's {name} witness")
        witness = json.loads((HERE / f"WITNESS-{name}.json").read_text(encoding="utf-8"))
        need(witness["uniform_saving"] == base["witness"]["uniform_saving"] and witness["kappa"] == base["witness"]["kappa"],
             f"{name}: same uniform saving and kappa")
        need(witness["H"] == new_H, f"{name}: new H")
        case = dict(base, witness=witness)
        res = check(case)
        smaller = json.loads(json.dumps(case))
        smaller["witness"]["H"] = new_H - 10 ** 6
        try:
            check(smaller)
            need(False, "H - 10^6 must fail")
        except AssertionError as exc:
            need("(17)" in str(exc), f"{name}: H - 10^6 fails only the final funding")
        src = json.loads((ROOT / base["source"]).read_text(encoding="utf-8"))
        if base["profile_key"]:
            src = src[base["profile_key"]]
        theirs = comp.certify({"targets": src["targets"], "paid": src["paid"]}, witness)
        need(theirs["status"] == "PASS_ADAPTIVE_HEIGHT_DIRECT_COMPILER" and theirs["H"] == new_H, f"{name}: #4483 compiler")
        out[name] = {"H_new": new_H, "H_4483": old_H, "exponent_ratio": round(old_H / new_H, 4), "gates": res}
    print(json.dumps({"status": "PASS_ADAPTIVE_WITNESS_RETUNE", "witnesses": out, "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
