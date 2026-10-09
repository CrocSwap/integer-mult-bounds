#!/usr/bin/env python3
"""Reusable weighted side circuits with binary phase-frame certificates.

New finite-network construction, conditional on the written transfer proof.
The published compact-control certificate and upstream sources are unchanged.
"""
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
from itertools import combinations, product
from math import comb
from pathlib import Path
import json

from binary_phase_frames import basis, certify_chain, nullspace
from certify import Parameters, constraints, margins, require, verify_sources
from exclusion_circuit import ExclusionCircuit
from incidence_rectangles import Plan, rectangles, stars
from paired_network import BIT_SAVING
from prepare_layers import serializable
from search_network import log_integer_bounds, log_ratio_bounds

ROOT = Path(__file__).resolve().parents[1]


@cache
def disjoint_plan(n, a=3, b=3):
    """Exact partition; optimize only stars and recursive unweighted splits."""
    assert n >= 0 and 0 <= a <= 3 and 0 <= b <= 3
    if a+b > n:
        return Plan(n, a, b, 0, 0, 0, 'empty')
    if not a or not b:
        return Plan(n, a, b, 1, comb(n, a), comb(n, b), 'base')
    winner = min((stars(n, a, b, 'rows'), stars(n, a, b, 'cols')), key=lambda p:p.score())
    for left in range(1, n):
        terms = tuple((disjoint_plan(left, x, y), disjoint_plan(n-left, a-x, b-y))
                      for x in range(a+1) for y in range(b+1)
                      if x+y <= left and a+b-x-y <= n-left)
        p = Plan(n, a, b, sum(A.count*B.count for A, B in terms),
                 sum(A.left*B.left for A, B in terms),
                 sum(A.right*B.right for A, B in terms), 'split', left, terms)
        if p.score() < winner.score():
            winner = p
    return winner


class LeaveOneCircuit(ExclusionCircuit):
    """Disjoint-support sums of all but one input, with reusable compilation."""
    def __init__(self, n):
        assert n >= 3
        self.n = n
        self.inputs = list(range(n))
        self.support = [0]+[1 << i for i in range(n)]
        self.args = [None]*len(self.support)
        self.lookup = {s:i for i, s in enumerate(self.support)}
        self.variables = {i:i+1 for i in range(n)}
        _, values, _ = self.vector(list(range(1, n+1)), two=False)
        self.outputs = dict(enumerate(values))
        self.active = set()
        stack = list(values)
        while stack:
            node = stack.pop()
            if not node or node in self.active:
                continue
            self.active.add(node)
            if self.args[node]:
                stack.extend(self.args[node])
        self.additions = sum(self.args[i] is not None for i in self.active)

    def verify(self):
        assert self.additions == 3*self.n-6
        for i, node in self.outputs.items():
            assert self.support[node] == ((1 << self.n)-1) ^ (1 << i)
        for node in self.active:
            if self.args[node]:
                a, b = self.args[node]
                assert not self.support[a] & self.support[b]
                assert self.support[node] == self.support[a] | self.support[b]
        code = self.compile()
        values = [0]*code['roles']
        forward_frames = [0]*code['roles']
        for i, slot in code['sources'].items():
            values[slot] = forward_frames[slot] = 1 << i
        for node, ins, outs in code['gates']:
            for slot in set(ins+outs):
                assert not forward_frames[slot] & ~self.support[node]
                forward_frames[slot] = self.support[node]
            for i in ins[1:]:
                assert not values[ins[0]] & values[i]
                values[ins[0]] |= values[i]
            for i in outs[1:]:
                assert values[i] == 0
                values[i] = values[ins[0]]
        for i, slot in code['outputs'].items():
            assert values[slot] == ((1 << self.n)-1) ^ (1 << i)
        descendants = {node:0 for node in self.active}
        reverse_frames = [0]*code['roles']
        for i,node in self.outputs.items():
            descendants[node] |= 1 << i
            reverse_frames[code['outputs'][i]] = 1 << i
        for node in sorted(self.active,reverse=True):
            if self.args[node]:
                for parent in self.args[node]:descendants[parent] |= descendants[node]
        for node,ins,outs in reversed(code['gates']):
            for slot in set(ins+outs):
                assert not reverse_frames[slot] & ~descendants[node]
                reverse_frames[slot] = descendants[node]
        for i,slot in code['sources'].items():
            assert reverse_frames[slot] == ((1 << self.n)-1) ^ (1 << i)
        return dict(inputs=self.n, additions=self.additions, outputs=self.n,
                    roles=code['roles'], exact_integer_coefficient_map=True,
                    forward_and_reverse_support_frames_nested=True)


