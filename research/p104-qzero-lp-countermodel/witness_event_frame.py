#!/usr/bin/env python3
"""Construct a CallerEv event-data HP witness, not a signed-product word.

The code directly checks EvData, Match, hG, both full row ranks, pair
inequalities and the exact counts over the rationals. It distributes the
two-stage roles on a path and leaves one stage isolated.
"""
from collections import Counter
from verify_independent import BAR, check_primal, decimal_bound

def check(k, corrupt=False):
    assert k>=3
    n=2*k-2
    M=[frozenset(range(k)),frozenset(range(k))]+[frozenset((e,e+1)) for e in range(k-2) for j in range(2)]
    events=[(frozenset((s,)),j) for s in range(k) for j in range(2)] + [(M[r],r) for r in range(2,n)]
    # Pair-event x has one hub coordinate and one low-role coordinate.
    x=[{r:1} if len(S)==1 else {r:1,(r-2)%2:1} for S,r in events]
    y=[]
    for S,r in events:
        if len(S)>1: y.append({r:1})
        else:
            s=next(iter(S)); y.append({r:1,**{i:-1 for i in range(2,n) if s in M[i] and (i-2)%2==r}})
    if corrupt: x[2*k]={0:1}
    def bh(r,s,a):
        if s not in M[r]: return 0
        return int(r==a) if r<2 else -int((r-2)%2==a)
    def ah(r,s,a): return bh(r,s,a)
    # bh, ah respect M, and off-diagonal Ghat is either I_2 or 2 I_2.
    for s in range(k):
        for r in range(n):
            if s not in M[r]:
                assert all(bh(r,s,a)==ah(r,s,a)==0 for a in range(2))
        for t in range(k):
            if s!=t:
                for a in range(2):
                    for b in range(2):
                        value=sum(bh(r,s,a)*ah(r,t,b) for r in range(n))
                        assert value==int(a==b)*(2 if frozenset((s,t)) in M[2:] else 1)
        # Every role's declared mask is its exact A/B support.
        for r in range(n):
            assert (s in M[r])==any(bh(r,s,a)!=0 or ah(r,s,a)!=0 for a in range(2))
    # Full row ranks A and B: for each coordinate, the selected minor has
    # one hub row and k-2 edge rows. The isolated-stage column isolates the
    # hub; the remaining (k-2)x(k-2) edge block is upper triangular with -1
    # diagonal, so determinant is +/-1. A=B.
    for a in range(2):
        assert bh(a,k-1,a)==1
        for e in range(k-2):
            r=2+2*e+a
            assert bh(r,k-1,a)==0
            assert bh(r,e,a)==-1
            for col in range(e): assert bh(r,col,a)==0
    # With the source's sgStage = I + A_s B_s^T and A=B, Sylvester's
    # determinant identity gives det(sgStage) = det(I_2+A_s^T A_s).
    # This product is >1, while det(-I_n)=1 since n is even. Consequently
    # this event-data witness CANNOT be a P=-I signed-product frame.
    prod_det=1
    for s in range(k):
        gram=[[sum(ah(r,s,a)*bh(r,s,b) for r in range(n)) for b in range(2)] for a in range(2)]
        assert gram[0][1]==gram[1][0]==0 and gram[0][0]==gram[1][1]>=1
        prod_det*=(1+gram[0][0])*(1+gram[1][1])
    assert prod_det==324*16**(k-3) and prod_det>1 and n%2==0
    for i,(S,role) in enumerate(events):
        for r in x[i]: assert S.issubset(M[r]),'x_supp'
        if len(S)>=2:
            for s in S:
                for a in range(2): assert sum(v*bh(r,s,a) for r,v in x[i].items())==0,'x_ker'
        for j,(T,_) in enumerate(events):
            if S&T: assert sum(v*x[j].get(r,0) for r,v in y[i].items())==int(i==j),'biorth'
    # Matching is the event with the same role, at each active stage.
    for s in range(k):
        matched=[role for S,role in events if s in S]
        assert len(matched)==len(set(matched))
        assert set(matched)=={r for r in range(n) if s in M[r]}
        for S,r in events:
            if s in S: assert S.issubset(M[r])
    # Derive pair-cut counts from the explicit sets, compacting repeated sizes.
    for s in range(k):
        for t in range(k):
            if s==t: continue
            role_types=Counter((len(Mr),t in Mr) for Mr in M if s in Mr)
            event_types=Counter((len(S),t in S) for S,_ in events if s in S and len(S)>=2)
            for ell in range(2,k+1):
                w=sum(c for (d,contains),c in role_types.items() if ell<=d or contains)
                g=sum(c for (d,contains),c in event_types.items() if ell<=d or contains)
                assert 2+g==w,('pair cut',s,t,ell,2+g,w)
    low,high=check_primal(k,{2:2*k-4,k:2},{1:2*k,2:2*k-4})
    return low,high,len(events)

for k in (71,72,73,74):
    lo,hi,ne=check(k)
    print('k=%d roles=%d events=%d event value in [%s, %s], > bar=%s'%(k,2*k-2,ne,decimal_bound(lo,12,False),decimal_bound(hi,12,True),lo>BAR))
try:
    check(3,corrupt=True)
except AssertionError as err:
    print('control rejected corrupted event vector:',err)
else:
    raise AssertionError('corrupt event vector accepted')
print('event-data witness checks passed with rank(A)=rank(B)=n; determinant excludes P=-I')
