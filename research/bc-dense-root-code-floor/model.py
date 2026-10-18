"""B/C dense binary pairing and exact star witnesses; ywz65, Apache-2.0.
Prepared with substantial OpenAI Codex assistance. Coefficients are not F2.
"""
from itertools import combinations

def require(ok,message):
    if not ok:raise ValueError(message)

def roots(n,kind='B'):
    require(type(n)is int and n>=1 and kind in ('B','C'),'root domain')
    out=[]
    for i in range(n):
        a=[0]*n;a[i]=2 if kind=='B' else 4;out.append(tuple(a))
    for i,j in combinations(range(n),2):
        for sign in (1,-1):
            a=[0]*n;a[i]=2;a[j]=2*sign;out.append(tuple(a))
    return out

def dot(a,b):return sum(x*y for x,y in zip(a,b))

def dense(lines):
    return [sum(1<<j for j,b in enumerate(lines) if i==j or dot(a,b)==0) for i,a in enumerate(lines)]

def rank2(rows):
    piv={}
    for value in rows:
        while value:
            p=value.bit_length()-1
            if p not in piv:piv[p]=value;break
            value^=piv[p]
    return len(piv)

def support(lines,x,prime=None):
    return [i for i,r in enumerate(lines) if (dot(r,x)%prime if prime else dot(r,x))!=0]

def block(rows,rs,cs):
    return [sum(((rows[i]>>j)&1)<<k for k,j in enumerate(cs)) for i in rs]

def star(lines,x,anchor,other=None,prime=None):
    n=len(x);nz=lambda v:(v%prime if prime else v)!=0
    require(nz(x[anchor]),'zero anchor')
    selected=[anchor]
    order=([other] if other is not None and other!=anchor else [])
    order += [j for j in range(n) if j!=anchor and j not in order]
    for j in order:
        choices=[i for i,r in enumerate(lines) if i>=n and {k for k,v in enumerate(r) if v}=={anchor,j}]
        good=next((i for i in choices if nz(dot(lines[i],x))),None)
        require(good is not None,'no supported edge root')
        selected.append(good)
    require(len(set(selected))==n and all(i in support(lines,x,prime) for i in selected),'star membership')
    return selected

def cross_matrix(n,same):
    if same:return [1<<i for i in range(n)]
    require(n>=2,'distinct anchors require n>=2')
    return [1|sum(1<<j for j in range(2,n)),2]+[1|sum(1<<j for j in range(2,n) if j!=i) for i in range(2,n)]

def verify_star(lines,rows,x,y,prime=None):
    nz=lambda v:(v%prime if prime else v)!=0
    i=next(k for k,v in enumerate(x) if nz(v));j=next(k for k,v in enumerate(y) if nz(v))
    rs=star(lines,x,i,j,prime);cs=star(lines,y,j,i,prime)
    actual=block(rows,rs,cs);expected=cross_matrix(len(x),i==j)
    require(actual==expected,'geometry does not match cross-star formula')
    reduced=list(actual)
    if i!=j:
        for k in range(2,len(x)):reduced[k]^=reduced[0]
    require(all((row&((1<<(k+1))-1))==1<<k for k,row in enumerate(reduced)),'star not unit upper triangular')
    require(rank2(actual)==len(x),'singular star')
    return rs,cs

def patterns(n):
    """Canonical signed equality/zero cells of x_i, including no zero vector."""
    def visit(a,k):
        if len(a)==n:
            if k:yield tuple(a)
        else:
            for x in [0,*range(1,k+2),*range(-k,0)]:yield from visit(a+[x],max(k,x))
    return list(visit([],0))

def partitions(n,lo=1):
    if not n:yield []
    for k in range(lo,n+1):
        for tail in partitions(n-k,k):yield [k]+tail

def orbit_representatives(n):
    for zeros in range(n):
        for sizes in partitions(n-zeros):
            yield tuple([0]*zeros+[j+1 for j,size in enumerate(sizes) for _ in range(size)])
