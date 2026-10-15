#!/usr/bin/env python3
"""Bounded sparse/fused-primitive audit; no new multiplication bound.

Quadratic phase signatures describe exact products of directional C kernels.
They do not grant permission to commute a phase through a scalar mixing gate.
"""
from collections import deque
from fractions import Fraction as Q
from itertools import combinations, product
import json
from pathlib import Path

from certify import require, verify_sources
from prepare_layers import BIT_SAVING, scenarios, serializable

ROOT=Path(__file__).resolve().parents[1]


def parity(value):
    return value.bit_count()%2


def signature(dimension, directions=()):
    """q(x)=sum d_i*x_i+2 sum b_ij*x_i*x_j mod 4.

    Each (v,sign) contributes sign*[v dot x], the Fourier eigenphase of C_v.
    A zero direction is the identity. Signs may be arbitrary integers.
    """
    require(dimension>=1,'Positive dimension required')
    diagonal=[0]*dimension
    cross=[0]*(dimension*(dimension-1)//2)
    for v,sign in directions:
        require(0<=v<1<<dimension,'Direction exceeds dimension')
        for i in range(dimension):
            diagonal[i]=(diagonal[i]+sign*((v>>i)&1))%4
        k=0
        for i in range(dimension):
            for j in range(i+1,dimension):
                cross[k]=(cross[k]+sign*((v>>i)&1)*((v>>j)&1))%2
                k+=1
    return tuple(diagonal+cross)


def phase_value(dimension, phase, x):
    require(len(phase)==dimension+dimension*(dimension-1)//2,'Wrong signature size')
    value=sum(phase[i]*((x>>i)&1) for i in range(dimension))
    k=dimension
    for i in range(dimension):
        for j in range(i+1,dimension):
            value+=2*phase[k]*((x>>i)&1)*((x>>j)&1)
            k+=1
    return value%4


def add_phase(dimension,left,right):
    return tuple((a+b)%(4 if i<dimension else 2)
                 for i,(a,b) in enumerate(zip(left,right)))


def minimum_words(dimension):
    """Exact BFS in the finite phase group; one C_v or inverse is one call.

    The cost excludes physical basis changes, so it is an optimistic scalar
    count, not a tape implementation bound.
    """
    require(1<=dimension<=3,'Bound this audit to dimensions at most three')
    zero=signature(dimension)
    words={zero:()}
    queue=deque([zero])
    generators=[(v,sign,signature(dimension,[(v,sign)]))
                for v in range(1,1<<dimension) for sign in (1,-1)]
    while queue:
        current=queue.popleft()
        for v,sign,step in generators:
            target=add_phase(dimension,current,step)
            if target not in words:
                words[target]=words[current]+((v,sign),)
                queue.append(target)
    require(len(words)==4**dimension*2**(dimension*(dimension-1)//2),
            'Generators did not span the phase group')
    return words


def binary_rank(columns):
    basis={}
    for value in columns:
        while value:
            pivot=value.bit_length()-1
            if pivot in basis:value^=basis[pivot]
            else:
                basis[pivot]=value
                break
    return len(basis)


def polar_columns(dimension,phase):
    """The bilinear form (q(x+y)-q(x)-q(y))/2 over F2."""
    columns=[(phase[i]%2)<<i for i in range(dimension)]
    k=dimension
    for i in range(dimension):
        for j in range(i+1,dimension):
            if phase[k]:
                columns[i]^=1<<j
                columns[j]^=1<<i
            k+=1
    return columns


def mixes_commute(matrix,phases):
    """Exact criterion for a scalar G to commute with per-role phase frames."""
    require(len(matrix)==len(phases) and all(len(r)==len(phases) for r in matrix),
            'Expected a square scalar gate and one phase per role')
    return all(not entry or phases[i]==phases[j]
               for i,row in enumerate(matrix) for j,entry in enumerate(row))


def central_gate_screen(h=25):
    """Rank lower bound for changing just a central frame's active h-factor.

    The written proof covers every symmetric polar matrix Q. This bounded
    screen checks all symmetric 3x3 changes embedded in the original I_h.
    It is not a search over new gate topologies or coupled frame changes.
    """
    require(h>=22,'Use the admissible complex family')
    triples=[sum(1<<i for i in t) for t in combinations(range(h),3)]
    v=len(triples);centers=h+1
    baseline=v*(h-1)+2*centers*h
    minimum_changed=None
    frames=[]
    for bits in range(64):
        Qcols=[1<<i for i in range(h)]
        Qcols[:3]=[0,0,0]
        at=0
        for i in range(3):
            for j in range(i,3):
                if bits>>at&1:
                    Qcols[j]^=1<<i
                    if i!=j:Qcols[i]^=1<<j
                at+=1
        k=binary_rank(Qcols)
        r=binary_rank([col^(1<<i) for i,col in enumerate(Qcols)])
        unary=sum(binary_rank([col^(t if t>>i&1 else 0)
                                for i,col in enumerate(Qcols)])+r for t in triples)
        frames.append((Qcols,k,r,unary))
        if r==0:continue
        actual=unary+2*centers*k
        proved_increase=v*(k+r-h)+2*(Q(v,h)-centers)*(h-k)
        require(actual-baseline>=proved_increase>0,'Central-frame lower bound failed')
        minimum_changed=actual if minimum_changed is None else min(actual,minimum_changed)
    # Allow both middle central frames to change. The other two central
    # frames can be eliminated from this LOWER bound by triangle inequalities.
    joint_baseline=2*v*(h-1)+3*centers*h
    joint_min_changed=None
    for A,kA,rA,unaryA in frames:
        for IC,kIC,rIC,unaryIC in frames:
            # The second middle frame is C=I+IC.
            AC=[x^y^(1<<i) for i,(x,y) in enumerate(zip(A,IC))]
            actual=unaryA+unaryIC+centers*(kA+binary_rank(AC)+kIC)
            x,y=h-kA,h-kIC
            u,w=kA+rA-h,kIC+rIC-h
            lower=(v-centers)*(u+w)+2*(Q(v,h)-centers)*(x+y)
            require(actual-joint_baseline>=lower>=0,'Joint central-frame bound failed')
            if rA or rIC:
                require(lower>0,'Nonoriginal middle frames escaped strict bound')
                joint_min_changed=actual if joint_min_changed is None else min(joint_min_changed,actual)
            else:require(actual==joint_baseline,'Original central frame score changed')
    return dict(h=h,triples=v,center_roles=centers,baseline_incident_rank=baseline,
                sampled_changed_frames=63,minimum_sampled_changed_rank=minimum_changed,
                rank_density=Q(v,h),density_minus_center_count=Q(v,h)-centers,
                joint_frame_pairs=4096,joint_baseline=joint_baseline,
                joint_minimum_changed_rank=joint_min_changed,
                theorem='The original four central frames jointly minimize the directional rank lower bound when side frames and the active h-factor are fixed.',
                scope='All four central frames may vary, but side frames, topology and the tensor factor are retained. Does not exclude changing those ingredients or the tape primitive.')


def finite_audit():
    words=minimum_words(3)
    # All seven nonzero 3-bit linear forms have phase sum zero modulo four.
    all_seven=[(v,1) for v in range(1,8)]
    require(signature(3,all_seven)==signature(3),'Seven-direction identity failed')
    six=[(v,1) for v in range(1,8) if v!=1]
    require(signature(3,six)==signature(3,[(1,-1)]),'Six-to-one identity failed')
    require(len(words[signature(3,six)])==1,'Scalar minimum not reproduced')

    # A nontrivial collective symmetry in dimension six: M=I+J over F2.
    columns=[63^(1<<i) for i in range(6)]
    require(binary_rank(columns)==6,'Collective symmetry is singular')
    require(signature(6,[(v,1) for v in columns])==
            signature(6,[(1<<i,1) for i in range(6)]),
            'Collective conjugation identity failed')

    # Exhaust GL(3,2), checking that preserving a coordinate phase also
    # preserves its active coordinate subspace. This is a finite control
    # for the general polar-form proof in the accompanying note.
    total=preserving=0
    for columns3 in product(range(1,8),repeat=3):
        if binary_rank(columns3)!=3:continue
        total+=1
        for active in range(1,8):
            left=signature(3,[(columns3[i],1) for i in range(3) if active>>i&1])
            right=signature(3,[(1<<i,1) for i in range(3) if active>>i&1])
            if left==right:
                preserving+=1
                require(all(columns3[i]&~active==0 for i in range(3) if active>>i&1),
                        'A coordinate phase stabilizer moved its active subspace')
    require(total==168,'GL(3,2) enumeration is incomplete')

    # Moving a phase through a mixing gate is a separate algebraic condition.
    zero=signature(3)
    one=signature(3,[(1,1)])
    shear=((1,0),(1,1))
    require(not mixes_commute(shear,(one,zero)),'Unequal-frame shear unexpectedly commutes')
    require(mixes_commute(shear,(one,one)),'Common phase must commute')
    require(mixes_commute(((1,0),(0,-1)),(one,zero)),
            'A diagonal scalar gate should allow independent phases')

    return dict(phase_group_dimension=3,phase_group_size=len(words),
                maximum_minimum_direction_calls=max(map(len,words.values())),
                all_seven_product_is_identity=True,
                six_direction_product_equals_inverse_of_missing_direction=True,
                six_direction_minimum_calls=1,
                collective_symmetry_dimension=6,collective_symmetry_columns=columns,
                gl3_invertible_matrices=total,gl3_phase_preserving_pairs=preserving,
                unequal_phase_shear_commutes=False,
                scope='Exact operator identities and optimistic directional-call distances; no tape cost or legal cross-gate fusion is inferred.')


def candidate_budgets():
    rows={}
    for name,row in scenarios().items():
        if not row['recurrence']['hypothetical']:continue
        p=row['parameters']
        target_gap=p['kappa']/p['epsilon']
        r=p['tau'];beta=p['beta'];sigma=p['sigma'];c=p['c']
        # Feasibility requires chi<1-kappa/epsilon, before choosing lambda.
        max_theta=(1-target_gap-r-(1-beta)*max(sigma-r,Q(0)))/c
        # Alternative theta=1/1000 in the sigma>r branch.
        theta=Q(1,1000)
        required_active_saving=(theta*c+target_gap-(1-beta)*(1-sigma))/beta
        require(0<required_active_saving<1 and required_active_saving>1-sigma,
                'Alternative active-saving regime does not apply')
        rows[name]=dict(target=p['kappa'],beta=beta,c=c,
                       maximum_spacing_exponent_at_current_active_saving=max_theta,
                       alternative_spacing_exponent=theta,
                       necessary_active_saving_for_alternative=required_active_saving,
                       note='Strict necessary internal-cost budgets for these fixed parameters, not a primitive or sufficient whole-algorithm certificate.')
    return rows


def certificate():
    a=BIT_SAVING;tau=1-a
    return dict(status='BOUNDED SPARSE/FUSION AUDIT; NO NEW MULTIPLICATION EXPONENT',
                upstream_commit=verify_sources(),finite=finite_audit(),
                central_frame_screen=central_gate_screen(),
                candidate_budgets=candidate_budgets(),
                batching=dict(existing_active_exponent=tau,spacing_exponent=tau,
                              necessary_c_upper=a/tau,
                              proof='For positive batch sizes b_i summing to f, sum b_i^tau >= f^tau. Separate calls to the existing whole-slot bound cannot improve its exponent by batching alone.',
                              scope='Optimizing these certified separate-call upper bounds, not a lower bound on actual tape time.'),
                next_step='Search coordinated side/central changes, a new gate topology, or a new sparse address primitive. Central-only relabeling is excluded in the audited model. Require the complete gate product and tape accounting.')


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/sparse-fusion-audit.json').write_text(
        json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS bounded sparse/fusion audit; phase group size',result['finite']['phase_group_size'])
    print('Six-to-one scalar fusion verified; intervening mixing gates remain an obstruction.')
