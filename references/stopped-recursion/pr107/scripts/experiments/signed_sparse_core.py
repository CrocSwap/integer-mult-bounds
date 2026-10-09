"""Constructive binary factors for rational signed-sparse orthogonality cores.

Large ranks are factor-size upper bounds. Hypothetical side budgets are not
side constructions, and no multiplication witness is asserted here.
"""
from fractions import Fraction as Q
from itertools import combinations, product
from math import comb

from certify import require
from experiments.cube_core_family import binary_product
from experiments.rank_product_core import binary_factor,check_core
from experiments.shared_core import shared_counts, target_budget,compile_shared


def choose(n, k):
    return comb(n, k) if 0 <= k <= n else 0


def specification(h, q):
    require(type(h) is int and type(q) is int and h >= q >= 2
            and q & (q-1) == 0, 'Need h>=q and power-of-two q>=2')
    n = 2**(q-1)*comb(h, q)
    M = sum(comb(h, b)*sum(choose(h-b, a) for a in range(q-3*b))
            for b in range((q-1)//3+1))
    twice_degree = sum(choose(q,j)*choose(h-q,q-j)*choose(j,j//2)*2**(q-j)
                       for j in range(0,q+1,2))
    require(twice_degree % 2 == 0 and twice_degree > 0,
            'Orthogonality degree must be positive and even before quotient')
    # The stacked inclusion matrix on the (q-b)-slice has Q-rank at most
    # choose(h-b,min(L,q-b,h-q)); reduction modulo 2 cannot increase rank.
    refined_M=sum(comb(h,b)*comb(h-b,min(q-1-3*b,q-b,h-q))
                  for b in range((q-1)//3+1))
    r = 2*refined_M
    return dict(h=h,q=q,n=n,d=h,central_factor_size=r,
                low_weight_feature_count=M,low_weight_span_bound=refined_M,
                coarse_factor_size=2*M,orthogonality_degree=twice_degree//2,
                positive_numerator=n>6*r*h,
                factor_is_upper_bound_not_exact_rank=True,
                orthogonal_matching='Positive regular bipartite graph; Hall matching')


def vectors(h,q):
    specification(h,q)
    for support in combinations(range(h),q):
        for signs in product((-1,1),repeat=q-1):
            v=[0]*h;v[support[0]]=1
            for i,s in zip(support[1:],signs):v[i]=s
            yield tuple(v)


def feature_catalog(h,q):
    """(P,N): product of support indicators P and negative indicators N."""
    return [(sum(1<<i for i in P),sum(1<<i for i in N))
            for b in range((q-1)//3+1) for N in combinations(range(h),b)
            for a in range(q-3*b)
            for P in combinations([i for i in range(h) if i not in N],a)]


def coefficient_terms(h,q):
    """Exact expansion of [z^(q-1)] (1+z)^(-1) prod_i (1+z)^(x_i y_i).

    Coordinate choices: 0, pp, np, pn. A term with r pp and s cross
    choices has coefficient binom(q-1-r-s,s) mod 2 if r+2s<=q-1.
    """
    require(h<=8,'Explicit coefficient expansion budget exceeded')
    for choices in product(range(4),repeat=h):
        r=choices.count(1);s=choices.count(2)+choices.count(3)
        if r+2*s>q-1 or not (comb(q-1-r-s,s)&1):continue
        xp=xn=yp=yn=0
        for i,c in enumerate(choices):
            if c==1:xp|=1<<i;yp|=1<<i
            elif c==2:xn|=1<<i;yp|=1<<i
            elif c==3:xp|=1<<i;yn|=1<<i
        require(xp.bit_count()+3*xn.bit_count()+yp.bit_count()+3*yn.bit_count()
                <=2*(q-1),'Feature weight bound failed')
        yield (xp,xn),(yp,yn)


def expand_factor(h,q,maximum_n=160):
    spec=specification(h,q);n=spec['n']
    require(n<=maximum_n,'Explicit signed-vector factor exceeds budget')
    labels=list(vectors(h,q));features=feature_catalog(h,q);M=len(features)
    require(M==spec['low_weight_feature_count'],'Feature count mismatch')
    index={f:i for i,f in enumerate(features)}
    encoded=[(sum(1<<i for i,x in enumerate(v) if x),
              sum(1<<i for i,x in enumerate(v) if x<0)) for v in labels]
    def evaluations(f):
        p,neg=f
        return sum(1<<i for i,(s,t) in enumerate(encoded) if p&s==p and neg&t==neg)
    ev={f:evaluations(f) for f in features}
    left=[ev[f] for f in features]+[0]*M
    right=[0]*M+[ev[f] for f in features]
    for x,y in coefficient_terms(h,q):
        if x in index:right[index[x]]^=evaluations(y)
        else:
            require(y in index,'Neither feature is below the split weight')
            left[M+index[y]]^=evaluations(x)
    U=[sum(((column>>i)&1)<<j for j,column in enumerate(left)) for i in range(n)]
    C=[]
    for i,x in enumerate(labels):
        row=0
        for j,y in enumerate(labels):
            dot=sum(a*b for a,b in zip(x,y))
            require((dot%q==0)==(i==j or dot==0),'Modular/orthogonal support mismatch')
            if dot%q==0:row|=1<<j
        C.append(row)
    require(binary_product(U,right)==C,'Signed-sparse factor identity failed')
    require(all(row.bit_count()==1+spec['orthogonality_degree'] for row in C),
            'Exact degree formula failed')
    reduced_U,reduced_V=binary_factor(C,n)
    require(len(reduced_V)<=spec['central_factor_size'],'Refined rank bound failed')
    return dict(specification=spec,labels=labels,U=U,V=right,C=C,
                reduced_U=reduced_U,reduced_V=reduced_V)


def ledger(h,q,side_roles=None):
    spec=specification(h,q);n=spec['n'];r=spec['central_factor_size']
    side=n*spec['orthogonality_degree'] if side_roles is None else side_roles
    require(type(side) is int and side>=0,'Nonnegative integral side count required')
    out=shared_counts(n,r,h,side)
    out.update(full_network_expanded=False,
               side_status='raw orthogonality-edge compiler' if side_roles is None
               else 'hypothetical loss-preserving side construction required')
    return out


def budget(h,q,target=Q(16,10**8)):
    spec=specification(h,q)
    return target_budget(spec['n'],spec['central_factor_size'],h,target)


def redundant_factor_control():
    """Check that charging a nonminimal factor is safe in the full compiler."""
    from audit_joint_frames import eye
    from finite_bit_contract import inspect_candidate
    data=expand_factor(2,2);r=data['specification']['central_factor_size']
    core=check_core(data['C'],data['labels'],eye(2))
    core['V'] += [0]*(r-core['r']);core['r']=r
    candidate,expected=compile_shared(core,[1,0])
    actual=inspect_candidate(candidate,require_deficit=False)
    require(actual['s']==expected['s'] and actual['deficit']==expected['deficit'],
            'Nonminimal-factor compiler ledger failed')
    return dict(central_factor_size=r,complete_contract=actual,expected=expected,
                purpose='Redundant-factor/all-role control, not a positive construction')
