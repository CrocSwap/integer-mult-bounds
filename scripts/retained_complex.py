#!/usr/bin/env python3
"""Exact shared side circuit for the complex motif, with binary frame labels.

Disjoint triples use coordinate-completed source trees with a spare coordinate.
Intersection-two triples use orthonormal fixed-pair trees. This module supplies
finite certificates; the general phase/tape transfer is a separate written proof.
"""
from dataclasses import dataclass, replace
from functools import lru_cache
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import json
from hashlib import sha256
from itertools import combinations
from struct import pack

from certify import require, constraints, margins, verify_sources
from compact_control_layer import parameters as baseline_parameters, layer_exponents
from prepare_layers import serializable
from search_network import log_integer_bounds
from exclusion_circuit import ExclusionCircuit


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


@dataclass(frozen=True)
class Plan:
    n: int
    a: int
    b: int
    count: int
    left: int
    right: int
    kind: str
    split: int = 0
    terms: tuple = ()

    @property
    def score(self):
        return self.left + self.right - self.count


@lru_cache(None)
def best_plan(n, a, b):
    """Restricted recursive rectangle search for D(a,b).

    The search is deliberately the same row/column/split family as the
    incidence compiler, generalized only to a,b<=3.  It is a construction,
    not a lower bound over all biclique partitions.
    """
    if a < 0 or b < 0 or a + b > n:
        return Plan(n, a, b, 0, 0, 0, "empty")
    if a == 0 or b == 0:
        return Plan(n, a, b, 1, comb(n, a), comb(n, b), "base")

    def stars(kind):
        if kind == "rows":
            c = comb(n, a)
            return Plan(n, a, b, c, c, c * comb(n - a, b), "rows")
        c = comb(n, b)
        return Plan(n, a, b, c, c * comb(n - b, a), c, "cols")

    winner = min((stars("rows"), stars("cols")), key=lambda p: p.score)
    for split in range(1, n):
        right_n = n - split
        terms = []
        for x in range(a + 1):
            for y in range(b + 1):
                if x + y > split or (a - x) + (b - y) > right_n:
                    continue
                left = best_plan(split, x, y)
                right = best_plan(right_n, a - x, b - y)
                if left.count and right.count:
                    terms.append((left, right))
        if not terms:
            continue
        candidate = Plan(
            n, a, b,
            sum(left.count * right.count for left, right in terms),
            sum(left.left * right.left for left, right in terms),
            sum(left.right * right.right for left, right in terms),
            "split", split, tuple(terms),
        )
        if candidate.score < winner.score:
            winner = candidate
    return winner


def rectangle_stream(plan, points=None):
    if points is None:
        points = tuple(range(plan.n))
    if plan.kind == "empty":
        return
    if plan.kind == "base":
        yield tuple(combinations(points, plan.a)), tuple(combinations(points, plan.b))
    elif plan.kind == "rows":
        for source in combinations(points, plan.a):
            rest = tuple(i for i in points if i not in source)
            yield (source,), tuple(combinations(rest, plan.b))
    elif plan.kind == "cols":
        for target in combinations(points, plan.b):
            rest = tuple(i for i in points if i not in target)
            yield tuple(combinations(rest, plan.a)), (target,)
    else:
        left_points, right_points = points[:plan.split], points[plan.split:]
        for left, right in plan.terms:
            for source_l, target_l in rectangle_stream(left, left_points):
                for source_r, target_r in rectangle_stream(right, right_points):
                    yield (tuple(x + y for x in source_l for y in source_r),
                           tuple(x + y for x in target_l for y in target_r))



def triple_mask(triple):
    return sum(1 << i for i in triple)


