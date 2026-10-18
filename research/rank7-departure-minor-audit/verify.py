#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent, bounded audit of PR3114's ten departure obstructions.

No predecessor Python module is imported or executed. Inputs are the two
immutable PR3042 words. See README.md for the proof and exact scope.
Prepared for josecarlosgonzalezroque-design with OpenAI Codex assistance.
"""
import argparse
import gzip
import hashlib
import json
import math
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FULL = frozenset(range(512))
ZERO = frozenset({0})
SPLIT_REGISTERS = (5, 34, 44, 54, 73, 105, 414, 430)
SKIP_REGISTERS = (69, 444)


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def space(vectors):
    out = {0}
    for x in vectors:
        require(type(x) is int and 0 <= x < 512, 'invalid binary vector')
        if x not in out:
            out |= {y ^ x for y in out}
    return frozenset(out)


@lru_cache(None)
def join(a, b):
    return a if b <= a else b if a <= b else space(sorted(a | b))


def dim(s):
    require(len(s) > 0 and len(s) & (len(s) - 1) == 0, 'not a subspace size')
    return len(s).bit_length() - 1


def basis(s):
    """Greedy finite-set basis, ascending, independent of the source RREF."""
    out, seen = [], ZERO
    for x in sorted(s):
        if x not in seen:
            out.append(x)
            seen = join(seen, space([x]))
    require(seen == s, 'not an XOR-closed subspace')
    return out


def all_subspaces(lo, hi):
    require(lo <= hi, 'empty subspace interval')
    seen, pending = {lo}, [lo]
    while pending:
        a = pending.pop()
        for x in sorted(hi - a):
            b = join(a, space([x]))
            if b not in seen:
                seen.add(b)
                pending.append(b)
    return sorted(seen, key=lambda s: (len(s), sorted(s)))


def live(w):
    return sorted(set(range(224 + w['report']['R'])) - set(w['removed']))


def target(r):
    return 112 <= r < 224


def ends(w):
    e = {r: FULL for r in live(w)}
    for i, p in enumerate(w['ports']):
        e[112 + i] = frozenset(x for x in FULL if (x & p).bit_count() % 2 == 0)
    e.update({int(r): space(f) for r, f in w['helper_final'].items()})
    return e


def b_events(w):
    at = {}
    for op, rec in enumerate(w['warps'], 1):
        at.setdefault(rec[0], []).append(['warp', rec[1], op, rec[3], rec[4]])
    require(all(0 <= p <= len(w['B']) for p in at), 'warp position')
    for i in range(len(w['B']) + 1):
        yield from at.get(i, [])
        if i < len(w['B']):
            yield w['B'][i]


def entry_bounds(w, m, end):
    """Set dataflow; cut/warp equalities anchor the last uses.

    Build the whole DAG before propagating. A last-use equality can affect
    later operations on the OTHER operand of that earlier gate. No source
    frame solver, cost function or optimized assignment is used. Backward
    intersections enforce the other operand's subsequent frame constraints.
    """
    nodes, last = [], {}

    def fixed(r, f, parent=None):
        last[r] = len(nodes)
        nodes.append({'parents': [] if parent is None else [parent], 'fixed': f, 'equal': None})

    for r in range(224 + w['report']['R']):
        f = space([w['ports'][r]]) if r < 112 else ZERO
        fixed(r, space(w['start_extra'][str(r)]) if str(r) in w['start_extra'] else f)

    def anchor(r, f):
        node = nodes[last[r]]
        old = node['equal']
        require(old is None or old == f, 'inconsistent last-use equalities')
        node['equal'] = f

    def event(g):
        if g[0] == 'warp':
            anchor(g[1], space(g[3]))
            fixed(g[1], space(g[4]))
            return
        require(g[0] in ('add', 'scale'), 'unknown frame event')
        regs = g[1:3] if g[0] == 'add' else g[1:2]
        k = len(nodes)
        nodes.append({'parents': [last[r] for r in regs], 'fixed': None, 'equal': None})
        for r in regs:
            last[r] = k

    for g in w['A']:
        event(g)
    cuts = list(zip(w['centers'], w['center_frames']))
    cuts += [(112 + i, w['target_levels'].get(str(i), [])) for i in range(112)]
    for r, f in cuts:
        f = space(f)
        anchor(r, f)
        fixed(r, f, last[r])
    for g in b_events(w):
        event(g)
    values = []
    for node in nodes:
        f = ZERO
        for p in node['parents']:
            f = join(f, values[p])
        if node['fixed'] is not None:
            require(f <= node['fixed'], 'fixed frame below its incoming lower bound')
            f = node['fixed']
        if node['equal'] is not None:
            require(f <= node['equal'], 'last-use equality below its lower bound')
            f = node['equal']
        values.append(f)
    ceilings = [FULL for _ in nodes]
    for k, node in enumerate(nodes):
        for f in (node['fixed'], node['equal']):
            if f is not None:
                ceilings[k] &= f
    for r in live(w):
        ceilings[last[r]] &= end[r]
    for c, row in m.items():
        for r, coefficient in row.items():
            if r != c and coefficient:
                ceilings[last[r]] &= end[c]
    # A final shared gate is constrained by the subsequent uses of BOTH
    # operands. Propagate their end/cap/equality constraints backward.
    for k in reversed(range(len(nodes))):
        require(values[k] <= ceilings[k], 'inconsistent frame interval')
        for p in nodes[k]['parents']:
            ceilings[p] &= ceilings[k]
    return ({r: values[last[r]] for r in live(w)},
            {r: ceilings[last[r]] for r in live(w)})


def add_row(a, b, c):
    out = dict(a)
    for k, v in b.items():
        out[k] = out.get(k, Q(0)) + c * v
        if not out[k]:
            del out[k]
    return out


def scalar(g, rows):
    if g[0] == 'add':
        t, s = g[1:3]
        require(t != s and t in rows and s in rows, 'illegal ADD operands')
        rows[t] = add_row(rows[t], rows[s], Q(g[3], g[4]))
    else:
        require(g[0] == 'scale' and g[1] in rows, 'unknown scalar gate')
        c = Q(g[2], g[3])
        require(c != 0, 'noninvertible SCALE')
        rows[g[1]] = {k: c * v for k, v in rows[g[1]].items()}


def forced_coordinates(w):
    """Derive M from restore, then prove its coordinates against the A/B prefix.

    Target writes cannot feed back into non-targets. The non-target prefix is
    a product of invertible ADD/SCALE/free-warp maps, so its rows are independent.
    M*entry = own-input therefore establishes UNIQUE forced coordinates.
    A malformed restore cannot define its own acceptance condition.
    """
    regs = [r for r in live(w) if not target(r)]
    rows = {r: {(r, ()): Q(1)} for r in regs}
    for c in w['initial_corrections']:
        require(target(c['target']), 'correction changes a non-target')
    for g in w['precondition'] + w['compensation'] + w['cut']:
        require(target(g[1]), 'wrapper changes a non-target')
    for g in list(w['A']) + list(b_events(w)):
        if target(g[1]):
            require(g[0] in ('add', 'scale'), 'target warp not covered')
            continue
        if g[0] == 'warp':
            op = g[2]
            require(type(op) is int and op != 0, 'invalid warp symbol')
            changed = {}
            for (r, word), c in rows[g[1]].items():
                word = word[1:] if word and word[0] == -op else (op,) + word
                changed[(r, word)] = c
            rows[g[1]] = changed
        else:
            scalar(g, rows)
    m = {r: {r: Q(1)} for r in regs}
    for g in w['restore']:
        scalar(g, m)
    result = {}
    for c in sorted(map(int, w['helper_final'])):
        row = {}
        for q, coefficient in m[c].items():
            row = add_row(row, rows[q], coefficient)
        require(row == {(c, ()): Q(1)}, f'forced coordinate fails prefix identity for {c}')
        result[c] = m[c]
    return result


def integer_rows(matrix):
    out, scales = [], []
    for row in matrix:
        scale = math.lcm(*(x.denominator for x in row))
        out.append([int(x * scale) for x in row])
        scales.append(scale)
    return out, scales


def pivot_rows(a):
    """Fraction-free row-space basis, retaining original row indices."""
    pivots, selected = {}, []
    for i, row in enumerate(a):
        row = list(row)
        for j, p in sorted(pivots.items()):
            x = row[j]
            if x:
                row = [p[j] * u - x * v for u, v in zip(row, p)]
                g = math.gcd(*row)
                if g:
                    row = [v // g for v in row]
        j = next((j for j, v in enumerate(row) if v), None)
        if j is not None:
            pivots[j] = row
            selected.append(i)
    return selected


def determinant(a):
    """Bareiss determinant of a square integer witness."""
    n = len(a)
    require(n > 0 and all(len(r) == n for r in a), 'minor must be square')
    a, sign, prev = [list(r) for r in a], 1, 1
    for k in range(n - 1):
        p = next((i for i in range(k, n) if a[i][k]), None)
        if p is None:
            return 0
        if p != k:
            a[k], a[p] = a[p], a[k]
            sign = -sign
        pivot = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                v = a[i][j] * pivot - a[i][k] * a[k][j]
                require(v % prev == 0, 'nonexact Bareiss division')
                a[i][j] = v // prev
            a[i][k] = 0
        prev = pivot
    return sign * a[-1][-1]


def kernel_vector(matrix, n):
    """Rational representation for the row-restriction failure control."""
    a = [list(map(Q, r)) for r in matrix]
    used, k = [], 0
    for j in range(n):
        p = next((i for i in range(k, len(a)) if a[i][j]), None)
        if p is None:
            continue
        a[k], a[p] = a[p], a[k]
        c = a[k][j]
        a[k] = [v / c for v in a[k]]
        for i in range(len(a)):
            if i != k and a[i][j]:
                c = a[i][j]
                a[i] = [u - c * v for u, v in zip(a[i], a[k])]
        used.append(j)
        k += 1
    free = next((j for j in range(n) if j not in used), None)
    if free is None:
        return None
    v = [Q(0)] * n
    v[free] = 1
    for i, j in enumerate(used):
        v[j] = -a[i][free]
    return v


def rank_witness(m, lower, end, r, frame):
    z = [r] + [q for q in sorted(lower) if q != r and not target(q) and lower[q] <= frame]
    o = [c for c in sorted(m) if c != r and not end[r] <= end[c]]
    matrix = [[m[c].get(q, Q(0)) for q in z] for c in o]
    ints, scales = integer_rows(matrix)
    chosen = pivot_rows(ints)
    require(len(chosen) == len(z), f'departure matrix not full rank for {r}')
    minor = [ints[i] for i in chosen]
    det = determinant(minor)
    require(det != 0, 'zero witness determinant')
    weak = [row for c, row in zip(o, matrix) if frame <= end[c]]
    null = kernel_vector(weak, len(z))
    require(null is not None, 'row restriction unexpectedly retains full rank')
    require(all(sum(x * y for x, y in zip(row, null)) == 0 for row in weak), 'false kernel witness')
    require(any(sum(x * y for x, y in zip(row, null)) != 0 for row in matrix), 'full rows fail to detect weak-kernel vector')
    return {'register': r, 'frame': basis(frame), 'columns': z,
            'selected_receivers': [o[i] for i in chosen],
            'row_denominator_scales': [scales[i] for i in chosen],
            'integer_minor': minor, 'integer_determinant': det,
            'rational_determinant': str(Q(det, math.prod(scales[i] for i in chosen))),
            'restricted_receivers': [c for c in o if frame <= end[c]],
            'restricted_row_rank': len(pivot_rows(integer_rows(weak)[0])),
            'restricted_row_null_vector': list(map(str, null))}


def inspect_word(w):
    require(w['report']['v'] == 112 and w['report']['h'] == 9, 'unexpected word interface')
    end, m = ends(w), forced_coordinates(w)
    lower, upper = entry_bounds(w, m, end)
    witnesses, no_readers, domains = [], [], []
    for r in SPLIT_REGISTERS + SKIP_REGISTERS:
        require(r not in m and end[r] == FULL, 'expected a non-restored full-ended register')
        receivers = [c for c in m if c != r and m[c].get(r)]
        require(receivers, 'missing receivers')
        cap = end[r]
        for c in receivers:
            cap &= end[c]
        ceiling = cap if r in SPLIT_REGISTERS else cap & upper[r]
        candidates = all_subspaces(lower[r], ceiling)
        if r in SPLIT_REGISTERS:
            require(dim(lower[r]) == 5 and dim(cap) == 7, 'split geometry changed')
            require(lower[r] == upper[r], 'split entry frame is not forced')
            require(not any(q != r and not target(q) and lower[q] <= lower[r] <= end[q]
                            for q in lower), 'split register has an entry-frame reader')
            candidates = [s for s in candidates if dim(s) == 6]
            require(len(candidates) == 3, 'incomplete six-dimensional frame enumeration')
        domains.append({'register': r, 'entry_lower': basis(lower[r]),
                        'receiver_cap': basis(cap), 'entry_upper': basis(upper[r]),
                        'candidate_frames': [basis(s) for s in candidates]})
        local = []
        for frame in candidates:
            readers = [q for q in lower if q != r and not target(q) and lower[q] <= frame <= end[q]]
            if not readers:
                no_readers.append({'register': r, 'frame': basis(frame)})
            else:
                local.append(rank_witness(m, lower, end, r, frame))
        require(len(local) == 1, f'expected one departure rank witness for {r}')
        witnesses.extend(local)
    require(len(no_readers) == 17, 'reader-free frame count changed')
    require(len(lower) - 112 == 520 and len(m) == 91, 'word population changed')
    return {'non_target_prefix_rows': len(lower) - 112, 'restored_coordinates_checked': len(m),
            'domains': domains, 'no_reader_cases': no_readers, 'departure_witnesses': witnesses}


def canonical(x):
    return json.dumps(x, indent=2, sort_keys=True) + '\n'


def decode_word(raw, digest):
    require(hashlib.sha256(raw).hexdigest() == digest, 'source digest mismatch')
    return json.loads(gzip.decompress(raw))


def run():
    manifest = json.loads((HERE / 'SOURCES.json').read_bytes())
    sources = [s for s in manifest['files'] if s['usage'] == 'input']
    require(len(sources) == 2, 'expected the two pinned provider inputs')
    reports = {}
    for s, variant in zip(sources, ('base', 'extra')):
        raw = (ROOT / s['path']).read_bytes()
        reports[variant] = inspect_word(decode_word(raw, s['sha256']))
    require(reports['base'] == reports['extra'], 'provider geometry or obstruction differs')
    return {'status': 'PASS_RANK7_DEPARTURE_MINOR_AUDIT', 'providers': 2,
            'source_pr': 3114, 'source_head': 'c88769c350977d9ed4f90fe5c652d582cfe2782a',
            'scope': 'Ten departure rank obstructions, not the complete restore-optimality theorem or supplier admission.',
            'result': reports['base']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write', action='store_true', help='write the deterministic receipt after all checks')
    args = p.parse_args()
    result = run()
    raw = canonical(result).encode()
    if args.write:
        (HERE / 'RESULT.json').write_bytes(raw)
    else:
        require((HERE / 'RESULT.json').read_bytes() == raw, 'stored receipt differs from recomputation')
    print(result['status'] + ' providers=2 rank_witnesses=20 no_reader_cases=34 restored_coordinates=182')


if __name__ == '__main__':
    main()
