"""Replay 33 fixed-word exclusions and mathematical positive/negative controls."""
if not __debug__:
    raise SystemExit('Verification requires assertions; run Python without -O.')

from collections import Counter
from copy import deepcopy
from hashlib import sha256
from itertools import permutations
import gzip
import json
from pathlib import Path

from model import (Engine, IDENTITY, FREE, decode, generic_paths,
                   coefficient_records, execute, endpoint_frames, pauli_image)
from independent import (path_rows, layers, group, rank_formula,
                         binomial_certificate, diagonal_trace)
from support import encode_support, verify, selected_support, solve
from rank_support import compile_support as strengthened
from torus import equations, complete, diagonalize
import dense

ROOT = Path(__file__).resolve().parent


def block_selection(cnf, selection):
    clause = []
    for i, label in enumerate(cnf['labels']):
        if not label:
            continue
        if label[0] == 'entry':
            _, k, r, c = label
            clause.append(-i if selection['entry_support'][k][3*r+c] else i)
        elif label[0] == 'frame' and selection['frames'][label[1]] == label[2]:
            clause.append(-i)
    return clause


def check_dense(program):
    ring = Engine()
    rows = execute(ring, program)
    wanted = [{(key & 3, ring.groups[key >> 2]): value for key, value in row.items()} for row in rows]
    assert wanted == dense.execute(program)
    for i, tableau in enumerate(ring.groups):
        assert ring.frames(i) == dense.independent_frame(tableau)
    return ring, rows


def check_template(template, counts, dense_check=True):
    program, answer = decode(template['program']), template['result']
    assert sum(g[0] == 'paid' for g in program) == 8
    assert sum(g[0] == 'mix3' for g in program) == 3
    ring = Engine()
    rows, blocks = path_rows(ring, program)
    assert (rows, blocks) == generic_paths(ring, program, 3)
    records, targets = coefficient_records(ring, rows)
    cnf = rank_formula(program, encode_support(records, targets, blocks))
    assert cnf == strengthened(program)
    assert sha256(json.dumps(cnf, sort_keys=True).encode()).hexdigest() == answer['cnf_sha256']
    assert answer['status'] == 'excluded' and answer['steps']
    for number, step in enumerate(answer['steps']):
        result = step['support']
        counts['boolean_proof_nodes'] += verify(cnf, result)
        counts['support_models_or_refutations'] += 1
        if result['status'] == 'support_obstruction':
            assert number == len(answer['steps'])-1
            continue
        assert result['status'] == 'support_feasible'
        selection = selected_support(cnf, result)
        assert selection == step['selection']
        arithmetic = step['binomial']
        assert arithmetic['status'] in ('all_components_singular', 'inconsistent_torus')
        binomial_certificate(equations(program, selection), arithmetic)
        assert step['blocking_clause'] == block_selection(cnf, selection)
        cnf['clauses'].append(step['blocking_clause'])
        counts['exact_torus_refutations'] += 1
    assert answer['steps'][-1]['support']['status'] == 'support_obstruction'
    if 'defining_words' in template:
        words = {name: decode(word) for name, word in template['defining_words'].items()}
        def unary(word):
            return group(ring, layers(word)[0][0])
        pq = unary(words['Q']+words['P'])
        assert pq == unary(words['T']+words['Q'])
        assert pq != unary(words['P']+words['Q'])
        assert ring.frame_info(pq)[1] == template['shared_product_rank']
        assert template['q_calls'] in (1, 2)
        assert sum(g[0] == 'paid' for g in words['Q']) == template['q_calls']
        counts['noncommuting_relations'] += 1
    if dense_check:
        literal = tuple(('mix3', 2, 1, 0, 1, 1, 1, 0, 1, 1) if g[0] == 'mix3' else g for g in program)
        check_dense(literal)
        counts['dense_skeleton_checks'] += 1
    counts['excluded_templates'] += 1


def actual_boolean_model(cnf, program):
    ring = Engine()
    frames = endpoint_frames(ring, execute(ring, program))
    assert frames is not None
    matrices = [g[1:] for g in program if g[0] == 'mix3']
    active = sum(1 << (9*k+i) for k, matrix in enumerate(matrices) for i, value in enumerate(matrix) if value)
    model = []
    for label in cnf['labels'][1:]:
        kind, *args = label
        if kind == 'entry':
            k, r, c = args
            value = bool(matrices[k][3*r+c])
        elif kind == 'matching':
            k, permutation = args
            value = all(matrices[k][3*r+permutation[r]] for r in range(3))
        elif kind == 'frame':
            column, frame = args
            value = frames[column] == frame
        elif kind == 'term':
            mask, = args
            value = not mask & ~active
        else:
            assert kind == 'rank_matching'
            variable = len(model)+1
            guards = [c[1] for c in cnf['clauses'] if len(c) == 2 and c[0] == -variable]
            value = all(model[g-1] for g in guards)
        model.append(int(bool(value)))
    result = {'status': 'support_feasible', 'model': model, 'proof': None}
    verify(cnf, result)
    return selected_support(cnf, result)


def det3(matrix):
    total = 0
    for p in permutations(range(3)):
        value = (-1)**sum(p[i] > p[j] for i in range(3) for j in range(i+1, 3))
        for r in range(3):
            value *= matrix[3*r+p[r]]
        total += value
    return total


def reject(action):
    try:
        action()
    except (AssertionError, ValueError, KeyError, IndexError):
        return
    raise AssertionError('corrupt or ineligible witness accepted')


