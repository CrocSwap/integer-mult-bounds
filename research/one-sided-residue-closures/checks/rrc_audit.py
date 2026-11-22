# AUDIT-SC independent RRC engine (relative root counting, SC-B2 Lemma RRC; j=d is SC-S7B's lemma; immediate rule = S7a).
# Certificate = (K0 multiset of g-values, j, family of (j-1)-index-subsets M of comp) with
#   cap(comp\M)+extra <= 77, cap(comp\(M u M'))+extra <= 56 (distinct M,M'), |F| > N_j.
# Immediate: some (d-1)-subset K with cap([a]\K)+extra <= 56.
import itertools, random, functools
from collections import Counter
G={1:1,2:2,3:4,4:8,5:12,6:20,7:36,8:64}          # verified by gtab.py (independent model)
N={1:1,2:3,3:6,4:12,5:20,6:36,7:63,8:120}            # ADE classification; N_2,N_3 exhaustive (nj.py), N_4 run nj4.out
def submultisets(cnt,k):
    keys=sorted(cnt)
    def rec(i,k):
        if k==0: yield (); return
        if i==len(keys): return
        v=keys[i]
        for t in range(min(cnt[v],k),-1,-1):
            for rest in rec(i+1,k-t): yield (v,)*t+rest
    yield from rec(0,k)
def clique(comp,j,extra,tries=30):
    cap=sum(comp)+extra; m=len(comp)
    nodes=[M for M in itertools.combinations(range(m),j-1) if cap-sum(comp[i] for i in M)<=77]
    if len(nodes)<=N[j]: return None
    def ok(A,B): return cap-sum(comp[i] for i in set(A)|set(B))<=56
    rnd=random.Random(1)
    orders=[sorted(nodes,key=lambda M:-sum(comp[i] for i in M)), sorted(nodes,key=lambda M:sum(comp[i] for i in M)), list(nodes)]
    for t in range(tries if len(nodes)<3000 else 3): o=list(nodes); rnd.shuffle(o); orders.append(o)
    best=[]
    for o in orders:
        F=[]
        for M in o:
            if all(ok(M,X) for X in F): F.append(M)
        if len(F)>len(best): best=F
        if len(best)>N[j]: return best
    return None
@functools.lru_cache(maxsize=None)
def kill(gv,d,extra=0):
    gv=tuple(sorted(gv,reverse=True)); a=len(gv)
    if d<1: return None
    # immediate: K = d-1 largest
    if sum(gv[d-1:])+extra<=56: return ('IMM',gv[:d-1])
    cnt=Counter(gv)
    for j in range(2,d+1):
        for K0 in submultisets(cnt,d-j):
            rest=cnt.copy(); rest.subtract(Counter(K0)); comp=sorted(rest.elements(),reverse=True)
            F=clique(comp,j,extra)
            if F: return ('RRC',K0,j,tuple(comp),tuple(F))
    return None
def verify(cert,gv,d,extra):
    """independent re-check of a certificate"""
    gv=sorted(gv,reverse=True)
    if cert[0]=='IMM':
        K=list(cert[1]); assert len(K)==d-1
        rest=Counter(gv); rest.subtract(Counter(K)); assert min(rest.values())>=0
        assert sum(rest.elements())+extra<=56; return True
    _,K0,j,comp,F=cert
    assert len(K0)==d-j and j>=2
    assert sorted(list(K0)+list(comp))==sorted(gv)
    cap=sum(comp)+extra
    assert len(set(F))==len(F)>N[j]
    for M in F:
        assert len(M)==j-1 and len(set(M))==j-1 and all(0<=i<len(comp) for i in M)
        assert cap-sum(comp[i] for i in M)<=77
    for A,B in itertools.combinations(F,2):
        assert cap-sum(comp[i] for i in set(A)|set(B))<=56
    return True
def scen(ws,d,s):
    """list of (tag, gvalues, d, extra) that must ALL be killed"""
    gv=[G[w] for w in ws]
    if s==7: return [('ClassI',gv,d,0)]
    if s==6:
        L=[('base(b1,b2-nonT,b3-c8/9)',gv,d,0),('alpha(+f)',gv,d,1)]
        for x in sorted(set(ws)):
            i=ws.index(x); g2=list(gv); g2[i]=G[x+1]
            L.append(('bump x=%d (b2%s)'%(x,',b3-i' if x<=6 else ''),g2,d,0))
        if 7 in ws:
            i=ws.index(7); g2=gv[:i]+gv[i+1:]
            L.append(('b3-B (drop a 7, d-1)',g2,d-1,0))
        return L
    return None
