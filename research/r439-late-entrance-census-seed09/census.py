# SPDX-License-Identifier: Apache-2.0
"""Engine 1: late-compensated helper entrances on an R439 bit word (bitE8/1+mut), standard library only.

Notation (README "Definitions"): sources 0..v-1, targets v..2v-1 (target t = register v+t), helpers 2v..
(helper j = register 2v+j). A value is an int bitmask over the n = 2v+R dirty columns. Frames are closed
label lists, so containment is label-mask inclusion (checked against rational containment by Engine 2).
sigma = the cut right after the scatter; tau = number of B gates applied.
"""
import itertools
from collections import Counter, defaultdict
from fractions import Fraction as Q


# ------------------------------------------------------------------------------------------------ rationals
def rref(rows, ncol=8):
    m = [[Q(x) for x in r] for r in rows]
    rk = 0
    piv = []
    for c in range(ncol):
        p = next((i for i in range(rk, len(m)) if m[i][c] != 0), None)
        if p is None:
            continue
        m[rk], m[p] = m[p], m[rk]
        pv = m[rk][c]
        m[rk] = [a / pv for a in m[rk]]
        for i in range(len(m)):
            if i != rk and m[i][c] != 0:
                f = m[i][c]
                m[i] = [a - f * b for a, b in zip(m[i], m[rk])]
        piv.append(c)
        rk += 1
    return tuple(tuple(r) for r in m[:rk]), piv


def nullspace(rows, ncol=8):
    b, piv = rref(rows, ncol) if rows else ((), [])
    out = []
    for fc in (c for c in range(ncol) if c not in piv):
        vec = [Q(0)] * ncol
        vec[fc] = Q(1)
        for r, pc in zip(b, piv):
            vec[pc] = -r[fc]
        out.append(tuple(vec))
    return out


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def popcount(x):
    return bin(x).count('1')


# ------------------------------------------------------------------------------------------------ the word
class Word:
    def __init__(self, w):
        self.w = w
        self.v, self.R = w['v'], w['R']
        self.n = 2 * self.v + self.R
        self.lines = w['lines']
        self.mask = [sum(1 << i for i in f) for f in w['frames']]
        self.dim = [len(rref([self.lines[i] for i in f])[0]) if f else 0 for f in w['frames']]
        self.tperp = [w['final'][self.v + t] for t in range(self.v)]

    def le(self, a, b):
        """frame a inside frame b (closed frames: label inclusion)."""
        return self.mask[a] & self.mask[b] == self.mask[a]

    def raw(self):
        """Raw replay of A, scatter, B from val[r] = 1 << r (no D, no C).

        Returns the sigma state, the snapshots, the end state and K (K[t] = helper bits of raw y_t)."""
        v, R, n, w = self.v, self.R, self.n, self.w
        val = [1 << r for r in range(n)]
        cur = list(w['start'])
        for f, d, ss in w['A']:
            for r in (d, *ss):
                cur[r] = f
            a = 0
            for s in ss:
                a ^= val[s]
            val[d] ^= a
        snaps = [val[q] for q in w['ret']]
        for t, row in enumerate(w['scatter']):
            for k in row:
                val[v + t] ^= snaps[k]
        if not all(self.dim[cur[v + t]] == 0 for t in range(v)):
            raise ValueError('a target leaves frame 0 before the scatter')
        sigma_val, sigma_cur = list(val), list(cur)
        for f, d, ss in w['B']:
            a = 0
            for s in ss:
                a ^= val[s]
            val[d] ^= a
        K = [(val[v + t] >> (2 * v)) & ((1 << R) - 1) for t in range(v)]
        if not all(val[v + t] & ((1 << (2 * v)) - 1) == (1 << (v + t)) | (1 << t) for t in range(v)):
            raise ValueError('raw word is not y -> y + x + K h (V = I, J = I)')
        return dict(sigma_val=sigma_val, sigma_cur=sigma_cur, snaps=snaps, end_val=val, K=K)

    def first_contact(self):
        """frame of the first A/B gate touching each helper (all helpers are touched in A)."""
        v = self.v
        first = {}
        for sec in ('A', 'B'):
            for f, d, ss in self.w[sec]:
                for r in (d, *ss):
                    if r >= 2 * v and r not in first:
                        first[r] = (f, sec)
        if len(first) != self.R or any(sec != 'A' for _, sec in first.values()):
            raise ValueError('every helper must be first touched in A')
        return {r: f for r, (f, _) in first.items()}

    def next_frames(self):
        """next(r, tau): frame of r's first gate with index >= tau in B ++ C, else final[r]."""
        nl = defaultdict(list)
        for i, (f, d, ss) in enumerate(self.w['B'] + self.w['C']):
            for r in (d, *ss):
                nl[r].append((i, f))
        final = self.w['final']

        def nxt(r, tau):
            for i, f in nl.get(r, ()):
                if i >= tau:
                    return f
            return final[r]
        return nxt


