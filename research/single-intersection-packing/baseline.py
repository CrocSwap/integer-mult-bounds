"""Single-intersection two-field cores and exact binary minor witnesses."""
from fractions import Fraction as Q
from math import comb
from itertools import combinations

from certify import require
from search_network import log_integer_bounds


def core_parameters(h,k,j):
    require(all(type(x) is int for x in (h,k,j)) and 2<=k<h and 0<=j<k,
            'Invalid single-intersection parameters')
    n=comb(h,k);d=h-int(h*j==k*k)
    coefficients=[((comb(l,j) if l>=j else 0)+int(l==k))%2 for l in range(k+1)]
    for t in range(k+1):
        require(sum(a*comb(t,l) for l,a in enumerate(coefficients) if l<=t)%2 == int(t==j or t==k),
                'Binomial coefficient expansion failed')
    levels=[l for l,a in enumerate(coefficients) if a]
    retained=[l for l in levels if not any(t>l and comb(k-l,t-l)%2 for t in levels)]
    cover={l:next(t for t in retained if t>=l and comb(k-l,t-l)%2) for l in levels}
    upper=sum(comb(h,l) for l in retained)
    degree=comb(k,j)*comb(h-k,k-j) if h-k>=k-j else 0
    return dict(h=h,k=k,j=j,n=n,d=d,binomial_coefficients=coefficients,
                retained_levels=retained,level_cover=cover,
                binary_factor_upper=upper,degree=degree,
                positive_with_supplied_factor=n>6*upper*d,
                positivity_exclusion_rank=(n+6*d-1)//(6*d))


def rank_of_rows(rows):
    basis={}
    for row in rows:
        require(type(row) is int and row>=0,'Invalid packed binary row')
        while row:
            pivot=row.bit_length()-1
            if pivot not in basis:
                basis[pivot]=row;break
            row^=basis[pivot]
    return len(basis)


def minor_rows(labels,j):
    require(len(labels)==len(set(labels)) and all(type(x) is int and x>0 for x in labels),
            'Distinct positive packed labels required')
    return [sum(1<<b for b,T in enumerate(labels) if S==T or (S&T).bit_count()==j) for S in labels]


def check_minor(h,k,j,labels,independent_indices):
    parameters=core_parameters(h,k,j)
    require(all(x<1<<h and x.bit_count()==k for x in labels),'Wrong subset labels')
    require(len(independent_indices)==len(set(independent_indices)) and
            all(type(i) is int and 0<=i<len(labels) for i in independent_indices),
            'Invalid independent-row indices')
    require(len(labels)==len(set(labels)),'Repeated minor labels')
    rows=[sum(1<<b for b,T in enumerate(labels)
              if labels[i]==T or (labels[i]&T).bit_count()==j) for i in independent_indices]
    r=rank_of_rows(rows)
    require(r==len(independent_indices),'Supplied minor rows are dependent')
    return dict(binary_rank_lower=r,positive_deficit_excluded=6*r*parameters['d']>=parameters['n'])


def free_side_bounds(h,k,j,r):
    p=core_parameters(h,k,j);n=p['n'];d=p['d'];m=d**3
    require(type(r) is int and 1<=r<=n,'Use a nonzero rank bound at most n')
    f=1-Q(6*r*d,n)
    if f<=0:return None
    eta=f/(m*(2+Q(3*r,n)))
    lo,hi=log_integer_bounds(m)
    return dict(relative_deficit=eta,lower=eta/hi,upper=eta/((1-eta)*lo))


def spectral_parity_bound(h,k,j):
    """Integer Johnson spectrum gives a binary rank lower bound.

    The common rational eigenspaces need not remain eigenspaces over F2.
    Only the integer characteristic polynomial is reduced modulo two.
    """
    p=core_parameters(h,k,j)
    require(2*k<=h,'Spectral formula here uses k<=h/2')
    b=[(((-1)**(l-j)*comb(l,j)) if l>=j else 0)+int(l==k) for l in range(k+1)]
    eigenvalues=[sum(b[l]*comb(k-i,l-i)*comb(h-l-i,k-l) for l in range(i,k+1))
                 for i in range(k+1)]
    multiplicities=[comb(h,i)-(comb(h,i-1) if i else 0) for i in range(k+1)]
    require(sum(multiplicities)==p['n'],'Wrong total spectral multiplicity')
    require(sum(m*e for m,e in zip(multiplicities,eigenvalues))==p['n'],'Wrong spectral trace')
    require(sum(m*e*e for m,e in zip(multiplicities,eigenvalues))==p['n']*(1+p['degree']),
            'Wrong spectral squared trace')
    lower=sum(m for m,e in zip(multiplicities,eigenvalues) if e%2)
    return dict(eigenvalues=eigenvalues,multiplicities=multiplicities,
                binary_rank_lower=lower,positive_deficit_excluded=6*lower*p['d']>=p['n'])


def intersecting_minor_bound(h,k,j):
    """Identity minor on all labels containing one fixed (j+1)-subset."""
    p=core_parameters(h,k,j)
    candidates={'fixed_common_subset':comb(h-j-1,k-j-1)}
    block=2*k-j-1
    if j>0 and block<=h:
        candidates['disjoint_blocks']=h//block*comb(block,k)
    if j==k-1:
        # Adjacent labels differ in one ground point, so their point sums
        # differ nontrivially modulo h. A largest color class is independent.
        candidates['sum_mod_h_color_class']=(p['n']+h-1)//h
    lower=max(candidates.values())
    return dict(binary_rank_lower=lower,positive_deficit_excluded=6*lower*p['d']>=p['n'],
                fixed_common_subset_size=j+1,identity_minor_lower_bounds=candidates)


def verify_feature_orbit(h,k,j,labels,feature_budget=40000):
    """Certify the feature row span by adjacent-transposition closure.

    Every supplied label is an actual k-subset. Independent feature rows
    whose span is invariant under all adjacent ground permutations span
    the entire transitive orbit. The full C rank then equals their Gram rank.
    """
    p=core_parameters(h,k,j)
    require(labels and len(labels)==len(set(labels)),'Distinct nonempty orbit basis required')
    require(all(type(S) is int and 0<=S<1<<h and S.bit_count()==k for S in labels),
            'Invalid orbit labels')
    levels=[l for l,a in enumerate(p['binomial_coefficients']) if a]
    require(sum(comb(h,l) for l in levels)<=feature_budget,'Feature expansion exceeds budget')
    feature_indices={}
    for l in levels:
        for S in combinations(range(h),l):
            feature_indices[sum(1<<a for a in S)]=len(feature_indices)
    def feature(S):
        points=[i for i in range(h) if S>>i&1]
        return sum(1<<feature_indices[sum(1<<a for a in T)]
                   for l in levels for T in combinations(points,l))
    basis={}
    def reduce(row):
        while row:
            pivot=row.bit_length()-1
            if pivot not in basis:return row
            row^=basis[pivot]
        return 0
    for S in labels:
        row=reduce(feature(S))
        require(row!=0,'Feature basis is dependent')
        basis[row.bit_length()-1]=row
    checked=0
    for S in labels:
        for i in range(h-1):
            if ((S>>i)^(S>>(i+1)))&1:
                image=S^(3<<i)
                require(reduce(feature(image))==0,'Feature span is not permutation invariant')
                checked+=1
    rows=minor_rows(labels,j)
    r=rank_of_rows(rows)
    return dict(h=h,k=k,j=j,feature_count=len(feature_indices),feature_span_dimension=len(labels),
                adjacent_image_checks=checked,exact_full_binary_rank=r,
                full_scalar_matrix_expanded=False,complete_feature_orbit_proof=True,
                positive_deficit=p['n']>6*r*p['d'])
