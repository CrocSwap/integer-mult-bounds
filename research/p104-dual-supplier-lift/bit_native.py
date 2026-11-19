"""Build and verify eight causal punctures in the selected binary native word. Apache-2.0."""
from collections import Counter, defaultdict
from hashlib import sha256
from heapq import heapify, heappop, heappush
import gzip
import json

NATIVE = 'research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz'
NATIVE_SHA = '51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78'
# Each row names the original public owner and three zero-based MOVE ordinals.
# Remove the first two MOVEs. Add the second sender's row into the third sender.
PUNCTURES = (
    (633, 2323, 2657, 1599), (638, 2342, 2669, 1617),
    (646, 2381, 2695, 1634), (640, 2453, 2743, 1621),
    (649, 2496, 2771, 1646), (636, 2497, 2773, 1609),
    (651, 2513, 2783, 1662), (635, 2532, 2795, 1608),
)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def indices(value):
    while value:
        first = value & -value
        yield first.bit_length() - 1
        value ^= first


def combine(row, values):
    result = 0
    for source in indices(row):
        result ^= values[source]
    return result


def read_pinned(root, path, expected):
    raw = (root / path).read_bytes()
    need(sha256(raw).hexdigest() == expected, 'source digest for ' + str(path))
    return json.loads(gzip.decompress(raw))


def extract(source):
    public = source['public']
    initial = dict(enumerate(source['start']))
    final = dict(enumerate(source['final']))
    rows, moves, clocks = {}, {}, {}
    banks = [1 << i for i in initial] + [0]*source['owned_fields']
    for clock, (op, r, *args) in enumerate(source['program']):
        if op == 'ADD':
            banks[r] ^= banks[args[0]]
        elif op in ('INIT', 'CLEAR'):
            banks[r] = 0
        elif op == 'SWAP':
            s, = args
            banks[r], banks[s] = banks[s], banks[r]
        else:
            need(op == 'MOVE', 'original binary instruction')
            k = public + len(moves)
            rows[k], moves[k], clocks[k] = banks[r], tuple(args), clock
            banks[r] = 1 << k
    rows.update({~r: banks[r] for r in final})
    return initial, final, moves, rows, clocks


def schedule(initial, final, moves, rows):
    chart = initial.copy()
    chart.update({k: arrival for k, (_, arrival) in moves.items()})
    need(rows.keys() == moves.keys() | {~r for r in final}, 'every packet and terminal has one row')
    count, uses = {}, defaultdict(list)
    for k, row in rows.items():
        here = moves[k][0] if k >= 0 else final[~k]
        parents = list(indices(row))
        need(all(chart.get(j) == here for j in parents), 'every XOR donor has the current rational chart')
        if k >= 0:
            count[k] = sum(j in moves for j in parents)
            for j in parents:
                if j in moves:
                    uses[j].append(k)
    ready = [k for k in moves if not count[k]]
    heapify(ready)
    order = []
    while ready:
        k = heappop(ready)
        order.append(k)
        for child in uses[k]:
            count[child] -= 1
            if not count[child]:
                heappush(ready, child)
    need(len(order) == len(moves), 'causal binary packet schedule')
    return order


def basis(initial, moves, rows, order):
    values = {r: 1 << r for r in initial}
    for k in order:
        values[k] = combine(rows[k], values)
    for r in initial:
        target = 1 << r
        if 111 <= r < 222:
            target ^= 1 << (r-111)
        need(combine(rows[~r], values) == target, 'complete binary public transfer')
    # A pulse in a delivered packet gives this column at all outputs.
    columns = {j: 0 for j in initial.keys() | moves.keys()}
    for r in initial:
        for j in indices(rows[~r]):
            columns[j] ^= 1 << r
    for k in reversed(order):
        for j in indices(rows[k]):
            columns[j] ^= columns[k]
    for r in initial:
        expected = 1 << r
        if r < 111:
            expected ^= 1 << (r+111)
        need(columns[r] == expected, 'complete transposed binary public transfer')
    return columns


