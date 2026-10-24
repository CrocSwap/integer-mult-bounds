#!/usr/bin/env python3
"""Bounded discovery of commuting scalar swaps with movable native maps.

Apache-2.0. Substantial OpenAI Codex assistance. Uses Cao Yifan's exact
subspace intervals and transported native-map lemma, credited in TASK.json.
Prices are floating discovery evidence; emitted words require exact replay.
"""
from collections import Counter, defaultdict
from copy import deepcopy
from hashlib import sha256
from itertools import product
from pathlib import Path
import argparse
import gzip
import json
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research/scalar-reorder-20261022'))
from intervals import basis, closure, complete_interval


def need(ok, message):
    if not ok:
        raise ValueError(message)


def roles(event):
    if event[0] == 'scalar':
        gate = event[1]
        rr = gate[1:3] if gate[0] in ('add', 'copy') else gate[1:2]
        return [r[1] for r in rr if r[0] == 'L']
    return [event[1][1]] if event[0] == 'warp' else []


def commuting_pair(a, b):
    if a[0] != 'scalar' or b[0] != 'scalar':
        return False
    g, h = a[1], b[1]
    if g[0] != 'add' or h[0] != 'add':
        return False
    if any(r[0] != 'L' for r in g[1:3] + h[1:3]):
        return False
    if g[1] == h[2] or h[1] == g[2]:
        return False
    return len(set(roles(a)) & set(roles(b))) == 1