def repaired_rectangles(plan, points):
    """Split only frame-bad rectangles; singleton-target repairs preserve cost."""
    full = (1 << plan.n) - 1
    raw = list(rectangle_stream(plan, points))
    repaired = []
    bad = []
    for source, target in raw:
        source_union = 0
        for s in source:
            source_union |= triple_mask(s)
        source_dim = source_union.bit_count()
        frame_bad = any(
            source_dim < plan.n - 1
            and not ((full ^ triple_mask(t)) & ~source_union)
            for t in target
        )
        if not frame_bad:
            repaired.append((source, target))
            continue
        bad.append((len(source), len(target), source_dim))
        # Every bad rectangle in the observed plans has one target.  The
        # generic fallback splits both sides into singleton edge rectangles;
        # this remains exact if a future plan has a wider bad target family.
        for s in source:
            for t in target:
                repaired.append(((s,), (t,)))
    return raw, repaired, bad



class RetainedComplexCircuit:
    def __init__(self, h=24):
        require(h >= 8 and h % 2 == 0, 'Use an even ground size at least eight')
        self.h = h
        self.full = (1 << h) - 1
        self.inputs = list(combinations(range(h), 3))
        self.variables = {t: i + 1 for i, t in enumerate(self.inputs)}
        self.masks = [sum(1 << i for i in t) for t in self.inputs]
        self.args = [None] * (len(self.inputs) + 1)
        self.union = [0] + self.masks[:]
        self.labels = [('zero', 0)] + [('line', m) for m in self.masks]
        self.outputs = {}
        self.targets = []

        groups = []
        for a in range(h - 2):
            rows = []
            for b in range(a + 1, h - 1):
                leaves = [self.variables[a, b, c] for c in range(b + 1, h)]
                rows.append(self.tree(leaves))
            groups.append(self.tree(rows))
        root = self.tree(groups)
        self.disjoint_end = len(self.args)

        self.pair_ranges = []
        for pair in combinations(range(h), 2):
            mask = sum(1 << i for i in pair)
            leaves = [self.variables[tuple(sorted((*pair, k)))]
                      for k in range(h) if not mask & (1 << k)]
            start = len(self.args)
            root = self.tree(leaves, mask)
            self.pair_ranges.append((start, len(self.args)))
            for k in range(h):
                if not mask & (1 << k):
                    self.select(root, mask | (1 << k), True)

        # Rectangle source sums replace only the disjoint side branch.
        _, rectangles, _ = repaired_rectangles(best_plan(h,3,3),tuple(range(h)))
        self.rectangle_counts = (len(rectangles),sum(len(a) for a,b in rectangles),
                                 sum(len(b) for a,b in rectangles))
        for source,target in rectangles:
            node = self.tree([self.variables[t] for t in source])
            for t in target:
                output = len(self.targets)
                self.outputs[output] = node
                self.targets.append((triple_mask(t),1))

        # Retain all pair roots, doubled point totals, and the global total.
        roots = {tuple(i for i in range(h) if self.labels[end-1][1] & (1 << i)): end-1
                 for _, end in self.pair_ranges}
        self.total_outputs = []
        for i in range(h-1):
            nodes = [roots[tuple(sorted((i,j)))] for j in range(h) if j != i]
            node = self.point_tree(nodes, i)
            output = len(self.outputs)
            self.outputs[output] = node
            self.total_outputs.append(output)
        output = len(self.outputs)
        self.outputs[output] = self.disjoint_end-1
        self.total_outputs.append(output)

        self.active = set()
        stack = list(self.outputs.values())
        while stack:
            node = stack.pop()
            if node in self.active:
                continue
            self.active.add(node)
            if self.args[node]:
                stack.extend(self.args[node])
        self.additions = sum(self.args[n] is not None for n in self.active)
        self.roles = self.additions + len(self.outputs)

    def point_tree(self, nodes, point):
        if len(nodes) == 1:
            return nodes[0]
        mid = len(nodes)//2
        a = self.point_tree(nodes[:mid], point)
        b = self.point_tree(nodes[mid:], point)
        node = len(self.args)
        self.args.append((a,b))
        self.union.append(self.full)
        self.labels.append(('point',point))
        return node

    def tree(self, nodes, pair=0):
        if len(nodes) == 1:
            return nodes[0]
        mid = len(nodes) // 2
        a, b = self.tree(nodes[:mid], pair), self.tree(nodes[mid:], pair)
        node = len(self.args)
        union = self.union[a] | self.union[b]
        self.args.append((a, b))
        self.union.append(union)
        self.labels.append(('star', pair, union & ~pair) if pair else ('coordinate', union))
        return node

    def select(self, node, target, star):
        union = self.union[node]
        if star:
            accepted = ((union & target).bit_count() == 2 if self.args[node] is None
                        else not (self.labels[node][2] & target))
        else:
            accepted = not union & target and union != self.full ^ target
        if accepted:
            index = len(self.targets)
            self.outputs[index] = node
            self.targets.append((target, -1 if star else 1))
        elif self.args[node]:
            for child in self.args[node]:
                self.select(child, target, star)

    def basis(self, label):
        kind = label[0]
        if kind == 'point':
            return [self.full ^ (1 << j) for j in range(self.h) if j != label[1]]
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
        if kind == 'point':
            return dot(vector,self.full ^ (1 << label[1])) == 0
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
        if label[0] == 'point':
            return 1 << label[1]
        if label[0] != 'star':
            return label[1]
        _, pair, variables = label
        return variables ^ (pair if variables.bit_count() & 1 else 0)

    def dimension(self, label):
        if label[0] == 'point':
            return self.h-1
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
            if self.labels[node][0] != 'point':
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
        # Integer ancestry expansion verifies multiplicity two in D_i.
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
            expected = {j:1 if i == self.h-1 else 2
                        for j,t in enumerate(self.masks)
                        if i == self.h-1 or t & (1 << i)}
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
SAVING = Q(750,10**11)
KAPPA = Q(591,10**12)
LOG_UPPER = Q(477,50)


