"""Exact rectangular A1/A5 controls; finite checks supplement the general proof."""
from fractions import Fraction as Q
import json,random
from pathlib import Path
HERE=Path(__file__).resolve().parent


def pivots(matrix):
    a=[row[:] for row in matrix];active=set(range(len(a[0])));out=[]
    for i in range(len(a)):
        nz=[j for j in active if a[i][j]]
        if not nz:continue
        j=max(nz);active.remove(j);out.append((i,j))
        for k in range(i+1,len(a)):
            q=a[k][j]/a[i][j]
            if q:a[k]=[x-q*y for x,y in zip(a[k],a[i])]
    return out


def runs(ps):
    ans=[];old=None
    for p in ps:
        if old is not None and p==(old[0]+1,old[1]+1):ans[-1]+=1
        else:ans.append(1)
        old=p
    return ans


def run(pre):
    data=json.loads((HERE/'inputs.json').read_text());pair={k:list(map(Q,v)) for k,v in data['controls']['exact_A1']['line_pairs'].items()}
    p,xi,t,phi,u,eta,v,nu=(pair[k] for k in ('p','xi','t','phi','u','eta','v','nu'))
    assert sum(x*y for x,y in zip(p,xi))==sum(x*y for x,y in zip(t,phi))==1
    assert sum(x*y for x,y in zip(u,eta))==sum(x*y for x,y in zip(v,nu))==1
    assert sum(x*y for x,y in zip(u,nu))==sum(x*y for x,y in zip(v,eta))==0
    a,b,k=pre['dims'];H=a*b;n=a+k;R,C=pre['R'],pre['C'];outerR=list(range(k))+list(range(a));outerC=list(range(a))+list(range(k))
    matrix=[[int(outerR[i]==outerC[j])*p[R[i]]*xi[C[j]]*v[i%b]*nu[(H-n+j)%b]
             +int(R[i]==C[j])*t[outerR[i]]*phi[outerC[j]]*u[i%b]*eta[(H-n+j)%b]
             for j in range(n)] for i in range(n)]
    ps=pivots(matrix);assert len(ps)==n and runs(ps)==[a,k-2*a,a,a]
    records=[]
    for seed in (281027,281028):
        rng=random.Random(seed)
        p=[Q(rng.randrange(1,100)) for _ in range(a)];xi=[Q(rng.randrange(1,100)) for _ in range(a)];dot=sum(x*y for x,y in zip(p,xi));xi=[x/dot for x in xi]
        v=[Q(rng.randrange(1,100)) for _ in range(b)];nu=[Q(rng.randrange(1,100)) for _ in range(b)];dot=sum(x*y for x,y in zip(v,nu));nu=[x/dot for x in nu]
        r=a+b-1
        def corner(labels):
            return [[int(i%b==(H-r+j)%b)*p[R[i]]*xi[labels[n-r+j]]
                +int(R[i]==labels[n-r+j])*v[i%b]*nu[(H-r+j)%b]
                -p[R[i]]*xi[labels[n-r+j]]*v[i%b]*nu[(H-r+j)%b]
                for j in range(r)] for i in range(r)]
        q=corner(C);qs=pivots(q);expected=[(i,i+a-1) for i in range(1,b-1)]
        assert len(qs)==r and qs[1:b-1]==expected
        for i in range(1,b-1):
            for j in range(a,r-1):
                schur=q[i][j]-q[i][r-1]*q[0][j]/q[0][r-1]
                exact=int(i==j-a+1)*p[i]*xi[j-b+1]+int(i==j-b+1)*v[i]*nu[j-a+1]
                assert schur==exact
                if j>i+a-1:assert schur==0
                if j==i+a-1:assert schur==p[i]*xi[i+a-b]!=0
        wrong=C[:];wrong[-a+1],wrong[-2]=wrong[-2],wrong[-a+1]
        assert pivots(corner(wrong))[1:b-1]!=expected and q[1][r-2]!=0
        records.append(dict(seed=seed,rank=r,block=b-2,exact_schur=True,negative_controls=['wrong_boundary','omit_first_pivot']))
    return dict(field='Q',A1=dict(rank=n,runs=runs(ps)),A5=records,
                scope='Actual retained prescribed corners; general simultaneous minors use the written proof, not these finite samples.')
