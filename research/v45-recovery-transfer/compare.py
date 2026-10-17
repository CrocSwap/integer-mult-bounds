#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact bounded V45 information comparison on five authenticated provider stages.

The complete forward free-group replay and rational kernel implementation are
reused, with attribution, from research/helper408-rank7-pairing/verify_boundary.py.
This file supplies the changed five-stage observation contract, full readout
comparisons, known-helper separation and exact scalar nuisance certificates.
"""
import argparse
import copy
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
ENGINE = 'research/helper408-rank7-pairing/verify_boundary.py'
FRAME_EDITS = 'research/rank7-joint-endframes/data/STAGE1-FRAME-EDITS.json'
V45 = (256, 128, 64, 35, 16, 11, 5)
U12 = (2, 61, 62, 63, 70, 71, 72, 94, 249, 251, 265, 267)
P4 = (249, 251, 265, 267)
STAGES = ('PR2894', 'PR2917', 'PR2942', 'PR2979_stage1', 'PR2979_final')
EXPECTED_H = (226, 216, 212, 212, 207)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw)


def authenticated_sources():
    manifest = read(PACKAGE / 'SOURCES.json')
    pins = {}
    for row in manifest['files']:
        if row['usage'] != 'input':
            continue
        rel = row['path']
        need(rel not in pins, 'duplicate input pin: ' + rel)
        path = (ROOT / rel).resolve()
        need(path.is_relative_to(ROOT.resolve()), 'input outside repository')
        need(hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'], 'input hash mismatch: ' + rel)
        pins[rel] = row['sha256']
    return pins


def source_paths(variant):
    return {
        'PR2894': f'research/helper408-rank7-pairing/sources/data/PARENT-{variant}.json.gz',
        'PR2917': f'research/paired-helper-extension/data/WORD-{variant}.json.gz',
        'PR2942': f'research/rank7-joint-endframes/data/PARENT-{variant}.json.gz',
        'PR2979_final': f'research/rank7-joint-endframes/data/WORD-{variant}.json.gz',
    }


def stage1(parent, record):
    """Apply exactly the shipped frame-only record, without source synthesis code."""
    child = copy.deepcopy(parent)
    for helper, change in record['helper_final_changes'].items():
        need(child['helper_final'][helper] == change['old'], 'stage1 helper preimage')
        child['helper_final'][helper] = change['new']
    seen = set()
    for edit in record['frame_edits']:
        key = edit['section'], edit['index']
        need(key not in seen and key[0] in ('A', 'B', 'restore'), 'stage1 duplicate/unknown frame edit')
        seen.add(key)
        gate = child[key[0]][key[1]]
        need(gate[:-1] == edit['gate'] and gate[-1] == edit['old_frame'], 'stage1 gate preimage')
        gate[-1] = edit['new_frame']
    need(all(g[:-1] == h[:-1] for sec in ('A', 'B', 'restore')
             for g, h in zip(parent[sec], child[sec])), 'stage1 changed a scalar operator')
    return child


def matrix_rank(rows, engine):
    variables = sorted({k for row in rows for k in row})
    return engine.kernel(rows, variables)[1]['rank']


def determinant(matrix):
    a = [[Q(c) for c in row] for row in matrix]
    n = len(a)
    need(all(len(row) == n for row in a), 'determinant requires square matrix')
    result = Q(1)
    for k in range(n):
        pivot = next((i for i in range(k, n) if a[i][k]), None)
        if pivot is None:
            return Q(0)
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            result = -result
        value = a[k][k]
        result *= value
        for i in range(k + 1, n):
            ratio = a[i][k] / value
            for j in range(k + 1, n):
                a[i][j] -= ratio * a[k][j]
    return result


def dyadic_unit(value):
    def power_of_two(n):
        return n > 0 and n & (n - 1) == 0
    return power_of_two(abs(value.numerator)) and power_of_two(value.denominator)


def encoded_rows(matrix, support):
    return [[r, c, list(word), str(value)] for r in sorted(support)
            for (c, word), value in sorted(matrix[r].items())]


def rows_digest(rows):
    return hashlib.sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest()


def nuisance_certificate(matrix, H, support, engine):
    """Greedy independent, exactly scalar forbidden columns, with full entries."""
    selected, columns = [], []
    for c in sorted(set(matrix) - set(H)):
        if any(word for r in support for (column, word) in matrix[r] if column == c):
            continue
        vector = {r: matrix[r][c, ()] for r in support if (c, ()) in matrix[r]}
        if vector and matrix_rank(columns + [vector], engine) > len(columns):
            selected.append(c)
            columns.append(vector)
        if len(columns) == len(support):
            break
    entries = [[str(column.get(r, Q(0))) for column in columns] for r in support]
    det = determinant(entries) if len(selected) == len(support) else None
    pivot_rows, independent_rows = [], []
    for r, row in zip(support, entries):
        sparse = {j: Q(c) for j, c in enumerate(row) if Q(c)}
        if matrix_rank(independent_rows + [sparse], engine) > len(independent_rows):
            pivot_rows.append(r)
            independent_rows.append(sparse)
    rank_entries = [[str(row.get(j, Q(0))) for j in range(len(columns))] for row in independent_rows]
    rank_det = determinant(rank_entries)
    need(len(pivot_rows) == len(columns) and rank_det != 0, 'nuisance rank witness failed')
    return {'rank_witness_rows': pivot_rows, 'rank_witness_matrix': rank_entries,
            'rank_witness_determinant': str(rank_det), 'rank_witness_dyadic_unit': dyadic_unit(rank_det),
            'rows': list(support), 'columns': selected, 'matrix': entries,
            'rank': len(columns), 'determinant': str(det) if det is not None else None,
            'dyadic_unit': dyadic_unit(det) if det is not None else False,
            'nonempty_word_coefficients': 0}


def analyze_support(matrix, H, support, engine):
    result = engine.analyze(matrix, H, support)
    answer = {key: [engine.encode_vector(v) for v in result[key]]
              for key in ('V', 'Y', 'Alpha', 'U')}
    answer.update({'forward': result['forward'], 'inverse': result['inverse'],
                   'pairing': [[str(c) for c in row] for row in result['pairing']],
                   'pairing_rank': matrix_rank([dict(enumerate(row)) for row in result['pairing']], engine),
                   'nuisance_certificate': nuisance_certificate(matrix, H, support, engine)})
    pairing = result['pairing']
    square = bool(pairing) and all(len(row) == len(pairing) for row in pairing)
    answer['pairing_determinant'] = str(determinant(pairing)) if square else None
    terms = [(r, c, word, value) for r in support for (c, word), value in matrix[r].items() if c in H]
    answer['eligible_block_coefficient_count'] = len(terms)
    answer['eligible_block_zero'] = not terms
    nuisance = answer['nuisance_certificate']
    Y = result['Y']
    if len(Y) + nuisance['rank'] == len(support):
        completion = [[str(y.get(r, Q(0))) for y in Y] + nuisance['matrix'][i]
                      for i, r in enumerate(support)]
        completion_det = determinant(completion)
        alpha_B = [[sum(alpha.get(r, Q(0)) * Q(nuisance['matrix'][i][j])
                        for i, r in enumerate(support)) for j in range(nuisance['rank'])]
                   for alpha in result['Alpha']]
        need(not any(c for row in alpha_B for c in row), 'Alpha times nuisance is nonzero')
        answer['paired_nuisance_completion'] = {
            'column_order': 'Y basis, then scalar nuisance columns', 'matrix': completion,
            'determinant': str(completion_det), 'dyadic_unit': dyadic_unit(completion_det),
            'alpha_times_nuisance': [[str(c) for c in row] for row in alpha_B],
        }
    else:
        answer['paired_nuisance_completion'] = None
    # For this bounded support every coefficient is scalar. Thus ordinary
    # rational rank(B) is the full nuisance rank, not a wordwise surrogate.
    need(not any(word for r in support for c, word in matrix[r]), 'nonscalar bounded readout')
    scalar_rows = [{c: value for (c, _), value in matrix[r].items()} for r in support]
    nuisance_rows = [{c: value for c, value in row.items() if c not in H} for row in scalar_rows]
    answer['readout_rank'] = matrix_rank(scalar_rows, engine)
    answer['nuisance_rank'] = matrix_rank(nuisance_rows, engine)
    answer['recoverable_scalar_dimension'] = answer['readout_rank'] - answer['nuisance_rank']
    need(answer['recoverable_scalar_dimension'] == result['inverse']['dimension'], 'quotient/kernel dimensions disagree')
    return answer


def compute():
    pins = authenticated_sources()
    required = {ENGINE, FRAME_EDITS} | {path for tag in ('base', 'extra') for path in source_paths(tag).values()}
    need(required <= set(pins), 'consumed input lacks authentication')
    spec = importlib.util.spec_from_file_location('v45_boundary_engine', ROOT / ENGINE)
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    record = read(ROOT / FRAME_EDITS)
    output = {'schema_version': 1, 'status': 'PASS_BOUNDED_V45_OBSERVATION_COMPARISON',
              'V45': list(V45), 'common_observation_U12': list(U12), 'known_pivots_P4': list(P4),
              'consumed_input_sha256': {p: pins[p] for p in sorted(required)}, 'variants': {}}
    for variant in ('base', 'extra'):
        paths = source_paths(variant)
        providers = {label: read(ROOT / path) for label, path in paths.items()}
        providers['PR2979_stage1'] = stage1(providers['PR2942'], record)
        reports, raw_readouts = {}, {}
        for index, label in enumerate(STAGES):
            word = providers[label]
            matrix = engine.replay(word)
            frames, frame_counts = engine.terminal_frames(word)
            protected = (set(map(int, word['helper_final'])) | set(map(int, word['start_extra']))
                         | {c['source'] for c in word['initial_corrections']})
            H = sorted(r for r in matrix if r >= 224 and r not in protected)
            need(len(H) == EXPECTED_H[index], 'eligible helper cardinality')
            prelude = [g for g in word['A'][:word['prelude_events']] if not engine.target(g[1])]
            need(all(g[0] == 'warp' and g[1] not in H for g in prelude), 'prelude violates independent eligible cut')
            literal = sorted(r for r in matrix if engine.contained(frames[r], V45))
            wanted = () if index < 3 else U12 if index == 3 else tuple(r for r in U12 if r not in (61, 63))
            need(literal == list(wanted), 'literal V45 support differs')
            observed = {r: matrix[r] for r in U12}
            raw_readouts[label] = observed
            coefficients = encoded_rows(matrix, U12)
            report = {
                'eligible_H': H, 'known_pivots_in_H': sorted(set(P4) & set(H)),
                'literal_V45_support': literal,
                'U12_terminal_frames': {str(r): list(frames[r]) for r in U12},
                'middle_gate_count': len(engine.literal_program(word)),
                'middle_operator_sha256': engine.operator_digest(matrix),
                'middle_coefficient_count': sum(map(len, matrix.values())),
                'prelude_events': word['prelude_events'], 'non_target_prelude_warps': len(prelude),
                'frame_replay': frame_counts,
                'U12_coefficients': coefficients, 'U12_coefficient_count': len(coefficients),
                'U12_coefficients_sha256': rows_digest(coefficients),
            }
            for support_name, support in (('U12', U12), ('literal', literal)):
                report[support_name] = analyze_support(matrix, set(H), support, engine)
                report[support_name]['with_known_P4'] = analyze_support(matrix, set(H) | set(P4), support, engine)
            need(report['U12']['inverse']['dimension'] == (4 if index < 2 else 0), 'fresh left dimension')
            need(report['U12']['forward']['dimension'] == (4 if index < 2 else 0), 'fresh right dimension')
            need(report['U12']['with_known_P4']['inverse']['dimension'] == 4, 'known-helper left dimension')
            if index < 2:
                need(report['U12']['pairing_determinant'] == '-128', 'original paired determinant')
                need(report['U12']['paired_nuisance_completion']['determinant'] == '256', 'original dyadic completion')
            else:
                need(report['U12']['eligible_block_zero'], 'fresh input block is not zero')
                need(report['U12']['nuisance_certificate']['determinant'] == '2', 'full nuisance determinant')
                need(report['U12']['with_known_P4']['U'] == [{str(h): '1'} for h in P4], 'known helper quotient differs')
            reports[label] = report
        need(raw_readouts['PR2894'] == raw_readouts['PR2917'], 'old-to-2917 complete observation changed')
        need(raw_readouts['PR2942'] == raw_readouts['PR2979_stage1'] == raw_readouts['PR2979_final'],
             'post-extraction complete observation changed')
        output['variants'][variant] = {'stages': reports,
            'complete_U12_equalities': [['PR2894', 'PR2917'], ['PR2942', 'PR2979_stage1', 'PR2979_final']]}
    # Different source placements must produce the same bounded map and spaces.
    for label in STAGES:
        a, b = [output['variants'][tag]['stages'][label] for tag in ('base', 'extra')]
        need(a['U12_coefficients'] == b['U12_coefficients'], 'provider bounded observations differ')
        need(a['eligible_H'] == b['eligible_H'] and a['U12'] == b['U12'] and a['literal'] == b['literal'],
             'provider bounded spaces differ')
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true', help='emit complete deterministic JSON instead of comparing EXPECTED.json')
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        need(result == read(PACKAGE / 'EXPECTED.json'), 'complete bounded comparison differs from EXPECTED.json')
        print(json.dumps({'status': result['status'], 'providers': 2, 'stages_per_provider': 5,
                          'common_observation_rows': len(U12), 'no_new_kappa': True}, sort_keys=True))


if __name__ == '__main__':
    main()
