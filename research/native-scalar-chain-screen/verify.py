#!/usr/bin/env python3
"""Exact bounded corrective-ADD census; no solver or numerical rank price.

Cinna Davis / 1337isnot1337 with substantial OpenAI Codex assistance.
Apache-2.0. Not a full multiplication verification.
"""
from bisect import bisect_left, bisect_right
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import permutations
from pathlib import Path
import argparse
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
MAX_DISTANCE = 16


def need(ok, message):
    if not ok:
        raise ValueError(message)


def span(vectors):
    out = {0}
    for v in vectors:
        out.update(x ^ v for x in tuple(out))
    return frozenset(out)


def dim(space):
    n = len(space)
    need(n > 0 and n & (n - 1) == 0, 'Binary space cardinality')
    return n.bit_length() - 1


def roles(event):
    if event[0] == 'scalar':
        g = event[1]
        operands = g[1:3] if g[0] in ('add', 'copy') else g[1:2]
        return [r[1] for r in operands if r[0] == 'L']
    return [event[1][1]] if event[0] == 'warp' else []


def eligible(e):
    return e[0] == 'scalar' and e[1][0] == 'add' and len(roles(e)) == 2


def commute(g, h):
    return g[1] != h[2] and h[1] != g[2]


def chain(g, h):
    a, b = g[1:3]
    u, v = h[1:3]
    return len({tuple(r) for r in (a, b, u, v)}) == 3 and (b == u or v == a)


def correction(g, h):
    need(chain(g, h), 'Three distinct roles and one directed chain')
    a, b = g[1:3]
    u, v = h[1:3]
    q = Fraction(g[3], g[4]) * Fraction(h[3], h[4])
    dst, src, q = (a, v, -q) if b == u else (u, b, q)
    return ['add', dst, src, q.numerator, q.denominator]


def matrix(gates, owners):
    index = {r: i for i, r in enumerate(owners)}
    out = [[Fraction(i == j) for j in range(len(owners))] for i in range(len(owners))]
    for g in gates:
        a, b = index[g[1][1]], index[g[2][1]]
        q = Fraction(g[3], g[4])
        out[a] = [x + q * y for x, y in zip(out[a], out[b])]
    return out


def histogram(order, ranks, starts, ends):
    current = dict(starts)
    out = Counter()
    for operands, rank in zip(order, ranks):
        for r in operands:
            step = rank - current[r]
            need(step >= 0, 'No descending ordinary transport')
            if step:
                out[step] += 1
            current[r] = rank
    for r, rank in ends.items():
        step = rank - current[r]
        need(step >= 0, 'Paid exit transport is nonnegative and included')
        if step:
            out[step] += 1
    return out


def cut_slacks(candidate, baseline):
    need(sum(r * n for r, n in candidate.items()) == sum(r * n for r, n in baseline.items()),
         'Exact equal rank mass')
    return [sum((candidate[r] - baseline[r]) * min(r, k)
                for r in set(candidate) | set(baseline)) for k in range(1, 10)]


def dominance(candidate, baseline):
    slacks = cut_slacks(candidate, baseline)
    need(min(slacks) >= 0 and slacks[-1] == 0, 'No improvement for every concave rank price')
    return slacks


def triples(lo1, lo2, hi2, hi3):
    if not lo2 <= hi2:
        return
    need(lo1 <= lo2 <= hi2 <= hi3, 'Exact nested boundary flag')
    for a in range(dim(lo1), dim(hi2) + 1):
        for b in range(max(a, dim(lo2)), dim(hi2) + 1):
            for c in range(b, dim(hi3) + 1):
                yield a, b, c