# ------------------------------------------------------------------------------------------------ closure L
def closure(word, first):
    """distinct first-contact spaces, their nonzero pairwise intersections (#1253's L) and I(V)."""
    v, R = word.v, word.R
    spaces = {}
    for j in range(R):
        f = first[2 * v + j]
        key = rref([word.lines[i] for i in word.w['frames'][f]])[0]
        spaces.setdefault(key, []).append(2 * v + j)
    gens = list(spaces)
    planes = [g for g in gens if len(g) == 2]
    L = set(gens)
    meets = 0
    for a, b in itertools.combinations(planes, 2):
        inter = nullspace(nullspace(list(a)) + nullspace(list(b)))
        if inter:
            if len(inter) != 1:
                raise ValueError('two distinct planes meet in more than a line')
            meets += 1
            L.add(rref(inter)[0])

    def inside(V, F):
        ann = nullspace(list(F))
        return all(dot(u, a) == 0 for u in V for a in ann)
    elig = {V: sorted(r for key, regs in spaces.items() if inside(V, key) for r in regs) for V in L}
    return dict(L=L, elig=elig, planes=len(planes), lines=len(gens) - len(planes), plane_pairs=len(planes) * (len(planes) - 1) // 2,
                meets=meets)


def supports(elig):
    """every nonzero c inside some I(V): {frozenset of registers: one V}."""
    out = {}
    for V, I in elig.items():
        for k in range(1, len(I) + 1):
            for S in itertools.combinations(I, k):
                out.setdefault(frozenset(S), V)
    return out


# ------------------------------------------------------------------------------------------------ spans
class Span:
    """F2 echelon basis on int bitmasks keyed by leading bit."""
    __slots__ = ('b',)

    def __init__(self):
        self.b = {}

    def add(self, x):
        b = self.b
        while x:
            h = x.bit_length() - 1
            if h in b:
                x ^= b[h]
            else:
                b[h] = x
                return True
        return False


def rotate(word, y_free=True):
    """dirt to the low R bits, x (and y unless y_free) above: echelon vectors led by a dirt bit are x/y-free."""
    v, R = word.v, word.R
    keep = (1 << v) - 1 if y_free else (1 << (2 * v)) - 1
    return lambda x: (x >> (2 * v)) | ((x & keep) << R)


def dirt_basis(span, R):
    return sorted((x for h, x in span.b.items() if h < R), reverse=True)


def canonical(vectors):
    """reduced echelon form of a set of bitmasks (for exact comparison between engines)."""
    piv = {}
    for x in vectors:
        while x:
            h = x.bit_length() - 1
            if h in piv:
                x ^= piv[h]
            else:
                for k in list(piv):
                    if (piv[k] >> h) & 1:
                        piv[k] ^= x
                piv[h] = x
                break
    out = {}
    for h in sorted(piv):
        x = piv[h]
        for k in sorted(piv):
            if k != h and (x >> k) & 1 and k in out:
                x ^= out[k]
        out[h] = x
    return sorted(out.values(), reverse=True)


def W_fav(word, st, y_free=True):
    """LC-fav: generators at sigma = registers (other than t) whose frame lies in t-perp, plus the snapshots."""
    v, R, n = word.v, word.R, word.n
    rot = rotate(word, y_free)
    out = []
    for t in range(v):
        S = Span()
        for c in st['snaps']:
            S.add(rot(c))
        for r in range(n):
            if r != v + t and word.le(st['sigma_cur'][r], word.tperp[t]):
                S.add(rot(st['sigma_val'][r]))
        out.append(dirt_basis(S, R))
    return out