def mask(points):
    return sum(1 << x for x in points)


def rectangle_frame(sources, targets, h):
    """Common physical-source frame; swap arguments for the inverse stage."""
    if len(sources) == 1:
        return (mask(sources[0]),)
    if len(targets) == 1:
        return nullspace((mask(targets[0]),), h)
    used = set().union(*map(set, sources))
    return tuple(1 << i for i in sorted(used))


def verify_disjoint_partition(h):
    triples = list(combinations(range(h), 3))
    indices = {t:i for i, t in enumerate(triples)}
    v = len(triples)
    seen = bytearray(v*v)
    plan = disjoint_plan(h)
    totals = [0, 0, 0]
    frame_types = dict(source_line=0, target_complement=0, coordinate=0)
    digest = sha256()
    edges = 0
    for sources, targets in rectangles(plan):
        A = set().union(*map(set, sources)); B = set().union(*map(set, targets))
        assert not A & B
        if len(sources) == 1:
            frame_types['source_line'] += 1
            assert h > 6
        elif len(targets) == 1:
            frame_types['target_complement'] += 1
            assert h > 6
        else:
            frame_types['coordinate'] += 1
            assert len(A) >= 4 and len(B) >= 4
        totals[0] += 1; totals[1] += len(sources); totals[2] += len(targets)
        si = [indices[s] for s in sources]; ti = [indices[t] for t in targets]
        digest.update(json.dumps([si, ti], separators=(',', ':')).encode()+b'\n')
        for i in si:
            for j in ti:
                index = i*v+j
                assert not seen[index], 'Duplicate disjoint-triple coefficient'
                seen[index] = 1
                edges += 1
    assert totals == [plan.count, plan.left, plan.right]
    assert edges == v*comb(h-3, 3)
    return dict(h=h, rectangles=plan.count, source_memberships=plan.left,
                target_memberships=plan.right, roles=plan.score(), coefficients=edges,
                every_ordered_disjoint_pair_once=True, frame_types=frame_types,
                partition_sha256=digest.hexdigest())


def phase_controls(h=8):
    """Exact local residual bases in both directions for every small rectangle."""
    full = tuple(1 << i for i in range(h))
    checked = 0
    for sources, targets in rectangles(disjoint_plan(h)):
        for S, T in ((sources, targets), (targets, sources)):
            U = rectangle_frame(S, T, h)
            certify_chain(((), U, full))
            for s in S:
                certify_chain(((mask(s),), U, full))
            for t in T:
                certify_chain(((), U, nullspace((mask(t),), h), full))
            checked += 1
    # Fixed-pair indicator vectors plus two extras form an explicit full basis.
    for pair in combinations(range(h), 2):
        points = [i for i in range(h) if i not in pair]
        vectors = [mask((*pair, i)) for i in points]
        extras = [mask((i, *points)) for i in pair]
        from binary_phase_frames import dot
        all_vectors = vectors+extras
        assert all(dot(a,b)==(i==j) for i,a in enumerate(all_vectors)
                   for j,b in enumerate(all_vectors))
        for size in range(1, len(points)):
            U = vectors[:size]
            certify_chain(((), U, nullspace((vectors[size],), h), full))
    return dict(h=h, directed_rectangle_checks=checked,
                all_local_residual_bases_constructed=True, pair_basis_checked=True)


def matching(h):
    assert h >= 8 and h % 2 == 0
    triples = list(combinations(range(h), 3))
    index = {t:i for i,t in enumerate(triples)}
    pi = [index[tuple(sorted(x ^ 1 for x in t))] for t in triples]
    assert len(set(pi)) == len(triples)
    assert all(len(set(t)&set(triples[j])) in (0,2) for t,j in zip(triples,pi))
    return triples, pi


