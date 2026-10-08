#!/usr/bin/env python3
"""Combine eumemic's shared-exclusion circuit with retained-total phase frames.

The base builder is copied from PR #3 at dfe5b818aad4d386cb5dd7d76df108088107765d
(eumemic, Claude-assisted). Retained exclusion totals and stage sharing
are the PR #4 contribution. This module supplies
finite certificates; the general phase/tape transfer is a separate written proof.
"""
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path
import json
from hashlib import sha256
from struct import pack

from certify import require, constraints, margins, verify_sources
from compact_control_layer import parameters as baseline_parameters, layer_exponents
from prepare_layers import serializable
from search_network import log_integer_bounds
from exclusion_circuit import ExclusionCircuit
from complex_circuit import ComplexSideCircuit, EMPTY


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def dot(a, b):
    return (a & b).bit_count() & 1


class RetainedComplexCircuit:
    def __init__(self, h=24):
        require(h >= 8 and h % 2 == 0, 'Use an even ground size at least eight')
        self.h, self.full = h, (1 << h)-1
        source = ComplexSideCircuit(h)
        self.base_additions = source.additions
        self.base_outputs = len(source.pieces)
        self.base_active = set(source.active)
        # Reuse PR #3's cached exclusion sums and full pair-star roots.
        retained = source.tri(list(range(h)),1)
        self.inputs = source.triples
        self.variables = dict(source.input)
        self.masks = [sum(1 << i for i in t) for t in self.inputs]
        self.args = list(source.args)
        self.union = [0]+self.masks[:]
        cores = [0]+self.masks[:]
        self.labels = [('zero',0)]+[('line',m) for m in self.masks]
        for node in range(len(self.inputs)+1,len(self.args)):
            a,b = self.args[node]
            union, core = self.union[a] | self.union[b], cores[a] & cores[b]
            self.union.append(union); cores.append(core)
            if source.kind[node] == 'd0':
                self.labels.append(('coordinate',union))
            else:
                require(core.bit_count() == 2,'Pair-star node lost its common pair')
                self.labels.append(('star',core,union & ~core))
        self.outputs = {i:node for i,(_,node,_) in enumerate(source.pieces)}
        self.targets = [(sum(1 << i for i in t),int(2*coef))
                        for t,_,coef in source.pieces]
        self.total_outputs = []
        roots = [retained[frozenset([i])] for i in range(h-1)]+[retained[EMPTY]]
        for node in roots:
            output = len(self.outputs)
            self.outputs[output] = node; self.total_outputs.append(output)
        self.active = set(); stack = list(self.outputs.values())
        while stack:
            node = stack.pop()
            if node in self.active: continue
            self.active.add(node)
            if self.args[node]: stack.extend(self.args[node])
        self.additions = sum(self.args[n] is not None for n in self.active)
        self.roles = self.additions+len(self.outputs)
        self.new_ancestors = sum(self.args[n] is not None
                                 for n in self.active-self.base_active)

    def basis(self, label):
        kind = label[0]
        if kind == 'zero':
            return []
        if kind == 'line':
            return [label[1]]
        if kind == 'coordinate':
            return [1 << i for i in range(self.h) if label[1] & (1 << i)]
        _, pair, variables = label
        return [pair | (1 << i) for i in range(self.h) if variables & (1 << i)]

    def contains(self, label, vector):
        kind = label[0]
        if kind == 'zero':
            return vector == 0
        if kind == 'line':
            return vector in (0, label[1])
        if kind == 'coordinate':
            return not vector & ~label[1]
        _, pair, variables = label
        if vector & ~(pair | variables) or vector & pair not in (0, pair):
            return False
        return bool(vector & pair) == bool((vector & variables).bit_count() & 1)

    def characteristic(self, label):
        if label[0] != 'star':
            return label[1]
        _, pair, variables = label
        return variables ^ (pair if variables.bit_count() & 1 else 0)

    def dimension(self, label):
        if label[0] == 'line':
            return 1
        return label[-1].bit_count()

    def check_inclusion(self, low, high):
        require(all(self.contains(high, x) for x in self.basis(low)), 'Frame inclusion failed')
        delta = self.dimension(high) - self.dimension(low)
        require(delta >= 0, 'Negative residual dimension')
        if delta:
            require(not self.contains(low, self.characteristic(high)), 'Alternating residual')
        return delta

    compile = ExclusionCircuit.compile

    def verify(self):
        supports = [0] + [1 << i for i in range(len(self.inputs))]
        for node in range(len(self.inputs) + 1, len(self.args)):
            a, b = self.args[node]
            require(not supports[a] & supports[b], 'Scalar cancellation in a tree node')
            supports.append(supports[a] | supports[b])
        by_target = {s: [0, 0] for s in self.masks}
        digest = sha256()
        for node in sorted(self.active):
            digest.update(repr((node, self.args[node], self.labels[node])).encode() + b'\n')
            label = self.labels[node]
            basis = self.basis(label)
            require(all(dot(a, b) == int(i == j)
                        for i, a in enumerate(basis) for j, b in enumerate(basis)),
                    'Node label lacks the advertised orthonormal basis')
            require(len(basis) == self.h or not self.contains(label,self.full),
                    'Alternating retirement residual')
            if self.args[node]:
                for child in self.args[node]:
                    self.check_inclusion(self.labels[child], label)
        residuals = 0
        for index, (target, sign) in enumerate(self.targets):
            node = self.outputs[index]
            part = 0 if sign == 1 else 1
            require(not by_target[target][part] & supports[node], 'Repeated output coefficient')
            by_target[target][part] |= supports[node]
            label = self.labels[node]
            require(all(not dot(target, x) for x in self.basis(label)), 'Output is not target-orthogonal')
            # Characteristic of t_target-perp is full+target. A nonzero
            # residual is nonalternating iff this characteristic is outside U.
            delta = self.h - 1 - self.dimension(label)
            require(delta >= 0, 'Output frame too large')
            if delta:
                require(not self.contains(label, self.full ^ target), 'Alternating output residual')
            residuals += 1
            digest.update(pack('<IIb', target, node, sign))
        for target, actual in by_target.items():
            expected = [0, 0]
            for i, source in enumerate(self.masks):
                intersection = (target & source).bit_count()
                if intersection in (0, 2):
                    expected[intersection // 2] |= 1 << i
            require(actual == expected, 'Full complex side coefficient map failed')
        # Integer ancestry expansion verifies the retained exclusion totals.
        cache = {}
        def expand(node):
            if node not in cache:
                if self.args[node] is None:
                    cache[node] = {node-1:1}
                else:
                    a,b = self.args[node]
                    row = dict(expand(a))
                    for key,value in expand(b).items():
                        row[key] = row.get(key,0)+value
                    cache[node] = row
            return cache[node]
        for i,output in enumerate(self.total_outputs):
            expected = {j:1 for j,t in enumerate(self.masks)
                        if i == self.h-1 or not t & (1 << i)}
            require(expand(self.outputs[output]) == expected, 'Wrong retained total multiplicity')
        return dict(h=self.h,inputs=len(self.inputs),additions=self.additions,
                    partial_outputs=len(self.targets),roles=self.roles,
                    zero_output_uses=sum(s == 1 for _, s in self.targets),
                    two_output_uses=sum(s == -1 for _, s in self.targets),
                    full_coefficient_map_exact=True,all_residuals_nonalt=True,
                    activation_and_retirement_checked=True,
                    retained_totals=len(self.total_outputs), exact_total_multiplicities=True,
                    output_residual_checks=residuals,circuit_sha256=digest.hexdigest())

    def verify_role_frames(self, code=None):
        code = code or self.compile()
        current = [('zero', 0)] * code['roles']
        for triple, slot in code['sources'].items():
            current[slot] = ('line', sum(1 << i for i in triple))
        for node, ins, outs in code['gates']:
            label = self.labels[node]
            for slot in set(ins + outs):
                self.check_inclusion(current[slot], label)
                current[slot] = label
        for index, slot in code['outputs'].items():
            require(current[slot] == self.labels[self.outputs[index]], 'Wrong output role label')
        # Store the uncomplemented labels; inclusion reverses when both
        # labels are complemented, and the orthogonal difference is identical.
        reverse = [('zero', 0)] * code['roles']
        for index, slot in code['outputs'].items():
            reverse[slot] = self.labels[self.outputs[index]]
        for node, ins, outs in reversed(code['gates']):
            label = self.labels[node]
            for slot in set(ins + outs):
                if reverse[slot][0] != 'zero':
                    self.check_inclusion(label, reverse[slot])
                reverse[slot] = label
        for triple, slot in code['sources'].items():
            require(reverse[slot] == ('line', sum(1 << i for i in triple)), 'Wrong reverse source label')
        return dict(roles=code['roles'],both_physical_frame_directions=True,
                    pivot_and_fanout_roles_distinct=True)

ROOT = Path(__file__).resolve().parents[1]
H = 24
SAVING = Q(2970,10**11)
KAPPA = Q(591,10**12)
LOG_UPPER = Q(477,50)


def counts(c):
    h,v = c.h,len(c.inputs)
    additions = c.base_additions+c.new_ancestors
    require((c.additions,len(c.targets),len(c.outputs)) ==
            (additions,c.base_outputs,c.base_outputs+h), 'Independent counts disagree')
    m,N = h**3,v**3
    W = 2*N+2*v*v*c.roles
    loss = 3*v*v*((h-1)**2+h)
    D = 2*N-2*loss
    return dict(h=h,v=v,m=m,N=N,additions=additions,side_outputs=c.base_outputs,base_additions=c.base_additions,
                new_ancestors=c.new_ancestors,
                retained_totals=h,roles=c.roles,W=W,L=loss,D=D,s=W*m-D,
                eta=Q(D,W*m))


def scatter_weights(c,mask,step):
    """A normalized grouped pass: every coefficient has magnitude <=1.

    E_i=sum_{T not containing i} x_T, for i<h-1; the last slot is C_*.
    The h-5 passes commute. Later passes touch only C_* and last-point targets.
    """
    require(0 <= step < c.h-5,'Invalid scatter pass')
    last = bool(mask & (1 << (c.h-1)))
    if step:
        return {c.h-1:Q(-1,2)} if last else {}
    row = {c.h-1:Q(-1,2) if last else Q(1)}
    for i in range(c.h-1):
        if last and not mask & (1 << i): row[i] = Q(1,2)
        elif not last and mask & (1 << i): row[i] = Q(-1,2)
    return row


def parameters():
    return replace(baseline_parameters(),sigma=1-SAVING,c=Q(1),
                   lam=1-Q(2959,10**12),lamp=1-Q(2958,10**12),kappa=KAPPA)


def check(p,n,zeta=Q(1,10000)):
    require(0 < 1-p.tau <= 1-baseline_parameters().tau, 'Unsupported bit saving')
    lo,hi = log_integer_bounds(n['m'])
    require(0 < 1-p.sigma and n['eta'] > (1-p.sigma)*LOG_UPPER and hi < LOG_UPPER,
            'Unsupported complex recurrence saving')
    require(0 < p.beta < 1 and zeta > 0, 'Invalid stopping parameters')
    m,W,s = n['m'],n['W'],n['s']
    E = 64*(W+m+1)**3
    B = s+E
    require(m >= 3 and 2 <= s < m**5, 'Stopped-depth branching premise failed')
    gates = 3*n['v']**2*(8*n['v']+4*n['additions']+4+2*(n['h']-6))
    require(gates < 12*W, 'Scalar gate-count premise failed')
    require(36*W**3+4*s+4*W+4 < E, 'Quarter-coefficient depth premise failed')
    require(s*(8+E) <= 9*B*B, 'One-piece depth premise failed')
    C0 = max(Q(128*m*B*B),18*m*B*B*(1+1/zeta))
    C0 = -(-C0.numerator//C0.denominator)
    require(9*m*B*B*(1+1/zeta)+18 <= C0, 'Whole-layer depth premise failed')
    require(p.C1 == 5-4*p.beta+zeta, 'Guard exponent mismatch')
    exponents = layer_exponents(p.tau,p.sigma,p.beta,p.c)
    slacks = constraints(p,layout_model='nonadjacent',assembly_model='tight-gaussian')
    slacks['packed_overhead'] = p.lam-exponents['internal']
    slacks['reserved_axes'] = p.lamp-exponents['preprocessing']
    for name,slack in slacks.items():
        require(slack > 0, 'Retained complex constraint: '+name)
    gs = margins(p,layout_model='nonadjacent',assembly_model='tight-gaussian')
    require(min(gs.values()) > p.kappa, 'No strict absorption gap')
    return dict(parameters=vars(p),counts=n,log_interval=[lo,hi],log_upper=LOG_UPPER,
                deficit_slack=n['eta']-(1-p.sigma)*LOG_UPPER,
                guard=dict(E=E,B=B,C0=C0,C1=p.C1,zeta=zeta,scalar_gates=gates),
                exponents=exponents,constraint_slacks=slacks,margins=gs,
                minimum_margin=min(gs.values()),absorption_gap=min(gs.values())-p.kappa)


def certificate():
    c = RetainedComplexCircuit(H)
    producer = c.verify()
    frames = c.verify_role_frames()
    n = counts(c)
    main = check(parameters(),n)
    require(n['roles'] == 90950 and n['D'] == 2990500480, 'Unexpected compiled deficit')
    require(main['minimum_margin'] == Q(2956521,5*10**15), 'Unexpected final margin')
    require(main['absorption_gap'] == Q(1521,5*10**15), 'Unexpected absorption gap')
    require(KAPPA > Q(1,2**31), 'Wrong dyadic corollary')
    files = ['scripts/complex_circuit.py','scripts/retained_complex.py','scripts/make_retained_complex_patch.py',
             'docs/research/shared-retained-complex.md','notes/retained-complex-construction.tex',
             'notes/compact-control-movement.tex',
             'notes/compact-control-layout.tex','notes/compact-control-guard.tex']
    return dict(status='CONDITIONAL RETAINED-TOTAL COMPLEX WITNESS; NOT FULL FORMAL VERIFICATION',
                upstream_commit=verify_sources(),main=main,producer=producer,frames=frames,
                kappa=KAPPA,ratio_over_compact_witness=KAPPA/Q(83,10**12),
                imported_builder=dict(pr='https://github.com/CrocSwap/integer-mult-bounds/pull/3',
                    author='eumemic',commit='dfe5b818aad4d386cb5dd7d76df108088107765d'),
                proof_sha256={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in files},
                scope='Full h24 scalar coefficients, total multiplicities and compiled frame inclusions; '
                      'small dirty-scratch and projector/phase controls in tests. The general tensor '
                      'phase, fixed-tape, compact-control and analytic transfer use the written proof '
                      'and retained upstream interfaces. This is not a runtime measurement.')


if __name__ == '__main__':
    result = certificate()
    (ROOT/'certificates/retained-complex-layer.json').write_text(
        json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS conditional retained complex:',KAPPA,'> 2^-31; gap',result['main']['absorption_gap'])
