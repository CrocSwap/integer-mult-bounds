"""Exact frame optimum of a bitE8/1+mut word whose phase-A/phase-B gate order may have been changed.

Model (the paid local profile of PR589's wlib.replay): every gate puts all of its operands on its frame; each register's
frames nest from its start to its final frame; each strict climb is one paid call of rank equal to the dimension step.
A retained total's COPY rank is the dimension of its frame when the scatter reads it; here that frame is pinned to the
base word's (so the COPY ranks and the decoder constant 63 cannot change), which pins the total's last phase-A gate to
exactly that frame. Targets stay at frame 0 until the scatter.

D (all frame 0, before any climb) and C (the literal reverse of the z-destination gates at the full frame, H4) cannot
contribute a climb other than the last climb to the full final frame; `Word` asserts both facts and drops them.

For a gate order the optimum over all frame assignments is computed exactly:
  1. forward least frames lo_g and backward greatest frames hi_g; every legal assignment has lo_g <= f_g <= hi_g, and
     the all-least assignment itself nests (so components can be enumerated with the others at any legal value);
  2. gates with lo_g != hi_g ("free") interact only when consecutive on a register, so the components of that
     relation are independent in legality and in cost;
  3. every component is enumerated exhaustively over all closed frames (catalogue or not) between its bounds.
The cost of a profile is sum_d n_d d (64/d)^z at the base word's c, which is linear in the profile; with the rank mass
fixed, a profile can raise c only if it lowers this sum (see README). Standard library only.
Prepared with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0.
"""
import gzip
import itertools
import json
from collections import Counter
from fractions import Fraction


def load(path):
    return json.load(gzip.open(path, 'rt'))


class Lattice:
    """closed frames: sets of live lines closed under rational span membership, as int masks; exact Fraction RREF"""

    def __init__(self, lines):
        self.lines = [tuple(map(Fraction, l)) for l in lines]
        self.n = len(lines)
        self.cache = {0: (0, 0)}

    def _reduce(self, basis, row):
        row = list(row)
        for piv, b in basis:
            if row[piv]:
                q = row[piv]
                row = [a - q * c for a, c in zip(row, b)]
        return row

    def close(self, mask):
        """(closed mask, dimension) of the span of the lines in mask"""
        hit = self.cache.get(mask)
        if hit is not None:
            return hit
        basis = []
        for i in range(self.n):
            if mask >> i & 1:
                row = self._reduce(basis, self.lines[i])
                piv = next((k for k, x in enumerate(row) if x), None)
                if piv is not None:
                    row = [x / row[piv] for x in row]
                    basis = [(p, [a - b[piv] * c for a, c in zip(b, row)]) for p, b in basis] + [(piv, row)]
        closed = 0
        for i in range(self.n):
            if mask >> i & 1 or not any(self._reduce(basis, self.lines[i])):
                closed |= 1 << i
        out = (closed, len(basis))
        self.cache[mask] = out
        self.cache[closed] = out
        return out

    def dim(self, mask):
        return self.close(mask)[1]


class Word:
    """phase A, scatter and phase B of a word as (frame mask, target, sources) gates; D and C checked and dropped"""

    def __init__(self, w, lat=None):
        self.w = w
        self.V = V = w['v']
        self.N = 2 * V + w['R']
        self.lat = lat or Lattice(w['lines'])
        self.fm = [sum(1 << i for i in f) for f in w['frames']]
        for m in self.fm:
            assert self.lat.close(m)[0] == m, 'catalogue frame not closed'
        self.full = max(self.fm, key=self.lat.dim)
        assert self.lat.dim(self.full) == 8
        self.start = [self.fm[f] for f in w['start']]
        self.final = [self.fm[f] for f in w['final']]
        # D: frame 0 and every operand still at frame 0 there, so D contributes no climb and no lower bound
        for f, t, ss in w['D']:
            assert self.fm[f] == 0 and all(self.start[r] == 0 for r in [t, *ss])
        # C: every gate at the full frame, every C operand ends at the full frame
        incC = set()
        for f, t, ss in w['C']:
            assert self.fm[f] == self.full
            incC.update([t, *ss])
        assert all(self.final[r] == self.full for r in incC)
        self.ret = list(w['ret'])
        A = [(self.fm[f], t, tuple(ss)) for f, t, ss in w['A']]
        B = [(self.fm[f], t, tuple(ss)) for f, t, ss in w['B']]
        cur = list(self.start)
        for f, t, ss in A:
            for r in (t, *ss):
                cur[r] = f
        self.pin = {q: cur[q] for q in self.ret}  # COPY frames of the retained totals
        self.A, self.B = A, B
        self.targets = range(V, 2 * V)
        assert not any(V <= r < 2 * V for f, t, ss in A for r in (t, *ss)), 'a target is touched in phase A'

    def base_frames(self):
        return [g[0] for g in self.A] + [g[0] for g in self.B]


def cost_of(H, z):
    return sum(n * d * (64 / d) ** z for d, n in H.items())


