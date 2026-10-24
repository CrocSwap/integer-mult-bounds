"""Check the fixed pair on every independent input and count its gates.

This code adapts the history and residual-syndrome exact replay methods.
New code uses Apache-2.0. OpenAI Codex assisted this work.
"""

from collections import Counter
from fractions import Fraction as Q


MODES = (225, 226, 229, 232, 241, 242, 257, 258)
WIDTH = 704


def need(value, message):
    if not value:
        raise ValueError(message)


def add(target, source, coefficient=1):
    for key, value in source.items():
        value = target.get(key, 0) + coefficient * value
        if value:
            target[key] = value
        else:
            target.pop(key, None)


def line(row, port, exponent):
    """Prepend one port line. Use only its exact order-four relation."""
    result = {}
    for (column, word), value in row.items():
        power = exponent % 4
        if word and word[0][0] == port:
            power = (power + word[0][1]) % 4
            word = word[1:]
        if power:
            word = ((port, power),) + word
        add(result, {(column, word): value})
    return result


def compose(matrix, rows):
    result = []
    for coefficients in matrix:
        row = {}
        for index, value in coefficients.items():
            add(row, rows[index], value)
        result.append(row)
    return result


def core_frames(events, word):
    current = word['start'].copy()
    for event in events:
        if event[0] == 'climb':
            need(current[event[2]] == event[3], 'Core climb input frame')
            current[event[2]] = event[4]
        elif event[0] == 'scalar':
            gate, frame = event[1:]
            need(gate[0] in ('add', 'scale') and gate[1][0] == 'L',
                 'Core uses invertible scalar gates and no private field')
            need(current[gate[1][1]] == frame, 'Core scalar target frame')
            if gate[0] == 'add':
                need(gate[2][0] == 'L' and current[gate[2][1]] == frame,
                     'Core scalar source frame')
    need(current == word['final'], 'Core final frames')


def endpoint(events, rows, word, where):
    result = [row.copy() for row in rows]
    bank, power = (0, 1) if where == 'input' else (112, -1)
    for rep in range(2):
        for p in range(112):
            i = rep * WIDTH + bank + p
            result[i] = line(result[i], p, power)
    frames = word['start' if where == 'input' else 'final']
    for event in events:
        need(event['endpoint'] == where, 'Wrapper endpoint tag')
        rep, slot = event['target']
        need(rep in (0, 1) and (0 <= slot < 224 or slot in MODES),
             'Wrapper target is data or mode')
        target = rep * WIDTH + slot
        if event['kind'] == 'physical_translation':
            need(slot < 224 and word['ports'][slot % 112] == event['label'],
                 'Translation uses its own port')
            result[target] = line(result[target], slot % 112, 2)
        else:
            need(event['kind'] == 'physical_add', 'Known wrapper operation')
            r, source = event['source']
            need(r in (0, 1) and (0 <= source < 224 or source in MODES),
                 'Wrapper source is data or mode')
            need(event['target_frame'] == frames[slot]
                 and event['source_frame'] == frames[source],
                 'Recorded physical endpoint frames')
            add(result[target], result[r * WIDTH + source], Q(event['coefficient']))
    for rep in range(2):
        for p in range(112):
            i = rep * WIDTH + bank + p
            result[i] = line(result[i], p, -power)
    return result


def run_pair(parts, core_map, rows, word):
    result = endpoint(parts['prefix'], rows, word, 'input')
    middle = []
    for rep in range(2):
        middle.extend(compose(core_map, result[rep * WIDTH:(rep + 1) * WIDTH]))
    return endpoint(parts['suffix'], middle, word, 'output')


def gap_query(rows, bank, r):
    result = []
    for rep in range(2):
        other, power = 1 - rep, 1 if rep == 0 else -1
        for row in r:
            value = {}
            for p, coefficient in row.items():
                add(value, rows[rep * WIDTH + bank + p], coefficient)
                add(value, line(rows[other * WIDTH + bank + p], p, power), -coefficient)
            result.append(value)
    return result


