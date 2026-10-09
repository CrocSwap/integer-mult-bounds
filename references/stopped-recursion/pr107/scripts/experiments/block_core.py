"""Uniform higher-rank idempotent labels for the three-stage bit compiler.

This is a finite-interface extension, not a supplied better block geometry.
The scalar circuit is unchanged; the source and central-return ranks change.
"""
from fractions import Fraction as Q
from itertools import combinations

from audit_joint_frames import matrix,rank,product,row_basis,eye,zero
from certify import require
from experiments.rank_product_core import binary_factor,_compile,counts
from experiments.shared_core import compile_shared
from search_network import log_integer_bounds


def check_block_projectors(rows,projections):
    n=len(rows);require(n>=2 and len(projections)==n,'One projector per scalar label required')
    U,V=binary_factor(rows,n)
    require(all(row>>i&1 for i,row in enumerate(rows)),'Central diagonal must be one')
    d=len(projections[0]);require(d>=2,'Ambient dimension too small')
    Ps=[]
    for P in projections:
        require(len(P)==d and all(len(row)==d for row in P),'Wrong projector dimensions')
        require(all(type(x) is int or isinstance(x,(Q,str)) for row in P for x in row),
                'Use exact rational projectors')
        P=matrix(P);require(product(P,P)==P,'Label is not idempotent');Ps.append(P)
    ranks=[rank(P) for P in Ps];ell=ranks[0]
    require(ell>=1 and ranks==[ell]*n,'All labels must have the same positive rank')
    side=[(i,j) for i,row in enumerate(rows) for j in range(n) if i!=j and row>>j&1]
    Z=zero(d)
    require(all(product(Ps[i],Ps[j])==Z and product(Ps[j],Ps[i])==Z for i,j in side),
            'Every side edge needs mutual annihilation')
    return dict(n=n,r=len(V),d=d,ell=ell,U=U,V=V,side_edges=side,projections=Ps)


def check_block_pair(rows,fitting,ell):
    """Rational block fitting matrix with identity ell-by-ell diagonal blocks."""
    require(type(ell) is int and ell>=1,'Positive integer block size required')
    n=len(rows);size=n*ell
    require(len(fitting)==size and all(len(row)==size for row in fitting),'Wrong block fitting shape')
    require(all(type(x) is int or isinstance(x,(Q,str)) for row in fitting for x in row),
            'Use exact rational fitting entries')
    F=matrix(fitting)
    require(all(F[i*ell+a][i*ell+b]==int(a==b)
                for i in range(n) for a in range(ell) for b in range(ell)),
            'Normalize every diagonal block to the identity')
    A=row_basis(F);d=len(A);B=[]
    for row in F:
        residual=list(row);coeff=[]
        for basis in A:
            pivot=next(i for i,x in enumerate(basis) if x);value=residual[pivot]
            coeff.append(value);residual=[x-value*y for x,y in zip(residual,basis)]
        require(not any(residual),'Block fitting factorization failed');B.append(coeff)
    require(product(B,A)==F,'Wrong rational block factorization')
    Ps=[]
    for i in range(n):
        Ai=matrix([row[i*ell:(i+1)*ell] for row in A]);Bi=matrix(B[i*ell:(i+1)*ell])
        require(product(Bi,Ai)==eye(ell),'Diagonal block factor failed')
        Ps.append(product(Ai,Bi))
    core=check_block_projectors(rows,Ps)
    require(core['ell']==ell and core['d']==d,'Block rank normalization changed')
    core['fitting_matrix']=F
    return core


def block_counts(n,r,d,ell,side_roles,shared=False):
    require(all(type(x) is int for x in (n,r,d,ell,side_roles)) and 1<=ell<=d,
            'Use integer dimensions and a positive label rank')
    out=counts(n,r,d,side_roles)
    if shared:out['W']-=n*n*(side_roles+r)
    L=3*n*n*r*d*ell*ell;gain=n**3*ell**3;delta=gain-2*L
    out.update(ell=ell,L=L,source_rank_gain=gain,deficit=delta,s=out['W']*d**3-delta,
               positive=delta>0,density=Q(n*ell,r*d),relative_deficit=Q(delta,out['W']*d**3),
               shared=shared,normalized_ambient_dimension=Q(d,ell))
    if delta>0:
        lo,hi=log_integer_bounds(d**3);eta=out['relative_deficit']
        require(eta<1,'Invalid rank sum')
        out.update(saving_lower=eta/hi,saving_upper=eta/((1-eta)*lo))
    return out


def compile_block(core,permutation=None,maximum_roles=1000):
    """Use the retained scalar/frame formula, replacing only its rank ledger."""
    if permutation is None:candidate,_=_compile(core,maximum_roles)
    else:candidate,_=compile_shared(core,permutation,maximum_roles)
    expected=block_counts(core['n'],core['r'],core['d'],core['ell'],len(core['side_edges']),
                          shared=permutation is not None)
    require(candidate['W']==expected['W'] and candidate['m']==expected['m'],'Wrong compiled dimensions')
    return candidate,expected


def block_side_budget(n,r,d,ell,target):
    require(isinstance(target,Q) and target>0,'Exact positive bit-saving target required')
    require(n*ell>6*r*d,'No positive block numerator')
    gain=Q(ell**3)*(1-Q(6*r*d,n*ell));lo,hi=log_integer_bounds(d**3)
    suff=Q(n,2)*(gain/(d**3*target*hi)-2)-r
    t=target*lo;necessary=Q(n,2)*(gain*(1+t)/(d**3*t)-2)-r
    return dict(target=target,sufficient_side_roles=suff,necessary_side_roles=necessary,
                sufficient_ratio=suff/n,necessary_ratio=necessary/n,
                geometry_and_compressed_side_frames_supplied=False)
