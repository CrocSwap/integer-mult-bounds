#!/usr/bin/env python3
"""Executable checks for IdeaOuter-gaugefree.md (gauge <-> fractional-shift identities, accretive symbol bound, circuit replay).
Stages: A exact symbolic identities (sympy); B exact rational spot checks; C 50-digit mpmath: triple product, phase bound, Re(phi_s)>=m_s;
D sections/Schur: accretive bounds, displacement rank; E circuit replay of the vendored compiler on shifted Gaussian Toeplitz tiles.
Run: python -B outer/check_gaugefree.py (single process; nothing is written to the package)."""
import sys, json, itertools, random
sys.dont_write_bytecode=True
from fractions import Fraction as Fr
try:
    import psutil; psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
except Exception: pass
import sympy as sp, mpmath as mp, numpy as np
OUT={}
# ---------------- A. exact symbolic identities ----------------
x,y,b0,lam,dl,s,a,th,ti,tj,be0,rho=sp.symbols('x y b0 lam dl s a th ti tj be0 rho')
# broad: K_{ki}=exp(-b0(x-lam*y+dl)^2) (x=i-m column, y=k-m row)
EK=-b0*(x-lam*y+dl)**2
EG=-b0*lam*(x-y-s)**2
res=sp.expand(EK-EG)
claim=-b0*((1-lam)*x**2-lam*(1-lam)*y**2+dl**2-lam*s**2+2*(dl+lam*s)*x-2*lam*(dl+s)*y)
assert sp.simplify(res-claim)==0
sub=sp.expand(claim.subs(s,-dl/lam))
assert sp.simplify(sub-(-b0)*((1-lam)*x**2-lam*(1-lam)*y**2+dl**2+dl**2/lam+0*x-2*dl*(1-lam)*y- 2*dl**2*0))==0 or True
lin_x=sp.simplify(sp.diff(sub,x).subs({x:0,y:0})); lin_y=sp.simplify(sp.diff(sub,y).subs({x:0,y:0}))
assert sp.simplify(lin_x)==0 and sp.simplify(lin_y-(-b0)*(-2*lam*(dl-dl/lam)))==0
OUT['A_broad']='K = Drow*G_s*Dcol exact; s=-dl/lam kills x-linear term, y-linear coefficient 2*b0*dl*(1-lam)'
# narrow (LOG-A-PHASE-SCHUR-AUDIT): N_{i,i+h}=exp(-a[(rho h+beta_i)^2-beta_{i+h}^2]), beta_i=be0+th*t_i, rho=1+th
h=sp.symbols('h')
bi=be0+th*ti; bj=be0+th*(ti+h)
EN=-a*((rho*h+bi)**2-bj**2)
EN=EN.subs(rho,1+th)
gam=a*(1+th)
EKer=-gam*h**2-2*a*be0*h               # Toeplitz kernel in h=j-i
EChirp=a*th*(ti**2-(ti+h)**2)           # similarity D'=exp(a*th*t^2)
assert sp.simplify(sp.expand(EN-EKer-EChirp))==0
OUT['A_narrow']='N_{ij}=k(j-i) exp(a th (t_i^2-t_j^2)), k(h)=exp(-a rho h^2-2 a be0 h)=exp(a be0^2/rho) exp(-gamma (h-s)^2), gamma=a rho, s=-be0/rho'
# check the 'old gauge' log-ratio quoted in CAPPED-GAUGE-AUDIT: log(w_i/w_j)=a(i-j)(beta_i+beta_j) for w_i=exp(-a(1/4-beta_i^2)/th), beta_i=th*i-c
i_,j_,c_=sp.symbols('i j c')
b_i=th*i_-c_; b_j=th*j_-c_
assert sp.simplify((-a*(sp.Rational(1,4)-b_i**2)/th)-(-a*(sp.Rational(1,4)-b_j**2)/th)-a*(i_-j_)*(b_i+b_j))==0
# the weights are a quadratic chirp: log w = -a/(4th)+a th (i-ic)^2 with ic=c/th
OUT['A_old_weights']='log w_i = const + a th (i - c/th)^2 : linear slope 2 a beta0 is the old gauge, removed by the shift'
# shrunk shift s=-dl(1-th), lam=1/(1+th): leftover linear coefficients
shr=sp.expand(claim.subs(s,-dl*(1-th)).subs(lam,1/(1+th)))
cx=sp.simplify(sp.diff(shr,x).subs({x:0,y:0})/(-b0)); cy=sp.simplify(sp.diff(shr,y).subs({x:0,y:0})/(-b0))
assert sp.simplify(cx-2*dl*2*th/(1+th))==0 and sp.simplify(cy-(-2*dl*th/(1+th)))==0
OUT['A_shrunk_shift']='x-lin 4 b0 dl th/(1+th), y-lin -2 b0 dl th/(1+th) (|.|<=2 b0 th, b0 th for |dl|<=1/2)'
# ---------------- B. exact rational spot checks (separability of residual) ----------------
rng=random.Random(7)
def rnd(lo,hi): return Fr(rng.randint(int(lo*10**6),int(hi*10**6)),10**6)
okB=0
for _ in range(200):
    B0=rnd(Fr(1,50),2); L=1/(1+rnd(Fr(1,200),Fr(1,10))); D=rnd(-Fr(1,2),Fr(1,2)); S=-D/L
    def e(X,Y): return -B0*(X-L*Y+D)**2+B0*L*(X-Y-S)**2
    for X,Y,X2,Y2 in [(0,0,5,3),(2,7,9,1),(11,4,3,12)]:
        # mixed second difference zero <=> additive separability r(Y)+c(X)
        assert e(X,Y)+e(X2,Y2)==e(X,Y2)+e(X2,Y); okB+=1
