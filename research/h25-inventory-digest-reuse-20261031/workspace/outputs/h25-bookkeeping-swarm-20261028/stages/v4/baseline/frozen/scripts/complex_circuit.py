#!/usr/bin/env python3
"""Compressed side correction for the complex network, with binary frames.

Target S must receive (1/2) * sum{x_T : T disjoint from S}
minus (1/2) * sum{x_T : |S cap T| = 2}. Both sums are computed by
cancellation-free addition graphs and injected as pieces with those weights.

Labels are subspaces of F2^h with the dot product. A disjoint-sum node carries
the coordinate space of its covered points; a pair-star node carries the span
of its triple indicators, which is orthonormal. An injected piece must leave a
point outside S uncovered: the residual up to t_S^perp then contains an odd
coordinate vector. A disjoint piece covering every point outside S would have
the alternating residual <e_a+e_b, e_b+e_c>, so the disjoint sum is split.
"""
from fractions import Fraction as Q
from itertools import combinations

EMPTY = frozenset()


def subsets(points, k):
    return [frozenset(c) for j in range(min(k, len(points))+1)
            for c in combinations(points, j)]


class ComplexSideCircuit:
    def __init__(self, h):
        assert h >= 8, 'Need at least four points outside every target'
        self.h = h
        self.triples = list(combinations(range(h), 3))
        self.index = {t: i for i, t in enumerate(self.triples)}
        self.support = [0]; self.args = [None]; self.kind = [None]
        self.lookup = {}; self.input = {}
        for i, t in enumerate(self.triples):
            self.input[t] = len(self.support)
            self.support.append(1 << i); self.args.append(None); self.kind.append('in')
        self.points = {}  # covered point masks, filled lazily
        self.pieces = []  # (target, node, coefficient)
        self.build_disjoint()
        self.build_pair_stars()
        self.prune()

    # -- node store -------------------------------------------------------
    def x(self, *pts):
        return self.input[tuple(sorted(pts))]

    def add(self, a, b, kind):
        if not a: return b
        if not b: return a
        sa, sb = self.support[a], self.support[b]
        assert not sa & sb, 'Cancellation is forbidden'
        key = (kind, sa | sb)
        node = self.lookup.get(key)
        if node is None:
            node = len(self.support)
            self.lookup[key] = node
            self.support.append(sa | sb); self.args.append((a, b)); self.kind.append(kind)
        return node

    def total(self, nodes, kind):
        nodes = [x for x in nodes if x]
        while len(nodes) > 1:
            nodes = [self.add(nodes[i], nodes[i+1], kind) if i+1 < len(nodes) else nodes[i]
                     for i in range(0, len(nodes), 2)]
        return nodes[0] if nodes else 0

    # -- disjoint sums ----------------------------------------------------
    def vec(self, items, k):
        """{E: sum of item nodes whose points avoid E}, |E| <= k."""
        if not items: return {EMPTY: 0}
        if len(items) == 1:
            p, node = items[0]
            return {EMPTY: node, frozenset([p]): 0} if k else {EMPTY: node}
        half = len(items)//2
        A = self.vec(items[:half], k); B = self.vec(items[half:], k)
        return {ea | eb: self.add(xa, xb, 'd0') for ea, xa in A.items()
                for eb, xb in B.items() if len(ea)+len(eb) <= k}

    def pairs(self, pts, weight, k):
        """{E: sum of weight(u,v) over pairs avoiding E}, |E| <= k."""
        if len(pts) < 2: return {E: 0 for E in subsets(pts, k)}
        half = len(pts)//2; L, R = pts[:half], pts[half:]
        PL = self.pairs(L, weight, k); PR = self.pairs(R, weight, k)
        rows = {u: self.vec([(r, weight(u, r)) for r in R], k) for u in L}
        cross = {}
        for ER in subsets(R, k):
            for EL, node in self.vec([(u, rows[u][ER]) for u in L], k-len(ER)).items():
                cross[EL, ER] = node
        return {EL | ER: self.total([xl, xr, cross[EL, ER]], 'd0')
                for EL, xl in PL.items() for ER, xr in PR.items() if len(EL)+len(ER) <= k}

    def tri_parts(self, pts, k):
        """Recursive halves and the two mixed families, before combination."""
        half = len(pts)//2; L, R = pts[:half], pts[half:]
        TL = self.tri(L, k); TR = self.tri(R, k)
        PR = {r: self.pairs(L, lambda u, v, r=r: self.x(u, v, r), k) for r in R}
        PL = {u: self.pairs(R, lambda a, b, u=u: self.x(u, a, b), k) for u in L}
        return L, R, TL, TR, PR, PL

    def tri(self, pts, k):
        """{E: sum of triples inside pts avoiding E}, |E| <= k."""
        if len(pts) < 3: return {E: 0 for E in subsets(pts, k)}
        L, R, TL, TR, PR, PL = self.tri_parts(pts, k)
        c21 = {}; c12 = {}
        for EL in subsets(L, k):
            for ER, node in self.vec([(r, PR[r][EL]) for r in R], k-len(EL)).items():
                c21[EL, ER] = node
        for ER in subsets(R, k):
            for EL, node in self.vec([(u, PL[u][ER]) for u in L], k-len(ER)).items():
                c12[EL, ER] = node
        return {EL | ER: self.total([xl, xr, c21[EL, ER], c12[EL, ER]], 'd0')
                for EL, xl in TL.items() for ER, xr in TR.items() if len(EL)+len(ER) <= k}

    def build_disjoint(self):
        """Six pieces per target, each leaving an outside point uncovered."""
        pts = list(range(self.h))
        L, R, TL, TR, PR, PL = self.tri_parts(pts, 3)
        R1, R2 = R[:len(R)//2], R[len(R)//2:]
        L1, L2 = L[:len(L)//2], L[len(L)//2:]
        for S in self.triples:
            E = frozenset(S); EL = E & frozenset(L); ER = E & frozenset(R)
            pieces = [TL[EL], TR[ER]]
            for half in (R1, R2):
                pieces.append(self.vec([(r, PR[r][EL]) for r in half], 3-len(EL))[ER & frozenset(half)])
            for half in (L1, L2):
                pieces.append(self.vec([(u, PL[u][ER]) for u in half], 3-len(ER))[EL & frozenset(half)])
            for node in pieces: self.emit(S, node, Q(1, 2))

    # -- pair stars -------------------------------------------------------
    def build_pair_stars(self):
        """Prefix and suffix pair-star sums around each excluded third point."""
        h = self.h
        for a, b in combinations(range(h), 2):
            others = [u for u in range(h) if u not in (a, b)]
            n = len(others)
            pre = [0]
            for u in others: pre.append(self.add(pre[-1], self.x(a, b, u), 'd2'))
            suf = [0]*(n+1)
            for i in range(n-1, -1, -1): suf[i] = self.add(self.x(a, b, others[i]), suf[i+1], 'd2')
            for i, c in enumerate(others):
                S = tuple(sorted((a, b, c)))
                self.emit(S, pre[i], Q(-1, 2)); self.emit(S, suf[i+1], Q(-1, 2))

    def emit(self, S, node, coef):
        """Inject a piece, splitting it until it leaves a point outside S uncovered."""
        if not node: return
        if self.cover(node) | sum(1 << p for p in S) == (1 << self.h)-1:
            a, b = self.args[node]
            self.emit(S, a, coef); self.emit(S, b, coef)
        else:
            self.pieces.append((S, node, coef))

    # -- bookkeeping ------------------------------------------------------
    def prune(self):
        self.active = set(); stack = [node for _, node, _ in self.pieces]
        while stack:
            node = stack.pop()
            if node in self.active: continue
            self.active.add(node)
            if self.args[node]: stack.extend(self.args[node])
        self.additions = sum(self.args[n] is not None for n in self.active)
        self.roles = self.additions + len(self.pieces)

    def cover(self, node):
        """Mask of ground points covered by the node's source triples."""
        if node not in self.points:
            s = self.support[node]; mask = 0
            while s:
                low = s & -s; mask |= sum(1 << p for p in self.triples[low.bit_length()-1]); s ^= low
            self.points[node] = mask
        return self.points[node]

    def stats(self):
        v = len(self.triples)
        return dict(h=self.h, v=v, additions=self.additions, injections=len(self.pieces),
                    roles=self.roles, roles_per_target=round(self.roles/v, 3),
                    disjoint_additions=sum(self.kind[n] == 'd0' for n in self.active),
                    pair_star_additions=sum(self.kind[n] == 'd2' for n in self.active))


# -- binary linear algebra on F2^h, vectors as integer masks ---------------
def echelon(vectors):
    """Reduced basis {pivot bit: vector}; raises on dependence."""
    basis = {}
    for x in vectors:
        for bit, b in basis.items():
            if x & bit: x ^= b
        assert x, 'Dependent label vectors'
        bit = x & -x
        for other in basis:
            if basis[other] & bit: basis[other] ^= x
        basis[bit] = x
    return basis


def reduce(basis, x):
    for bit, b in basis.items():
        if x & bit: x ^= b
    return x


def dot(x, y):
    return (x & y).bit_count() & 1


def rank(rows):
    rows = list(rows); r = 0
    for col in range(max((x.bit_length() for x in rows), default=0)):
        bit = 1 << col
        pivot = next((i for i in range(r, len(rows)) if rows[i] & bit), None)
        if pivot is None: continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        for i in range(len(rows)):
            if i != r and rows[i] & bit: rows[i] ^= rows[r]
        r += 1
    return r


class Label:
    """A binary subspace with a canonical basis."""
    def __init__(self, vectors):
        self.basis = echelon(vectors); self.dim = len(self.basis)
        self.key = tuple(sorted(self.basis.values()))

    def contains(self, other):
        return all(not reduce(self.basis, x) for x in other.basis.values())

    def nondegenerate(self):
        vs = list(self.basis.values())
        return rank([sum(dot(a, b) << j for j, b in enumerate(vs)) for a in vs]) == len(vs)

    def complement_in(self, other):
        """Basis of other ∩ self^perp, assuming self ⊆ other."""
        vs = list(other.basis.values()); us = list(self.basis.values()); k = len(us)
        rows = [sum(dot(v, u) << j for j, u in enumerate(us)) | 1 << (k+i)
                for i, v in enumerate(vs)]
        r = 0
        for col in range(k):
            bit = 1 << col
            piv = next((i for i in range(r, len(rows)) if rows[i] & bit), None)
            if piv is None: continue
            rows[r], rows[piv] = rows[piv], rows[r]
            for i in range(len(rows)):
                if i != r and rows[i] & bit: rows[i] ^= rows[r]
            r += 1
        out = []
        for row in rows[r:]:
            assert not row & ((1 << k)-1)
            x = 0
            for i, v in enumerate(vs):
                if row >> (k+i) & 1: x ^= v
            out.append(x)
        return out


def odd(vectors):
    return any(x.bit_count() & 1 for x in vectors)


# -- exact checks -----------------------------------------------------------
def tmask(t):
    return sum(1 << p for p in t)


class Checks:
    """Exact verification of the side map, labels and compiled roles."""
    def __init__(self, c):
        self.c = c; self.h = c.h; self.cache = {}; self.verdicts = {}
        self.everything = Label([1 << p for p in range(c.h)])

    def label(self, node):
        if node in self.cache: return self.cache[node]
        c = self.c; kind = c.kind[node]
        if kind == 'in':
            vectors = [tmask(c.triples[node-1])]
        elif kind == 'd0':
            m = c.cover(node); vectors = [1 << p for p in range(self.h) if m >> p & 1]
        else:
            s = c.support[node]; ts = []
            while s:
                low = s & -s; ts.append(c.triples[low.bit_length()-1]); s ^= low
            common = set(ts[0]).intersection(*ts)
            assert len(common) >= 2, 'Pair-star node without a common pair'
            vectors = [tmask(t) for t in ts]
        lab = Label(vectors); self.cache[node] = lab
        return lab

    def target_frame(self, S):
        t = tmask(S)
        key = ('perp', S)
        if key not in self.cache:
            self.cache[key] = Label([x for x in (1 << p for p in range(self.h))
                                     if not dot(x, t)] + [tmask((S[0], S[1])), tmask((S[1], S[2]))])
        return self.cache[key]

    def residual_ok(self, small, big):
        """small ⊆ big and big ⊖ small is zero or has an odd vector."""
        key = (small.key, big.key)
        if key not in self.verdicts:
            res = small.complement_in(big) if big.contains(small) else None
            self.verdicts[key] = res is not None and (not res or odd(res))
        return self.verdicts[key]

    def label_ok(self, lab):
        """Nondegenerate, contains an odd vector, and its complement is zero or does."""
        key = ('label', lab.key)
        if key not in self.verdicts:
            perp = lab.complement_in(self.everything)
            self.verdicts[key] = (lab.nondegenerate() and odd(lab.basis.values())
                                  and (not perp or odd(perp)))
        return self.verdicts[key]

    def verify_map(self):
        c = self.c
        for node in c.active:
            if c.args[node]:
                a, b = c.args[node]
                assert a < node and b < node and not c.support[a] & c.support[b]
                assert c.support[node] == c.support[a] | c.support[b]
        got = {}
        for S, node, coef in c.pieces:
            assert coef in (Q(1, 2), Q(-1, 2))
            key = (S, coef)
            assert not got.get(key, 0) & c.support[node], 'Overlapping pieces'
            got[key] = got.get(key, 0) | c.support[node]
        nonzero = 0
        for S in c.triples:
            zero = sum(1 << i for i, T in enumerate(c.triples) if not set(S) & set(T))
            two = sum(1 << i for i, T in enumerate(c.triples) if len(set(S) & set(T)) == 2)
            assert got.get((S, Q(1, 2)), 0) == zero and got.get((S, Q(-1, 2)), 0) == two
            nonzero += zero.bit_count()+two.bit_count()
        return dict(targets=len(c.triples), nonzero_coefficients=nonzero,
                    side_map_exact=True, coefficients='+1/2 disjoint, -1/2 intersection two')

    def verify_labels(self):
        c = self.c; checked = 0
        for node in sorted(c.active):
            lab = self.label(node)
            assert self.label_ok(lab), node  # includes the exit to the full space
            if c.args[node]:
                for child in c.args[node]:
                    assert self.residual_ok(self.label(child), lab), (node, child)
                    checked += 1
        for S, node, coef in c.pieces:
            assert self.residual_ok(self.label(node), self.target_frame(S)), (S, node)
            checked += 1
        return dict(active_nodes=len(c.active), checked_inclusions=checked,
                    all_labels_nondegenerate=True, all_residuals_have_odd_vectors=True)


def compile_roles(c):
    """Reversible roles: one per addition plus one per injected piece."""
    users = {x: [] for x in c.active}
    for node in sorted(c.active):
        if c.args[node]:
            for pos, x in enumerate(c.args[node]): users[x].append(('gate', node, pos))
    for i, (_, node, _) in enumerate(c.pieces): users[node].append(('output', i))
    edge = {}; sources = {}; outputs = {}; gates = []; size = 0
    for node in sorted(c.active):
        if c.args[node]:
            ins = (edge[node, 0], edge[node, 1]); pivot = ins[0]
        else:
            pivot = size; size += 1; ins = (pivot,); sources[c.triples[node-1]] = pivot
        assert users[node]
        outs = (pivot,)+tuple(range(size, size+len(users[node])-1))
        size += len(users[node])-1
        assert len(set(ins)) == len(ins) and set(ins) & set(outs) == {pivot}
        gates.append((node, ins, outs))
        for user, slot in zip(users[node], outs):
            if user[0] == 'gate': edge[user[1], user[2]] = slot
            else: outputs[user[1]] = slot
    assert size == c.roles
    return dict(roles=size, gates=gates, sources=sources, outputs=outputs)


def verify_role_frames(c, checks, code=None):
    """Follow every physical role in both directions through its frames."""
    code = code or compile_roles(c)
    def step(small, big): assert checks.residual_ok(small, big)
    frames = [None]*code['roles']
    for T, slot in code['sources'].items(): frames[slot] = checks.label(c.input[T])
    for node, ins, outs in code['gates']:
        lab = checks.label(node)
        for slot in set(ins+outs):
            if frames[slot] is None: assert checks.label_ok(lab)  # entry from D0
            else: step(frames[slot], lab)
            frames[slot] = lab
    for i, slot in code['outputs'].items():
        S = c.pieces[i][0]; J = checks.target_frame(S)
        step(frames[slot], J); frames[slot] = J
    for lab in frames:
        assert checks.label_ok(lab)  # includes the exit residual to D1
    # Reverse stage: complements, traversed backward. U^perp grows iff U shrinks.
    # Its entries and exits have the forward residuals U^perp and U, checked above.
    back = [None]*code['roles']
    for i, slot in code['outputs'].items(): back[slot] = ('line', c.pieces[i][0])
    for node, ins, outs in reversed(code['gates']):
        lab = checks.label(node)
        for slot in set(ins+outs):
            prev = back[slot]
            if prev is None:
                assert checks.label_ok(lab)  # reverse entry residual is lab^perp
            elif prev[0] == 'line':  # <t_S> ⊆ U^perp  iff  U ⊆ t_S^perp
                step(lab, checks.target_frame(prev[1]))
            else:
                step(lab, prev[1])  # prev^perp ⊆ lab^perp iff lab ⊆ prev
            back[slot] = ('node', lab)
    for T, slot in code['sources'].items():
        assert back[slot][1].key == checks.label(c.input[T]).key  # ends at t_T^perp
    return dict(roles=code['roles'], forward_frames_nested=True,
                reverse_complement_frames_nested=True)


def simulate_invocation(c, code, x, y, side, center, inverse=False):
    """Scalar invocation over Q with arbitrary scratch; returns the new state.

    Forward: L,-J,L^-1,-R,V,G,R,L,J,L^-1,G^-1,V^-1 gives y <- y + x.
    inverse=True runs the inverted schedule, giving x <- x - y.
    """
    h = c.h; T = c.triples
    side = list(side); center = dict(center); x = dict(x); y = dict(y)
    def L(sign=1):
        order = code['gates'] if sign > 0 else list(reversed(code['gates']))
        for node, ins, outs in order:
            if sign > 0:
                if len(ins) == 2: side[ins[0]] += side[ins[1]]
                for o in outs[1:]: side[o] += side[outs[0]]
            else:
                for o in outs[1:]: side[o] -= side[outs[0]]
                if len(ins) == 2: side[ins[0]] -= side[ins[1]]
    def J(target, sign):
        for i, slot in code['outputs'].items():
            S, _, coef = c.pieces[i]; target[S] += sign*coef*side[slot]
    def V(source, sign):
        for t, slot in code['sources'].items(): side[slot] += sign*source[t]
    def G(source, sign):
        for i in range(h): center[i] += sign*sum(source[t] for t in T if i in t)
        center['*'] += sign*sum(source.values())
    def R(target, sign):
        for t in T: target[t] += sign*(sum(center[i] for i in t)-center['*'])/2
    if not inverse:
        L(); J(y, -1); L(-1); R(y, -1); V(x, 1); G(x, 1); R(y, 1)
        L(); J(y, 1); L(-1); G(x, -1); V(x, -1)
    else:  # inverse schedule with logical source y and target x
        V(y, 1); G(y, 1); L(); J(x, -1); L(-1); R(x, -1); G(y, -1); V(y, -1)
        R(x, 1); L(); J(x, 1); L(-1)
    return x, y, side, center


if __name__ == '__main__':
    import sys, time
    for h in map(int, sys.argv[1:] or ['10', '12', '16']):
        t = time.time(); c = ComplexSideCircuit(h)
        print(c.stats(), f'{time.time()-t:.1f}s', flush=True)
