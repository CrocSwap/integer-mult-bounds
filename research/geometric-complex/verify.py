"""Reproducible exact checks for a proposed geometric complex motif.

No floating point is used in acceptance criteria. The certificate records
finite evidence and conditional arithmetic, not a formal theorem proof.
"""
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import json
import random

from explore import Circuit, counts, assembly, serializable, log_integer_bounds


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length()-1
        mask ^= bit


def projector(c, z):
    h = c.n+1
    if c.relation == 'disjoint' and c.args[z] is not None:
        basis = [1 << i for i in bits(c.union[z])]
    else:
        basis = [c.masks[i] for i in bits(c.support[z])]
    for i,u in enumerate(basis):
        for j,v in enumerate(basis):
            assert ((u & v).bit_count() % 2) == (i == j)
    rows = [0]*h
    for u in basis:
        for i in bits(u):
            rows[i] ^= u
    return tuple(rows)


def product(a,b):
    out=[]
    for row in a:
        x=0
        for i in bits(row):
            x ^= b[i]
        out.append(x)
    return tuple(out)


def rank(rows):
    pivots={}
    for x in rows:
        while x:
            p=x.bit_length()-1
            if p in pivots:
                x ^= pivots[p]
            else:
                pivots[p]=x
                break
    return len(pivots)


def residual(a,b):
    """Validate nesting and nonalternation directly from binary projectors."""
    assert product(a,b) == a == product(b,a)
    r=tuple(x^y for x,y in zip(a,b))
    assert product(r,r) == r
    assert rank(r) == rank(b)-rank(a)
    if any(r):
        # Q_ii = norm(Q e_i); a nonzero diagonal witnesses a norm-one vector.
        assert any(row & (1 << i) for i,row in enumerate(r))


def small_frame_audit(c):
    code=c.compile()
    h=c.n+1
    zero=(0,)*h
    full=tuple(1 << i for i in range(h))
    ps={z:projector(c,z) for z in c.active}
    comp=lambda p:tuple(x^y for x,y in zip(full,p))
    states=[zero]*code['roles']
    checks=0
    for z,slot in code['sources'].items():
        residual(zero,ps[z]);states[slot]=ps[z];checks+=1
    for z,ins,outs in code['gates']:
        for slot in set(ins+outs):
            residual(states[slot],ps[z]);checks+=1
            states[slot]=ps[z]
    for key,slot in code['outputs'].items():
        j=key if c.relation == 'disjoint' else key[1]
        residual(states[slot],comp(projector(c,j)));checks+=1
        states[slot]=comp(projector(c,j))
    for state in states:
        residual(state,full);checks+=1
    # Reverse execution uses complement frames, and physical banks exchange.
    states=[zero]*code['roles']
    for key,slot in code['outputs'].items():
        j=key if c.relation == 'disjoint' else key[1]
        residual(zero,projector(c,j));checks+=1
        states[slot]=projector(c,j)
    for z,ins,outs in reversed(code['gates']):
        for slot in set(ins+outs):
            residual(states[slot],comp(ps[z]));checks+=1
            states[slot]=comp(ps[z])
    for z,slot in code['sources'].items():
        residual(states[slot],comp(ps[z]));checks+=1
        states[slot]=comp(ps[z])
    for state in states:
        residual(state,full);checks+=1
    return checks


def apply_mixer(values,code,inverse=False):
    gates=reversed(code['gates']) if inverse else code['gates']
    for _,ins,outs in gates:
        pivot=ins[0]
        if inverse:
            for slot in reversed(outs[1:]):values[slot]-=values[pivot]
            for slot in reversed(ins[1:]):values[pivot]-=values[slot]
        else:
            for slot in ins[1:]:values[pivot]+=values[slot]
            for slot in outs[1:]:values[slot]+=values[pivot]


