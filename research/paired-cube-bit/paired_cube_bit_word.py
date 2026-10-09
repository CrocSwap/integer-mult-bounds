#!/usr/bin/env python3
"""Paired-cube BIT local word with partner-pair source mixing: deterministic generator and rank compiler.

Ports are the triples of [h] (h = 2p) taking one coordinate from each of three distinct coordinate pairs
(v = 8*C(p,3)); bit labels chi_S in Q^h with H0 = (I - J/9)/2, so H0(chi_S, chi_T) = (|S cap T| - 1)/2.
Payload F2. Mod-2 decoder, for every target T:
    x_T = sum_{c in T} star(c)                         (2p copied point-star centres, frames of dim h-2)
        + face channels  P'(J,i,eta_i)                  (cubes sharing exactly pair i, matching selector)
        + edge channels  Q'(J,i,j,mode)                 (cubes sharing pairs i,j, exactly one selector match)
        + partner        x_{T'}, T' = T with the selectors of cube pairs 1,2 flipped (single-source root)
        + partner-pair sum of the opposite pair of T's parity class, mixed on two SOURCE registers and
          delivered at the shared cap of {T, T'} (no auxiliary role).
At p = 12 each cube merges its face-1 and edge-01 outputs into u(b0,b1) and its face-2 and edge-02 outputs into
w(b0,b2) (variant u); each merged node is read by two single roots and the mod-2 sums are unchanged. Its local
channels use the L1 association (local_l1): three of the six G sums add long face diagonals instead of edges.
Compiler: the PR #144 frames.py/gauges.py ledger on rational frames (target cap ker(3 chi_T - 1), centre frame =
span of the star), coordinate-padded maximum carrier matching (frozen arcs), plain frames span(n) for additions of
span dimension <= PLAIN (closed under operands; a linked donor's span must lie in the plain target), PR #144
chronological partial gauges with a G-nondegeneracy filter, PR #144 bit ledger (m = 3h, W = 2v + R).
Linear algebra is exact: ranks are computed modulo the Mersenne prime 2^127-1, which exceeds the Hadamard bound
of every minor that occurs (see README.md); G-nondegeneracy is certified by integer Gram determinants.

Usage: python3 paired_cube_bit_word.py --p 12 [--out DIR] [--check] [--solve-matching]
Standard library only. Run without -O.
"""
import argparse, gzip, hashlib, json, math, os, sys, time
from collections import Counter, defaultdict, deque
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
P = (1 << 127) - 1
PLAIN = 8
L1_DIAGONAL = {(0, 1, 0), (0, 1, 1), (1, 2, 1)}  # (cube positions j < k, mode) of the diagonal G sums at p = 12
MODULES ={11: 'pair_module_p11.json', 12: 'pair_module_p12.json', 13: 'pair_module_p13.json'}


def require(cond, msg):
    if not cond:
        raise SystemExit('FAIL: ' + msg)


# ----------------------------------------------------------------------------- exact subspaces of F_P^h
def rref(rows, h):
    piv = {}
    for r in rows:
        x = [a % P for a in r]
        for c, y in piv.items():
            if x[c]:
                f = x[c]
                x = [(a - f * b) % P for a, b in zip(x, y)]
        nz = next((j for j in range(h) if x[j]), None)
        if nz is None:
            continue
        inv = pow(x[nz], P - 2, P)
        x = [(a * inv) % P for a in x]
        for c in list(piv):
            y = piv[c]
            if y[nz]:
                f = y[nz]
                piv[c] = [(a - f * b) % P for a, b in zip(y, x)]
        piv[nz] = x
    return tuple(tuple(piv[c]) for c in sorted(piv))


def kernel(S, h):
    pivs = [next(j for j in range(h) if row[j]) for row in S]
    ps = set(pivs)
    out = []
    for f in range(h):
        if f in ps:
            continue
        u = [0] * h
        u[f] = 1
        for row, c in zip(S, pivs):
            u[c] = (-row[f]) % P
        out.append(u)
    return rref(out, h)


class Table:
    """Interned subspaces (canonical RREF) with memoized joins; id 0 is the zero space."""
    def __init__(self, h):
        self.h = h
        self.rows = [()]
        self.index = {(): 0}
        self.jc = {}
        self.pc = {}

    def intern(self, rows):
        S = rref(rows, self.h)
        i = self.index.get(S)
        if i is None:
            i = len(self.rows)
            self.rows.append(S)
            self.index[S] = i
        return i

    def dim(self, i):
        return len(self.rows[i])

    def join(self, i, j):
        if i == j or j == 0:
            return i
        if i == 0:
            return j
        if i > j:
            i, j = j, i
        k = self.jc.get((i, j))
        if k is None:
            A, B = self.rows[i], self.rows[j]
            k = i if len(A) == self.h else j if len(B) == self.h else self.intern(A + B)
            self.jc[(i, j)] = k
        return k

    def join_many(self, ids):
        k = 0
        for i in ids:
            k = self.join(k, i)
        return k

    def contained(self, i, j):
        return self.join(i, j) == j

    def perp(self, i):
        k = self.pc.get(i)
        if k is None:
            k = self.intern(kernel(self.rows[i], self.h))
            self.pc[i] = k
        return k


