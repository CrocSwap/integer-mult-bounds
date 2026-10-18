#!/usr/bin/env python3
"""Exact internal fixed-grid implementation of one P104 collector. Apache-2.0."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
N = 512
SCALE = 16
ZERO = (0, 0)
SOURCES = ('D31', 'D30', 'D29', 'D28', 'D27')
FRAME = [256, 136, 64, 40, 16, 4, 2, 1]
QUERY_FRAME = [364]
GRID_BITS = [0, 1, 1, 2, 2, 3, 3, 4, 4, 4, 3, 3, 2, 2, 1, 1, 0, 0]
ROW_BOUNDS = [1, 2, 2, 4, 4, 8, 8, 16, 16, 16, 8, 8, 4, 4, 2, 2, 1, 1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate JSON key: ' + key)
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object)


def authenticate():
    pins = read_json(HERE / 'SOURCES.json')['vendored_files']
    need(len(pins) == 3, 'source inventory')
    for pin in pins:
        raw = (HERE / pin['local']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source SHA256: ' + pin['local'])
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(blob == pin['git_blob'], 'source Git blob: ' + pin['local'])


def load_inputs():
    authenticate()
    word = read_json(HERE / 'inputs/WORD.json')
    raw = gzip.decompress((HERE / 'inputs/NATIVE.json.gz').read_bytes())
    native = json.loads(raw, object_pairs_hook=unique_object)
    need(word['chart'] == native['chart'] == 'Delta_W = conjugate(Gamma_W) = Gamma_W^(-T)',
         'physical chart convention')
    program = word['program']
    need(len(program) == 5398, 'source word length')
    frames = {name: list(frame) for name, frame in word['initial_frames'].items()}
    for event in program[:2025]:
        op, target = event[:2]
        if op == 'transport':
            need(frames[target] == event[2], 'prefix transport source frame')
            frames[target] = event[3]
        elif op == 'add':
            need(frames[target] == frames[event[2]] == event[4], 'prefix common ADD frame')
        elif op == 'sign':
            need(frames[target] == event[3] and event[2] in ('-1', '1'), 'prefix sign frame')
        else:
            raise ValueError('unexpected prefix operation')
    need(all(frames[s] == FRAME for s in SOURCES), 'five entrance frames')
    need(frames['Q7'] == QUERY_FRAME, 'query entrance frame')
    expected = ([['zero', 'C', FRAME]]
                + [['add', 'C', s, 1, FRAME] for s in SOURCES]
                + [['transport', 'C', FRAME, QUERY_FRAME, 7],
                   ['add', 'Q7', 'C', '1', QUERY_FRAME],
                   ['transport', 'C', QUERY_FRAME, FRAME, 7]]
                + [['add', 'C', s, '-1', FRAME] for s in reversed(SOURCES)]
                + [['erase', 'C', FRAME]])
    need(program[2025:2040] == expected, 'literal fifteen-event collector')
    recipes = []
    for index in (2031, 2033):
        matches = [item for item in native['transports'] if index in item['events']]
        need(len(matches) == 1, 'unique native event')
        item = matches[0]
        need(program[index] == ['transport', 'C', item['old'], item['new'], 7], 'native frames')
        need(item['recipe']['rank'] == 7, 'native rank')
        recipes.append(item['recipe'])
    return recipes


def rotate(value, phase):
    a, b = value
    phase %= 4
    if phase == 0:
        return a, b
    if phase == 1:
        return -b, a
    if phase == 2:
        return -a, -b
    return b, -a


def plan(record):
    rows = record['matrix_rows']
    linear = record['linear_Z4']
    quadratic = record['quadratic_rows']
    need(len(rows) == len(linear) == len(quadratic) == 9, 'monomial dimension')
    need(all(type(x) is int and 0 <= x < N for x in rows + quadratic), 'binary row')
    need(all(type(x) is int and 0 <= x < 4 for x in linear), 'linear phase')
    need(type(record['offset']) is int and 0 <= record['offset'] < N, 'offset')
    need(type(record['phase']) is int, 'global phase')
    result = []
    for address in range(N):
        target = record['offset']
        phase = record['phase']
        for j in range(9):
            target ^= ((rows[j] & address).bit_count() % 2) << j
            if address & (1 << j):
                phase += linear[j]
                phase += 2 * (quadratic[j] & address & ~((1 << (j + 1)) - 1)).bit_count()
        result.append((target, phase % 4))
    need(sorted(target for target, _ in result) == list(range(N)), 'monomial permutation')
    return result


def monomial(vector, mapping):
    result = [ZERO] * N
    for address in range(N):
        target, phase = mapping[address]
        result[target] = rotate(vector[address], phase)
    return result


def round_half(numerator, guard, exact):
    """Store numerator/2 in units h/16, using the requested nearest-even grid."""
    spacing = 1 << (4 - guard)
    denominator = 2 * spacing
    if exact:
        need(numerator % denominator == 0, 'inexact internal division')
    quotient, remainder = divmod(numerator, denominator)
    rounded = quotient + int(2 * remainder > denominator
                             or (2 * remainder == denominator and quotient % 2))
    return spacing * rounded


def butterfly(vector, bit, guard=4, exact=True):
    step = 1 << bit
    result = [ZERO] * N
    for address in range(N):
        if address & step:
            continue
        a, b = vector[address]
        c, d = vector[address | step]
        numerators = (a - b + c + d, a + b - c + d,
                      a + b + c - d, b - a + c + d)
        values = [round_half(value, guard, exact) for value in numerators]
        result[address] = (values[0], values[1])
        result[address | step] = (values[2], values[3])
    return result


def trace(vector, mappings, guard=4, exact=True):
    right, left = mappings
    stages = [monomial(vector, right)]
    for bit in range(7):
        stages.append(butterfly(stages[-1], bit, guard, exact))
    stages.append(monomial(stages[-1], left))
    return stages


def basis(address, amount=SCALE):
    result = [ZERO] * N
    result[address] = (amount, 0)
    return result


def direct_column(address, mappings):
    """Closed seven-factor coefficient formula, independent of butterfly updates."""
    right, left = mappings
    middle, phase = right[address]
    result = [ZERO] * N
    for low in range(128):
        target, final_phase = left[(middle & ~127) | low]
        distance = ((middle & 127) ^ low).bit_count()
        result[target] = rotate((1, -1), phase + final_phase - distance)
    return result


def inplace_monomial(data, mapping):
    """Cycle execution uses four scalar scratch slots and a 512-bit visited set."""
    visited = 0
    placements = 0
    for origin in range(N):
        if visited & (1 << origin):
            continue
        address = origin
        saved_a, saved_b = data[2 * address:2 * address + 2]
        for _ in range(N):
            target, phase = mapping[address]
            next_a, next_b = data[2 * target:2 * target + 2]
            data[2 * target], data[2 * target + 1] = rotate((saved_a, saved_b), phase)
            saved_a, saved_b = next_a, next_b
            visited |= 1 << address
            placements += 1
            address = target
            if address == origin:
                break
        else:
            raise ValueError('monomial cycle bound exceeded')
    need(visited == (1 << N) - 1 and placements == N, 'complete in-place permutation')


def inplace_native(data, mappings, guard=4):
    """Fixed h/16 integer payload; quantize after every binary pair update."""
    need(len(data) == 2 * N and all(type(x) is int for x in data), 'integer payload shape')
    need(type(guard) is int and 0 <= guard <= 4, 'guard domain')
    inplace_monomial(data, mappings[0])
    for bit in range(7):
        step = 1 << bit
        for address in range(N):
            if address & step:
                continue
            x, y = 2 * address, 2 * (address | step)
            # Four scratch numerators are completed before any payload write.
            p = data[x] - data[x + 1] + data[y] + data[y + 1]
            q = data[x] + data[x + 1] - data[y] + data[y + 1]
            r = data[x] + data[x + 1] + data[y] - data[y + 1]
            s = data[x + 1] - data[x] + data[y] + data[y + 1]
            data[x] = round_half(p, guard, guard == 4)
            data[x + 1] = round_half(q, guard, guard == 4)
            data[y] = round_half(r, guard, guard == 4)
            data[y + 1] = round_half(s, guard, guard == 4)
    inplace_monomial(data, mappings[1])


def column_census(mappings):
    row_sums = [[0] * N for _ in range(18)]
    guards = [0] * 18
    for address in range(N):
        initial = basis(address)
        forward = trace(initial, mappings[0])
        need(forward[-1] == direct_column(address, mappings[0]), 'direct U column')
        standalone_return = trace(initial, mappings[1])[-1]
        need(standalone_return == direct_column(address, mappings[1]), 'direct V column')
        backward = trace(forward[-1], mappings[1])
        need(backward[-1] == initial, 'inverse column')
        data = [component for value in initial for component in value]
        inplace_native(data, mappings[0])
        need(list(zip(data[::2], data[1::2])) == forward[-1], 'in-place U column')
        inplace_native(data, mappings[1])
        need(list(zip(data[::2], data[1::2])) == initial, 'in-place correlated V column')
        for stage, vector in enumerate(forward + backward):
            for row, (a, b) in enumerate(vector):
                row_sums[stage][row] += abs(a) + abs(b)
                for coefficient in (a, b):
                    for bits in range(5):
                        if coefficient % (1 << (4 - bits)) == 0:
                            guards[stage] = max(guards[stage], bits)
                            break
    bounds = [max(rows) for rows in row_sums]
    need(guards == GRID_BITS, 'all-prefix lattice profile')
    need(bounds == [SCALE * bound for bound in ROW_BOUNDS], 'all-prefix row norm profile')
    return guards, ROW_BOUNDS


def add(left, right, coefficient=1):
    return [(a + coefficient * c, b + coefficient * d)
            for (a, b), (c, d) in zip(left, right)]


def native(vector, mappings, guard=4):
    data = [component for value in vector for component in value]
    inplace_native(data, mappings, guard)
    return list(zip(data[::2], data[1::2]))


def collector(initial, mappings, guard=4, exact=True, cleanup_sign=-1):
    value = [ZERO] * N
    for source in SOURCES:
        value = add(value, initial[source])
    need(exact == (guard == 4), 'collector exact/rounded mode')
    outbound = native(value, mappings[0], guard)
    query = add(initial['Q7'], outbound)
    value = native(outbound, mappings[1], guard)
    for source in reversed(SOURCES):
        value = add(value, initial[source], cleanup_sign)
    return value, query


def fixtures_and_controls(mappings):
    zero = [ZERO] * N
    for seed in range(5):
        initial = {name: [(16 * ((x * (j + 3) + seed) % 31 - 15),
                           16 * ((x * x + j + seed) % 29 - 14)) for x in range(N)]
                   for j, name in enumerate(SOURCES + ('Q7',))}
        before = {name: list(vector) for name, vector in initial.items()}
        residue, query = collector(initial, mappings)
        need(residue == zero and initial == before, 'dense dirty restoration')
        expected = list(initial['Q7'])
        for source in SOURCES:
            expected = add(expected, trace(initial[source], mappings[0])[-1])
        need(query == expected, 'dirty query endpoint')
    initial = {name: list(zero) for name in SOURCES + ('Q7',)}
    initial['D31'] = basis(0)
    for guard in range(4):
        residue, query = collector(initial, mappings, guard, exact=False)
        need(query == zero and residue == basis(0, -SCALE), 'insufficient guard witness')
    need(collector(initial, mappings, cleanup_sign=1)[0] != zero, 'cleanup sign control')
    wrong = [list(pair) for pair in mappings]
    wrong[1] = [wrong[1][0], [(target, (phase + 2) % 4) for target, phase in wrong[1][1]]]
    need(collector(initial, wrong)[0] != zero, 'inverse phase control')
    try:
        trace(basis(0, 1), mappings[1])
    except ValueError as error:
        need(str(error) == 'inexact internal division', 'fine-grid control failure reason')
    else:
        raise ValueError('arbitrary fine-grid return unexpectedly accepted')
    return ['guards 0..3', 'cleanup sign', 'inverse phase', 'arbitrary fine-grid return']


def verify():
    recipes = load_inputs()
    mappings = [(plan(recipe['right']), plan(recipe['left'])) for recipe in recipes]
    guards, bounds = column_census(mappings)
    controls = fixtures_and_controls(mappings)
    phases = [0] * 4
    for pair in mappings:
        for mapping in pair:
            for _, phase in mapping:
                phases[phase] += 1
    return dict(status='PASS_P104_INTERNAL_GRID_COLLECTOR',
                native_events=[2031, 2033], real_basis_columns=512,
                correlated_prefix_columns=512 * 18, closed_native_columns=1024,
                prefix_extra_fractional_bits=guards, prefix_real_component_row_bounds=bounds,
                fixed_buffer_extra_fractional_bits=4, exact_query_extra_fractional_bits=4,
                private_extra_storage_bits=4096, query_extra_storage_bits=4096,
                buffer_component_bound='80B', query_component_bound='81B',
                scratch_numerator_bound='320B', pair_scratch_integer_slots=4,
                monomial_visited_bits=512, monomial_plan_payload_bits=2048 * 11,
                binary_pair_updates=14 * 256, real_add_subtracts=14 * 256 * 12 + 11 * 1024,
                exact_real_halvings=14 * 256 * 4, complex_monomial_placements=4 * 512,
                monomial_phase_counts=phases, monomial_real_negations=phases[1] + 2 * phases[2] + phases[3],
                dense_dirty_fixtures=5, controls=controls,
                scope='Fixed 512-coordinate local integer kernel; no recursive-child cost, rounded caller, hosting, supplier or kappa.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.out:
        need(not args.out.exists(), 'output already exists')
    result = verify()
    expected = read_json(HERE / 'RESULT.json')
    # Canonical encoding distinguishes Boolean values from integer counts.
    need(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True), 'complete receipt mismatch')
    if args.out:
        with args.out.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print('PASS_P104_INTERNAL_GRID_COLLECTOR prefixes=9216 guard=4 exact_halvings=14336 no_new_kappa')


if __name__ == '__main__':
    main()
