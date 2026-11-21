# EXTRATHIN et7: EXACT check of the TRIANGLE witness (e = 1, k = 3g): three all-main hubs on class pairs + d1 leaves.
# Verifies every row of the et6 pattern LP (count, MAINS, DEEP, SET-RC2 for ALL partner sets T of every size, leaf) in integer
# arithmetic, then evaluates chat = 104 F / k with mpmath (60 digits).  A feasible primal point => LP value >= chat.
import itertools, sys
from math import comb
from fractions import Fraction as Fr
from mpmath import mp, mpf
mp.dps=60; s=mpf('0.99'); pw=lambda x: mpf(x)**s
def check(g, X=None):
    m=3; k=3*g; e=1
    inc=[[0,1,1],[1,0,1],[1,1,0]]
    hubs=[(g,g,0),(g,0,g),(0,g,g)]
    unit=lambda j: tuple(1 if t==j else 0 for t in range(m))
    X=X or k-1
    comps=[c for c in itertools.product(range(g+1),repeat=m) if 1<=sum(c)<=X]
    worst=None
    for i in range(m):
        for c in comps:
            if c[i]>g-1: continue
            nz=[j for j in range(m) if c[j]>0]
            rk=1 if (len(nz)==1 and nz[0]!=i and inc[i][nz[0]]) else 2
            rhs=rk*g*1
            for j in range(m): rhs*=comb(g-(1 if j==i else 0),c[j])
            for l in range(2,k+1):
                lhs=0
                for a in hubs:
                    D=sum(a)
                    for jj in range(m):
                        if a[jj]==0: continue
                        p=unit(jj)        # singleton piece at a stage of class jj
                        if jj!=i: continue
                        av=1; av2=1
                        for t in range(m): av*=comb(g-p[t],c[t]); av2*=comb(g-a[t],c[t])
                        cnt=a[jj]        # stages of class i in the mask, each a singleton
                        if D>=l: lhs+=av*cnt          # |P|=1<l
                        else: lhs+=(av-av2)*cnt
                if lhs<rhs: return ('VIOLATED',i,c,l,lhs,rhs)
                sl=Fr(lhs,rhs)
                if worst is None or sl<worst[0]: worst=(sl,i,c,l)
    # global rows
    hub_sing=sum(sum(a) for a in hubs)              # 6g = 2k deep singletons
    assert hub_sing>=2*k                             # MAINS and DEEP (leaves only add to MAINS)
    d1=max(2*k-1-len(hubs), -(-k*(2*k-6)//(k-1)))  # count n>=2k-1 and leaf d1 <= k*T, T = n-2k+2+e
    n=len(hubs)+d1; T=n-2*k+2+e
    assert n>=2*k-1 and d1<=k*T and T>=0
    vhub=pw(8*2*g+1)-2*g*pw(8); v1=pw(9)-pw(8)
    F=2*k-2-e-len(hubs)*(1-vhub)-d1*(1-v1)
    return ('OK',k,d1,T,mp.nstr(104*F/k,15),'tightest set row',worst)
for g in map(int,sys.argv[1:]): print(check(g),flush=True)
