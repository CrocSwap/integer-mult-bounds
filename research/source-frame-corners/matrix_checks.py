"""Independent exact-Q reconstruction of the new lower/lower factorizations.

Uses integer unimodular controlled bases and tracks BOTH triangular factors.
No modular equality is accepted as a substitute for a rational equality.
"""
from fractions import Fraction as Q
from pathlib import Path
import json
import random
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'controlled-corners'))
from matrix_checks import eye,corner,nonsingular


def product(a,b):
    columns=list(zip(*b))
    return [[sum(x*y for x,y in zip(row,col)) for col in columns] for row in a]


def unimodular(n,rng):
    a=eye(n);b=eye(n)
    for _ in range(12*n):
        i,j=rng.sample(range(n),2);c=rng.choice((-1,1))
        a[i]=[x+c*y for x,y in zip(a[i],a[j])]
        for row in b:row[j]-=c*row[i]
    assert product(a,b)==eye(n)
    return a,b


def factor(a):
    n=len(a);m=[[Q(x) for x in row] for row in a];L=eye(n);R=eye(n);positions=[]
    for i in range(n):
        j=next((j for j in range(n-1,-1,-1) if m[i][j]),None)
        if j is None:continue
        positions.append((i,j));v=m[i][j]
        m[i]=[x/v for x in m[i]];L[i]=[x/v for x in L[i]]
        for k in range(i+1,n):
            v=m[k][j]
            if v:
                m[k]=[x-v*y for x,y in zip(m[k],m[i])]
                L[k]=[x-v*y for x,y in zip(L[k],L[i])]
        for k in range(j):
            v=m[i][k]
            if v:
                for row in m:row[k]-=v*row[j]
                for row in R:row[k]-=v*row[j]
    assert all(not L[i][j] and not R[i][j] for i in range(n) for j in range(i+1,n))
    assert all(L[i][i] and R[i][i] for i in range(n))
    pi=[[int((i,j) in positions) for j in range(n)] for i in range(n)]
    assert m==pi
    assert product(product(L,a),R)==pi
    return positions


def check(h):
    H=h*h;n=h*H;r=h-1;rng=random.Random(100*h)
    for attempt in range(100):
        K,Ki=unimodular(H,rng)
        pairs=[unimodular(h,rng) for _ in range(H)]
        G=[x[0] for x in pairs];Gi=[x[1] for x in pairs]
        S=[[G[i][a][b]*K[i][j] for b in range(h) for j in range(H)] for a in range(h) for i in range(H)]
        Si=[[Ki[j][i]*Gi[i][b][a] for a in range(h) for i in range(H)] for b in range(h) for j in range(H)]
        assert product(S,Si)==eye(n)
        U={j*h+1 for j in range(h)}
        diagonals={
            'A1':[int(i!=0 and not(a==0 and i in U)) for a in range(h) for i in range(H)],
            'A2':[int(a!=0) for a in range(h) for i in range(H)],
            'A3':[int(a!=0 and i!=0) for a in range(h) for i in range(H)],
            'A4':[int(a==0 and i>=h) for a in range(h) for i in range(H)],
            'A5':[int(a==0 and bool(i//h) and bool(i%h)) for a in range(h) for i in range(H)],
            'A6':[int(not(a==0 and i<h)) for a in range(h) for i in range(H)],
        }
        matrices={name:product([[x*d for x,d in zip(row,diagonal)] for row in S],Si)
                  for name,diagonal in diagonals.items()}
        required=[corner(matrices['A6'],h),corner(matrices['A1'],2*h),corner(matrices['A2'],H),
                  corner(matrices['A3'],H+r),corner(matrices['A3'],H),
                  corner(corner(matrices['A3'],H),r),corner(corner(matrices['A4'],H),h)]
        if h>=4:required.append(corner(corner(matrices['A5'],H),2*h-1))
        if not all(nonsingular([[x%1009 for x in row] for row in a],1009) for a in required):continue
        expected={
            'A6':[(i,i) for i in range(h,n-h)],
            'A1':[(i,i) for i in range(2*h,n-2*h)],
            'A2':[(i,n-H+i) for i in range(H)]+[(i,i) for i in range(H,n-H)],
            'A3':[(i,n-H+i) for i in range(r,H-r)]+[(i,i) for i in range(H+r,n-H-r)],
            'A4':[(i,n-H+i) for i in range(h,H-h)],
            'A5':[(i,n-H+i) for i in range(2*h-1,H-2*h+1)] if h>=4 else [],
        }
        profiles={}
        for name,blocks in expected.items():
            a=matrices[name]
            assert product(a,a)==a
            ps=factor(a)
            assert len(ps)==sum(diagonals[name])
            assert set(blocks)<=set(ps),(h,name)
            profiles[name]=dict(rank=len(ps),pivots=ps,block_pivots=blocks,
                               exact_lower_factors_reconstruct_partial_permutation=True)
        return dict(h=h,attempt=attempt+1,K=K,G=G,profiles=profiles,
                    all_equalities_over='Q',modular_test_used_only_to_filter_nonzero_minors=True)
    raise AssertionError('Could not find a simultaneous unimodular example')


if __name__=='__main__':
    rows=[]
    for h in (3,4):
        rows.append(check(h))
        print('PASS exact rational reconstruction at h=',h,flush=True)
    print('All six profiles admit one simultaneous rational basis at each tested h.')