def gap_injection(modes, k):
    result = []
    for rep in range(2):
        other, power = 1 - rep, 1 if rep == 0 else -1
        for p, row in enumerate(k):
            value = {}
            for j, coefficient in row.items():
                add(value, modes[8 * rep + j], coefficient)
                add(value, line(modes[8 * other + j], p, power), coefficient)
            result.append(value)
    return result


def formula(rows, direction, r, k, inverse=False):
    result = [row.copy() for row in rows]
    bank, beta = (0, Q(1)) if direction == 'forward' else (112, Q(1, 8))
    query = gap_query(rows, bank, r)
    old = [rows[rep * WIDTH + slot] for rep in range(2) for slot in MODES]
    modes = []
    for initial, value in zip(old, query):
        modes.append({key: -x for key, x in initial.items()})
        add(modes[-1], value, -beta)
    for rep in range(2):
        for j, slot in enumerate(MODES):
            result[rep * WIDTH + slot] = modes[8 * rep + j]
    injection_modes = old if direction == 'forward' and inverse else modes
    if direction == 'backward' and not inverse:
        injection_modes = old
    injection = gap_injection(injection_modes, k)
    for rep in range(2):
        for p in range(112):
            x, y = rep * WIDTH + p, rep * WIDTH + 112 + p
            if direction == 'forward':
                coefficient = -1 if inverse else 1
                add(result[y], rows[x], coefficient)
                add(result[y], injection[112 * rep + p], coefficient)
            else:
                coefficient = 1 if inverse else -1
                add(result[x], rows[y], coefficient)
                add(result[x], injection[112 * rep + p], 8 * coefficient)
    return result


