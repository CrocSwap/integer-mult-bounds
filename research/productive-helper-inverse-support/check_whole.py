#!/usr/bin/env python3
"""Whole scalar-A encoder extension of the cold inverse-support certificate.

Apache-2.0. Substantial OpenAI Codex assistance. The three required inverse
columns are replayed directly as632-entry vectors. Independently, sparse
forward/inverse matrices are reconstructed and both full identity products
are checked. No dense inversion, optimizer or discovery fixture is used.
"""
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import argparse
import importlib.util
import json

HERE = Path(__file__).resolve().parent
LO, HI, N = 6347, 10315, 632


@lru_cache(None)
def core():
    spec = importlib.util.spec_from_file_location('productive_inverse_support_core', HERE / 'check.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def need(condition, message):
    if not condition:
        raise ValueError(message)


def instruction(event):
    need(event[0] == 'scalar', 'whole interval is pure scalar')
    g = event[1]
    need(g[1][0] == 'L' and 0 <= g[1][1] < N, 'persistent scalar target')
    if g[0] == 'add':
        need(g[2][0] == 'L' and 0 <= g[2][1] < N and g[1] != g[2], 'distinct persistent scalar source')
        return 'add', g[1][1], g[2][1], Q(*g[3:5])
    need(g[0] == 'scale' and Q(*g[2:4]) != 0, 'invertible scalar scale')
    return 'scale', g[1][1], None, Q(*g[2:4])


def apply_vector(vector, program, backwards=False):
    result = list(vector)
    for event in reversed(program) if backwards else program:
        kind, dst, src, coefficient = instruction(event)
        if kind == 'add':
            result[dst] += (-coefficient if backwards else coefficient) * result[src]
        else:
            result[dst] *= 1 / coefficient if backwards else coefficient
    return result


def pull_row(functional, program):
    """Compute a row of M by backward propagation of its output weights."""
    row = list(functional)
    for event in reversed(program):
        kind, dst, src, coefficient = instruction(event)
        if kind == 'add':
            row[src] += coefficient * row[dst]
        else:
            row[dst] *= coefficient
    return row


def accumulate(target, source, coefficient):
    for column, value in source.items():
        value = target.get(column, Q(0)) + coefficient * value
        if value:
            target[column] = value
        else:
            target.pop(column, None)


def sparse_matrix(program, backwards=False):
    rows = [{i: Q(1)} for i in range(N)]
    for event in reversed(program) if backwards else program:
        kind, dst, src, coefficient = instruction(event)
        if kind == 'add':
            accumulate(rows[dst], rows[src], -coefficient if backwards else coefficient)
        else:
            coefficient = 1 / coefficient if backwards else coefficient
            rows[dst] = {j: coefficient * value for j, value in rows[dst].items()}
    return rows


def identity_product(a, b):
    for i, row in enumerate(a):
        result = {}
        for j, coefficient in row.items():
            accumulate(result, b[j], coefficient)
        need(result == {i: Q(1)}, 'full632 sparse inverse product')


def entry_frames(payload, program):
    current = payload['canonical']['start'][:]
    for event in program[:LO]:
        if event[0] == 'scalar':
            for typ, role in core().refs(event):
                if typ == 'L':
                    current[role] = event[2]
        elif event[0] == 'warp':
            current[event[1][1]] = event[4]
    return current


def validate_cold(payload, frames, cold):
    actual = [r for r, label in enumerate(frames) if r != 416 and not payload['canonical']['frames'][label]]
    need(cold == actual, 'complete actual cold-role census')
    need(len(cold) == 457, 'source whole-encoder cold count')


def check_identity(alpha, column78, column431, cold):
    need(any(alpha), 'nonzero whole-encoder compensation')
    for role in cold:
        need(alpha[role] == -column78[role] + column431[role] / 2, 'whole cold-projected annihilator')


def model(payload):
    m = core()
    program = [e for e in payload['programs']['forward'] if e[0] != 'climb']
    phase = program.index(['phase', 'A'])
    need(program.index(['phase', 'centers']) == HI
         and 1 + max(i for i in range(phase, HI) if program[i][0] == 'warp') == LO,
         'whole scalar encoder starts after last A prelude and ends before centers')
    segment = program[LO:HI]
    for event in segment:
        instruction(event)
    frames = entry_frames(payload, program)
    need(payload['canonical']['frames'][frames[416]] == []
         and payload['canonical']['frames'][frames[13]] == [73], 'whole E prefix availability')
    cold = [r for r, label in enumerate(frames) if r != 416 and not payload['canonical']['frames'][label]]
    validate_cold(payload, frames, cold)

    functional = [Q(0)] * N
    functional[417], functional[419] = Q(1, 2), Q(-1)
    wanted = [Q(r in (13, 416)) for r in range(N)]
    need(pull_row(functional, segment) == wanted, 'whole reserved value entry13 plus dirty entry416')

    forward = sparse_matrix(segment)
    backward = sparse_matrix(segment, True)
    identity_product(forward, backward)
    identity_product(backward, forward)
    selected = {}
    for column in (416, 78, 431):
        seed = [Q(0)] * N
        # T^-1*P*e416=e417-e419/2; the other two columns are unchanged.
        if column == 416:
            seed[417], seed[419] = Q(1), Q(-1, 2)
        else:
            seed[column] = Q(1)
        inverse_column = apply_vector(seed, segment, True)
        need(apply_vector(inverse_column, segment) == seed, 'selected inverse-column forward round trip')
        need(apply_vector(apply_vector(seed, segment), segment, True) == seed, 'selected inverse-column backward round trip')
        independent_column = [sum(value * seed[j] for j, value in row.items()) for row in backward]
        need(inverse_column == independent_column, 'vector and full-matrix inverse-column agreement')
        inverse_column[416] += inverse_column[13]  # Left multiplication by E.
        need(inverse_column[416] == Q(column == 416), 'reserved inverse row on selected columns')
        selected[column] = inverse_column
    alpha = [-x if i != 416 else Q(0) for i, x in enumerate(selected[416])]
    need(all(not value or r in cold for r, value in enumerate(alpha)), 'whole compensation only on cold inputs')
    check_identity(alpha, selected[78], selected[431], cold)
    expected_alpha = {418: Q(1, 2), 419: Q(1, 2), 420: Q(1, 2), 421: Q(1, 2),
                      425: Q(1, 2), 430: Q(-1, 2), 431: Q(-1, 2)}
    need({r: value for r, value in enumerate(alpha) if value} == expected_alpha, 'exact whole alpha support')
    need(all(backward[416].get(j, Q(0)) + backward[13].get(j, Q(0))
             == (Q(1, 2) if j == 417 else Q(-1) if j == 419 else Q(0)) for j in range(N)),
         'full reserved inverse row before right T inverse P')
    return {'frames': frames, 'cold': cold, 'alpha': alpha, 'columns': selected,
            'forward_nnz': sum(map(len, forward)), 'inverse_nnz': sum(map(len, backward))}


def suffix(payload, direction):
    m = core()
    events, provenance = m.make_suffix(payload, direction, cut=HI)
    combined, combined_origins, counts = m.combine(events, provenance)
    result = {'coalescing': counts, 'variants': {}}
    for name, word, origins in (('uncoalesced', events, provenance), ('coalesced', combined, combined_origins)):
        graph = m.suffix_graph(payload, word, origins)
        caps = {}
        for role in m.TARGETS:
            need(graph['upper'][role] == m.span(m.EXPECTED_CAPS[role]), 'whole-A greatest suffix cap')
            certificate = m.witness(graph, role)
            caps[str(role)] = {'basis': m.basis(graph['upper'][role]), 'witness': m.compact_witness(graph, certificate)}
        result['variants'][name] = {'suffix_event_count': len(word), 'suffix_sha256': m.digest(word),
                                    'omitted_native_occurrences': graph['omitted_native_occurrences'],
                                    'caps': caps}
    return result


def verify(payload=None):
    m = core()
    payload = m.read_source() if payload is None else payload
    need(m.digest(payload) == m.SOURCE_SHA256, 'pinned whole-encoder source')
    data = model(payload)
    m.native_binding(payload)
    return {'status': 'PASS_WHOLE_SCALAR_ENCODER_INVERSE_SUPPORT', 'source_sha256': m.SOURCE_SHA256,
            'source_interval': [LO, HI], 'scalar_events': HI - LO, 'arbitrary_input_roles': N,
            'both_full632_inverse_products': True, 'selected_inverse_columns': [416, 78, 431],
            'independent_vector_column_round_trips': True,
            'forward_matrix_nonzeros': data['forward_nnz'], 'inverse_matrix_nonzeros': data['inverse_nnz'],
            'cold_role_count': len(data['cold']), 'cold_main_role_count': sum(r < 224 for r in data['cold']),
            'cold_role_list_sha256': m.digest(data['cold']),
            'alpha': {str(r): str(c) for r, c in enumerate(data['alpha']) if c},
            'annihilator': 'alpha = -D^-1[:,78] + (1/2)D^-1[:,431] on every actual cold entry role',
            'directions': {d: suffix(payload, d) for d in ('forward', 'backward')},
            'scope': 'The same obstruction covers arbitrary invertible bases on all457 zero-chart persistent entry roles of the entire scalar-A interval, including cold main roles, with all compensation placed before its pure-scalar quotient. Paid canonical chart spaces must grow by inclusion through the declared retained suffix. Native edges, helper final pins and intermediate adapter pins are released. Interleaved compensation, changed suffix contacts, nonmonotone transports and a new bound remain outside the claim.'}


def controls(payload=None):
    m = core()
    payload = m.read_source() if payload is None else payload
    data = model(payload)
    passed = []

    def rejected(name, action):
        try:
            action()
        except ValueError:
            passed.append(name)
        else:
            raise ValueError('whole corruption accepted: ' + name)

    bad = deepcopy(payload)
    pure = [e for e in bad['programs']['forward'] if e[0] != 'climb']
    pure[9961][1][3] *= -1
    rejected('whole_source_compensation_value_changed', lambda: model(bad))
    rejected('whole_cold_role_omitted', lambda: validate_cold(payload, data['frames'], data['cold'][:-1]))
    rejected('whole_noncold_main_role_added', lambda: validate_cold(payload, data['frames'], sorted(data['cold'] + [13])))
    wrong = list(data['columns'][78])
    wrong[418] += 1
    rejected('whole_inverse_column_coefficient_changed', lambda: check_identity(data['alpha'], wrong, data['columns'][431], data['cold']))
    corrupted_inverse = sparse_matrix([e for e in payload['programs']['forward'] if e[0] != 'climb'][LO:HI], True)
    corrupted_inverse[0][0] = corrupted_inverse[0].get(0, Q(0)) + 1
    forward = sparse_matrix([e for e in payload['programs']['forward'] if e[0] != 'climb'][LO:HI])
    rejected('whole_full_inverse_product_corrupted', lambda: identity_product(forward, corrupted_inverse))
    return {'count': len(passed), 'passed': passed}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = verify()
    result['controls'] = controls()
    if args.write:
        (HERE / 'WHOLE-CHECK-RESULT.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, sort_keys=True, indent=2))
