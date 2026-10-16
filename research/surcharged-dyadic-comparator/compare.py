"""Exact dyadic-rank comparison with the retained count-dependent surcharge."""
from fractions import Fraction as Q


def need(ok, message):
    if not ok: raise ValueError(message)


def trim(p):
    p=list(map(Q,p))
    while p and p[-1]==0: p.pop()
    return p


def value(p,x):
    v=Q(0)
    for c in reversed(p): v=v*x+c
    return v


def divide(a,b):
    a,b=trim(a),trim(b)
    need(bool(b),'zero polynomial divisor')
    out=[Q(0)]*max(0,len(a)-len(b)+1)
    while a and len(a)>=len(b):
        k=len(a)-len(b);c=a[-1]/b[-1];out[k]=c
        for j,d in enumerate(b): a[k+j]-=c*d
        a=trim(a)
    return trim(out),a


def gcd(a,b):
    a,b=trim(a),trim(b)
    while b: a,b=b,divide(a,b)[1]
    return [c/a[-1] for c in a] if a else []


def polynomial(counts,m,W):
    need(type(m) is int and m>=2 and m&(m-1)==0,'power-of-two dimension')
    need(type(W) is int and W>0,'positive integer live stock')
    need(isinstance(counts,dict) and bool(counts),'nonempty profile')
    need(all(type(r) is int and 1<=r<=m and r&(r-1)==0 and
             type(n) is int and n>=0 for r,n in counts.items()),'nonnegative integer dyadic profile')
    N=sum(counts.values());need(N>0,'positive call count')
    k=m.bit_length()-1
    p=[Q(-m*W)]+[Q(0)]*k
    for r,n in counts.items(): p[k-(r.bit_length()-1)]+=r*n
    p[k]+=Q(32*m*m,10**16)*N
    need(value(p,1)<0,'positive-root contract')
    return trim(p)


def refine(p,lo,hi):
    if lo==hi: return lo,hi
    mid=(lo+hi)/2;v=value(p,mid)
    return (mid,mid) if v==0 else (mid,hi) if v<0 else (lo,mid)


def compare(a,b,m,W,*,max_steps=None):
    """Order a's root against b's: +1 means a has the larger saving.

    Default terminates on this exact domain, by gcd detection then separation
    of distinct roots. A caller-supplied refinement budget may return UNRESOLVED.
    No physical realization or non-dyadic spectrum is inferred.
    """
    need(max_steps is None or type(max_steps) is int and max_steps>=0,'refinement budget')
    p,q=polynomial(a,m,W),polynomial(b,m,W)
    g=gcd(p,q)
    # Each input has exactly one positive simple root, lying above one.
    # Therefore the monic common divisor is negative at one iff they coincide.
    if value(g,1)<0:
        pa,ra=divide(p,g);pb,rb=divide(q,g)
        need(not ra and not rb,'common factor division')
        return dict(status='EXACT_EQUAL',order=0,gcd=list(map(str,g)),
                    quotients=[list(map(str,pa)),list(map(str,pb))],steps=0)
    hi=Q(2)
    while value(p,hi)<=0 or value(q,hi)<=0: hi*=2
    la=lb=Q(1);ua=ub=hi;steps=0
    while True:
        if ua<lb or ub<la:
            return dict(status='EXACT_ORDER',order=-1 if ua<lb else 1,
                        intervals=[[str(la),str(ua)],[str(lb),str(ub)]],
                        gcd=list(map(str,g)),steps=steps)
        if max_steps is not None and steps>=max_steps:
            return dict(status='UNRESOLVED',order=None,
                        intervals=[[str(la),str(ua)],[str(lb),str(ub)]],steps=steps)
        la,ua=refine(p,la,ua);lb,ub=refine(q,lb,ub);steps+=1
