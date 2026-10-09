"""Necessary limits for the rank-one, three-stage two-field compiler.

These limits do not cover arbitrary finite networks or higher-rank labels.
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations
from math import comb

from audit_joint_frames import matrix, rank
from certify import require
from experiments.rank_product_core import binary_factor
from search_network import log_integer_bounds


def binary_type_bound(rows, fitting):
    n=len(rows);U,V=binary_factor(rows,n);r=len(V)
    require(all(row>>i&1 for i,row in enumerate(rows)), 'Diagonal must be one')
    require(all(type(x) is int or isinstance(x,(Q,str)) for row in fitting for x in row),
            'Use exact rational fitting entries')
    F=matrix(fitting)
    require(len(F)==n and all(len(row)==n for row in F) and all(F[i][i] for i in range(n)),
            'Need a square fitting matrix with nonzero diagonal')
    require(all(not ((rows[i]>>j)&1) or (not F[i][j] and not F[j][i])
                for i in range(n) for j in range(n) if i!=j), 'Incompatible fitting pair')
    groups={}
    for i,u in enumerate(U):
        require(u!=0,'A diagonal-one matrix cannot have a zero factor row')
        groups.setdefault(u,[]).append(i)
    d=rank(F)
    for indices in groups.values():
        require(all(F[i][j]==0 for i in indices for j in indices if i!=j),
                'A repeated binary type did not give a rational identity minor')
        require(len(indices)<=d,'Identity minor exceeds rational rank')
    require(n<=len(groups)*d<=(2**r-1)*d,'Binary type bound failed')
    return dict(n=n,r=r,d=d,binary_types=len(groups),largest_type=max(map(len,groups.values())),
                universal_upper_on_n=(2**r-1)*d)


def dimension_limit(target_kappa=Q(1,2**25), auxiliary_floor=True):
    """Uses kappa<a_b/5 from the retained Gaussian assembly."""
    require(isinstance(target_kappa,Q) and target_kappa>0,'Exact positive target required')
    factor=4 if auxiliary_floor else 2
    target=5*target_kappa
    for d in range(2,10000):
        lo,hi=log_integer_bounds(d**3)
        upper=1/((factor*d**3-1)*lo)
        if upper<target:
            if d>2:
                plo,phi=log_integer_bounds((d-1)**3)
                require(1/((factor*(d-1)**3-1)*phi)>target,'Threshold straddles log enclosure')
            return dict(target_kappa=target_kappa,required_bit_saving=target,
                        W_over_N_lower=factor,first_excluded_dimension=d,
                        largest_not_excluded_dimension=d-1,upper_at_excluded=upper,
                        all_larger_dimensions_excluded=True,achievability_claimed=False)
    raise ValueError('Dimension search budget exceeded')


def multiplicities(h,k):
    require(0<=k<=h//2,'Use complement symmetry to take k<=h/2')
    return [comb(h,i)-(comb(h,i-1) if i else 0) for i in range(k+1)]


def radial_scope():
    bound=dimension_limit();require(bound['first_excluded_dimension']==53,'Target changed')
    small=[]
    for h in range(4,12):
        for k in range(2,h//2+1):
            dims=multiplicities(h,k);least=min(dims[2:]);n=comb(h,k)
            require(n<=30*least,'Small nonlinear case not excluded')
            small.append(dict(h=h,k=k,n=n,least_nonlinear_multiplicity=least,
                              n_at_most_30d=True))
    # The proof handles the infinite tail. These are its exact base values.
    require(comb(12,2)-12==54>52,'Second multiplicity base failed')
    catalan6=comb(12,6)//7
    require(catalan6==132>52,'Central multiplicity base failed')
    return dict(dimension_limit=bound,small_cases=small,
                minimum_positive_binary_rank=5,
                nonlinear_tail=dict(h_at_least=12,second_multiplicity_base=54,
                    middle_multiplicity_base=132,all_nonlinear_multiplicities_exceed_52=True),
                conclusion='A target-capable full-subset rational radial fitting matrix must be linear in intersection size. Binary matrices need not be radial.',
                scope='Rank-one three-stage compiler, transparent central/side factorization, first/third sharing, and retained Gaussian assembly only.')


def incidence_rigidity(q,expand=False):
    require(type(q) is int and q>=2 and q&(q-1)==0,'Use a power of two')
    k,j,h=2*q-1,q-1,3*q-2
    types=[]
    for t in range(k+1):
        value=comb(t,j)%2 if t>=j else 0
        require(value==int(t in (j,k)),'Parity support identity failed')
        types.append(value)
    require(2*k-h==q>j,'Local off-diagonal intersections must exceed j')
    require(comb(h,k)==comb(h,j),'Local incidence matrix is not square')
    out=dict(q=q,k=k,j=j,local_ground_size=h,local_matrix_dimension=comb(h,j),
             parity_values=types,local_incidence_times_transpose_is_identity=True,
             rigid_for_all_h_at_least=h,expanded=False,
             scope='Every row lies in the j-subset incidence span; no claim about other row spaces.')
    if expand:
        require(comb(h,j)<=200,'Local expansion budget exceeded')
        features=list(combinations(range(h),j))
        rows=[sum(1<<i for i,J in enumerate(features) if set(J)<=set(S))
              for S in combinations(range(h),k)]
        require(all((a&b).bit_count()%2==int(i==l)
                    for i,a in enumerate(rows) for l,b in enumerate(rows)),
                'Local incidence matrix is not orthogonal over F2')
        out.update(expanded=True,packed_rows=rows)
    return out
