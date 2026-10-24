"""Exact completion census and literal signed Pauli controls.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The turn, product and signed-extension conventions follow JoyboyBrian's
PR5051 pauli.py at 0960807a68ff46acbe6510c8867912ef2324ee71.
"""
from itertools import product
from fractions import Fraction as F


def need(ok, message):
    if not ok:
        raise ValueError(message)


def span(rows):
    out = {0}
    for x in rows:
        out |= {v ^ x for v in out}
    return out


def basis(values):
    out, seen = [], {0}
    for x in sorted(values):
        if x not in seen:
            out.append(x)
            seen |= {v ^ x for v in seen}
    return tuple(out)


def omega(a, b, n):
    mask = (1 << n) - 1
    return (((a & mask) & (b >> n)) ^ ((b & mask) & (a >> n))).bit_count() % 2


def act(columns, x):
    out = 0
    for j, v in enumerate(columns):
        if x >> j & 1:
            out ^= v
    return out


def symplectic(n):
    out = []
    def extend(cols):
        j = len(cols)
        if j == 2 * n:
            out.append(tuple(cols))
            return
        for v in range(1, 1 << (2*n)):
            if v not in span(cols) and all(omega(v,w,n)==omega(1<<j,1<<i,n) for i,w in enumerate(cols)):
                extend(cols+[v])
    extend([])
    return out


def spaces(n):
    out = {frozenset({0})}
    for _ in range(2*n):
        out |= {frozenset(set(s) | {x ^ v for x in s}) for s in out for v in range(1 << (2*n))}
    return {basis(s) for s in out}


def predicted(n, rows, targets):
    z = set(range(0, 1 << (2*n), 1 << n))
    u = span(rows)
    image = {act(targets,c) for c in range(1 << len(rows))}
    pairs = {act(rows,c): act(targets,c) for c in range(1 << len(rows))}
    a = u & z
    b = {pairs[x] for x in a}
    c = b & z
    t = {x for x in image & z if all(not omega(x,y,n) for y in b)}
    return (len(b).bit_length()-1)+(len(t).bit_length()-1)-2*(len(c).bit_length()-1)


def mulp(a,b):
    return a[0]^b[0],a[1]^b[1],(a[2]+b[2]+2*(a[1]&b[0]).bit_count())%4


def apply(p, gates, n):
    mask=(1<<n)-1
    for axis in gates:
        a,b=axis&mask,axis>>n
        if ((a&p[1])^(b&p[0])).bit_count()%2:
            p=(p[0]^a,p[1]^b,(p[2]+(a&b).bit_count()+2*(b&p[0]).bit_count()-1)%4)
    return p


def lift(n, columns):
    current=[1<<j for j in range(2*n)]
    fixed=[]; gates=[]
    for j,target in enumerate(columns):
        v=current[j]
        if v != target:
            if omega(v,target,n):
                axes=[v^target]
            else:
                mids=[w for w in range(1<<(2*n)) if omega(v,w,n) and omega(target,w,n) and all(omega(w,p,n)==omega(v,p,n) for p in fixed)]
                need(bool(mids),'Witt middle')
                axes=[v^mids[0],mids[0]^target]
            for a in axes:
                current=[x^(a if omega(x,a,n) else 0) for x in current]
                gates.append(a)
        fixed.append(target)
    need(tuple(current)==columns,'lift tableau')
    return gates

# Gaussian rationals are pairs, so no floating-point phase test is used.
def add(a,b): return (a[0]+b[0],a[1]+b[1])
def mul(a,b): return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def scale(a,b): return (a[0]*b,a[1]*b)
def ipow(p): return ((F(1),F(0)),(F(0),F(1)),(F(-1),F(0)),(F(0),F(-1)))[p%4]
def pauli(p,v):
    x,z,phase=p; out=[(F(0),F(0)) for _ in v]
    for j,a in enumerate(v):out[j^x]=mul(ipow(phase+2*(z&j).bit_count()),a)
    return out

def word(n,gates,v):
    for axis in gates:
        mask=(1<<n)-1; x,z=axis&mask,axis>>n
        pv=pauli((x,z,(x&z).bit_count()%4),v)
        v=[add(mul((F(1,2),F(1,2)),a),mul((F(1,2),F(-1,2)),b)) for a,b in zip(v,pv)]
    return v


