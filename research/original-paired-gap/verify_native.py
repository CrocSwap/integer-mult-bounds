"""Check exact line phases, actual routes, and physical wrapper groups.

This code adapts the coherent-port review and PR #1969 route calculation.
New code uses Apache-2.0. OpenAI Codex assisted this work.
"""

from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import json


AXES = tuple(1 << j for j in range(73))
MODES = (225, 226, 229, 232, 241, 242, 257, 258)


def need(value, message):
    if not value:
        raise ValueError(message)


def act(columns, vector):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= columns[bit.bit_length() - 1]
        vector ^= bit
    return result


def routes_from_source(phases, ports):
    need(phases['m'] == 73 and len(phases['recipes']) == 112, 'Actual phase source dimensions')
    result = []
    for p, record in enumerate(phases['recipes']):
        basis = tuple([record['q']] + record['idle_children'][0]['orthogonal_axes'][:8]) + AXES[9:]
        need(record['port'] == p and basis[0] == ports[p], 'Actual source port and normal')
        need(all((basis[i] & basis[j]).bit_count() % 2 == (i == j)
                 for i in range(73) for j in range(73)), 'Actual source orthogonal chart')
        beta = sum(1 << i for i, value in enumerate(basis[1:9]) if (value.bit_count() - 1) // 2 % 2)
        stages = []
        for stage in range(9):
            if stage == 0:
                columns, entry, exit_value = AXES, 0, 0
            else:
                swaps = [basis[i + 1] ^ AXES[9 + 8 * (stage - 1) + i] for i in range(8)]
                columns = tuple(value ^ act(swaps, sum(((value & axis).bit_count() % 2) << i
                                                       for i, axis in enumerate(swaps))) for value in AXES)
                entry = ports[p] ^ act(basis[1:9], beta)
                exit_value = act(basis[1:9], beta) ^ (beta << (9 + 8 * (stage - 1)))
            shifts = {'entry_X': entry, 'entry_Y': entry, 'exit_X': exit_value, 'exit_Y': exit_value}
            need(record['stage_alignment'][stage] == shifts, 'Original entry and exit translations')
            need(tuple(act(columns, col) for col in columns) == AXES, 'Actual route inverse')
            need(act(columns, ports[p]) == ports[p], 'Actual route fixes its native line')
            stages.append({'matrix_columns': list(columns), 'translations': shifts})
        result.append({'port': p, 'basis': list(basis), 'stages': stages})
    return result


def mono(recipe, address):
    exponent = recipe['phase']
    for i in range(9):
        if address >> i & 1:
            exponent += recipe['linear_Z4'][i]
            exponent += 2 * ((recipe['quadratic_rows'][i] & address) >> (i + 1)).bit_count()
    result = recipe['offset']
    for i, row in enumerate(recipe['matrix_rows']):
        result ^= ((row & address).bit_count() % 2) << i
    return result, exponent % 4


def gaussian_mul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def line_column(recipe, address):
    moved, phase = mono(recipe['right'], address)
    result = {}
    for point, value in ((moved, (1, 1)), (moved ^ 1, (1, -1))):
        final, extra = mono(recipe['left'], point)
        result[final] = gaussian_mul(value, ((1, 0), (0, 1), (-1, 0), (0, -1))[(phase + extra) % 4])
    return result


def check_lines(lines, ports):
    need([item['port'] for item in lines['recipes']] == list(range(112)), 'All positive line recipes once')
    count = 0
    for item in lines['recipes']:
        p, recipe = item['port'], item['recipe']
        q = ports[p]
        need(item['label'] == q and recipe['rank'] == 1, 'Native line and rank')
        columns = [line_column(recipe, x) for x in range(512)]
        for x, column in enumerate(columns):
            need(column == {x: (1, 1), x ^ q: (1, -1)}, 'Exact positive line kernel and phase')
            square = {}
            for z, value in column.items():
                for y, other in columns[z].items():
                    a, b = square.get(y, (0, 0)), gaussian_mul(value, other)
                    square[y] = a[0] + b[0], a[1] + b[1]
            square = {y: value for y, value in square.items() if value != (0, 0)}
            need(square == {x ^ q: (4, 0)}, 'C squared is the translation, including phase')
            need({y ^ q: value for y, value in column.items()}
                 == {x: (1, -1), x ^ q: (1, 1)}, 'Exact inverse line')
            need((x ^ q) ^ q == x, 'Exact fourth power')
            count += 1
        altered = deepcopy(recipe)
        altered['left']['phase'] = (altered['left']['phase'] + 1) % 4
        need(line_column(altered, 0) != {0: (1, 1), q: (1, -1)}, 'Wrong global phase control')
    return count


def wrapper_groups(packet, word, r):
    def event(rt, target, rs, source, coefficient, endpoint):
        frames = word['start' if endpoint == 'input' else 'final']
        return {'kind': 'physical_add', 'target': [rt, target], 'source': [rs, source],
                'coefficient': str(coefficient), 'endpoint': endpoint,
                'target_frame': frames[target], 'source_frame': frames[source]}

    def read(rt, rs, offset, scale, endpoint):
        return [event(rt, MODES[k], rs, offset + p, scale * r[k][p], endpoint)
                for k in range(8) for p in range(112) if p in r[k]]

    def scatter(rt, rs, offset, scale, endpoint):
        return [event(rt, offset + p, rs, MODES[k], scale * r[k][p] / 4, endpoint)
                for p in range(112) for k in range(8) if p in r[k]]

    def translate(replica, offset, endpoint):
        return [{'kind': 'physical_translation', 'target': [replica, offset + p],
                 'label': word['ports'][p], 'endpoint': endpoint} for p in range(112)]

    expected = {
        'forward': {
            'prefix': [read(0, 1, 0, -1, 'input'), translate(0, 0, 'input'),
                       read(1, 0, 0, -1, 'input'), translate(0, 0, 'input')],
            'suffix': [read(0, 0, 0, 1, 'output'), read(1, 1, 0, 1, 'output'),
                       scatter(0, 1, 112, 1, 'output'), translate(1, 112, 'output'),
                       scatter(1, 0, 112, 1, 'output'), translate(1, 112, 'output')],
        },
        'backward': {
            'prefix': [translate(0, 0, 'input'), scatter(0, 1, 0, -8, 'input'),
                       translate(0, 0, 'input'), scatter(1, 0, 0, -8, 'input'),
                       read(0, 0, 112, -Q(1, 8), 'input'), read(1, 1, 112, -Q(1, 8), 'input')],
            'suffix': [translate(1, 112, 'output'), read(0, 1, 112, Q(1, 8), 'output'),
                       translate(1, 112, 'output'), read(1, 0, 112, Q(1, 8), 'output')],
        },
    }
    encode = lambda value: json.dumps(value, sort_keys=True)
    for direction, parts in expected.items():
        for side, groups in parts.items():
            actual = packet['programs'][direction][side]
            offset = 0
            for group in groups:
                need(Counter(map(encode, actual[offset:offset + len(group)])) == Counter(map(encode, group)),
                     'Every physical graph, coefficient, frame, and boundary is exact')
                offset += len(group)
            need(offset == len(actual), 'No operation outside the specified physical groups')
    return sum(len(groups) for parts in expected.values() for groups in parts.values())


def verify(local, lines, packet, r):
    word = local['CANONICAL-WORD.json.gz']
    ports = word['ports']
    for p, label in enumerate(ports):
        need(word['frames'][word['start'][p]] == [label], 'Input X has its exact canonical line')
        need(word['start'][112 + p] == 0 and word['final'][p] == 1,
             'Input Y and output X have the required common endpoints')
        vectors = word['frames'][word['final'][112 + p]]
        pivots = {}
        for vector in vectors:
            need((vector & label).bit_count() % 2 == 0, 'Output Y space is perpendicular to its line')
            while vector:
                bit = vector.bit_length() - 1
                if bit not in pivots:
                    pivots[bit] = vector
                    break
                vector ^= pivots[bit]
        need(len(pivots) == len(vectors) == 8, 'Output Y has the exact rank-eight complement')
        need(lines['recipes'][p]['canonical_start_frame_id'] == word['start'][p],
             'Native line recipe binds the actual input frame')
    groups = wrapper_groups(packet, word, r)
    columns = check_lines(lines, ports)
    routes = routes_from_source(local['DATA-PHASES.json'], ports)
    checks = 0
    for item in routes:
        p, basis = item['port'], item['basis']
        for stage, record in enumerate(item['stages']):
            g = record['matrix_columns']
            if stage:
                for delta in record['translations'].values():
                    for z in (0, *AXES):
                        need(act(g, z ^ ports[p]) ^ delta == act(g, z) ^ delta ^ ports[p],
                             'Affine route commutes with its line translation')
                        checks += 1
        swapped = tuple(value ^ (basis[0] ^ basis[1])
                        if (value & (basis[0] ^ basis[1])).bit_count() % 2 else value for value in AXES)
        need(act(swapped, ports[p]) != ports[p], 'Wrong owner direction control')
    need(columns == 57344 and checks == 265216, 'Complete line and affine census')
    raw = json.dumps(routes, sort_keys=True, separators=(',', ':')).encode()
    return {
        'status': 'PASS_ORIGINAL_PAIRED_NATIVE_COMPONENTS',
        'exact_line_spatial_columns': columns, 'phase_mutation_controls': 112,
        'actual_stage_port_routes': 1008, 'affine_translation_checks': checks,
        'ordered_physical_groups': groups, 'wrong_owner_direction_controls': 112,
        'derived_route_sha256': sha256(raw).hexdigest(),
        'tensor_scope': 'Exact line identity and owner-dependent covariance tensor to every positive depth',
        'inherited': 'Old core native kernels and complete helper interface; no fresh old-core kernel sweep',
    }
