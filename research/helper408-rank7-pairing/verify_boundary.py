#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact rational scalar-boundary spaces in the free group algebra.

Written independently of the PR2908 auditor/structure implementation. No source
module is imported. The two pinned providers remain the mathematical premises.
"""
import argparse
from collections import defaultdict
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path

Q = Fraction
E7 = (256, 128, 66, 36, 22, 8, 1)
E8 = (256, 128, 64, 36, 20, 8, 2, 1)
EXPECTED_R = (105, 307, 309, 314, 369, 371, 373, 378, 408, 572, 573)
CERTIFICATE_J = (14, 307, 309, 314, 369, 371, 373, 378, 41, 572, 573)
EXPECTED_SHA256 = {
    'base': 'c20a470aec0f3e61833cb41fe190639eb358f58017143d2336c55c80fba265eb',
    'extra': 'db34e39876241087b581ed9374c53e9cd393e3e86ef6103bfb54f3077c3d2761',
}
TRANSFORM_SHA256 = '1d38f0369fce0b892d202ce2e5fd7ea95d9a95d3f80734b672cddd5cb93ce8ca'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def gf2_basis(vectors):
    pivots = {}
    for original in vectors:
        x = original
        while x:
            bit = x.bit_length() - 1
            if bit in pivots:
                x ^= pivots[bit]
            else:
                pivots[bit] = x
                break
    for bit in sorted(pivots):
        for higher in pivots:
            if higher > bit and (pivots[higher] >> bit) & 1:
                pivots[higher] ^= pivots[bit]
    return tuple(pivots[bit] for bit in sorted(pivots, reverse=True))


def contained(a, b):
    return gf2_basis(tuple(a) + tuple(b)) == gf2_basis(b)


def supported_add(destination, source, coefficient):
    for k, c in source.items():
        value = destination.get(k, Q(0)) + coefficient * c
        if value:
            destination[k] = value
        else:
            destination.pop(k, None)


def target(r):
    return 112 <= r < 224


def literal_program(provider):
    """M = restore * B * Aord, chronological list; no target writes."""
    program = list(provider['A'][provider['prelude_events']:])
    warps = defaultdict(list)
    for symbol, record in enumerate(provider['warps'], 1):
        warps[record[0]].append(['warp', record[1], symbol])
    for position in range(len(provider['B']) + 1):
        program.extend(warps[position])
        if position < len(provider['B']):
            program.append(provider['B'][position])
    program.extend(provider['restore'])
    return [g for g in program if g[0] == 'warp' or not target(g[1])]


def replay(provider):
    live = sorted(set(range(704)) - set(provider['removed']) - set(range(112, 224)))
    rows = {r: {(r, ()): Q(1)} for r in live}
    for gate in literal_program(provider):
        kind, destination = gate[:2]
        need(destination in rows, 'destination not in live non-target coordinates')
        if kind == 'add':
            source = gate[2]
            need(source in rows and source != destination, 'invalid scalar source')
            supported_add(rows[destination], rows[source], Q(gate[3], gate[4]))
        elif kind == 'scale':
            coefficient = Q(gate[2], gate[3])
            need(coefficient != 0, 'noninvertible scale')
            rows[destination] = {k: coefficient * c for k, c in rows[destination].items()}
        elif kind == 'warp':
            symbol = gate[2]
            need(symbol != 0, 'invalid free generator')
            image = {}
            for (column, word), c in rows[destination].items():
                # Left multiplication, with only adjacent inverse cancellation.
                reduced = word[1:] if word and word[0] == -symbol else (symbol,) + word
                image[column, reduced] = c
            rows[destination] = image
        else:
            raise ValueError('unknown gate')
    return rows


def terminal_frames(provider):
    """Replay *all* frame incidents, including target writes and warp resets."""
    live = set(range(704)) - set(provider['removed'])
    current = [(p,) for p in provider['ports']] + [()] * 592
    for r, frame in provider['start_extra'].items():
        current[int(r)] = gf2_basis(frame)
    counts = defaultdict(int)

    def climb(register, frame):
        need(register in live, 'frame incident on removed register')
        frame = gf2_basis(frame)
        need(contained(current[register], frame), 'nonmonotone scalar frame')
        current[register] = frame
        counts['scalar_incidents'] += 1

    def step(gate):
        if gate[0] == 'warp':
            _, r, symbol, before, after = gate
            need(current[r] == gf2_basis(before), 'prelude warp frame mismatch')
            need(provider['warps'][abs(symbol) - 1][1] == r, 'prelude lender mismatch')
            current[r] = gf2_basis(after)
            counts['prelude_warps'] += 1
        elif gate[0] == 'add':
            for r in gate[1:3]:
                climb(r, gate[-1])
        elif gate[0] == 'scale':
            climb(gate[1], gate[-1])
        else:
            raise ValueError('unknown frame gate')

    for gate in provider['A']:
        step(gate)
    for r, frame in zip(provider['centers'], provider['center_frames']):
        need(current[r] == gf2_basis(frame), 'center frame mismatch')
    warps = defaultdict(list)
    for record in provider['warps']:
        warps[record[0]].append(record)
    for position in range(len(provider['B']) + 1):
        for _, r, _, before, after in warps[position]:
            need(current[r] == gf2_basis(before), 'B warp frame mismatch')
            current[r] = gf2_basis(after)
            counts['middle_warps'] += 1
        if position < len(provider['B']):
            step(provider['B'][position])
    for gate in provider['restore']:
        step(gate)
    return {r: current[r] for r in sorted(live) if not target(r)}, dict(counts)


def kernel(equations, variables):
    """Complete sparse rational Gaussian elimination; no modular inference."""
    pivots = {}
    nonzero_equations = 0
    for source in equations:
        row = {k: Q(c) for k, c in source.items() if c}
        if not row:
            continue
        nonzero_equations += 1
        while row:
            lead = min(row)
            if lead not in pivots:
                d = row[lead]
                pivots[lead] = {k: c / d for k, c in row.items()}
                break
            supported_add(row, pivots[lead], -row[lead])
    free = [r for r in variables if r not in pivots]
    basis = []
    for f in free:
        vector = {f: Q(1)}
        for p in sorted(pivots, reverse=True):
            value = -sum(c * vector.get(k, Q(0)) for k, c in pivots[p].items() if k != p)
            if value:
                vector[p] = value
        basis.append(vector)
    return basis, {'equations': nonzero_equations, 'rank': len(pivots), 'dimension': len(free)}


def column_image(matrix, vector):
    result = {}
    for r, row in matrix.items():
        polynomial = {}
        for (c, word), coefficient in row.items():
            if c in vector:
                supported_add(polynomial, {word: coefficient}, vector[c])
        if polynomial:
            result[r] = polynomial
    return result


def row_image(matrix, covector):
    result = {}
    for r, coefficient in covector.items():
        supported_add(result, matrix[r], coefficient)
    return result


def scalar_column(image, allowed):
    need(all(r in allowed and set(poly) == {()} for r, poly in image.items()), 'column support/scalar violation')
    return {r: poly[()] for r, poly in image.items()}


def scalar_row(image, allowed):
    need(all(r in allowed and not word for r, word in image), 'row support/scalar violation')
    return {r: coefficient for (r, _), coefficient in image.items()}


def analyze(matrix, H, R):
    H, R = set(H), set(R)
    forward = []
    for r, row in matrix.items():
        byword = defaultdict(dict)
        for (c, word), coefficient in row.items():
            if c in H and (r not in R or word):
                byword[word][c] = coefficient
        forward.extend(byword.values())
    inverse = defaultdict(dict)
    for r in sorted(R):
        for (c, word), coefficient in matrix[r].items():
            if c not in H or word:
                inverse[c, word][r] = coefficient
    V, v_info = kernel(forward, sorted(H))
    Alpha, a_info = kernel(inverse.values(), sorted(R))
    Y = [scalar_column(column_image(matrix, v), R) for v in V]
    U = [scalar_row(row_image(matrix, a), H) for a in Alpha]
    pairing = [[sum(a.get(r, Q(0)) * c for r, c in y.items()) for y in Y] for a in Alpha]
    for i, u in enumerate(U):
        for j, v in enumerate(V):
            need(pairing[i][j] == sum(u.get(r, Q(0)) * c for r, c in v.items()), 'two forms of pairing differ')
    return {'V': V, 'Y': Y, 'Alpha': Alpha, 'U': U, 'pairing': pairing,
            'forward': v_info, 'inverse': a_info}


def encode_vector(vector):
    return {str(k): str(c) for k, c in sorted(vector.items())}


def scalar_change(gates, coordinates):
    matrix = {r: {r: Q(1)} for r in coordinates}
    for gate in gates:
        if gate[0] == 'add':
            need(gate[1] != gate[2], 'self add in calibration')
            supported_add(matrix[gate[1]], matrix[gate[2]], Q(gate[3], gate[4]))
        elif gate[0] == 'scale':
            c = Q(gate[2], gate[3])
            need(c != 0, 'zero scale in calibration')
            matrix[gate[1]] = {r: c * a for r, a in matrix[gate[1]].items()}
        else:
            raise ValueError('nonscalar calibration gate')
    return matrix


def check_pair(matrix, H, R, v, alpha):
    need(set(v) <= set(H), 'input nominee outside H')
    need(set(alpha) <= set(R), 'terminal nominee outside R')
    y = scalar_column(column_image(matrix, v), set(R))
    u = scalar_row(row_image(matrix, alpha), set(H))
    need(sum(alpha.get(r, Q(0)) * c for r, c in y.items()) == 1, 'nonunit witness pairing')
    return y, u


def rejects(action, reason):
    try:
        action()
    except ValueError as error:
        need(str(error) == reason, 'control failed for an unexpected reason: ' + str(error))
        return {'rejected': True, 'reason': reason}
    raise ValueError('invalid witness control was accepted')


def calibrate(matrix, H, frames, transform):
    """Verify the pinned known E52 construction, then break real equations."""
    h = transform['helper']
    need(h == 408, 'calibration helper differs')
    R8 = {r for r in matrix if contained(frames[r], E8)}
    for gate in transform['before']:
        need(gate[-1] == [], 'calibration entrance not zero frame')
        need(set(gate[1:3] if gate[0] == 'add' else gate[1:2]) <= set(H),
             'calibration entrance touches protected register')
    for gate in transform['after']:
        need(gf2_basis(gate[-1]) == E8, 'calibration terminal not E52')
        need(set(gate[1:3] if gate[0] == 'add' else gate[1:2]) <= R8,
             'calibration terminal touches ineligible register')
    S = scalar_change(transform['before'], matrix)
    T = scalar_change(transform['after'], matrix)
    v = {r: row[h] for r, row in S.items() if h in row}
    alpha = T[h]
    y, u = check_pair(matrix, H, R8, v, alpha)
    need(y == {42: Q(2)}, 'known E52 column image differs')
    need(alpha == {408: Q(1), 42: Q(1, 2), 105: Q(1)}, 'known E52 row differs')
    uS = {}
    for r, c in u.items():
        supported_add(uS, S[r], c)
    Ty = {r: sum(c * y.get(k, Q(0)) for k, c in row.items()) for r, row in T.items()}
    Ty = {r: c for r, c in Ty.items() if c}
    need(uS == {h: Q(1)} and Ty == {h: Q(1)}, 'known E52 basis completion fails')
    bad_v = dict(v)
    bad_v[226] += Q(1, 2)  # 1/2 -> 1: changes an actual input coefficient.
    bad_alpha = dict(alpha)
    bad_alpha[42] += Q(1, 2)  # 1/2 -> 1: changes the cancelling output coefficient.
    R7 = {r for r in matrix if contained(frames[r], E7)}
    controls = {
        'input_coefficient_226_half_to_one': rejects(
            lambda: check_pair(matrix, H, R8, bad_v, alpha), 'column support/scalar violation'),
        'output_coefficient_42_half_to_one': rejects(
            lambda: check_pair(matrix, H, R8, v, bad_alpha), 'row support/scalar violation'),
        'unchanged_known_pair_claimed_at_E7': rejects(
            lambda: check_pair(matrix, H, R7, v, alpha), 'terminal nominee outside R'),
    }
    return {
        'status': 'PASS_EXACT_KNOWN_E52_PAIR_AND_BASIS_COMPLETION',
        'eligible_terminal_count': len(R8), 'v': encode_vector(v), 'u': encode_vector(u),
        'alpha': encode_vector(alpha), 'y': encode_vector(y), 'pairing': '1',
        'identities': ['S e408 = v', 'u S = e408^T', 'M v = y', 'alpha M = u',
                       'alpha y = 1', 'T y = e408', 'e408^T T = alpha'],
        'controls': controls,
    }


def diagonal_certificate(matrix, H, R):
    need(tuple(R) == EXPECTED_R, 'eligible set differs from certificate')
    need(not (set(CERTIFICATE_J) & set(H)), 'certificate column allowed in H')
    diagonal = [Q(-1, 2)] + [Q(1)] * 7 + [Q(1, 2), Q(1), Q(1)]
    determinant = Q(1)
    for i, r in enumerate(R):
        for j, c in enumerate(CERTIFICATE_J):
            polynomial = {word: coefficient for (column, word), coefficient in matrix[r].items() if column == c}
            expected = {(): diagonal[i]} if i == j else {}
            need(polynomial == expected, 'exact forbidden-input minor differs')
        determinant *= diagonal[i]
    need(determinant == Q(-1, 4), 'certificate determinant differs')
    return {
        'terminal_rows': list(R), 'forbidden_input_columns': list(CERTIFICATE_J),
        'exact_scalar_diagonal': [str(c) for c in diagonal], 'determinant': str(determinant),
        'nonempty_words_in_minor': 0,
        'conclusion': 'alpha M supported on H forces alpha = 0; no paired extraction',
    }


def operator_digest(matrix):
    terms = [[r, c, list(word), str(a)] for r in sorted(matrix)
             for (c, word), a in sorted(matrix[r].items())]
    return hashlib.sha256(json.dumps(terms, separators=(',', ':')).encode()).hexdigest()


def report(provider, label, transform):
    M = replay(provider)
    frames, frame_counts = terminal_frames(provider)
    protected = (set(map(int, provider['helper_final'])) | set(map(int, provider['start_extra']))
                 | {record['source'] for record in provider['initial_corrections']})
    H = sorted(r for r in M if r >= 224 and r not in protected)
    R = sorted(r for r in M if contained(frames[r], E7))
    need(frames[408] == E7 and 408 in H and 408 in R, 'helper408 boundary differs')
    prelude_lenders = {g[1] for g in provider['A'][:provider['prelude_events']] if g[0] == 'warp'}
    need(not (prelude_lenders & set(H)), 'eligible input helper affected by prelude warp')
    result = analyze(M, H, R)
    need(len(H) == 226 and result['forward']['dimension'] == 0 and result['inverse']['dimension'] == 0,
         'scoped obstruction ranks differ')
    return {
        'variant': label, 'H': H, 'R': R, 'R_frames': {str(r): list(frames[r]) for r in R},
        'frame_replay': frame_counts,
        'non_target_registers': len(M), 'free_operator_terms': sum(map(len, M.values())),
        'middle_gate_count': len(literal_program(provider)),
        'middle_operator_sha256': operator_digest(M),
        'forward': result['forward'], 'inverse': result['inverse'],
        'V': [encode_vector(v) for v in result['V']],
        'Y': [encode_vector(y) for y in result['Y']],
        'Alpha': [encode_vector(a) for a in result['Alpha']],
        'U': [encode_vector(u) for u in result['U']],
        'pairing': [[str(c) for c in row] for row in result['pairing']],
        'pairing_zero': not any(c for row in result['pairing'] for c in row),
        'diagonal_certificate': diagonal_certificate(M, H, R),
        'calibration': calibrate(M, H, frames, transform),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=Path(__file__).resolve().parent / 'sources' / 'data')
    args = parser.parse_args()
    transform_raw = (args.data_dir / 'TRANSFORM.json').read_bytes()
    need(hashlib.sha256(transform_raw).hexdigest() == TRANSFORM_SHA256,
         'calibration transform bytes differ from scientific pin')
    transform = json.loads(transform_raw)
    reports = []
    for label in ('base', 'extra'):
        path = args.data_dir / ('PARENT-' + label + '.json.gz')
        raw = path.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256[label], 'provider bytes differ from scientific pin')
        provider = json.loads(gzip.decompress(raw))
        item = report(provider, label, transform)
        item['input_sha256'] = hashlib.sha256(raw).hexdigest()
        reports.append(item)
    print(json.dumps({
        'status': 'PASS_SCOPED_RANK7_OBSTRUCTION',
        'calibration_transform_sha256': TRANSFORM_SHA256,
        'both_middle_operators_identical': reports[0]['middle_operator_sha256'] == reports[1]['middle_operator_sha256'],
        'reports': reports,
    }, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
