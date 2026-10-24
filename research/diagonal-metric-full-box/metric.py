"""Exact rational metric classification and constructive original-anchor witnesses.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F


def need(ok, message):
    if not ok:
        raise ValueError(message)


def v2(x):
    x = F(x)
    need(x != 0, 'valuation of zero')
    a, b = abs(x.numerator), x.denominator
    return (a & -a).bit_length() - (b & -b).bit_length()


def pow2(k):
    return F(2)**k


def residue4(x):
    x = F(x)
    need(x.denominator % 2 == 1, 'nonintegral at two')
    return (x.numerator * pow(x.denominator, -1, 4)) % 4


def classify(d):
    d = F(d)
    need(d > 0, 'positive metric required')
    k = v2(d)
    u = d / pow2(k)
    return k % 2 == 0 and residue4(u) == 1


def factors(p, d):
    d = F(d)
    need(d > 0, 'positive metric required')
    p = tuple(tuple(F(x) for x in row) for row in p)
    need(p and all(len(row) == 3 and any(row) for row in p), 'nonzero three-column rows')
    return p, tuple((r[0], d*r[1], r[2]) for r in p)


def anchors(p, q):
    active = [j for j in range(3) if any(r[j] for r in p) and any(r[j] for r in q)]
    need(active, 'no active columns')
    m = {j:min(v2(r[j]) for r in p if r[j]) for j in active}
    n = {j:min(v2(r[j]) for r in q if r[j]) for j in active}
    gamma = min(m[j]+n[j] for j in active)
    a = tuple(sum(1<<j for j in active if r[j] and v2(r[j]) == m[j]) for r in p)
    b = tuple(sum(1<<j for j in active if r[j] and v2(r[j])+m[j] == gamma) for r in q)
    return a, b, gamma


def matrix(p, q):
    return tuple(tuple(sum(x*y for x,y in zip(r,s)) for s in q) for r in p)


def dot(a,b):
    return (a & b).bit_count() % 2


def accepts(p, q, order, labels):
    a,b,_ = anchors(p,q)
    n=len(p)
    if len(order)!=len(labels) or len(set(order))!=len(order):return False
    if any(type(i) is not int or not 0<=i<n for i in order):return False
    if any(type(x) is not int or type(y) is not int or x<=0 or y<=0
           or x & ~a[i] or y & ~b[i] or dot(x,y)!=1
           for i,(x,y) in zip(order,labels)):return False
    m=matrix(p,q)
    return all(m[i][j]!=0 or dot(labels[s][0],labels[t][1])==0
               for s,i in enumerate(order) for t,j in enumerate(order) if s<t)


def full_witness(p, d):
    """Construct F/O/L witness; no search, subset renormalization or Gram isometry."""
    need(classify(d), 'metric outside universal class')
    p,q = factors(p,d)
    a,b,_ = anchors(p,q)
    need(all(x & y for x,y in zip(a,b)), 'empty canonical tie')
    h=v2(d)//2
    reduced=tuple((r[0],r[1]*pow2(h),r[2]) for r in p)
    m=min(v2(x) for r in reduced for x in r if x)
    scaled=tuple(tuple(x/pow2(m) for x in r) for r in reduced)
    first,middle,last=[],[],[]
    for i,r in enumerate(scaled):
        support=[j for j in range(3) if r[j] and v2(r[j])==0]
        need(sum(1<<j for j in support)==b[i], 'original target anchor invariant')
        if len(support)%2:middle.append(i)
        elif residue4(r[support[0]]*r[support[1]])==1:first.append(i)
        else:last.append(i)
    order=tuple(first+middle+last)
    labels=tuple((a[i],b[i]&-b[i]) for i in first)
    labels+=tuple((a[i],b[i]) for i in middle)
    labels+=tuple((b[i]&-b[i],b[i]) for i in last)
    need(accepts(p,q,order,labels),'constructed full witness failed')
    return order,labels


def obstruction(d):
    """Return rational family, exact attaining order/labels and obstructed core."""
    d=F(d)
    need(d>0 and not classify(d), 'requires complementary positive metric')
    h=v2(d)//2
    e=d/pow2(2*h)
    if v2(e)==1:
        rows=((1,0,1),(1,1,-1),(1,-2/e,-1))
        order,labels=(0,1),((1,1),(4,4))
    else:
        rows=((1,1,0),(e,-1,2),(e,-1,-e*(e+1)/2),(1,0,1))
        order,labels=(0,1,3),((1,1),(2,2),(1,1))
    p=tuple((F(r[0]),F(r[1])/pow2(h),F(r[2])) for r in rows)
    p,q=factors(p,d)
    need(accepts(p,q,order,labels),'attaining obstruction witness')
    return p,order,labels
