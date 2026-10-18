#!/usr/bin/env python3
"""Exact output-covector audit of the pinned selected JP8 scalar programs.

Prepared for Sagar Thakrar with substantial OpenAI Codex assistance.
Apache-2.0. No production checker or constructor is imported.
"""

import gzip
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V, N, CENTRES = 112, 716, 8


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def load_inputs():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for path, expected in pins['files_sha256'].items():
        require(digest((ROOT / path).read_bytes()) == expected, 'source pin: ' + path)
    selected = json.loads((ROOT / 'certificates/selected-result.json').read_text())
    manifest = json.loads((ROOT / selected['source_manifest']).read_text())
    spec_path = 'research/complex-k492-owner-repair/data/SPEC.json'
    require(manifest['files'][spec_path] == pins['files_sha256'][spec_path], 'selected SPEC binding')
    for pr, head in pins['reviewed_heads'].items():
        require(selected['reviewed_dependency_heads'][pr] == head, 'reviewed head: ' + pr)
    spec = json.loads((ROOT / spec_path).read_text())
    require(sorted(spec['providers'])[pins['assignment_seed'] % 2] == 'jp8', 'seed selection')
    provider = spec['providers']['jp8']
    loaded = []
    for kind, artifact in [('programs', 'LOCAL-PROGRAMS.json.gz'), ('word', 'CANONICAL-WORD.json.gz')]:
        payload = gzip.decompress((ROOT / pins[kind + '_path']).read_bytes())
        expected = pins[kind + '_payload_sha256']
        require(digest(payload) == expected, 'payload pin: ' + kind)
        require(provider['artifact_semantic_sha256'][artifact] == expected, 'SPEC artifact: ' + kind)
        loaded.append(json.loads(payload))
    programs, word = loaded
    require((word['v'], word['R']) == (V, N - 2 * V), 'word dimensions')
    require(set(programs) == {'forward', 'backward'}, 'program orientations')
    for name, events in programs.items():
        require(digest(canonical(events)) == provider['program_hashes'][name], 'SPEC program: ' + name)
    return programs, word


def register(value):
    require(isinstance(value, list) and len(value) == 2, 'register shape')
    bank, index = value
    require(type(index) is int, 'register index type')
    require((bank == 'L' and 0 <= index < N) or
            (bank == 'C' and 0 <= index < CENTRES), 'register range')
    return index if bank == 'L' else N + index


def decode(events):
    """Retain literal event indices and phase names for mutation witnesses."""
    result, phase = [], None
    for index, event in enumerate(events):
        tag = event[0]
        if tag == 'phase':
            phase = event[1]
        elif tag == 'scalar':
            op = event[1]
            kind, target = op[0], register(op[1])
            require(kind in {'add', 'scale', 'copy', 'clear'}, 'unknown scalar operation')
            require(len(op) == {'add': 5, 'scale': 4, 'copy': 3, 'clear': 2}[kind], 'scalar arity')
            source = register(op[2]) if kind in {'add', 'copy'} else None
            require(source != target, 'self read/write')
            coefficient = Fraction(1)
            if kind in {'add', 'scale'}:
                a, b = op[-2:]
                require(type(a) is int and type(b) is int and b != 0, 'coefficient syntax')
                coefficient = Fraction(a, b)
                require(coefficient != 0, 'zero coefficient')
                denominator = coefficient.denominator
                require(denominator & (denominator - 1) == 0, 'non-dyadic coefficient')
                if kind == 'scale':
                    numerator = abs(coefficient.numerator)
                    require(numerator & (numerator - 1) == 0, 'nonbinary scale')
            result.append((kind, target, source, coefficient, index, phase))
        else:
            # These describe frame/wrapper transport, outside the scalar projection.
            require(tag in {'adapter', 'residual_adapter', 'climb', 'center'}, 'unknown event')
    return result


def pullback(operations, output):
    """Pull one output linear functional back to all arbitrary input coordinates."""
    covector = {output: Fraction(1)}
    for kind, target, source, coefficient, _, _ in reversed(operations):
        weight = covector.get(target)
        if not weight:
            continue
        if kind == 'scale':
            covector[target] = weight * coefficient
        else:
            if kind in {'copy', 'clear'}:
                del covector[target]
            if kind in {'add', 'copy'}:
                value = covector.get(source, 0) + weight * coefficient
                if value:
                    covector[source] = value
                else:
                    covector.pop(source, None)
    return covector


def expected_row(direction, output):
    if output >= N:
        return {}
    row = {output: Fraction(1)}
    if direction == 'forward' and V <= output < 2 * V:
        row[output - V] = Fraction(1)
    elif direction == 'backward' and output < V:
        row[output + V] = Fraction(-1)
    return row


def coordinate(index):
    return ['L', index] if index < N else ['C', index - N]


def direct_basis_value(operations, input_coordinate, output):
    """Scalar-value replay of one witness, independent of covector propagation."""
    values = [Fraction(0)] * (N + CENTRES)
    values[input_coordinate] = Fraction(1)
    for kind, target, source, coefficient, _, _ in operations:
        if kind == 'add':
            values[target] += coefficient * values[source]
        elif kind == 'scale':
            values[target] *= coefficient
        elif kind == 'copy':
            values[target] = values[source]
        elif kind == 'clear':
            values[target] = Fraction(0)
    return values[output]