class Geometry:
    """Bit geometry: source line <chi_S>; target cap annihilated by 3 chi_T - 1 (the H0 = (I-J/9)/2 cap)."""
    def __init__(self, h, labels):
        self.h = h
        self.T = Table(h)
        self.src = [self.T.intern([[1 if j in lab else 0 for j in range(h)]]) for lab in labels]
        self.tcov = [self.T.intern([[(3 if j in lab else 0) - 1 for j in range(h)]]) for lab in labels]
        self.coord = [self.T.intern([[1 if k == j else 0 for k in range(h)]]) for j in range(h)]

    def join(self, a, b): return self.T.join(a, b)
    def join_many(self, ids): return self.T.join_many(ids)
    def dim(self, a): return self.T.dim(a)
    def perp(self, a): return self.T.perp(a)
    def contained(self, a, b): return self.T.contained(a, b)


def gram_nondegenerate_frame(rows, h):
    """G = I - J/9 nondegenerate on the F_P-subspace with basis rows (exact sound test: an integer determinant
    nonzero mod P is nonzero over Q; frames here are reductions of rational frames of the same dimension)."""
    k = len(rows)
    if k == 0:
        return True
    inv9 = pow(9, P - 2, P)
    sums = [sum(s) % P for s in rows]
    M = [[(sum(a * b for a, b in zip(rows[i], rows[j])) - inv9 * sums[i] * sums[j]) % P for j in range(k)] for i in range(k)]
    return len(rref(M, k)) == k


# ----------------------------------------------------------------------------- graph
class BitGraph:
    def __init__(self, p):
        self.p, self.h = p, 2 * p
        self.cubes = list(combinations(range(p), 3))
        self.labels = [tuple(2 * i + b for i, b in zip(I, bits)) for I in self.cubes for bits in product(range(2), repeat=3)]
        self.a = [None] * len(self.labels)
        self.s = [1 << i for i in range(len(self.labels))]
        self.intern = {}
        self.source = {(I, bits): 8 * j + k for j, I in enumerate(self.cubes) for k, bits in enumerate(product(range(2), repeat=3))}
        self.A, self.G = {}, {}
        self.root, self.centers, self.mix = [], [], []

    def add(self, a, b):
        if a is None:
            return b
        if b is None:
            return a
        if a > b:
            a, b = b, a
        if (a, b) not in self.intern:
            require(not self.s[a] & self.s[b], 'support-disjoint addition')
            self.intern[a, b] = len(self.a)
            self.a.append([a, b])
            self.s.append(self.s[a] | self.s[b])
        return self.intern[a, b]

    def sum(self, xs):
        xs = [x for x in xs if x is not None]
        while len(xs) > 1:
            xs = [self.add(xs[i], xs[i + 1]) if i + 1 < len(xs) else xs[i] for i in range(0, len(xs), 2)]
        return xs[0] if xs else None

    def module(self, data, inputs):
        image = list(inputs)
        n = data['input_count']
        require(len(image) == n, 'module arity')
        for pair in data['args'][n:]:
            image.append(self.add(image[pair[0]], image[pair[1]]))
        return [image[x] for x in data['roots']]

    def local_channels(self):
        for I in self.cubes:
            src = lambda bits: self.source[I, tuple(bits)]
            edges = {}
            for ii, jj in combinations(range(3), 2):
                kk = 3 - ii - jj
                for a, b in product(range(2), repeat=2):
                    b0 = [0] * 3
                    b0[ii], b0[jj] = a, b
                    b1 = b0[:]
                    b1[kk] = 1
                    edges[ii, jj, a, b] = self.add(src(b0), src(b1))
                self.G[I, I[ii], I[jj], 0] = self.add(edges[ii, jj, 0, 0], edges[ii, jj, 1, 1])
                self.G[I, I[ii], I[jj], 1] = self.add(edges[ii, jj, 0, 1], edges[ii, jj, 1, 0])
            for ii in range(3):
                jj = next(j for j in range(3) if j != ii)
                for a in range(2):
                    ids = [edges[(ii, jj, a, b) if ii < jj else (jj, ii, b, a)] for b in range(2)]
                    self.A[I, I[ii], a] = self.add(*ids)

    def local_l1(self):
        """L1 local-channel association (eumemic, Claude assistance): the G sums listed in L1_DIAGONAL add the two
        long diagonals of their cube face, the other G sums and the A sums add two edges; same supports as
        local_channels, with the nodes created in channel order."""
        for I in self.cubes:
            def at(bits):
                b = [0] * 3
                for q, x in bits.items():
                    b[q] = x
                return self.source[I, tuple(b)]

            def edge(d, fixed):
                return self.add(at({**fixed, d: 0}), at({**fixed, d: 1}))
            for j, k in combinations(range(3), 2):
                r = 3 - j - k
                for mode in range(2):
                    if (j, k, mode) in L1_DIAGONAL:
                        node = self.add(self.add(at({j: 0, k: mode, r: 0}), at({j: 1, k: 1 - mode, r: 1})),
                                        self.add(at({j: 0, k: mode, r: 1}), at({j: 1, k: 1 - mode, r: 0})))
                    else:
                        node = self.add(edge(r, {j: 0, k: mode}), edge(r, {j: 1, k: 1 - mode}))
                    self.G[I, I[j], I[k], mode] = node
            for i in range(3):
                j, k = [q for q in range(3) if q != i]
                for a in range(2):
                    self.A[I, I[i], a] = self.add(edge(k, {i: a, j: 0}), edge(k, {i: a, j: 1}))

    def finish(self, pair, allbut, merge=False, l1=False):
        p = self.p
        self.local_l1() if l1 else self.local_channels()
        Pm, Qm = {}, {}
        for i in range(p):
            pairs = list(combinations([a for a in range(p) if a != i], 2))
            for bit in range(2):
                for K, node in zip(pairs, self.module(pair, [self.A[tuple(sorted((i, *K))), i, bit] for K in pairs])):
                    Pm[tuple(sorted((i, *K))), i, bit] = node
        for i, j in combinations(range(p), 2):
            others = [a for a in range(p) if a not in (i, j)]
            for mode in range(2):
                for k, node in zip(others, self.module(allbut, [self.G[tuple(sorted((i, j, k))), i, j, mode] for k in others])):
                    Qm[tuple(sorted((i, j, k))), i, j, mode] = node
        allb = list(product(range(2), repeat=3))

        def emit(I, bl, node, channel):
            self.root.append(dict(node=node, targets=[self.source[I, b] for b in bl], kind='side', channel=channel))
        for I in self.cubes:
            for a in range(2):
                emit(I, [b for b in allb if b[0] == a], Pm[I, I[0], a], 'face0')
            for a in range(2):
                for m12 in range(2):
                    emit(I, [b for b in allb if b[0] == a and (b[1] ^ b[2]) == m12], Qm[I, I[1], I[2], 1 - m12], 'edge12')
            if merge:
                # variant u output merge (eumemic, Claude assistance): u(b0,b1) = face1 + edge01 and
                # w(b0,b2) = face2 + edge02, each read by two single roots, replace the four single reads
                u = {(b0, b1): self.add(Pm[I, I[1], b1], Qm[I, I[0], I[1], 1 - (b0 ^ b1)]) for b0 in range(2) for b1 in range(2)}
                w = {(b0, b2): self.add(Pm[I, I[2], b2], Qm[I, I[0], I[2], 1 - (b0 ^ b2)]) for b0 in range(2) for b2 in range(2)}
            for b in allb:
                if merge:
                    emit(I, [b], u[b[0], b[1]], 'u01')
                    emit(I, [b], w[b[0], b[2]], 'w02')
                else:
                    emit(I, [b], Pm[I, I[1], b[1]], 'face1')
                    emit(I, [b], Qm[I, I[0], I[1], 1 - (b[0] ^ b[1])], 'edge01')
                    emit(I, [b], Pm[I, I[2], b[2]], 'face2')
                    emit(I, [b], Qm[I, I[0], I[2], 1 - (b[0] ^ b[2])], 'edge02')
                emit(I, [b], self.source[I, (b[0], 1 - b[1], 1 - b[2])], 'partner')
            # partner-pair source mixing: in each parity class the pair with selector a on cube pair 0
            # (carrier = smaller bits, passive = its partner) is delivered to the opposite pair of the class.
            for par in range(2):
                for a in range(2):
                    pair_ = sorted(b for b in allb if sum(b) % 2 == par and b[0] == a)
                    recv = sorted(b for b in allb if sum(b) % 2 == par and b[0] == 1 - a)
                    self.mix.append(dict(carrier=self.source[I, pair_[0]], passive=self.source[I, pair_[1]],
                                         receivers=[self.source[I, r] for r in recv]))
        for i in range(p):
            for e in range(2):
                self.centers.append(self.sum(self.A[I, i, e] for I in self.cubes if i in I))
        for coordinate, node in enumerate(self.centers):
            self.root.append(dict(node=node, targets=[t for t, lab in enumerate(self.labels) if coordinate in lab],
                                  kind='center', coordinate=coordinate))
        return dict(p=p, h=self.h, v=len(self.labels), labels=[list(l) for l in self.labels], args=self.a,
                    roots=self.root, partner_mix=self.mix)