def scalar_audit(n):
    circuits=[Circuit(n,'disjoint'),Circuit(n,'intersection_two')]
    codes=[c.compile() for c in circuits]
    v=circuits[0].v
    sizes=[code['roles'] for code in codes]
    width=2*v+sum(sizes)+n+1
    def forward(values,reverse=False):
        x=list(values[:v]);y=list(values[v:2*v])
        side=[];offset=2*v
        for size in sizes:
            side.append(list(values[offset:offset+size]));offset+=size
        center=list(values[offset:])
        def L(sign):
            for z,code in zip(side,codes):apply_mixer(z,code,sign<0)
        def J(sign):
            for c,code,z,weight in zip(circuits,codes,side,(Q(1,2),Q(-1,2))):
                for key,slot in code['outputs'].items():
                    j=key if c.relation == 'disjoint' else key[1]
                    y[j]+=sign*weight*z[slot]
        def V(sign):
            for code,z in zip(codes,side):
                for source,slot in code['sources'].items():z[slot]+=sign*x[source]
        def G(sign):
            for j,t in enumerate(circuits[0].triples):
                for i in t:center[i]+=sign*x[j]
                center[n]+=sign*x[j]
        def R(sign):
            for j,t in enumerate(circuits[0].triples):
                y[j]+=sign*(sum(center[i] for i in t)-center[n])/2
        schedule=[(L,1),(J,-1),(L,-1),(R,-1),(V,1),(G,1),
                  (R,1),(L,1),(J,1),(L,-1),(G,-1),(V,-1)]
        if reverse:schedule=[(op,-sign) for op,sign in reversed(schedule)]
        for op,sign in schedule:op(sign)
        return x+y+[z for block in side for z in block]+center
    # All basis vectors, including every dirty-scratch direction.
    for index in range(width):
        initial=[Q(0)]*width;initial[index]=Q(1)
        for reverse in (False,True):
            expected=list(initial)
            if index<v:expected[v+index]+=(-1 if reverse else 1)
            assert forward(initial,reverse)==expected
    rng=random.Random(109)
    for _ in range(12):
        initial=[Q(rng.randrange(-20,21),1 << rng.randrange(4)) for _ in range(width)]
        out=forward(initial)
        expected=list(initial)
        expected[v:2*v]=[a+b for a,b in zip(initial[v:2*v],initial[:v])]
        assert out==expected and forward(out,True)==initial
        # Three shears on whole banks: (X,Y)->(-Y,X), dirty scratch restored.
        second_input=out[v:2*v]+out[:v]+out[2*v:]
        second=forward(second_input,True)
        third_input=second[v:2*v]+second[:v]+second[2*v:]
        third=forward(third_input)
        assert third==[-x for x in initial[v:2*v]]+initial[:v]+initial[2*v:]
    return dict(n=n,scalar_basis_directions=width,both_orientations=True,
                random_dyadic_cases=12,three_shear_signed_exchange=True,
                arbitrary_scratch_basis_checked=True)


def full_structural_audit(c):
    c.verify()
    code=c.compile()
    # Validate the frame kind of every node, rather than sampling matrices.
    for z in c.active:
        if c.relation == 'intersection_two':
            core=(1 << c.n)-1
            count=0
            for i in bits(c.support[z]):
                core &= c.masks[i];count+=1
            assert count==1 or core.bit_count()==2
            # Triples in a fixed pair-star are pairwise orthonormal over F2.
        elif c.args[z] is not None:
            assert c.union[z].bit_count()>=4
        # The extra coordinate is absent from every intermediate envelope.
        assert not c.union[z] & (1 << c.n)
    def contained(a,b):
        if c.relation == 'intersection_two':
            return not c.support[a] & ~c.support[b]
        if c.args[b] is None:
            return a==b
        return not c.union[a] & ~c.union[b]
    states=[None]*code['roles']
    for z,slot in code['sources'].items():states[slot]=z
    edges=0
    for z,ins,outs in code['gates']:
        for slot in set(ins+outs):
            assert states[slot] is None or contained(states[slot],z)
            states[slot]=z;edges+=1
    for key,slot in code['outputs'].items():
        assert states[slot]==c.outputs[key]
        j=key if c.relation=='disjoint' else key[1]
        if c.relation=='disjoint':assert not c.union[states[slot]] & c.masks[j]
        else:
            assert all((c.masks[i]&c.masks[j]).bit_count()==2
                       for i in bits(c.support[states[slot]]))
    states=[None]*code['roles']
    for key,slot in code['outputs'].items():states[slot]=c.outputs[key]
    for z,ins,outs in reversed(code['gates']):
        for slot in set(ins+outs):
            assert states[slot] is None or contained(z,states[slot])
            states[slot]=z;edges+=1
    for z,slot in code['sources'].items():assert states[slot]==z
    digest=sha256()
    for z in sorted(c.active):
        digest.update(f'{z}:{c.args[z]}:{c.support[z]}\n'.encode())
    for key,z in sorted(c.outputs.items()):digest.update(f'{key}:{z}\n'.encode())
    return dict(**c.verify(),compiled_roles=code['roles'],nested_role_incidences=edges,
                dummy_coordinate_unused=True,circuit_sha256=digest.hexdigest())