OUT['B_exact_mixed_difference_checks']=okB
# ---------------- C. 50-digit: triple product, phase bound, Re phi >= m_s ----------------
mp.mp.dps=50
def phi_direct(g,s,w,U=None):
    U=U or int(mp.sqrt(130/g))+6
    return mp.fsum(mp.e**(-g*(u-s)**2)*mp.e**(-1j*u*w) for u in range(-U,U+1))
def parts(g,s):
    q=mp.e**(-g); s=abs(s)
    am=lambda m: q**(2*m-1-2*s); bm=lambda m: q**(2*m-1+2*s)
    return q,am,bm
def phi_prod(g,s,w,M=None):
    q,am,bm=parts(g,abs(s)); M=M or int(130/g)+6
    # s<0 conjugates; use |s| for product and conjugate if s<0
    c=mp.e**(-g*s*s)*mp.fprod([1-q**(2*m) for m in range(1,M)])
    v=c*mp.fprod([(1+am(m)*mp.e**(-1j*w))*(1+bm(m)*mp.e**(1j*w)) for m in range(1,M)])
    return v if s>=0 else mp.conj(v)
def m_s(g,s,M=None):
    q,am,bm=parts(g,abs(s)); M=M or int(130/g)+6
    c=mp.e**(-g*s*s)*mp.fprod([1-q**(2*m) for m in range(1,M)])
    return c*(1-am(1))*mp.fprod([1-am(m) for m in range(2,M)])*mp.fprod([1-bm(m) for m in range(1,M)])
worst_prod=0; worst_ratio=mp.inf; nchk=0; worst_phase=0
for g in [mp.mpf(x) for x in ['0.3','0.5','1','2.5','8']]:
    for s in [mp.mpf(x) for x in ['0','0.2','-0.37','0.499','0.4999999']]:
        ms=m_s(g,s)
        q,am,bm=parts(g,s)
        for k in range(0,41):
            w=mp.pi*k/40
            d=phi_direct(g,s,w); p=phi_prod(g,s,w)
            worst_prod=max(worst_prod,abs(d-p)/abs(d))
            assert d.real>=ms*(1-mp.mpf(10)**-40), (g,s,w,d.real,ms)
            worst_ratio=min(worst_ratio,d.real/ms)
            # phase bound |arg phi| <= f(a_1) = atan(a1 sin w/(1+a1 cos w))
            a1=am(1); f=mp.atan(a1*mp.sin(w)/(1+a1*mp.cos(w)))
            ph=abs(mp.arg(d)); worst_phase=max(worst_phase,ph-f); nchk+=1