def check_decoder(g):
    v, args = g['v'], g['args']
    sup = [1 << i for i in range(v)] + [0] * (len(args) - v)
    for x in range(v, len(args)):
        a, b = args[x]
        require(not sup[a] & sup[b], 'disjoint supports')
        sup[x] = sup[a] | sup[b]
    acc = [0] * v
    for r in g['roots']:
        for t in r['targets']:
            acc[t] ^= sup[r['node']]
    for mx in g['partner_mix']:
        for t in mx['receivers']:
            acc[t] ^= (1 << mx['carrier']) | (1 << mx['passive'])
    return sum(acc[t] != 1 << t for t in range(v))


# ----------------------------------------------------------------------------- matching
def hopcroft_karp(adj, nleft, nright):
    INF = 1 << 30
    mL, mR = [-1] * nleft, [-1] * nright
    while True:
        dist = [INF] * nleft
        dq = deque(u for u in range(nleft) if mL[u] < 0)
        for u in dq:
            dist[u] = 0
        found = False
        while dq:
            u = dq.popleft()
            for w in adj[u]:
                m = mR[w]
                if m < 0:
                    found = True
                elif dist[m] == INF:
                    dist[m] = dist[u] + 1
                    dq.append(m)
        if not found:
            return mL
        it = [0] * nleft
        for u0 in range(nleft):
            if mL[u0] >= 0:
                continue
            stack = [u0]
            while stack:
                u = stack[-1]
                if it[u] < len(adj[u]):
                    w = adj[u][it[u]]
                    it[u] += 1
                    m = mR[w]
                    if m < 0:
                        ws = w
                        for uu in reversed(stack):
                            prev = mL[uu]
                            mL[uu], mR[ws] = ws, uu
                            ws = prev
                        break
                    if dist[m] == dist[u] + 1:
                        stack.append(m)
                else:
                    dist[u] = INF
                    stack.pop()