def verify(local, cores, packet, source):
    word = local['CANONICAL-WORD.json.gz']
    original = local['LOCAL-PROGRAMS.json.gz']
    need((word['v'], word['R'], word['h']) == (112, 480, 9), 'Source geometry')
    need(packet['mode_carriers_per_replica'] == list(MODES), 'Actual promoted roles')
    boundary = source.replay(original['forward'], cut=original['forward'].index(['phase', 'centers']))
    r = [{p: q for p, q in boundary[c].items() if p < 112} for c in word['centers']]
    k = [{j: row[p] / 4 for j, row in enumerate(r) if p in row} for p in range(112)]
    need(source.product(r, k) == [{j: Q(14)} for j in range(8)], 'R K is 14 I')
    need(sum(map(len, r)) == 448, 'All 448 centre incidences')
    need(all(word['start'][slot] == 0 and word['final'][slot] == 1 for slot in MODES),
         'Modes have I to F endpoints')
    projection = source.product(k, r)
    identity = [{i: Q(1)} for i in range(WIDTH)]
    formal_identity = [{(i, ()): Q(1)} for i in range(2 * WIDTH)]
    reports = {}
    for direction in ('forward', 'backward'):
        events = cores[direction]
        core_frames(events, word)
        native = lambda stream: [e for e in stream if e[0] in ('climb', 'adapter', 'residual_adapter')]
        need(native(events) == native(original[direction]), 'Original native events retained')
        need(len(native(events)) == 5056, 'Core native event count')
        need(not any(e[0] == 'center' for e in events), 'Centre children removed')
        profile = Counter(e[5] for e in events if e[0] == 'climb')
        need(dict(profile) == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82}, 'Core rank profile')
        core_cost = 2 * sum(source.primitive_bound(e[1]) for e in events if e[0] == 'scalar')
        need(core_cost == 204418, 'Full core scalar allowance')
        all_rows = source.replay(events)
        need(all_rows[WIDTH:] == [{i: Q(1)} for i in range(WIDTH, WIDTH + 8)],
             'Private centres preserved by non-use')
        actual = all_rows[:WIDTH]
        expected = [row.copy() for row in identity]
        for p in range(112):
            if direction == 'forward':
                add(expected[112 + p], {p: Q(1)})
                add(expected[112 + p], projection[p], -1)
                add(expected[112 + p], {MODES[j]: q for j, q in k[p].items()}, -1)
            else:
                add(expected[p], {112 + p: Q(1)}, -1)
                add(expected[p], {112 + j: q for j, q in projection[p].items()}, -1)
                add(expected[p], {MODES[j]: q for j, q in k[p].items()}, -8)
        for j, slot in enumerate(MODES):
            expected[slot] = {slot: Q(-1)}
            add(expected[slot], {p if direction == 'forward' else 112 + p: q for p, q in r[j].items()},
                -2 if direction == 'forward' else -Q(1, 4))
        need(actual == expected, 'Every core input column: ' + direction)
        suffix = next(i for i, e in enumerate(events) if e == ['phase', 'mode_output_basis'])
        bad = events[:suffix] + [e for e in events[suffix:] if e[0] != 'scalar']
        need(source.replay(bad)[:WIDTH] != expected, 'Missing output basis control')
        parts = packet['programs'][direction]
        need(parts['core_invocations'] == [{'replica': rep, 'orientation': direction} for rep in range(2)],
             'Both cores have the required order')
        pair_rows = run_pair(parts, actual, formal_identity, word)
        desired = formula(formal_identity, direction, r, k)
        need(pair_rows == desired, 'Every paired input column: ' + direction)
        for rep in range(2):
            need(all(pair_rows[rep * WIDTH + j] == formal_identity[rep * WIDTH + j]
                     for j in range(224, WIDTH) if j not in MODES), 'Arbitrary ordinary helpers restored')
        need(formula(pair_rows, direction, r, k, True) == formal_identity, 'Inverse after pair')
        need(run_pair(parts, actual, formula(formal_identity, direction, r, k, True), word)
             == formal_identity, 'Pair after inverse')
        controls = {'missing input graph': {'prefix': [], 'suffix': parts['suffix']},
                    'missing translations': {side: [e for e in parts[side] if e['kind'] != 'physical_translation']
                                             for side in ('prefix', 'suffix')}}
        if direction == 'backward':
            controls['mode preload before old-mode read'] = {
                'prefix': parts['prefix'][-896:] + parts['prefix'][:-896], 'suffix': parts['suffix']}
        else:
            controls['target correction before mode update'] = {
                'prefix': parts['prefix'], 'suffix': parts['suffix'][896:] + parts['suffix'][:896]}
        for label, mutant in controls.items():
            need(run_pair(mutant, actual, formal_identity, word) != desired, 'Mutation rejected: ' + label)
        wrapper = parts['prefix'] + parts['suffix']
        adds = [e for e in wrapper if e['kind'] == 'physical_add']
        cost = 0
        for event in adds:
            q = Q(event['coefficient'])
            cost += 2 * source.primitive_bound(['add', ['L', 0], ['L', 1], q.numerator, q.denominator])
        need(len(adds) == 2688 and len(wrapper) - len(adds) == 448, 'Complete wrapper counts')
        need(cost == (25088 if direction == 'forward' else 34048), 'Added scalar allowance')
        reports[direction] = {
            'core_input_columns': WIDTH, 'pair_input_columns': 2 * WIDTH,
            'arbitrary_mode_inputs': 16, 'restored_ordinary_helpers': 944,
            'private_fields': 'No access; arbitrary values are preserved',
            'core_scalar_allowance': core_cost, 'added_scalar_allowance': cost,
            'complete_scalar_allowance': 2 * core_cost + cost,
            'physical_ADDs': len(adds), 'literal_translation_maps': len(wrapper) - len(adds),
            'retained_native_events': 2 * len(native(events)), 'retained_native_rank_mass': 11044,
            'added_native_children': 0, 'both_algebraic_inverse_orders': 'PASS',
            'negative_controls': ['missing output basis', *controls],
        }
    return {'status': 'PASS_EXACT_ORIGINAL_PAIRED_MAPS', 'orientations': reports}, r, k
