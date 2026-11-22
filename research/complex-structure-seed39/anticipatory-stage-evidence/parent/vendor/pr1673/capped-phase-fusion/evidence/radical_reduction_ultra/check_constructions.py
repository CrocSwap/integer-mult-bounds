#!/usr/bin/env python3
"""Exact finite controls for two proposed outer-reduction refinements.
No selected supplier or producer code is imported. Apache-2.0.
"""
from fractions import Fraction as F
from itertools import product
import json, random
from pathlib import Path

OPS = 0

def add(a, b, sign=1):
    return [[x + sign*y for x,y in zip(ar,br)] for ar,br in zip(a,b)]

def mul(a,b):
    global OPS
    n=len(a)
    assert n and n & (n-1)==0 and len(b)==n
    if n==1:
        OPS += 1
        return [[a[0][0]*b[0][0]]]
    h=n//2
    def cut(x,i,j): return [r[j:j+h] for r in x[i:i+h]]
    A,B,C,D=(cut(a,0,0),cut(a,0,h),cut(a,h,0),cut(a,h,h))
    E,G,H,J=(cut(b,0,0),cut(b,0,h),cut(b,h,0),cut(b,h,h))
    m1=mul(add(A,D),add(E,J));m2=mul(add(C,D),E)
    m3=mul(A,add(G,J,-1));m4=mul(D,add(H,E,-1))
    m5=mul(add(A,B),J);m6=mul(add(C,A,-1),add(E,G))
    m7=mul(add(B,D,-1),add(H,J))
    c00=add(add(add(m1,m4),m5,-1),m7)
    c01=add(m3,m5);c10=add(m2,m4)
    c11=add(add(add(m1,m2,-1),m3),m6)
    return [x+y for x,y in zip(c00,c01)]+[x+y for x,y in zip(c10,c11)]

def classical(a,b):
    return [[sum(x*y for x,y in zip(ar,bc)) for bc in zip(*b)] for ar in a]

def inverse(a):
    n=len(a); c=[list(r)+[F(i==j) for j in range(n)] for i,r in enumerate(a)]
    for i in range(n):
        j=next(j for j in range(i,n) if c[j][i]);c[i],c[j]=c[j],c[i]
        v=c[i][i];c[i]=[x/v for x in c[i]]
        for j in range(n):
            if j!=i:
                v=c[j][i];c[j]=[x-v*y for x,y in zip(c[j],c[i])]
    return [r[n:] for r in c]

def block_solve(a,rhs,width):
    """Block lower-triangular solve using seven-product multiplication.
    A has scalar lower bandwidth at most width; RHS columns padded per batch.
    """
    global OPS
    n=len(a); k=len(rhs[0]);N=((n+width-1)//width)*width
    aa=[[F(0) for _ in range(N)] for _ in range(N)]
    for i in range(N):
        aa[i][i]=F(1)
        if i<n:aa[i][:n]=a[i]
    result=[[F(0) for _ in range(k)] for _ in range(n)]
    inverses=[]
    for i in range(0,N,width):
        inverses.append(inverse([r[i:i+width] for r in aa[i:i+width]]))
    for col in range(0,k,width):
        prev=[[F(0) for _ in range(width)] for _ in range(width)]
        for block,i in enumerate(range(0,N,width)):
            cur=[[rhs[i+j][col+t] if i+j<n and col+t<k else F(0)
                  for t in range(width)] for j in range(width)]
            if i:
                lower=[r[i-width:i] for r in aa[i:i+width]]
                cur=add(cur,mul(lower,prev),-1)
            solved=mul(inverses[block],cur)
            for j in range(width):
                for t in range(width):
                    if i+j<n and col+t<k:result[i+j][col+t]=solved[j][t]
            prev=solved
    return result

# Gaussian rational pair helpers. C entries a=(1+i)/2, b=(1-i)/2.
def ga(x=0,y=0):return (F(x),F(y))
def plus(x,y):return (x[0]+y[0],x[1]+y[1])
def times(x,y):return (x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0])
a,b=ga(F(1,2),F(1,2)),ga(F(1,2),-F(1,2))
def c_axes(v, axes, d):
    v=list(v)
    for axis in axes:
        w=[ga() for _ in v]
        for i in range(1<<d):
            if not(i>>axis&1):
                j=i|(1<<axis)
                w[i]=plus(times(a,v[i]),times(b,v[j]))
                w[j]=plus(times(b,v[i]),times(a,v[j]))
        v=w
    return v

