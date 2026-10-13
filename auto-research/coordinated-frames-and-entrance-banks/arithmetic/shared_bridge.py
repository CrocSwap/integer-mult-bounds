"""Exact shared-core bridge validator for a paid balanced-layout adapter.

The numerical bridge follows icekylinx/eumemic PR152 at 627089e85badda0b450048c29307786716d51037.
This does not replay or establish a scalar word, weighted selector theorem,
moment enclosure, or analytic/fixed-tape interface. Those are distinct inputs.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
from fractions import Fraction as Q
from math import prod

def require(test,reason):
    if not test:raise ValueError(reason)
def rational(value):
    require(type(value) in (int,str,Q),'Exact rational required')
    return Q(value)
def integer(value):
    q=rational(value);require(q.denominator==1,'Integer required');return q.numerator
def halving(m,r):
    require(0<r<m,'Strictly contracting positive child')
    k=1
    while m**k<=2*r**k:k+=1
    return k
def nofloat(value):
    require(not isinstance(value,float),'Binary float not permitted')
    if isinstance(value,dict):
        for x in value.values():nofloat(x)
    if isinstance(value,(list,tuple)):
        for x in value:nofloat(x)

def validate_shared_bridge(bridge,row):
    """Recompute numeric PR152 bridge, without inventing a finite bit profile.

    `row` is the explicit complex local inventory. Its scalar/frame proof and
    the supplier moment proofs remain separate source-bound obligations.
    The supplied bit_uniform fields describe an already completed ordinary
    interchange with borrowed-and-restored q-adic rows, not old PR141's
    finite coarse-profile contract. The inherited conservative external
    reserves 9909 and 252 are retained as separate stated proof inputs.
    """
    nofloat(bridge);nofloat(row)
    h,v,R,c,M=(integer(row[k]) for k in ('h','v','R','c','total_M_operations'))
    scalar_R=integer(row['scalar_role_reserve'])
    reuse=integer(row['reuse_pairs']);terminal=integer(row.get('terminal_sinks',0))
    require(scalar_R==integer(row['c'])+integer(row['q'])-integer(row['matched']),
            'Scalar role reserve must retain the complete pre-reuse inventory')
    require(reuse>=0 and terminal>=0 and scalar_R-R==reuse+terminal,'Physical role count must match reuse and terminal removals')
    require(h>=2 and h%2==0 and min(v,R,c,M)>0,'Positive even-dimensional complex family')
    m=3*h
    hist={integer(k):integer(n) for k,n in row['child_histogram'].items() if integer(n)}
    require(all(0<t<m and n>0 for t,n in hist.items()),'Proper positive child histogram')
    r=max(hist);localW=2*v+R;localS=sum(t*n for t,n in hist.items())
    require((m,localW,localS)==tuple(integer(row[k]) for k in ('m','W_per_vertex','rank_per_vertex')),'Complex inventory totals')
    require(m*localW-localS==integer(row['deficit_per_vertex'])==2*v-3*integer(row['loss']),'Shared-core deficit identity')
    half=m//2
    vertices=2**(m-1+(half-1)**2)*prod(2**(2*i)-1 for i in range(1,half))
    W,s,N=vertices*localW,vertices*localS,vertices*v
    original_X=32*v
    local=4*(c+v)+10*v+4*h*v+4*h*h+8*h+8+2*h+8*scalar_R*v*(M+16)+original_X
    logical=3*vertices*local+8*W+4*N+8*m*scalar_R*vertices
    G=64*(m+1)**3*(logical+1)*(W+1)**2
    E=64*(W+m+G+1)**3
    literal=2*G*W**2+8*s+4*W+4+32*m
    B=s+E;C0=32*m*B**2;depth=halving(m,r)
    expected_complex=dict(m=m,W=W,s=s,N=N,maxchild=r,invocations_per_stage=vertices,stages=3,
      auxiliary_banks_after_sharing=1,halving_degree=depth,wire_bits=W.bit_length(),
      original_X_involution_scalar_group_upper=original_X,local_group_upper=local,
      logical_group_upper=logical,finite_group_router_upper=G,scalar_group_upper=G,
      coefficient_bound=h+4,coefficient_denominator_divides=6,
      physical_roles_per_vertex=R,scalar_role_reserve=scalar_R,reuse_pairs=reuse,terminal_sinks=terminal)
    expected_semantic=dict(E=E,literal_charge=literal,strict_literal_gap=E-literal,B=B,C0=C0,C1=1,
      induction_gap=2*B*(m-r)-s-E,fixed_odd_divisor=3)
    for name,expected in [('complex',expected_complex),('semantic',expected_semantic)]:
        for k,value in expected.items():require(rational(bridge[name][k])==value,'Stale '+name+'/'+k)
    require(E>literal and 2*B*(m-r)>=s+E and C0>2*B+18,'Completed exact-child semantic induction')
    # These are conservative, retained external reserves. The varying q-adic
    # group cardinality is deliberately not interpreted as an external stock.
    old_coarse=integer(bridge['conservative_old_coarse_row_reserve'])
    old_leaf=integer(bridge['ordinary_leaf_row_degree'])
    require(old_coarse==9909 and old_leaf==252,'Retained separate external row reserves')
    coeff=depth*W.bit_length()+old_coarse+old_leaf
    degree=integer(bridge['rows']['degree']);gap=Q(degree)-Q(51,25)*coeff
    require(degree>0 and gap>0,'Insufficient external row reserve')
    expected_rows=dict(coefficient=coeff,complex_coefficient=depth*W.bit_length(),
      degree=degree,suffix_slope=4*degree,degree_gap=gap)
    for k,value in expected_rows.items():require(rational(bridge['rows'][k])==value,'Stale row/'+k)
    u=bridge['bit_uniform']
    coarse,atom,old,actual=(rational(u[k]) for k in ('coarse_saving','atom_beta','old_atom_saving','ordinary_saving'))
    require(0<coarse<1 and 0<atom<1 and old==Q(384599,10**10),'Uniform stopped supplier constants')
    require(actual==(1-atom)*coarse+atom*old,'Uniform stopped saving identity')
    require(actual<atom<1-actual,'Paid atom-adapter and internal-row tolls')
    return dict(complex=expected_complex,semantic=expected_semantic,rows=expected_rows,
      bit_uniform=dict(coarse_saving=coarse,atom_beta=atom,old_atom_saving=old,ordinary_saving=actual),
      conservative_old_coarse_row_reserve=old_coarse,ordinary_leaf_row_degree=old_leaf)
