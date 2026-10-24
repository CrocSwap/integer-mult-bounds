"""Exact source-ordered defect maps; independent Gaussian-rational arithmetic.

JoyboyBrian, substantial OpenAI Codex assistance; Apache-2.0.
"""
from fractions import Fraction as Q

ZERO=(Q(0),Q(0)); ONE=(Q(1),Q(0)); PHASES=(ONE,(Q(0),Q(1)),(-Q(1),Q(0)),(Q(0),-Q(1)))


def need(ok, why):
    if not ok: raise ValueError(why)


def add(a,b): return a[0]+b[0],a[1]+b[1]
def mul(a,b): return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def scale(c,a): return c*a[0],c*a[1]
def conj(a): return a[0],-a[1]


def eye(n=8): return [{i:ONE} for i in range(n)]


def put(row,j,z):
    z=add(row.get(j,ZERO),z)
    if z==ZERO: row.pop(j,None)
    else: row[j]=z


def plus(a,b,c=1):
    out=[dict(row) for row in a]
    for row,source in zip(out,b):
        for j,z in source.items(): put(row,j,scale(c,z))
    return out


def product(a,b):
    out=[{} for row in a]
    for i,row in enumerate(a):
        for k,x in row.items():
            for j,y in b[k].items(): put(out[i],j,mul(x,y))
    return out


def word(*matrices):
    out=eye(len(matrices[0]))
    for a in matrices: out=product(out,a)
    return out


def adjoint(a):
    out=[{} for row in a]
    for i,row in enumerate(a):
        for j,z in row.items(): out[j][i]=conj(z)
    return out


def monomial(perm,phases=None):
    phases=phases or [0]*len(perm)
    need(sorted(perm)==list(range(len(perm))),'monomial bijection')
    out=[{} for i in perm]
    for j,i in enumerate(perm): out[i][j]=PHASES[phases[j]%4]
    return out


def pauli(x,z):
    return monomial([j^x for j in range(8)],[(x&z).bit_count()+2*(j&z).bit_count() for j in range(8)])


def letters():
    C=[plus([{i:(Q(1,2),Q(1,2))} for i in range(8)],
            [{i^(1<<j):(Q(1,2),Q(-1,2))} for i in range(8)]) for j in range(3)]
    S=monomial(list(range(8)),[j.bit_count() for j in range(8)])
    U=monomial([0,5,2,7,4,1,6,3]); V=monomial([0,2,1,3,4,6,5,7])
    P,T=word(S,U,S),word(S,V,S)
    W=pauli(0,5); M=word(pauli(0,2),V); J=word(M,C[2]); A=C[0]
    D=word(J,W,A)
    return dict(A=A,C2=C[2],P=P,Q=T,W=W,M=M,J=J,D=D,I=eye())


def tensor(a,b):
    m=len(b); out=[]
    for ar in a:
        for br in b:
            out.append({i*m+j:mul(x,y) for i,x in ar.items() for j,y in br.items()})
    return out


def power(a,f):
    need(type(f) is int and 1<=f<=3,'bounded executable width')
    out=[{0:ONE}]
    for i in range(f): out=tensor(out,a)
    return out


def apply(a,v):
    return [sum_complex(mul(z,v[j]) for j,z in row.items()) for row in a]


def sum_complex(values):
    out=ZERO
    for z in values: out=add(out,z)
    return out


def vplus(a,b,c=1): return [add(x,scale(c,y)) for x,y in zip(a,b)]


def l1(row):
    axis=diagonal=Q(0)
    for x,y in row.values():
        if x==0 or y==0: axis+=abs(x)+abs(y)
        else:
            need(abs(x)==abs(y),'axis or eighth-root phase')
            diagonal+=abs(x)
    return axis,diagonal


def leq(a,b):
    x,y=b[0]-a[0],b[1]-a[1]
    if x>=0 and y>=0: return True
    if x<=0 and y<=0: return x==y==0
    return x*x>=2*y*y if x>=0 else 2*y*y>=x*x


def Lpower(k):
    return (Q(1<< (k//2)),Q(0)) if k%2==0 else (Q(0),Q(1<<(k//2)))


def pair_sum(*parts): return tuple(sum(z[i] for z in parts) for i in (0,1))
def pair_scale(c,a): return c*a[0],c*a[1]


def maps(base,f,kind,reverse=False):
    A,P,T,D,J,W,M,I=(base[k] for k in ('A','P','Q','D','J','W','M','I'))
    def lifted(*terms):
        out=[{} for i in range(8**f)]
        for c,a in terms: out=plus(out,power(a,f),c)
        return out
    if reverse:
        cols=[lifted((-1,P),(-2,T)),lifted((1,adjoint(A if kind==2 else D)))]
        cols += ([lifted((1,I))] if kind==2 else
                 [lifted((1,word(adjoint(A),adjoint(W)))),lifted((1,I))])
        cols.append(None)
        return cols
    B=A if kind==2 else D
    cols=[lifted((1,word(B,P,A)),(2,word(B,T,A))),lifted((1,B)),
          lifted((1,word(B,P)),(2,word(B,T)))]
    cols.append(lifted((1,I if kind==2 else word(J,W))))
    if kind==3: cols.append(lifted((1,M)))
    return cols


def schedule(base,f,kind,reverse,x,y,defects):
    lifted={k:power(v,f) for k,v in base.items()}
    A,P,T,W,M,C2=(lifted[k] for k in ('A','P','Q','W','M','C2'))
    dx,dy,*e=defects; x=vplus(x,dx); y=vplus(y,dy)
    if not reverse:
        t=vplus(apply(A,x),e[0]); z=vplus(y,apply(P,t)); z=vplus(z,apply(T,t),2)
        out=vplus(apply(A,z),e[1])
        if kind==3: out=apply(M,vplus(apply(C2,apply(W,out)),e[2]))
        return t,out
    if kind==3:
        out=vplus(apply(adjoint(C2),apply(adjoint(M),y)),e[0])
        out=vplus(apply(adjoint(A),apply(adjoint(W),out)),e[1])
    else: out=vplus(apply(adjoint(A),y),e[0])
    out=vplus(vplus(out,apply(P,x),-1),apply(T,x),-2)
    return vplus(apply(adjoint(A),x),e[-1]),out
