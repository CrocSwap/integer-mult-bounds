# SPDX-License-Identifier: Apache-2.0
"""Independent exhaustive-subset frame barrier in F_2^9, without basis routines.

Joins are explicit XOR closures, meets are set intersections. The rejection at
cut c uses only the original entrance and eight centre frames, even though the
optimizer additionally preserves B and restore. It therefore survives arbitrary
reframing of the intervening A gates and every replacement-addition order.
Tekalign with substantial OpenAI Codex assistance.
"""
from functools import lru_cache
from fractions import Fraction as Q
import hashlib
import json
import common as s

FULL = frozenset(range(512))
ZERO = frozenset({0})


@lru_cache(None)
def span(vectors):
    out = {0}
    for v in vectors:
        out |= {x ^ v for x in tuple(out)}
    return frozenset(out)


@lru_cache(None)
def join(left, right):
    out = set(left)
    for v in sorted(right):
        if v not in out:
            out |= {x ^ v for x in tuple(out)}
    return frozenset(out)


def boundaries(word, original, relax_centres=False):
    A, n = word['A'], word['prelude_events']
    cur = [span((p,)) for p in word['ports']] + [ZERO] * 592
    for r, frame in word['start_extra'].items():
        cur[int(r)] = span(tuple(frame))
    for gate in A[:n]:
        if gate[0] == 'warp':
            cur[gate[1]] = span(tuple(gate[4]))
        else:
            for r in gate[1:3] if gate[0] == 'add' else gate[1:2]:
                cur[r] = span(tuple(gate[-1]))
    lower = {n: tuple(cur)}
    for i, gate in enumerate(A[n:], n):
        if i != original:
            roles = gate[1:3] if gate[0] == 'add' else gate[1:2]
            value = ZERO
            for r in roles:
                value = join(value, cur[r])
            for r in roles:
                cur[r] = value
        lower[i + 1] = tuple(cur)
    cur = [FULL] * 704
    if not relax_centres:
        for r, frame in zip(word['centers'], word['center_frames']):
            cur[r] = span(tuple(frame))
    upper = {len(A): tuple(cur)}
    for i in range(len(A) - 1, n - 1, -1):
        if i != original:
            gate = A[i]
            roles = gate[1:3] if gate[0] == 'add' else gate[1:2]
            value = FULL
            for r in roles:
                value = value & cur[r]
            for r in roles:
                cur[r] = value
        upper[i] = tuple(cur)
    return lower, upper


def census(word, target, source, original, first, boundary):
    A = word['A']
    s.require(A[original][:5] == ['add', target, source, 1, 1], 'exact source addition')
    actual_first = 1 + max(i for i, g in enumerate(A[:original])
                           if (g[0] == 'add' and g[2] == target)
                           or (g[0] == 'scale' and g[1] == target))
    s.require(first == actual_first, 'maximal read-only target interval')
    lower, upper = boundaries(word, original)
    row, classes, blocked, feasible = {source: Q(1)}, [], 0, 0
    digest = hashlib.sha256()
    representative = None
    boundary_witness = None
    for cut in range(original, first - 1, -1):
        old = row
        touched = True
        if cut < original:
            g = A[cut]
            row = s.scalar_pull(row, g)
            roles = set(g[1:3] if g[0] == 'add' else g[1:2])
            touched = bool(roles & (set(old) | set(row) | {target}))
        s.require(target not in row, 'source row excludes the accumulator')
        witnesses = [(r, min(lower[cut][target] - upper[cut][r]))
                     for r in sorted(row) if not lower[cut][target] <= upper[cut][r]]
        record = {'cut': cut, 'row': [(r, str(a)) for r, a in sorted(row.items())]}
        if witnesses:
            s.require(cut < boundary, 'no late false rejection')
            blocked += 1
            record['witness'] = witnesses[0]
            if cut == boundary - 1:
                boundary_witness = dict(cut=cut, source=witnesses[0][0], vector=witnesses[0][1],
                                        row=record['row'])
        else:
            s.require(cut >= boundary, 'unexpected earlier feasible cut')
            feasible += 1
            if representative is None or touched:
                representative = cut
                classes.append({'cut': cut, 'row': dict(row)})
            record['representative'] = representative
        digest.update((json.dumps(record, sort_keys=True, separators=(',', ':')) + '\n').encode())
    s.require(blocked == boundary - first and feasible == original - boundary + 1,
              'complete integer cut coverage')
    return {'target': target, 'source': source, 'original_index': original,
            'first_cut': first, 'earliest_legal_cut': boundary,
            'cuts': original - first + 1, 'blocked': blocked, 'surviving': feasible,
            'classes': len(classes), 'census_sha256': digest.hexdigest(),
            'boundary_witness': boundary_witness}, classes


def inverse_column(column, gate):
    """G^{-1} u, paired with scalar_pull's v^T G."""
    out = dict(column)
    if gate[0] == 'add':
        t, source, a, b = gate[1:5]
        out[t] = out.get(t, Q(0)) - Q(a, b) * out.get(source, Q(0))
    else:
        t, a, b = gate[1:4]
        out[t] = out.get(t, Q(0)) * Q(b, a)
    return {r: a for r, a in out.items() if a}