def counts(c):
    h,v = c.h,len(c.inputs)
    # Independent rectangle and fixed-pair counts.
    nr, left, right = c.rectangle_counts
    n = h-2
    q2 = sum(n*(n-1)-sum(n-(c.union[j].bit_count()-2) for j in range(a,b))
             for a,b in c.pair_ranges)
    additions = v-1+comb(h,2)*(h-3)+(h-1)*(h-2)+left-nr
    require((c.additions,len(c.targets),len(c.outputs)) ==
            (additions,right+q2,right+q2+h), 'Independent counts disagree')
    m,N = h**3,v**3
    W = 2*N+2*v*v*c.roles
    loss = 3*v*v*((h-1)**2+h)
    D = 2*N-2*loss
    return dict(h=h,v=v,m=m,N=N,additions=additions,side_outputs=right+q2,
                retained_totals=h,roles=c.roles,W=W,L=loss,D=D,s=W*m-D,
                eta=Q(D,W*m))


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
    gates = 3*n['v']**2*(8*n['v']+4*n['additions']+4)
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
    require(n['roles'] == 365760 and n['D'] == 2990500480, 'Unexpected compiled deficit')
    require(main['minimum_margin'] == Q(2956521,5*10**15), 'Unexpected final margin')
    require(main['absorption_gap'] == Q(1521,5*10**15), 'Unexpected absorption gap')
    require(KAPPA > Q(1,2**31), 'Wrong dyadic corollary')
    files = ['scripts/retained_complex.py','scripts/make_retained_complex_patch.py',
             'notes/retained-complex-construction.tex','notes/compact-control-movement.tex',
             'notes/compact-control-layout.tex','notes/compact-control-guard.tex']
    return dict(status='CONDITIONAL RETAINED-TOTAL COMPLEX WITNESS; NOT FULL FORMAL VERIFICATION',
                upstream_commit=verify_sources(),main=main,producer=producer,frames=frames,
                kappa=KAPPA,ratio_over_compact_witness=KAPPA/Q(83,10**12),
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
