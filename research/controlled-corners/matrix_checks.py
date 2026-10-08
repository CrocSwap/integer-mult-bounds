"""Exact finite-field controls for simultaneous controlled pivot profiles.

The general rational existence proof is separate. Matrices stored in the
report are integer lifts; nonzero modular determinants also certify that
the corresponding rational determinants are nonzero for these examples.
"""
from pathlib import Path
import json
import random


def eye(n):return [[int(i==j) for j in range(n)] for i in range(n)]


def multiply(a,b,p):
    result=[[0]*len(b[0]) for _ in a]
    for i,row in enumerate(a):
        for k,x in enumerate(row):
            if x:
                for j,y in enumerate(b[k]):
                    result[i][j]=(result[i][j]+x*y)%p
    return result


def inverse(a,p):
    n=len(a);b=[row[:]+ident for row,ident in zip(a,eye(n))]
    for i in range(n):
        pivot=next((j for j in range(i,n) if b[j][i]),None)
        if pivot is None:raise ValueError('singular')
        b[i],b[pivot]=b[pivot],b[i]
        z=pow(b[i][i],-1,p);b[i]=[(z*x)%p for x in b[i]]
        for j in range(n):
            if j!=i and b[j][i]:
                z=b[j][i];b[j]=[(x-z*y)%p for x,y in zip(b[j],b[i])]
    return [row[n:] for row in b]


def nonsingular(a,p):
    try:inverse(a,p);return True
    except ValueError:return False


def corner(a,k):return [row[-k:] for row in a[:k]]


def pivots(matrix,p):
    """Top-to-bottom, rightmost pivot; only lower/lower operations."""
    a=[row[:] for row in matrix];positions=[]
    for i,row in enumerate(a):
        j=next((j for j in range(len(row)-1,-1,-1) if row[j]),None)
        if j is None:continue
        positions.append((i,j));inv=pow(a[i][j],-1,p)
        for k in range(i+1,len(a)):
            z=a[k][j]*inv%p
            if z:a[k]=[(x-z*y)%p for x,y in zip(a[k],a[i])]
        for k in range(j):
            z=a[i][k]*inv%p
            if z:
                for row in a:row[k]=(row[k]-z*row[j])%p
    return positions


def one(h,p=1009):
    H=h*h;m=h*H;r=h-1
    rng=random.Random(h)
    def invertible(n):
        while True:
            a=[[rng.randrange(p) for _ in range(n)] for _ in range(n)]
            if nonsingular(a,p):return a
    q=0
    U={j*h+1 for j in range(h)}
    U4=set(range(h,H))
    U5={i for i in range(H) if i//h and i%h}
    ranks={'A1':m-2*h,'A2':m-H,'A3':m-H-h+1,'A4':H-h,'A5':(h-1)**2}
    for attempt in range(100):
        K=invertible(H);Gs=[invertible(h) for _ in range(H)]
        S=[[Gs[i][a][b]*K[i][j]%p for b in range(h) for j in range(H)]
           for a in range(h) for i in range(H)]
        Si=inverse(S,p)
        diagonal={
            'A1':[int(i!=q and not(a==0 and i in U)) for a in range(h) for i in range(H)],
            'A2':[int(a!=0) for a in range(h) for i in range(H)],
            'A3':[int(a!=0 and i!=q) for a in range(h) for i in range(H)],
            'A4':[int(a==0 and i in U4) for a in range(h) for i in range(H)],
            'A5':[int(a==0 and i in U5) for a in range(h) for i in range(H)],
        }
        matrices={name:multiply([[x*d for x,d in zip(row,diag)] for row in S],Si,p)
                  for name,diag in diagonal.items()}
        C3=corner(matrices['A3'],H)
        C4=corner(matrices['A4'],H)
        tests=[nonsingular(corner(matrices['A1'],2*h),p),
               nonsingular(corner(matrices['A2'],H),p),
               nonsingular(corner(matrices['A3'],H+r),p),
               nonsingular(C3,p),nonsingular(corner(C3,r),p),
               nonsingular(corner(C4,h),p)]
        if h>=4:tests.append(nonsingular(corner(corner(matrices['A5'],H),2*h-1),p))
        if not all(tests):continue
        expected={
            'A1':[(i,i) for i in range(2*h,m-2*h)],
            'A2':[(i,m-H+i) for i in range(H)]+[(i,i) for i in range(H,m-H)],
            'A3':[(i,m-H+i) for i in range(r,H-r)]+[(i,i) for i in range(H+r,m-H-r)],
            'A4':[(i,m-H+i) for i in range(h,H-h)],
            'A5':[(i,m-H+i) for i in range(2*h-1,H-2*h+1)] if h>=4 else [],
        }
        profiles={}
        for name,a in matrices.items():
            assert multiply(a,a,p)==a
            ps=pivots(a,p)
            assert len(ps)==ranks[name]
            assert set(expected[name])<=set(ps),(h,name)
            profiles[name]=dict(rank=ranks[name],pivots=ps,
                contiguous_pivots=expected[name],remaining_singletons=len(ps)-len(expected[name]))
        return dict(h=h,modulus=p,attempt=attempt+1,K=K,G=Gs,profiles=profiles,
                    all_idempotents_and_pivot_profiles_exact=True)
    raise AssertionError('No simultaneous example found')


if __name__=='__main__':
    rows=[one(h) for h in (3,4,5)]
    for row in rows:
        print('PASS h=',row['h'],'singleton pivots:',
              {k:v['remaining_singletons'] for k,v in row['profiles'].items()})
