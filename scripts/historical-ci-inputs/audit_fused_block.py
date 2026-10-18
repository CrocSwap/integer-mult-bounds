#!/usr/bin/env python3
"""Exact parity-butterfly block and a scoped coordinate-recursion obstruction.

The direct block uses three exact coordinate Hadamard layers plus diagonal
phases. It is not a faster multiplication algorithm. Its recursive call
count fails the all-role contraction requirement.
"""
from fractions import Fraction as Q
from pathlib import Path
import json

from certify import network, require, verify_sources
from prepare_layers import serializable

ROOT=Path(__file__).resolve().parents[1]


def gadd(a,b):return (a[0]+b[0],a[1]+b[1])
def gsub(a,b):return (a[0]-b[0],a[1]-b[1])
def gmul(a,b):return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])


def phase_i(value,power):
    return gmul(value,((1,0),(0,1),(-1,0),(0,-1))[power%4])


def layout(f,K,rho=0,spectator_bits=0):
    require(f>=1 and K>=1 and 0<=rho<K and spectator_bits>=0,'Invalid layout')
    # Two physical slots of f*K bits; any extra high bits are spectators.
    # Masks use least-significant-bit indexing; array order is integer order.
    x=[rho+j*K for j in range(f)]
    y=[f*K+rho+j*K for j in range(f)]
    return x,y,2*f*K+spectator_bits


def walsh_numerator(state,positions):
    """Unnormalized coordinate Walsh layers, with no layout permutation."""
    out=list(state)
    for position in positions:
        mask=1<<position
        for i in range(len(out)):
            if not i&mask:
                a,b=out[i],out[i|mask]
                out[i],out[i|mask]=gadd(a,b),gsub(a,b)
    return out


def controlled_phase(state,x_positions,y_positions):
    # D=product_j i^((2*y_j-1)*x_j), using current physical coordinates.
    return [phase_i(z,sum((2*((i>>y)&1)-1)*((i>>x)&1)
                         for x,y in zip(x_positions,y_positions)))
            for i,z in enumerate(state)]


def validate_positions(state,x_positions,y_positions):
    require(len(state)>0 and len(state)&(len(state)-1)==0,'State size must be a power of two')
    positions=list(x_positions)+list(y_positions)
    require(len(x_positions)==len(y_positions)>0,'Unequal or empty active sets')
    require(len(set(positions))==len(positions),'Active coordinates must be distinct')
    require(all(0<=p<len(state).bit_length()-1 for p in positions),'Invalid active coordinate')


def fused_numerator(state,x_positions,y_positions):
    """Return numerator and denominator of [2(1+i)]^f H0_y D H0_x D H0_y.

    More precisely, the normalization factor is [2(1+i)]^f. Cancellation
    with the three H0 denominators leaves numerator (1+i)^f/2^(2f).
    All arithmetic below uses exact Gaussian integer pairs.
    """
    validate_positions(state,x_positions,y_positions)
    out=walsh_numerator(state,y_positions)
    out=controlled_phase(out,x_positions,y_positions)
    out=walsh_numerator(out,x_positions)
    out=controlled_phase(out,x_positions,y_positions)
    out=walsh_numerator(out,y_positions)
    factor=(1,0)
    for _ in x_positions:factor=gmul(factor,(1,1))
    return [gmul(factor,z) for z in out],2**(2*len(x_positions))


def directional_numerator(state,directions):
    """Product C_v, evaluated directly; one factor has denominator two."""
    out=list(state)
    for v in directions:
        out=[gadd(gmul((1,1),z),gmul((1,-1),out[i^v])) for i,z in enumerate(out)]
    return out,2**len(directions)


def invertible_map(columns,x):
    value=0
    for i,col in enumerate(columns):
        if x>>i&1:value^=col
    return value


def permute(state,columns):
    out=[(0,0)]*len(state)
    for x,z in enumerate(state):out[invertible_map(columns,x)]=z
    return out


def sandwich_numerator(state,x_positions,y_positions,nbits):
    """P_M (product C_x) P_M^-1 for M: y_j <- y_j XOR x_j."""
    validate_positions(state,x_positions,y_positions)
    require(len(state)==1<<nbits,'Address dimension disagrees with state')
    columns=[1<<i for i in range(nbits)]
    for x,y in zip(x_positions,y_positions):columns[x]^=1<<y
    before=permute(state,columns)  # This M is its own inverse.
    middle,denominator=directional_numerator(before,[1<<x for x in x_positions])
    return permute(middle,columns),denominator


def rational_rank(matrix):
    rows=[[Q(x) for x in row] for row in matrix]
    rank=0
    if not rows:return 0
    for col in range(len(rows[0])):
        pivot=next((i for i in range(rank,len(rows)) if rows[i][col]),None)
        if pivot is None:continue
        rows[rank],rows[pivot]=rows[pivot],rows[rank]
        scale=rows[rank][col]
        rows[rank]=[x/scale for x in rows[rank]]
        for i in range(rank+1,len(rows)):
            scale=rows[i][col]
            if scale:rows[i]=[x-scale*y for x,y in zip(rows[i],rows[rank])]
        rank+=1
        if rank==len(rows):break
    return rank


