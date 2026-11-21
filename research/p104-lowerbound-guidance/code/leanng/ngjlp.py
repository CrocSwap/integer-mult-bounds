#!/usr/bin/env python3
"""WALLCORE jlp2.py (own code): joint IP v2 over node types tau=(a,b,gat,dep,A,Dd), A=D_anc, Dd=D_desc (capped at 9).
All constraints [P] for P104 NetWs in class HALF3 (Q2-gauge e,e'<=1; Phi rows and Lambda rows 2-adic spread <=1):
 Q2   104 <= sum N1(d) + d*min(9-a, A)                       (QP §2 + ancestor-span refinement)
 PHI  104 <= sum_gat N1(min(a, 9-b, d+Dd))                   (ADICWALL graded bound on Phi + forward sweep)
 LAM  104 <= sum_dep N1(min(9-b, a, d+A))  [a+A capped 9]     (graded bound on Lambda + reverse sweep)
 CAP  gather/deposit label coverage with exact P104 N(d); CUT LR §3 mixed cuts, rank>=8, l=1..9
 ANC  every used type has d+A+Dd <= D (ancestors/descendants disjoint): enforced by restricting types to d+A+Dd<=D0
 REG  >=9 gatherers or >=9 depositors.
Smallest D0 with restricted min D <= D0 is the bound. Integer optimum rechecked exactly."""
import sys
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
KPACK=int(__import__('os').environ.get('KPACK','1'))
N={1:1,2:2,3:4,4:8,5:12,6:20,7:36,8:60,9:104}
N1=lambda d: d*(d+1)//2
use=set(sys.argv[1].split(',')) if len(sys.argv)>1 else {'Q2','PHI','LAM','CAP','CUT','PAIR','L2','KC','SOLE','REL','FWD','MIR'}
# NG flags: iota=1 iff node receives a relay (iota=0 => no ancestors, A=0); o=1 iff it sends one (o=0 => Dd=0)  [sound relaxation]
TT=[(a,b,g,p,A,Dd,io,o) for a in range(1,10) for b in range(a) for g in (0,1) for p in (0,1) for A in range(10) for Dd in range(10) for io in (0,1) for o in (0,1) if (io==1 or A==0) and (o==1 or Dd==0)]
def q2(t): a,b,g,p,A,Dd,io,o=t; d=a-b; return N1(d)+d*min(9-a,A)
def phi(t): a,b,g,p,A,Dd,io,o=t; d=a-b; return N1(min(a,9-b,d+Dd)) if g else 0
def lam(t): a,b,g,p,A,Dd,io,o=t; d=a-b; return N1(min(9-b,a+A if a+A<9 else 9,d+A)) if p else 0
def solve(D0,reg):
    T=[t for t in TT if (t[0]-t[1])+t[4]+t[5]<=D0]
    c=np.array([t[0]-t[1] for t in T],float); A=[];lo=[]
    if 'Q2' in use: A.append([q2(t) for t in T]); lo.append(104)
    if 'L2' in use:  # predecessor-attributed mixed monomials: N1(d)+[Dd>=1]*b*(min(9,a+A)-b)   [P sketch, E=1 gauge]
        A.append([N1(t[0]-t[1])+(t[1]*(min(9,t[0]+t[4])-t[1]) if t[5]>=1 else 0) for t in T]); lo.append(104)
    if 'FWD' in use:  # NG forward: n <= sum [C(d+1,2) + iota d (h-a)]   [P, HALF-NET]
        A.append([N1(t[0]-t[1])+(t[6]*(t[0]-t[1])*(9-t[0])) for t in T]); lo.append(104)
    if 'MIR' in use:  # NG mirror: n <= sum [C(d+1,2) + o d b]
        A.append([N1(t[0]-t[1])+(t[7]*(t[0]-t[1])*t[1]) for t in T]); lo.append(104)
    if 'PHI' in use: A.append([phi(t) for t in T]); lo.append(104)
    if 'LAM' in use: A.append([lam(t) for t in T]); lo.append(104)
    if 'CAP' in use:
        A.append([N[t[0]] if t[2] else 0 for t in T]); lo.append(104)
        A.append([N[9-t[1]] if t[3] else 0 for t in T]); lo.append(104)
    if 'CUT' in use:
        for l in range(1,10):
            A.append([1 if (t[1]<l<=t[0]) or (t[2] and t[0]<l) or (t[3] and t[1]>=l) else 0 for t in T]); lo.append(8)
    A.append([1 if t[reg] else 0 for t in T]); lo.append(9)
    if 'SOLE' in use:  # CORE-BUILD SOLE law: sole-gathered ports at g pairwise even, <= dim a_g; shared ports covered twice  [P]
        A.append([(N[t[0]]+min(t[0],N[t[0]])) if t[2] else 0 for t in T]); lo.append(208)
        A.append([(N[9-t[1]]+min(9-t[1],N[9-t[1]])) if t[3] else 0 for t in T]); lo.append(208)  # mirror: sole-deposited readers
    if 'KC' in use:  # clique-cut: omega_odd(P104 minus Del_l labels) <= |C_l|; relaxed |C_l|/c + Del_l/kappa_c >= 1, kappa_c >= K(9-c)   [P]
        for l in range(1,10):
            for cc in range(2,9):
                kap=min(104,KPACK*(9-cc))
                A.append([(kap if (t[1]<l<=t[0]) else 0)+cc*((N[t[0]] if (t[2] and t[0]<l) else 0)+(N[9-t[1]] if (t[3] and t[1]>=l) else 0)) for t in T]); lo.append(cc*kap)
    if 'PAIR' in use:  # sum_k d_k A_k <= #weighted ancestor pairs <= (D^2 - sum d^2)/2, same for Dd   [P]
        for j in (4,5):
            A.append([-(2*(t[0]-t[1])*t[j]+(t[0]-t[1])**2) for t in T]); lo.append(-D0*D0)
    nT=len(T); extra=[]
    if 'REL' in use:
        # [P] REL: every ancestor of k reaches k through a direct predecessor j with dim b_j <= dim a_k = alpha.
        # If no FUNNEL node (dim b <= alpha < dim a) exists, every ancestor of k has dim b <= alpha (else the path into S_alpha
        # needs a node of S_alpha accepting dim b > alpha, i.e. a funnel). Then A_k <= D(S_alpha) - d_k.
        wv={}; zv={}
        for al in range(1,9):
            zv[al]=nT+len(extra); extra.append(('z',al))
            for Av in range(1,10):
                wv[(al,Av)]=nT+len(extra); extra.append(('w',al,Av))
        nv=nT+len(extra); A=[row+[0]*len(extra) for row in A]
        for al in range(1,9):
            row=[0]*nv
            for i,t in enumerate(T):
                if t[1]<=al<t[0]: row[i]=1
            row[zv[al]]=-1; A.append(row); lo.append(0)            # funnel count >= z
            for Av in range(1,10):
                row=[0]*nv
                for i,t in enumerate(T):
                    if t[1]<=al: row[i]=t[0]-t[1]
                row[zv[al]]=300; row[wv[(al,Av)]]=-(Av+1); A.append(row); lo.append(0)   # D(S_al)+300z >= (A+1)w
                row=[0]*nv
                for i,t in enumerate(T):
                    if t[0]==al and t[4]==Av: row[i]=-1
                row[wv[(al,Av)]]=300; A.append(row); lo.append(0)  # x_tau <= 300 w
        c=np.concatenate([c,np.zeros(len(extra))])
    nv=nT+len(extra)
    ub=np.array([300]*nT+[1]*len(extra),float)
    r=milp(c,constraints=LinearConstraint(np.array(A,float),lo,np.inf),integrality=np.ones(nv),bounds=Bounds(0,ub))
    if r.x is None: return None,None
    x=np.round(r.x).astype(int)
    for row,l0 in zip(A,lo): assert sum(int(v)*int(xi) for v,xi in zip(row,x))>=l0
    return int(sum((t[0]-t[1])*xi for t,xi in zip(T,x[:nT]))), [(t,int(xi)) for t,xi in zip(T,x[:nT]) if xi]
for reg,name in ((2,'>=9 gat'),(3,'>=9 dep')):
    for D0 in range(1,200):
        D,prof=solve(D0,reg)
        if D is not None and D<=D0: break
    print(f'[{",".join(sorted(use))}] {name}: bound D >= {D} (found at D0={D0})',flush=True)
    for t,xi in prof: print(f'   {xi} x (a={t[0]},b={t[1]},gat={t[2]},dep={t[3]},Danc={t[4]},Ddesc={t[5]},iota={t[6]},o={t[7]}) q2={q2(t)} phi={phi(t)} lam={lam(t)}')