def earlier_transport(word, target, source, original, first):
    """A directed information-path obstruction, even for alternative scalar factorizations.

Only a necessary test. A surviving cut is explicitly unresolved, not feasible.
Auxiliary scalar registers cannot defeat a forbidden source-to-output path;
new warps or changes to the original surrounding word are outside the test.
"""
    lower, upper = boundaries(word, original)
    u, v = {target: Q(1)}, {source: Q(1)}
    digest, rejected, unresolved = hashlib.sha256(), 0, []
    last_witness = None
    for cut in range(original - 1, word['prelude_events'] - 1, -1):
        gate = word['A'][cut]
        u, v = inverse_column(u, gate), s.scalar_pull(v, gate)
        s.require(sum(a * v.get(r, 0) for r, a in u.items()) == 0, 'transported rank-one nilpotence')
        if cut >= first:
            continue
        witnesses = [(r, j, min(lower[cut][j] - upper[cut][r]))
                     for r in sorted(u) for j in sorted(v)
                     if r != j and not lower[cut][j] <= upper[cut][r]]
        record = {'cut': cut, 'u': [(r, str(a)) for r, a in sorted(u.items())],
                  'v': [(r, str(a)) for r, a in sorted(v.items())]}
        if witnesses:
            rejected += 1
            record['witness'] = witnesses[0]
            if last_witness is None:
                last_witness = {'cut': cut, 'destination': witnesses[0][0],
                                'source': witnesses[0][1], 'vector': witnesses[0][2],
                                'nonzero_coefficient': str(u[witnesses[0][0]] * v[witnesses[0][1]])}
        else:
            unresolved.append(cut)
            record['status'] = 'necessary-test-only; unresolved'
        digest.update((json.dumps(record, sort_keys=True, separators=(',', ':')) + '\n').encode())
    s.require(unresolved == [first - 1], 'declared earlier-transport boundary')
    s.require(rejected == first - word['prelude_events'] - 1, 'complete earlier-cut coverage')
    return {'cuts': first - word['prelude_events'], 'rejected': rejected,
            'unresolved_cuts': unresolved, 'census_sha256': digest.hexdigest(),
            'nearest_rejection': last_witness}


def explicit_invoice(word):
    """Full chronological invoice using enumerated vector sets, independent of basis code."""
    from collections import Counter
    cur = [span((p,)) for p in word['ports']] + [ZERO] * 592
    for r, frame in word['start_extra'].items():
        cur[int(r)] = span(tuple(frame))
    start = list(cur)
    end = ([FULL] * 112 +
           [frozenset(v for v in range(512) if (v & p).bit_count() % 2 == 0)
            for p in word['ports']] + [FULL] * 480)
    for r, frame in word['helper_final'].items():
        end[int(r)] = span(tuple(frame))
    paid = Counter()
    def rank(frame):
        return len(frame).bit_length() - 1
    def climb(r, frame):
        s.require(cur[r] <= frame, 'set invoice nonmonotone frame')
        delta = rank(frame) - rank(cur[r])
        if delta:
            paid[delta] += 1
        cur[r] = frame
    def scalar(gate):
        for r in gate[1:3] if gate[0] == 'add' else gate[1:2]:
            climb(r, span(tuple(gate[-1])))
    for gate in word['A']:
        if gate[0] == 'warp':
            s.require(cur[gate[1]] == span(tuple(gate[3])), 'set invoice A warp')
            cur[gate[1]] = span(tuple(gate[4]))
        else:
            scalar(gate)
    for r, given in zip(word['centers'], word['center_frames']):
        frame = span(tuple(given))
        s.require(cur[r] == frame, 'set invoice centre')
        levels = {span(tuple(word['target_levels'].get(str(g[1] - 112), [])))
                  for g in word['cut'] if g[2] == r}
        for level in sorted(levels, key=lambda x: -len(x)):
            s.require(level <= frame, 'set invoice centre descent')
            if level != frame:
                paid[rank(frame) - rank(level)] += 1
            frame = level
    by_position = {}
    for warp in word['warps']:
        by_position.setdefault(warp[0], []).append(warp)
    for pos in range(len(word['B']) + 1):
        for warp in by_position.get(pos, []):
            s.require(cur[warp[1]] == span(tuple(warp[3])), 'set invoice B warp')
            cur[warp[1]] = span(tuple(warp[4]))
        if pos < len(word['B']):
            scalar(word['B'][pos])
    for gate in word['restore']:
        scalar(gate)
    live = set(range(704)) - set(word['removed'])
    for r in live:
        climb(r, end[r])
    inventory = Counter(rank(end[r]) - rank(start[r]) for r in live if r >= 224)
    s.require({str(r): n for r, n in paid.items()} == word['report']['local_profile'], 'set invoice profile')
    s.require({str(r): n for r, n in inventory.items()} == word['report']['width_inventory'], 'set invoice inventory')
