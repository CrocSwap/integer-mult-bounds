#!/usr/bin/env python3
"""Costed helper normalization of PR4694. Apache-2.0; OpenAI assistance.

The frozen PR4694 native emitter/replay is reused unchanged with credit.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
J = [224, 225, 227, 229, 240, 241, 256, 257]


def need(value, message):
    if not value:
        raise ValueError(message)


def load_engine():
    spec = importlib.util.spec_from_file_location('retained_center_engine', HERE/'inputs/retained_verify.py')
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    engine.HERE = HERE
    return engine


def power_two(value):
    return value > 0 and value & (value-1) == 0


def make_header(r, cold):
    """P sends new u to old h, so R_H P selects exactly u_J."""
    header = []
    for i, dst in enumerate(J):
        for src, value in sorted(r[i].items()):
            if src in cold and src not in J:
                header.append(('add', dst, src, -value, 0))
    matrix = [[row.get(j, Q(0)) for j in J] for row in r]
    determinant = Q(1)
    pivots = []
    for i in range(8):
        k = next(k for k in range(i, 8) if matrix[k][i])
        if k != i:
            matrix[k], matrix[i] = matrix[i], matrix[k]
            a, b = J[i], J[k]
            header.extend([('add', a, b, Q(1), 0), ('add', b, a, Q(-1), 0),
                           ('add', a, b, Q(1), 0), ('scale', b, Q(-1), 0)])
            determinant *= -1
        value = matrix[i][i]
        need(power_two(abs(value.numerator)) and power_two(value.denominator),
             'Every pivot is a dyadic unit')
        determinant *= value
        pivots.append(str(value))
        if value != 1:
            header.append(('scale', J[i], 1/value, 0))
        matrix[i] = [a/value for a in matrix[i]]
        for k in range(8):
            if k == i or not matrix[k][i]:
                continue
            value = matrix[k][i]
            header.append(('add', J[k], J[i], -value, 0))
            matrix[k] = [a-value*b for a, b in zip(matrix[k], matrix[i])]
    need(matrix == [[Q(i == j) for j in range(8)] for i in range(8)], 'Invert the actual minor')
    return header, determinant, pivots


def inverse_header(header, frame):
    return [('add', e[1], e[2], -e[3], frame) if e[0] == 'add'
            else ('scale', e[1], 1/e[2], frame) for e in reversed(header)]


def dual_header(header):
    return [('add', e[2], e[1], -e[3], e[4]) if e[0] == 'add'
            else ('scale', e[1], 1/e[2], e[3]) for e in header]


def scalar_matrix(engine, header):
    rows = [{i: Q(1)} for i in range(640)]
    for e in header:
        if e[0] == 'add':
            engine.plus(rows[e[1]], rows[e[2]], e[3])
        else:
            rows[e[1]] = {i: e[2]*v for i, v in rows[e[1]].items()}
    return rows


def add_matrices(engine, a, b, coefficient=Q(1)):
    out = [dict(row) for row in a]
    for dst, src in zip(out, b):
        engine.plus(dst, src, coefficient)
    return out


def bound(events):
    envelope, maximum = [Q(1)]*640, Q(1)
    for e in events:
        if e[0] == 'add':
            envelope[e[1]] += abs(e[3])*envelope[e[2]]
        elif e[0] == 'scale':
            envelope[e[1]] *= abs(e[2])
        else:
            continue
        maximum = max(maximum, envelope[e[1]])
    return maximum


def run():
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'Changed pinned input: '+row['path'])
    origins = json.loads((HERE/'inputs/ORIGINS.json').read_text())
    for row in origins['files']:
        need(sha256((HERE/row['path']).read_bytes()).hexdigest() == row['sha256'],
             'Changed frozen PR4694 source')
    spec = importlib.util.spec_from_file_location('three_field_consumer', HERE/'consumer.py')
    consumer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(consumer)
    consumer_result = consumer.check()
    engine = load_engine()
    payload = engine.load()
    c = payload['canonical']
    abi = json.loads((HERE/'inputs/ABI.json').read_text())
    r = [{i: Q(value) for i, value in row} for row in abi['R_rows']]
    cold = {i for i in range(224, 632) if c['start'][i] == 0 and c['final'][i] == 1}
    support = {i for row in r for i in row if i >= 224}
    need(len(cold) == 326 and len(support) == 106 and support <= cold,
         'All 106 observed helpers have common birth and complete charts')
    need(set(J) <= cold, 'The eight physical pivots are cold complete helpers')
    need(all(e[2] not in cold for e in payload['programs']['forward'] if e[0] == 'adapter'),
         'No ignored endpoint adapter changes a mixed helper chart')
    header, determinant, pivots = make_header(r, cold)
    footer = inverse_header(header, 1)
    identity = [{i: Q(1)} for i in range(640)]
    p, pinv = scalar_matrix(engine, header), scalar_matrix(engine, footer)
    need(engine.product(p, pinv) == engine.product(pinv, p) == identity,
         'Both exact physical helper basis inverse identities')
    source_starts, centers, source = engine.emit(payload)
    original = engine.replay(payload, source_starts, source)
    b = [{i: Q(value) for i, value in row} for row in abi['B_rows']]
    expected_original = [dict(row) for row in identity]
    for i in range(112):
        expected_original[112+i][i] = Q(1)
    for i in range(632):
        engine.plus(expected_original[i], b[i])
    for i in range(8):
        engine.plus(expected_original[632+i], r[i])
    need(original == expected_original, 'Fresh source native replay authenticates the ABI')
    native = header+source+footer
    actual = engine.replay(payload, source_starts, native)
    expected = engine.product(engine.product(pinv, original), p)
    need(actual == expected, 'All 640 arbitrary columns of the normalized native word')
    normalized_r = []
    for i in range(8):
        row = dict(actual[632+i])
        row.pop(632+i)
        need({j: value for j, value in row.items() if j >= 224} == {J[i]: Q(1)},
             'Each center observes precisely one independent helper')
        need({j: value for j, value in row.items() if j < 224}
             == {j: value for j, value in r[i].items() if j < 224},
             'The original data observation is retained exactly')
        normalized_r.append(row)
    need(actual[:632] == original[:632], 'All old-input outputs and incoming-center leakage are retained')
    k = add_matrices(engine, actual, identity, Q(-1))
    k2 = engine.product(k, k)
    need(not any(engine.product(k2, k)), 'Exact cube-zero nilpotent structure')
    ranks = engine.matrix_rank(k), engine.matrix_rank(k2)
    need(ranks == (120, 8), 'Exact nilpotent ranks')
    for i, helper in enumerate(J):
        # Matrix-vector products are checked as actual sparse columns.
        column = {a: row.get(helper, Q(0)) for a, row in enumerate(k) if row.get(helper)}
        need(column == {632+i: Q(1)}, 'First link of every explicit length-three chain')
        column = {a: row.get(632+i, Q(0)) for a, row in enumerate(k) if row.get(632+i)}
        need(column == {a: row.get(632+i) for a, row in enumerate(b) if row.get(632+i)},
             'Second link is the actual nonzero Y scatter column')
    inverse = add_matrices(engine, add_matrices(engine, identity, k, Q(-1)), k2)
    need(engine.product(actual, inverse) == engine.product(inverse, actual) == identity,
         'Both exact normalized inverse identities')
    _, _, source_dual = engine.emit(payload, dual=True)
    dual = dual_header(header)+source_dual+dual_header(footer)
    need(engine.replay(payload, source_starts, dual) == engine.transpose(inverse),
         'All 640 raw inverse-transpose columns and unchanged paid profile')
    prefix, dual_prefix = bound(native), bound(dual)
    need(max(prefix, dual_prefix) < 2**192,
         'Both complete positive scalar envelopes remain inside the retained cap')
    bad = list(header)
    e = bad[0]
    bad[0] = (*e[:3], -e[3], e[4])
    need(engine.replay(payload, source_starts, bad+source+footer) != actual,
         'A wrong actual basis coefficient is rejected')
    need(engine.replay(payload, source_starts, header+source) != actual,
         'Omitting the physical output inverse is rejected')
    bad_footer = list(footer)
    bad_footer[0] = (*bad_footer[0][:-1], 0)
    try:
        engine.replay(payload, source_starts, header+source+bad_footer)
    except ValueError:
        pass
    else:
        raise ValueError('A mixed-chart footer was accepted')
    return {'status': 'PASS_CENTER_HELPER_NORMAL_FORM', 'source_pr': 4694,
            'source_commit': origins['files'][0]['source_commit'],
            'pivots': J, 'minor_determinant': str(determinant), 'elimination_pivots': pivots,
            'observed_helpers_before': len(support), 'observed_helpers_after': 8,
            'cold_complete_helper_pool': len(cold), 'header_gates': len(header),
            'footer_gates': len(footer), 'new_recursive_calls': 0,
            'paid': {str(i): n for i, n in engine.PAID.items()},
            'nilpotent_rank': ranks[0], 'square_rank': ranks[1],
            'jordan_blocks': {'3': 8, '2': 104, '1': 408},
            'normalized_R': engine.encoded(normalized_r), 'positive_prefix_envelope': str(prefix),
            'raw_dual_positive_prefix_envelope': str(dual_prefix),
            'primal_and_raw_dual_640_columns': True,
            'independent_center_credit': False, 'new_kappa': None,
            'conditional_three_field_controller': consumer_result,
            'program_sha256': sha256(json.dumps(native, default=str).encode()).hexdigest()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = run()
    target = HERE/'RESULT.json'
    if args.write:
        target.write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    else:
        need(result == json.loads(target.read_text()), 'Exact deterministic result')
    print('PASS_CENTER_HELPER_NORMAL_FORM no_new_kappa')
