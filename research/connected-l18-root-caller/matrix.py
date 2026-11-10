"""Exact rational matrix helpers and explicit L3 projector decoder."""
from fractions import Fraction as F

def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]

def zero(n):
    return [[F(0) for _ in range(n)] for _ in range(n)]

def add(a, b, c=F(1)):
    return [[x+c*y for x,y in zip(r,s)] for r,s in zip(a,b)]

def scale(a, c):
    return [[c*x for x in r] for r in a]

def mul(a,b):
    bt=list(zip(*b))
    return [[sum((x*y for x,y in zip(r,s) if x and y), F(0)) for s in bt] for r in a]

def outer(a,b):
    return [[x*y for y in b] for x in a]

def dot(a,b):
    return sum((x*y for x,y in zip(a,b)), F(0))

def rank(a):
    a=[r[:] for r in a]; pivot=0
    for c in range(len(a[0])):
        p=next((i for i in range(pivot,len(a)) if a[i][c]),None)
        if p is None: continue
        a[pivot],a[p]=a[p],a[pivot]; q=a[pivot][c]
        a[pivot]=[x/q for x in a[pivot]]
        for i in range(pivot+1,len(a)):
            q=a[i][c]
            if q: a[i]=[x-q*y for x,y in zip(a[i],a[pivot])]
        pivot+=1
        if pivot==len(a): break
    return pivot

def inverse(a):
    n=len(a); b=[r[:]+s for r,s in zip(a,eye(n))]
    for c in range(n):
        p=next(i for i in range(c,n) if b[i][c]); b[c],b[p]=b[p],b[c]
        q=b[c][c]; b[c]=[x/q for x in b[c]]
        for i in range(n):
            if i!=c:
                q=b[i][c]; b[i]=[x-q*y for x,y in zip(b[i],b[c])]
    return [r[n:] for r in b]

def prefixes(a,b,coefficient):
    out=[eye(len(a[0]))]
    for x,y in zip(a,b):
        out.append(mul(add(eye(len(x)),outer(x,y),coefficient),out[-1]))
    return out

def reconstruct(data,coefficient=F(1)):
    """Recovered interpretation; not claimed to reproduce unpublished author code.
    Six (p,q) pairs normalize to p q/(q p). Slot s is after s units.
    Prefix conjugation transports every projector to initial coordinates.
    """
    a=[[F(v) for v in r] for r in data['a']]
    b=[[F(v) for v in r] for r in data['b']]
    n=len(a[0]); v=list(map(F,data['params']))
    pref=prefixes(a,b,coefficient); inv=[inverse(p) for p in pref]
    es=[]; pieces=[]
    for k,st in enumerate(data['stages']):
        u,w=st['block'][1]
        host=add(outer(a[w],b[u]),outer(a[u],b[w]),F(-1))
        ps=[mul(mul(inv[w+1],host),pref[w+1])]
        for j,slot in enumerate(st['idle_slots']):
            off=4*n*k+2*n*j; p,q=v[off:off+n],v[off+n:off+2*n]
            idle=scale(outer(p,q),1/dot(q,p))
            ps.append(mul(mul(inv[slot],idle),pref[slot]))
        pieces.append(ps); e=zero(n)
        for p in ps: e=add(e,p)
        es.append(e)
    return a,b,pref,pieces,es