def compatible(n, constraints):
    rows=[]; selected=[]
    for p,q in constraints:
        value=p[0]|p[1]<<n
        if value not in span(rows):
            rows.append(value); selected.append((p,q))
    targets=[q[0]|q[1]<<n for p,q in selected]
    if len(basis(targets))!=len(rows):return False
    if any(omega(a,b,n)!=omega(targets[i],targets[j],n) for i,a in enumerate(rows) for j,b in enumerate(rows)):return False
    for p,q in constraints:
        bits=next(c for c in range(1<<len(rows)) if act(rows,c)==(p[0]|p[1]<<n))
        pp=qq=(0,0,0)
        for j,(a,b) in enumerate(selected):
            if bits>>j&1:pp,qq=mulp(pp,a),mulp(qq,b)
        if qq[:2]!=q[:2] or (pp[2]-p[2])%4!=(qq[2]-q[2])%4:return False
    return True


def main():
    total=0; signed=0; columns_checked=0
    chosen=[]
    for n in (0,1,2):
        group=symplectic(n); subs=spaces(n); cases={}
        for g in group:
            d=len(basis([v & ((1<<n)-1) for v in g[n:]]))
            for u in subs:
                targets=tuple(act(g,x) for x in u)
                key=(u,targets)
                if key not in cases or d<cases[key][0]:cases[key]=(d,g)
        for (u,t),(d,g) in cases.items():
            need(predicted(n,u,t)==d,'minimum differs from complete completion fiber')
        total+=len(cases)
        need(len(group)==(1,6,720)[n],'full symplectic group')
        need(len(subs)==(1,5,67)[n],'all binary subspaces')
        if n:
            chosen += [(n,u,t,d,g) for (u,t),(d,g) in sorted(cases.items())[::max(1,len(cases)//48)]]
    for n,u,t,d,g in chosen:
        gates=lift(n,g)
        mask=(1<<n)-1
        for signs in range(1<<len(u)):
            src=[(x&mask,x>>n,((x&mask)&(x>>n)).bit_count()%4) for x in u]
            dst=[(y&mask,y>>n,(((y&mask)&(y>>n)).bit_count()+2*(signs>>j&1))%4) for j,y in enumerate(t)]
            rhs=[((q[2]-apply(p,gates,n)[2])%4)//2 for p,q in zip(src,dst)]
            corrections=[v for v in range(1<<(2*n)) if all(omega(v,y,n)==r for y,r in zip(t,rhs))]
            need(bool(corrections),'signed correction exists')
            corr=corrections[0]
            for p,q in zip(src,dst):
                a=apply(p,gates,n); a=(a[0],a[1],(a[2]+2*omega(corr,a[0]|a[1]<<n,n))%4)
                need(a==q,'signed partial relation')
            signed+=1
        for j in range(1<<n):
            v=[(F(int(i==j)),F(0)) for i in range(1<<n)]
            for k in range(2*n):
                p=(1<<k,0,0) if k<n else (0,1<<(k-n),0)
                need(word(n,gates,pauli(p,v))==pauli(apply(p,gates,n),word(n,gates,v)),'literal turn conjugation')
                columns_checked+=1
    # Equal unsigned data do not excuse an inconsistent dependent sign.
    x,z=(1,0,0),(0,1,0); xz=mulp(x,z)
    y=(1,1,1)
    need(compatible(1,[(x,x),(z,z),(y,y)]),'consistent dependent relation')
    need(not compatible(1,[(x,x),(z,z),(y,(1,1,3))]),'dependent central sign rejection')
    # A scalar -I has the same signed tableau and rank, but differs literally.
    zero=[(F(1),F(0)),(F(0),F(0))]
    need(word(1,[],zero)!=[scale(a,-1) for a in zero],'absolute scalar control')
    need(predicted(1,(2,),(1,))==1,'Z to X forces paid rank')
    need(predicted(1,(1,),(1,))==0,'X to X permits monomial')
    need(predicted(1,(1,),(2,))==1,'image intersection is necessary')
    print('PASS_PARTIAL_PAULI_GAUSSIAN_MINIMUM',dict(completion_fibers=total,signed_lifts=signed,literal_columns=columns_checked,controls=5))

if __name__=='__main__': main()
