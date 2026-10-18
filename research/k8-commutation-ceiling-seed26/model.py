# SPDX-License-Identifier: Apache-2.0
"""The commutation trace class of the selected k8 word: dependency DAG, frame intervals and the exact per-register
bound (standard library; loads merged PR1671 code, research/selected-k8-frame-ceiling, for the word, its bitset
helpers, cone caps and ceiling.py, after checking their digests).

Class: W' = A' B' T', each segment any linear extension of its dependency order (same-register pairs that do not
commute), coefficients unchanged; frames: one frame per gate shared by its operands, nested along every register,
under PR1671's starts, ends, charged pins, cone caps and fixed centre descents.
"""
import collections
import importlib.util
from fractions import Fraction as Q
from pathlib import Path

PKG1671 = Path(__file__).resolve().parents[1] / 'selected-k8-frame-ceiling'
BASE_LO = Q(1690054109088, 10 ** 15)
BASE_HI = Q(1690054109089, 10 ** 15)
A_STAR = Q(21, 20) * BASE_HI
PROFILE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
LAMBDA_BITS = 40


def load_1671():
    spec = importlib.util.spec_from_file_location('k8_independent', PKG1671 / 'independent.py')
    I = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(I)
    return I


def regs(e):
    return tuple(e[1:3]) if e[0] == 'add' else (e[1],)


def commute(e, g):
    """matrix commutation of two elementary row operations: ADD row_t += c row_s, SCALE row_t *= c (c != 1)."""
    if e[0] == 'add' and g[0] == 'add':
        return e[1] != g[2] and g[1] != e[2]
    if e[0] == 'scale' and g[0] == 'scale':
        return True
    return not (set(regs(e)) & set(regs(g)))


def apply_exact(e, vec):
    """apply one gate to a sparse rational row vector {register: Fraction} (rows are linear forms)."""
    out = dict(vec)
    if e[0] == 'add':
        t, s = e[1], e[2]
        out[t] = out.get(t, Q(0)) + Q(e[3], e[4]) * out.get(s, Q(0))
    else:
        out[e[1]] = out.get(e[1], Q(0)) * Q(e[2], e[3])
    return {k: v for k, v in out.items() if v}


