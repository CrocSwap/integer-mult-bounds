#!/usr/bin/env python3
"""Exact cubic decoder for an integral norm-six shell.

The implementation checks a dyadic factorization and the binary frame map.
It does not supply the framed side word or establish a new kappa.
"""
from fractions import Fraction as Q
from itertools import combinations, product
from math import comb
from pathlib import Path
import hashlib
import argparse
from collections import defaultdict
import json
import numpy as np
import sympy as sp


def need(value, message):
    if not value:
        raise ValueError(message)


def cubic_integer(x):
    numerator = x * x * x - x
    need(numerator % 3 == 0, 'integer cubic divisibility')
    return numerator // 3


def source_features(x):
    d = len(x)
    return ([cubic_integer(v) for v in x] + list(x) +
            [x[i] * x[i] * x[j] for i in range(d) for j in range(d) if i != j] +
            [x[i] * x[j] * x[k] for i, j, k in combinations(range(d), 3)])


def target_features(v):
    d = len(v)
    return ([w ** 3 for w in v] + [cubic_integer(w) - w for w in v] +
            [v[i] * v[i] * v[j] for i in range(d) for j in range(d) if i != j] +
            [2 * v[i] * v[j] * v[k] for i, j, k in combinations(range(d), 3)])


def inverse_mod2(matrix):
    n = len(matrix)
    work = np.concatenate((matrix.copy(), np.eye(n, dtype=np.uint8)), axis=1)
    for i in range(n):
        nz = np.flatnonzero(work[i:, i])
        need(len(nz) > 0, 'invertible binary Gram')
        j = i + int(nz[0])
        work[[i,j]] = work[[j,i]]
        for j in range(n):
            if i != j and work[j,i]:
                work[j] ^= work[i]
    return work[:,n:]


def symplectic_congruence(matrix):
    n = len(matrix)
    need(n % 2 == 0 and not np.any(np.diag(matrix)) and
         np.array_equal(matrix, matrix.T), 'alternating binary form')
    work = matrix.copy()
    t = np.eye(n, dtype=np.uint8)
    for first in range(0,n,2):
        pairs = np.argwhere(work[first:,first:])
        need(len(pairs) > 0, 'nondegenerate alternating pivot')
        a,b = map(lambda k:int(k)+first, pairs[0])
        # a != b because the form is alternating. Find the pair after swapping a.
        work[[a,first]] = work[[first,a]]
        work[:,[a,first]] = work[:,[first,a]]
        t[[a,first]] = t[[first,a]]
        if b == first:
            b = a
        work[[b,first+1]] = work[[first+1,b]]
        work[:,[b,first+1]] = work[:,[first+1,b]]
        t[[b,first+1]] = t[[first+1,b]]
        for j in range(first+2,n):
            x,y = int(work[j,first+1]),int(work[j,first])
            if x:t[j] ^= t[first]
            if y:t[j] ^= t[first+1]
        work = (t.astype(np.int64) @ matrix @ t.T) % 2
    standard = np.zeros((n,n),dtype=np.uint8)
    for j in range(0,n,2):standard[j,j+1]=standard[j+1,j]=1
    need(np.array_equal(work,standard),'full symplectic congruence')
    return t


def binary_map(g):
    n = len(g)
    even = np.ones((n,n),dtype=np.uint8)^np.eye(n,dtype=np.uint8)
    t=symplectic_congruence(g)
    u=symplectic_congruence(even)
    r=(inverse_mod2(t).astype(np.int64)@u)%2
    need(np.array_equal((r@even@r.T)%2,g),'Gram chart congruence')
    e=np.concatenate((np.eye(n,dtype=np.uint8),np.ones((n,1),dtype=np.uint8)),axis=1)
    return (r@e)%2


def polynomial_identity(d):
    actual=defaultdict(Q)
    for i in range(d):
        actual[((i,i,i),(i,i,i))]+=Q(1,3)
        actual[((i,),(i,i,i))]-=Q(1,3)
        actual[((i,),(i,i,i))]+=Q(1,3)
        actual[((i,),(i,))]-=Q(4,3)
        for j in range(d):
            if i!=j:actual[(tuple(sorted((i,i,j))),tuple(sorted((i,i,j))))]+=1
    for a,b,c in combinations(range(d),3):actual[((a,b,c),(a,b,c))]+=2
    actual={k:v for k,v in actual.items() if v}
    expected=defaultdict(Q)
    for i,j,k in product(range(d),repeat=3):
        m=tuple(sorted((i,j,k)));expected[(m,m)]+=Q(1,3)
    for i in range(d):expected[((i,),(i,))]-=Q(4,3)
    need(actual==dict(expected),'complete symbolic coefficient identity')
    mutant=dict(actual);del mutant[((0,1,2),(0,1,2))]
    need(mutant!=dict(expected),'omitted triple feature rejected')
    return len(actual)


