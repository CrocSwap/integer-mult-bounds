#!/usr/bin/env python3
"""Two-stage unequal-axis characteristic and finite basis prescriptions.
See notes/two-stage-16-note.tex for the conditional physical and basis proof.
"""
from pathlib import Path
from collections import Counter
from math import comb,log,expm1
import json
HERE=Path(__file__).resolve().parent

def prescriptions(a,b):
    assert a==b+2 and b>=10
    R=list(range(a))+list(range(1,a))+[0]
    C=[a-1]+list(range(a-1))+list(range(a))
    matrices=[]
    for beta in range(b):
        entries={}
        def add(row,col):
            assert row not in entries or entries[row]==col
            assert col not in entries.values() or entries.get(row)==col
            entries[row]=col
        for i,c in enumerate(R):
            if i%b==beta:add(i//b,c)
        for j,c in enumerate(C):
            i=a*b-2*a+j
            if i%b==beta:add(i//b,c)
        unused=iter(c for c in range(a) if c not in entries.values())
        matrices.append([entries[r] if r in entries else next(unused) for r in range(a)])
    for edges in [[(0,b),(1,b+1)]+[(j+2,j+1) for j in range(b-2)]+[(0,b-1)],
                  [(b,0),(b+1,1),(b+1,2)]+[(j-2,j-1) for j in range(4,b+2)]]:
        seen={0}
        for _ in range(a):seen|={y for x,y in edges if x in seen}|{x for x,y in edges if y in seen}
        assert len(edges)==a-1 and len(seen)==a
    return matrices

def profile(A,B,aux=True,local=True):
    a,b=A['h'],B['h'];va,vb=comb(a,3),comb(b,3);N=va*vb;m=a*b
    # Each retained-total producer already includes its h centers.
    ba,bb=vb*A['R'],va*B['R'];W=2*N+ba+bb
    L=vb*A['loss']+va*B['loss'];D=N-2*L;s=W*m-D
    z=Counter()
    def ordinary(h,r,n):
        if local and 2*r>h:
            z[2*r-h]+=n;z[1]+=(h-r)*n
        else:z[1]+=r*n
    z[m-2*a]+=ba;z[m-2*b]+=bb
    if aux:z[a]+=ba;z[b]+=bb
    else:z[1]+=a*ba+b*bb
    d=a+b-1;z[m-2*d]+=2*N;z[1]+=d*2*N
    for row,copies in [(A,vb),(B,va)]:
        h=row['h']
        for r,n in enumerate(row['histogram']):ordinary(h,r,copies*n)
        ordinary(h,h-1,2*N)
    z[1]+=N  # Explicit Paureel copy correction, never a free operation.
    z=Counter({t:n for t,n in z.items() if n})
    assert z[1]>=0 and sum(t*n for t,n in z.items())==s
    def moment(a):return sum(n*t*expm1(a*log(m/t)) for t,n in z.items())-D
    lo,hi=0.,.001
    assert moment(lo)<0<moment(hi)
    for _ in range(70):
        mid=(lo+hi)/2
        if moment(mid)<0:lo=mid
        else:hi=mid
    return dict(a=a,b=b,m=m,N=N,W=W,L=L,s=s,deficit=D,rows=dict(sorted(z.items())),numeric_root=lo)
