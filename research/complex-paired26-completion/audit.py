#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate stdlib arithmetic replay; imports no primary-verifier code.

Written in the same ChatGPT investigation, not an independent-author review.
Uses normalized Fraction elimination on the actual violation matrices, rather
than the primary streaming-integer / Bareiss-minor certificate route.
"""
import json
import sys
from fractions import Fraction as F
from itertools import combinations, product
from math import gcd, lcm
from pathlib import Path

P = [0,23,24,25,26,34,35,36,37,48,60,61,62,63,66,67,
     72,73,76,77,78,79,82,83,88,89]
A_FIRST = [F(x,2) for x in [1,-1,-1,-1,1,1,-1,1]]
B_FIRST = list(map(F,[0,0,0,0,0,0,-2,2]))
B_CANDIDATES = [23,25,30,34,36,61,63,66,73,77,79,82,89]


def check(ok, message):
    if not ok:
        raise RuntimeError(message)


def inner(u,v):
    check(len(u)==len(v), 'inner product dimensions')
    return sum(x*y for x,y in zip(u,v))


def binary_rank_low(rows):
    basis = {}
    for x in rows:
        while x:
            low = x & -x
            if low in basis:
                x ^= basis[low]
            else:
                basis[low] = x
                break
    return len(basis)


def fractional_rows(rows, width=8):
    basis = {}
    for row in rows:
        v = list(map(F,row))
        for p in sorted(basis):
            if v[p]:
                x = v[p]
                v = [a-x*b for a,b in zip(v,basis[p])]
        p = next((i for i,x in enumerate(v) if x),None)
        if p is not None:
            x = v[p]
            basis[p] = [a/x for a in v]
        if len(basis)==width:
            break
    return basis


def normalized(v):
    denominator = lcm(*(x.denominator for x in v))
    w = [int(x*denominator) for x in v]
    divisor = gcd(*w)
    check(divisor!=0, 'zero normalized vector')
    if next(x for x in w if x)<0:
        divisor=-divisor
    return tuple(x//divisor for x in w)


def line_kernel(basis):
    free = [j for j in range(8) if j not in basis]
    check(len(free)==1, 'kernel is not a line')
    v = [F(0)]*8
    v[free[0]]=F(1)
    for p in sorted(basis,reverse=True):
        v[p]=-sum(basis[p][j]*v[j] for j in range(p+1,8))
    return normalized(v)


def multiply(x,y):
    columns = list(zip(*y))
    return [[inner(r,c) for c in columns] for r in x]


def read_matrix(x):
    return [list(map(F,r)) for r in x]


def roots_and_labels():
    roots = set()
    for i in range(8):
        for j in range(i+1,8):
            for s,t in [(-2,-2),(-2,2),(2,-2),(2,2)]:
                x=[0]*8;x[i]=s;x[j]=t
                roots.add(max(tuple(x),tuple(-v for v in x)))
    for x in product([-1,1],repeat=8):
        if x.count(-1)%2==0:
            roots.add(max(x,tuple(-v for v in x)))
    roots=sorted(roots)
    check(len(roots)==120, 'root count')
    n=[]
    for x in roots:
        row=0
        for j,y in enumerate(roots):
            z,rem=divmod(inner(x,y),4)
            check(rem==0, 'nonintegral pairing')
            if (z+1)%2:
                row |= 1<<j
        n.append(row)
    check(binary_rank_low(n)==9, 'pairing rank')
    basis=[]
    for i,row in enumerate(n):
        if binary_rank_low([n[j] for j in basis]+[row])>len(basis):
            basis.append(i)
        if len(basis)==9:
            break
    labels=[sum(((row>>b)&1)<<k for k,b in enumerate(basis)) for row in n]
    check(basis==[0,1,2,3,6,12,20,30,42], 'pairing-row basis')
    return roots,n,labels


def main():
    path=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name('certificate.json')
    data=json.loads(path.read_text())
    check(data['schema']=='fixed-paired26-completion-v1', 'schema')
    check(data['geometry']['punctures']==P, 'fixed puncture')
    roots,n,labels=roots_and_labels()
    live=[j for j in range(120) if j not in P]
    rr=[[F(x,2) for x in roots[j]] for j in live]
    check(len(fractional_rows([roots[j] for j in live]))==8, 'R rank')
    root_map={normalized(list(map(F,r))):i for i,r in enumerate(roots)}
    directions={}; ranks={7:0,8:0}
    records=data['inventory']['matrices']
    check([r['lambda'] for r in records]==list(range(1,512)), 'all 511 functionals')
    for lam in range(1,512):
        rows=[roots[j] for j in live if (labels[j]&lam).bit_count()%2]
        echelon=fractional_rows(rows)
        rank=len(echelon)
        check(rank in ranks and rank==records[lam-1]['rank'], 'inventory rank mismatch')
        ranks[rank]+=1
        if rank==7:
            kernel=line_kernel(echelon)
            check(kernel in root_map, 'nonroot kernel line')
            j=root_map[kernel]
            check(j==records[lam-1]['kernel_root_index'], 'kernel index mismatch')
            directions.setdefault(j,[]).append(lam)
        else:
            check(records[lam-1]['kernel_root_index'] is None, 'full rank with claimed kernel')
    check(ranks=={7:29,8:482}, 'rank totals')
    check(sorted(directions)==sorted(P+[30]), 'complete reduced root set')
    def supp(v): return [j for j in live if inner(roots[j],v)!=0]
    for j in directions:
        dim=binary_rank_low(labels[i] for i in supp(roots[j]))
        check(dim==(7 if j==0 else 8), 'reduced support dimension')
    ea=[j for j in sorted(directions) if inner(roots[j],B_FIRST)==0]
    eb=[j for j in sorted(directions) if inner(roots[j],A_FIRST)==0]
    check(ea==[30] and eb==B_CANDIDATES, 'residual eligibility')
    check(all(inner(roots[30],roots[j]) for j in eb), 'orthogonality exclusion')
    sets=[]
    for indices in combinations(eb,7):
        if len(fractional_rows([roots[i] for i in indices]))==7:
            sets.append(list(indices))
    check(len(sets)==256 and sets==data['optimal_classification']['optimal_unordered_B_root_sets'],
          'complete optimal root-basis set')
    for name,expected in [('prior_69',[6]+[9]*7),('optimal_62',[6]+[8]*7),
                          ('sharp_reduced_A_branch_67',[6,7]+[9]*6),
                          ('complex_isotropic_control',[6,8,9,8,8,8,8,8])]:
        report=data[name]
        complex_case=name=='complex_isotropic_control'
        a=read_matrix(report['A_real_rows' if complex_case else 'A_rows'])
        b=read_matrix(report['B_real_rows' if complex_case else 'B_rows'])
        ai=read_matrix(report['A_imag_rows']) if complex_case else [[F(0)]*8 for _ in range(8)]
        bi=read_matrix(report['B_imag_rows']) if complex_case else [[F(0)]*8 for _ in range(8)]
        check(len(a)==len(b)==len(ai)==len(bi)==8 and all(len(r)==8 for m in (a,b,ai,bi) for r in m),
              'matrix shape')
        check([r[0] for r in a]==A_FIRST and [r[0] for r in b]==B_FIRST and
              all(r[0]==0 for m in (ai,bi) for r in m), 'first pair changed')
        d,di,t,ti=[multiply(rr,m) for m in (a,ai,b,bi)]
        for i in range(94):
            for j in range(94):
                check(inner(d[i],t[j])-inner(di[i],ti[j])==2*inner(rr[i],rr[j]) and
                      inner(d[i],ti[j])+inner(di[i],t[j])==0, name+' all-pairs identity')
        costs=[]
        for k in range(8):
            s=[root for i,root in enumerate(live) if d[i][k] or di[i][k]]
            u=[root for i,root in enumerate(live) if t[i][k] or ti[i][k]]
            mask=sum(1<<j for j in u)
            charge=binary_rank_low(n[i]&mask for i in s)
            costs.append(charge)
            check(s==report['terms'][k]['D_support'] and u==report['terms'][k]['T_support'],
                  name+' actual support')
            check(charge==report['terms'][k]['copy_cost'], name+' term cost')
        check(costs==expected and sum(costs)==report['total_copy_cost'],name+' complete charge')
        print('AUDIT',name,'costs='+str(costs),'8836 ordered entries PASS')
    print('PASS_SEPARATE_FRACTION_AUDIT: 511 kernels, 1716 subsets, 256 optimal classes; minimum premises verified')


if __name__=='__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError, TypeError, KeyError) as exc:
        print('FAIL_SEPARATE_AUDIT: '+str(exc),file=sys.stderr)
        sys.exit(1)
