#!/usr/bin/env python3
"""Check the complete local error operator in the three actual native charts."""
from fractions import Fraction as F
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scalar_source as source
import error_operator as op
need, encoded = op.need, source.encoded

for row in json.loads((HERE / 'SOURCES.json').read_text())['files']:
    if row['usage'] == 'input':
        need(sha256((HERE.parents[1] / row['path']).read_bytes()).hexdigest() == row['sha256'], 'retained exact frame input')
path = HERE.parents[1] / 'research/owned-ascent-contract/independent.py'
spec = importlib.util.spec_from_file_location('retained_exact_frames', path)
frames = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frames)
SIZE = 512


def zero():
    return (tuple(F(0) for _ in range(SIZE)), tuple(F(0) for _ in range(SIZE)))


def plus(a, b, q=F(1)):
    return tuple(tuple(x + q * y for x, y in zip(u, v, strict=True)) for u, v in zip(a, b, strict=True))


def norm2(a):
    return sum(x * x for row in a for x in row)


def digest(a):
    return sha256(encoded([[str(x) for x in row] for row in a])).hexdigest()


def mover(descriptions):
    def move(value, start, end):
        if start == end:
            return value
        data = tuple([[x] for x in component] for component in value)
        data, a = frames.apply_frame(data, descriptions[start], -1)
        data, b = frames.apply_frame(data, descriptions[end], 1)
        divisor = 1 << (a + b)
        return tuple(tuple(F(row[0], divisor) for row in component) for component in data)
    return move


def execute(events, sites, initial, residuals, move, omitted=None, phase_fault=None, align=True):
    fields, current = dict(initial), dict(op.INITIAL)
    at = {site['offset']: i for i, site in enumerate(sites)}
    for offset, event in enumerate(events):
        kind, role = event[:2]
        if kind == 'MOVE':
            fields[role] = move(fields[role], event[2], event[3])
            current[role] = event[3]
            if offset == phase_fault:
                fields[role] = plus(zero(), fields[role], F(-1))
        else:
            fields[role] = plus(fields[role], fields[event[2]], F(event[3]))
        if offset in at and at[offset] != omitted:
            fields[role] = plus(fields[role], residuals[at[offset]])
    return [move(fields[role], current[role], 927) if align else fields[role] for role in op.ROLES]


def predicted(matrix, sites, residuals, move):
    aligned = [move(value, site['frame'], 927) for value, site in zip(residuals, sites, strict=True)]
    result = []
    for row in matrix:
        value = zero()
        for q, field in zip(row, aligned, strict=True):
            if q:
                value = plus(value, field, q)
        result.append(value)
    return result


def frame_checks(descriptions):
    identity = ([[int(i == j) for j in range(SIZE)] for i in range(SIZE)], [[0] * SIZE for _ in range(SIZE)])
    results = []
    for chart, description in sorted(descriptions.items()):
        forward, a = frames.apply_frame(identity, description, 1)
        backward, b = frames.apply_frame(forward, description, -1)
        scale = 1 << (a + b)
        need(all(value == scale * int(i == j) for i, row in enumerate(backward[0]) for j, value in enumerate(row)), 'all exact real adjoint columns')
        need(all(value == 0 for row in backward[1] for value in row), 'all exact imaginary adjoint columns')
        results.append({'chart': chart, 'rank': a, 'columns': SIZE,
                        'forward_numerator_sha256': sha256(encoded(forward)).hexdigest(), 'denominator_power': a})
    return results