# ----------------------------------------------------------------------------- compiler
def compile_word(g, frozen=None, plain_k=PLAIN, log=lambda *a: None):
    h, v = g['h'], g['v']
    geo = Geometry(h, [tuple(l) for l in g['labels']])
    args = [None] + [None if a is None else [x + 1 for x in a] for a in g['args']]  # node 0 reserved
    roots = [dict(r, node=r['node'] + 1) for r in g['roots']]
    n, q = len(args), len(roots)
    sup = [0] * n
    for i in range(v):
        sup[i + 1] = 1 << i
    spans = [0] * n
    for i in range(v):
        spans[i + 1] = geo.src[i]
    for x in range(v + 1, n):
        a, b = args[x]
        spans[x] = geo.join(spans[a], spans[b])
        sup[x] = sup[a] | sup[b]
    rframe, rann, ell = [], [], 0
    Y, targetH = [0] * v, Counter()
    for r in roots:
        x = r['node']
        if r['kind'] == 'center':
            U = spans[x]; A = geo.perp(U); ell += geo.dim(U)
        else:
            A = geo.join_many(geo.tcov[t] for t in r['targets']); U = geo.perp(A)
            for t in r['targets']:
                require(geo.contained(Y[t], U), 'target retreat')
                targetH[geo.dim(U) - geo.dim(Y[t])] += 1
                Y[t] = U
        require(geo.contained(spans[x], U), 'root physical compatibility')
        rframe.append(U); rann.append(A)
    for t in range(v):
        require(geo.contained(Y[t], geo.perp(geo.tcov[t])), 'target cap')
        targetH[h - 1 - geo.dim(Y[t])] += 1
    active, todo = set(range(1, v + 1)), [r['node'] for r in roots]
    while todo:
        x = todo.pop()
        if x not in active:
            active.add(x)
            if args[x]:
                todo.extend(args[x])
    succ0, cons = [[] for _ in args], [[] for _ in args]
    for x in sorted(active):
        if args[x]:
            for y in args[x]:
                succ0[y].append(x)
    for j, r in enumerate(roots):
        cons[r['node']].append(rann[j])
    preann, initial = [0] * n, [0] * n
    for x in sorted(active, reverse=True):
        preann[x] = geo.join_many(cons[x] + [preann[y] for y in succ0[x]])
        cover = 0
        s = sup[x]
        while s:
            b = s & -s; s ^= b
            for j in g['labels'][b.bit_length() - 1]:
                cover |= 1 << j
        initial[x] = geo.join_many([preann[x]] + [geo.coord[j] for j in range(h) if not cover >> j & 1])
    order = sorted(active, key=lambda x: (h - geo.dim(initial[x]), x))
    position = {x: i for i, x in enumerate(order)}
    uses, usevalue, usetarget, useann, usecode = [[] for _ in args], [], [], [], []
    for x in order:
        if args[x]:
            for j, y in enumerate(args[x]):
                uses[y].append(len(usevalue)); usevalue.append(y); usetarget.append(x); useann.append(initial[x]); usecode.append(['op', x - 1, j])
    for j, r in enumerate(roots):
        x = r['node']
        uses[x].append(len(usevalue)); usevalue.append(x); usetarget.append(n + j); useann.append(rann[j]); usecode.append(['root', j])
    donors = [x for x in order if args[x]]
    code_index = {tuple(c): u for u, c in enumerate(usecode)}
    if frozen is not None:
        arcs = {d + 1: code_index[tuple(c)] for d, c in frozen}
    else:
        dindex = {x: i for i, x in enumerate(donors)}
        adj = [[] for _ in donors]
        for x in donors:
            for y in args[x]:
                for u in uses[y]:
                    t = usetarget[u]
                    if t == x or (t < n and position[t] <= position[x]):
                        continue
                    if geo.contained(useann[u], initial[x]):
                        adj[dindex[x]].append(u)
        mL = hopcroft_karp(adj, len(donors), len(usevalue))
        arcs = {donors[i]: u for i, u in enumerate(mL) if u >= 0}
    for x, u in arcs.items():
        t = usetarget[u]
        require(usevalue[u] in args[x] and (t >= n or position[t] > position[x]), 'arc order')
        require(geo.contained(useann[u], initial[x]), 'arc frame')
    succ, direct = [[] for _ in args], [[] for _ in args]
    for x in order:
        if args[x]:
            for y in args[x]:
                succ[y].append(x)
    for j, r in enumerate(roots):
        direct[r['node']].append(rann[j])
    for x, u in arcs.items():
        t = usetarget[u]
        (succ[x].append(t) if t < n else direct[x].append(rann[t - n]))
    ann, rank = [0] * n, [0] * n
    for x in reversed(order):
        ann[x] = geo.join_many(direct[x] + [ann[y] for y in succ[x]])
        rank[x] = h - geo.dim(ann[x])
        require(geo.contained(ann[x], geo.perp(spans[x])), 'span inside frame')
    # plain frames span(n): leaves and small additions, closed under operands; a linked donor must be plain and
    # its span must lie in the plain target's span
    cand = set(x for x in active if not args[x])
    for x in sorted(active):
        if args[x] and geo.dim(spans[x]) <= plain_k and all(y in cand for y in args[x]):
            cand.add(x)
    arcin, users = defaultdict(list), defaultdict(list)
    for x, u in arcs.items():
        if usetarget[u] < n:
            arcin[usetarget[u]].append(x)
    for x in active:
        if args[x]:
            for y in args[x]:
                users[y].append(x)
    changed = True
    while changed:
        changed = False
        for t in sorted(cand):
            if t in cand and any(x not in cand or not geo.contained(spans[x], spans[t]) for x in arcin[t]):
                cand.discard(t); changed = True
                st = [t]
                while st:
                    z = st.pop()
                    for w in users[z]:
                        if w in cand:
                            cand.discard(w); st.append(w)
    plain = sorted(cand)
    for x in plain:
        ann[x] = geo.perp(spans[x]); rank[x] = h - geo.dim(ann[x])
    H = Counter()
    for x in order:
        r, deg = rank[x], len(uses[x])
        require(deg > 0, 'unused node')
        H[r] += deg - 1
        if args[x]:
            H[h - r] += 1
            for y in args[x]:
                require(geo.contained(ann[x], ann[y]), 'operand nesting')
                H[r - rank[y]] += 1
        else:
            H[1] += 1; H[r - 1] += 1
    for j, root in enumerate(roots):
        x = root['node']; r = rank[x]; rt = geo.dim(rframe[j])
        require(r <= rt, 'root climb')
        if root['kind'] == 'center':
            require(r == rt, 'centre frame')
            H[r] += 1; H[h - r] += 1
        else:
            H[rt - r] += 1; H[h - rt] += 1
    for x, u in arcs.items():
        val, t = usevalue[u], usetarget[u]
        rv, rd = rank[val], rank[x]
        rt = rank[t] if t < n else geo.dim(rframe[t - n])
        require(rt >= rd >= rv, 'arc ranks')
        H[h - rd] -= 1; H[rv] -= 1; H[rt - rv] -= 1; H[rt - rd] += 1
    require(min(H.values()) >= 0, 'nonnegative ledger')
    R = len(donors) + q - len(arcs)
    require(sum(r * c for r, c in H.items()) == h * R + ell, 'mass identity')
    prof = dict(h=h, v=v, R=R, q=q, c=len(donors), matched=len(arcs), loss=ell, plain=len(plain))
    wit = dict(geo=geo, args=args, roots=roots, n=n, order=order, arcs=arcs, ann=ann, rank=rank, uses=uses,
               usevalue=usevalue, usetarget=usetarget, usecode=usecode, rframe=rframe, rann=rann, spans=spans,
               plain=plain, H=H, targetH=targetH)
    return prof, wit