def optimum(word, A, B, z, want_frames=False):
    """exact optimum over all frame assignments of the gate order (A, B); A/B gates are (frame, t, sources), frames
    ignored except for reporting.  Returns None if no legal assignment exists, else a dict with the optimal profile
    (climbs plus COPY ranks), its cost and statistics."""
    lat = word.lat
    close = lat.close
    gates = [(t, ss) for f, t, ss in A] + [(t, ss) for f, t, ss in B]
    nA = len(A)
    G = len(gates)
    pin = word.pin
    # the last phase-A gate on a retained total fixes its frame at the scatter, so in every legal assignment that
    # gate sits exactly at the total's COPY frame; using this as its least frame keeps the all-least assignment legal
    lastA = {}
    for g in range(nA):
        t, ss = gates[g]
        for r in (t, *ss):
            if r in pin:
                lastA[r] = g
    pinned = {}
    for q, g in lastA.items():
        if pinned.setdefault(g, pin[q]) != pin[q]:
            return None
    # 1. forward least frames
    lo = [0] * G
    cur = list(word.start)
    for g in range(G):
        if g == nA:
            for q, m in pin.items():
                if cur[q] != m:
                    return None
        t, ss = gates[g]
        m = cur[t]
        for s in ss:
            m |= cur[s]
        m = close(m)[0]
        if g in pinned:
            if m & ~pinned[g]:
                return None
            m = pinned[g]
        lo[g] = m
        cur[t] = m
        for s in ss:
            cur[s] = m
    if G == nA:
        raise ValueError('empty phase B')
    for r in range(word.N):
        if cur[r] & ~word.final[r]:
            return None
    # backward greatest frames (an intersection of closed sets is closed)
    hi = [0] * G
    ub = list(word.final)
    for g in range(G - 1, -1, -1):
        t, ss = gates[g]
        m = ub[t]
        for s in ss:
            m &= ub[s]
        hi[g] = m
        ub[t] = m
        for s in ss:
            ub[s] = m
        if g == nA:
            for q, m2 in pin.items():
                if m2 & ~ub[q]:
                    return None
                ub[q] = m2
            for r in word.targets:
                ub[r] = 0
    for g in range(G):
        if lo[g] & ~hi[g]:
            return None
    for r in range(word.N):
        if word.start[r] & ~ub[r]:
            return None
    # per-register gate lists
    touch = [[] for _ in range(word.N)]
    for g, (t, ss) in enumerate(gates):
        touch[t].append(g)
        for s in ss:
            touch[s].append(g)
    free = [g for g in range(G) if lo[g] != hi[g]]
    frames = list(lo)

    def chain(r, fr):
        """(Counter of climbs, legal) of register r under frames fr"""
        c = word.start[r]
        H = Counter()
        crossed = r not in pin
        for g in touch[r]:
            if not crossed and g >= nA:
                if c != pin[r]:
                    return None
                crossed = True
            m = fr[g]
            if m != c:
                if c & ~m:
                    return None
                H[lat.dim(m) - lat.dim(c)] += 1
                c = m
        if not crossed and c != pin[r]:
            return None
        m = word.final[r]
        if m != c:
            if c & ~m:
                return None
            H[lat.dim(m) - lat.dim(c)] += 1
        return H

    # 2. components of free gates (consecutive on a register)
    parent = {g: g for g in free}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    fs = set(free)
    for r in range(word.N):
        prev = None
        for g in touch[r]:
            if g in fs and prev in fs:
                a, b = find(prev), find(g)
                if a != b:
                    parent[a] = b
            prev = g
    comps = {}
    for g in free:
        comps.setdefault(find(g), []).append(g)
    # 3. exhaustive enumeration per component
    enumerated = illegal = 0
    for members in comps.values():
        opts = []
        for g in members:
            seen, todo = {lo[g]}, [lo[g]]
            while todo:
                m = todo.pop()
                rest = hi[g] & ~m
                while rest:
                    b = rest & -rest
                    rest ^= b
                    n = close(m | b)[0]
                    if n & ~hi[g] == 0 and n not in seen:
                        seen.add(n)
                        todo.append(n)
            opts.append(sorted(seen))
        regs = sorted({r for g in members for r in (gates[g][0], *gates[g][1])})
        best = None
        for combo in itertools.product(*opts):
            fr = frames
            saved = [fr[g] for g in members]
            for g, m in zip(members, combo):
                fr[g] = m
            enumerated += 1
            H = Counter()
            ok = True
            for r in regs:
                h = chain(r, fr)
                if h is None:
                    ok = False
                    break
                H.update(h)
            if ok:
                c = cost_of(H, z)
                key = (c, combo)
                if best is None or key < best:
                    best = key
            else:
                illegal += 1
            for g, m in zip(members, saved):
                fr[g] = m
        if best is None:
            return None
        for g, m in zip(members, best[1]):
            frames[g] = m
    # total profile under the optimal frames
    H = Counter()
    for r in range(word.N):
        h = chain(r, frames)
        if h is None:
            return None
        H.update(h)
    for q in word.ret:
        H[lat.dim(pin[q])] += 1  # COPY ranks
    out = dict(profile=dict(sorted(H.items())), cost=cost_of(H, z), free=len(free), components=len(comps),
               component_sizes=dict(Counter(len(v) for v in comps.values())), enumerated=enumerated, illegal=illegal,
               mass=sum(d * n for d, n in H.items()))
    if want_frames:
        out['frames'] = frames
    return out


def fixed_profile(word, A, B):
    """paid profile of the given frames (no optimisation); None if they do not nest"""
    lat = word.lat
    gates = [(f, t, ss) for f, t, ss in A] + [(f, t, ss) for f, t, ss in B]
    nA = len(A)
    cur = list(word.start)
    H = Counter()
    for g, (f, t, ss) in enumerate(gates):
        if g == nA:
            for q, m in word.pin.items():
                if cur[q] != m:
                    return None
        for r in (t, *ss):
            c = cur[r]
            if c != f:
                if c & ~f:
                    return None
                H[lat.dim(f) - lat.dim(c)] += 1
                cur[r] = f
    for r in range(word.N):
        c, m = cur[r], word.final[r]
        if c != m:
            if c & ~m:
                return None
            H[lat.dim(m) - lat.dim(c)] += 1
    for q in word.ret:
        H[lat.dim(word.pin[q])] += 1
    return dict(sorted(H.items()))
