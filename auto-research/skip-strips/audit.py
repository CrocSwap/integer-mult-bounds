#!/usr/bin/env python3
"""Independent defining-property checks of the fixed projector formula.

No imported projector/profiler implementation. Exact fractions only. The
canonical tests cover every envelope size at both dimensions; coordinate
permutation equivariance extends these identities to all cores/covers.
The mathematical extension is stated and proved in PROOF.md.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse
import json


def matrix(h,c,n):
    core=set(range(c)); outside=set(range(c,c+n))
    s=3-c; d=s*s+(c-1)*n
    w=[3+int(i in core) for i in range(h)]
    z=[3*(h+1)*int(i in core)-10 for i in range(h)]
    o=[int(i in outside) for i in range(h)]
    return [[Q(int(i==j and i in outside))+
             Q(s*o[i]*z[j]+3*(h+1)*s*w[i]*o[j]+n*w[i]*z[j]
               -3*(h+1)*(c-1)*o[i]*o[j],3*(h+1)*d)
             for j in range(h)] for i in range(h)]


def check_projector(h,c,n):
    A=matrix(h,c,n)
    # Pull every image column back by L^{-1}=I-J/(h+1), and verify it lies in E.
    for j in range(h):
        total=sum(A[i][j] for i in range(h))
        x=[A[i][j]-total/(h+1) for i in range(h)]
        assert len(set(x[:c]))==1 and sum(x)==3*x[0]
        assert all(x[i]==0 for i in range(c+n,h))
    # Each transformed basis vector of E is fixed; hence rank=n and A^2=A.
    for k in range(c,c+n):
        y=[Q(int(i==k))+Q(3+int(i<c),3-c) for i in range(h)]
        assert all(sum(A[i][j]*y[j] for j in range(h))==y[i] for i in range(h))
    # G'=L^{-T}(I-J/9)L^{-1}; symmetry identifies the unique orthogonal projector.
    coefficient=Q(9*h+19,9*(h+1)**2)
    cols=[sum(A[i][j] for i in range(h)) for j in range(h)]
    assert all(A[i][j]-coefficient*cols[j]==A[j][i]-coefficient*cols[i]
               for i in range(h) for j in range(h))
    if c==2:
        # Identity proving rank <=2 for SAME-core differences: the constant
        # rank-one term cancels, leaving a difference of two rank-one matrices.
        w=[3+int(i<c) for i in range(h)]
        z=[3*(h+1)*int(i<c)-10 for i in range(h)]
        o=[int(c<=i<c+n) for i in range(h)]
        assert all(A[i][j]==Q(int(i==j and o[i]))+Q(w[i]*z[j],3*(h+1))
                   -Q((w[i]-o[i])*(z[j]-3*(h+1)*o[j]),3*(h+1)*(n+1))
                   for i in range(h) for j in range(h))


def run():
    assert __debug__, 'Run without -O'
    cases=[]
    for h in (23,25):
        for c in (1,2):
            for n in range(1,h-c+1):
                check_projector(h,c,n)
                cases.append([h,c,n])
        # Source t: independent derivation from t^T G t=2, followed by conjugation.
        t=[int(i<3) for i in range(h)]
        p=[Q(x+3) for x in t]
        dual=[Q(x,2)-Q(5,3*(h+1)) for x in t]
        assert sum(x*y for x,y in zip(p,dual))==1
        assert all(x!=0 for x in p+dual)
        assert all(p[i]*dual[j] == Q((3+t[i])*(3*(h+1)*t[j]-10),6*(h+1))
                   for i in range(h) for j in range(h))
    return dict(exact_envelope_cases=len(cases),cases=cases,source_line_cases=2,
                checks=['image contained in envelope','identity on envelope basis',
                        'self adjoint in transformed rational metric',
                        'same-core rank-two difference identity','source line normalization'],
                scope='Exact canonical size cases, with coordinate-equivariance proof in PROOF.md; '
                      'full graph, matching and CRT profiles independently replayed by producer.py')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=run()
    if args.output:args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS independent exact projector audit:',result['exact_envelope_cases'],'envelopes')
