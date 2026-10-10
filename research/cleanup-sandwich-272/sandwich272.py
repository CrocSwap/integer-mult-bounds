"""Remove the cleanup sandwich of 99 helpers in #272's word and check the result on every formal column.

For a selected helper a, the suffix of the word after the first cut contains exactly three gates on a:

    t += a,   a += b,   t += a          (F2, in this order)

and t is not a control strictly between the first and the last. Over F2 the three gates equal

    a += b,   t += b.

`rewrite` moves a += b to the first cut, at the common frame of a and b there, and replaces the middle gate by
t += b at its original position and frame. The helper then has no gate after the cut. It stops at the new
four-dimensional frame instead of climbing to the full frame for cleanup. The emitted word is checked over F2 on
every source, target and dirty column, so the side conditions (b unchanged on the interval, no other use of a) are
verified, not assumed.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import lcm
import struct

H = 24                  # local address dimension
PRIME = 1000003         # Gram ranks are computed modulo this prime: full rank mod p implies full rank over Q
SANDWICH, EARLY = 32, 33  # tags on the two new gates, used by the omission controls


def rational_basis(rows):
    """Reduced integer basis of the rational row space."""
    basis = {}
    for values in rows:
        row = list(map(Q, values))
        for p, b in sorted(basis.items()):
            if row[p]:
                row = [x - row[p] * y for x, y in zip(row, b)]
        p = next((i for i, x in enumerate(row) if x), None)
        if p is not None:
            basis[p] = [x / row[p] for x in row]
    out = []
    for _, row in sorted(basis.items()):
        d = lcm(*(x.denominator for x in row))
        out.append([int(x * d) for x in row])
    return out


def rank_mod_prime(rows):
    basis = {}
    for row in rows:
        row = [x % PRIME for x in row]
        for p, b in sorted(basis.items()):
            if row[p]:
                c = row[p]
                row = [(x - c * y) % PRIME for x, y in zip(row, b)]
        p = next((i for i, x in enumerate(row) if x), None)
        if p is not None:
            inv = pow(row[p], -1, PRIME)
            basis[p] = [x * inv % PRIME for x in row]
    return len(basis)


def annihilator(B):
    """Rational basis of {x : B x = 0} for a reduced basis B."""
    pivots = [next(i for i, x in enumerate(row) if x) for row in B]
    out = []
    for free in sorted(set(range(H)) - set(pivots)):
        v = [Q(i == free) for i in range(H)]
        for p, row in reversed(list(zip(pivots, B))):
            v[p] = -sum(Q(row[j]) * v[j] for j in range(p + 1, H)) / row[p]
        out.append([str(x) for x in v])
    return out


def histogram(records):
    h = Counter()
    for op, a, b, c, f, z in records:
        if op == 0 and f:
            h[f] += 1
        elif op == 2:
            h[z] += 1
    return h


def rewrite(export, lead, helpers):
    """Return (records, new frames, receipt) for the frozen helpers; export and lead are base replay directories."""
    def load(p): return json.loads(p.read_text())
    frames = load(export / 'frames.json')['frames']
    frames.update(load(lead / 'COHORT249-FRAMES.json'))
    states = load(export / '249-states.json')
    initial = {int(a): f for a, f in load(lead / 'COHORT249-INITIAL.json').items()}
    blob = (lead / 'COHORT249-RECORDS.bin').read_bytes()
    old = list(struct.iter_unpack('<6i', blob))
    n, v = states['n'], states['v']

    # Frames of every register at the first cut (the first kernel cut record).
    cut = next(i for i, r in enumerate(old) if r[0] == 1 and r[5] == 3)
    at_cut = dict(initial)
    for op, a, b, c, f, z in old[:cut]:
        if op == 1:
            at_cut[a] = at_cut[b] = f
        elif op == 2:
            at_cut[a], at_cut[b] = c, f
        elif op == 3:
            del at_cut[b]

    edits, skip, replace, new_frames = [], set(), {}, {}
    for a in helpers:
        gates = [(i, r) for i, r in enumerate(old) if i >= cut and r[0] == 1 and a in r[1:3]]
        assert len(gates) == 3, ('helper must have exactly three gates after the cut', a)
        (first, x), (middle, y), (last, w) = gates
        t, b = x[1], y[2]
        assert x[2] == a and y[1] == a and w[1:3] == (t, a), ('not a sandwich t+=a, a+=b, t+=a', a)
        assert all(r[0] != 1 or r[2] != t for r in old[first + 1:last]), ('t is a control inside the sandwich', a)
        assert b not in helpers and t not in helpers, ('overlapping sandwiches', a)
        B = rational_basis(frames[str(at_cut[a])]['B'] + frames[str(at_cut[b])]['B'])
        assert len(B) == 4, ('the joint frame of a and b at the cut is not four-dimensional', a)
        sums = [sum(u) for u in B]
        gram = [[9 * sum(p * q for p, q in zip(u, w)) - su * sw for w, sw in zip(B, sums)] for u, su in zip(B, sums)]
        assert rank_mod_prime(gram) == 4, ('new frame is degenerate for 9I - J', a)
        frame = 600000 + len(new_frames)
        assert str(frame) not in frames
        frames[str(frame)] = new_frames[str(frame)] = {'dim': 4, 'B': B, 'A': annihilator(B)}
        skip.update((first, last))
        replace[middle] = (1, t, b, y[3], y[4], SANDWICH)
        edits.append({'helper': a, 'source': b, 'target': t, 'frame': frame,
                      'old_indices': [first, middle, last], 'entrance_frame': initial[a]})

    # Re-emit the word with explicit frame moves; every new connector is checked for exact rational inclusion.
    state, new, checked = dict(initial), [], set()
    inherited = {(b, c) for op, a, b, c, f, z in old if op == 0}

    def move(a, f):
        before = state[a]
        if before == f:
            return
        if (before, f) not in inherited and (before, f) not in checked:
            B, A = frames[str(before)]['B'], frames[str(f)]['A']
            assert all(sum(Q(p) * Q(q) for p, q in zip(u, w)) == 0 for u in B for w in A), ('not nested', before, f)
            checked.add((before, f))
        rank = frames[str(f)]['dim'] - frames[str(before)]['dim']
        assert rank >= 0, ('frame retreats', a, before, f)
        new.append((0, a, before, f, rank, 0))
        state[a] = f

    def emit(r):
        op, a, b, c, f, z = r
        if op == 1:
            move(a, f)
            move(b, f)
        elif op == 2:
            move(a, c)
            state[b] = f
        elif op == 3:
            assert state[a] == c and state[b] == f
            del state[b]
        new.append(r)

    for i, r in enumerate(old):
        if i == cut:
            for e in edits:
                emit((1, e['helper'], e['source'], 1, e['frame'], EARLY))
        if r[0] != 0 and i not in skip:
            emit(replace.get(i, r))
    final = {int(a): f for a, f in states['final'].items()}
    final.update({e['helper']: e['frame'] for e in edits})
    for a in range(n):
        move(a, final[a])

    def wrong_rows(records, omit=None):
        """F2 formal replay: every register must end as itself, every target as itself plus its source."""
        rows = [1 << a for a in range(n)] + [0]
        for op, a, b, c, f, z in records:
            if op == 1 and c % 2 and z != omit:
                rows[a] ^= rows[b]
            elif op == 2:
                rows[b] = rows[a]
            elif op == 3:
                assert rows[a] == rows[b]
                rows[b] = 0
        return sum(rows[a] != ((1 << a) ^ ((1 << (a - v)) if v <= a < 2 * v else 0)) for a in range(n))

    assert wrong_rows(new) == 0, 'rewritten word fails the formal replay'
    controls = {'omit early a += b': wrong_rows(new, EARLY), 'omit sandwich t += b': wrong_rows(new, SANDWICH)}
    assert all(controls.values()), 'an omission control was accepted'
    delta = histogram(new)
    delta.subtract(histogram(old))
    assert sum(r * c for r, c in delta.items()) == -20 * len(edits), 'endpoint rank mass must drop by 20 per helper'
    data = b''.join(struct.pack('<6i', *r) for r in new)
    receipt = {'helpers_retired': len(edits), 'input_sha256': sha256(blob).hexdigest(),
               'output_sha256': sha256(data).hexdigest(), 'formal_columns': n,
               'omission_controls_wrong_rows': controls, 'new_connectors_checked': len(checked),
               'new_frames': len(new_frames), 'histogram_delta': {str(r): c for r, c in sorted(delta.items()) if c},
               'endpoint_rank_mass_drop': 20 * len(edits), 'edits': edits}
    return data, new_frames, receipt
