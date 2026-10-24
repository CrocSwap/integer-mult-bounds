#!/usr/bin/env python3
"""Independent arithmetic check of #4535: conditional kappa 0.003020165 via critical-root transfer.

Reads #4535's RESULT.json (vendored as RESULT-4535.json, sha256 pinned to head cca1112d) and the unchanged p16
profile on main (research/compact-joint-compiler/arithmetic/RESULT.json; 10,928 fields, 64,620 paid jobs). With its
own certified intervals (helpers of research/rank-convergence-gates) it checks:
  * the critical-root interval [theta_lo, theta_hi] brackets the T_t = P_t crossing and equals 1 minus #4478's raw-root
    bracket (0.0030201659770, 0.0030201659771);
  * kappa < uniform saving and t - theta_hi = 377/10^12 exactly (t = 1 - uniform saving);
  * the mirror windows at theta: E_J(theta_hi) <= beta S_J(theta_lo) with beta = 141/250 (worst 0.56281);
  * absorption A N^theta (133 + ln N)^(2/5) <= N^t with ln A <= (1 - theta_lo) ln(145 * 1024^650), at ln N = 10^12
    (#4535's log_threshold) and at the stated N = 2^(10^12), and its monotonicity (gap > p/(c + ln N));
  * seven of the nine outer rows (main transform eps*q, global router a, fused Gaussian 1-eps+q*beta, group bit router
    1-eps+a*beta, group scans 1-eps+beta, polynomial products eps, micro-box faces 79-eps-beta) exceed kappa; the
    binding main-transform margin equals the reported minimum 29969798347/10^20; the parameter schedule is kappa + k d.
xi is not printed in #4535's outer parameters, so the two xi rows are not recomputed.
  * the finite envelope arithmetic: height G <= 2e11 at N = 2^(10^12), W0 < 2^14, W0+P0+1 < 2^17, C_N < 2^(17G+31) =
    2^3400000000031, and the episode counts 144 = 18*8 and 1680 = 15*112.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULT_SHA = "85f6e8a659c53c49acfde141eaae3ece0b7d8c5c1750b82674bc7292e7d630e8"


def need(condition, message):
    if not condition:
        raise AssertionError(message)


GRID = Q(1, 10**50)




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




def main():
    for row in json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]:
        need(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"], row["path"])
    raw = (HERE / "RESULT-4535.json").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == RESULT_SHA, "#4535 RESULT.json bytes")
    R = json.loads(raw)
    pr=json.loads((ROOT / 'research/compact-joint-compiler/arithmetic/RESULT.json').read_text(encoding='utf-8')); T={int(k):v for k,v in pr['targets'].items()}; P={int(k):v for k,v in pr['paid'].items()}
    need(sum(T.values())==10928 and sum(P.values())==64620,"p16 invoice")
    th_lo,th_hi=(Q(x) for x in R['critical_root']['critical_root_interval'])
    # raw root: T_t - P_t changes sign across [th_lo, th_hi]
    a=mgf(T,th_lo); b=mgf(P,th_lo); need(a[1]<b[0],"T < P at theta_lo (t below crossing)")
    a=mgf(T,th_hi); b=mgf(P,th_hi); need(a[0]>b[1],"T > P at theta_hi")
    us=Q(R['uniform_saving']); kap=Q(R['kappa']); t=1-us
    need(kap<us and t>th_hi and t-th_hi==Q(377,10**12),"saving order and gap 377/1e12")
    need(1-th_hi==Q(30201659770,10**13) and 1-th_lo==Q(30201659771,10**13),"theta interval = 1 - raw-root bracket (#4478)")
    # mirror at theta (pointwise): E_J(theta_hi) <= beta S_J(theta_lo)
    beta=Q(R['critical_root']['beta']); pts=sorted({Q(1,x) for x in list(T)+list(P)}); worst=Q(0)
    pw={}
    for r in P:
        for k in T:
            l=ln(r*k); pw[r,k]=(expi(th_lo*l[0],th_lo*l[1])[0],expi(th_hi*l[0],th_hi*l[1])[1])
    for lo,hi in zip(pts,pts[1:]):
        mid=(lo+hi)/2
        E=sum(P[r]*T[k]*pw[r,k][1] for r in P for k in T if r>k and Q(1,r)<mid<=Q(1,k))
        S=sum(P[r]*T[k]*pw[r,k][0] for r in P for k in T if k>r and Q(1,k)<mid<=Q(1,r))
        if E: need(S>0 and E<=beta*S,"mirror"); worst=max(worst,E/S)
    print("mirror worst",float(worst),"beta",float(beta))
    # absorption: (t - theta) lnN - lnA - p ln(c + lnN) > 0 with lnA <= (1-theta_lo) ln n0, n0 = 145*1024^650
    p=Q(2,5); c=Q(133); l1024=ln(1024); l145=ln(145)
    ln_n0_hi=l145[1]+650*l1024[1]
    lnA_hi=(1-th_lo)*ln_n0_hi
    print("lnA upper (mine)",float(lnA_hi),"theirs",float(Q(R['absorption']['logA_upper'])))
    for label,lnN in (("ln N = 1e12",(Q(10**12),Q(10**12))),("N = 2^(1e12)",(10**12*ln(2)[0],10**12*ln(2)[1]))):
        lc=lnq(up(c+lnN[1]))[1]
        margin=(t-th_hi)*lnN[0]-lnA_hi-p*lc
        need(margin>0 and (t-th_hi)>p/(c+lnN[0]),label)
        print(label,"margin lower",float(margin))
    # outer rows
    op={k:Q(v) for k,v in R['outer_parameters'].items()}
    e,q,a_,be,ka=op['epsilon'],op['q'],op['a'],op['beta'],op['kappa']
    print(sorted(op))
    rows={"main_transform":e*q,"global_coordinate_router":a_,"fused_gaussian":1-e+q*be,"group_bit_router":1-e+a_*be,
          "group_scans":1-e+be,"polynomial_products":e,"microbox_face_corrections":1-(e+be+48-128+2)}
    for k,v in rows.items(): need(v>ka,k)
    mn=min(rows,key=rows.get); print("binding",mn,rows[mn]-ka, rows[mn]-ka==Q(R['minimum_outer_margin_above_kappa']))
    need(op['complex_uniform_saving']==us and op['kappa']==ka,"outer point binds uniform saving and kappa")
    d=op['d']; need(op['tested_saving']==ka+7*d and us==ka+6*d and op['b']==ka+5*d and a_==ka+4*d and q==ka+3*d and e==1-d and be==1-3*d,"parameter schedule kappa + k d")
    print("schedule ok")

    # finite envelope (#4535 RESULT finite_envelope): height, class-count and episode arithmetic
    fe = R["finite_envelope"]
    W0, P0, M_, g_ = 10928, 64620, fe["height_base"], fe["height_multiplier"]
    need((fe["raw_productive_fields"], fe["raw_paid_jobs"], fe["raw_rank_surplus"]) == (W0, P0, 752), "raw counts")
    logN = 10 ** 12                                         # N = 2^(10^12)
    # ell = floor(log_M floor(N/145)); floor(N/145) lies in [2^(logN-8), 2^logN) since 145 < 2^8
    ell_hi = logN // 10                                     # M = 1024 = 2^10
    need(M_ == 1024 and g_ * ell_hi <= fe["G_depth_upper"] == 2 * 10 ** 11, "height G = g * ell <= 2e11")
    need(W0 < 2 ** 14 and W0 + P0 + 1 < 2 ** 17, "W0 < 2^14 and W0 + P0 + 1 < 2^17")
    need(17 * fe["G_depth_upper"] + 31 == fe["log2_C_N_strict_upper"] == 3400000000031, "C_N < 2^(17 G + 31)")
    need(fe["full_call_centre_episodes_per_raw_unit"] == 18 * 8 and fe["thin_query_episodes_per_raw_unit"] == 15 * 112,
         "episodes 144 = 18 * 8 and 1680 = 15 * 112")
    print(json.dumps({"status": "PASS_PR4535_ARITHMETIC_CHECK", "kappa": str(ka), "uniform_saving": str(us),
                      "mirror_worst": f"{float(worst):.6f}", "binding_margin": str(rows[mn] - ka),
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
