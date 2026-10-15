"""Dyadic rank-h factor for the retained complex central map.

Only the central scalar factor changes. All incidences at each gather/scatter
remain grouped at their old common frames, including zero coefficients.
"""
from fractions import Fraction as Q
from itertools import combinations

from certify import require
from experiments.disjoint_tensor import complex_counts


def factor(h):
    require(type(h) is int and h >= 8 and h % 2 == 0, 'Use even h >= 8')
    triples = list(combinations(range(h), 3))
    base = frozenset((0, 1, 2))
    gather = []
    scatter = []
    for T in triples:
        S = frozenset(T)
        v = [1] + [int(i in S)-int(i in base) for i in range(1, h)]
        u = [len(S & base)-1] + [int(i in S)-int(0 in S) for i in range(1, h)]
        gather.append(tuple((i, x) for i, x in enumerate(v) if x))
        scatter.append(tuple(u))
    return dict(h=h, triples=triples, gather=gather, scatter=scatter)


def verify_factor(f):
    h=f['h'];triples=list(combinations(range(h),3));n=len(triples)
    require(f['triples']==triples and len(f['gather'])==len(f['scatter'])==n,
            'Wrong triple or factor dimensions')
    require(all(len(u)==h and all(type(x) is int for x in u) for u in f['scatter']),
            'Scatter must be integral')
    for v in f['gather']:
        require(len({i for i,x in v})==len(v) and
                all(type(i) is int and type(x) is int and 0<=i<h and x in (-1,1)
                    for i,x in v), 'Invalid sparse gather')
    masks=[sum(1<<i for i in T) for T in triples]
    for S,u in zip(masks,f['scatter']):
        for T,v in zip(masks,f['gather']):
            require(sum(u[i]*x for i,x in v)==(S&T).bit_count()-1,
                    'Central factor coefficient mismatch')
    require(all(x in (-1,0,1,2) for u in f['scatter'] for x in u),
            'Scalar charge requires these dyadic weights')
    G=sum(len(v) for v in f['gather'])
    R=sum(1 if abs(x)==2 else 2 for u in f['scatter'] for x in u if x)
    return dict(h=h,triples=n,central_roles=h,coefficients_checked=n*n,
                integer_product_verified=True,gather_steps=G,scatter_steps=R,
                all_scalar_weights_dyadic=True)


def counts(h, disjoint_roles):
    old=complex_counts(h,disjoint_roles)
    n=old['v'];m=old['m'];N=old['N']
    W=2*N+2*n*n*(old['side_roles']+h)
    L=3*n*n*h*h;delta=2*N-2*L
    return dict(old,central_roles=h,W=W,L=L,deficit=delta,s=W*m-delta,eta=Q(delta,W*m))


def invoke(x,y,scratch,center,code,f,inverse=False):
    """Signed transparent invocation, with independent arbitrary auxiliaries."""
    require(code['triples']==f['triples'] and code['h']==f['h'], 'Mismatched scalar factors')
    require(len(x)==len(y)==len(f['triples']) and len(center)==f['h'] and
            len(scratch)==code['roles'], 'Wrong role dimensions')
    def mix(sign):
        for ins,outs in (code['gates'] if sign==1 else reversed(code['gates'])):
            pivot=ins[0]
            if sign==1:
                for i in ins[1:]:scratch[pivot]+=scratch[i]
                for j in outs[1:]:scratch[j]+=scratch[pivot]
            else:
                for j in outs[1:]:scratch[j]-=scratch[pivot]
                for i in ins[1:]:scratch[pivot]-=scratch[i]
    def copy(sign):
        for i,slot in code['sources']:scratch[slot]+=sign*x[i]
    def inject(sign):
        for i,slot,weight in code['outputs']:y[i]+=sign*weight*scratch[slot]
    def gather(sign):
        for i,v in enumerate(f['gather']):
            for j,weight in v:center[j]+=sign*weight*x[i]
    def scatter(sign):
        for i,u in enumerate(f['scatter']):
            for j,weight in enumerate(u):
                if weight:y[i]+=sign*Q(weight,2)*center[j]
    operations=((mix,1),(inject,-1),(mix,-1),(scatter,-1),(copy,1),(gather,1),
                (scatter,1),(mix,1),(inject,1),(mix,-1),(gather,-1),(copy,-1))
    if inverse:operations=tuple((op,-sign) for op,sign in reversed(operations))
    for op,sign in operations:op(sign)
