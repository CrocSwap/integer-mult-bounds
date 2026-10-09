#!/usr/bin/env python3
"""Independent exact forward/opposite polynomial Fourier layout controls.

Sparse Gaussian-dyadic polynomials are evaluated through actual butterfly
and monomial operations. No producer layout implementation is imported.
"""

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import resource
import time


def shape(ell, K, lengths):
    assert ell >= 2 and 1 <= K < ell
    n=ell-1;q=n//K;L,t=divmod(n,q)
    widths=[L+1]*t+[L]*(q-t)
    assert sum(widths)==n and K<=min(widths)<=max(widths)<2*K
    physical=[(i,ell-1) for i,a in enumerate(lengths) if a==ell]
    low=n
    for width in widths:
        for i in range(len(lengths)):
            physical.extend((i,h) for h in range(low-1,low-width-1,-1))
        low-=width
    assert low==0 and len(physical)==sum(lengths)
    assert len(set(physical))==len(physical)
    masks={slot:1<<(len(physical)-1-j) for j,slot in enumerate(physical)}
    rounds=[]
    if ell in lengths:rounds.append((ell-1,[i for i,a in enumerate(lengths) if a==ell]))
    rounds += [(h,list(range(len(lengths)))) for h in range(ell-2,-1,-1)]
    return widths,masks,rounds


def coordinates(index,lengths):
    result=[]
    for a in reversed(lengths):result.append(index%2**a);index//=2**a
    assert index==0
    return result[::-1]


def encoded(values,lengths,masks,frequency=False):
    return sum(mask*((values[i]>>(lengths[i]-1-h if frequency else h))&1)
               for (i,h),mask in masks.items())


def polynomial_add(a,b,sign=1):
    result=dict(a)
    for k,v in b.items():
        result[k]=result.get(k,Q(0))+sign*v
        if result[k]==0:del result[k]
    return {k:v/2 for k,v in result.items()}


def monomial(p,E,r):
    result={}
    for k,v in p.items():
        e=(k+E)%(2*r);s=-1 if e>=r else 1
        result[e%r]=s*v
    return result


def layer(values,h,axes,masks):
    for i in axes:
        mask=masks[i,h]
        for j in range(len(values)):
            if j&mask:continue
            a,b=values[j],values[j|mask]
            values[j],values[j|mask]=polynomial_add(a,b),polynomial_add(a,b,-1)


def twiddle(values,h,axes,masks,r,inverse=False):
    for j,p in enumerate(values):
        if not p:continue
        E=0
        for i in axes:
            branch=bool(j&masks[i,h])
            lower=sum((1<<v)*bool(j&masks[i,v]) for v in range(h))
            E-=(2*r//(1<<(h+1)))*branch*lower
        values[j]=monomial(p,-E if inverse else E,r)


def control(ell,K,lengths,all_basis):
    widths,masks,rounds=shape(ell,K,lengths)
    M=2**sum(lengths);r=2**ell
    bases=list(range(M)) if all_basis else sorted({0,1,M//3,M//2,M-1})
    checks=0
    for basis in bases:
        input_coordinates=coordinates(basis,lengths)
        target=encoded(input_coordinates,lengths,masks)
        values=[{} for _ in range(M)];values[target]={0:Q(1)}
        for h,axes in rounds:
            layer(values,h,axes,masks);twiddle(values,h,axes,masks,r)
        for frequency in range(M):
            js=coordinates(frequency,lengths)
            exponent=-sum((2*r//(1<<a))*j*k for a,j,k in zip(lengths,js,input_coordinates))%(2*r)
            expected={exponent%r:Q(-1 if exponent>=r else 1,M)}
            address=encoded(js,lengths,masks,True)
            assert values[address]==expected
            checks+=1
        for h,axes in reversed(rounds):
            twiddle(values,h,axes,masks,r,True);layer(values,h,axes,masks)
        assert values[target]=={0:Q(1,M)}
        assert all(not p for j,p in enumerate(values) if j!=target)
    return dict(ell=ell,K=K,axis_bit_widths=lengths,balanced_widths=widths,
                input_basis_columns=len(bases),all_basis_columns=all_basis,
                exact_forward_polynomial_matrix_entries=checks,
                normalized_opposite_composite_exact=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists()
    started=time.monotonic();start_utc=datetime.now(timezone.utc).isoformat();rows=[]
    for ell in (2,3):
        for K in range(1,ell):
            for D in (1,2):
                for flags in product((0,1),repeat=D):
                    rows.append(control(ell,K,[ell-1+flag for flag in flags],True))
    for ell,Ks in ((4,(1,2,3)),(6,(2,3))):
        for K in Ks:
            for flags in product((0,1),repeat=2):
                rows.append(control(ell,K,[ell-1+flag for flag in flags],False))
    result=dict(status='PASS exact independent balanced forward/opposite polynomial operators',
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),started_utc=start_utc,
        completed_utc=datetime.now(timezone.utc).isoformat(),cases=rows,
        shape_count=len(rows),input_basis_columns=sum(row['input_basis_columns'] for row in rows),
        exact_forward_matrix_entries=sum(row['exact_forward_polynomial_matrix_entries'] for row in rows),
        wall_seconds=time.monotonic()-started,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        scope='Actual exact normalized butterflies/negacyclic monomials against independent closed Fourier formula and normalized opposite composite; full tiny bases, sparse boundary columns at unequal balanced widths. Asymptotic tape/layout/precision transfer remains written proof.')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS',result['shape_count'],'shapes;',result['input_basis_columns'],'basis columns;',result['exact_forward_matrix_entries'],'exact polynomial entries')


if __name__=='__main__':main()
