"""Fixed-pool, exact additive higher-arity echoes. Apache-2.0; see NOTICE."""
from functools import lru_cache

def need(ok,message):
    if not ok: raise ValueError(message)

def leaves(tree):
    if type(tree) is int:
        need(tree>=0,'leaf index');return [tree]
    need(isinstance(tree,(list,tuple)) and 2<=len(tree)<=4,'arity2..4 required')
    return [i for t in tree for i in leaves(t)]

def validate(tree):
    ids=leaves(tree);need(ids==list(range(len(ids))),'ordered leaf indices');return len(ids)

def compositions(n,k):
    if k==1:
        yield (n,);return
    for a in range(1,n-k+2):
        for rest in compositions(n-a,k-1):yield (a,)+rest

def plan(limit,arity):
    need(type(limit) is int and limit>=1,'positive limit')
    need(type(arity) is int and 2<=arity<=4,'planner arity')
    f=[0,1];splits=[None,None];count=0
    for n in range(2,limit+1):
        best=None
        for k in range(2,min(arity,n)+1):
            for sizes in compositions(n,k):
                weights=[2]+[4]*(k-2)+[2]
                candidate=(sum(w*f[s] for w,s in zip(weights,sizes)),k,sizes)
                count+=1
                if best is None or candidate<best:best=candidate
        f.append(best[0]);splits.append(best[2])
    def build(n,start=0):
        if n==1:return start
        out=[]
        for a in splits[n]:out.append(build(a,start));start+=a
        return tuple(out)
    return f,build(limit),count

def macro(k):
    need(2<=k<=4,'macro arity')
    C=[(i,1) for i in range(k-1)];D=C[1:]
    inverse=lambda w:[(i,-q) for i,q in reversed(w)]
    return C+[(k-1,1)]+inverse(C)+D+[(k-1,-1)]+inverse(D)

def emit(tree,dirty=4,sign=1):
    validate(tree)
    need(type(dirty) is int and dirty>=0,'dirty count')
    need(type(sign) is int and sign in (-1,1),'sign')
    pool=[r for r in (2,3,1,4,5) if r<dirty+2]
    pool+=list(range(6,dirty+2))
    def visit(t,s,d,q):
        if type(t) is int:return [(s,d,t,q)]
        available=[r for r in pool if r not in (s,d)]
        need(len(available)>=len(t)-1,'insufficient mutable ports')
        ports=[s]+available[:len(t)-1]+[d]
        word=macro(len(t))
        if q<0:word=[(i,-v) for i,v in reversed(word)]
        return [record for i,v in word for record in visit(t[i],ports[i],ports[i+1],v)]
    # Materialize before returning: insufficient pools never expose a partial word.
    return visit(tree,0,1,sign)

def stats(t):
    if type(t) is int:return {'leaves':1,'calls':1,'nodes':1,'depth':0,'reserved':0,'max_arity':1}
    c=[stats(x) for x in t];k=len(t);weights=[2]+[4]*(k-2)+[2]
    return {'leaves':sum(x['leaves'] for x in c),'calls':sum(w*x['calls'] for w,x in zip(weights,c)),
        'nodes':1+sum(x['nodes'] for x in c),'depth':1+max(x['depth'] for x in c),
        'reserved':k-1+max(x['reserved'] for x in c),'max_arity':max(k,max(x['max_arity'] for x in c))}

def bound(t,K):
    need(type(K) is int and K>=1,'factor norm')
    if type(t) is int:return 1+K
    return (len(t)+1)*K**len(leaves(t))*max(bound(c,K) for c in t)

@lru_cache(None)
def all_trees(n,start=0):
    if n==1:return (start,)
    from itertools import product
    out=[]
    for k in range(2,min(4,n)+1):
        for sizes in compositions(n,k):
            children=[];offset=start
            for a in sizes:children.append(all_trees(a,offset));offset+=a
            out.extend(product(*children))
    return tuple(out)
