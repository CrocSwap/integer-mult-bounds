#!/usr/bin/env python3
"""Complete pivot checks under ONE nested S, plus joint-condition negatives."""
from pathlib import Path
import json,random,sys
P=65521

def ident(n):return [[int(i==j) for j in range(n)] for i in range(n)]
def mm(a,b):
    return [[sum(x*y for x,y in zip(row,col))%P for col in zip(*b)] for row in a]
def inv(a):
    n=len(a); a=[list(row)+e for row,e in zip(a,ident(n))]
    for j in range(n):
        k=next((k for k in range(j,n) if a[k][j]),None)
        if k is None:raise ValueError('singular')
        a[j],a[k]=a[k],a[j]; d=pow(a[j][j],-1,P); a[j]=[x*d%P for x in a[j]]
        for k in range(n):
            if k!=j:
                f=a[k][j];a[k]=[(x-f*y)%P for x,y in zip(a[k],a[j])]
    return [row[n:] for row in a]
def randinv(n,rng):
    while True:
        a=[[rng.randrange(P) for _ in range(n)] for _ in range(n)]
        try:return a,inv(a)
        except ValueError:pass
def kron(a,b):return [[x*y%P for x in ar for y in br] for ar in a for br in b]
def subtract(a,b):return [[(x-y)%P for x,y in zip(ar,br)] for ar,br in zip(a,b)]
def rankone(h,rng):
    while True:
        t=[rng.randrange(P) for _ in range(h)]; f=[rng.randrange(P) for _ in range(h)]
        z=sum(x*y for x,y in zip(t,f))%P
        if z:
            f=[x*pow(z,-1,P)%P for x in f]
            return t,f,[[x*y%P for y in f] for x in t]
def pivots(a):
    a=[r[:] for r in a]; active=set(range(len(a[0]))); out=[]
    for i in range(len(a)):
        js=[j for j in active if a[i][j]]
        if not js:continue
        j=max(js); out.append((i,j));active.remove(j)
        c=pow(a[i][j],-1,P)
        for k in range(i+1,len(a)):
            f=a[k][j]*c%P
            if f:
                a[k]=[(x-f*y)%P for x,y in zip(a[k],a[i])]
    return out



def tr(a):return [list(x) for x in zip(*a)]
def projector(pair,k):
    a,b=pair;n=len(a)
    return [[a[i][k]*b[k][j]%P for j in range(n)] for i in range(n)]
def conj(a,pair):return mm(mm(pair[0],a),pair[1])
def params(h,rng,same_inner=False):
    K0,K0i=randinv(h,rng);Js=[randinv(h,rng) for _ in range(h)]
    if same_inner:Js=[Js[0]]*h
    H=h*h
    K=[[Js[i][0][al][be]*K0[i][j]%P for be in range(h) for j in range(h)]
       for al in range(h) for i in range(h)]
    Ki=[[K0i[i][j]*Js[j][1][al][be]%P for be in range(h) for j in range(h)]
        for al in range(h) for i in range(h)]
    assert mm(K,Ki)==ident(H)
    gs=[randinv(h,rng) for _ in range(H)]
    return (K,Ki),gs

def run_one(h,seed,same_inner=False):
    rng=random.Random(seed);H=h*h;m=h*H;Ih=ident(h);IV=ident(H)
    K,gs=params(h,rng,same_inner)
    labels=[randinv(h,rng),randinv(h,rng)]
    first=projector(labels[0],0);second=projector(labels[1],0);orth=projector(labels[1],1)
    q=kron(first,orth);U=kron(Ih,second);Z=kron(first,Ih)
    data=kron(subtract(Ih,first),subtract(Ih,second))
    assert mm(q,U)==[[0]*H for _ in range(H)]
    # Transform all original and transposed operators with the SAME K and G_i.
    products={(i,j):mm(gs[i][0],gs[j][1]) for i in range(H) for j in range(H)}
    records=[]
    for dual in (False,True):
        t=tr(first) if dual else first
        q2=conj(tr(q) if dual else q,K)
        u2=conj(tr(U) if dual else U,K)
        z2=conj(tr(Z) if dual else Z,K)
        d2=conj(tr(data) if dual else data,K)
        tp={(i,j):mm(mm(gs[i][0],t),gs[j][1]) for i in range(H) for j in range(H)}
        def matrix(kind):
            out=[]
            for al in range(h):
                for i in range(H):
                    row=[]
                    for be in range(h):
                        for j in range(H):
                            eye=int(i==j and al==be);g=products[i,j][al][be];p=tp[i,j][al][be]
                            if kind=='A1':v=eye-q2[i][j]*g-u2[i][j]*p
                            elif kind=='A3':v=(int(i==j)-q2[i][j])*(g-p)
                            elif kind=='A4':v=eye-z2[i][j]*p
                            elif kind=='data':v=d2[i][j]*p
                            row.append(v%P)
                    out.append(row)
            return out
        for kind in ('A1','A3','A4','data'):
            A=matrix(kind);ps=pivots(A);lookup=dict(ps)
            if kind=='A1':
                r=2*h
                passed=len(ps)==m-r and all(lookup.get(i)==i for i in range(r,m-r))
                if not passed and same_inner:return {'h':h,'same_inner':True,'rejected_condition':'A1 corner loses required rank'}
                assert passed,('A1',h,seed,dual)
                assert {lookup[i] for i in range(r)}==set(range(m-r,m))
                shape=dict(rank=m-r,singletons=r,blocks=[m-2*r])
            elif kind=='A3':
                r=h-1;R=H+r
                assert len(ps)==m-R
                assert all(lookup.get(i)==m-H+i for i in range(r,H-r))
                assert all(lookup.get(i)==i for i in range(R,m-R))
                assert {lookup[i] for i in range(R)}==set(range(m-R,m))
                shape=dict(rank=m-R,singletons=3*r,blocks=[H-2*r,m-2*R])
            elif kind=='A4':
                assert len(ps)==m-h
                assert all(lookup.get(i)==m-h+i for i in range(h))
                assert all(lookup.get(i)==i for i in range(h,m-h))
                shape=dict(rank=m-h,singletons=0,blocks=[h,m-2*h])
            else:
                r=2*h-1
                assert len(ps)==H-r
                assert all(lookup.get(i)==m-H+i for i in range(r,H-r))
                assert {lookup[i] for i in range(r)}==set(range(m-r,m))
                shape=dict(rank=H-r,singletons=r,blocks=[H-2*r])
            # Complete idempotence at small h; all larger matrices have the
            # displayed exact projector formula and verified rank/profile.
            if h==4:assert mm(A,A)==A
            records.append(dict(kind=kind,dual=dual,**shape))
    if same_inner:raise AssertionError('Degenerate inner controls unexpectedly pass')
    return dict(h=h,seed=seed,one_basis_for_all=True,profiles=records)

def main():
    positives=[]
    for h in (4,5):
        for rep in range(2):
            positives.append(run_one(h,191000+h*100+rep))
    negatives=[run_one(h,199000+h,same_inner=True) for h in (4,5)]
    return dict(status='EXACT FINITE-FIELD JOINT PIVOT CONTROLS',field=P,
                positive_shared_bases=len(positives),positive_complete_profiles=8*len(positives),
                positives=positives,negatives=negatives,
                scope='One nested basis simultaneously covers A1/A3/A4/data and all dual projectors in each finite instance; not a substitute for rational finite-family existence or h32 scalar audit.')
if __name__=='__main__':print(json.dumps(main(),indent=2))
