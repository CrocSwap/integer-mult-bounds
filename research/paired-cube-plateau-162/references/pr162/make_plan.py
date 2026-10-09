#!/usr/bin/env python3
"""Regenerate data/{arcs,frames,pairs}.json: how the extended matching and its physical layer were found.

Stdlib only, deterministic, about one minute.  verify.py does not use this file: it checks the frozen plan with the
repository's own checkers, so the certified value does not depend on how the plan was found and no optimality is
claimed.

  arcs    #161's frozen carrier arcs, then every further arc x -> u (x's control register keeps one of x's operands
          and serves another use u of that operand) that keeps the generalized dependency graph acyclic and keeps
          every value span inside its full backward-intersection frame.  Candidates are tried once, in node order.
  frames  per-operation frame descent as in #131/#155: an operation's common frame may be any space between the
          span of its two roles' previous frames (and its value span) and the intersection of their next frames.
          The rank cost is concave in the frame dimension, so one of the two ends is always best.
  pairs   every gauged role takes the slot of a dead, ungauged, non-root donor whose last frame can be placed
          inside the gauge (#124), with the old-value read immediately before the role's first operation (#143).
          Greedy by first-order saving; a pair that would break an ascending target chain is dropped.
"""
import functools
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cxlinks  # noqa: E402
from cxlinks import basis, perp, contained, ROOT  # noqa: E402

H = 22


@functools.lru_cache(maxsize=None)
def join(A, B):
    if A == B or not B: return A
    if not A: return B
    return basis(A + B)


@functools.lru_cache(maxsize=None)
def ortho(A): return perp(A, H)


@functools.lru_cache(maxsize=None)
def meet(A, B): return A if A == B else ortho(basis(ortho(A) + ortho(B)))


@functools.lru_cache(maxsize=None)
def inside(A, B): return contained(A, B)


@functools.lru_cache(maxsize=None)
def orthogonal(S, A): return all((s & a).bit_count() % 2 == 0 for s in S for a in A)


def cost(r, m): return r * math.log(m / r) if r else 0.0


