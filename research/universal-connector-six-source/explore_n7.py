#!/usr/bin/env python3
"""Heuristic annealing for universal restored source words. NOT a certificate.

Usage: python3 explore_n7.py N LENGTH ITERATIONS TRIALS
Prints the best |D(w)| found and its word. Failure to reach 2^N is a search
failure in this heuristic, not an impossibility result.
"""
import random,sys
def cov(w):
    q=0;P={0}
    for j in w: q^=1<<j;P.add(q)
    P=list(P);return len({a^b for a in P for b in P})
def search(n,L,iters,seed):
    R=random.Random(seed)
    base=[j for j in range(n) for _ in (0,1)]
    while len(base)<L: base+= [R.randrange(n)]*2
    w=base[:];R.shuffle(w);c=cov(w);best=(c,w[:])
    T=2.0
    for it in range(iters):
        v=w[:]
        r=R.random()
        if r<0.6:
            i,k=R.randrange(L),R.randrange(L);v[i],v[k]=v[k],v[i]
        elif r<0.8:
            i=R.randrange(L);x=v.pop(i);v.insert(R.randrange(L),x)
        else:
            # relabel a pair of equal labels to another label (keeps parity) if label keeps >=2
            a=R.randrange(n);idx=[i for i in range(L) if v[i]==a]
            if len(idx)>=4:
                b=R.randrange(n);i,k=R.sample(idx,2);v[i]=v[k]=b
        cv=cov(v)
        if cv>=c or R.random()<2.718**((cv-c)/T):
            w,c=v,cv
            if c>best[0]: best=(c,w[:])
            if c==1<<n: return best
        T=max(0.05,T*0.99995)
    return best
n,L,iters,trials=map(int,sys.argv[1:5])
b=max((search(n,L,iters,s) for s in range(trials)),key=lambda t:t[0])
print(n,L,b[0],1<<n,b[1])