def certificate():
    from certify import verify_sources
    from audit import certificate as physical_audit
    n=25
    out=counts(n)
    ac=Q(4,10**9)
    _,loghi=log_integer_bounds(out['m'])
    assert out['eta']>ac*loghi
    assert out['N']>out['L'] and out['depth_hypothesis']
    result=assembly(ac,n)
    assert result['all_slacks_positive']
    k=result['parameters']['kappa']
    assert result['minimum_margin']>k>Q(1,2**31)
    E=64*(out['W']+out['m']+1)**3
    I=3*out['v']**2
    scalar_depth_bound=32*I*(out['side_roles']+out['v']+n+1)
    assert scalar_depth_bound+4*out['s']+4*out['W']+4<E
    B=out['s']+E
    zeta=Q(1,10000)
    raw=max(128*out['m']*B*B,18*out['m']*B*B*(1+1/zeta))
    C0=-(-raw.numerator//raw.denominator)
    assert 9*out['m']*B*B*(1+1/zeta)+18<=C0
    assert out['s']*(8+E)<=9*B*B
    small=[]
    for n0 in (6,7):
        frames=sum(small_frame_audit(Circuit(n0,r)) for r in ('disjoint','intersection_two'))
        small.append(dict(**scalar_audit(n0),direct_binary_residual_checks=frames))
    # An intentional failure: with no dummy, complement of the target triple
    # inside its coordinate support is alternating. This detects the reason
    # the geometric extension is needed.
    h=6;target=7
    tproj=tuple(target if target&(1 << i) else 0 for i in range(h))
    outside=tuple(1 << i if i>=3 else 0 for i in range(h))
    full=tuple(1 << i for i in range(h))
    target_complement=tuple(a^b for a,b in zip(full,tproj))
    rejected=False
    try:residual(outside,target_complement)
    except AssertionError:rejected=True
    assert rejected
    out.update(complex_saving=ac,complex_deficit_slack=out['eta']-ac*loghi,
               assembly=result,guard=dict(E=E,B=B,C0=C0,scalar_depth_bound=scalar_depth_bound),
               full_circuits=[full_structural_audit(Circuit(n,r))
                              for r in ('disjoint','intersection_two')],
               small_audits=small,missing_dummy_negative_control_rejected=True,
               physical_phase_audit=physical_audit(),
               improvement_factor=k/Q(83,10**12),
               upstream_commit=verify_sources(),
               status='CONDITIONAL RESEARCH CANDIDATE; NOT INDEPENDENT OR FORMAL VERIFICATION',
               repository_base='6e564879f51ae16f23d392e9e196c605f36d90df',
               scope='New written geometric finite-network argument plus retained upstream and compact-control interfaces. No full multiplication machine or manuscript integration patch.')
    folder=Path(__file__).resolve().parent
    out['source_sha256']={name:sha256((folder/name).read_bytes()).hexdigest()
                          for name in ('explore.py','verify.py','audit.py','bit_screen.py','geometric-note.tex')}
    retained=['notes/paired-construction.tex','notes/compact-control-movement.tex',
              'notes/compact-control-layout.tex','notes/compact-control-guard.tex',
              'notes/independent-complex.tex','scripts/certify.py',
              'scripts/prepare_layers.py','scripts/compact_control_layer.py',
              'scripts/search_network.py','scripts/paired_network.py']
    from explore import ROOT
    out['retained_source_sha256']={name:sha256((ROOT/name).read_bytes()).hexdigest()
                                   for name in retained}
    return serializable(out)


if __name__=='__main__':
    result=certificate()
    path=Path(__file__).resolve().with_name('certificate.json')
    path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS exact geometric candidate checks; conditional kappa='+result['assembly']['parameters']['kappa'])
    print('PASS full circuit supports, role paths, finite binary residuals, dirty-scratch basis, negative control, guard and assembly.')
