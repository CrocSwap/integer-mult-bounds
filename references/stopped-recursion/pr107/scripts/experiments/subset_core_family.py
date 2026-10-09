"""Two-field subset cores: exact construction ledger, not a stronger kappa.

For q a power of two, labels are (2q-1)-subsets. Binary central factors
are incidences with (q-1)-subsets; the rational fitting matrix is
|S intersection T|-(q-1). Inner factor size need not be the minimal rank.
"""
from fractions import Fraction as Q
from functools import cache
from itertools import combinations
from math import comb

from certify import require
from experiments.rank_product_core import counts, check_core
from incidence_rectangles import Plan, stars
from search_network import log_integer_bounds


def specification(h, q):
    require(type(h) is int and type(q) is int and q >= 2 and q & (q-1) == 0,
            'q must be a power of two at least two')
    k, j = 2*q-1, q-1
    require(h > k and j*h != k*k, 'Need h>k and a nondegenerate rational form')
    n, r = comb(h, k), comb(h, j)
    degree = comb(k, j)*comb(h-k, q) if h-k >= q else 0
    types = []
    for t in range(k+1):
        central = comb(t,j) % 2 if t >= j else 0
        require(central == int(t in (j,k)), 'Binary coefficient support failed')
        require(t == k or not central or t-j == 0, 'Two-field compatibility failed')
        types.append(dict(intersection=t, binary_coefficient=central,
                          rational_inner_product=t-j, diagonal=t == k))
    return dict(h=h, q=q, k=k, j=j, n=n, central_factor_size=r,
                rational_dimension=h, degree=degree, pair_types=types,
                form='I - (j/k^2) J', norm=q,
                form_determinant=1-Q(j*h,k*k))


def ledger(h,q,side_roles=None):
    spec=specification(h,q)
    n,r=spec['n'],spec['central_factor_size']
    R=n*spec['degree'] if side_roles is None else side_roles
    out=counts(n,r,h,R)
    out.update(h=h,q=q,k=spec['k'],j=spec['j'],
               central_factor_size=r, minimal_binary_rank_claimed=False)
    eta=out['relative_deficit']
    if eta>0:
        lo,hi=log_integer_bounds(out['m'])
        out['saving_lower']=eta/hi
        out['saving_upper']=eta/((1-eta)*lo)
    return out


def side_budget(h,q,target):
    """Conservative sufficient and necessary side-role bounds for a>target.

    These assume the side implementation preserves all frame losses. They
    do not certify any proposed compression or stage reuse.
    """
    require(isinstance(target,Q) and target>0,'Use an exact positive target')
    spec=specification(h,q);n=spec['n'];r=spec['central_factor_size'];m=h**3
    f=1-Q(6*r*h,n)
    require(f>0,'No positive numerator')
    lo,hi=log_integer_bounds(m)
    suff=Q(n,3)*(f/(m*target*hi)-2)-r
    t=target*lo
    necessary=Q(n,3)*(f*(1+t)/(m*t)-2)-r
    return dict(target_bit_saving=target,
                sufficient_strict_upper_on_side_roles=suff,
                necessary_strict_upper_on_side_roles=necessary,
                sufficient_ratio=suff/n, necessary_ratio=necessary/n,
                requires_loss_preserving_side_certificate=True)


def small_core(h,q,maximum_labels=100):
    """Expand C, rational labels, and an explicit (possibly redundant) UV.

    The returned object is compatible with the retained compiler's internal
    input format. Large positive cores use the compact construction proof.
    """
    spec=specification(h,q);n=spec['n'];k=spec['k'];j=spec['j']
    require(n <= maximum_labels,'Core expansion exceeds label budget')
    labels=list(combinations(range(h),k));centers=list(combinations(range(h),j))
    masks=[sum(1<<i for i in S) for S in labels]
    cmasks=[sum(1<<i for i in S) for S in centers]
    U=[sum(1<<a for a,B in enumerate(cmasks) if B&M == B) for M in masks]
    V=[sum(1<<i for i,M in enumerate(masks) if B&M == B) for B in cmasks]
    rows=[]
    for coeff in U:
        row=0
        for a,v in enumerate(V):
            if coeff>>a&1:row^=v
        rows.append(row)
    expected=[sum(1<<b for b,T in enumerate(masks)
                  if (S&T).bit_count() in (j,k)) for S in masks]
    require(rows==expected,'Incidence factors do not give claimed support')
    H=[[Q(int(i==a))-Q(j,k*k) for a in range(h)] for i in range(h)]
    vectors=[[int(M>>i&1) for i in range(h)] for M in masks]
    core=check_core(rows,vectors,H)
    core.update(r=len(centers),U=U,V=V)
    return core