def reserve_schedule(d,k,g,row_bits=0):
    """Reserve enough complete K chunks for 3hG dirty bits and row bits.
    Stop when ceiling costs do not shrink; these tiny cases are literal leaves.
    """
    pending=list(range(d));stages=[]
    while len(pending)>4:
        h=len(pending); r=(3*h*g+row_bits+k-1)//k
        if r>=h or h-r<1:break
        reserved=pending[:r];active=pending[r:]
        assert r*k >= 3*h*g+row_bits
        stages.append(dict(active=active,reserved=reserved))
        pending=reserved
    stages.append(dict(active=pending,reserved=[]))
    flat=[x for s in stages for x in s['active']]
    assert sorted(flat)==list(range(d)) and len(set(flat))==d
    return stages

def run():
    global OPS
    rng=random.Random(128731);mm=0;solve=0;rhs_entries=0
    for size in (1,2,4,8):
        for _ in range(5):
            A=[[F(rng.randint(-3,3),4) for _ in range(size)] for _ in range(size)]
            B=[[F(rng.randint(-3,3),4) for _ in range(size)] for _ in range(size)]
            before=OPS
            assert mul(A,B)==classical(A,B)
            assert OPS-before==7**(size.bit_length()-1)
            mm+=1
    for width in (1,2,4,8):
        for n in (1,3,7,10,17):
            for k in (1,3,9):
                A=[[F(0) for _ in range(n)] for _ in range(n)]
                for i in range(n):
                    A[i][i]=F(1)
                    for j in range(max(0,i-width),i):A[i][j]=F(rng.randint(-2,2),8*width)
                B=[[F(rng.randint(-4,4),8) for _ in range(k)] for _ in range(n)]
                X=block_solve(A,B,width)
                assert classical(A,X)==B
                assert X==classical(inverse(A),B)
                solve+=1;rhs_entries+=n*k
    schedule_cases=0;exact_entries=0
    for d in range(1,1001):
        s=reserve_schedule(d,128,1,8)
        assert sum(len(t['active']) for t in s)==d
        assert len(s)<=d
        schedule_cases+=1
    for d in range(1,7):
        s=reserve_schedule(d,8,1)
        for col in range(1<<d):
            v=[ga(int(i==col)) for i in range(1<<d)]
            for t in s:v=c_axes(v,t['active'],d)
            for row in range(1<<d):
                z=ga(1)
                for bit in range(d):z=times(z,b if (row^col)>>bit&1 else a)
                assert v[row]==z;exact_entries+=1
    # Meaningful failure controls: the unresolved reserved coordinates matter.
    s=reserve_schedule(6,8,1)
    v=[ga(int(i==0)) for i in range(64)]
    full=c_axes(v,range(6),6)
    omitted=c_axes(v,s[0]['active'],6)
    assert omitted!=full
    # A wrong block dependency (drop the preceding solved block) fails.
    A=[[F(1),F(0)],[F(1,4),F(1)]]; B=[[F(1)],[F(1)]]
    assert B!=block_solve(A,B,1)
    result=dict(status='PASS_EXACT_SCOPED_CONTROLS',strassen_cases=mm,
        blocked_lower_solve_cases=solve,rhs_entries=rhs_entries,
        reserve_schedules=schedule_cases,complex_tensor_matrix_entries=exact_entries,
        negative_controls=['omit_reserved_axes','drop_preceding_solve_block'],
        scalar_products_executed=OPS,
        scope='Finite exact identities only; not a tape simulator or all-size compiler proof.')
    print(json.dumps(result,indent=2))
    Path(__file__).with_name('CONTROLS.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':run()