def puncture(initial, final, moves, rows, r, zero, alias, donor, send=True):
    initial, final, moves = initial.copy(), final.copy(), moves.copy()
    del initial[r], final[r], moves[zero], moves[alias]
    erased = (1 << r) | (1 << zero) | (1 << alias)
    new_rows = {k: row & ~erased for k, row in rows.items() if k not in (~r, zero, alias)}
    if send:
        new_rows[donor] ^= rows[alias] & ~erased
    return initial, final, moves, new_rows


def emit_word(source, initial, final, moves, rows, order):
    owners = sorted(initial)
    public = len(owners)
    location = {r: i for i, r in enumerate(owners)}
    program = []
    def accumulate(scratch, chart, row):
        program.append(['INIT', scratch, chart])
        program.extend(['ADD', scratch, location[j], chart] for j in indices(row))
    for i, k in enumerate(order):
        a, b = moves[k]
        scratch = public+i
        accumulate(scratch, a, rows[k])
        program.append(['MOVE', scratch, a, b])
        location[k] = scratch
    output_base = public + len(moves)
    for i, r in enumerate(owners):
        accumulate(output_base+i, final[r], rows[~r])
    # Exchange the full contents and chart tags only after all output sums are ready.
    for i, r in enumerate(owners):
        program.append(['SWAP', i, output_base+i])
        program.append(['CLEAR', output_base+i, initial[r]])
    for k in order:
        program.append(['CLEAR', location[k], moves[k][1]])
    return dict(schema='BIT-functional-GL-kernel-native/1', public=public,
                owned_fields=len(moves)+public, frames=source['frames'], start=[initial[r] for r in owners],
                final=[final[r] for r in owners], program=program)


def build(root):
    source = read_pinned(root, NATIVE, NATIVE_SHA)
    initial, final, moves, rows, clocks = extract(source)
    start = source['public']
    need((start, len(moves), len(source['frames'])) == (659, 2871, 636), 'selected native inventory')
    order = schedule(initial, final, moves, rows)
    columns = basis(initial, moves, rows, order)
    trace = []
    for index, (r, *ordinals) in enumerate(PUNCTURES):
        zero, alias, donor = [start+i for i in ordinals]
        need(columns[zero] == 1 << r and columns[alias] ^ columns[donor] == 1 << r,
             'both exact transpose equations for the surrendered helper')
        need(moves[alias][0] == moves[donor][0] and clocks[donor] < clocks[alias],
             'same sender bank and later donor in the old reverse order')
        trace.append(dict(role=r, original_move_ordinals=ordinals, original_word_clocks=[clocks[k] for k in (zero,alias,donor)],
                          paid_routes=[list(moves[k]) for k in (zero,alias,donor)],
                          original_public_boundary=[initial[r], final[r]]))
        if index == 0:
            bad = puncture(initial, final, moves, rows, r, zero, alias, donor, send=False)
            try:
                basis(bad[0], bad[2], bad[3], schedule(*bad))
            except ValueError as error:
                need(str(error) == 'complete binary public transfer', 'changed-sender control failure')
            else:
                raise ValueError('missing sender XOR accepted')
        initial, final, moves, rows = puncture(initial, final, moves, rows, r, zero, alias, donor)
        order = schedule(initial, final, moves, rows)
        columns = basis(initial, moves, rows, order)
    word = emit_word(source, initial, final, moves, rows, order)
    receipt = dict(punctures=trace, checked_prefix_public_dimensions=list(range(659,650,-1)),
                   surviving_original_owners=sorted(initial), program_sha256=digest(word),
                   scalar_rows_per_orientation=len(initial), final_public_coefficients=len(initial)**2,
                   paid_packets=len(moves), largest_sender_xor=max(v.bit_count() for v in rows.values()),
                   instruction_counts=dict(Counter(e[0] for e in word['program'])),
                   changed_sender_control_rejected=True)
    return word, receipt
