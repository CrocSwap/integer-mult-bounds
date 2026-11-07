#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Export exact rank, factorization and complete left/right kernel witnesses.

Classical Gaussian elimination and rank factorization. Prepared for
Ali Romman with substantial OpenAI Codex assistance.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import lcm
from pathlib import Path
import re
import sys
from compare_recursive_invoices import _pairs, _integer, _not_integer, require


MAX_PRODUCT_SCALE_BITS = 16384


def rational(x):
    require(type(x) is int or type(x) is str and len(x) <= 4096
            and re.fullmatch(r'-?[0-9]+(?:/[1-9][0-9]*)?',x,re.ASCII), 'Use exact rational entries')
    return Q(x)


def encode_rational(q):
    require(max(abs(q.numerator).bit_length(), q.denominator.bit_length()) <= 6000,
            'Exact certificate exceeds the 6000-bit rational budget')
    return str(q)


def read(path, limit):
    with Path(path).open('rb') as f: raw=f.read(limit+1)
    require(len(raw)<=limit,'JSON byte limit exceeded')
    return json.loads(raw,object_pairs_hook=_pairs,parse_int=_integer,
                      parse_float=_not_integer,parse_constant=_not_integer),sha256(raw).hexdigest()


def matrix(raw,m,n):
    require(type(raw) is list and len(raw)==m
            and all(type(row) is list and len(row)==n for row in raw),'Wrong matrix shape')
    return [[rational(x) for x in row] for row in raw]


def validate(value):
    require(type(value) is dict and value.keys()=={'schema','matrix'}
            and value['schema']=='rational-rank-problem/v1','Invalid rank problem')
    raw=value['matrix']
    require(type(raw) is list and 1<=len(raw)<=64 and type(raw[0]) is list
            and 1<=len(raw[0])<=64,'Use 1..64 rows and columns')
    a=matrix(raw,len(raw),len(raw[0]))
    require(all(abs(x.numerator)<=10**9 and x.denominator<=10**9 for row in a for x in row),
            'Input numerator and denominator limit is 10^9')
    return a


def inverse(a):
    n=len(a);rows=[row[:]+[Q(i==j) for j in range(n)] for i,row in enumerate(a)]
    for k in range(n):
        pivot=next(i for i in range(k,n) if rows[i][k])
        rows[k],rows[pivot]=rows[pivot],rows[k];d=rows[k][k];rows[k]=[x/d for x in rows[k]]
        for i in range(n):
            if i!=k and rows[i][k]:
                c=rows[i][k];rows[i]=[x-c*y for x,y in zip(rows[i],rows[k])]
    return [row[n:] for row in rows]


def certify(value):
    a=validate(value);m,n=len(a),len(a[0]);work=[row[:] for row in a]
    row_ids=list(range(m));chosen_rows=[];cols=[]
    for j in range(n):
        r=len(cols);pivot=next((i for i in range(r,m) if work[i][j]),None)
        if pivot is None:continue
        work[r],work[pivot]=work[pivot],work[r];row_ids[r],row_ids[pivot]=row_ids[pivot],row_ids[r]
        chosen_rows.append(row_ids[r]);cols.append(j)
        for i in range(r+1,m):
            if work[i][j]:
                c=work[i][j]/work[r][j]
                for k in range(j,n):work[i][k]-=c*work[r][k]
    r=len(cols);inv=inverse([[a[i][j] for j in cols] for i in chosen_rows])
    coeff=[[sum((inv[k][l]*a[chosen_rows[l]][j] for l in range(r)),Q(0)) for j in range(n)] for k in range(r)]
    right=[]
    for free in (j for j in range(n) if j not in cols):
        v=[Q(j==free) for j in range(n)]
        for k,j in enumerate(cols):v[j]=-coeff[k][free]
        right.append(v)
    left=[]
    for free in (i for i in range(m) if i not in chosen_rows):
        v=[Q(i==free) for i in range(m)]
        for l,i in enumerate(chosen_rows):v[i]=-sum((a[free][cols[k]]*inv[k][l] for k in range(r)),Q(0))
        left.append(v)
    encode=lambda rows:[[encode_rational(x) for x in row] for row in rows]
    result={'schema':'rational-rank-certificate/v1','rank':r,'rows':chosen_rows,'columns':cols,
            'minor_inverse':encode(inv),'coefficients':encode(coeff),
            'right_kernel':encode(right),'left_kernel':encode(left)}
    verify(value,result);return result