class Word:
    def __init__(self, I):
        self.I = I
        self.U = I.U
        w = self.U.word()
        self.w = w
        self.v, self.n = 112, 704
        nA, nB = len(w['A']), len(w['B'])
        tail = [w['cleanup'][i][:-1] + [f] for i, f in w['early_cleanup']]
        self.ops = w['A'] + w['B'] + tail
        self.seg = ['A'] * nA + ['B'] * nB + ['T'] * len(tail)
        self.nA, self.nB = nA, nB
        low = {int(q): I.frame(x) for q, x in w['helper_final'].items()}
        self.caps = I.cone_caps(w, self.n, self.v, low)
        self.pins = {q: I.frame(x) for q, x in zip(w['centers'], w['center_frames'])}
        for t in range(self.v):
            self.pins[self.v + t] = 1                     # target_levels is empty: zero subspace
        self.chrono = I.build(w)
        self.fixed = {}
        for q in range(self.n):
            self.fixed[('S', q)] = self.chrono['lo'][('S', q)]
            self.fixed[('E', q)] = self.chrono['hi'][('E', q)]
        for q, f in self.pins.items():
            self.fixed[('P', q)] = f
        self.on = collections.defaultdict(list)
        for i, e in enumerate(self.ops):
            for q in regs(e):
                self.on[q].append(i)

    def depends(self, mode, g, h):
        """does the earlier same-register gate g constrain the later gate h?"""
        return mode == 'chrono' or self.seg[g] != self.seg[h] or not commute(self.ops[g], self.ops[h])

    # ---------------------------------------------------------------- implementation I: propagation
    def intervals(self, mode):
        I, ops, seg = self.I, self.ops, self.seg
        pred = collections.defaultdict(set)
        for q, gs in self.on.items():
            for x, h in enumerate(gs):
                for g in gs[:x]:
                    if self.depends(mode, g, h):
                        pred[('G', h)].add(('G', g))
        for q in range(self.n):
            gs = self.on.get(q, [])
            for i in gs:
                pred[('G', i)].add(('S', q))
                pred[('E', q)].add(('G', i))
            pred[('E', q)].add(('S', q))
            if q in self.pins:
                pred[('P', q)].add(('S', q))
                pred[('E', q)].add(('P', q))
                for i in gs:
                    if seg[i] == 'A':
                        pred[('P', q)].add(('G', i))
                    else:
                        pred[('G', i)].add(('P', q))
        for q in self.caps:
            X = ('X', q)
            pred[X].add(('S', q))
            if q in self.pins:
                pred[X].add(('P', q))
            for i in self.on.get(q, []):
                if seg[i] in 'AB':
                    pred[X].add(('G', i))
                else:
                    pred[('G', i)].add(X)
            pred[('E', q)].add(X)
        order = ([('S', q) for q in range(self.n)] + [('G', i) for i in range(self.nA)] + [('P', q) for q in self.pins]
                 + [('G', i) for i in range(self.nA, self.nA + self.nB)] + [('X', q) for q in self.caps]
                 + [('G', i) for i in range(self.nA + self.nB, len(ops))] + [('E', q) for q in range(self.n)])
        pos = {x: k for k, x in enumerate(order)}
        succ = collections.defaultdict(set)
        for b, ps in pred.items():
            for a in ps:
                assert pos[a] < pos[b]
                succ[a].add(b)
        lo, hi = {}, {}
        for node in order:
            if node in self.fixed:
                lo[node] = self.fixed[node]
                if any(lo[p] & ~self.fixed[node] for p in pred[node]):
                    raise ValueError('fixed frame below the join of its predecessors')
            else:
                f = 1
                for p in pred[node]:
                    f = I.join(f, lo[p])
                lo[node] = f
        for node in reversed(order):
            if node in self.fixed:
                hi[node] = self.fixed[node]
            else:
                f = I.FULL
                for s in succ[node]:
                    f &= hi[s]
                if node[0] == 'X':
                    f &= self.caps[node[1]]
                hi[node] = f
            if lo[node] & ~hi[node]:
                raise ValueError('empty interval at %r' % (node,))
        return lo, hi

    # ---------------------------------------------------------------- implementation II: closed form
    def intervals_closed(self, mode):
        """lo2(g) = join of starts (and B/T-side pins) over ancestors; hi2(g) = meet of ends, A-side pins and caps over
        descendants; frame_model reduced-echelon tuples and its Zassenhaus meet."""
        M = self.U.retained('frame_model.py')
        I, ops, seg = self.I, self.ops, self.seg
        N = len(ops)

        def tup(mask):
            return M.basis(list(I.canonical_frame(mask)))

        def mask(t):
            vals = {0}
            for x in t:
                vals |= {y ^ x for y in vals}
            return sum(1 << y for y in vals)
        pred = [0] * N
        for q, gs in self.on.items():
            for x, h in enumerate(gs):
                for g in gs[:x]:
                    if self.depends(mode, g, h):
                        pred[h] |= 1 << g
        anc = [0] * N
        for j in range(N):
            a, x = pred[j], pred[j]
            while x:
                b = x & -x
                x ^= b
                a |= anc[b.bit_length() - 1]
            anc[j] = a
        desc = [0] * N
        for i in range(N):
            x = anc[i]
            while x:
                b = x & -x
                x ^= b
                desc[b.bit_length() - 1] |= 1 << i
        S = {q: tup(self.fixed[('S', q)]) for q in range(self.n)}
        E = {q: tup(self.fixed[('E', q)]) for q in range(self.n)}
        P = {q: tup(f) for q, f in self.pins.items()}
        CAP = {q: tup(f) for q, f in self.caps.items()}

        def bits(x):
            while x:
                b = x & -x
                x ^= b
                yield b.bit_length() - 1
        lo, hi = {}, {}
        for g in range(N):
            A_ = list(bits(anc[g])) + [g]
            D_ = list(bits(desc[g])) + [g]
            parts = {S[q] for h in A_ for q in regs(ops[h])}
            parts |= {P[q] for h in A_ if seg[h] != 'A' for q in regs(ops[h]) if q in P}
            hp = set()
            for h in D_:
                for q in regs(ops[h]):
                    hp.add(E[q])
                    if seg[h] == 'A' and q in P:
                        hp.add(P[q])
                    if seg[h] in 'AB' and q in CAP:
                        hp.add(CAP[q])
            top = tuple(1 << k for k in range(8, -1, -1))
            for f in sorted(hp):
                top = M.meet(top, f)
            lo[('G', g)] = mask(M.join(sorted(parts)))
            hi[('G', g)] = mask(top)
        return lo, hi


# -------------------------------------------------------------------- subspaces of an interval (two enumerators)
def subspaces_closure(I, l, h, _memo={}):
    if (l, h) not in _memo:
        comp, cur = [], l
        for x in I.canonical_frame(h):
            if not (cur >> x) & 1:
                comp.append(x)
                cur = I.extend(cur, x)
        res = []
        for sub in I.small_spaces(len(comp)):
            val = l
            for b in I.elements(sub):
                x = 0
                for j, c in enumerate(comp):
                    if b >> j & 1:
                        x ^= c
                val = I.extend(val, x)
            res.append(val)
        _memo[(l, h)] = res
    return _memo[(l, h)]


def subspaces_rref(I, l, h):
    """every subspace V with l <= V <= h: l plus a reduced-echelon choice of vectors from a complement basis."""
    comp, cur = [], l
    for x in I.canonical_frame(h):
        if not (cur >> x) & 1:
            comp.append(x)
            cur = I.extend(cur, x)
    k = len(comp)
    out = set()
    for r in range(k + 1):
        for pivots in _combinations(range(k), r):
            free = [(i, j) for i, p in enumerate(pivots) for j in range(p + 1, k) if j not in pivots]
            for bits in range(1 << len(free)):
                rows = [1 << p for p in pivots]
                for b, (i, j) in enumerate(free):
                    if bits >> b & 1:
                        rows[i] |= 1 << j
                val = l
                for row in rows:
                    x = 0
                    for j in range(k):
                        if row >> j & 1:
                            x ^= comp[j]
                    val = I.extend(val, x)
                out.add(val)
    return out


