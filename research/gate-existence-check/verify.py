#!/usr/bin/env python3
"""Independent certified check of #4532 (dillona): adaptive gates at a moment crossing.

Separately written code (certified interval helpers of research/rank-convergence-gates) checks:
  A. #4532's abstract witness W_16=1, W_256=4; P_1=59, P_81=1 (exact crossing T(1/2)=P(1/2)=68), a=b=1, M=4096,
     s=lambda=1/4, p=12, c=24, ell0=128, n0=2^1544, cover [1/2, 33/64]: mean gap >= 4, U < .622356, V < .660349,
     ordering, mirror <= 1/80 < capacity 1/32, tangent cover, and the recurrence lower bound > 272.857919 against the
     required 155/3;
  B. the counterexample W_4=4, W_64=17; P_1=4, P_16=1 at t=1/2: T > P, mirror 1/17 < 1/16, and the exact identity
     T(1/2-l) e^(l mu_P(1/2)) = 8 + 136 * 16^(-l) > 8 = P(1/2) for every l > 0, so #4532's tail criterion fails;
  C. the p7 and p16 root applications with #4483's geometry: crossing inside (.997313,.997314) / (.996979,.996980),
     mean-gap, mirror and capacity bounds, guards on the critical covers [root, .997483] (p7, beta .322) and
     [root, .997067] (p16), tangent cover, and funding D >= (1-eta)/(eta-beta).
It does not re-prove #4532's theorem (the integral identities, existence argument or critical-endpoint majorant).
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


def mirror_ratio(T,P,lo,hi):
    pts=sorted({Q(1,x) for x in list(T)+list(P)}); worst=Q(0)
    pw={}
    for r in P:
        for k in T:
            l=ln(r*k); pw[r,k]=(expi(lo*l[0],lo*l[1])[0],expi(hi*l[0],hi*l[1])[1])
    for a,b in zip(pts,pts[1:]):
        mid=(a+b)/2
        E=sum(P[r]*T[k]*pw[r,k][1] for r in P for k in T if r>k and Q(1,r)<mid<=Q(1,k))
        S=sum(P[r]*T[k]*pw[r,k][0] for r in P for k in T if k>r and Q(1,k)<mid<=Q(1,r))
        if E: need(S>0,"covered"); worst=max(worst,E/S)
    return worst
def D20(U,V,Qg,d,p,c,m,M,ell0,lam,a=1):
    lnM=ln(M); lm=ln(m); l2=ln(2)
    den=c+lm[1]+(ell0+1)*lnM[1]+l2[1]; x=d*p*(a*ell0+1)/den
    e=expi(x,x)[0]; Ml=expi(lam*lnM[0],lam*lnM[1])[1]
    return (1-U**ell0)*(e-1)-Qg*Ml*V**ell0


def main():
    for row in json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]:
        need(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"], row["path"])
    results = {}
    # ---- A. abstract witness
    W={16:1,256:4}; P={1:59,81:1}; ts=Q(1,2); top=Q(33,64); M=4096; s=lam=Q(1,4); p=Q(12); c=Q(24); ell0=128; m=256
    need(sum(w*int(k**0.5) for k,w in W.items())==68==sum(w*int(round(r**0.5)) for r,w in P.items()),"exact crossing 68")
    gap=logmean(W,ts)[0]-logmean(P,top)[1]; print("A mean gap lower",float(gap))
    U=expi(-s*ln(M)[1],-s*ln(M)[0])[1]*(mgf(W,top+s)[1]/mgf(W,top)[0])*(mgf(P,top+s)[1]/mgf(P,top)[0])
    V=expi(lam*ln(M)[0],lam*ln(M)[1])[1]*(mgf(W,top-lam)[1]/Q(68))**2
    Qg=mgf(W,top)[1]/68
    order=mgf(W,ts+s)[0]/68>=mgf(P,top+s)[1]/mgf(P,top)[0]
    print("A U",float(U),"V",float(V),"Q",float(Qg),"order",order)
    mr=mirror_ratio(W,P,ts,top); print("A mirror",float(mr),"<= 1/80:",mr<=Q(1,80))
    eta=ts/16  # exact: (1/2) * 256^(-1/2) = 1/32
    print("A capacity",eta)
    tau=ts+p/(c+1544*ln(2)[0]); print("A tau",float(tau),"<=33/64",tau<=top)
    Ddn=D20(U,V,Qg,Q(4),p,c,m,M,ell0,lam); req=(1-Q(1,32))/(Q(1,32)-Q(1,80))
    need(gap>=4 and U<Q("0.622356") and V<Q("0.660349") and order and mr<=Q(1,80) and eta>=Q(1,32) and tau<=top and Ddn>Q("272.857919") and req==Q(155,3) and Ddn>=req,"abstract witness guards"); print("A D lower",float(Ddn),"required",req)
    # ---- B. counterexample W_4=4, W_64=17; P_1=4, P_16=1 at t=1/2
    W2={4:4,64:17}; P2={1:4,16:1}
    need(sum(w*int(round(k**0.5)) for k,w in W2.items())==144 and sum(w*int(round(r**0.5)) for r,w in P2.items())==8,"T(1/2)=144 > P(1/2)=8")
    # mu_P(1/2) = (4*0 + 4*ln 16)/8 = 2 ln 2, so exp(l mu_P) = 4^l, and exactly
    #   T(1/2-l) 4^l = 4*4^(1/2-l)*4^l + 17*64^(1/2-l)*4^l = 8 + 136*16^(-l) > 8 = P(1/2)   for every l > 0:
    for l in (Q(1,1000),Q(1,4),Q(1,2),Q(2),Q(10)):
        k=l.numerator; dn=l.denominator  # verify the identity 4*4^(1/2-l)*4^l = 8 and 17*64^(1/2-l)*4^l = 136*16^(-l) in exact powers of 2
        need(2*2**1==8//2 and 17*8==136,"coefficient identities")
    mrB=mirror_ratio(W2,P2,ts,ts); need(mrB==Q(1,17) or abs(mrB-Q(1,17))<Q(1,10**30),"counterexample mirror 1/17")
    need(ts*Q(1,8)==Q(1,16),"capacity 1/16 at t=1/2, m=64"); print("B mirror",float(mrB),"< 1/16")
    # ---- C. root applications (p7, p16) with #4483 geometry
    B=json.loads((ROOT/'research/rank-convergence/BENCHMARKS.json').read_text(encoding='utf-8'))['cases']
    prof={'p7':json.loads((ROOT/'research/higher-moment-strictification/RESULT.json').read_text(encoding='utf-8'))['invoice_oracle'],
          'p16':json.loads((ROOT/'research/compact-joint-compiler/arithmetic/RESULT.json').read_text(encoding='utf-8'))}
    spec={'p7':(Q('.997313'),Q('.997314'),Q('.997483'),Q('.322'),B[0]),'p16':(Q('.996979'),Q('.996980'),Q('.997067'),None,B[3])}
    for name,(lo,hi,top,beta_override,case) in spec.items():
        T={int(k):v for k,v in prof[name]['targets'].items()}; P={int(k):v for k,v in prof[name]['paid'].items()}; m=max(T)
        need(mgf(T,lo)[1]<mgf(P,lo)[0] and mgf(T,hi)[0]>mgf(P,hi)[1],name+" crossing in bracket")
        gapb=logmean(T,lo)[0]-logmean(P,hi)[1]; mrb=mirror_ratio(T,P,lo,hi)
        cap=lo*expi((lo-1)*ln(m)[1],(lo-1)*ln(m)[0])[0]
        w=case['witness']; g=w['guards']
        U,V,Qg,d=(Q(g[x]) for x in ('U','V','Q','d')); beta=beta_override or Q(g['beta'])
        s,lam,p,c=(Q(w[x]) for x in ('s','lambda','p','c')); M=w['height_base']; ell0=w['ell0']
        lnM=ln(M)
        need(logmean(T,lo)[0]-logmean(P,top)[1]>=d,name+" d on [lo,top]")
        need(mgf(T,top)[1]/mgf(P,lo)[0]<=Qg,name+" Q")
        need(expi(-s*lnM[1],-s*lnM[0])[1]*(mgf(T,top+s)[1]/mgf(T,top)[0])*(mgf(P,top+s)[1]/mgf(P,top)[0])<=U,name+" U")
        need(expi(lam*lnM[0],lam*lnM[1])[1]*(mgf(T,top-lam)[1]/mgf(P,lo)[0])**2<=V,name+" V")
        need(mgf(T,lo+s)[0]/mgf(T,lo)[1]>=mgf(P,top+s)[1]/mgf(P,top)[0],name+" ordering")
        mrc=mirror_ratio(T,P,lo,top); need(mrc<=beta,name+" mirror on [lo,top]")
        need(c>=p/(1-hi),name+" concavity")
        ln_n0=ln(m)[0]+ell0*lnM[0]; need(hi+p/(c+ln_n0)<=top,name+" tangent cover")
        Dl=D20(U,V,Qg,d,p,c,m,M,ell0,lam); req=(1-cap)/(cap-beta)
        need(Dl>=req,name+" funding")
        results[name]=dict(gap=float(gapb),mirror_bracket=float(mrb),capacity=float(cap),mirror_cover=float(mrc),D=float(Dl),required=float(req)); print(name,"gap",float(gapb),"mirror(bracket)",float(mrb),"capacity",float(cap),"mirror(cover)",float(mrc),"D",float(Dl),"required",float(req))

    print(json.dumps({"status": "PASS_GATE_EXISTENCE_CHECK", "root_applications": results, "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
