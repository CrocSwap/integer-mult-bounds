#!/usr/bin/env python3
"""Exact fixed-rank symmetric-phase rigidity; Apache-2.0, Codex assistance.

The phase grammar is credited to Dugongue, PR4654. The native word is Cao
Yifan's PR4610 round-three word, on the retained PR4470/native lineage.
"""
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def span(basis):
    out = {0}
    for x in basis:
        need(isinstance(x, int) and 0 <= x < 512, 'nine-bit basis vector')
        out |= {y ^ x for y in tuple(out)}
    need(len(out) == 2 ** len(basis), 'independent frame basis')
    return frozenset(out)


def mv(columns, x):
    out = 0
    for i, v in enumerate(columns):
        if x >> i & 1:
            out ^= v
    return out


def inverse(columns):
    values = {mv(columns, x): x for x in range(512)}
    need(len(values) == 512, 'invertible shared native map')
    return [values[1 << i] for i in range(9)]


def graph(payload):
    c, word = payload['canonical'], payload['programs']['forward']
    frames = c['frames']
    spaces = list(map(span, frames))
    nodes, fixed, edges, helpers = [0, 0], set(), [], []
    reconstructed = Counter()

    def new(f, freeze=False):
        n = len(nodes)
        nodes.append(f)
        if freeze:
            fixed.add(n)
        return n

    current = [new(f, r < 224) for r, f in enumerate(c['start'])]
    entry = current[:]

    def move(r, f, dst=None):
        a = current[r]
        old = nodes[a]
        need(spaces[old] <= spaces[f], 'nested paid transition')
        if old != f:
            reconstructed[len(frames[f]) - len(frames[old])] += 1
        b = new(f) if dst is None else dst
        edges.append(('paid', a, b, tuple(frames[old]), tuple(frames[old])))
        current[r] = b

    maps = {w['op']: w['G_columns'] for w in c['warps']}
    maps.update({-op: inverse(cols) for op, cols in list(maps.items())})
    paid = Counter()
    for event in word:
        kind = event[0]
        if kind == 'climb':
            _, _, r, a, b, width = event
            need(spaces[a] < spaces[b] and len(frames[b]) - len(frames[a]) == width,
                 'source paid rank derived from actual geometry')
            paid[width] += 1
        elif kind == 'scalar':
            g, f = event[1:]
            refs = g[1:3] if g[0] in ('add', 'copy') else g[1:2]
            contact = new(f, any(typ != 'L' for typ, _ in refs))
            for typ, r in refs:
                if typ == 'L':
                    move(r, f, contact)
        elif kind == 'warp':
            _, role, op, a, b = event
            need(role[0] == 'L', 'persistent native warp')
            move(role[1], a)
            src, dst = current[role[1]], new(b)
            image = tuple(mv(maps[op], v) for v in frames[a])
            need(span(image) == spaces[b], 'shared map acts on the declared chart')
            edges.append(('warp', src, dst, tuple(frames[a]), image))
            current[role[1]] = dst
        elif kind == 'adapter':
            fixed.add(current[event[2]])
        elif kind == 'center':
            _, _, a, b, width = event
            need(spaces[a] < spaces[b] or spaces[b] < spaces[a], 'nested owned center')
            need(abs(len(frames[a]) - len(frames[b])) == width, 'owned center rank')
            paid[width] += 1
            reconstructed[width] += 1
        else:
            need(kind == 'phase', 'known source event')
    for r, f in enumerate(c['final']):
        dst = new(f, r < 224)
        move(r, f, dst)
        if r >= 224:
            need(spaces[c['start'][r]] <= spaces[f], 'nested helper boundary')
            helpers.append((r, entry[r], dst, tuple(frames[c['start'][r]])))
    need(paid == {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8},
         'exact round-three paid source profile')
    need(reconstructed == paid, 'contact graph reproduces the actual paid profile')
    return frames, nodes, fixed, edges, helpers


class Forms:
    def __init__(self, frames, nodes, fixed):
        self.frames, self.nodes, self.fixed = frames, nodes, fixed
        self.offsets, self.count = [], 0
        self.bases, self.coords, self.coeffs = {}, {}, {}
        for n, f in enumerate(nodes):
            self.offsets.append(self.count + 1)
            if n >= 2 and n not in fixed:
                d = len(frames[f])
                self.count += d * (d + 1) // 2

    def coordinates(self, f, x):
        if (f, x) in self.coords:
            return self.coords[f, x]
        if f not in self.bases:
            basis = {}
            for i, v in enumerate(self.frames[f]):
                mask = 1 << i
                while v:
                    p = v.bit_length() - 1
                    if p not in basis:
                        basis[p] = v, mask
                        break
                    v ^= basis[p][0]
                    mask ^= basis[p][1]
            self.bases[f] = basis
        y, mask = x, 0
        while y:
            p = y.bit_length() - 1
            need(p in self.bases[f], 'vector lies in contact subspace')
            v, m = self.bases[f][p]
            y ^= v
            mask ^= m
        self.coords[f, x] = mask
        return mask

    def at(self, node, x, y):
        if node < 2 or node in self.fixed:
            return []
        f = self.nodes[node]
        a, b = self.coordinates(f, x), self.coordinates(f, y)
        key = f, a, b
        if key not in self.coeffs:
            out, index = [], 0
            for i in range(len(self.frames[f])):
                for j in range(i, len(self.frames[f])):
                    v = (a >> i & 1) & (b >> j & 1)
                    if i != j:
                        v ^= (a >> j & 1) & (b >> i & 1)
                    if v:
                        out.append(index)
                    index += 1
            self.coeffs[key] = out
        return [self.offsets[node] + i for i in self.coeffs[key]]


