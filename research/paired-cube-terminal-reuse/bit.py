#!/usr/bin/env python3
"""Exact frame descent and compensated birth cuts on the paired-cube bit word.

The virtual scalar word, selected gauge frames, copied centres, source-register
partner mixer and all root read times remain fixed.  Explicit disjoint aliases
reuse dead ungauged roles at a gauged recipient's birth, with its old-value
correction immediately before first use.  Every frame and handoff is checked
over the rationals and must be nondegenerate for G = I - J/9.  The complete
physical chain ledger includes every handoff and every remaining gauge tail.

The endpoint and flat-component search follows the parallel complex-frame
experiment in this directory.  The search is numerical; the emitted witness,
exact frame check and complete F2 basis replay do not rely on that heuristic.
The bit word and exact checker are eumemic's PR157/PR161 construction.  The
compensated birth-cut method follows jamesyc's PR124, with late compensation
as in PR143 and the PR157 complex verifier. Original source notices remain.
Substantial OpenAI Codex assistance. Apache-2.0.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'research/paired-cube-bit/out'
sys.path.insert(0, str(ROOT / 'research/paired-cube-bit'))
from check_paired_cube_bit import Checker, Fail, need, kernel, reduce_rows, dot

if sys.flags.optimize:
    raise ValueError('Run without -O')


def canonical(rows, h):
    """Primitive integer RREF, with sorted pivot columns."""
    rr, pp = reduce_rows(rows, h)
    return tuple(tuple(r) for _, r in sorted(zip(pp, rr)))


def encoded(H):
    return {str(r): n for r, n in sorted(H.items()) if r and n}


def numerical_root(H, W, m):
    lo, hi = 0., .1
    for _ in range(70):
        mid = (lo + hi) / 2
        if math.fsum(n*r*math.exp(mid*math.log(m/r)) for r, n in H.items()) < W*m:
            lo = mid
        else:
            hi = mid
    return lo


class Frames:
    """Exact rational joins/intersections interned beside the checked frames."""
    def __init__(self, checker):
        self.c, self.h = checker, checker.h
        self.index = {}
        for s, rec in checker.fr['frames'].items():
            typ = 'a' if 'a' in rec else 'b'
            self.index[typ, tuple(tuple(r) for r in rec[typ])] = int(s)
        self.next = max(checker.A) + 1
        self.joins, self.meets, self.nd = {}, {}, {}
        self.zero = self.intern(())

    def dim(self, f):
        return self.c.dimf[f]

    def sub(self, a, b):
        return self.c.sub(a, b)

    def intern(self, rows):
        B = canonical(rows, self.h)
        d = len(B)
        if d < self.h-d:
            typ, keyrows = 'b', B
            A = None
        else:
            A = canonical(kernel(B, self.h)[0], self.h)
            typ, keyrows = 'a', A
        old = self.index.get((typ, keyrows))
        if old is not None:
            return old
        if A is None:
            A = canonical(kernel(B, self.h)[0], self.h)
        f = self.next
        self.next += 1
        self.index[typ, keyrows] = f
        self.c.A[f], self.c.B[f], self.c.dimf[f] = A, B, d
        need(len(A)+len(B) == self.h, 'new frame ranks')
        need(all(dot(a, b) == 0 for a in A for b in B), 'new frame annihilation')
        return f

    def join(self, a, b):
        if a == b or b == self.zero:
            return a
        if a == self.zero:
            return b
        if a > b:
            a, b = b, a
        key = a, b
        if key not in self.joins:
            if self.sub(a, b):
                f = b
            elif self.sub(b, a):
                f = a
            else:
                f = self.intern(tuple(self.c.B[a]) + tuple(self.c.B[b]))
            self.joins[key] = f
        return self.joins[key]

    def join_all(self, values):
        f = self.zero
        for v in values:
            f = self.join(f, v)
        return f

    def meet(self, a, b):
        if a == b:
            return a
        if a > b:
            a, b = b, a
        key = a, b
        if key not in self.meets:
            if self.sub(a, b):
                f = a
            elif self.sub(b, a):
                f = b
            else:
                f = self.intern(kernel(tuple(self.c.A[a]) + tuple(self.c.A[b]), self.h)[0])
            self.meets[key] = f
        return self.meets[key]

    def meet_all(self, values):
        f = self.c.w['full_frame']
        for v in values:
            f = self.meet(f, v)
        return f

    def nondeg(self, f):
        if f not in self.nd:
            self.nd[f] = self.c.nondeg(f)
        return self.nd[f]

    def record(self, f):
        d = self.dim(f)
        typ = 'b' if d < self.h-d else 'a'
        rows = self.c.B[f] if typ == 'b' else self.c.A[f]
        return dict(dim=d, **{typ: [list(r) for r in canonical(rows, self.h)]})


class Experiment:
    def __init__(self, baseline=BASE, p=12, checker=None, alpha=.0006, quiet=False):
        t = time.monotonic()
        self.base, self.p = baseline, p
        self.c = checker or Checker(baseline, p)
        # The inherited checker independently verifies every original rational
        # frame, node/root/source geometry, selected gauge and partner chronology.
        self.baseline_checks = self.c.run()
        _, self.target_histogram, self.source_histogram, _ = self.c.chains()
        need(encoded(self.target_histogram) == encoded(
            {int(r): n for r, n in self.c.prof['target_data_histogram'].items()}),
            'original target histogram independently recounted')
        need(encoded(self.source_histogram) == encoded(
            {int(r): n for r, n in self.c.prof['source_data_histogram'].items()}),
            'original source histogram independently recounted')
        self.g, self.w, self.record = self.c.g, self.c.w, self.c.prof
        self.h, self.v, self.R = self.c.h, self.c.v, self.record['R']
        self.T = Frames(self.c)
        self.ops = [tuple(o) for o in self.w['ops']]
        self.N = len(self.ops)
        self.base_frames = [self.c.nf[x] for _, _, x in self.ops]
        self.frames = list(self.base_frames)
        self.sources = {int(x): s for x, s in self.w['sources'].items()}
        self.gauges = {z['role']: z for z in self.w['gauges']}
        self.start = [self.T.zero] * self.R
        for x, s in self.sources.items():
            self.start[s] = self.w['source_frame'][x]
        for s, z in self.gauges.items():
            self.start[s] = z['frame']
        self.role_ops = defaultdict(list)
        for i, (a, b, _) in enumerate(self.ops):
            self.role_ops[a].append(i)
            self.role_ops[b].append(i)
        self.rootframe, self.rootkind = {}, {}
        for j, (r, s) in enumerate(zip(self.g['roots'], self.w['rootroles'])):
            need(s not in self.rootframe, 'unique root roles')
            self.rootframe[s] = self.c.rf[j]
            self.rootkind[s] = r['kind']
        self.pairs = []
        self.donors, self.merge = {}, {}
        self.deadline = {}
        phase = set(self.w['phase1'])
        self.order = self.w['phase1']+[i for i in range(self.N) if i not in phase]
        self.position = {i: t for t, i in enumerate(self.order)}
        self.build_edges()
        self.cost = [r*math.expm1(alpha*math.log(3*self.h/r)) if r else 0.
                     for r in range(self.h+1)]
        self.spans = list(self.w['source_frame'])
        plain = set(self.w['plain'])
        for x, (a, b) in enumerate(self.g['args'][self.v:], self.v):
            self.spans.append(self.c.nf[x] if x in plain else self.T.join(self.spans[a], self.spans[b]))
        self.node_spans = [self.spans[x] for _, _, x in self.ops]
        self.check()
        if not quiet:
            print(json.dumps(dict(initialized_seconds=time.monotonic()-t,
                                  baseline_root=self.profile()['numerical_root'])), flush=True)

    def build_edges(self):
        self.constants = []
        constids = {}
        def const(f):
            if f not in constids:
                constids[f] = -len(self.constants)-1
                self.constants.append(f)
            return constids[f]
        self.edges = []
        for s in range(self.R):
            if s in self.merge:
                continue
            seq = [const(self.start[s])] + self.role_ops[s]
            if s in self.rootframe:
                seq.append(const(self.rootframe[s]))
            if s in self.donors:
                b = self.donors[s]
                seq += [const(self.start[b])] + self.role_ops[b]
                if b in self.rootframe:
                    seq.append(const(self.rootframe[b]))
            seq.append(const(self.w['full_frame']))
            self.edges.extend(zip(seq, seq[1:]))
        self.inc, self.out = [[] for _ in self.ops], [[] for _ in self.ops]
        for k, (a, b) in enumerate(self.edges):
            if a >= 0:
                self.out[a].append(k)
            if b >= 0:
                self.inc[b].append(k)

    def F(self, i):
        return self.frames[i] if i >= 0 else self.constants[-i-1]

    def check(self):
        for i, f in enumerate(self.frames):
            need(self.T.sub(self.node_spans[i], f), 'operation value span at %d' % i)
            need(self.T.nondeg(f), 'nondegenerate operation frame %d' % i)
        for a, b in self.edges:
            need(self.T.sub(self.F(a), self.F(b)), 'nested physical role edge %s' % ((a, b),))

    def set_pairs(self, pairs):
        """Compensated birth cuts: dead ungauged roles feed untouched gauges."""
        self.pairs = [tuple(p) for p in pairs]
        self.donors = {a: b for a, b, _ in self.pairs}
        self.merge = {b: a for a, b, _ in self.pairs}
        self.deadline = {b: t for _, b, t in self.pairs}
        need(len(self.donors) == len(self.merge) == len(pairs), 'one-to-one bit aliases')
        need(not set(self.donors) & set(self.merge), 'disjoint bit donor/recipient sets')
        phase = set(self.w['phase1'])
        for a, b, t in self.pairs:
            need(a not in self.gauges and a not in self.rootframe, 'ungauged non-root donor')
            need(b in self.gauges and self.rootkind.get(b) == 'side', 'gauged terminal recipient')
            need(isinstance(t, int) and 0 <= t < self.N and t not in phase,
                 'recipient read after the centre phase')
            last = self.role_ops[a][-1]
            need(self.position[last] < self.position[t], 'donor dead before recipient birth')
            need(t == self.role_ops[b][0], 'recipient read at first-use deadline')
            need(self.T.sub(self.frames[last], self.start[b]), 'donor terminal frame inside gauge')
        self.recount_targets()
        self.build_edges()
        self.check()

    def recount_targets(self):
        """Target increments along actual retimed dirty reads and root reads."""
        cut = len(self.w['phase1'])
        entries = list(reversed(self.w['gauges']))
        ordered = sorted(enumerate(entries), key=lambda kz: (
            self.position[self.deadline[kz[1]['role']]] if kz[1]['role'] in self.deadline else cut,
            kz[0]))
        current = [self.T.zero]*self.v
        H = Counter()
        def read(t, f):
            need(self.T.sub(current[t], f), 'retimed bit target chain')
            r = self.T.dim(f)-self.T.dim(current[t])
            if r:
                H[r] += 1
            current[t] = f
        for _, z in ordered:
            for t in z['targets']:
                read(t, z['frame'])
        deliveries = defaultdict(list)
        for entry in self.c.k['entries']:
            deliveries[entry['deliver_after_root']].append(entry)
        for j, root in enumerate(self.g['roots']):
            if root['kind'] != 'center':
                for t in root['targets']:
                    read(t, self.c.rf[j])
            for entry in deliveries.get(j, ()):
                for t in entry['receivers']:
                    read(t, entry['deliver_frame'])
        for t, f in enumerate(current):
            need(all(dot(self.c.cov[t], b) == 0 for b in self.c.B[f]), 'final target cap')
            if self.h-1-self.T.dim(f):
                H[self.h-1-self.T.dim(f)] += 1
        need(sum(r*n for r, n in H.items()) == self.v*(self.h-1), 'retimed target rank mass')
        self.target_histogram = H

    def match_pairs(self, gauge_rank=None):
        """Maximum-weight donor set for one gauge rank, with exact edge tests.

        Matchable donor sets form a transversal matroid.  Donors are inserted
        in decreasing terminal dimension, and each insertion uses an augmenting
        path that retains all previously accepted donors.  For one fixed gauge
        rank this order maximizes the moment saving of the donor set at every
        trial exponent in (0, 1).  No global optimality across frame choices or
        distinct gauge ranks is asserted.
        """
        need(not self.pairs, 'generate matching on an unaliased word')
        gauge_rank = self.h-3 if gauge_rank is None else gauge_rank
        eligible = [s for s, z in self.gauges.items()
                    if z['dim'] == gauge_rank and self.rootkind.get(s) == 'side']
        recipients = defaultdict(list)
        for s in eligible:
            recipients[self.start[s]].append(s)
        terminal = {}
        by_frame = defaultdict(list)
        for s, uses in self.role_ops.items():
            if s not in self.gauges and s not in self.rootframe:
                f = self.frames[uses[-1]]
                if self.T.dim(f) <= gauge_rank:
                    terminal[s] = f
                    by_frame[f].append(s)
        adj = defaultdict(list)
        for f, recv in sorted(recipients.items()):
            recv.sort(key=lambda s: (self.position[self.role_ops[s][0]], s))
            last_birth = self.position[self.role_ops[recv[-1]][0]]
            for fd, donors in by_frame.items():
                avail = [s for s in donors if self.position[self.role_ops[s][-1]] < last_birth]
                # Avoid storing millions of unsuccessful search pairs in the
                # exact containment cache; accepted pairs are checked again.
                if avail and all(dot(a, b) == 0 for a in self.c.A[f] for b in self.c.B[fd]):
                    for s in avail:
                        death = self.position[self.role_ops[s][-1]]
                        adj[s].extend(b for b in recv if death < self.position[self.role_ops[b][0]])
        for s in adj:
            adj[s].sort(key=lambda b: (self.position[self.role_ops[b][0]], b))
        match_d, match_r = {}, {}
        order = sorted(adj, key=lambda s: (-self.T.dim(terminal[s]),
                                          self.position[self.role_ops[s][-1]], s))
        for start in order:
            queue, cursor, previous = [start], 0, {}
            seen = {start}
            free = None
            while cursor < len(queue) and free is None:
                a = queue[cursor]
                cursor += 1
                for b in adj[a]:
                    if b in previous:
                        continue
                    previous[b] = a
                    if b not in match_r:
                        free = b
                        break
                    nxt = match_r[b]
                    if nxt not in seen:
                        seen.add(nxt)
                        queue.append(nxt)
            if free is None:
                continue
            b = free
            while True:
                a = previous[b]
                old = match_d.get(a)
                match_d[a], match_r[b] = b, a
                if old is None:
                    break
                b = old
            if len(match_r) == len(eligible):
                break
        pairs = sorted((a, b, self.role_ops[b][0]) for a, b in match_d.items())
        self.set_pairs(pairs)
        print(json.dumps(dict(eligible_recipients=len(eligible), matched_pairs=len(pairs),
                              donor_dimensions=encoded(Counter(self.T.dim(terminal[a]) for a, _, _ in pairs)),
                              root=self.profile()['numerical_root'])), flush=True)
        return pairs

    def profile(self):
        H = Counter(self.T.dim(self.F(b))-self.T.dim(self.F(a)) for a, b in self.edges)
        H.pop(0, None)
        H[1] += len(self.sources)
        for s, kind in self.rootkind.items():
            if kind == 'center':
                H[self.T.dim(self.rootframe[s])] += 1
        Y = Counter({r: n for r, n in self.target_histogram.items() if r and n})
        src = Counter({r: n for r, n in self.source_histogram.items() if r and n})
        gauges = Counter(z['dim'] for s, z in self.gauges.items() if s not in self.merge)
        children = Counter()
        for hist in (H, Y, src):
            children.update({r: 3*n for r, n in hist.items()})
        children.update({3*r: n for r, n in gauges.items()})
        children[2] += 2*self.v
        m, W = 3*self.h, 2*self.v+self.R-len(self.pairs)
        mass = sum(r*n for r, n in children.items())
        need(W*m-mass == self.record['deficit_per_vertex'], 'complete rank deficit')
        need(all(0 < r < m and n > 0 for r, n in children.items()), 'proper children')
        return dict(h=self.h, v=self.v, R=self.R, physical_R=self.R-len(self.pairs),
                    pairs=len(self.pairs), late_pairs=len(self.pairs), m=m,
                    W_per_vertex=W, rank_per_vertex=mass, deficit_per_vertex=W*m-mass,
                    loss=self.record['loss'], local_histogram=encoded(H),
                    remaining_internal_histogram=encoded(H),
                    source_data_histogram=encoded(src), target_data_histogram=encoded(Y),
                    selected_roles=sum(gauges.values()), selected_rank_histogram=encoded(gauges),
                    logical_selected_roles=len(self.gauges), physical_gauge_histogram=encoded(gauges),
                    child_histogram=encoded(children), numerical_root=numerical_root(children, W, m),
                    changed_operation_frames=sum(a != b for a, b in zip(self.frames, self.base_frames)))

    def components(self):
        parent = list(range(self.N))
        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i
        for a, b in self.edges:
            if a >= 0 and b >= 0 and self.frames[a] == self.frames[b]:
                a, b = find(a), find(b)
                parent[max(a, b)] = min(a, b)
        groups = defaultdict(list)
        for i in range(self.N):
            groups[find(i)].append(i)
        return list(groups.values())

    def boundary(self, group):
        gs = set(group)
        inc = [k for i in group for k in self.inc[i] if self.edges[k][0] not in gs]
        out = [k for i in group for k in self.out[i] if self.edges[k][1] not in gs]
        return inc, out

    def update(self, group, mode='both'):
        old = self.frames[group[0]]
        if any(self.frames[i] != old for i in group):
            return 0., 0
        inc, out = self.boundary(group)
        low = self.T.join_all([self.node_spans[i] for i in group] +
                              [self.F(self.edges[k][0]) for k in inc])
        high = self.T.meet_all(self.F(self.edges[k][1]) for k in out)
        need(self.T.sub(low, old) and self.T.sub(old, high), 'frame search interval')
        dins = [self.T.dim(self.F(self.edges[k][0])) for k in inc]
        douts = [self.T.dim(self.F(self.edges[k][1])) for k in out]
        def cost(f):
            d = self.T.dim(f)
            return math.fsum(self.cost[d-x] for x in dins) + math.fsum(self.cost[x-d] for x in douts)
        options = [old]
        if mode in ('both', 'low') and self.T.nondeg(low):
            options.append(low)
        if mode in ('both', 'high') and self.T.nondeg(high):
            options.append(high)
        best = min(options, key=lambda f: (cost(f), self.T.dim(f), f))
        gain = cost(old)-cost(best)
        if gain <= 1e-12:
            return 0., 0
        for i in group:
            self.frames[i] = best
        return gain, len(group)

    def optimize(self, rounds=20, seed=0, mode='both'):
        rng = random.Random(seed)
        for turn in range(rounds):
            t = time.monotonic()
            groups = self.components() if turn % 2 else [[i] for i in range(self.N)]
            if turn % 4 == 1:
                groups.reverse()
            if turn % 4 >= 2:
                rng.shuffle(groups)
            gain, changed = 0., 0
            for group in groups:
                improve, moved = self.update(group, mode)
                gain += improve
                changed += moved
            print(json.dumps(dict(round=turn, seconds=time.monotonic()-t, gain=gain,
                                  moved=changed, root=self.profile()['numerical_root'])), flush=True)
            if changed == 0 and turn % 2:
                break
        self.check()

    def envelopes(self, group, ensure_nondeg=False):
        lower, upper = {}, {}
        for i in sorted(group):
            f = self.T.join_all([self.node_spans[i]] + [
                lower.get(self.edges[k][0], self.F(self.edges[k][0])) for k in self.inc[i]])
            need(self.T.sub(f, self.frames[i]), 'lower envelope')
            lower[i] = self.frames[i] if ensure_nondeg and not self.T.nondeg(f) else f
        for i in sorted(group, reverse=True):
            f = self.T.meet_all(
                upper.get(self.edges[k][1], self.F(self.edges[k][1])) for k in self.out[i])
            need(self.T.sub(self.frames[i], f), 'upper envelope')
            upper[i] = self.frames[i] if ensure_nondeg and not self.T.nondeg(f) else f
        return lower, upper

    def update_envelope(self, group):
        changed_edges = set(k for i in group for k in self.inc[i]+self.out[i])
        plans = self.envelopes(group, ensure_nondeg=True)
        def cost(plan):
            return math.fsum(self.cost[self.T.dim(plan.get(b, self.F(b))) -
                                       self.T.dim(plan.get(a, self.F(a)))]
                             for k in changed_edges for a, b in [self.edges[k]])
        before = cost({})
        plan = min(plans, key=cost)
        gain = before-cost(plan)
        if gain <= 1e-12:
            return 0., 0
        changed = sum(f != self.frames[i] for i, f in plan.items())
        for i, f in plan.items():
            self.frames[i] = f
        return gain, changed

    def update_subsets(self, group):
        old = self.frames[group[0]]
        if not all(self.frames[i] == old for i in group):
            return 0., 0
        best_gain, best_nodes, best_frame = 0., [], old
        for env, lower in zip(self.envelopes(group), (True, False)):
            for f in sorted(set(env.values())-{old}, key=lambda v: (self.T.dim(v), v)):
                if not self.T.nondeg(f):
                    continue
                selected = [i for i in group if self.T.sub(env[i], f)] if lower else [
                    i for i in group if self.T.sub(f, env[i])]
                inc, out = self.boundary(selected)
                d, od = self.T.dim(f), self.T.dim(old)
                gain = math.fsum(self.cost[od-self.T.dim(self.F(self.edges[k][0]))] -
                                 self.cost[d-self.T.dim(self.F(self.edges[k][0]))] for k in inc)
                gain += math.fsum(self.cost[self.T.dim(self.F(self.edges[k][1]))-od] -
                                  self.cost[self.T.dim(self.F(self.edges[k][1]))-d] for k in out)
                if gain > best_gain+1e-12:
                    best_gain, best_nodes, best_frame = gain, selected, f
        for i in best_nodes:
            self.frames[i] = best_frame
        return best_gain, len(best_nodes)

    def collective_pass(self, kind, seed=0):
        t = time.monotonic()
        groups = [g for g in self.components() if len(g) > 1]
        random.Random(seed).shuffle(groups)
        gain, moved = 0., 0
        update = self.update_envelope if kind == 'envelope' else self.update_subsets
        for group in groups:
            g, n = update(group)
            gain += g
            moved += n
        self.check()
        print(json.dumps(dict(collective=kind, seconds=time.monotonic()-t, gain=gain,
                              moved=moved, root=self.profile()['numerical_root'])), flush=True)
        return moved

    def adjacent_pass(self, seed=0, radius=1):
        """Joint endpoint moves across adjacent vertices of unequal frames."""
        t = time.monotonic()
        neighbors = [set() for _ in self.ops]
        for a, b in self.edges:
            if a >= 0 and b >= 0:
                neighbors[a].add(b)
                neighbors[b].add(a)
        groups = set()
        if radius == 1:
            groups = {(min(a,b), max(a,b)) for a, b in self.edges
                      if a >= 0 and b >= 0 and self.frames[a] != self.frames[b]}
        else:
            for i in range(self.N):
                group = {i}
                for _ in range(radius-1):
                    group |= {j for s in list(group) for j in neighbors[s]}
                if len(group) > 1:
                    groups.add(tuple(sorted(group)))
        groups = sorted(groups)
        random.Random(seed).shuffle(groups)
        gain, moved = 0., 0
        for group in groups:
            g, n = self.update_envelope(group)
            gain += g
            moved += n
        self.check()
        print(json.dumps(dict(adjacent_radius=radius, seconds=time.monotonic()-t, gain=gain,
                              moved=moved, root=self.profile()['numerical_root'])), flush=True)
        return moved

    def source_hashes(self):
        paths = [self.base/(name+'_p%d.json' % self.p)
                 for name in ('graph','word','frames','kchron','profile')]
        return {p.name: sha256(p.read_bytes()).hexdigest() for p in paths}

    def load(self, path, require_pins=False):
        record = json.loads(path.read_text())
        if require_pins or 'source_sha256' in record:
            pins = record.get('source_sha256', {})
            normalized = {Path(k).name: v for k, v in pins.items()}
            need(len(normalized) == len(pins) and normalized == self.source_hashes(),
                 'physical bit source hash pins')
        used = set()
        for i, rec in record['frames']:
            need(i not in used and 0 <= i < self.N, 'unique changed frame indices')
            used.add(i)
            if isinstance(rec, int):
                need(0 <= rec < len(record['spaces']), 'new frame table index')
                rec = record['spaces'][rec]
            rows = rec['b'] if 'b' in rec else kernel(rec['a'], self.h)[0]
            f = self.T.intern(rows)
            need(self.T.dim(f) == rec['dim'], 'loaded frame rank')
            self.frames[i] = f
        self.check()
        self.set_pairs(record.get('pairs', []))

    def verified_profile(self, replay=True, controls=True):
        self.check()
        profile = self.profile()
        if replay:
            profile['scalar_replay'] = complete_replay(self.c, self.pairs)
        profile['checks'] = dict(original_checker=self.baseline_checks,
            value_spans_inside_frames=True, all_changed_frames_nondegenerate=True,
            all_role_chains_nested=True, same_sources_targets_centres_gauges=True,
            compensated_lifetime_pairs_checked=True, target_chains_in_actual_read_order=True,
            complete_physical_rank_recount=True)
        profile['fresh_opcode_binding'] = fresh_opcode_binding(self.c)
        if controls:
            profile['rejected_frame_controls'] = frame_controls(self)
        profile['source_sha256'] = self.source_hashes()
        return profile

    def save(self, path, replay=False):
        path.mkdir(parents=True, exist_ok=True)
        diff = [(i, f) for i, f in enumerate(self.frames) if f != self.base_frames[i]]
        records = {f: self.T.record(f) for _, f in diff}
        frames = sorted(records, key=lambda f: json.dumps(records[f], sort_keys=True))
        indices = {f: j for j, f in enumerate(frames)}
        witness = dict(frames=[[i, indices[f]] for i, f in diff],
                       spaces=[records[f] for f in frames], pairs=self.pairs,
                       source_sha256=self.source_hashes())
        (path/'frames.json').write_text(json.dumps(witness, separators=(',', ':'), sort_keys=True)+'\n')
        profile = self.verified_profile(replay=replay)
        (path/'profile.json').write_text(json.dumps(profile, indent=2, sort_keys=True)+'\n')
        return profile


def frame_controls(e):
    """Reject actual broken geometric obligations, independently of moments."""
    controls = []
    old = e.frames[0]
    try:
        e.frames[0] = e.T.zero
        e.check()
    except Fail:
        controls.append('operation_frame_omits_value')
    finally:
        e.frames[0] = old
    full = e.w['full_frame']
    a = next(a for a, b in e.edges if a >= 0 and e.F(b) != full)
    old = e.frames[a]
    try:
        e.frames[a] = full
        e.check()
    except Fail:
        controls.append('role_chain_retreat')
    finally:
        e.frames[a] = old
    isotropic = e.T.intern([tuple(int(j < 9) for j in range(e.h))])
    need(not e.T.nondeg(isotropic), 'isotropic line must fail Gram check')
    controls.append('degenerate_isotropic_line')
    need(len(controls) == 3, 'all physical bit mutation controls rejected')
    if e.pairs:
        saved = list(e.pairs)
        try:
            e.set_pairs(saved+[saved[0]])
        except Fail:
            controls.append('duplicate_physical_alias')
        finally:
            e.set_pairs(saved)
        phase = set(e.w['phase1'])
        i = next((i for i, (a, _, _) in enumerate(saved) if e.role_ops[a][-1] not in phase), None)
        need(i is not None, 'selected witness has a donor alive after the centre cut')
        broken = list(saved)
        a, b, _ = broken[i]
        broken[i] = a, b, e.role_ops[a][-1]
        try:
            e.set_pairs(broken)
        except Fail as error:
            need(str(error) == 'donor dead before recipient birth', 'live-donor control reached chronology check')
            controls.append('donor_still_live_at_read')
        finally:
            e.set_pairs(saved)
        need(len(controls) == 5, 'all alias mutation controls rejected')
    e.check()
    return controls


def fresh_opcode_binding(c):
    """Exact source support of every original virtual XOR and root.

    Independently supplied by the parallel source-cap investigation.  Reuse
    treats a donor's terminal content as the next role's arbitrary dirty start;
    this check binds the unaliased clean word to its named graph nodes first.
    """
    v, R = c.v, c.prof['R']
    support = [1 << s for s in range(v)]
    for a, b in c.g['args'][v:]:
        need(not support[a] & support[b], 'graph additions have disjoint supports')
        support.append(support[a] ^ support[b])
    fresh = [0]*R
    for leaf, role in c.w['sources'].items():
        fresh[role] ^= 1 << int(leaf)
    phase = set(c.w['phase1'])
    order = sorted(phase)+[i for i in range(len(c.w['ops'])) if i not in phase]
    for i in order:
        a, b, node = c.w['ops'][i]
        need(not fresh[a] & fresh[b], 'actual virtual gate has disjoint fresh supports')
        fresh[a] ^= fresh[b]
        need(fresh[a] == support[node], 'virtual opcode/frame graph-node binding')
    for root, role in zip(c.g['roots'], c.w['rootroles']):
        need(fresh[role] == support[root['node']], 'virtual root/graph-node binding')
    return dict(exact_fresh_gate_supports=len(order), exact_root_supports=len(c.g['roots']),
                phased_execution=True, conservative_disjoint_supports=True)


def checked_experiment(frames_path, baseline=BASE, p=12):
    """Return the checked physical experiment for composable source changes."""
    e = Experiment(baseline=baseline, p=p, quiet=True)
    e.load(Path(frames_path), require_pins=True)
    e.checked_profile = e.verified_profile(replay=True, controls=True)
    return e


def checked_record(frames_path, expected_path=None, baseline=BASE, p=12):
    """Quiet integration entry point: exact geometry, full basis and recount."""
    result = checked_experiment(frames_path, baseline, p).checked_profile
    if expected_path is not None:
        expected = json.loads(Path(expected_path).read_text())
        need(expected == result, 'saved physical bit row differs from exact reconstruction')
    return result


def complete_replay(c, pairs=(), mutation=None):
    """Literal centre-cut/read-order replay over every F2 source and dirty basis.

    Y registers are write-only, so their initial-value coefficients remain
    the identity by construction.  Their computed increments are checked on
    all v + R other formal basis inputs, and all auxiliary/source inputs are
    checked restored by the literal inverse word.
    """
    g, w, h, v, R = c.g, c.w, c.h, c.v, c.prof['R']
    ops = w['ops']
    rootroles, roots = w['rootroles'], g['roots']
    adj = [0]*R
    for r, s in zip(roots, rootroles):
        adj[s] ^= sum(1 << t for t in r['targets'])
    for a, b, _ in reversed(ops):
        adj[b] ^= adj[a]
    sources = {int(x): s for x, s in w['sources'].items()}
    selected = {z['role'] for z in w['gauges']}
    merge = {b: a for a, b, _ in pairs}
    late_at = defaultdict(list)
    for _, b, t in pairs:
        late_at[t].append(b)
    live = [s for s in range(R) if s not in merge]
    slot = {s: i for i, s in enumerate(live)}
    alias = lambda s: slot[merge.get(s, s)]
    omitted = pairs[0][1] if pairs else w['gauges'][-1]['role']
    premature = pairs[0][1] if pairs else None
    phase = set(w['phase1'])
    rest = [i for i in range(len(ops)) if i not in phase]
    X = [1 << i for i in range(v)]
    Z0 = [1 << (v+s) for s in range(len(live))]
    Z, Y = list(Z0), [0]*v
    def scatter(mask, value):
        while mask:
            bit = mask & -mask
            Y[bit.bit_length()-1] ^= value
            mask ^= bit
    # Initial zero-frame dirty-response correction.
    for s in range(R):
        if s not in selected and s not in merge:
            scatter(adj[s], Z[alias(s)])
    if mutation == 'read_before_donor_death':
        scatter(adj[premature], Z[alias(premature)])
    for x, s in sources.items():
        Z[alias(s)] ^= X[x]
    for i in w['phase1']:
        a, b, _ = ops[i]
        need(alias(a) != alias(b), 'distinct aliased phase-one gate ports')
        Z[alias(a)] ^= Z[alias(b)]
    # Copy each retained centre at its proper root frame, restore its copy to
    # zero, and scatter at the common target zero frame before gauge reads.
    for r, s in zip(roots, rootroles):
        if r['kind'] == 'center':
            scatter(sum(1 << t for t in r['targets']), Z[alias(s)])
    for z in reversed(w['gauges']):
        s = z['role']
        if s in merge or (mutation == 'omit_gauge_read' and s == omitted):
            continue
        scatter(adj[s], Z[alias(s)])
    for i in rest:
        for s in late_at.get(i, ()):
            if mutation == 'omit_gauge_read' and s == omitted:
                continue
            if mutation == 'read_before_donor_death' and s == premature:
                continue
            scatter(adj[s], Z[alias(s)])
        a, b, _ = ops[i]
        need(alias(a) != alias(b), 'distinct aliased gate ports')
        if mutation != 'omit_xor' or i != rest[0]:
            Z[alias(a)] ^= Z[alias(b)]
    deliveries = defaultdict(list)
    for e in c.k['entries']:
        # All V injections are finished before changing a source register.
        X[e['carrier']] ^= X[e['passive']]
        deliveries[e['deliver_after_root']].append(e)
    for j, (r, s) in enumerate(zip(roots, rootroles)):
        if r['kind'] != 'center':
            scatter(sum(1 << t for t in r['targets']), Z[alias(s)])
        for e in deliveries.get(j, ()):
            scatter(sum(1 << t for t in e['receivers']), X[e['carrier']])
    for e in c.k['entries']:
        X[e['carrier']] ^= X[e['passive']]
    for i in reversed(w['phase1']+rest):
        a, b, _ = ops[i]
        if mutation != 'omit_xor' or i != rest[0]:
            Z[alias(a)] ^= Z[alias(b)]
    for x, s in sources.items():
        Z[alias(s)] ^= X[x]
    correct = Y == [1 << t for t in range(v)]
    restored = Z == Z0 and X == [1 << t for t in range(v)]
    if mutation is None:
        need(correct and restored, 'complete chronological F2 basis replay')
        controls = {}
        names = ['omit_gauge_read', 'omit_xor'] + (['read_before_donor_death'] if pairs else [])
        for name in names:
            controls[name] = complete_replay(c, pairs, name)
            need(not controls[name]['target_correct'], 'replay mutation rejected')
        return dict(field='F2', formal_source_and_dirty_basis=v+len(live),
                    logical_roles=R, physical_roles=len(live), compensated_pairs=len(pairs),
                    untouched_target_basis=v, complete_forward=True,
                    literal_inverse_restores_all=True, rejected_controls=list(controls))
    return dict(target_correct=correct, restored=restored)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, default=BASE)
    parser.add_argument('--p', type=int, default=12)
    parser.add_argument('--output', type=Path, default=ROOT/'build/paired-cube-lifetime/bit/descent')
    parser.add_argument('--input-frames', type=Path)
    parser.add_argument('--rounds', type=int, default=20)
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--mode', choices=('low','high','both'), default='both')
    parser.add_argument('--envelopes', type=int, default=0)
    parser.add_argument('--subsets', type=int, default=0)
    parser.add_argument('--adjacent', type=int, default=0)
    parser.add_argument('--radius', type=int, default=1)
    parser.add_argument('--reuse', action='store_true')
    parser.add_argument('--replay', action='store_true')
    args = parser.parse_args()
    e = Experiment(args.baseline, args.p)
    if args.input_frames:
        e.load(args.input_frames)
    e.optimize(args.rounds, args.seed, args.mode)
    for kind, turns in (('envelope', args.envelopes), ('subsets', args.subsets)):
        for turn in range(turns):
            if not e.collective_pass(kind, args.seed+turn):
                break
            e.optimize(args.rounds, args.seed+turn+1, args.mode)
    for turn in range(args.adjacent):
        if not e.adjacent_pass(args.seed+turn, args.radius):
            break
        e.optimize(args.rounds, args.seed+turn+1, args.mode)
    if args.reuse:
        e.match_pairs()
    row = e.save(args.output, args.replay)
    print(json.dumps(dict(saved=str(args.output), root=row['numerical_root'],
                          changed_operation_frames=row['changed_operation_frames'])), flush=True)


if __name__ == '__main__':
    main()