def _scaled_rows(rows):
    """Clear row denominators, or decline excessive common-denominator growth."""
    result=[]
    for row in rows:
        denominator=1
        for x in row:
            denominator=lcm(denominator,x.denominator)
            if denominator.bit_length()>MAX_PRODUCT_SCALE_BITS:return None
        result.append(([x.numerator*(denominator//x.denominator) for x in row],denominator))
    return result


def _product_equal(a,b,c,m,k,n):
    """Test A B = C using exact integer dot products after row/column scaling.

    Shapes have already been checked at the certificate boundary. Explicit
    dimensions preserve empty factors and zero-dimensional kernels.
    """
    left=_scaled_rows(a)
    right=_scaled_rows([[b[i][j] for i in range(k)] for j in range(n)])
    if left is None or right is None:
        return all(sum((a[i][t]*b[t][j] for t in range(k)),Q(0))==c[i][j]
                   for i in range(m) for j in range(n))
    for i in range(m):
        row,rd=left[i]
        for j in range(n):
            column,cd=right[j];target=c[i][j]
            numerator=sum(x*y for x,y in zip(row,column))
            if numerator*target.denominator != target.numerator*rd*cd:return False
    return True


def verify(value,result):
    """Check the factorization, minor inverse and complete kernel bases by products."""
    a=validate(value);m,n=len(a),len(a[0])
    require(type(result) is dict and result.get('schema')=='rational-rank-certificate/v1','Invalid certificate')
    r=result.get('rank');require(type(r) is int and 0<=r<=min(m,n),'Invalid rank')
    rows,cols=result.get('rows'),result.get('columns')
    for indices,bound in ((rows,m),(cols,n)):
        require(type(indices) is list and len(indices)==r and len(set(indices))==r
                and all(type(i) is int and 0<=i<bound for i in indices),'Invalid pivot indices')
    inv=matrix(result.get('minor_inverse'),r,r);c=matrix(result.get('coefficients'),r,n)
    minor=[[a[i][j] for j in cols] for i in rows]
    require(_product_equal(minor,inv,[[Q(i==j) for j in range(r)] for i in range(r)],r,r,r),
            'Pivot minor inverse is false')
    require(_product_equal([[a[i][j] for j in cols] for i in range(m)],c,a,m,r,n),
            'Rank factorization is false')
    right=matrix(result.get('right_kernel'),n-r,n);left=matrix(result.get('left_kernel'),m-r,m)
    free_columns=[j for j in range(n) if j not in cols];free_rows=[i for i in range(m) if i not in rows]
    for index,v in enumerate(right):
        require(all(v[j]==Q(k==index) for k,j in enumerate(free_columns)), 'Right basis lacks free-coordinate identity')
    for index,v in enumerate(left):
        require(all(v[i]==Q(k==index) for k,i in enumerate(free_rows)), 'Left basis lacks free-coordinate identity')
    require(_product_equal(a,[[v[j] for v in right] for j in range(n)],
                          [[Q(0)]*(n-r) for _ in range(m)],m,n,n-r),'False right kernel')
    require(_product_equal(left,a,[[Q(0)]*n for _ in range(m-r)],m-r,m,n),'False left kernel')
    return True


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('problem');parser.add_argument('--check')
    args=parser.parse_args(argv)
    try:
        value,digest=read(args.problem,1024**2)
        if args.check:
            result,_=read(args.check,32*1024**2)
            require(type(result) is dict and result.get('input_sha256')==digest,'Problem bytes changed')
            verify(value,result);print('PASS_RATIONAL_RANK_CERTIFICATE')
        else:
            result=certify(value);result['input_sha256']=digest;print(json.dumps(result,indent=2,sort_keys=True))
    except (OSError,ValueError,TypeError,KeyError,RecursionError,ZeroDivisionError) as exc:
        print(str(exc),file=sys.stderr);return 2
    return 0


if __name__=='__main__':raise SystemExit(main())