def counts(h=26):
    assert h >= 8 and h % 2 == 0
    v=comb(h,3); N=v**3; m=h**3
    R0=disjoint_plan(h).score()
    R2=comb(h,2)*(4*(h-2)-6)
    R=R0+R2; L=3*v*v*h*(h+1)
    W=2*N+2*v*v*(R+h+1)
    deficit=2*N-2*L
    return dict(h=h,v=v,N=N,m=m,disjoint_roles=R0,intersection_two_roles=R2,
                side_roles=R,central_roles=h+1,L=L,W=W,s=W*m-deficit,
                deficit=deficit,eta=Q(deficit,W*m))


def saving_bounds(n):
    assert 0 < n['eta'] < Q(1,2)
    lo,hi=log_ratio_bounds(1/(1-n['eta']),terms=4)
    dlo,dhi=log_integer_bounds(n['m'])
    return lo/dhi,hi/dlo


def scalar_program(h):
    """Weighted rectangle and leave-one circuits, over characteristic zero."""
    triples=list(combinations(range(h),3));index={t:i for i,t in enumerate(triples)}
    gates=[];sources=[];outputs=[];offset=0
    for S,T in rectangles(disjoint_plan(h)):
        ins=tuple(range(offset,offset+len(S)))
        outs=(offset,)+tuple(range(offset+len(S),offset+len(S)+len(T)-1))
        gates.append((ins,outs))
        sources.extend((index[s],slot) for s,slot in zip(S,ins))
        outputs.extend((index[t],slot,Q(1,2)) for t,slot in zip(T,outs))
        offset+=len(S)+len(T)-1
    c=LeaveOneCircuit(h-2);code=c.compile()
    for pair in combinations(range(h),2):
        rest=[x for x in range(h) if x not in pair]
        def idx(i):return index[tuple(sorted((*pair,rest[i])))]
        for _,ins,outs in code['gates']:
            gates.append((tuple(offset+i for i in ins),tuple(offset+i for i in outs)))
        sources.extend((idx(i),offset+slot) for i,slot in code['sources'].items())
        outputs.extend((idx(i),offset+slot,Q(-1,2)) for i,slot in code['outputs'].items())
        offset+=code['roles']
    assert offset==counts(h)['side_roles']
    return dict(h=h,triples=triples,gates=gates,sources=sources,outputs=outputs,roles=offset)


def invoke(x,y,scratch,center,code,inverse=False):
    """Twelve signed operations; no temporary is assumed zero."""
    def mix(sign):
        for ins,outs in (code['gates'] if sign==1 else reversed(code['gates'])):
            pivot=ins[0]
            if sign==1:
                for i in ins[1:]:scratch[pivot]+=scratch[i]
                for j in outs[1:]:scratch[j]+=scratch[pivot]
            else:
                for j in outs[1:]:scratch[j]-=scratch[pivot]
                for i in ins[1:]:scratch[pivot]-=scratch[i]
    def copy(sign):
        for i,slot in code['sources']:scratch[slot]+=sign*x[i]
    def inject(sign):
        for i,slot,weight in code['outputs']:y[i]+=sign*weight*scratch[slot]
    def gather(sign):
        for i,t in enumerate(code['triples']):
            for point in t:center[point]+=sign*x[i]
            center[-1]+=sign*x[i]
    def scatter(sign):
        for i,t in enumerate(code['triples']):
            y[i]+=sign*Q(1,2)*(sum(center[point] for point in t)-center[-1])
    operations=((mix,1),(inject,-1),(mix,-1),(scatter,-1),(copy,1),(gather,1),
                (scatter,1),(mix,1),(inject,1),(mix,-1),(gather,-1),(copy,-1))
    if inverse:operations=tuple((op,-sign) for op,sign in reversed(operations))
    for op,sign in operations:op(sign)