class Model:
    def __init__(self, discovery_price=True):
        source = ROOT / 'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
        self.source_bytes = source.read_bytes()
        self.payload = json.loads(gzip.decompress(self.source_bytes))
        self.c = self.payload['canonical']
        self.raw = [deepcopy(e) for e in self.payload['programs']['forward']
                    if e[0] != 'climb']
        self.spaces = [closure(b) for b in self.c['frames']]
        self.dims = [len(b) for b in self.c['frames']]
        need(all(len(s) == 2 ** d and all(0 <= x < 512 for x in s)
                 for s, d in zip(self.spaces, self.dims)), 'Independent nine-axis frame bases')
        self.labels = {s: i for i, s in enumerate(self.spaces)}
        self.selected, self.lines = {}, {}
        for op in range(1, 73):
            occurrences = [(i, e) for i, e in enumerate(self.raw)
                           if e[0] == 'warp' and abs(e[2]) == op]
            choices = [(i, e) for i, e in occurrences
                       if self.dims[e[3]] not in (0, 9)]
            i, late = max(choices, key=lambda pair: self.dims[pair[1][3]])
            need(late[2] > 0, 'Positive selected late occurrence')
            self.selected[i] = op
            pairs = {(e[3], e[4]) if e[2] > 0 else (e[4], e[3])
                     for j, e in choices if j != i}
            if pairs:
                need(len(pairs) == 1, 'Only one additional prelude contract')
                a, b = next(iter(pairs))
                need(self.dims[a] == self.dims[b] == 1, 'Prelude line pair')
                self.lines[op] = (self.c['frames'][a][0],
                                  self.c['frames'][b][0])
        self.original = {i: e[2] for i, e in enumerate(self.raw)
                         if e[0] == 'scalar' and roles(e)}
        self.constant = lambda f: -f - 1
        self.edges = self.graph()
        self.incident = defaultdict(list)
        for edge in self.edges:
            a, b, _ = edge
            self.incident[a].append(edge)
            self.incident[b].append(edge)
        self.domain_cache = {}
        self.stats = Counter()
        self.price = ([0.] + [r ** (1 - .0030217758) - r for r in range(1, 10)]
                      if discovery_price else None)

    def label(self, space):
        space = frozenset(space)
        if space not in self.labels:
            self.labels[space] = len(self.spaces)
            self.spaces.append(space)
            b = basis(space)
            self.dims.append(len(b))
            self.c['frames'].append(b)
        return self.labels[space]

    def graph(self, swap=None):
        current = [self.constant(f) for f in self.c['start']]
        edges = []

        def edge(a, b):
            if isinstance(a, tuple):
                edges.append((a[0], b, a[1]))
            else:
                edges.append((a, b, 0))

        order = list(range(len(self.raw)))
        if swap is not None:
            order[swap], order[swap + 1] = order[swap + 1], order[swap]
        for i in order:
            e = self.raw[i]
            rr = roles(e)
            if e[0] == 'scalar' and rr:
                gate = e[1]
                gr = gate[1:3] if gate[0] in ('add', 'copy') else gate[1:2]
                node = i if all(r[0] == 'L' for r in gr) else self.constant(e[2])
                for r in rr:
                    edge(current[r], node)
                    current[r] = node
            elif e[0] == 'warp':
                r = e[1][1]
                if i in self.selected:
                    need(not isinstance(current[r], tuple), 'Separated late occurrences')
                    current[r] = (current[r], self.selected[i])
                else:
                    edge(current[r], self.constant(e[3]))
                    current[r] = self.constant(e[4])
        for r, f in enumerate(self.c['final']):
            edge(current[r], self.constant(f))
        return edges

    def frame(self, node, changed):
        return changed.get(node, self.original[node]) if node >= 0 else -node - 1

    def valid(self, a, b, kind):
        if not kind:
            return self.spaces[a] <= self.spaces[b]
        if self.dims[a] > self.dims[b]:
            return False
        if kind not in self.lines:
            return True
        x, y = self.lines[kind]
        return ((y in self.spaces[b]) if x in self.spaces[a]
                else (self.dims[a] < self.dims[b] or y not in self.spaces[b]))

    def cost(self, edges, changed):
        out = 0.
        for a, b, kind in edges:
            f, g = self.frame(a, changed), self.frame(b, changed)
            if not self.valid(f, g, kind):
                return float('inf')
            out += self.price[self.dims[g] - self.dims[f]]
        return out

    def domain(self, node, edges, variables):
        lower = {0}
        upper = set(range(512))
        restrictions = []
        for a, b, kind in edges:
            if a != node and b != node:
                continue
            other = b if a == node else a
            if other in variables:
                continue
            frame = self.frame(other, {})
            if kind:
                restrictions.append((a == node, frame, kind))
            elif a == node:
                upper &= self.spaces[frame]
            else:
                lower = set(closure(lower | self.spaces[frame]))
        if not lower <= upper:
            return []
        lo, hi = self.label(lower), self.label(upper)
        key = lo, hi
        if key not in self.domain_cache:
            values = complete_interval(self.spaces, self.dims, self.c['frames'],
                                       (lo,), (hi,), self.stats, max_gap=5)
            self.labels.update({s: i for i, s in enumerate(self.spaces)})
            self.domain_cache[key] = values
        values = self.domain_cache[key]
        out = []
        for f in values:
            if all(self.valid(f, g, kind) if outgoing else self.valid(g, f, kind)
                   for outgoing, g, kind in restrictions):
                out.append(f)
        return out

    def candidates(self):
        for i, (a, b) in enumerate(zip(self.raw, self.raw[1:])):
            if not commuting_pair(a, b):
                continue
            # Without a movable native edge this repeats the prior fixed-warp
            # family. Leave those already tested cases alone.
            if not any(k for n in (i, i + 1) for _, _, k in self.incident[n]):
                self.stats['fixed_warp_pairs_omitted'] += 1
                continue
            yield i

    def search(self):
        started = time.monotonic()
        best = None
        results = []
        for i in self.candidates():
            # The swap changes only per-role edges incident to these gates.
            # Every external contact and every other native edge stays fixed.
            variables = {i, i + 1}
            graph = self.graph(i)
            edges = [e for e in graph if e[0] in variables or e[1] in variables]
            old_edges = [e for e in self.edges if e[0] in variables or e[1] in variables]
            before = self.cost(old_edges, {})
            da, db = (self.domain(n, edges, variables) for n in (i, i + 1))
            self.stats['pairs'] += 1
            self.stats['frame_pairs'] += len(da) * len(db)
            value, frames = float('inf'), None
            # Free late edge endpoints have unique event IDs and may be
            # materialized from the selected frame pair after discovery.
            for f, g in product(da, db):
                changed = {i: f, i + 1: g}
                trial = self.cost(edges, changed)
                if trial < value:
                    value, frames = trial, (f, g)
            gain = before - value
            row = {'event': i, 'domain_sizes': [len(da), len(db)],
                   'gain': gain if frames else None,
                   'frames': list(frames) if frames else None,
                   'old_frames': [self.original[i], self.original[i + 1]],
                   'free_operators': sorted({k for _, _, k in edges if k})}
            results.append(row)
            if frames and gain > 1e-10 and (best is None or gain > best['gain']):
                best = row
                print('POSITIVE', json.dumps(row), flush=True)
            if self.stats['pairs'] % 25 == 0:
                print('PROGRESS', self.stats['pairs'], 'frame_pairs',
                      self.stats['frame_pairs'], 'seconds', time.monotonic() - started, flush=True)
        result = {'status': 'DISCOVERY_ONLY', 'stats': dict(self.stats),
                  'best': best, 'candidates': results,
                  'source_sha256': sha256(self.source_bytes).hexdigest(),
                  'source_payload_sha256': sha256(gzip.decompress(self.source_bytes)).hexdigest(),
                  'discovery_price_exponent': 1 - .0030217758,
                  'seconds': time.monotonic() - started}
        (HERE / 'SEARCH.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
        print('RESULT', json.dumps({k: v for k, v in result.items() if k != 'candidates'}), flush=True)
        if best:
            self.emit(best)
        return result

    def emit(self, best):
        sys.path.insert(0, str(ROOT / 'research/kappa-round3-warp-20261022'))
        from constrained_map import line_matching_map
        sys.path.insert(0, str(ROOT / 'research/warp-interface-20261022'))
        from free_warp_contacts import matching_map
        from warp_merge import synthesize
        i = best['event']
        changed = {i: best['frames'][0], i + 1: best['frames'][1]}
        graph = self.graph(i)
        recipes = {}
        for a, b, kind in graph:
            if not kind or kind not in best['free_operators']:
                continue
            fa, fb = self.frame(a, changed), self.frame(b, changed)
            if kind in self.lines:
                cols, outbasis = line_matching_map(self.c['frames'][fa], self.c['frames'][fb], *self.lines[kind])
            else:
                outbasis = self.c['frames'][fb][:self.dims[fa]]
                cols = matching_map(self.c['frames'][fa], outbasis)
            recipes[kind] = {'input': fa, 'output': self.label(closure(outbasis)), 'G_columns': cols}
        programs = {}
        for direction, program in self.payload['programs'].items():
            raw = [deepcopy(e) for e in program if e[0] != 'climb']
            need(len(raw) == len(self.raw), 'Dual event alignment')
            for n, f in changed.items():
                need(raw[n][0] == 'scalar', 'Actual scalar event alignment')
                raw[n][2] = f
            for n, op in self.selected.items():
                if op in recipes:
                    need(raw[n][0] == 'warp' and raw[n][2] == op, 'Actual dual late warp')
                    raw[n][3:5] = [recipes[op]['input'], recipes[op]['output']]
            raw[i], raw[i + 1] = raw[i + 1], raw[i]
            programs[direction] = synthesize(self.c, raw)
        for row in self.c['warps']:
            if row['op'] in recipes:
                row['G_columns'] = recipes[row['op']]['G_columns']
        paid = {}
        for direction, p in programs.items():
            census = Counter(e[5] for e in p if e[0] == 'climb')
            census.update(e[4] for e in p if e[0] == 'center')
            paid[direction] = census
        need(paid['forward'] == paid['backward'], 'Complete two-orientation invoice')
        oldpaid = Counter(e[5] for e in self.payload['programs']['forward'] if e[0] == 'climb')
        oldpaid.update(e[4] for e in self.payload['programs']['forward'] if e[0] == 'center')
        print('ACTUAL_PAID', dict(paid['forward']), 'old', dict(oldpaid), flush=True)
        delta = {r: oldpaid[r] - paid['forward'][r] for r in set(oldpaid) | set(paid['forward'])}
        need(sum(r * v for r, v in delta.items()) == 0, 'Unchanged rank-mass deficit')
        need(sum(self.price[r] * v for r, v in delta.items()) > 1e-10, 'Actual reconstructed gain')
        best['new_paid'] = dict(paid['forward'])
        best['old_paid'] = dict(oldpaid)
        best['warp_recipes'] = recipes
        (HERE / 'CANDIDATE.json').write_text(json.dumps(best, indent=2, sort_keys=True) + '\n')
        payload = {'canonical': self.c, 'programs': programs}
        (HERE / 'CANDIDATE-WORD.json.gz').write_bytes(gzip.compress(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode(), mtime=0))


if __name__ == '__main__':
    Model().search()