class Equalities:
    def __init__(self, count):
        self.parent = list(range(count + 1))
        self.pending, self.merges = [], 0

    def root(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def simplify(self, row):
        out = set()
        for x in row:
            r = self.root(x)
            if r:
                out.symmetric_difference_update((r,))
        return sorted(out)

    def equation(self, row):
        r = self.simplify(row)
        if len(r) in (1, 2):
            a, b = (0, r[0]) if len(r) == 1 else r
            self.parent[b] = a
            self.merges += 1
        elif r:
            self.pending.append(r)

    def finish(self):
        while self.pending:
            before = self.merges
            rows, self.pending = self.pending, []
            for r in rows:
                self.equation(r)
            if before == self.merges:
                break


def result(payload):
    frames, nodes, fixed, edges, helpers = graph(payload)
    forms = Forms(frames, nodes, fixed)
    equalities = Equalities(forms.count)
    counts = Counter()
    for kind, a, b, old, image in edges:
        for i, x in enumerate(old):
            for j in range(i, len(old)):
                row = sorted(set(forms.at(a, x, old[j])) ^ set(forms.at(b, image[i], image[j])))
                if row:
                    counts[kind] += 1
                    equalities.equation(row)
    equalities.finish()
    need(not equalities.pending, 'all equations discharged by exact equality substitution')
    need(all(equalities.root(i) == 0 for i in range(1, forms.count + 1)),
         'every free form coordinate is forced zero')
    queries = 0
    for _, a, b, basis in helpers:
        for i, x in enumerate(basis):
            for y in basis[i:]:
                row = sorted(set(forms.at(a, x, y)) ^ set(forms.at(b, x, y)))
                if row:
                    queries += 1
                    need(not equalities.simplify(row), 'helper difference forced zero')
    return {'status': 'EXACT_FIXED_PAID_RANK_PHASE_RIGIDITY_NO_NEW_KAPPA',
            'native_roles': 632, 'helpers': len(helpers), 'frame_registry': len(frames),
            'contact_nodes_including_two_sentinels': len(nodes), 'frozen_nodes': len(fixed),
            'free_binary_form_coordinates': forms.count, 'equations': dict(counts),
            'independent_equalities': equalities.merges, 'all_coordinates_forced_zero': True,
            'nontrivial_helper_coefficient_queries': queries, 'unresolved_equations': 0,
            'scope': 'Fixed subspaces/logical word/maps, unchanged paid ranks, zero main/adapter/owned gauges; both helper boundaries may vary.'}


def controls():
    e = Equalities(2)
    e.equation([1, 2])
    e.finish()
    need(not e.simplify([1, 2]) and e.simplify([1]), 'free homogeneous direction detected')
    e.equation([1])
    e.finish()
    need(not e.simplify([1]) and not e.simplify([2]), 'zero boundary propagates')
    e = Equalities(3)
    e.equation([1, 2, 3])
    e.equation([1])
    e.equation([2])
    e.finish()
    need(not e.pending and not e.simplify([3]), 'higher-arity equation revisited')
    return ['free_direction_detected', 'zero_boundary_propagation', 'higher_arity_substitution']


def main():
    source = HERE / 'sources/round3-native.json.gz'
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    pin = next(r for r in pins['files'] if r['path'].endswith('sources/round3-native.json.gz'))
    raw = source.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'exact source bytes')
    payload = json.loads(gzip.decompress(raw))
    report = result(payload)
    changed = deepcopy(payload)
    for basis in changed['canonical']['frames']:
        if len(basis) >= 2:
            basis[0] ^= basis[1]
    need(result(changed) == report, 'independent frame-basis change preserves rigidity')
    report['controls'] = controls()
    report['controls'].append('all_frame_basis_changes_preserve_result')
    path = HERE / 'RESULT.json'
    if '--write' in sys.argv:
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    else:
        need(report == json.loads(path.read_text()), 'committed result equality')
    print('PASS_SYMMETRIC_PHASE_RIGIDITY: %d exact coordinates forced zero; no new kappa' % report['free_binary_form_coordinates'])


if __name__ == '__main__':
    main()