class Census:
    def __init__(self, canonical, program):
        self.c = canonical
        self.raw = [e for e in program if e[0] != 'climb']
        self.spaces = [span(b) for b in canonical['frames']]
        self.dims = [len(b) for b in canonical['frames']]
        need(all(dim(s) == d and all(0 <= v < 512 for v in s)
                 for s, d in zip(self.spaces, self.dims)), 'All actual frame bases')
        self.occ = {r: [] for r in range(632)}
        for i, e in enumerate(self.raw):
            for r in roles(e):
                self.occ[r].append(i)
        self.joins = {}

    def before(self, i, r):
        k = bisect_left(self.occ[r], i) - 1
        if k < 0:
            return self.c['start'][r]
        e = self.raw[self.occ[r][k]]
        return e[4] if e[0] == 'warp' else e[2]

    def after(self, i, r):
        k = bisect_right(self.occ[r], i)
        if k == len(self.occ[r]):
            return self.c['final'][r]
        e = self.raw[self.occ[r][k]]
        return e[3] if e[0] == 'warp' else e[2]

    def join(self, frames):
        key = tuple(sorted(frames))
        if key not in self.joins:
            self.joins[key] = span(v for f in frames for v in self.c['frames'][f])
        return self.joins[key]

    def candidates(self):
        for i, e in enumerate(self.raw):
            if not eligible(e):
                continue
            for j in range(i + 1, min(i + MAX_DISTANCE + 1, len(self.raw))):
                if j > i + 1:
                    middle = self.raw[j - 1]
                    if not eligible(middle) or not commute(e[1], middle[1]):
                        break
                f = self.raw[j]
                if not eligible(f):
                    break
                if chain(e[1], f[1]):
                    yield i, j

    def run(self):
        stats, deltas, digest = Counter(), Counter(), sha256()
        for i, j in self.candidates():
            e, f = self.raw[i], self.raw[j]
            owners = sorted(set(roles(e) + roles(f)))
            starts = {r: self.before(i, r) for r in owners}
            ends = {r: self.after(j, r) for r in owners}
            old_order = [sorted(set(roles(t)) & set(owners)) for t in self.raw[i:j + 1]]
            old_ranks = [self.dims[t[2]] for t in self.raw[i:j + 1]]
            current = dict(starts)
            for operands, t in zip(old_order, self.raw[i:j + 1]):
                for r in operands:
                    need(self.spaces[current[r]] <= self.spaces[t[2]], 'Actual source containment')
                    current[r] = t[2]
            need(all(self.spaces[current[r]] <= self.spaces[ends[r]] for r in owners), 'Source exits')
            baseline = histogram(old_order, old_ranks,
                                 {r: self.dims[v] for r, v in starts.items()},
                                 {r: self.dims[v] for r, v in ends.items()})
            prefix_current, prefix = dict(starts), Counter()
            for t in self.raw[i + 1:j]:
                for r in sorted(set(roles(t)) & set(owners)):
                    need(self.spaces[prefix_current[r]] <= self.spaces[t[2]], 'Fixed prefix after deletion')
                    rank = self.dims[t[2]] - self.dims[prefix_current[r]]
                    if rank:
                        prefix[rank] += 1
                    prefix_current[r] = t[2]
            kind = 'adjacent' if j == i + 1 else 'nonadjacent'
            stats[kind + '_pairs'] += 1
            k_gate = correction(e[1], f[1])
            for placement in range(3):
                gates = [f[1], e[1]]
                gates.insert(placement, k_gate)
                need(matrix(gates, owners) == matrix([e[1], f[1]], owners), 'Rational corrective identity')
                order = [[r[1] for r in g[1:3]] for g in gates]
                lo1 = self.join([prefix_current[r] for r in order[0]])
                lo2 = self.join(list(prefix_current.values()))
                hi2 = frozenset.intersection(*(self.spaces[ends[r]] for r in owners))
                hi3 = frozenset.intersection(*(self.spaces[ends[r]] for r in order[-1]))
                stats[kind + '_orders'] += 1
                rows = []
                for ranks in triples(lo1, lo2, hi2, hi3):
                    candidate = histogram(order, ranks,
                                          {r: self.dims[v] for r, v in prefix_current.items()},
                                          {r: self.dims[v] for r, v in ends.items()})
                    candidate.update(prefix)
                    slacks = dominance(candidate, baseline)
                    stats[kind + '_rank_triples'] += 1
                    stats['equal' if candidate == baseline else 'strictly_worse'] += 1
                    delta = tuple((r, candidate[r] - baseline[r]) for r in range(1, 10)
                                  if candidate[r] != baseline[r])
                    deltas[delta] += 1
                    rows.append([ranks, sorted(candidate.items()), slacks])
                if not rows:
                    stats[kind + '_infeasible_orders'] += 1
                record = [i, j, placement, sorted(starts.items()), sorted(ends.items()),
                          sorted(baseline.items()), rows]
                digest.update(json.dumps(record, separators=(',', ':')).encode() + b'\n')
        return {'stats': dict(sorted(stats.items())), 'ordered_rows_sha256': digest.hexdigest(),
                'candidate_minus_baseline_deltas': [
                    {'delta': d, 'count': n} for d, n in sorted(deltas.items())]}


