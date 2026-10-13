"""Paid common-frame deferred SWAP lowering; ToikY / Codex, Apache-2.0.

Historical scalar projections only. Native physical admission is not supplied.
"""
from fractions import Fraction as Q

WORK = ('W', 0)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def swapped_pair(events, i):
    """Two literal chronological representations of an exact transposition."""
    block = events[i:i + 4]
    if len(block) != 4 or any(e[0] != 'scalar' or e[2] != block[0][2] for e in block):
        return None
    ops = [e[1] for e in block]
    if [op[0] for op in ops] != ['add', 'add', 'add', 'scale']:
        return None
    a, b = tuple(ops[0][1]), tuple(ops[0][2])
    if a == b or a[0] != 'L' or b[0] != 'L':
        return None
    if tuple(ops[1][1]) != b or tuple(ops[1][2]) != a:
        return None
    if tuple(ops[2][1]) != a or tuple(ops[2][2]) != b:
        return None
    q = Q(*ops[0][3:5])
    if q not in (-1, 1) or Q(*ops[1][3:5]) != -q or Q(*ops[2][3:5]) != q:
        return None
    if Q(*ops[3][2:4]) != -1 or tuple(ops[3][1]) != (b if q == 1 else a):
        return None
    return a, b


def scalar_runs(events):
    runs = []
    i = 0
    while i < len(events):
        if events[i][0] != 'scalar':
            i += 1
            continue
        start, frame = i, events[i][2]
        while i < len(events) and events[i][0] == 'scalar' and events[i][2] == frame:
            i += 1
        runs.append((start, i, frame))
    return runs


def materialize(locations, work=WORK):
    """Output slot r receives the current slot locations[r], all costs paid."""
    require(work not in locations and set(locations) == set(locations.values()), 'invalid permutation')
    pending = {r for r, s in locations.items() if r != s}
    word, cycles = [], []
    while pending:
        first = min(pending)
        cycle, cursor = [first], locations[first]
        while cursor != first:
            require(cursor in pending and cursor not in cycle, 'invalid cycle')
            cycle.append(cursor)
            cursor = locations[cursor]
        word.append(('copy', work, first))
        for target, source in zip(cycle, cycle[1:]):
            word.append(('copy', target, source))
        word.append(('copy', cycle[-1], work))
        pending.difference_update(cycle)
        cycles.append(cycle)
    # Original swap's unit ADDs erase arbitrary coefficient dirt. This clear
    # is required even when several swaps compose to the identity.
    word.append(('clear', work))
    return word, cycles


def remap(op, locations):
    op = list(op)
    op[1] = locations.get(tuple(op[1]), tuple(op[1]))
    if op[0] in ('add', 'copy'):
        op[2] = locations.get(tuple(op[2]), tuple(op[2]))
    return op


def compile_block(events, start, end, lower):
    require(0 <= start < end <= len(events), 'invalid block')
    frame = events[start][2]
    require(all(e[0] == 'scalar' and e[2] == frame for e in events[start:end]), 'frame/event barrier')
    locations, primitives, swaps = {}, [], []
    i = start
    while i < end:
        pair = swapped_pair(events, i) if i + 4 <= end else None
        if pair is not None:
            a, b = pair
            locations.setdefault(a, a)
            locations.setdefault(b, b)
            locations[a], locations[b] = locations[b], locations[a]
            swaps.append(i)
            i += 4
        else:
            primitives.extend(lower(remap(events[i][1], locations), WORK))
            i += 1
    cycles = []
    if swaps:
        restore, cycles = materialize(locations)
        primitives.extend(restore)
    return {'start': start, 'end': end, 'frame': frame, 'swap_starts': swaps,
            'permutation': [[list(r), list(s)] for r, s in sorted(locations.items())],
            'cycles': [[list(r) for r in c] for c in cycles], 'primitives': primitives}


def compile_program(events, lower):
    return [compile_block(events, a, b, lower) for a, b, _ in scalar_runs(events)]
