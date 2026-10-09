"""Exact necessary bounds for the common-subset prime-power construction.

Scope: incidence central factor, rational indicator lines, the three-stage
shared compiler, distinct partial-output sum DAG, and kappa<a_b/5 assembly.
"""
from fractions import Fraction as Q
from itertools import combinations
from math import comb
from certify import require
from experiments.core_limits import dimension_limit
from search_network import log_integer_bounds


def characteristic(q):
    require(type(q) is int and q>=2,'Integer q>=2 required')
    for p in range(2,q+1):
        if q%p:continue
        x=q
        while x%p==0:x//=p
        return p if x==1 else None


def local_identity(q,expand=False):
    p=characteristic(q);require(p is not None,'q must be a prime power')
    k,j=2*q-1,q-1;h=3*q-2
    residues=[comb(t,j)%p if t>=j else 0 for t in range(k+1)]
    require(residues==[int(t in (j,k)) for t in range(k+1)],'Lucas support identity failed')
    out=dict(q=q,p=p,k=k,j=j,local_h=h,local_dimension=comb(h,j),
             intersection_residues=residues,central_rank_is_binomial_h_j_for_h_at_least=h)
    if expand:
        require(comb(h,j)<=100,'Expansion budget exceeded')
        points=range(h);cols=[set(t) for t in combinations(points,j)]
        B=[[int(T<=set(S)) for T in cols] for S in combinations(points,k)]
        require(all(sum(a*b for a,b in zip(u,v))%p==int(i==l)
                    for i,u in enumerate(B) for l,v in enumerate(B)),
                'Local incidence Gram is not identity')
        out['expanded_local_gram_checked']=True
    return out


def partial_output_control(q,h):
    require(characteristic(q) is not None and h>=3*q,'Need nontrivial distinct partial sums')
    k,j=2*q-1,q-1
    require(comb(h,k)<=200,'Support expansion budget exceeded')
    labels=[sum(1<<i for i in S) for S in combinations(range(h),k)]
    roots=set();minimum=comb(h-k,q)
    for T in labels:
        for J in combinations([i for i in range(h) if T>>i&1],j):
            fixed=sum(1<<i for i in J)
            support=tuple(S for S in labels if S&T==fixed)
            require(len(support)==minimum>1,'Wrong partial row size')
            intersection=(1<<h)-1;union=0
            for S in support:intersection&=S;union|=S
            require(intersection==fixed and ((1<<h)-1)^union==T^fixed,
                    'Partial output does not reconstruct its source pair and target')
            require(support not in roots,'Two partial outputs are equal');roots.add(support)
    require(len(roots)==comb(k,j)*len(labels),'Wrong number of partial outputs')
    return dict(q=q,h=h,partial_outputs=len(roots),minimum_terms=minimum,
                exact_distinct_nonsingleton_supports_checked=True)


def envelope(q,h):
    require(characteristic(q) is not None and h>=2*q-1,'Invalid subset family')
    k,j=2*q-1,q-1;n,r=comb(h,k),comb(h,j);delta=n-6*r*h
    if delta<=0:return dict(q=q,h=h,positive_deficit=False)
    require(h>=3*q,'Positive deficit without nontrivial partial sums')
    M=comb(k,j);side_floor=2*M*n
    eta=Q(delta,2*h**3*(n+side_floor+r))
    lo,hi=log_integer_bounds(h**3)
    # -log(1-eta) <= eta/(1-eta), with a strict inequality for eta>0.
    upper=eta/((1-eta)*lo)
    return dict(q=q,h=h,positive_deficit=True,n=n,r=r,outputs_per_label=M,
                side_role_floor=side_floor,eta_upper=eta,bit_saving_upper=upper,
                kappa_upper=upper/5)


def screen(target=Q(1,2**26)):
    tail=dimension_limit(target);cut=tail['first_excluded_dimension'];cases=[]
    for q in range(2,(cut+1)//2+1):
        if characteristic(q) is None:continue
        local_identity(q)
        for h in range(2*q-1,cut):cases.append(envelope(q,h))
    survivors=[x for x in cases if x['positive_deficit']]
    best=max(survivors,key=lambda x:x['kappa_upper'])
    require(best['kappa_upper']<target,'Family screen has a target survivor')
    return dict(target=target,tail_dimension_exclusion=tail,cases=cases,
                best_finite_upper=best,all_prime_powers_and_ground_sizes_excluded=True,
                scope='Unchanged incidence center, indicator-line frames, common-subset partial-output DAG with c+q roles, shared three-stage compiler, retained kappa<a_b/5 assembly. Not a limit on arbitrary finite networks.')
