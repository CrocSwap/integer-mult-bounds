#!/usr/bin/env python3
"""Exact dyadic even-subset kernels and their actual encoder-support bills.

No side circuit, bit supplier or multiplication exponent is claimed.
"""
from fractions import Fraction as Q
from itertools import combinations
from math import comb
from pathlib import Path
import json
import argparse
from functools import lru_cache


def need(ok,message):
    if not ok:raise ValueError(message)


@lru_cache(None)
def value(k,t):
    ans=Q(1)
    for j in range(k//2):ans*=Q(t-2*j,k-2*j)
    return ans


def specification(n,k):
    need(n%2 and k%2==0 and 2<=k<n,'valid odd ground size and even subset size')
    d=k//2
    coefficients=[sum((-1)**(j-i)*comb(j,i)*value(k,i) for i in range(j+1)) for j in range(d+1)]
    need(coefficients[0]==0,'zero constant coefficient')
    need(all(c.denominator&(c.denominator-1)==0 for c in coefficients),'all coefficients dyadic')
    for t in range(k+1):
        need(value(k,t)==sum(c*comb(t,j) for j,c in enumerate(coefficients) if j<=t),'binomial basis identity')
        if t==k:need(value(k,t)==1,'unit diagonal')
        elif t%2==0:need(value(k,t)==0,'forbidden intersection zero')
    widths={n-j:comb(n,j) for j,c in enumerate(coefficients) if c}
    return {'ground_points':n,'subset_size':k,'ports':comb(n,k),'binary_width':n,
       'coefficients_in_binomial_basis':[str(c) for c in coefficients],
       'kernel_by_intersection':[str(value(k,t)) for t in range(k+1)],
       'encoder_count':sum(widths.values()),'copy_width_histogram':widths,
       'encoder_support_rank_sum':sum(w*count for w,count in widths.items()),
       'side_johnson_distances':[k-t for t in range(k) if value(k,t)],
       'claim':'exact algebraic geometry and copy support bill; no side program or kappa'}


def binary_rank(rows):
    piv={}
    for row in rows:
        while row:
            j=row.bit_length()
            if j not in piv:piv[j]=row;break
            row^=piv[j]
    return len(piv)


def verify_small(n,k):
    sets=[sum(1<<i for i in S) for S in combinations(range(n),k)]
    full=(1<<n)-1;labels=[full^s for s in sets]
    checks=0
    for i,s in enumerate(sets):
        need(labels[i].bit_count()%2==1,'norm-one labels')
        for j,t in enumerate(sets):
            overlap=(s&t).bit_count()
            need((labels[i]&labels[j]).bit_count()%2==(1+overlap)%2,'full binary pairing identity')
            if i!=j and value(k,overlap):need((labels[i]&labels[j]).bit_count()%2==0,'support only on allowed distinct pairs')
            checks+=1
    ranks=[]
    for j in range(1,k//2+1):
        fixed=(1<<j)-1
        rows=[label for s,label in zip(sets,labels) if s&fixed==fixed]
        r=binary_rank(rows);need(r==n-j,'representative support rank');ranks.append(r)
    support_checks=0
    for j in range(1,k//2+1):
        for J in combinations(range(n),j):
            fixed=sum(1<<i for i in J)
            rows=[label for s,label in zip(sets,labels) if s&fixed==fixed]
            need(binary_rank(rows)==n-j,'every actual feature-support span')
            need(all(label&fixed==0 for label in rows),'support lies in named coordinate frame')
            support_checks+=1
    return {'actual_supports_checked':support_checks,'n':n,'k':k,'ports':len(sets),'all_pair_checks':checks,'representative_support_ranks':ranks}


def compute():
    out={'status':'PASS_EVEN_SUBSET_KERNEL_IDENTITIES',
       'small_complete_controls':[verify_small(9,4),verify_small(11,6),verify_small(11,8)],
       'cases':[specification(n,k) for k in (4,6,8) for n in (17,25,33,41,49)],
       'dyadic_degree_controls':[specification(2*k+1,k)['coefficients_in_binomial_basis'] for k in range(2,25,2)],
       'negative_controls':3,
       'scope':'dyadic decoder and binary support geometry only; side/compiler/bit/outer work unresolved'}
    need(value(6,6)/2!=1,'wrong normalization rejected')
    broken_labels=[sum(1<<i for i in S) for S in combinations(range(11),6)]
    need(not all(x.bit_count()%2==1 for x in broken_labels),
         'omitting complement violates norm-one label')
    # Deleting the degree-three term breaks the full diagonal identity.
    c=[Q(x) for x in specification(25,6)['coefficients_in_binomial_basis']]
    need(sum(c[j]*comb(6,j) for j in range(3))!=1,'omitted top feature rejected')
    return out


def main():
    p=argparse.ArgumentParser();p.add_argument('--record',type=Path);args=p.parse_args()
    out=compute()
    if args.record:args.record.write_text(json.dumps(out,indent=2)+'\n')
    else:need(json.loads(json.dumps(out))==json.loads(Path(__file__).with_name('RESULT.json').read_text()),'canonical result mismatch')
    print('PASS_EVEN_SUBSET_DYADIC_KERNELS all_pairs='+str(sum(x['all_pair_checks'] for x in out['small_complete_controls']))+' actual_supports='+str(sum(x['actual_supports_checked'] for x in out['small_complete_controls']))+' controls=3 no_new_kappa')


if __name__=='__main__':main()
