#!/usr/bin/env python3
"""Independent finite checker of the fixed PR681 factory map.

Prepared for Ross Richardson with substantial OpenAI Codex assistance.
Apache-2.0. Credits: Alluri's PR681 matrix/window evidence, Jeremy Kothe's
PR622 supplier, Sagar Thakrar's PR696 lowering, and its credited predecessors.
No producer, search, repository verifier, or lowering implementation is imported.
This is a finite local calculation, not a formal multiplication theorem proof.
"""
import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REFERENCE = HERE.parent / 'complex-factory5-resynthesis' / 'CIRCUIT.json'
N = 8
WORK = 8


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def power_two(value):
    return value > 0 and value & (value - 1) == 0


def dyadic(numerator, denominator=1):
    """Return (integer, exponent), representing integer / 2**exponent."""
    require(type(numerator) is int and type(denominator) is int,
            'coefficients must be integers')
    require(denominator != 0, 'zero denominator')
    if denominator < 0:
        numerator, denominator = -numerator, -denominator
    # Reduce a rational before requiring a dyadic denominator.
    from math import gcd
    common = gcd(abs(numerator), denominator)
    numerator, denominator = numerator // common, denominator // common
    require(power_two(denominator), 'coefficient is not dyadic')
    exponent = denominator.bit_length() - 1
    while exponent and numerator % 2 == 0:
        numerator //= 2
        exponent -= 1
    return numerator, exponent


def add(left, right):
    exponent = max(left[1], right[1])
    value = (left[0] << (exponent-left[1])) + (right[0] << (exponent-right[1]))
    return dyadic(value, 1 << exponent)


def multiply(left, right):
    return dyadic(left[0]*right[0], 1 << (left[1]+right[1]))


def fraction(value):
    return Fraction(value[0], 1 << value[1])


def span(frame):
    values = {0}
    for direction in frame:
        require(type(direction) is int and direction > 0, 'invalid frame direction')
        values |= {x ^ direction for x in values}
    return values


def coefficient(event):
    return dyadic(*event[3:5]) if event[0] == 'add' else dyadic(*event[2:4])


def validate_events(events, frame):
    require(isinstance(events, list) and events, 'empty event word')
    touched = set()
    for event in events:
        require(isinstance(event, list) and event, 'invalid event')
        require(event[0] in ('add', 'scale'), 'unknown event')
        require(len(event) == (6 if event[0] == 'add' else 5), 'wrong event arity')
        registers = event[1:3] if event[0] == 'add' else event[1:2]
        require(all(type(r) is int and 0 <= r < N for r in registers),
                'invalid or aliased private register')
        require(event[-1] == frame, 'changed gate frame')
        touched.update(registers)
        numerator, _ = coefficient(event)
        require(numerator != 0, 'zero coefficient')
        if event[0] == 'add':
            require(event[1] != event[2], 'self addition')
        else:
            require(power_two(abs(numerator)), 'scale is not a signed power of two')
    require(touched == set(range(N)), 'not every physical register reaches the frame')


def macro_columns(events):
    """Replay one input basis column at a time with scaled integers."""
    columns = []
    for basis in range(N):
        state = [(int(i == basis), 0) for i in range(N)]
        for event in events:
            target, q = event[1], coefficient(event)
            if event[0] == 'add':
                state[target] = add(state[target], multiply(q, state[event[2]]))
            else:
                state[target] = multiply(q, state[target])
        columns.append([fraction(value) for value in state])
    return columns


def invert_matrix(matrix):
    """Gauss-Jordan inversion only of the independently retained target matrix."""
    rows = [list(row) + [Fraction(i == j) for j in range(N)]
            for i, row in enumerate(matrix)]
    for column in range(N):
        pivot = next((i for i in range(column, N) if rows[i][column]), None)
        require(pivot is not None, 'singular target matrix')
        rows[column], rows[pivot] = rows[pivot], rows[column]
        divisor = rows[column][column]
        rows[column] = [value / divisor for value in rows[column]]
        for other in range(N):
            if other != column:
                factor = rows[other][column]
                rows[other] = [a-factor*b for a, b in zip(rows[other], rows[column])]
    return [row[N:] for row in rows]


