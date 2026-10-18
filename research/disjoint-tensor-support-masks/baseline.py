"""Cancellation-free tensor contractions for disjoint-subset sums.

The recurrence counts arithmetic DAG nodes, not rectangle memberships.
Expanded DAGs intern equal supports and are checked coefficient by coefficient.
"""
from functools import cache
from itertools import combinations
from math import comb
from hashlib import sha256
import json

from certify import require
from exclusion_circuit import ExclusionCircuit
from binary_phase_frames import nullspace, certify_chain


@cache
def plan(n, a, b):
    require(0 <= a <= n and 0 <= b <= n, 'Invalid subset sizes')
    if a+b > n: return (0, 'empty')
    if not a: return (0, 'copy')
    if not b: return (comb(n, a)-1, 'sum')
    best = (comb(n, b)*(comb(n-b, a)-1), 'rows')
    for left in range(1, n//2+1):
        right = n-left; total = 0
        for j in range(max(0, b-right), min(left, b)+1):
            parts = 0
            for i in range(max(0, a-right), min(left, a)+1):
                if i+j > left or a-i+b-j > right: continue
                A, B = plan(left, i, j)[0], plan(right, a-i, b-j)[0]
                total += min(comb(right, a-i)*A+comb(left, j)*B,
                             comb(left, i)*B+comb(right, b-j)*A)
                parts += 1
            if parts: total += comb(left, j)*comb(right, b-j)*(parts-1)
        if total < best[0]: best = total, left
    return best


@cache
def subsets(points, size):
    return tuple(sum(1 << p for p in S) for S in combinations(points, size))


class DisjointTensor(ExclusionCircuit):
    def __init__(self, h, k=3, maximum_inputs=10000):
        require(type(h) is int and type(k) is int and h >= 2*k and k >= 1,
                'Need a nonempty disjointness relation')
        require(comb(h, k) <= maximum_inputs, 'Expansion budget exceeded')
        self.h, self.k = h, k
        self.inputs = list(subsets(tuple(range(h)), k))
        self.support = [0]+[1 << i for i in range(len(self.inputs))]
        self.args = [None]*len(self.support)
        self.lookup = {s:i for i, s in enumerate(self.support)}
        self.variables = {S:i+1 for i, S in enumerate(self.inputs)}
        self.outputs = self.transform(tuple(range(h)), k, k, self.variables)
        self.active = set(); pending = list(self.outputs.values())
        while pending:
            node = pending.pop()
            if not node or node in self.active: continue
            self.active.add(node)
            if self.args[node]: pending.extend(self.args[node])
        self.additions = sum(self.args[node] is not None for node in self.active)

    def transform(self, points, a, b, values):
        n = len(points); _, method = plan(n, a, b)
        outputs = subsets(points, b)
        if method == 'empty': return {T:0 for T in outputs}
        if method == 'copy': return {T:values[0] for T in outputs}
        if method == 'sum': return {0:self.total(list(values.values()))}
        if method == 'rows':
            return {T:self.total([values[S] for S in subsets(points, a) if not S&T])
                    for T in outputs}
        left, right = points[:method], points[method:]
        l, r = len(left), len(right)
        terms = {T:[] for T in outputs}
        for j in range(max(0, b-r), min(l, b)+1):
            for i in range(max(0, a-r), min(l, a)+1):
                if i+j > l or a-i+b-j > r: continue
                A, B = plan(l, i, j)[0], plan(r, a-i, b-j)[0]
                if comb(r, a-i)*A+comb(l, j)*B <= comb(l, i)*B+comb(r, b-j)*A:
                    middle = {S:self.transform(left, i, j,
                              {R:values[R|S] for R in subsets(left, i)})
                              for S in subsets(right, a-i)}
                    for T in subsets(left, j):
                        row = self.transform(right, a-i, b-j, {S:M[T] for S,M in middle.items()})
                        for U, node in row.items(): terms[T|U].append(node)
                else:
                    middle = {S:self.transform(right, a-i, b-j,
                              {R:values[R|S] for R in subsets(right, a-i)})
                              for S in subsets(left, i)}
                    for T in subsets(right, b-j):
                        row = self.transform(left, i, j, {S:M[T] for S,M in middle.items()})
                        for U, node in row.items(): terms[T|U].append(node)
        return {T:self.total(nodes) for T,nodes in terms.items()}

    def verify(self):
        for node in sorted(self.active):
            if self.args[node]:
                a, b = self.args[node]
                require(a < node and b < node and not self.support[a]&self.support[b],
                        'An addition uses cancellation or is not acyclic')
                require(self.support[node] == self.support[a]|self.support[b], 'Wrong sum')
        for T, node in self.outputs.items():
            expected = sum(1 << i for i, S in enumerate(self.inputs) if not S&T)
            require(self.support[node] == expected, 'Wrong integer output coefficient')
        require(self.additions <= plan(self.h,self.k,self.k)[0], 'Interning exceeded recurrence')
        code = self.compile(); values = [0]*code['roles']
        for S, slot in code['sources'].items(): values[slot] = self.support[self.variables[S]]
        for node, ins, outs in code['gates']:
            for slot in ins[1:]:
                require(not values[ins[0]]&values[slot], 'Embedding adds overlapping supports')
                values[ins[0]] |= values[slot]
            for slot in outs[1:]:
                require(values[slot] == 0, 'Fanout destination is not fresh')
                values[slot] = values[ins[0]]
        for T, slot in code['outputs'].items():
            require(values[slot] == self.support[self.outputs[T]], 'Wrong embedded output')
        encoded = json.dumps([[i,self.args[i],str(self.support[i])] for i in sorted(self.active)],
                             separators=(',',':')).encode()
        return dict(h=self.h,k=self.k,inputs=len(self.inputs),outputs=len(self.outputs),
                    additions=self.additions,unshared_recurrence_additions=plan(self.h,self.k,self.k)[0],
                    roles=code['roles'],integer_coefficient_map_verified=True,
                    disjoint_additions_verified=True,embedding_verified=True,
                    coefficients=len(self.inputs)*comb(self.h-self.k,self.k),
                    dag_sha256=sha256(encoded).hexdigest())

    def frame_data(self):
        """Ancestor/reachable-target families and their ground-point unions."""
        descendants = {node:0 for node in self.active}
        targets = sorted(self.outputs)
        for i,T in enumerate(targets): descendants[self.outputs[T]] |= 1 << i
        for node in sorted(self.active, reverse=True):
            if self.args[node]:
                for parent in self.args[node]: descendants[parent] |= descendants[node]
        source_union = {}
        target_union = {}
        for node in sorted(self.active):
            if self.args[node]:
                a,b = self.args[node]; source_union[node] = source_union[a]|source_union[b]
            else: source_union[node] = self.inputs[node-1]
            bits = descendants[node]; union = 0
            while bits:
                bit = bits&-bits; bits ^= bit; union |= targets[bit.bit_length()-1]
            target_union[node] = union
            require(union and not union&source_union[node], 'Node is not a disjoint rectangle')
        return descendants, source_union, target_union

    def verify_frames(self, exact_bases=False):
        """Every physical transition, both orientations, including idle endpoints.

        General acceptance uses the proved three-case enclosure lemma. Optional
        exact mode constructs every distinct local residual's binary basis.
        """
        require(self.k == 3 and self.h > 6, 'The phase lemma here is for triples')
        descendants, source_union, target_union = self.frame_data()
        code = self.compile(); h = self.h; full = ('coordinate',(1 << h)-1)
        empty = ('coordinate',0); checked = set(); types = {}
        def space(frame):
            kind, mask = frame
            if kind == 'line': return (mask,)
            if kind == 'complement': return nullspace((mask,),h)
            return tuple(1 << i for i in range(h) if mask >> i & 1)
        def transition(lower, upper):
            if lower == upper: return
            pair = lower, upper
            if pair in checked: return
            a,A = lower; b,B = upper
            if a == 'coordinate' and b == 'coordinate': require(A&~B == 0,'Not nested coordinates')
            elif a == 'line' and b == 'coordinate': require(A&~B == 0 and B&~A,'Missing residual unit')
            elif a == 'coordinate' and b == 'line': require(A == 0,'Invalid line entry')
            elif a == 'coordinate' and b == 'complement':
                require(not A&B and ((1 << h)-1)&~(A|B),'Missing complement residual unit')
            elif a == 'line' and b == 'complement':
                require(not A&B and ((1 << h)-1)&~(A|B),'Missing two-line residual unit')
            elif a == 'complement' and b == 'coordinate': require(B == (1 << h)-1,'Invalid complement exit')
            else: require(False,'Unsupported phase transition')
            if exact_bases: certify_chain((space(lower),space(upper)))
            checked.add(pair)
        for reverse in (False,True):
            labels = {}
            for node in sorted(self.active):
                ns,nt = self.support[node].bit_count(),descendants[node].bit_count()
                A,B = source_union[node],target_union[node]
                if reverse: ns,nt,A,B = nt,ns,B,A
                label = ('line',A) if ns == 1 else ('complement',B) if nt == 1 else ('coordinate',A)
                labels[node] = label; types[label[0]] = types.get(label[0],0)+1
            physical = [empty]*code['roles']
            inputs = code['outputs'] if reverse else code['sources']
            outputs = code['sources'] if reverse else code['outputs']
            for S,slot in inputs.items():
                physical[slot] = ('line',S); transition(empty,physical[slot])
            gates = reversed(code['gates']) if reverse else code['gates']
            for node,ins,outs in gates:
                label = labels[node]
                for slot in set(ins+outs): transition(physical[slot],label); physical[slot] = label
            for T,slot in outputs.items():
                target = ('complement',T); transition(physical[slot],target); physical[slot] = target
            for old in physical: transition(old,full)
        return dict(h=h,orientations=2,all_physical_transitions_checked=True,
                    distinct_nontrivial_transitions=len(checked),frame_types=types,
                    exact_residual_bases_constructed=exact_bases)


def complex_counts(h, disjoint_roles):
    from fractions import Fraction as Q
    require(h >= 8 and h%2 == 0 and disjoint_roles >= 0, 'Invalid complex ledger')
    n = comb(h,3); N = n**3; m = h**3
    pair_roles = comb(h,2)*(4*(h-2)-6)
    side = disjoint_roles+pair_roles; centers = h+1
    W = 2*N+2*n*n*(side+centers); L = 3*n*n*h*centers
    delta = 2*N-2*L
    return dict(h=h,v=n,N=N,m=m,disjoint_roles=disjoint_roles,
                intersection_two_roles=pair_roles,side_roles=side,central_roles=centers,
                W=W,L=L,s=W*m-delta,deficit=delta,eta=Q(delta,W*m))


def scalar_program(circuit):
    """Reuse the signed invocation interface with the new +1/2 side DAG."""
    from fractions import Fraction as Q
    from complex_compression import LeaveOneCircuit
    h = circuit.h
    require(circuit.k == 3 and h >= 8 and h%2 == 0, 'Complex triple interface requires even h')
    triples = list(combinations(range(h),3))
    index = {sum(1 << x for x in T):i for i,T in enumerate(triples)}
    code = circuit.compile()
    gates = [(ins,outs) for _,ins,outs in code['gates']]
    sources = [(index[T],slot) for T,slot in code['sources'].items()]
    outputs = [(index[T],slot,Q(1,2)) for T,slot in code['outputs'].items()]
    offset = code['roles']; pair_code = LeaveOneCircuit(h-2).compile()
    for pair in combinations(range(h),2):
        rest = [i for i in range(h) if i not in pair]
        def target(i): return index[sum(1 << x for x in (*pair,rest[i]))]
        for _,ins,outs in pair_code['gates']:
            gates.append((tuple(offset+i for i in ins),tuple(offset+i for i in outs)))
        sources.extend((target(i),offset+slot) for i,slot in pair_code['sources'].items())
        outputs.extend((target(i),offset+slot,Q(-1,2)) for i,slot in pair_code['outputs'].items())
        offset += pair_code['roles']
    require(offset == complex_counts(h,code['roles'])['side_roles'], 'Wrong scalar role ledger')
    return dict(h=h,triples=triples,gates=gates,sources=sources,outputs=outputs,roles=offset)