def W_sweep(word, st, mode, y_free=True, next_override=None):
    """Union over tau in [0, |B|] of the readable values, for mode 'fav', 'strict' (scout prototype: carrier frame in
    t's next frame, no carrier check) or 'A6' (some F with cur_t + cur_r <= F <= next_t and next_r)."""
    v, R, n = word.v, word.R, word.n
    rot = rotate(word, y_free)
    base_next = word.next_frames()
    override = next_override or {}

    def nxt(r, tau):
        return override[r] if r in override else base_next(r, tau)
    val, cur = list(st['sigma_val']), list(st['sigma_cur'])
    spans = [Span() for _ in range(v)]
    for S in spans:
        for c in st['snaps']:
            S.add(rot(c))

    def legal(t, r, tau):
        if mode == 'fav':
            return word.le(cur[r], word.tperp[t])
        nt = nxt(v + t, tau)
        if mode == 'strict':
            return word.le(cur[r], nt)
        return word.le(cur[r], nt) and word.le(cur[v + t], nxt(r, tau))

    for t in range(v):
        for r in range(n):
            if r != v + t and legal(t, r, 0):
                spans[t].add(rot(val[r]))
    for i, (f, d, ss) in enumerate(word.w['B']):
        ops = (d, *ss)
        for r in ops:
            cur[r] = f
        a = 0
        for s in ss:
            a ^= val[s]
        val[d] ^= a
        touched_targets = {r - v for r in ops if v <= r < 2 * v}
        for t in range(v):
            regs = range(n) if t in touched_targets else ops
            for r in regs:
                if r != v + t and legal(t, r, i + 1):
                    spans[t].add(rot(val[r]))
    return [dirt_basis(S, R) for S in spans]


# ------------------------------------------------------------------------------------------------ census
def response(K, cmask, donors=0):
    return [t for t in range(len(K)) if (popcount(K[t] & cmask) + ((donors >> t) & 1)) & 1]


def admits(W, T, cmask):
    return all(any(popcount(u & cmask) & 1 for u in W[t]) for t in T)


def census(word, K, W, sup):
    """[(registers, |T|)] admitted by the per-target odd-parity test, kernel pairs (T empty) included."""
    v = word.v
    out = []
    for S in sup:
        cm = sum(1 << (r - 2 * v) for r in S)
        T = response(K, cm)
        if admits(W, T, cm):
            out.append((tuple(sorted(S)), len(T)))
    return sorted(out, key=lambda a: (len(a[0]), a[0]))


def coverage(word, K, W):
    v, R = word.v, word.R
    return sum(1 for t in range(v) for j in range(R) if (K[t] >> j) & 1 and any((u >> j) & 1 for u in W[t]))


def relax(word, K, W, elig):
    """sound linear superset per class V: drop rows t whose W_t meets I(V); report the kernel of the rest."""
    v = word.v
    out = {}
    for V, I in elig.items():
        Im = sum(1 << (r - 2 * v) for r in I)
        rows = [t for t in range(v) if not any(u & Im for u in W[t])]
        piv = {}
        kern = []
        for a, r in enumerate(I):
            col = sum(((K[t] >> (r - 2 * v)) & 1) << k for k, t in enumerate(rows))
            comb = 1 << a
            x = col
            while x:
                h = x.bit_length() - 1
                if h in piv:
                    x ^= piv[h][0]
                    comb ^= piv[h][1]
                else:
                    piv[h] = (x, comb)
                    break
            if not x:
                kern.append(tuple(I[b] for b in range(len(I)) if (comb >> b) & 1))
        if kern:
            out[V] = dict(kernel=kern, rows_kept=len(rows))
    return out