@cache
def disjoint_plan(n,a,b):
    """Bounded baseline DP; exactly the listed splits and row/column stars.

    Unlike the older weighted two-subset optimizer, each product chooses
    the best stored unweighted child independently. No optimality asserted.
    """
    require(n>=0 and 0<=a<=8 and 0<=b<=8,'Invalid disjoint-subset sizes')
    if a+b>n:return Plan(n,a,b,0,0,0,'empty')
    if not a or not b:return Plan(n,a,b,1,comb(n,a),comb(n,b),'base')
    winner=min((stars(n,a,b,'rows'),stars(n,a,b,'cols')),key=lambda p:p.score())
    for left in range(1,n):
        terms=tuple((disjoint_plan(left,x,y),disjoint_plan(n-left,a-x,b-y))
                    for x in range(a+1) for y in range(b+1)
                    if x+y<=left and a+b-x-y<=n-left)
        candidate=Plan(n,a,b,sum(A.count*B.count for A,B in terms),
                       sum(A.left*B.left for A,B in terms),
                       sum(A.right*B.right for A,B in terms),'split',left,terms)
        if candidate.score()<winner.score():winner=candidate
    return winner


def rectangle_ledger(h,q):
    """Candidate role count from independent fixed-intersection rectangles.

    Accounting assumes monotone side compilation; the complete frame proof
    is an explicit obligation, not supplied by this count function.
    """
    spec=specification(h,q);require(q<=8,'DP screen limited to q<=8')
    plan=disjoint_plan(h-spec['j'],q,q)
    R=comb(h,spec['j'])*plan.score()
    out=ledger(h,q,R)
    out.update(side_model='independent fixed-intersection disjointness rectangles',
               rectangle_count_per_intersection=plan.count,
               left_memberships=plan.left,right_memberships=plan.right,
               complete_side_frame_certificate=False)
    return out


def rational_companion(q):
    """Candidate opposite-field central polynomial, normalized at k=2q-1.

    Its off-diagonal nonzero entries occur only at even intersections,
    orthogonal for odd-weight binary incidence labels. This verifies the
    core identity, not a complex phase-kernel transfer.
    """
    require(type(q) is int and q>=2 and q & (q-1)==0,'Invalid power of two')
    k=2*q-1;j=q-1
    roots=list(range(1,k,2))
    def value(t):
        out=Q(1)
        for root in roots:out*=Q(t-root,k-root)
        return out
    values=[value(t) for t in range(k+1)]
    differences=values[:];coeff=[]
    for order in range(j+1):
        coeff.append(differences[0])
        differences=[b-a for a,b in zip(differences,differences[1:])]
    for t,val in enumerate(values):
        require(val==sum(a*comb(t,l) for l,a in enumerate(coeff) if l<=t),
                'Binomial-basis expansion failed')
        require(t==k or t%2==0 or val==0,'Binary orthogonality support failed')
    require(values[k]==1,'Rational companion diagonal failed')
    return dict(q=q,k=k,j=j,odd_roots=roots,values=values,
                binomial_coefficients=coeff,
                central_factor_size_formula='C(h,j)',
                complete_complex_frame_certificate=False)


def complex_count_screen(h,q,side_roles=None):
    """Hypothetical generalization of complex ledger, with honest guard size.

    Scalar polynomial and binary labels are compatible; a complete phase
    residual and signed-schedule proof is still required for this new family.
    """
    spec=specification(h,q);k=spec['k'];n=spec['n'];r=spec['central_factor_size']
    require(h>2*k,'Use a spare coordinate outside every pair of labels')
    poly=rational_companion(q)
    degree=sum(comb(k,t)*comb(h-k,k-t) for t in range(k)
               if h-k>=k-t and poly['values'][t])
    R=n*degree if side_roles is None else side_roles
    out=counts(n,r,h,R)
    out['deficit']=2*n**3-6*n*n*r*h
    out['s']=out['W']*out['m']-out['deficit']
    out['relative_deficit']=Q(out['deficit'],out['W']*out['m'])
    out['positive']=out['deficit']>0
    power=1
    while out['s']>=out['m']**power:power+=1
    out.update(h=h,q=q,strict_residual_power=power,
               original_fifth_power_guard_applies=out['s']<out['m']**5,
               complete_complex_frame_certificate=False,
               ledger_status='HYPOTHETICAL COMPLEX LEDGER; PROOF OBLIGATIONS REMAIN')
    if out['positive']:
        lo,hi=log_integer_bounds(out['m']);eta=out['relative_deficit']
        out.update(saving_lower=eta/hi,saving_upper=eta/((1-eta)*lo))
    return out
