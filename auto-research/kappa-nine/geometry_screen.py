"""Rescore specified alternate geometries; no new transfer theorem asserted.

The two-stage count model is an explicit optimistic hypothesis for new cores.
An exclusion is scoped to that ledger and the stated explicit factor, not
to every implementation of the geometry or every supported binary matrix.
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations, product
from math import comb
from pathlib import Path
import argparse
import hashlib
import json
from target_budget import HERE, encode, moment, require


def subset_axis(h,q):
    k,j=2*q-1,q-1
    require(q>=2 and q&(q-1)==0 and h>k and j*h!=k*k,'subset domain')
    # Label indicators lie in H=I-(j/k^2)J and have norm q.
    # A fixed j-subset center spans U_J: all J-coordinates equal c,
    # sum(x)=k*c. In coordinates outside J, its restricted form is sum x_i^2.
    # Thus dim U_J=h-j and U_J is nondegenerate. This replaces the
    # overly pessimistic h-1 bound used in an initial exploratory calculation.
    return dict(h=h,q=q,k=k,j=j,n=comb(h,k),r=comb(h,j),center_dimension=h-j)


def optimistic_pair(a,b):
    da,db=a['h'],b['h'];m=da*db
    rows=Counter({(da-1)*(db-1):Q(2),1:Q(1)})
    rows[da-1]+=2;rows[db-1]+=2
    for axis in (a,b):
        d,n,r,u=(axis[k] for k in ('h','n','r','center_dimension'))
        rows[d]+=Q(r*u,n*d)
    bound=moment(rows,m,2)
    # Arbitrary auxiliary role additions have coefficient >1 relative to
    # their W contribution, even if their rank is batched into d and m-d.
    coefficients={d:moment(Counter({d:1,m-d:1}),m,1) for d in (da,db)}
    return dict(axes=[a,b],dimension=m,free_role_constant=bound,
                auxiliary_role_coefficients=coefficients,
                target_excluded=bound[0]>1 and all(x[0]>1 for x in coefficients.values()),
                scope='Hypothetical modern two-stage copied-center ledger, specified incidence factors, ideal full-rank macro batching. Does not assert that these transferred circuits or profiles exist.')


def subset_scan(maximum_h=64):
    candidates=[];best_by_dimension={}
    for q in (2,4,8,16,32):
        for h in range(2*q,maximum_h+1):
            if (q-1)*h==(2*q-1)**2:continue
            a=subset_axis(h,q);candidates.append(a)
            if h not in best_by_dimension or Q(a['r']*a['center_dimension'],a['n'])<Q(best_by_dimension[h]['r']*best_by_dimension[h]['center_dimension'],best_by_dimension[h]['n']):
                best_by_dimension[h]=a
    # The free-role score is monotone in r*u/n, so this exact domination
    # reduction covers every pair of listed q families at each dimension.
    axes=list(best_by_dimension.values());results=[]
    for i,a in enumerate(axes):
        for b in axes[i:]:results.append(optimistic_pair(a,b))
    require(all(x['target_excluded'] for x in results),'A geometry survived; investigate it')
    best=min(results,key=lambda r:r['free_role_constant'][0])
    return dict(maximum_h=maximum_h,axis_candidates=len(candidates),
                unordered_pairs_covered=len(candidates)*(len(candidates)+1)//2,
                dimension_pairs_checked=len(results),best_relaxation=best,
                selected_axes=axes,all_target_excluded=True,
                selection_proof='At fixed dimension the constant depends positively and linearly on r*center_dimension/n. Select its exact minimum; role coefficients depend only on dimensions.',
                ordered_interval_digest=hashlib.sha256(json.dumps(encode(results),sort_keys=True).encode()).hexdigest(),
                cases=results)


def signed_rank(h,q):
    require(h>=q and q>=2 and q&(q-1)==0,'signed domain')
    labels=[]
    for support in combinations(range(h),q):
        mask=sum(1<<i for i in support)
        for signs in product((0,1),repeat=q-1):
            negative=sum(1<<i for i,z in zip(support[1:],signs) if z)
            labels.append((mask^negative,negative))
    n=len(labels);basis={};witness=[];digest=hashlib.sha256();columns=[0]*n
    for i,(pos,neg) in enumerate(labels):
        row=0
        for j,(p,nm) in enumerate(labels):
            dot=(pos&p).bit_count()+(neg&nm).bit_count()-(pos&nm).bit_count()-(neg&p).bit_count()
            selected=dot%q==0
            require(selected==(i==j or dot==0),'orthogonality/diagonal contract')
            if selected:row|=1<<j;columns[j]|=1<<i
        digest.update(row.to_bytes((n+7)//8,'little'))
        x=row
        while x:
            pivot=x.bit_length()-1
            if pivot not in basis:basis[pivot]=x;witness.append(i);break
            x^=basis[pivot]
    # Every generated row was reduced; rank is exact, not a sampled lower bound.
    transpose_digest=hashlib.sha256(b''.join(c.to_bytes((n+7)//8,'little') for c in columns)).hexdigest()
    require(transpose_digest==digest.hexdigest(),'central symmetry')
    return dict(h=h,q=q,n=n,exact_binary_rank=len(basis),
                independent_row_indices=witness,central_matrix_sha256=digest.hexdigest(),
                density=Q(n,h*len(basis)),
                required_average_center_dimension_strict_upper_for_positive_two_stage_deficit=Q(n,2*len(basis)),
                scope='Exact central core only. No auxiliary/frame circuit or copied-center span claim.')


def audit(maximum_h=64):
    subset=subset_scan(maximum_h)
    signed=[signed_rank(h,4) for h in range(4,11)]
    signed.extend(signed_rank(h,8) for h in (8,9,10))
    return dict(status='FINITE GEOMETRY FEASIBILITY SCREENS; NO NEW NETWORK',
                subset_family=subset,signed_core_ranks=signed,
                exclusions_are_scoped=True,
                complex_status='Subset cores have historical dyadic polynomial companions, but no new full phase circuit is supplied. Signed even-weight vectors are isotropic after direct mod-2 reduction, so they cannot be imported as nondegenerate rank-one phase labels unchanged.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);parser.add_argument('--maximum-h',type=int,default=64);args=parser.parse_args()
    result=audit(args.maximum_h)
    if args.output:args.output.write_text(json.dumps(encode(result),indent=2,sort_keys=True)+'\n')
    best=result['subset_family']['best_relaxation']
    print('PASS finite subset relaxation screen; best axes',[(a['q'],a['h']) for a in best['axes']], 'lower moment',float(best['free_role_constant'][0]))
    print('PASS ten complete signed-core binary-rank checks; no phase or full network claim')