def check_program(direction, operations):
    rows = []
    for output in range(N + CENTRES):
        actual = pullback(operations, output)
        require(actual == expected_row(direction, output), f'endpoint mismatch: {direction} {coordinate(output)}')
        rows.append([[j, str(q)] for j, q in sorted(actual.items())])
    return {
        'scalar_operations': len(operations),
        'operation_counts': dict(sorted(Counter(op[0] for op in operations).items())),
        'input_coordinates': N + CENTRES,
        'output_coordinates_checked': len(rows),
        'persistent_outputs': N,
        'private_outputs': CENTRES,
        'nonzero_matrix_entries': sum(map(len, rows)),
        'output_covectors_sha256': digest(canonical(rows)),
    }


def omission_witness(direction, operations, operation_index):
    dropped = operations[operation_index]
    mutant = operations[:operation_index] + operations[operation_index + 1:]
    for output in range(N + CENTRES):
        actual = pullback(mutant, output)
        expected = expected_row(direction, output)
        for input_coordinate in sorted(actual.keys() | expected.keys()):
            a, e = actual.get(input_coordinate, 0), expected.get(input_coordinate, 0)
            if a != e:
                require(direct_basis_value(mutant, input_coordinate, output) == a, 'witness forward replay')
                require(direct_basis_value(operations, input_coordinate, output) == e, 'baseline witness replay')
                return {
                    'direction': direction, 'event_index': dropped[4], 'phase': dropped[5],
                    'operation': [dropped[0], coordinate(dropped[1]),
                                  coordinate(dropped[2]) if dropped[2] is not None else None, str(dropped[3])],
                    'input_basis_coordinate': coordinate(input_coordinate),
                    'output_coordinate': coordinate(output), 'expected': str(e), 'actual': str(a),
                }
    raise ValueError('omission control did not change the scalar map')


def dirty_centre_gap(operations, operation_index):
    """Check the whole omitted-clear defect, including its invisible L-only restriction."""
    dropped = operations[operation_index]
    require(dropped[0] == 'clear' and dropped[1] == N, 'C0 initial clear')
    mutant = operations[:operation_index] + operations[operation_index + 1:]
    defect = []
    for output in range(N + CENTRES):
        actual = pullback(mutant, output)
        expected = expected_row('backward', output)
        require({j: q for j, q in actual.items() if j < N} == expected,
                'mutant changed L-input restriction')
        require(all(j < N or j == N for j in actual), 'unexpected dirty-centre dependency')
        if N in actual:
            defect.append([output, str(actual[N])])
    require(defect and all(output < N for output, _ in defect), 'persistent-only nonzero defect')
    return {'event_index': dropped[4], 'input_coordinate': ['C', 0],
            'all_716_L_input_columns_unchanged': True, 'all_private_outputs_zero': True,
            'nonzero_output_coefficients': defect,
            'defect_rank': 1}


def self_check():
    # Overwriting a dirty destination must kill its former input coefficient.
    ops = [('copy', 1, 0, Fraction(1), 0, 'test'),
           ('add', 2, 1, Fraction(3, 2), 1, 'test'),
           ('scale', 2, None, Fraction(-2), 2, 'test'),
           ('clear', 1, None, Fraction(1), 3, 'test')]
    require(pullback(ops, 0) == {0: 1}, 'self-check identity')
    require(pullback(ops, 1) == {}, 'self-check clear')
    require(pullback(ops, 2) == {0: -3, 2: -2}, 'self-check mixed operations')


def compute():
    self_check()
    programs, word = load_inputs()
    decoded = {name: decode(events) for name, events in programs.items()}
    checks = {name: check_program(name, ops) for name, ops in decoded.items()}
    forward, backward = decoded['forward'], decoded['backward']
    first = lambda ops, predicate: next(i for i, op in enumerate(ops) if predicate(op))
    copy_index = first(forward, lambda op: op[0] == 'copy')
    final_clear_index = next(i for i in range(copy_index + 1, len(forward))
                             if forward[i][0] == 'clear' and forward[i][1] == forward[copy_index][1])
    backward_clear_index = first(backward, lambda op: op[0] == 'clear')
    controls = [
        ('forward_compensation', 'forward', len(word['precondition'])),
        ('forward_early_cleanup', 'forward', first(forward, lambda op: op[5] == 'cleanup_tail')),
        ('forward_full_cleanup', 'forward', first(forward, lambda op: op[5] == 'full_frame_cleanup')),
        ('forward_centre_copy', 'forward', copy_index),
        ('forward_final_centre_clear', 'forward', final_clear_index),
        ('backward_initial_centre_clear', 'backward', backward_clear_index),
    ]
    require(forward[len(word['precondition'])][5] == 'zero_frame_precondition', 'compensation location')
    witnesses = {name: omission_witness(direction, decoded[direction], index)
                 for name, direction, index in controls}
    require(witnesses['backward_initial_centre_clear']['input_basis_coordinate'][0] == 'C', 'dirty-centre control')
    return {'status': 'PASS_JP8_ADJOINT_RESTORATION', 'supplier': 'jp8',
            'checks': checks, 'omission_witnesses': witnesses,
            'dirty_centre_gap': dirty_centre_gap(backward, backward_clear_index),
            'scope': 'Exact finite scalar projection; frames, wrappers, costs and all-size interfaces are inherited.'}


def main():
    require(sys.argv[1:] in ([], ['--report']), 'usage: verify.py [--report]')
    report = compute()
    require(report == json.loads((HERE / 'EXPECTED.json').read_text()), 'certificate mismatch')
    if sys.argv[1:]:
        print(json.dumps(report, indent=2, sort_keys=True))
    print('PASS_JP8_ADJOINT_RESTORATION outputs=724x2 inputs=724 controls=6 kappa=unchanged')


if __name__ == '__main__':
    main()