# ------------------------------------------------------------------------------------------------ extended arcs
def extended_arcs(g, frozen):
    """Greedy extension of the frozen arcs.  gspan[x]: span of every value that reaches x through DAG or arc edges;
    gann[x]: annihilator of the intersection of every root frame reachable from x.  An arc x -> t is legal iff
    gspan[x] is orthogonal to gann[t] and t does not reach x."""
    h = g['h']; inputs = g['inputs']
    args = [None] + [None if a is None else [x + 1 for x in a] for a in g['args']]
    roots = [dict(r, node=r['node'] + 1) for r in g['roots']]
    v, n = len(inputs), len(args)
    spans = [()] * n
    for i, u in enumerate(inputs): spans[i + 1] = (u,)
    for x in range(v + 1, n): spans[x] = basis(spans[args[x][0]] + spans[args[x][1]])
    rann = [perp(spans[r['node']], h) if r.get('kind', 'side') == 'center' else basis(inputs[t] for t in r['targets'])
            for r in roots]
    active = set(range(1, v + 1)); todo = [r['node'] for r in roots]
    while todo:
        x = todo.pop()
        if x in active: continue
        active.add(x)
        if args[x]: todo.extend(args[x])
    succ = [set() for _ in args]; pred = [set() for _ in args]; direct = [[] for _ in args]
    uses = defaultdict(list)
    for x in sorted(active):
        if args[x]:
            for j, y in enumerate(args[x]): succ[y].add(x); pred[x].add(y); uses[y].append(2 * x + j)
    for j, r in enumerate(roots): direct[r['node']].extend(rann[j]); uses[r['node']].append((1 << 31) | j)
    gann = [None] * n; gspan = list(spans)
    for x in sorted(active, reverse=True): gann[x] = basis(direct[x] + [z for y in succ[x] for z in gann[y]])
    plain = list(gann)                                       # DAG-only intersections, for the candidate screen
    ancestors = {}
    def above(x):
        if x not in ancestors:
            seen = set(); stack = [x]
            while stack:
                y = stack.pop()
                if args[y]:
                    for z in args[y]:
                        if z not in seen: seen.add(z); stack.append(z)
            ancestors[x] = seen
        return ancestors[x]
    arcs = {}; used = set()
    def value(code): return roots[code & 0x7fffffff]['node'] if code >> 31 else args[code // 2][code & 1]
    def add(x, code, check):
        t = None if code >> 31 else code // 2
        At = rann[code & 0x7fffffff] if t is None else gann[t]
        if check:
            if not orthogonal(gspan[x], At): return False
            if t is not None:
                stack = [t]; seen = {t}
                while stack:
                    y = stack.pop()
                    if y == x: return False
                    for z in succ[y]:
                        if z not in seen: seen.add(z); stack.append(z)
        arcs[x] = code; used.add(code)
        work = [(x, At)]
        while work:
            y, extra = work.pop(); new = join(gann[y], extra)
            if new == gann[y]: continue
            gann[y] = new
            for z in pred[y]: work.append((z, new))
        if t is not None:
            succ[x].add(t); pred[t].add(x); work = [(t, gspan[x])]
            while work:
                y, extra = work.pop(); new = join(gspan[y], extra)
                if new == gspan[y]: continue
                gspan[y] = new
                for z in succ[y]: work.append((z, new))
        return True
    for x, code in frozen: assert add(x, code, True), ('frozen arc rejected', x, code)
    for x in sorted(active):
        if not args[x]: continue
        for j, y in enumerate(args[x]):
            other = args[x][1 - j]
            for code in uses[y]:
                if code == 2 * x + j or x in arcs or code in used: continue
                if code >> 31: screen = rann[code & 0x7fffffff]
                else:
                    t = code // 2
                    if t < x and t in above(x): continue
                    screen = plain[t]
                if not orthogonal(spans[other], screen): continue
                if sum(1 for u in uses[value(code)] if u not in used) <= 1: continue    # every value keeps a free use
                add(x, code, True)
    return sorted([x, code] for x, code in arcs.items())


# ------------------------------------------------------------------------------------------------ physical layer
class Layer:
    def __init__(self, g, witness, word, record):
        self.h = h = g['h']; self.v = g['v']; self.R = record['R']; self.m = 3 * h
        self.full = basis(1 << i for i in range(h))
        args = [None] + [None if a is None else (a[0] + 1, a[1] + 1) for a in g['args']]; inputs = g['inputs']
        roots = [dict(r, node=r['node'] + 1) for r in g['roots']]
        ann = witness['annihilators']; self.ops = ops = [tuple(o) for o in word['ops']]
        phase1 = sorted(word['phase1']); self.pset = pset = set(phase1)
        rest = [i for i in range(len(ops)) if i not in pset]
        self.position = {i: k for k, i in enumerate(phase1 + rest)}
        sources = {int(x): s for x, s in word['sources'].items()}
        spans = [()] * len(args)
        for x in range(1, len(args)):
            spans[x] = (inputs[x - 1],) if args[x] is None else basis(spans[args[x][0]] + spans[args[x][1]])
        self.spans = spans
        self.default = [ortho(tuple(ann[x])) for _, _, x in ops]; self.frames = list(self.default)
        self.start = [()] * self.R
        for x, s in sources.items(): self.start[s] = (inputs[x - 1],)
        self.gauge = {}
        for z in word['selected']:
            self.gauge[z['role']] = ortho(tuple(z['annihilator'])); self.start[z['role']] = self.gauge[z['role']]
        self.selected = word['selected']
        self.rootframe = {}
        for r, s in zip(roots, word['rootroles']):
            self.rootframe[s] = spans[r['node']] if r['kind'] == 'center' else ortho(basis(inputs[t] for t in r['targets']))
        self.role_ops = defaultdict(list)
        for i, (a, b, _) in enumerate(ops): self.role_ops[a].append(i); self.role_ops[b].append(i)
        self.idx = {(s, i): k for s, l in self.role_ops.items() for k, i in enumerate(l)}
        self.first = {s: l[0] for s, l in self.role_ops.items()}; self.last = {s: l[-1] for s, l in self.role_ops.items()}
        self.pairs = []; self.donors = {}

    def set_pairs(self, pairs): self.pairs = list(pairs); self.donors = dict(pairs)

    def prev(self, s, i):
        k = self.idx[s, i]
        return self.frames[self.role_ops[s][k - 1]] if k else self.start[s]

    def next(self, s, i):
        l = self.role_ops[s]; k = self.idx[s, i]
        if k + 1 < len(l): return self.frames[l[k + 1]]
        if s in self.rootframe: return self.rootframe[s]
        if s in self.donors: return self.gauge[self.donors[s]]
        return self.full

    def local(self, i, F):
        a, b, _ = self.ops[i]; d = len(F)
        return sum(cost(d - len(self.prev(s, i)), self.m) + cost(len(self.next(s, i)) - d, self.m) for s in (a, b))

    def descend(self, seed=1, passes=10):
        rng = random.Random(seed)
        for _ in range(passes):
            order = list(range(len(self.ops))); rng.shuffle(order); moved = 0
            for i in order:
                a, b, x = self.ops[i]
                low = join(join(self.prev(a, i), self.prev(b, i)), self.spans[x]); high = meet(self.next(a, i), self.next(b, i))
                cur = self.frames[i]
                if low == high:
                    if cur != low: self.frames[i] = low; moved += 1
                    continue
                cl, ch = self.local(i, low), self.local(i, high)
                if min(cl, ch) < self.local(i, cur) - 1e-9: self.frames[i] = low if cl < ch - 1e-9 else high; moved += 1
            if not moved: break

    def pair(self):
        """Greedy pairing by first-order saving; returns (pairs, fitted last frames)."""
        m = self.m; by_gauge = defaultdict(list)
        for b, sigma in self.gauge.items(): by_gauge[sigma].append(b)
        for sigma in by_gauge: by_gauge[sigma].sort(key=lambda b: self.position[self.first[b]])
        edges = []
        for a in range(self.R):
            if a in self.gauge or a in self.rootframe or a not in self.last: continue
            i = self.last[a]; aa, bb, x = self.ops[i]; other = bb if aa == a else aa
            low = join(join(self.prev(a, i), self.prev(other, i)), self.spans[x])
            cap = self.next(other, i); current = self.local(i, self.frames[i])
            for sigma in by_gauge:
                if len(low) > len(sigma) or not inside(low, sigma): continue
                best = None
                for F in (low, meet(cap, sigma)):
                    d = len(F)
                    c = (cost(d - len(self.prev(a, i)), m) + cost(len(sigma) - d, m) +
                         cost(d - len(self.prev(other, i)), m) + cost(len(cap) - d, m))
                    if best is None or c < best[0]: best = (c, F)
                saving = current + cost(3 * len(sigma), m) / 3.0 - best[0]
                if saving > 1e-9: edges.append((saving, a, sigma, best[1]))
        edges.sort(key=lambda e: -e[0])
        taken = set(); free = {sigma: list(bs) for sigma, bs in by_gauge.items()}; pairs = []; fit = {}
        for _, a, sigma, F in edges:
            if a in taken or not free[sigma]: continue
            death = self.position[self.last[a]]
            later = [b for b in free[sigma] if self.position[self.first[b]] > death]
            if not later: continue
            b = later[0]; free[sigma].remove(b); taken.add(a); pairs.append((a, b)); fit[a] = F
        return pairs, fit

    def chain_safe(self, pairs):
        """Drop recipients whose late read would break an ascending target chain."""
        cut = len(self.pset); pairs = list(pairs)
        while True:
            late = {b for _, b in pairs}
            when = {z['role']: ((self.position[self.first[z['role']]] if z['role'] in late else cut), k)
                    for k, z in enumerate(reversed(self.selected))}
            current = [self.full] * self.v; bad = set()
            for z in sorted(self.selected, key=lambda z: when[z['role']]):
                A = tuple(z['annihilator'])
                if all(inside(A, current[t]) for t in z['targets']):
                    for t in z['targets']: current[t] = A
                else: bad.add(z['role'])
            bad &= late
            if not bad: return pairs
            pairs = [(a, b) for a, b in pairs if b not in bad]

    def build(self, rounds=3):
        self.descend()
        for _ in range(rounds):
            self.set_pairs([])
            pairs, fit = self.pair(); pairs = self.chain_safe(pairs); self.set_pairs(pairs)
            for a, _ in pairs: self.frames[self.last[a]] = fit[a]
            self.descend()

    def export(self):
        frames = [[i, list(F)] for i, F in enumerate(self.frames) if F != self.default[i]]
        # scripts/paired_cube_physical.py re-reads the LAST late recipient at the phase cut as a negative control,
        # so the last pair must have a donor that dies after the cut
        order = sorted(self.pairs, key=lambda ab: (self.last[ab[0]] not in self.pset, self.position[self.last[ab[0]]]))
        return frames, [[a, b, self.first[b]] for a, b in order]


def dump(path, obj): path.write_text(json.dumps(obj, separators=(',', ':')) + '\n')


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / 'data'
    out.mkdir(parents=True, exist_ok=True)
    g = cxlinks.graph()
    frozen = json.loads((ROOT / 'references/paired-cube/selected-module/matching-arcs.json').read_text())
    arcs = extended_arcs(g, [tuple(a) for a in frozen])
    baseline, witness, record, word = cxlinks.word(g, arcs)
    layer = Layer(g, witness, word, record); layer.build()
    frames, pairs = layer.export()
    dump(out / 'arcs.json', arcs); dump(out / 'frames.json', dict(frames=frames)); dump(out / 'pairs.json', dict(pairs=pairs))
    print('arcs %d (frozen %d), moved operation frames %d, pairs %d -> %s' % (len(arcs), len(frozen), len(frames), len(pairs), out))


if __name__ == '__main__':
    main()
