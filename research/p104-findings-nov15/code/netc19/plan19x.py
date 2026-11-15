"""NETC19: unit-level route packing. Groups of units with the same PROJECTIVE delivered content (exact Fractions);
chain = t1 ascending, sp[G] nested ascending; helper gives with q = u_j/u_1. Min chain cover by bipartite matching."""
import sys,os,collections,pickle,time
sys.path.insert(0,'.')
os.environ['PLAN']='inputs/NETC6/g2a.plan.pkl'; os.environ['GRAN']='862,1540'
from core15 import *
from chainer import units
from fractions import Fraction as Q
def ratio(u1,u2):
    """u2 = q*u1 exactly? return q or None"""
    if set(u1)!=set(u2) or not u1: return None
    k=next(iter(u1)); q=Q(u2[k])/Q(u1[k])
    return q if all(Q(u2[x])==q*Q(u1[x]) for x in u1) else None
def groups(N,U):
    g=collections.defaultdict(list)
    for i,u in U.items():
        d=u['u']
        if not d: continue
        g[frozenset((k,Q(v)) for k,v in d.items())].append(i)
    return g
def cover(N,U,idx):
    """min chain cover (list of chains, each list of unit idx) under t1 strict asc & sp nested"""
    sp=N.w.sp; idx=sorted(idx,key=lambda i:(U[i]['t1'],i)); n=len(idx)
    ok=lambda a,b: U[a]['t1']<U[b]['t1'] and sp[U[a]['G']]<=sp[U[b]['G']]
    adj=[[j for j in range(n) if ok(idx[i],idx[j])] for i in range(n)]
    mt=[-1]*n
    def aug(i,seen):
        for j in adj[i]:
            if j in seen: continue
            seen.add(j)
            if mt[j]<0 or aug(mt[j],seen): mt[j]=i; return True
        return False
    for i in range(n): aug(i,set())
    nxt={mt[j]:j for j in range(n) if mt[j]>=0}; has_prev={j for j in range(n) if mt[j]>=0}
    ch=[]
    for i in range(n):
        if i in has_prev: continue
        c=[i]
        while c[-1] in nxt: c.append(nxt[c[-1]])
        ch.append([idx[x] for x in c])
    return ch
if __name__=='__main__':
    N=load14(); H0=N.H0; U=units(N,H0)
    g=groups(N,U); print('units',len(U),'proj contents',len(g))
    tot=0;tot2=0
    rows=[]
    for c,idx in g.items():
        ch=cover(N,U,idx); tot+=len(idx); tot2+=len(ch); rows.append((len(idx),len(ch),c))
    print('units in groups',tot,'chains',tot2)
    rows.sort(key=lambda x:-x[0])
    print([(a,b) for a,b,_ in rows[:25]])
    # dim-window-only comparison (NETC18 style): number of distinct (content, G) pairs
    pairs=sum(len(set(U[i]['G'] for i in idx)) for idx in g.values()); print('distinct (content,G) pairs',pairs)