def donors(word, K, W, elig):
    """source donors x_s ^= p at the entrance frame (line_s inside V); response K c + 1_{D_S}.
    'placeable' counts the donor sets whose span E_min = span(lines of D_S) lies inside every donor's first A frame
    (each donor must sit at the entrance frame before A without descending)."""
    v = word.v
    lab = {s: rref([word.lines[s]])[0] for s in range(v)}
    first_src = {}
    for f, d, ss in word.w['A']:
        for r in (d, *ss):
            if r < v and r not in first_src:
                first_src[r] = rref([word.lines[i] for i in word.w['frames'][f]])[0]

    def inside(V, F):
        ann = nullspace(list(F))
        return all(dot(u, a) == 0 for u in V for a in ann)
    checked, placeable, kernel, late = 0, 0, [], []
    for V, I in elig.items():
        srcs = [s for s in range(v) if inside(lab[s], V)]
        for k in range(1, len(srcs) + 1):
            for DS in itertools.combinations(srcs, k):
                xs = sum(1 << s for s in DS)
                emin = rref([word.lines[s] for s in DS])[0]
                legal = all(inside(emin, first_src[s]) for s in DS)
                for kk in range(1, len(I) + 1):
                    for J in itertools.combinations(I, kk):
                        checked += 1
                        placeable += legal
                        cm = sum(1 << (r - 2 * v) for r in J)
                        T = response(K, cm, xs)
                        if not T:
                            kernel.append((DS, J))
                        elif admits(W, T, cm):
                            late.append((DS, J, len(T)))
    return dict(checked=checked, placeable=placeable, kernel=kernel, late=late)


# ------------------------------------------------------------------------------------------------ A6R (storage relays)
def a6r_coverable(word, st, J, only_targets=None, relays=True):
    """A6 plus frame-tagged storage relays (relay restoration ignored: a superset). Values are projected to
    (pivot parity on J, x, y); target t is coverable when its stores span a vector with pivot 1 and x = y = 0.
    only_targets restricts which targets may receive inserted reads (the A6R(T-only) variant)."""
    v, R, n = word.v, word.R, word.n
    w = word.w
    nxt_frame = word.next_frames()
    cmJ = sum(1 << (r - 2 * v) for r in J)
    xym = (1 << (2 * v)) - 1

    def proj(x):
        return (popcount((x >> (2 * v)) & cmJ) & 1) | ((x & xym) << 1)
    val, cur = list(st['sigma_val']), list(st['sigma_cur'])
    store = [dict() for _ in range(v)]          # tag mask -> (Span, ordered list)
    total = [Span() for _ in range(v)]
    merged = {}
    cm = [word.mask[c] for c in cur]
    nr = [0] * n

    def sub(a, b):
        return a & b == a

    def put(t, tag, x):
        sp = store[t].get(tag)
        if sp is None:
            sp = store[t][tag] = (Span(), [])
        if sp[0].add(x):
            sp[1].append(x)
            total[t].add(x)
            return True
        return False
    for t in range(v):
        for c in st['snaps']:
            put(t, 0, proj(c))

    def allowed(t):
        return only_targets is None or (v + t) in only_targets

    def relay(t, u, work):
        if not (allowed(t) and allowed(u)):
            return
        got = False
        for tag, (sp, order) in list(store[u].items()):
            key = (t, u, tag)
            m = merged.get(key, 0)
            if m >= len(order):
                continue
            F = cm[v + t] | cm[v + u] | tag
            if sub(F, nr[v + t]) and sub(F, nr[v + u]):
                for x in order[m:]:
                    got |= put(t, F, x)
                merged[key] = len(order)
        if got:
            work.add(t)

    def step(tau, changed):
        regs = range(n) if changed is None else changed
        for r in regs:
            cm[r] = word.mask[cur[r]]
            nr[r] = word.mask[nxt_frame(r, tau)]
        work = set()
        for t in range(v):
            if not allowed(t):
                continue
            rr = range(n) if (changed is None or (v + t) in changed) else changed
            for r in rr:
                if r == v + t:
                    continue
                F = cm[v + t] | cm[r]
                if sub(F, nr[v + t]) and sub(F, nr[r]):
                    if put(t, F, proj(val[r])):
                        work.add(t)
        if not relays:
            return
        for x in [r - v for r in regs if v <= r < 2 * v]:
            for y in range(v):
                if y != x:
                    relay(x, y, work)
                    relay(y, x, work)
        while work:
            u = work.pop()
            for t in range(v):
                if t != u:
                    relay(t, u, work)
    step(0, None)
    for i, (f, d, ss) in enumerate(w['B']):
        ops = (d, *ss)
        for r in ops:
            cur[r] = f
        a = 0
        for s in ss:
            a ^= val[s]
        val[d] ^= a
        step(i + 1, set(ops))
    return [v + t for t in range(v) if 0 in total[t].b]


def dims(W):
    return dict(sorted(Counter(len(x) for x in W).items()))
