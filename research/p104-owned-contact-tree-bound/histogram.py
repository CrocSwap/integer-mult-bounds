"""Check exact minimizer histograms with outward signed intervals."""
from collections import Counter
from fractions import Fraction as Q
from functools import cache

GRID = 10**48


@cache
def log_interval(x):
    z=(x-1)/(x+1)
    t=z
    partial=Q(0)
    for j in range(1,160,2):
        partial+=t/j
        t*=z*z
    return 2*partial,2*(partial+t/(161*(1-z*z)))


def exp_negative(x,n):
    t=s=Q(1)
    for j in range(1,n+1):
        t*=-x/j
        s+=t
    return s


def verify_price(r,k,lower,upper):
    shift=r.bit_length()-1
    a,b=log_interval(Q(r,2**shift))
    c,d=log_interval(Q(2))
    scale=10**64
    lo=Q((scale*k*(a+shift*c)).__floor__(),scale)
    hi=Q((scale*k*(b+shift*d)).__ceil__(),scale)
    assert 0<=lo<=hi<1
    assert lower<=GRID*r*exp_negative(hi,49)<=GRID*r*exp_negative(lo,50)<=upper


def profile(values):
    out=[0]*9
    for rank in values:
        if rank:
            out[rank-1]+=1
    return tuple(out)


def add(a,b):
    return tuple(x+y for x,y in zip(a,b,strict=True))


def minimum(group,links,boundary,low,high,dimension_count=10):
    adj={u:Counter(links[u]) for u in group}
    profiles={u:[profile(abs(d-b) for b in boundary[u]) for d in range(dimension_count)] for u in group}
    checked=ambiguous=0

    @cache
    def floor(v):
        return sum(n*low[r] for r,n in enumerate(v,1))

    @cache
    def difference_floor(v):
        return sum(n*(low[r] if n>0 else high[r]) for r,n in enumerate(v,1))

    def choose(options):
        nonlocal checked,ambiguous
        best=min(options,key=floor)
        for v in options:
            checked+=1
            delta=tuple(a-b for a,b in zip(v,best,strict=True))
            ambiguous+=difference_floor(delta)<0
        return best

    while len(adj)>1:
        leaves=[u for u,a in adj.items() if len(a)==1]
        if not leaves:
            raise ValueError('simple graph has a cycle')
        u=max(leaves)
        v,m=adj[u].popitem()
        assert adj[v].pop(u)==m
        for d in range(dimension_count):
            merged=choose([add(p,profile([abs(d-q)]*m)) for q,p in enumerate(profiles[u])])
            profiles[v][d]=add(profiles[v][d],merged)
        del adj[u]
    u=next(iter(adj))
    assert not adj[u]
    answer=choose(profiles[u])
    return floor(answer),answer,checked,ambiguous