def nondeg_id(geo, f, cache):
    if f not in cache:
        cache[f] = gram_nondegenerate_frame(list(geo.T.rows[f]), geo.h)
    return cache[f]


def select_gauges(g, prof, wit, trial_a=0.00065):
    """PR #144 gauges.select, exactly, plus the bit G-nondegeneracy filter on sigma."""
    geo = wit['geo']; h, v = prof['h'], prof['v']
    args, roots, n, order, ann, arcs = wit['args'], wit['roots'], wit['n'], wit['order'], wit['ann'], wit['arcs']
    usevalue, usetarget = wit['usevalue'], wit['usetarget']
    incoming = set(arcs.values())
    uses, opuse, rootuse = [[] for _ in args], {}, {}
    for u, (val, t) in enumerate(zip(usevalue, usetarget)):
        uses[val].append(u)
        if t < n:
            opuse[t, 0 if args[t][0] == val else 1] = u
        else:
            rootuse[t - n] = u
    assign, sources, ops, R = {}, {}, [], 0
    for x in order:
        if args[x]:
            aa, bb = args[x]
            dest, control = assign[opuse[x, 0]], assign[opuse[x, 1]]
            if x in arcs:
                u = arcs[x]
                if usevalue[u] == aa:
                    dest, control = control, dest
                require(u not in assign, 'arc use assigned once')
                assign[u] = control
            ops.append((dest, control, x))
        else:
            dest = R; R += 1; sources[x] = dest
        free = [u for u in uses[x] if u not in incoming]
        require(free, 'free use')
        for j, u in enumerate(free):
            if j == 0:
                assign[u] = dest
            else:
                t = R; R += 1; assign[u] = t; ops.append((t, dest, x))
    require(R == prof['R'], 'role count')
    rootroles = [assign[rootuse[j]] for j in range(len(roots))]
    prev, pred, first = [-1] * R, [], [None] * R
    for i, (a, b, x) in enumerate(ops):
        pred.append((prev[a], prev[b])); prev[a] = prev[b] = i
        if first[a] is None:
            first[a] = x
        if first[b] is None:
            first[b] = x
    stack = [prev[s] for r, s in zip(roots, rootroles) if r['kind'] == 'center' and prev[s] >= 0]
    phase = set()
    while stack:
        i = stack.pop()
        if i not in phase:
            phase.add(i); stack.extend(j for j in pred[i] if j >= 0)
    touched = set(sources.values())
    for i in phase:
        touched.update(ops[i][:2])
    co = [0] * R
    for r, s in zip(roots, rootroles):
        co[s] |= sum(1 << t for t in r['targets'])
    for a, b, x in reversed(ops):
        co[b] |= co[a]
    limit = [None] * v
    for r in roots:
        if r['kind'] != 'center':
            A = geo.join_many(geo.tcov[t] for t in r['targets'])
            for t in r['targets']:
                if limit[t] is None:
                    limit[t] = A
    for t in range(v):
        if limit[t] is None:
            limit[t] = geo.tcov[t]
    H = Counter(wit['H'])
    gauges, selected, cache = Counter(), [], {}
    cands = sorted((s for s in range(R) if s not in touched and first[s] is not None),
                   key=lambda s: (geo.dim(ann[first[s]]), bin(co[s]).count('1'), s))

    def excess(t):
        return t * math.expm1(trial_a * math.log(3 * h / t)) if t else 0.
    for s in cands:
        A, targets, bits = ann[first[s]], [], co[s]
        while bits:
            low = bits & -bits; t = low.bit_length() - 1; bits ^= low; targets.append(t)
            A = geo.join(A, limit[t])
            if geo.dim(A) == h:
                break
        if geo.dim(A) == h:
            continue
        r, d = h - geo.dim(ann[first[s]]), h - geo.dim(A)
        delta = 3 * (excess(r - d) - excess(r)) + excess(3 * d)
        delta += 3 * math.fsum(excess(d) + excess(h - geo.dim(limit[t]) - d) - excess(h - geo.dim(limit[t])) for t in targets)
        if delta >= -1e-12 or not nondeg_id(geo, geo.perp(A), cache):
            continue
        H[r] -= 1; H[r - d] += 1; gauges[d] += 1
        require(H[r] >= 0, 'gauge ledger')
        for t in targets:
            limit[t] = A
        selected.append(dict(role=s, first=first[s] - 1, targets=targets, dim=d, ann=A))
    Yh, cur = Counter(), [0] * v
    for z in reversed(selected):
        U = geo.perp(z['ann'])
        for t in z['targets']:
            require(geo.contained(cur[t], U), 'gauge target chain')
            Yh[geo.dim(U) - geo.dim(cur[t])] += 1; cur[t] = U
    for r in roots:
        if r['kind'] != 'center':
            U = geo.perp(geo.join_many(geo.tcov[t] for t in r['targets']))
            for t in r['targets']:
                require(geo.contained(cur[t], U), 'side target chain')
                Yh[geo.dim(U) - geo.dim(cur[t])] += 1; cur[t] = U
    for t in range(v):
        Yh[h - 1 - geo.dim(cur[t])] += 1
    word = dict(ops=[[a, b, x - 1] for a, b, x in ops], sources={str(x - 1): s for x, s in sources.items()},
                rootroles=rootroles, phase1=sorted(phase), gauges=[{k: z[k] for k in ('role', 'first', 'targets', 'dim')} for z in selected],
                _gauge_ann=[z['ann'] for z in selected])
    return gauges, H, Yh, word


