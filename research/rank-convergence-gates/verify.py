#!/usr/bin/env python3
"""Independent certified check of #4483's finite gates (adaptive height, shifted-log majorant) for all four witnesses.

For each witness in research/rank-convergence/BENCHMARKS.json, with the raw profile read from its pinned source, this
recomputes with its own certified interval logarithms/exponentials (helpers of research/p17-b480-check) the guards
(18) of PROOF.md on [t0, t_hi]:
  T_t0 > P_t0;  d <= mu_T(t0) - mu_P(t_hi) (tilted log means);  Q >= T_thi / P_t0;
  U >= M^-s (T_(thi+s)/T_thi)^a (P_(thi+s)/P_thi)^b;  V >= M^lambda (T_(thi-lambda)/P_t0)^g;
  T_(t0+s)/T_t0 >= P_(thi+s)/P_thi;  eta_min <= t0 m^(t0-1);  c >= p/(1-t0);  tau(n0) = t0 + p/(c + ln n0) <= t_hi;
the mirror guard (4) on every elementary window and each of the witness's t-slices [ta, tb] in the sufficient form
E_J(tb) <= beta S_J(ta); the single recurrence inequality (20) (U^ell0, V^ell0 exact rational powers); and the final
funding (17) at N = 2^H with z = 1 - uniform saving and A0 = n0^(1-t0) / (c + ln n0)^p.
It also checks, on raw p7, the arbitrary-height flow of PROOF.md section 1 (heights 0 .. G0+2, including empty root
classes): the exact rank-one identity sum S s - sum X e = 608 col, exits below n, and the exact mirror identity of
#4459 at every such height. It does not re-prove PROOF.md's theorem, the native supplier or the outer consumer.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import hashlib
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


# ---- arbitrary-height flow (PROOF.md section 1; open question 1 of #4483) ----
from math import factorial
def multis(n_types, size):
    if n_types == 0:
        if size == 0: yield ()
        return
    for x in range(size + 1):
        for rest in multis(n_types - 1, size - x): yield (x,) + rest
def flow(N, W, P, Gover=None):
    ks = sorted(W); m = ks[-1]; kmin = ks[0]
    def c(a):
        v = 1
        for k, x in zip(ks, a): v *= k ** x
        return v
    def u(a):
        v = factorial(sum(a))
        for k, x in zip(ks, a): v = v // factorial(x) * W[k] ** x
        return v
    G = 0
    while kmin ** (G + 1) <= N // m: G += 1
    if Gover is not None: G = Gover
    F = [{1: 1}]
    for d in range(1, G + 1):
        nxt = {}
        for rho, cnt in F[d - 1].items():
            for r, pr in P.items():
                if m * rho * r <= N: nxt[rho * r] = nxt.get(rho * r, 0) + cnt * pr
        F.append(nxt)
    S, X, BX = {}, {}, {}
    col = units = matched = 0
    add = lambda D, k, v: D.__setitem__(k, D.get(k, 0) + v)
    present = lambda rho, a: m * rho * c(a) <= N
    for d in range(G + 1):
        for rho, cnt in F[d].items():
            for b in multis(len(ks), G - d):
                if not present(rho, b): continue
                units += cnt * u(b); col += cnt * u(b) * rho * c(b)
                for r, pr in P.items():
                    issued = cnt * pr * u(b); rank = r * rho * c(b)
                    if d == G:
                        add(X, rank, issued); continue
                    D = sum(W[k] * u(tuple(x - (i == j) for j, x in enumerate(b)))
                            for i, k in enumerate(ks) if b[i] > 0 and present(rho * r, tuple(x - (i == j) for j, x in enumerate(b))))
                    matched += cnt * pr * D
                    if issued - cnt * pr * D:
                        add(X, rank, issued - cnt * pr * D); add(BX, rank, issued - cnt * pr * D)
    for a in multis(len(ks), G):
        if present(1, a):
            for k in ks: add(S, k * c(a), W[k] * u(a))
    for d in range(1, G + 1):
        for rho, cnt in F[d - 1].items():
            for r, pr in P.items():
                for a in multis(len(ks), G - d):
                    if not present(rho * r, a): continue
                    for i, k in enumerate(ks):
                        b = list(a); b[i] += 1
                        if not present(rho, tuple(b)):
                            add(S, rho * r * c(tuple(b)), cnt * pr * u(a) * W[k])
    return dict(G=G, S=S, X=X, BX=BX, col=col, units=units, matched=matched)


def mirror_identity(N, W, P, m, r):
    """exact: BX and S equal the mirrored windows of the base measure mu(z), z = rho c(a)"""
    ks = sorted(W)
    G = r["G"]
    F = [{1: 1}]
    for d in range(1, G + 1):
        nxt = {}
        for rho, cnt in F[d - 1].items():
            for rr, pr in P.items():
                if m * rho * rr <= N:
                    nxt[rho * rr] = nxt.get(rho * rr, 0) + cnt * pr
        F.append(nxt)
    mu = {}
    for d in range(G):
        for rho, cnt in F[d].items():
            for a in multis(len(ks), G - d - 1):
                c, u = 1, factorial(sum(a))
                for k, x in zip(ks, a):
                    c *= k ** x
                    u = u // factorial(x) * W[k] ** x
                mu[rho * c] = mu.get(rho * c, 0) + cnt * u
    bx, src = {}, {}
    for z, w in mu.items():
        for rr in P:
            for k in W:
                if rr > k and N < m * z * rr and m * z * k <= N:
                    bx[rr * k * z] = bx.get(rr * k * z, 0) + P[rr] * W[k] * w
                if k > rr and N < m * z * k and m * z * rr <= N:
                    src[rr * k * z] = src.get(rr * k * z, 0) + P[rr] * W[k] * w
    for a in multis(len(ks), G):
        c, u = 1, factorial(G)
        for k, x in zip(ks, a):
            c *= k ** x
            u = u // factorial(x) * W[k] ** x
        if m * c <= N:
            for k in ks:
                src[k * c] = src.get(k * c, 0) + W[k] * u
    need(bx == {e: v for e, v in r["BX"].items() if v}, f"N={N}: boundary exits are the mirrored windows")
    need(src == r["S"], f"N={N}: sources are the mirrored windows plus the top layer")




def arbitrary_height():
    W = {5: 420, 6: 270, 7: 840, 8: 1395, 9: 3195, 25: 448, 41: 448, 57: 448, 121: 224}
    P = {1: 37305, 2: 10695, 3: 3360, 4: 1530, 5: 300, 8: 1464, 16: 448, 32: 448, 48: 448}
    surplus = sum(k * x for k, x in W.items()) - sum(r * x for r, x in P.items())
    need(surplus == 608, "raw p7 rank-one surplus")
    pairs = 0
    for N in (500, 3000, 20000):
        G0 = 0
        while 5 ** (G0 + 1) <= N // 121:
            G0 += 1
        for G in range(0, G0 + 3):
            r = flow(N, W, P, G)
            r["G"] = G
            need(sum(s * x for s, x in r["S"].items()) - sum(e * x for e, x in r["X"].items()) == surplus * r["col"],
                 f"N={N}, G={G}: rank-one identity")
            need(max(r["X"]) < N, f"N={N}, G={G}: exits below N")
            mirror_identity(N, W, P, 121, r)
            pairs += 1
    return pairs


def main():
    for row in json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]:
        need(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"], row["path"])
    cases = json.loads((ROOT / "research/rank-convergence/BENCHMARKS.json").read_text(encoding="utf-8"))["cases"]
    need([c["name"] for c in cases] == ["p7", "native4453", "native4453-matched-uniform", "p16"], "four witnesses")
    out = {c["name"]: check(c) for c in cases}
    # rejection control from PROOF.md section 6: t_hi = .9974808 fails to cover tau(n0) for p7
    bad = json.loads(json.dumps(cases[0]))
    bad["witness"]["t_upper"] = ".9974808"
    try:
        check(bad)
        need(False, "the smaller p7 endpoint must be rejected")
    except AssertionError as exc:
        need("tau" in str(exc) or "mirror" in str(exc) or "guard" in str(exc), "smaller p7 endpoint rejected")
    pairs = arbitrary_height()
    print(json.dumps({"status": "PASS_RANK_CONVERGENCE_GATES", "witnesses": out, "arbitrary_height_pairs": pairs, "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