def transpose(matrix):
    return [list(column) for column in zip(*matrix)]


def oriented(events, mode):
    """Derive each scalar word directly from elementary-matrix identities."""
    result = copy.deepcopy(events)
    if mode in ('inverse', 'transpose'):
        result.reverse()
    for event in result:
        if mode in ('inverse', 'inverse_transpose'):
            if event[0] == 'add':
                event[3] = -event[3]
            else:
                event[2], event[3] = event[3], event[2]
        if mode in ('transpose', 'inverse_transpose') and event[0] == 'add':
            event[1], event[2] = event[2], event[1]
    return result


def lower(events, scheme):
    """One real component; copy/clear/double/halve/negate/signed-add cost one."""
    require(scheme in ('historical_horner', 'pr696'), 'unknown lowering')
    primitives = []
    for event in events:
        target, (numerator, exponent) = event[1], coefficient(event)
        sign = 1 if numerator > 0 else -1
        magnitude = abs(numerator)
        if event[0] == 'scale':
            shift = magnitude.bit_length()-1-exponent
            # Each scheme follows its own published operation ordering.
            if sign < 0 and scheme == 'historical_horner':
                primitives.append(('negate', target))
            primitives.extend([('double' if shift > 0 else 'halve', target)] * abs(shift))
            if sign < 0 and scheme == 'pr696':
                primitives.append(('negate', target))
            continue
        source = event[2]
        if scheme == 'pr696' and magnitude == 1 and exponent == 0:
            primitives.extend([('add', target, source, sign), ('clear', WORK)])
            continue
        if scheme == 'historical_horner':
            primitives.append(('clear', WORK))
            remaining = bin(magnitude)[2:]
            for index, bit in enumerate(remaining):
                if index:
                    primitives.append(('double', WORK))
                if bit == '1':
                    primitives.append(('add', WORK, source, 1))
        else:
            primitives.append(('copy', WORK, source))
            for bit in bin(magnitude)[3:]:
                primitives.append(('double', WORK))
                if bit == '1':
                    primitives.append(('add', WORK, source, 1))
        primitives.extend([('halve', WORK)] * exponent)
        primitives.extend([('add', target, WORK, sign), ('clear', WORK)])
    return primitives


def primitive_columns(primitives):
    result = []
    # Include a dirty private input basis separately: arbitrary incoming private
    # work must be erased, and must not affect any data output.
    for basis in range(N+1):
        state = [(int(i == basis), 0) for i in range(N+1)]
        for event in primitives:
            tag, target = event[:2]
            if tag == 'clear':
                state[target] = (0, 0)
            elif tag == 'copy':
                state[target] = state[event[2]]
            elif tag == 'add':
                state[target] = add(state[target], multiply((event[3], 0), state[event[2]]))
            elif tag == 'double':
                state[target] = multiply(state[target], (2, 0))
            elif tag == 'halve':
                state[target] = multiply(state[target], (1, 1))
            elif tag == 'negate':
                state[target] = multiply(state[target], (-1, 0))
            else:
                raise ValueError('unknown primitive')
        require(state[WORK][0] == 0, 'private work not cleared')
        result.append([fraction(value) for value in state[:N]])
    require(result[-1] == [0]*N, 'dirty private input leaks into data')
    return result[:N]


