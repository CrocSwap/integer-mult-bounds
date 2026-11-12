"""Exact transport of one public ADD across two successive scalar blockers."""
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from fractions import Fraction as Q
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys

WORD_SHA = '9557c4682056ab7cc7cda89aa73865bef0e3948cc10b3c3061b0a944af05b96a'
GRID = 1125 * 2**25
ROOT = Path(__file__).resolve().parents[3]


def axes(event):
    return event[1:3] if event[0] in ('ADD', 'COPY') else event[1:2]


def update(vector, destination, change):
    if change:
        value = vector.get(destination, 0) + change
        if value:
            vector[destination] = value
        else:
            vector.pop(destination)


def conjugate(u, v, event, later):
    """Later means B(I+uv)B^-1. Earlier means B^-1(I+uv)B."""
    op, destination = event[:2]
    coefficient = Q(event[-2])
    x, y = u.copy(), v.copy()
    if op == 'SCALE':
        factor = coefficient if later else 1 / coefficient
        if destination in x:
            x[destination] *= factor
        if destination in y:
            y[destination] /= factor
    else:
        assert op == 'ADD'
        source = event[2]
        factor = coefficient if later else -coefficient
        update(x, destination, factor * u.get(source, 0))
        update(y, source, -factor * v.get(destination, 0))
    return x, y


def outer(u, v):
    return {(d, s): x * y for d, x in u.items() for s, y in v.items()}


def contacts(program):
    reads, writes, copies = defaultdict(list), defaultdict(list), defaultdict(list)
    for i, event in enumerate(program):
        op, destination = event[:2]
        if op in ('ADD', 'COPY', 'SCALE'):
            writes[destination].append(i)
            reads[destination if op == 'SCALE' else event[2]].append(i)
        if op == 'COPY':
            copies[destination].append(i)
    return reads, writes, copies


def next_contact(program, history, index, u, v, later):
    """Search all possible noncommutations with the current rank-one map."""
    reads, writes, copies = history
    lists = [reads[r] for r in u] + [writes[r] for r in v] + [copies[r] for r in u]
    current = outer(u, v)
    while True:
        if later:
            positions = (bisect_right(row, index) for row in lists)
            index = min((row[k] for row, k in zip(lists, positions) if k < len(row)),
                        default=len(program))
            if index == len(program):
                return index, None
        else:
            positions = (bisect_left(row, index) for row in lists)
            index = max((row[k-1] for row, k in zip(lists, positions) if k), default=-1)
            if index == -1:
                return index, None
        event = program[index]
        if event[0] == 'COPY':
            # An ADD affecting the zero destination also blocks COPY.
            return index, None
        changed = conjugate(u, v, event, later)
        if outer(*changed) != current:
            return index, changed


def coefficient_admissible(value):
    return GRID % value.denominator == 0 and abs(value) + 1 < 2**16


def plans(word, scalar, child, stats=None):
    """Yield ADD index, blockers in crossing order, inclusive cut window and ops."""
    stats = Counter() if stats is None else stats
    program, public = word['program'], word['public']
    history = contacts(program)
    for i in scalar:
        event = program[i]
        if i not in child or event[0] != 'ADD' or max(axes(event)) >= public:
            continue
        stats['public ADD bridges'] += 1
        d, s = axes(event)
        for later in (False, True):
            direction = 'later' if later else 'earlier'
            first, changed = next_contact(program, history, i, {d: Q(event[3])}, {s: Q(1)}, later)
            if changed is None or max(axes(program[first])) >= public:
                stats[f'{direction} stops before first public blocker'] += 1
                continue
            if changed[0].keys() & changed[1].keys():
                stats[f'{direction} first conjugate has overlap'] += 1
            second, final = next_contact(program, history, first, *changed, later)
            if final is None or max(axes(program[second])) >= public:
                stats[f'{direction} stops before second public blocker'] += 1
                continue
            if final[0].keys() & final[1].keys():
                stats[f'{direction} final overlap'] += 1
                continue
            terms = sorted(outer(*final).items())
            if not all(coefficient_admissible(x) for _, x in terms):
                stats[f'{direction} coefficient grid or magnitude excluded'] += 1
                continue
            ops = tuple(('ADD', d, s, str(x)) for (d, s), x in terms)
            next_stop, _ = next_contact(program, history, second, *final, later)
            lo, hi = (second+1, next_stop) if later else (next_stop+1, second)
            assert lo <= hi
            stats[f'{direction} {program[first][0]}/{program[second][0]} plans'] += 1
            stats[f'{direction} {len(ops)}-term plans'] += 1
            yield i, (first, second), lo, hi, ops


def choices(word, raw, scalar, child, stats=None):
    """Yield one representative per distinct raw chart tuple in each safe window."""
    histories = defaultdict(list)
    for j, (role, event, _) in enumerate(raw):
        histories[role].append((event+1, j))
    for history in histories.values():
        history.sort()
    end = len(raw)

    def visit(role, cut):
        h = histories[role]
        return h[bisect_right(h, (cut, end))-1][1]

    for i, blockers, lo, hi, ops in plans(word, scalar, child, stats):
        roles = {role for event in ops for role in axes(event)}
        cuts = {lo}
        for role in roles:
            h = histories[role]
            a, b = bisect_right(h, (lo, end)), bisect_right(h, (hi, end))
            cuts.update(cut for cut, _ in h[a:b])
        for cut in sorted(cuts):
            pairs = tuple((visit(d, cut), visit(s, cut)) for _, d, s, _ in ops)
            if stats is not None:
                stats['placements'] += 1
            yield i, blockers, cut, ops, pairs
