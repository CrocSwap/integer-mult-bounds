"""Independent exact opposite-bank factorization and ordinary-wrapper checks.
Source claim: icekylinx PR104, commit948ce1510df750f4c18b96bdaef436a86f8bf834.
Only reviewed stdlib rational helpers are imported; no PR104 code is executed.
"""
import importlib.util
import itertools
import json
from fractions import Fraction as Q
from pathlib import Path
from random import Random

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('factor',HERE/'round7-public/tree/independent/partial-swap/factor.py')
f = importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
eye, mul, inv = f.ident,f.mul,f.inv
def tr(a):return list(map(list,zip(*a)))
def plus(a,b,s=1):return [[x+s*y for x,y in zip(r,t)] for r,t in zip(a,b)]
def scale(a,s):return [[s*x for x in r] for r in a]
def zero(n):return [[Q(0)]*n for _ in range(n)]
def block(a,b,c,d):return [r+s for r,s in zip(a,b)]+[r+s for r,s in zip(c,d)]
def rev(n):return [[Q(i+j==n-1) for j in range(n)] for i in range(n)]
def kron(a,b):return [[x*y for x in ar for y in br] for ar in a for br in b]

def lower_factor(p):
    n=len(p);m=[r[:] for r in p];l=eye(n);r=eye(n)
    for i in range(n):
        c=max((j for j in range(n) if m[i][j]),default=None)
        if c is None:continue
        a=m[i][c]
        for k in range(i+1,n):
            v=m[k][c]/a
            if v:
                m[k]=[x-v*y for x,y in zip(m[k],m[i])]
                for j in range(n):l[j][i]+=v*l[j][k]
        for j in range(c):
            v=m[i][j]/a
            if v:
                for k in range(n):m[k][j]-=v*m[k][c]
                r[c]=[x+v*y for x,y in zip(r[c],r[j])]
    pi=[[Q(bool(x)) for x in row] for row in m]
    for j in range(n):
        a=next((m[i][j] for i in range(n) if m[i][j]),Q(1))
        r[j]=[a*x for x in r[j]]
    assert mul(mul(l,pi),r)==p
    return inv(l),pi,inv(r)

rng=Random(104);cases=0;lifted=0
for m in range(2,7):
    I,Z,C=eye(m),zero(m),rev(m)
    for rank in range(1,m):
        for trial in range(2):
            for attempt in range(500):
                U=eye(m)
                for _ in range(5*m):
                    a,b=rng.sample(range(m),2);v=rng.choice((-2,-1,1,2))
                    U[a]=[x+v*y for x,y in zip(U[a],U[b])]
                diag=[[Q(i==j and i<rank) for j in range(m)] for i in range(m)]
                P=mul(mul(U,diag),inv(U))
                if all(f.rank([row[:k] for row in P[:k]])==k for k in range(1,rank+1)):break
            else:raise AssertionError('generic sample not found')
            L,Pi,R=lower_factor(mul(P,C))
            E=[[Q(i==j) for j in range(rank)] for i in range(m)]
            F=[[Q(i==m-1-j) for j in range(rank)] for i in range(m)]
            assert Pi==mul(E,tr(F))
            DP=block(plus(I,P,-1),mul(P,C),mul(C,P),mul(mul(C,plus(I,P,-1)),C))
            Qmat=block(L,Z,Z,inv(R));g=mul(mul(Qmat,DP),inv(Qmat))
            A=[plus(g,eye(2*m),-1)[i][:m] for i in range(rank)]
            B=[[g[m+i][m+m-1-j]-Q(i==m-1-j) for j in range(rank)] for i in range(m)]
            assert plus(mul(A,E),mul(tr(F),B))==scale(eye(rank),-2)
            K=plus(scale(mul(plus(B,F),tr(E)),-1),mul(mul(F,A),plus(I,mul(E,tr(E)),-1)))
            S=block(I,Z,K,I)
            target=block(plus(I,mul(E,tr(E)),-1),Pi,tr(Pi),plus(I,mul(F,tr(F)),-1))
            assert mul(mul(S,g),inv(S))==target
            for atoms in (1,2):
                If,Cf,Zf=eye(atoms),rev(atoms),zero(m*atoms)
                Qf=block(kron(L,If),Zf,Zf,kron(inv(R),If))
                Sf=block(eye(m*atoms),Zf,kron(K,Cf),eye(m*atoms))
                Df=block(kron(plus(I,P,-1),If),kron(mul(P,C),Cf),kron(mul(C,P),Cf),kron(mul(mul(C,plus(I,P,-1)),C),If))
                want=block(kron(plus(I,mul(E,tr(E)),-1),If),kron(Pi,Cf),kron(tr(Pi),Cf),kron(plus(I,mul(F,tr(F)),-1),If))
                assert mul(mul(mul(mul(Sf,Qf),Df),inv(Qf)),inv(Sf))==want
                assert kron(rev(rank),Cf)==rev(rank*atoms)
                assert all(Qf[i][j]==Sf[i][j]==0 for i in range(2*m*atoms) for j in range(i+1,2*m*atoms))
                lifted+=1
            cases+=1

addresses=0
for n in range(1,5):
    for data in itertools.product(range(3),repeat=2*n):
        H,D=list(data[:n]),list(data[n:]);old=(H[:],D[:])
        D=[(d-h)%3 for h,d in zip(H,D)];H,D=D[::-1],H[::-1]
        D=[(d+h)%3 for h,d in zip(H,D)];H,D=D[::-1],H[::-1]
        D=[(h-d)%3 for h,d in zip(H,D)]
        assert (H,D)==old[::-1];addresses+=1

a=Q(4019,50000000);theta=Q(1,1000);old=Q(384599,10**10)
saving=(1-theta)*a+theta*old
assert saving==Q(803380799,10**13) and theta>saving
result=dict(status='PASS',rational_projectors=cases,atom_lift_cases=lifted,
    exhaustive_ordinary_wrapper_addresses=addresses,stopped_saving=str(saving),
    scope='Exact finite algebra and exponent identity; atom streaming uses the retained ordered-affine contract')
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
