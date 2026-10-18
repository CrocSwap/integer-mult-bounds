"""Separate dense interpreter for the serialized finite transition certificate.

Imports no primary simulator or table builder. Bounds are fixture memory only.
Apache-2.0; ywz65 with OpenAI Codex assistance.
"""
def execute(serial, initial, heads, entry, padding, maximum_steps):
    lookup = {tuple(row[:3]): row[3:] for row in serial}
    lo = min([*heads, *initial[0], *initial[1]]) - padding
    hi = max([*heads, *initial[0], *initial[1]]) + padding
    cells = [['_'] * (hi-lo+1), ['_'] * (hi-lo+1)]
    for k in (0, 1):
        for i, value in initial[k].items():
            cells[k][i-lo] = value
    positions = [heads[0]-lo, heads[1]-lo]
    state = entry
    counters = [0, 0, 0, 0]
    for _ in range(maximum_steps):
        key = (state, cells[0][positions[0]], cells[1][positions[1]])
        state, writes, moves = lookup[key]
        counters[0] += 1
        counters[1] += 2
        for k in (0, 1):
            if writes[k] is not None:
                cells[k][positions[k]] = writes[k]
                counters[2] += 1
            positions[k] += moves[k]
            counters[3] += abs(moves[k])
            if not 0 <= positions[k] < len(cells[k]):
                raise ValueError('dense fixture allocation exceeded')
        if state in ('done', 'reject'):
            return (state,
                    [{i+lo: x for i, x in enumerate(row) if x != '_'} for row in cells],
                    [i+lo for i in positions],
                    dict(zip(('steps', 'reads', 'writes', 'moves'), counters)))
    raise ValueError('dense fixture step budget exceeded')