def controls():
    rejected = []

    def reject(name, function):
        try:
            function()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('Control accepted: ' + name)

    def gate(a, b, q):
        q = Fraction(q)
        return ['add', ['L', a], ['L', b], q.numerator, q.denominator]

    identities = 0
    for a, b, c in permutations(range(3)):
        for x, y in ((1, 1), (-1, 2), (Fraction(1, 2), Fraction(-3, 4))):
            for g, h in ((gate(a, b, x), gate(b, c, y)), (gate(b, c, x), gate(a, b, y))):
                for place in range(3):
                    word = [h, g]
                    word.insert(place, correction(g, h))
                    need(matrix(word, [0, 1, 2]) == matrix([g, h], [0, 1, 2]), 'Rational toy identity')
                    identities += 1
    g, h = gate(0, 1, 2), gate(1, 2, Fraction(-3, 4))
    reject('omit_correction', lambda: need(matrix([h, g], [0, 1, 2]) == matrix([g, h], [0, 1, 2]), 'Order'))
    bad = correction(g, h)
    bad[3] *= -1
    reject('wrong_correction_sign', lambda: need(matrix([h, g, bad], [0, 1, 2]) == matrix([g, h], [0, 1, 2]), 'Sign'))
    reject('dependent_middle_gate', lambda: need(commute(g, h), 'Middle must commute'))
    reject('equal_dimension_wrong_space', lambda: need(span([1]) <= span([2]), 'Containment'))
    reject('descending_bridge', lambda: histogram([[0, 1]], [0], {0: 1, 1: 0}, {0: 1, 1: 1}))
    reject('omit_exit_charge', lambda: cut_slacks(Counter({1: 3}), Counter({1: 4})))
    old = histogram([[1, 2], [0, 1]], [1, 1], {0: 0, 1: 0, 2: 1}, {0: 1, 1: 2, 2: 2})
    new = histogram([[0, 1], [0, 2], [1, 2]], [0, 1, 2], {0: 0, 1: 0, 2: 1}, {0: 1, 1: 2, 2: 2})
    need(old == {1: 4} and new == {1: 2, 2: 1}, 'Credited improving fixture')
    reject('false_universal_barrier', lambda: dominance(new, old))
    spaces = sorted({span(v for v in range(1, 8) if mask & (1 << (v - 1)))
                     for mask in range(128)}, key=lambda s: (len(s), sorted(s)))
    flags = 0
    for lo1 in spaces:
        for lo2 in spaces:
            if not lo1 <= lo2:
                continue
            for hi2 in spaces:
                if not lo2 <= hi2:
                    continue
                for hi3 in spaces:
                    if not hi2 <= hi3:
                        continue
                    actual = {(dim(a), dim(b), dim(c)) for a in spaces if lo1 <= a
                              for b in spaces if lo2 <= b <= hi2 and a <= b
                              for c in spaces if b <= c <= hi3}
                    need(actual == set(triples(lo1, lo2, hi2, hi3)), 'Exhaustive three-bit flag control')
                    flags += 1
    return {'rational_identity_cases': identities, 'exhaustive_three_bit_flags': flags,
            'rejections': rejected, 'positive_fixture_cut_slacks': cut_slacks(new, old)}


def run():
    raw = (ROOT / SOURCE).read_bytes()
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    row = next(r for r in pins['files'] if r['path'] == SOURCE and r['usage'] == 'input')
    need(sha256(raw).hexdigest() == row['sha256'], 'Frozen source bytes')
    decoded = gzip.decompress(raw)
    need(sha256(decoded).hexdigest() == 'cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd',
         'Frozen logical source')
    payload = json.loads(decoded)
    result = {'status': 'PASS_EXACT_NATIVE_CORRECTIVE_CHAIN_SCREEN',
              'source_payload_sha256': sha256(decoded).hexdigest(),
              'maximum_raw_event_distance': MAX_DISTANCE, 'orientations': {}}
    for direction in ('forward', 'backward'):
        program = payload['programs'][direction]
        paid = Counter(e[5] for e in program if e[0] == 'climb')
        paid.update(e[4] for e in program if e[0] == 'center')
        need(paid == {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8}, 'Complete paid source census')
        result['orientations'][direction] = Census(payload['canonical'], program).run()
    helpers = Counter()
    for r in range(224, 632):
        a, b = payload['canonical']['start'][r], payload['canonical']['final'][r]
        fa, fb = (span(payload['canonical']['frames'][f]) for f in (a, b))
        need(fa < fb, 'Every arbitrary helper boundary remains productive')
        helpers[dim(fb) - dim(fa)] += 1
    need(helpers == {4: 28, 7: 7, 8: 47, 9: 326}, 'Complete helper census')
    result['paid'], result['helpers'] = dict(sorted(paid.items())), dict(sorted(helpers.items()))
    result['controls'] = controls()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Regenerate the deterministic receipt')
    args = parser.parse_args()
    result = run()
    canonical = json.dumps(result, indent=2, sort_keys=True) + '\n'
    path = HERE / 'RESULT.json'
    if args.write:
        path.write_text(canonical)
    else:
        need(json.loads(canonical) == json.loads(path.read_text()), 'Complete frozen receipt')
    print(result['status'], json.dumps({d: r['stats'] for d, r in result['orientations'].items()}, sort_keys=True))


if __name__ == '__main__':
    main()