def check(candidate, reference):
    """Return the exact identity/cost receipt; raise ValueError on failed obligations."""
    frame = reference['frame']
    for key in ('frame', 'entry_frames', 'exit_frames'):
        require(candidate[key] == reference[key], 'changed ' + key)
    require(candidate['matrix'] == reference['matrix'], 'changed claimed target matrix')
    require(len(frame) == 4 and len(span(frame)) == 16, 'invalid rank-four frame')
    require(len(reference['entry_frames']) == N, 'wrong entry-frame count')
    require(all(len(f) == 3 and len(span(f)) == 8 and span(f) <= span(frame)
                for f in reference['entry_frames']), 'invalid entry frame inclusion')
    require(reference['exit_frames'] == [frame]*N, 'invalid exit frames')
    validate_events(reference['original'], frame)
    validate_events(reference['replacement'], frame)
    validate_events(candidate['replacement'], frame)
    target = [[Fraction(value) for value in row] for row in reference['matrix']]
    require(len(target) == N and all(len(row) == N for row in target), 'wrong matrix size')
    inverse = invert_matrix(target)
    targets = {'forward': target, 'inverse': inverse,
               'inverse_transpose': transpose(inverse), 'transpose': transpose(target)}
    receipt = {}
    for mode, matrix in targets.items():
        columns = transpose(matrix)
        record = {}
        for label, events in (('original', reference['original']),
                              ('pr681', reference['replacement']),
                              ('candidate', candidate['replacement'])):
            word = oriented(events, mode)
            require(macro_columns(word) == columns, mode + ': ' + label + ' map differs')
            costs = {}
            for scheme in ('historical_horner', 'pr696'):
                primitives = lower(word, scheme)
                require(primitive_columns(primitives) == columns,
                        mode + ': ' + label + ' ' + scheme + ' lowering differs')
                costs[scheme] = len(primitives)
            record[label] = {'scalar_macros': len(word), 'real_primitives': costs}
        record['matrix_sha256'] = digest([[str(value) for value in row] for row in matrix])
        receipt[mode] = record
    return receipt


def negative_controls(candidate, reference):
    mutants = {}
    altered = copy.deepcopy(candidate)
    altered['replacement'] = altered['replacement'][1:]
    mutants['missing_gate'] = altered
    altered = copy.deepcopy(candidate)
    next(e for e in altered['replacement'] if e[0] == 'add')[3] *= -1
    mutants['wrong_sign'] = altered
    altered = copy.deepcopy(candidate)
    next(e for e in altered['replacement'] if e[0] == 'add')[3] *= 3
    mutants['wrong_coefficient'] = altered
    altered = copy.deepcopy(candidate)
    altered['replacement'][0][-1][0] ^= 1
    mutants['wrong_gate_frame'] = altered
    altered = copy.deepcopy(candidate)
    altered['entry_frames'][0][0] ^= 1
    mutants['changed_entry_frame'] = altered
    rejected = {}
    for label, mutant in mutants.items():
        try:
            check(mutant, reference)
        except ValueError as error:
            rejected[label] = str(error)
        else:
            raise ValueError('negative control accepted: ' + label)
    # Test primitive checker separately, so a correct macro word does not mask
    # loss of the clean-private boundary in either lowering.
    for scheme in ('historical_horner', 'pr696'):
        # A single unit add makes an omitted terminal clear observable even
        # when the full candidate ends in several already-cleared unit adds.
        primitives = lower([['add', 0, 1, 1, 1, reference['frame']]], scheme)
        require(primitives[-1] == ('clear', WORK), 'unexpected lowering boundary')
        bad = primitives[:-1]
        try:
            primitive_columns(bad)
        except ValueError as error:
            rejected['missing_private_clear_' + scheme] = str(error)
        else:
            raise ValueError('negative control accepted: missing private clear')
    return rejected


def verify(candidate_path=None, reference_path=None):
    candidate_path = Path(candidate_path) if candidate_path else HERE / 'candidate.json'
    reference_path = Path(reference_path) if reference_path else REFERENCE
    candidate = json.loads(candidate_path.read_text())
    reference = json.loads(reference_path.read_text())
    return {'status': 'PASS_INDEPENDENT_FACTORY_BUTTERFLY',
            'method': 'scaled-integer dyadic basis replay; rational target inversion',
            'candidate_sha256': hashlib.sha256(candidate_path.read_bytes()).hexdigest(),
            'reference_sha256': hashlib.sha256(reference_path.read_bytes()).hexdigest(),
            'data_columns_per_map': N, 'private_columns_per_lowered_map': 1,
            'orientations': check(candidate, reference),
            'negative_controls': negative_controls(candidate, reference),
            'scope': 'Exact finite eight-register scalar map and primitive private boundary; '
                     'physical hosting, precision, full-word integration and kappa not certified here.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path)
    parser.add_argument('--reference', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.candidate, args.reference), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
