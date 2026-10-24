"""Portable bounded-word banded LU/solve model, Apache-2.0.
Dugongue with substantial OpenAI Codex assistance.
Fraction is an independent test oracle, not used in band_solve().
"""
from fractions import Fraction
from random import Random
import json


def need(ok, why):
    if not ok:
        raise ValueError(why)


def band_solve(a, rhs, h, p, width, _same_matrix_factors=None):
    n=len(a);S=1<<p;limit=1<<width;ops=0;peak=0
    need(n>=1 and len(rhs)==n and h>=0 and p>=1,'shape')
    need(all(len(row)==2*h+1 for row in a),'band storage')
    a=[list(row) for row in a]
    def val(x):
        nonlocal ops,peak
        need(abs(x)<limit,'word overflow')
        ops+=1;peak=max(peak,abs(x).bit_length());return x
    def get(i,j):
        return a[i][j-i+h] if abs(i-j)<=h else 0
    def put(i,j,x):
        need(abs(i-j)<=h,'band fill escaped');a[i][j-i+h]=val(x)
    def mul(x,y):return val(val(x*y)//S)
    def div(x,y):
        need(y>0,'nonpositive pivot')
        return val(val(x*S)//y)
    val(S)
    for row in a:
        for entry in row: val(entry)
    for entry in rhs: val(entry)
    # The contract is A = I+E with strict row diagonal dominance.
    for i in range(n):
        total=abs(get(i,i)-S)+sum(abs(get(i,j)) for j in range(max(0,i-h),min(n,i+h+1)) if j!=i)
        need(total<=S//4,'near-identity contract')
    if _same_matrix_factors is not None:
        # Internal reuse requires factors prepared from these exact matrix bytes.
        a=[list(row) for row in _same_matrix_factors]
        need(len(a)==n and all(len(row)==2*h+1 for row in a),'factor shape')
        for row in a:
            for entry in row:val(entry)
    else:
        for k in range(n):
            pivot=get(k,k);need(pivot>=S//2,'lost pivot bound')
            for i in range(k+1,min(n,k+h+1)):
                factor=div(get(i,k),pivot);put(i,k,factor)
                for j in range(k+1,min(n,k+h+1)):
                    put(i,j,get(i,j)-mul(factor,get(k,j)))
                    ops+=8
                ops+=10
    y=[]
    for i in range(n):
        t=val(rhs[i]*S)
        for j in range(max(0,i-h),i):
            t=val(t-val(get(i,j)*y[j]));ops+=5
        y.append(val(t//S))
    x=[0]*n
    for i in range(n-1,-1,-1):
        t=val(y[i]*S)
        for j in range(i+1,min(n,i+h+1)):
            t=val(t-val(get(i,j)*x[j]));ops+=5
        x[i]=val(t//get(i,i))
    return dict(solution=x,factors=a,operations=ops,maximum_bits=peak,word_width=width)


class BandSystem:
    """Prepare once; retain ownership of the exact matrix and its factors."""
    def __init__(self,a,h,p,width):
        self.a=[list(row) for row in a];self.h=h;self.p=p;self.width=width
        out=band_solve(self.a,[0]*len(a),h,p,width)
        self.factors=out['factors'];self.preparation=out
    def solve(self,rhs):
        return band_solve(self.a,rhs,self.h,self.p,self.width,self.factors)


def check():
    rng=Random(20261022);cases=rows=0;max_error=Fraction(0);peak=0
    for n in (1,2,5,13,31):
        for h in (0,1,2,4):
            p=96;S=1<<p
            a=[[0]*(2*h+1) for _ in range(n)]
            for i in range(n):
                a[i][h]=S
                for j in range(max(0,i-h),min(n,i+h+1)):
                    if j!=i:a[i][j-i+h]=rng.randrange(-8,9)*(S//(128*max(1,h)))
            truth=[rng.randrange(-S,S) for _ in range(n)]
            rhs=[sum(a[i][j-i+h]*truth[j]//S for j in range(max(0,i-h),min(n,i+h+1))) for i in range(n)]
            out=band_solve(a,rhs,h,p,256)
            # Residual of the actual computed answer, evaluated exactly.
            error=max(abs(sum(Fraction(a[i][j-i+h],S)*out['solution'][j] for j in range(max(0,i-h),min(n,i+h+1)))-rhs[i]) for i in range(n))
            need(error<=10000*(h+1)**4,'native solve residual envelope')
            need(out['maximum_bits']<256,'native bound')
            max_error=max(max_error,error/S);peak=max(peak,out['maximum_bits']);cases+=1;rows+=n
    try:band_solve([[1<<20]],[1<<20],0,20,16)
    except ValueError:pass
    else:raise ValueError('undersized arithmetic word accepted')
    try:band_solve([[0]],[1],0,20,64)
    except ValueError:pass
    else:raise ValueError('singular diagonal accepted')
    return dict(status='PASS',banded_systems=cases,rows_checked=rows,
                maximum_normalized_residual=str(max_error),maximum_bits=peak,
                overflow_and_singular_controls=True,
                scope='finite bounded-word band solve; universal proof is separate')


if __name__=='__main__':print(json.dumps(check(),indent=2))