def _combinations(items, r):
    items = list(items)
    if r == 0:
        yield ()
        return
    for i in range(len(items)):
        for rest in _combinations(items[i + 1:], r - 1):
            yield (items[i],) + rest


# -------------------------------------------------------------------- the exact per-register bound
def costs(C, a):
    SC = 1 << C.PREC
    cost = [0] + [int(C.child_cost(d, 73, a)[0] * SC) for d in range(1, 10)]
    if not all(Q(cost[d], SC) == C.child_cost(d, 73, a)[0] for d in range(1, 10)):
        raise ValueError('child_cost lower ends are not on the 2^-PREC grid')
    return cost, SC


def bound(W, lo, hi, a, lam=None):
    """Lower bound on the local bill at exponent a over every member and every legal frame assignment.

    lam: None (Stage 1) or {free ADD gate: integer k} with multiplier k / 2^LAMBDA_BITS on the target copy and minus
    that on the source copy, charged by dimension at the copy's entry point (k > 0) or exit point (k < 0).
    Returns (exact bill lower bound as a Fraction, total local cost numerator at scale 2^PREC)."""
    I, C = W.I, W.U.retained('ceiling.py')
    cost, SC = costs(C, a)
    SH = C.PREC - LAMBDA_BITS
    dim = I.dimension
    lam = lam or {}
    total = 0
    for q in range(W.n):
        items = []
        for i in W.on.get(q, []):
            e = W.ops[i]
            co = 0
            if e[0] == 'add' and lo[('G', i)] != hi[('G', i)]:
                co = lam.get(i, 0) * (1 if e[1] == q else -1)
            items.append((lo[('G', i)], hi[('G', i)], co))
        if q in W.pins:
            items.append((W.fixed[('P', q)], W.fixed[('P', q)], 0))
        S, E = W.fixed[('S', q)], W.fixed[('E', q)]
        cand = {S, E}
        for l, h, _ in items:
            cand.update(subspaces_closure(I, l, h))
        cand = sorted(cand, key=lambda F: F.bit_count())
        K = len(items)
        inl = [sum(1 << k for k, it in enumerate(items) if it[0] & ~V == 0) for V in cand]
        inh = [sum(1 << k for k, it in enumerate(items) if V & ~it[1] == 0) for V in cand]
        dims = [dim(V) for V in cand]
        s0, e0 = cand.index(S), cand.index(E)
        pos = [k for k in range(K) if items[k][2] > 0]
        neg = [k for k in range(K) if items[k][2] < 0]
        f = [None] * len(cand)
        f[s0] = sum(items[k][2] * dims[s0] for k in pos if inl[s0] >> k & 1) << SH
        for j in range(len(cand)):
            if j == s0:
                continue
            best = None
            for i2 in range(j):
                if f[i2] is None or dims[i2] == dims[j] or cand[i2] & ~cand[j]:
                    continue
                ent = inl[j] & ~inl[i2]
                if ent & ~inh[j]:
                    continue                      # an item's first entry would land outside its upper end
                ex = inh[i2] & ~inh[j]
                val = f[i2] + cost[dims[j] - dims[i2]]
                val += sum(items[k][2] * dims[j] for k in pos if ent >> k & 1) << SH
                val += sum(items[k][2] * dims[i2] for k in neg if ex >> k & 1) << SH
                if best is None or val < best:
                    best = val
            f[j] = best
        if f[e0] is None:
            raise ValueError('no stabbing chain for register %d' % q)
        total += f[e0] + (sum(items[k][2] * dims[e0] for k in neg if inh[e0] >> k & 1) << SH)
    idle = C.child_cost(51, 73, a)[0]
    bill = (Q(total + 8 * cost[8], SC) + Q(1646, 51) * idle) / Q(896, 9)
    return bill, total


def given_word_profile(W):
    """the paid profile of the selected word's own frames (pins charged as climbs, centre descents added)."""
    I = W.I
    prof = collections.Counter()
    for q in range(W.n):
        seq = [W.fixed[('S', q)]]
        pinned = q not in W.pins
        for i in W.on.get(q, []):
            if not pinned and W.seg[i] != 'A':
                seq.append(W.fixed[('P', q)])
                pinned = True
            seq.append(I.frame(W.ops[i][-1]))
        if not pinned:
            seq.append(W.fixed[('P', q)])
        seq.append(W.fixed[('E', q)])
        for x, y in zip(seq, seq[1:]):
            if x != y:
                if x & ~y:
                    raise ValueError('given frames are not nested on register %d' % q)
                prof[I.dimension(y) - I.dimension(x)] += 1
    prof[8] += 8
    return dict(sorted(prof.items()))