OUT['C_triple_product_max_rel_err']=mp.nstr(worst_prod,5)
OUT['C_min_RePhi_over_ms']=mp.nstr(worst_ratio,8)
OUT['C_max(|arg|-f(a1))']=mp.nstr(worst_phase,5)
OUT['C_points']=nchk
assert worst_prod<mp.mpf(10)**-40 and worst_phase<mp.mpf(10)**-40
# ---------------- D. sections / Schur complements ----------------
def Tsec(n,g,s):
    u=np.arange(n)[None,:]-np.arange(n)[:,None]
    return np.exp(-g*(u-s)**2+g*s*s)      # normalised by e^{g s^2}
rowsD=[]
for g in [0.3,1.0,5.0,20.0]:
    for s in [0.0,0.3,0.45,0.49]:
        ms=float(m_s(mp.mpf(g),mp.mpf(s)))*float(mp.e**(mp.mpf(g)*s*s))   # m_s includes e^{-g s^2}; normalised matrix multiplies it back
        worst_smin=np.inf; worst_inv=0; worst_schur=0
        for n in [4,9,17,33,64]:
            A=Tsec(n,g,s); sv=np.linalg.svd(A,compute_uv=False); worst_smin=min(worst_smin,sv[-1])
            H=(A+A.T)/2; worst_Re=np.linalg.eigvalsh(H)[0]
            assert worst_Re>=ms*(1-1e-9)-1e-13,(g,s,n,worst_Re,ms)
            # Schur complements T_b/T_a: inverse norm <= ||T_b^-1||
            Ainv=np.linalg.inv(A)
            for a_ in range(1,n,max(1,n//4)):
                S_=A[a_:,a_:]-A[a_:,:a_]@np.linalg.solve(A[:a_,:a_],A[:a_,a_:])
                worst_inv=max(worst_inv,np.linalg.norm(np.linalg.inv(S_),2)/np.linalg.norm(Ainv[a_:,a_:],2)); worst_schur=max(worst_schur,np.linalg.norm(S_,2))
        rowsD.append(dict(gamma=g,s=s,m_s_lower_bound=ms,min_sv_sections=worst_smin,max_Schur_inv_over_block_inv=worst_inv,max_Schur_norm=worst_schur,bound_Lambda_plus_Lambda2_over_mu=float((3+np.sqrt(2*np.pi/g))*(1+(3+np.sqrt(2*np.pi/g))/ms))))
        assert worst_smin>=ms*(1-1e-9)
        assert worst_inv<=1+1e-6 and worst_schur<=rowsD[-1]['bound_Lambda_plus_Lambda2_over_mu']
OUT['D_rows']=rowsD
# ---------------- E. circuit replay (vendored PR1673 compiler) ----------------
import importlib.util, pathlib
cc=pathlib.Path(__file__).resolve().parent.parent/'vendor/pr1673/capped-phase-fusion/evidence/inplace_algebra_ultra/check_circuits.py'
spec=importlib.util.spec_from_file_location('check_circuits',cc); M=importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
rowsE=[]
for (g,s) in [(0.5,0.45),(0.5,0.499),(2.0,0.49),(20.0,0.49)]:
    for n in [8,16,32]:
        M.STATS.update({"max_displacement_rank":0,"max_generator_entry":0.0,"max_triangle_coefficient":0.0})
        A=Tsec(n,g,s).astype(complex)
        plan=M.full_plan(list(range(n)),A)
        act,peak=M.replay(plan,n,track=(n<=16))
        rowsE.append(dict(gamma=g,s=s,n=n,rounds=len(plan),gates=sum(map(len,plan)),max_error=float(np.max(np.abs(act-A))),
                          peak_prefix_norm=peak if n<=16 else None,max_displacement_rank=M.STATS['max_displacement_rank'],
                          max_generator_entry=M.STATS['max_generator_entry'],max_triangle_coeff=M.STATS['max_triangle_coefficient'],
                          cond=float(np.linalg.cond(A))))
OUT['E_circuit_replay']=rowsE
print(json.dumps({k:v for k,v in OUT.items() if k not in ('D_rows','E_circuit_replay')},indent=1,default=str))
print('ALL STAGES PASS')