def assembly_control(h=26):
    """Exact witness used by make_complex_compression_patch.py."""
    n=counts(h);ac=Q(5,10**9);a=BIT_SAVING
    require(saving_bounds(n)[0]>ac,'Unsupported compressed-complex saving')
    beta=Q(1,100);zeta=Q(1,1000);C1=5-4*beta+zeta
    p=Parameters(1-a,1-ac,Q(199,1000),Q(1),1-Q(293,10**11),
                 1-Q(29,10**10),Q(1,2**31),beta=beta,delta=Q(1,10000),C1=C1)
    chi=p.tau+(1-beta)*max(p.sigma-p.tau,0)
    cs=constraints(p,layout_model='nonadjacent',assembly_model='tight-gaussian')
    cs['packed_overhead']=p.lam-chi
    cs['reserved_axes']=p.lamp-max(0,1-p.c)
    require(all(value>0 for value in cs.values()),'Assembly constraint failed')
    gs=margins(p,layout_model='nonadjacent',assembly_model='tight-gaussian')
    require(min(gs.values())>p.kappa,'No absorption margin')
    require(2<=n['s']<n['m']**5,'Generalized guard branch hypothesis failed')
    B=n['s']+64*(n['W']+n['m']+1)**3
    plan=disjoint_plan(h)
    pair_count=comb(h,2); pair_inputs=h-2; pair_adds=3*pair_inputs-6
    mixer_additions=plan.score()-plan.count+pair_count*2*pair_adds
    copies=plan.left+pair_count*pair_inputs
    injections=plan.right+pair_count*pair_inputs
    scalar_steps=3*n['v']**2*(4*mixer_additions+2*copies+4*injections+18*n['v'])
    E=B-n['s']
    require(4*scalar_steps+8*n['s']+8*n['W']+8*n['m']<E,
            'Guard node charge does not dominate explicit scalar work')
    raw=max(Q(128*n['m']*B*B),18*n['m']*B*B*(1+1/zeta))
    C0=-(-raw.numerator//raw.denominator)
    require(C0>=9*n['m']*B*B*(1+1/zeta)+18,
            'Guard must also cover the reserved-axis and outer charges')
    powers=dict(d=p.epsilon, K=p.epsilon*p.c, ell=1-p.epsilon,
                alpha=(1+p.epsilon)/4, gamma=(1+3*p.epsilon)/2,
                prime_interval_ratio=1-2*p.epsilon, guard=p.epsilon*C1)
    return dict(status='CONDITIONAL 2^-31 WITNESS; INTEGRATED BY make_complex_compression_patch.py',
                parameters=vars(p),complex_saving=ac,internal_exponent=chi,
                constraint_slacks=cs,margins=gs,minimum_margin=min(gs.values()),
                absorption_gap=min(gs.values())-p.kappa,guard_C0=C0,guard_C1=C1,
                scalar_steps_per_network=scalar_steps,guard_node_charge=E,
                derived_powers=powers)


def certificate():
    h=26;n=counts(h);triples,pi=matching(h)
    _,loghi=log_integer_bounds(n['m'])
    require(n['eta']>Q(5,10**9)*loghi,'Simple exponential bound failed')
    proof_files=['notes/complex-compression.tex','notes/compact-control-movement.tex',
                 'notes/compact-control-layout.tex','notes/compact-control-guard.tex']
    return dict(status='CONDITIONAL FINITE COMPLEX NETWORK; WRITTEN TRANSFER PROOF SUPPLIED; PUBLISHED WITNESS UNCHANGED',
                upstream_commit=verify_sources(),counts=n,
                disjoint_partition=verify_disjoint_partition(h),
                intersection_two_circuit=LeaveOneCircuit(h-2).verify(),
                phase_controls=phase_controls(),
                matching=dict(h=h,triples=len(triples),bijective=True,all_binary_dot_products_zero=True,
                              sha256=sha256(json.dumps(pi,separators=(',',':')).encode()).hexdigest()),
                complex_saving_bounds=saving_bounds(n),simple_saving=Q(5,10**9),
                simple_saving_slack=n['eta']-Q(5,10**9)*loghi,
                assembly_control=assembly_control(),
                proof_sha256={name:sha256((ROOT/name).read_bytes()).hexdigest()
                              for name in proof_files},
                scoped_ceiling=dict(upper=BIT_SAVING/5,
                    scope='Retained certified bit exponent and Gaussian assembly constraint; not a ceiling for other bit networks or assembly proofs.'),
                finite_screen={str(h):dict(counts=counts(h),saving_bounds=saving_bounds(counts(h)))
                               for h in range(22,41,2)},
                scope='Exact finite construction and conditional accounting, not independent verification of upstream. The 2^-34 published source patch is unchanged. Finite screen has no all-h optimality claim.')


if __name__=='__main__':
    (ROOT/'certificates/complex-compression.json').write_text(
        json.dumps(serializable(certificate()),indent=2,sort_keys=True)+'\n')
    print('PASS compressed complex network and conditional 2^-31 witness.')