def field_checks(old, new, binding, derived, certificates):
    descriptions = {int(chart): frames.frame_data(basis) for chart, basis in binding['frames'].items()}
    move = mover(descriptions)
    native = frame_checks(descriptions)
    initial = {role: (tuple(F((i * (j + 1) + j) % (7 + 2 * j) - (3 + j)) for i in range(SIZE)),
                      tuple(F((i + 2 * j) % 5 - 2) for i in range(SIZE))) for j, role in enumerate(op.ROLES)}
    old_matrix, old_sites, _ = derived['old']
    new_matrix, new_sites, _ = derived['new']
    old_exact = execute(old, old_sites, initial, [zero() for _ in old_sites], move)
    new_exact = execute(new, new_sites, initial, [zero() for _ in new_sites], move)
    need(old_exact == new_exact, 'actual native exact output alignment')
    entry = [move(initial[role], op.INITIAL[role], 927) for role in op.ROLES]
    direct = []
    for row in source.MATRIX:
        value = zero()
        for q, field in zip(row, entry, strict=True):
            value = plus(value, field, q)
        direct.append(value)
    need(old_exact == direct, 'rational map in actual aligned charts')
    tests, controls = [], []
    for name, events, matrix, sites in [('old', old, old_matrix, old_sites), ('new', new, new_matrix, new_sites)]:
        high = F(certificates[name]['squared_norm_interval'][1])
        for active in range(len(sites)):
            residuals = [zero() for _ in sites]
            value = [[F(0)] * SIZE for _ in range(2)]
            value[active % 2][(37 + 29 * active) % SIZE] = F((-1) ** active)
            residuals[active] = tuple(map(tuple, value))
            actual = execute(events, sites, initial, residuals, move)
            error = [plus(a, b, F(-1)) for a, b in zip(actual, direct, strict=True)]
            reference = predicted(matrix, sites, residuals, move)
            need(error == reference, 'full-field residual operator')
            error_norm = sum(norm2(field) for field in error)
            need(error_norm == F(certificates[name]['one_port_squared_gains'][active]), 'exact native one-port gain')
            need(error_norm < high * sum(norm2(field) for field in residuals), 'certified joint residual bound')
            tests.append({'tape': name, 'active_port': active, 'squared_output_error': str(error_norm),
                          'output_error_sha256': [digest(field) for field in error]})
            if name == 'new' and active == 1:
                omitted = execute(events, sites, initial, residuals, move, omitted=1)
                need(omitted != actual, 'missing native residual is detected')
                controls.append('omitted x native MOVE residual')
            if name == 'new' and active == 2:
                wrong = [row.copy() for row in matrix]
                wrong[2][active] = F(1)
                need(predicted(wrong, sites, residuals, move) != error, 'lost native amplification is detected')
                controls.append('lost factor two on z native residual')
    wrong_phase = execute(new, new_sites, initial, [zero() for _ in new_sites], move, phase_fault=2)
    need(wrong_phase != direct, 'native global phase fault')
    controls.append('wrong global phase on x native MOVE')
    raw = execute(old, old_sites, initial, [zero() for _ in old_sites], move, align=False)
    need(raw[0] != direct[0], 'old x exit requires chart alignment')
    controls.append('omitted old x exit alignment')
    return {'frames': native, 'single_port_full_field_cases': tests, 'controls': controls,
            'exact_aligned_output_sha256': [digest(field) for field in direct]}


def main():
    old, new, binding = source.sources()
    derived = {'old': op.derive(old, 97747), 'new': op.derive(new, 97842)}
    need(derived['old'][0] == op.OLD and derived['new'][0] == op.NEW, 'independent hand-derived residual matrices')
    need(derived['old'][2] == [751, 927, 751] and derived['new'][2] == [927, 927, 751], 'literal mixed exit charts')
    matrices = {'old': op.OLD, 'new': op.NEW,
                'difference': [a + [-x for x in b] for a, b in zip(op.NEW, op.OLD, strict=True)]}
    certificates = {name: op.spectral_certificate(matrix) for name, matrix in matrices.items()}
    result = {'binding': binding, 'ports': {name: value[1] for name, value in derived.items()},
              'exit_charts': {name: value[2] for name, value in derived.items()},
              'certificates': certificates, 'native': field_checks(old, new, binding, derived, certificates),
              'sharpness_scope': 'arbitrary local residual vectors with a joint squared Euclidean budget; floor reachability is not asserted'}
    file = HERE / 'RESULT.json'
    if sys.argv[1:] == ['--write']:
        need(not file.exists(), 'do not replace checked receipt')
        file.write_text(json.dumps(result, indent=2) + '\n')
    else:
        need(not sys.argv[1:], 'unexpected arguments')
        need(encoded(result) == encoded(json.loads(file.read_text())), 'complete error-operator receipt')
    print('PASS_CURRENT_TRIANGLE_NATIVE_ERROR ' + json.dumps({'native_columns': 1536, 'full_field_ports': 10,
          'controls': len(result['native']['controls']),
          'norm_intervals': {name: row['norm_interval'] for name, row in certificates.items()}}, sort_keys=True))


if __name__ == '__main__':
    main()