def controls(templates, counts):
    for op in FREE+tuple(('C', v, 0) for v in range(1, 8)):
        matrix = dense.operator(op)
        for generator in IDENTITY:
            assert dense.multiply(matrix, dense.pauli(generator)) == dense.multiply(dense.pauli(pauli_image(op, generator)), matrix)
            counts['dense_generator_identities'] += 1
    for v in range(1, 8):
        assert dense.multiply(dense.operator(('C', v, 0)), dense.operator(('C', v, 0))) == dense.pauli(v)
        counts['paid_square_identities'] += 1
    for trial, axes in enumerate(((1, 2, 4), (3, 2, 4), (1, 6, 4), (5, 2, 4))):
        a = ('mix3', 1, 1, 0, 0, 1, 1, 1, 0, 1)
        b = ('mix3', 1, 0, 0, 0, trial+1, 0, 0, 0, -1)
        c = ('mix3', 2, 1, 0, 1, 1, 1, 0, 1, 1)
        u, v = ((), (axes[0],), axes[:2]), (axes, axes[1:], axes[2:])
        word = tuple([a]+[('paid', r, x) for r, unit in enumerate(u) for x in unit]
                     +[b]+[('paid', r, x) for r, unit in enumerate(v) for x in unit]+[c])
        ring, rows = check_dense(word)
        assert endpoint_frames(ring, rows) is not None
        assert all(det3(g[1:]) for g in word if g[0] == 'mix3')
        selection = actual_boolean_model(strengthened(word), word)
        candidate, result = complete(word, selection)
        assert candidate is not None and result['status'] == 'exact_rational_point'
        assert all(det3(g[1:]) for g in candidate if g[0] == 'mix3')
        ring, rows = check_dense(candidate)
        assert endpoint_frames(ring, rows) is not None
        binomial_certificate(equations(word, selection), result)
        counts['positive_nine_call_controls'] += 1
        counts['dense_positive_checks'] += 2
        if trial == 0:
            for removed, wanted in ((1, 'support_feasible'), (6, 'support_obstruction')):
                bad = word[:removed]+word[removed+1:]
                ring, rows = check_dense(bad)
                assert endpoint_frames(ring, rows) is None
                cnf = strengthened(bad)
                test = solve(cnf, seconds=2)
                assert test['status'] == wanted
                verify(cnf, test)
                counts['relaxation_false_positive' if wanted == 'support_feasible' else 'negative_eight_call'] += 1
    for matrix, rhs in (([[2]], [1]), ([[1], [1]], [0, 1]), ([[2, 3], [4, 6]], [1, 0])):
        eq = {'matrix': matrix, 'rhs_parity': rhs, 'nonzero_entries': list(range(len(matrix[0])))}
        trace = diagonalize(matrix, rhs, len(matrix[0]))
        diagonal_trace(eq, trace)
        counts['integer_trace_controls'] += 1
        forged = deepcopy(trace)
        forged['rhs'][0] += 1
        reject(lambda: diagonal_trace(eq, forged))
        counts['corrupt_integer_traces_rejected'] += 1
    fixture = {'clauses': [[1, 2], [1, -2], [-1, 2], [-1, -2]], 'variables': 2}
    result = solve(fixture)
    verify(fixture, result)
    node = result['proof']
    while 'conflict' not in node:
        node = node['positive']
    node['conflict'] = 0
    reject(lambda: verify(fixture, result))
    counts['corrupt_boolean_proofs_rejected'] += 1
    source = next(t for t in templates if len(t['result']['steps']) > 1)
    forged = deepcopy(source)
    forged['result']['steps'][0]['blocking_clause'].pop()
    reject(lambda: check_template(forged, Counter(), False))
    counts['corrupt_learned_clauses_rejected'] += 1
    forged = deepcopy(source)
    forged['result']['steps'].pop()
    reject(lambda: check_template(forged, Counter(), False))
    counts['missing_final_refutations_rejected'] += 1
    eq = {'matrix': [[2]], 'rhs_parity': [1], 'nonzero_entries': [0], 'blocks': 3}
    false = {'status': 'all_components_singular', 'equations': eq,
             'diagonalization': diagonalize([[2]], [1], 1), 'components': []}
    reject(lambda: binomial_certificate(eq, false))
    counts['unsupported_torsion_exclusions_rejected'] += 1


def main():
    manifest = json.loads((ROOT/'MANIFEST.json').read_text(encoding='utf-8'))
    for name, wanted in manifest['files_sha256'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest() == wanted, name
    raw = gzip.decompress((ROOT/'certificates.json.gz').read_bytes())
    assert sha256(raw).hexdigest() == manifest['certificate_payload_sha256']
    data = json.loads(raw)
    assert data['schema'] == 1 and len(data['templates']) == 33
    assert len({t['id'] for t in data['templates']}) == 33
    counts = Counter()
    for template in data['templates']:
        check_template(template, counts)
    controls(data['templates'], counts)
    assert counts['excluded_templates'] == 33 and counts['exact_torus_refutations'] == 78
    assert counts['noncommuting_relations'] == 32
    print(json.dumps({'status': 'PASS_FIXED_CLIFFORD_WORD_EXCLUSIONS',
                      'counts': dict(counts), 'certificate_payload_sha256': sha256(raw).hexdigest()}, indent=2))


if __name__ == '__main__':
    main()