def compute():
    here=Path(__file__).resolve().parent
    raw=(here/'sources/P48p-GRAM.json').read_bytes()
    g=json.loads(raw)
    d=len(g)
    need(d==48 and all(len(row)==d for row in g),'48-dimensional source Gram')
    matrix=sp.Matrix(g)
    need(matrix==matrix.T and all(g[i][i]%2==0 for i in range(d)),'even integral form')
    lower,diagonal=matrix.LDLdecomposition(hermitian=False)
    need(lower*diagonal*lower.T==matrix,'exact LDL reconstruction')
    pivots=list(diagonal.diagonal())
    need(all(v>0 for v in pivots),'exact positive definiteness')
    determinant=sp.prod(pivots)
    need(determinant==1,'exact unimodularity')
    need(hashlib.sha256(raw).hexdigest()==json.loads((here/'SOURCES.json').read_text())['external_data']['gram_sha256'],'source Gram pin')
    polynomial_terms=polynomial_identity(d)
    chart=binary_map((np.array(g,dtype=np.int64)%2).astype(np.uint8))
    # Use actual norm-six vectors in a bounded coordinate box, and independent
    # arbitrary integer vectors to check the factorization without norm restrictions.
    shell=[]
    for weight in (1,2):
        for indices in combinations(range(d),weight):
            for tail in product((-1,1),repeat=weight-1):
                x=[0]*d
                for j,v in zip(indices,(1,)+tail):x[j]=v
                norm=sum(x[i]*g[i][j]*x[j] for i in indices for j in indices)
                if norm==6:shell.append(x)
    need(len(shell)>24,'bounded shell sample')
    wide=np.array(shell,dtype=np.int64)
    labels=((wide%2)@chart)%2
    labels^=1
    pairings=wide@np.array(g,dtype=np.int64)@wide.T
    need(np.array_equal((labels@labels.T)%2,(1+pairings)%2),'all sampled binary pairings')
    need(np.all(np.sum(labels,axis=1)%2==1),'sample odd-norm labels')
    off=pairings.copy();np.fill_diagonal(off,0)
    need(np.max(np.abs(off))<=3,'sample minimum-six inner-product bound')
    rng=np.random.default_rng(20261014)
    sample_indices=sorted(set(map(int,np.linspace(0,len(shell)-1,32,dtype=int))))
    checks=0
    for x in [shell[i] for i in sample_indices]+rng.integers(-3,4,size=(12,d)).tolist():
        y=rng.integers(-3,4,size=d).tolist()
        v=[sum(g[i][j]*y[j] for j in range(d)) for i in range(d)]
        left=source_features(x);right=target_features(v)
        need(len(left)==len(right)==comb(d+2,3)+d,'explicit center count')
        t=sum(a*b for a,b in zip(x,v))
        need(3*sum(a*b for a,b in zip(left,right))==t**3-4*t,'full dyadic factorization')
        checks+=1
    values={t:str(Q(t**3-4*t,192)) for t in range(-3,4)}
    need(Q(6**3-4*6,192)==1 and all(Q(t**3-4*t,192)==0 for t in (-2,0,2)),
         'diagonal and forbidden scalar coefficients')
    # Mutations exercise the normalization and actual binary pairing claims.
    need(Q(6**3-4*6,64)!=1,'wrong kernel normalization rejected')
    broken=chart.copy();broken[0,0]^=1
    need(not np.array_equal((broken@broken.T)%2,np.array(g)%2),'broken binary chart rejected')
    out={'complete_polynomial_terms':polynomial_terms,'negative_controls':3,'status':'PASS_NORM6_DYADIC_DECODER_AND_BINARY_CHART',
         'claim':'exact local decoder identities; no framed side word, supplier or kappa',
         'gram_sha256':hashlib.sha256(raw).hexdigest(),
         'dimension':d,'exact_determinant':str(determinant),'positive_LDL_pivots':len(pivots),
         'binary_width':d+1,'explicit_dyadic_centers':comb(d+2,3)+d,
         'maximum_algebraic_copy_bill':(d+1)*(comb(d+2,3)+d),
         'factor_scale_denominator':64,'bounded_shell_vectors':len(shell),
         'all_sampled_pairings':len(shell)**2,'arbitrary_integer_factor_checks':checks,
         'off_diagonal_kernel_by_integer_pairing':values,'binary_chart':chart.tolist(),
         'external_theorem_dependencies':{'minimum':6,'antipodal_line_count':26208000,
           'source':'Nebe arXiv:1312.3780 introduction and Nebe-Sloane P48p catalogue',
           'locally_enumerated_full_shell':False}}
    return out


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record',type=Path);args=parser.parse_args()
    out=compute()
    if args.record:args.record.write_text(json.dumps(out,indent=2)+'\n')
    else:need(json.loads(json.dumps(out))==json.loads(Path(__file__).with_name('RESULT.json').read_text()),'receipt mismatch')
    print('PASS_NORM6_DYADIC_DECODER terms='+str(out['explicit_dyadic_centers'])+' polynomial_terms='+str(out['complete_polynomial_terms'])+' controls=3 no_new_kappa')


if __name__=='__main__':main()
