"""Orthogonality cores on binary cubes and bounded quadratic-code screens.

All ranks are over the stated field. Large factor sizes are constructive
upper bounds; no unexpanded numerical elimination is claimed.
"""
from fractions import Fraction as Q
from itertools import combinations
from math import comb
from hashlib import sha256

from certify import require
from experiments.rank_product_core import counts
from search_network import log_integer_bounds


def cube_spec(q):
    require(type(q) is int and q>=2 and q&(q-1)==0,'Use a power of two q>=2')
    k=2*q-1;d=k+1;n=1<<k;a=q//2
    R=2*sum(comb(k,i) for i in range(a))
    coefficients=[((comb(k-l,q-l) if l<=q else 0)+(1 if l==0 else 0))%2
                  for l in range(k+1)]
    require(coefficients==[int(l==q) for l in range(k+1)],'Square-zero basis identity failed')
    return dict(q=q,k=k,d=d,n=n,central_factor_size=R,split_degree=a,
                monomial_multiplication_coefficients=coefficients,
                degree=comb(k,q),factor_is_constructive_upper_bound=True,
                positive_numerator=n>6*R*d)


def cube_ledger(q,side_roles=None):
    spec=cube_spec(q);n=spec['n'];d=spec['d'];R=spec['central_factor_size']
    side=n*spec['degree'] if side_roles is None else side_roles
    out=counts(n,R,d,side)
    if out['positive']:
        lo,hi=log_integer_bounds(out['m']);eta=out['relative_deficit']
        out.update(saving_lower=eta/hi,saving_upper=eta/((1-eta)*lo))
    out.update(q=q,full_network_expanded=False)
    return out


def binary_product(A,B):
    rows=[]
    for row in A:
        out=0
        while row:
            bit=row&-row;row^=bit;out^=B[bit.bit_length()-1]
        rows.append(out)
    return rows


def expand_factor(q,maximum_n=128):
    spec=cube_spec(q);n=spec['n'];k=spec['k'];a=spec['split_degree']
    require(n<=maximum_n,'Explicit cube factor exceeds budget')
    L=[S for S in range(n) if S.bit_count()<a]
    H=[T for T in range(n) if T.bit_count()>=q+a]
    require(len(L)+len(H)==spec['central_factor_size'],'Wrong factor dimension')
    hindex={T:i for i,T in enumerate(H)}
    Z=[sum(1<<S for S in range(n) if S&T==T) for T in range(n)]
    Me=[sum(1<<S for S in range(n) if S&T==S and (T^S).bit_count()==q) for T in range(n)]
    lowmask=sum(1<<S for S in L)
    U=[sum(((row>>S)&1)<<i for i,S in enumerate(L))|
       ((1<<(len(L)+hindex[T])) if T in hindex else 0) for T,row in enumerate(Me)]
    V=[1<<S for S in L]+[Me[T]&~lowmask for T in H]
    require(binary_product(U,V)==Me,'Low-column/high-row factor failed')
    Ug=binary_product(Z,U);Vg=binary_product(V,Z)
    C=[sum(1<<S for S in range(n) if S==T or (S^T).bit_count()==q) for T in range(n)]
    require(binary_product(Z,Z)==[1<<i for i in range(n)],'Basis transform is not involutory')
    require(binary_product(Ug,Vg)==C,'Conjugated factor does not implement orthogonality core')
    return dict(specification=spec,U=Ug,V=Vg,C=C)


def quadratic_code_base(t):
    """Cayley row for constant-free Boolean polynomials of degree <=2."""
    require(type(t) is int and 2<=t<=6,'Quadratic-code discovery budget: t=2,...,6')
    d=1<<t
    basis=[sum(1<<x for x in range(d) if all(x>>i&1 for i in S))
           for degree in (1,2) for S in combinations(range(t),degree)]
    k=len(basis);n=1<<k;data=bytearray((n+7)//8);data[0]=1
    word=old=0
    for i in range(1,n):
        gray=i^(i>>1);bit=gray^old;old=gray
        word^=basis[bit.bit_length()-1]
        if word.bit_count()==d//2:data[gray//8]|=1<<(gray%8)
    return dict(t=t,d=d,k=k,n=n,basis=basis,base=int.from_bytes(data,'little'),
                base_sha256=sha256(data).hexdigest())


def xor_permute(bits,index,n):
    """Permute coefficient positions j -> j xor index in a packed row."""
    require(type(n) is int and n>0 and n&(n-1)==0 and
            type(index) is int and 0<=index<n and type(bits) is int and 0<=bits<1<<n,
            "Invalid packed row or XOR permutation")
    allbits=(1<<n)-1;b=0
    while index:
        if index&1:
            stride=1<<b
            mask=allbits//((1<<(2*stride))-1)*((1<<stride)-1)
            bits=((bits&mask)<<stride)|((bits>>stride)&mask)
        index>>=1;b+=1
    return bits


def quadratic_rank_screen(t,maximum_rows=4096):
    require(type(maximum_rows) is int and maximum_rows>0,'Positive row budget required')
    data=quadratic_code_base(t);n=data['n'];d=data['d']
    # Reaching this rank already prevents n>6rd for this particular C.
    stop=(n+6*d-1)//(6*d)
    pivots={};witnesses=[];stream=sha256()
    for i in range(min(n,maximum_rows)):
        row=xor_permute(data['base'],i,n)
        original=row
        while row:
            p=row.bit_length()-1
            if p not in pivots:
                pivots[p]=row;witnesses.append(i)
                stream.update(original.to_bytes((n+7)//8,'little'))
                break
            row^=pivots[p]
        if len(pivots)>=stop:break
    return dict(t=t,n=n,rational_dimension=d,
                binary_rank_lower_bound=len(pivots),independent_row_indices=witnesses,
                independent_row_sha256=stream.hexdigest(),base_sha256=data['base_sha256'],
                rows_checked=i+1,maximum_rows=maximum_rows,
                specified_core_positive_deficit_excluded=6*len(pivots)*d>=n,
                scope='Only C=I plus every orthogonality edge on the specified quadratic code. No exclusion of other supported binary matrices or subcodes.')


def cube_target_budget(q,target):
    require(isinstance(target,Q) and target>0,'Use an exact target')
    spec=cube_spec(q);n=spec['n'];d=spec['d'];r=spec['central_factor_size'];m=d**3
    f=1-Q(6*r*d,n)
    require(f>0,'No positive numerator')
    lo,hi=log_integer_bounds(m)
    suff=Q(n,3)*(f/(m*target*hi)-2)-r
    t=target*lo
    necessary=Q(n,3)*(f*(1+t)/(m*t)-2)-r
    return dict(target_bit_saving=target,sufficient_side_ratio=suff/n,
                necessary_side_ratio=necessary/n,
                requires_loss_preserving_side_certificate=True)
