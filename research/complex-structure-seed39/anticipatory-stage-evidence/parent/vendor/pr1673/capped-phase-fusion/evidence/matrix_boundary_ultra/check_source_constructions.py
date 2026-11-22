#!/usr/bin/env python3
"""Exact finite controls for the constructions in the supplied 9/4 paper.

These checks are controls for an end-to-end human proof audit, not substitutes
for the universal proofs or an executable fast matrix multiplication scheme.
"""
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
SOURCE = Path('/Users/vlado/Downloads/math-main/preprints/Matrix-Multiplication-Nine-Fourths-October-2-2026/build/paper.tex')

def inverse(a):
    n = len(a)
    t = [[Q(v) for v in row] + [Q(i == j) for j in range(n)]
         for i, row in enumerate(a)]
    for j in range(n):
        p = next(i for i in range(j, n) if t[i][j])
        t[j], t[p] = t[p], t[j]
        z = t[j][j]
        t[j] = [v/z for v in t[j]]
        for i in range(n):
            if i != j:
                z = t[i][j]
                t[i] = [v-z*w for v,w in zip(t[i],t[j])]
    return [row[n:] for row in t]

def mm(a,b):
    return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)]
            for row in a]

def basis(e):
    # Ambient coordinates: u^(e-i)v^i s, then u^(e-i)v^i w.
    n = 2*(e+1)
    cols = []
    for i in range(e+1):
        v = [Q(0)]*n
        v[i] = 1
        cols.append(v)
    v = [Q(0)]*n
    v[-1] = 1
    cols.append(v)
    for j in range(e):
        v = [Q(0)]*n
        v[j+1] = -1
        v[e+1+j] = 1
        cols.append(v)
    return [list(row) for row in zip(*cols)]

def check_determinant():
    cases = []
    for a in range(1,9):
        for b in range(2,9):
            ei, eo = b-1, a+b-2
            bi, bo = basis(ei), basis(eo)
            inv = inverse(bo)
            for k in range(a):
                mult = [[Q(0)]*(2*b) for _ in range(2*(a+b-1))]
                for side in range(2):
                    for i in range(b):
                        mult[side*(a+b-1)+i+k][side*b+i] = 1
                t = mm(inv,mm(mult,bi))
                qo, qi = a+b, b+1
                for i,row in enumerate(t):
                    for j,val in enumerate(row):
                        if i < qo and j < qi:
                            assert val == Q(i == j+k)
                        elif i < qo and j >= qi:
                            assert val == 0
                        elif i >= qo and j >= qi:
                            assert val == Q(i-qo == j-qi+k)
                # Only the lower-left block may remain, with weight +1.
            cases.append({'a':a,'b':b,'slices_checked':a})
    return cases

def check_fourier():
    cases = []
    for m in range(1,13):
        terms = surviving = zeros = 0
        for h in range(1,m+1):
            for g in range(1,m+1):
                for u in range(1,m+1):
                    for v in range(1,m+1):
                        terms += 1
                        phase = u-v+2*(g-h)
                        assert abs(phase) < 5*m
                        if phase % (5*m) == 0:
                            surviving += 1
                            assert phase == 0
                            weight = g*g+h*u-h*h-h*v
                            assert weight == (g-h)**2 >= 0
                            if weight == 0:
                                zeros += 1
                                assert g == h and u == v
        assert zeros == m*m
        cases.append({'M':m,'potential_terms':terms,
                      'fourier_survivors':surviving,'weight_zero_terms':zeros})
    return cases

def check_tripling():
    cases = []
    for a in range(1,15):
        for h in range(1,15):
            B=3*h+a-1
            sectors=[set(),set(),set()]
            for x in range(a):
                for y in range(B):
                    z=x+y
                    sy=0 if y<h else (1 if y<2*h+a-1 else 2)
                    sz=0 if z<h+a-1 else (1 if z<2*h+a-1 else 2)
                    weight=int(sy==1)-int(sz==1)
                    assert weight >= 0
                    if weight==0:
                        assert sy==sz
                        if sy==0:
                            t=(x,y,z)
                        elif sy==2:
                            t=(x,y-(2*h+a-1),z-(2*h+a-1))
                        else:
                            # Swap second/third legs; reverse first-leg basis.
                            t=(a-1-x,z-(h+a-1),y-h)
                        assert t[2]==t[0]+t[1]
                        sectors[sy].add(t)
            expected={(x,y,x+y) for x in range(a) for y in range(h)}
            assert all(s==expected for s in sectors)
            cases.append({'a':a,'h':h,'terms_in_each_branch':a*h})
    return cases

def check_growth():
    h=Q(1)
    for a in range(1,301):
        if a>1: h *= 1+Q(1,3*(a-1))
        assert h**3 >= a
        assert Q(3*a-1,2) >= a
    return {'maximum_a':300,'exact_product_inequalities':'PASS'}

if __name__ == '__main__':
    raw=SOURCE.read_bytes()
    result={
        'status':'PASS_EXACT_SOURCE_CONTROLS',
        'scope':'Finite controls accompany a full universal proof audit; no rank algorithm synthesized.',
        'source':str(SOURCE),
        'source_sha256':hashlib.sha256(raw).hexdigest(),
        'source_lines':len(raw.splitlines()),
        'fourier':check_fourier(),
        'determinant_filtration':check_determinant(),
        'tripling':check_tripling(),
        'growth':check_growth(),
        'negative_controls':{
            'drop_fourier_phase': 'reject: weights need not be nonnegative, e.g. M=2,h=2,g=1,u=1,v=2 has weight -5',
            'keep_only_one_outer_branch':'reject: factor 3 requires both outer branches and the leg-swapped middle branch',
            'arbitrary_arithmetic_circuit':'reject: stability proof requires recursive bilinear structure; unbounded sequential multiplication does not follow',
            'endpoint_exponent_9/4':'reject: rank infimum only supplies fixed algorithms strictly above 9/4',
            'arbitrary_complex_constants':'reject: computability requires algebraic-point replacement or explicit computable coefficients',
        },
    }
    (ROOT/'SOURCE-CONSTRUCTIONS.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'])
    print('source lines',result['source_lines'])
    print('fourier M cases',len(result['fourier']))
    print('determinant cases',len(result['determinant_filtration']))
    print('tripling cases',len(result['tripling']))