def cut_rank(matrix,e,bit):
    """Off-diagonal rank from input bit=0 to output bit=1, all roles."""
    addresses=1<<e
    output=[i for i in range(len(matrix)) if (i%addresses)>>bit&1]
    inputs=[i for i in range(len(matrix[0])) if not ((i%addresses)>>bit&1)]
    return rational_rank([[matrix[i][j] for j in inputs] for i in output])


def walsh_matrix(e,roles=1,active=None,role=None):
    """Integer Walsh operator, optionally restricted to one role and axis set."""
    size=1<<e
    active=(1<<e)-1 if active is None else active
    matrix=[[0]*(roles*size) for _ in range(roles*size)]
    for w in range(roles):
        mask=active if role is None or role==w else 0
        for x in range(size):
            for y in range(size):
                if (x^y)&~mask==0:
                    matrix[w*size+x][w*size+y]=(-1)**((x&y&mask).bit_count())
    return matrix


def pointwise_matrix(e,gate):
    size=1<<e
    return [[gate[i//size][j//size] if i%size==j%size else 0
             for j in range(len(gate)*size)] for i in range(len(gate)*size)]


def matrix_product(left,right):
    return [[sum(a*b for a,b in zip(row,col)) for col in zip(*right)] for row in left]


def finite_identity_checks():
    checked=0
    for f,K,rho,spectators in ((1,1,0,1),(1,3,2,1),(2,1,0,1)):
        x,y,nbits=layout(f,K,rho,spectators)
        size=1<<nbits
        for basis in range(size):
            state=[(int(i==basis),0) for i in range(size)]
            fused,fd=fused_numerator(state,x,y)
            direct,dd=directional_numerator(state,[(1<<u)|(1<<v) for u,v in zip(x,y)])
            sandwich,sd=sandwich_numerator(state,x,y,nbits)
            require(direct==sandwich and dd==sd,'Basis sandwich disagrees with directional block')
            require(all((a[0]*dd,a[1]*dd)==(b[0]*fd,b[1]*fd)
                        for a,b in zip(fused,direct)), 'Fused block identity failed')
            checked+=1
    return dict(exhaustive_basis_inputs=checked,
                exact_gaussian_integer_arithmetic=True,
                direct_equals_basis_sandwich_equals_three_layer_block=True,
                coordinate_layer_calls=3,
                minimum_coordinate_calls_from_cut_budget=2,
                layout_permutations=0,
                scope='Finite exact identity; phase/scalar overhead has a separate written streaming audit. No faster recursive algorithm follows.')


def cut_controls():
    records=[]
    for e in (1,2,3):
        roles=2
        whole=walsh_matrix(e,roles)
        gate=pointwise_matrix(e,((1,0),(1,1)))
        for bit in range(e):
            target=cut_rank(whole,e,bit)
            free=cut_rank(gate,e,bit)
            one=walsh_matrix(e,roles,1<<bit,role=0)
            child=cut_rank(one,e,bit)
            require(target==roles*2**(e-1) and free==0 and child==2**(e-1),
                    'Cut-rank normalization failed')
            # The inequality must hold even when same-cut factors cancel.
            for right in (one,gate,whole):
                prod=matrix_product(one,right)
                require(cut_rank(prod,e,bit)<=child+cut_rank(right,e,bit),
                        'Subadditivity failed')
            records.append(dict(axes=e,bit=bit,target_rank=target,
                                pointwise_rank=free,one_role_child_rank=child))
    return records


def certificate():
    n=network(25)
    return dict(status='FUSED BLOCK IDENTITY AND SCOPED OBSTRUCTION; NO NEW KAPPA',
                upstream_commit=verify_sources(),block=finite_identity_checks(),
                cut_controls=cut_controls(),
                recursion=dict(required_all_role_cut_budget='W*e',
                               maximum_budget_per_f_axis_child='f',
                               minimum_child_calls='W*e/f = W*m when e=m*f',
                               contraction_required='S<W*m',
                               conclusion='Coordinate-butterfly children and address-pointwise gates alone cannot meet the strict contraction requirement, even after arbitrary legal fusion.',
                               scope='Fixed all-role recursive templates with complete equal-volume address arrays; counts these child calls. Not a lower bound on general tape algorithms or primitives that move addresses.'),
                reference_complex_network=dict(h=25,W=n['Wc'],m=n['m'],s=n['sc'],
                                               contraction_deficit=n['Wc']*n['m']-n['sc']),
                next_step='Any surviving design must include a costed noncoordinate operation: sparse address movement or a direct directional butterfly not built solely from coordinate children and pointwise gates.')


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/fused-block-audit.json').write_text(
        json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS exact fused block; the three-child construction fails the contraction budget.')
    print('Coordinate-child/pointwise-only fusion is excluded in the stated recursive model.')