def profile(prof, gauges, H, Y):
    h, v, R, ell = prof['h'], prof['v'], prof['R'], prof['loss']
    m, W = 3 * h, 2 * v + R
    source = Counter({1: v, h - 4: v // 2, 2: v // 2, h - 2: v // 2})
    C = Counter()
    for part in (H, source, Y):
        for r, c in part.items():
            if r and c:
                C[r] += 3 * c
    for d, c in gauges.items():
        C[3 * d] += c
    C[2] += 2 * v
    mass = sum(r * c for r, c in C.items())
    require(W * m - mass == 2 * v - 3 * ell, 'shared-core telescoping deficit')
    srt = lambda c: {str(k): c[k] for k in sorted(c) if c[k]}
    return dict(h=h, v=v, R=R, c=prof['c'], q=prof['q'], matched=prof['matched'], loss=ell, plain_frames=prof['plain'],
                m=m, W_per_vertex=W, rank_per_vertex=mass, deficit_per_vertex=W * m - mass,
                selected_roles=sum(gauges.values()), selected_rank_histogram=srt(gauges),
                remaining_internal_histogram=srt(H), source_data_histogram=srt(source), target_data_histogram=srt(Y),
                child_histogram=srt(C), maxchild=max(C))


def float_root(child, W, m):
    items = [(int(t), c) for t, c in child.items()]
    lo, hi = 0., .1
    for _ in range(80):
        a = (lo + hi) / 2
        if math.fsum(c * (t / m) ** (1 - a) for t, c in items) < W:
            lo = a
        else:
            hi = a
    return lo


def ratrec(r):
    """Rational reconstruction a/b of a residue mod P with |a|, b < sqrt(P/2)."""
    r %= P
    if r == 0:
        return 0, 1
    bound = math.isqrt(P // 2)
    r0, r1, s0, s1 = P, r, 0, 1
    while r1 > bound:
        qq = r0 // r1
        r0, r1 = r1, r0 - qq * r1
        s0, s1 = s1, s0 - qq * s1
    require(abs(s1) <= bound and s1 != 0, 'rational reconstruction')
    a, b = (r1, s1) if s1 > 0 else (-r1, -s1)
    require((a - r * b) % P == 0, 'reconstruction residue')
    return a, b


def primitive(row):
    from fractions import Fraction
    fr = [Fraction(*ratrec(x)) for x in row]
    den = 1
    for f in fr:
        den = den * f.denominator // math.gcd(den, f.denominator)
    ints = [int(f * den) for f in fr]
    gg = 0
    for x in ints:
        gg = math.gcd(gg, abs(x))
    ints = [x // gg for x in ints] if gg else ints
    first = next((x for x in ints if x), 1)
    return [-x for x in ints] if first < 0 else ints


def frame_record(geo, ann_id):
    """Exact integer description of the frame perp(ann): 'a' = integer annihilator rows (frame = common kernel)
    when codim <= dim, else 'b' = integer basis rows. Both are primitive rows of the rational RREF."""
    h = geo.h
    A = geo.T.rows[ann_id]
    codim = len(A)
    if codim <= h - codim:
        rows = [primitive(r) for r in A]
        return dict(dim=h - codim, a=rows)
    B = geo.T.rows[geo.perp(ann_id)]
    return dict(dim=h - codim, b=[primitive(r) for r in B])


def dumps(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')) + '\n'


def build(p, frozen_arcs=None, log=print):
    mod = json.loads((HERE / 'data' / MODULES[p]).read_text())
    abo = nested_prefix(p - 2) if p == 12 else all_but_one(p - 2)
    g = BitGraph(p).finish(mod, abo, merge=p == 12, l1=p == 12)
    require(check_decoder(g) == 0, 'mod-2 decoder identity')
    t0 = time.time()
    prof, wit = compile_word(g, frozen=frozen_arcs)
    log('compiled p=%d in %.1fs: R=%d arcs=%d plain=%d' % (p, time.time() - t0, prof['R'], prof['matched'], prof['plain']))
    gauges, H, Y, word = select_gauges(g, prof, wit)
    prf = profile(prof, gauges, H, Y)
    arcs = sorted([x - 1, wit['usecode'][u]] for x, u in wit['arcs'].items())
    cache = {}
    geo = wit['geo']
    deg = sum(1 for x in wit['order'] if not nondeg_id(geo, geo.perp(wit['ann'][x]), cache))
    deg += sum(1 for U in wit['rframe'] if not nondeg_id(geo, U, cache))
    require(deg == 0, 'G-nondegenerate node and root frames')
    out = dict(graph=dict(p=p, h=g['h'], v=g['v'], labels=g['labels'], args=g['args'], roots=g['roots'],
                          partner_mix=g['partner_mix'], pair_module_sha256=hashlib.sha256((HERE / 'data' / MODULES[p]).read_bytes()).hexdigest()),
               compile=dict(plain_threshold=PLAIN, order=[x - 1 for x in wit['order']], plain=[x - 1 for x in wit['plain']], arcs=arcs),
               word={k: v for k, v in word.items() if not k.startswith('_')})
    exp = export(p, g, prof, wit, word, prf)
    return out, prf, arcs, exp


def export(p, g, prof, wit, word, prf):
    """Plain-JSON gate files: graph, word (selection.json shape), exact frames, partial-K chronology."""
    geo, h, v = wit['geo'], g['h'], g['v']
    n, roots = wit['n'], wit['roots']
    ann = wit['ann']
    frames = {}

    def fid(a):
        if a not in frames:
            frames[a] = None
        return a
    node_frame = {str(x - 1): fid(ann[x]) for x in wit['order']}
    root_frame = [fid(a) for a in wit['rann']]
    gauges = []
    for z, A in zip(word['gauges'], word['_gauge_ann']):
        gauges.append(dict(z, frame=fid(A)))
    lab = g['labels']
    src_ann = [fid(geo.perp(geo.src[i])) for i in range(v)]
    full = fid(0)
    level2 = {}
    for j, r in enumerate(g['roots']):
        if r['kind'] == 'side' and len(r['targets']) == 2:
            level2[tuple(sorted(r['targets']))] = j
    kchron = []
    for mx in g['partner_mix']:
        c, d = mx['carrier'], mx['passive']
        mixf = fid(geo.perp(geo.join(geo.src[c], geo.src[d])))
        j = level2[tuple(sorted(mx['receivers']))]
        capf = root_frame[j]
        require(geo.contained(capf, mixf), 'mix frame inside receivers cap')
        kchron.append(dict(carrier=c, passive=d, receivers=mx['receivers'], mix_frame=mixf, deliver_frame=capf,
                           deliver_after_root=j, undo_frame=full,
                           carrier_chain=[src_ann[c], mixf, capf, full], passive_chain=[src_ann[d], mixf, full],
                           carrier_ranks=[1, h - 4, 2], passive_ranks=[1, h - 2]))
    table = {str(a): frame_record(geo, a) for a in sorted(frames)}
    conv = dict(target_covector='3*chi_T - 1 (target cap = {u : (3 chi_T - 1).u = 0} = H0-orthogonal complement of chi_T)',
                gram='G = I - J/9 on Q^h (H0 = G/2, H0(chi_S,chi_T) = (|S cap T|-1)/2); nondegeneracy tested for G',
                frame_ids='frame id = id of the canonical annihilator; record "a" lists integer annihilator rows (frame ='
                          ' common kernel), record "b" lists integer basis rows; id 0 (empty "a") is the full space Q^h',
                ops='[dest, control, node]: dest ^= control at the frame of node (copies: dest is the fresh role)',
                nodes='zero-based graph nodes; nodes < v are the source leaves (port index)')
    graph = dict(p=p, h=h, v=v, labels=g['labels'], args=g['args'],
                 roots=[dict(r, coefficient=1) for r in g['roots']], partner_mix=g['partner_mix'],
                 decoder='mod 2: Y_T += sum of root nodes whose targets contain T (star roots: T reads star(c) for c in T;'
                         ' side roots; partner singles) + x_carrier + x_passive for each partner_mix entry receiving T;'
                         ' equals x_T = sum_{c in T} star(c) + sum_{|S cap T|=1} x_S')
    wordj = dict(ops=word['ops'], sources=word['sources'], rootroles=word['rootroles'], phase1=word['phase1'],
                 gauges=gauges, order=[x - 1 for x in wit['order']], arcs=sorted([x - 1, wit['usecode'][u]] for x, u in wit['arcs'].items()),
                 plain=[x - 1 for x in wit['plain']], node_frame=node_frame, root_frame=root_frame,
                 source_frame=src_ann, full_frame=full, conventions=conv,
                 schedule='old-value reads of non-gauged roles (frame 0); V injections at <chi_S>; ops in order (phase1 ops'
                          ' are those listed); centre copies read at 0; gauged old-value reads at their gauge frames'
                          ' (ascending per target); side root reads in root order; partial-K deliveries right after'
                          ' root deliver_after_root; undo at full frame; inverse ops; V removal')
    return dict(graph=graph, word=wordj, frames=dict(h=h, P_used_for_ranks='2^127-1', conventions=conv, frames=table),
                kchron=dict(h=h, entries=kchron, conventions=conv))


def nested_prefix(n):
    """Nested-prefix all-but-one module (QMOD lane; eumemic, Claude assistance): prefix p_{k+1} = p_k + x_k, suffix
    s_k = x_k + s_{k+1}; y_0 = s_1, y_{n-1} = p_{n-1}, y_{i+1} = p_i + (x_i + s_{i+2}). Each prefix is used twice with
    nested supports, which gives the carrier matching more links than the balanced tree. Contract-checked."""
    args = [None] * n

    def add(a, b):
        args.append([a, b])
        return len(args) - 1
    pre = {1: 0}
    for k in range(1, n - 1):
        pre[k + 1] = add(pre[k], k)
    suf = {n - 1: n - 1}
    for k in range(n - 2, 0, -1):
        suf[k] = add(k, suf[k + 1])
    roots = [None] * n
    roots[0], roots[n - 1] = suf[1], pre[n - 1]
    roots[1] = add(0, suf[2])
    for i in range(1, n - 2):
        roots[i + 1] = add(pre[i], add(i, suf[i + 2]))
    support = []
    for x, a in enumerate(args):
        if a is None:
            support.append(1 << x)
        else:
            require(0 <= a[0] < x and 0 <= a[1] < x and not support[a[0]] & support[a[1]], 'nested prefix disjoint')
            support.append(support[a[0]] | support[a[1]])
    full = (1 << n) - 1
    require(all(support[r] == full ^ (1 << i) for i, r in enumerate(roots)), 'nested prefix all-but-one roots')
    return dict(input_count=n, args=args, roots=roots)


def all_but_one(n):
    """PR #144 modules.all_but_one (balanced binary tree upward sums and complementary downward sums)."""
    args, support = [None] * n, [1 << i for i in range(n)]
    by = {s: i for i, s in enumerate(support)}

    def add(a, b):
        if a is None:
            return b
        if b is None:
            return a
        s = support[a] | support[b]
        if s not in by:
            by[s] = len(args); args.append([a, b]); support.append(s)
        return by[s]

    def tree(lo, hi):
        if hi - lo == 1:
            return (lo, None, None)
        mid = (lo + hi) // 2
        L, Rr = tree(lo, mid), tree(mid, hi)
        return (add(L[0], Rr[0]), L, Rr)
    roots = [None] * n

    def walk(t, outside):
        x, L, Rr = t
        if L is None:
            roots[x] = outside
            return
        walk(L, add(outside, Rr[0])); walk(Rr, add(outside, L[0]))
    walk(tree(0, n), None)
    active, stack = set(range(n)), list(roots)
    while stack:
        x = stack.pop()
        if x not in active:
            active.add(x)
            if args[x] is not None:
                stack.extend(args[x])
    ids = sorted(active); ren = {x: i for i, x in enumerate(ids)}
    return dict(input_count=n, args=[None if args[x] is None else [ren[y] for y in args[x]] for x in ids], roots=[ren[x] for x in roots])


def main():
    require(not sys.flags.optimize, 'run without -O')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--p', type=int, default=12)
    ap.add_argument('--out', type=Path, default=HERE / 'out')
    ap.add_argument('--check', action='store_true', help='regenerate from frozen arcs and compare byte-identically')
    ap.add_argument('--solve-matching', action='store_true', help='recompute the carrier matching (Hopcroft-Karp)')
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    arcs_path = HERE / 'data' / ('arcs_p%d.json' % a.p)
    frozen = None if a.solve_matching or not arcs_path.exists() else json.loads(arcs_path.read_text())
    out, prf, arcs, exp = build(a.p, frozen)
    root = float_root(prf['child_histogram'], prf['W_per_vertex'], prf['m'])
    word_bytes = gzip.compress(dumps(out).encode(), mtime=0)
    prof_bytes = dumps(prf).encode()
    names = {'word_p%d.json.gz' % a.p: word_bytes, 'profile_p%d.json' % a.p: prof_bytes}
    for k, obj in exp.items():
        names['%s_p%d.json' % (k, a.p)] = dumps(obj).encode()
    if a.check:
        for name, data in names.items():
            old = (a.out / name).read_bytes()
            if name.endswith('.gz'):  # gzip bytes depend on the zlib build; compare the compressed content
                old, data = gzip.decompress(old), gzip.decompress(data)
            require(old == data, 'byte-identical regeneration of ' + name)
        require(frozen is not None, 'frozen arcs present')
        print('PASS p=%d: word and profile regenerate byte-identically (sha256 %s, %s)' % (
            a.p, hashlib.sha256(word_bytes).hexdigest()[:16], hashlib.sha256(prof_bytes).hexdigest()[:16]))
    else:
        for name, data in names.items():
            (a.out / name).write_bytes(data)
        if frozen is None:
            arcs_path.write_text(dumps(arcs))
        print('wrote p=%d: R=%d R/v=%.3f loss=%d deficit=%d W=%d gauges=%d float a_b=%.7e' % (
            a.p, prf['R'], prf['R'] / prf['v'], prf['loss'], prf['deficit_per_vertex'], prf['W_per_vertex'],
            prf['selected_roles'], root))


if __name__ == '__main__':
    main()
