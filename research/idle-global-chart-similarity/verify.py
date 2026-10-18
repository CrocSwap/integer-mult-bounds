#!/usr/bin/env python3
"""Full-address trace obstruction to one-site native phase absorption.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import types

PACKAGE = Path(__file__).resolve().parent
N = 1 << 73


def require(ok, why):
    if not ok:
        raise ValueError(why)


def load(name):
    path = PACKAGE / (name + '.py')
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', optimize=0), module.__dict__)
    return module


def plus(a, b):
    return a[0] + b[0], a[1] + b[1]


def minus(a, b):
    return a[0] - b[0], a[1] - b[1]


def times(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def encode(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(v) for v in value]
    return value


def phase_terms(poly, algebra):
    return [{'phase': list(q), 'coefficient': c,
             'complete_gauss_sum': list(algebra.gauss(q))}
            for q, c in sorted(poly.items())]


def test_phase_sum(algebra):
    powers = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    count = 0
    for n in range(4):
        pair_keys = list(itertools.combinations(range(n), 2))
        for linear in itertools.product(range(4), repeat=n):
            low = sum((v & 1) << i for i, v in enumerate(linear))
            high = sum(((v >> 1) & 1) << i for i, v in enumerate(linear))
            for mask in range(1 << len(pair_keys)):
                edges = sum(algebra.PAIR[key] for at, key in enumerate(pair_keys) if mask >> at & 1)
                phase = low, high, edges
                brute = tuple(sum(powers[algebra.value(phase, x)][j] for x in range(1 << n))
                              for j in range(2))
                require(algebra.gauss(phase, n) == brute, 'complete tiny quadratic sum')
                count += 1
    require(count == 549, 'complete tiny phase coverage')
    for mask in range(1, 16):
        phase = algebra.parity(mask)
        for x in range(16):
            require(algebra.value(phase, x) == (mask & x).bit_count() % 2,
                    'parity phase expansion')
        require(algebra.gauss(phase, 4) == (8, 8), 'nonzero parity complete sum')
        require(algebra.gauss(algebra.qadd(phase, phase), 4) == (0, 0),
                'nonzero signed parity complete sum')
    # A dropped quadratic coefficient changes the complete sum, not only a representation.
    require(algebra.gauss((0, 0, algebra.PAIR[0, 1]), 2) == (2, 0),
            'quadratic sign control')
    require(algebra.gauss(algebra.ZERO, 2) == (4, 0), 'zero quadratic control')
    return {'all_quadratic_forms_through_3_variables': count,
            'four_variable_parity_forms': 15,
            'quadratic_coefficient_defect_sensitive': True}


def test_cross_character_conjugacy():
    # One C1 on a four-address stream has exactly two i eigenvalues.
    # This permutation moves one of them to another stream at the same character
    # as the retained one. Old fiber-rank tests reject; full similarity must accept.
    width, streams = 4, 8
    diagonal = [0] * (width * streams)
    diagonal[1] = diagonal[3] = 1
    permutation = list(range(width * streams))
    permutation[3], permutation[5] = permutation[5], permutation[3]
    result = [diagonal[permutation[j]] for j in range(width * streams)]
    require(result[1] == result[5] == 1 and result[3] == 0,
            'cross-character conjugate layout')
    powers = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    for j in range(width * streams):
        # Apply P^-1 D P to every independent dirty basis coordinate.
        encoded = permutation[j]
        amplitude = powers[diagonal[encoded]]
        decoded = permutation[encoded]
        require(decoded == j and amplitude == powers[result[j]],
                'full conjugacy column check')
    trace_square = tuple(sum(powers[2 * e % 4][k] for e in result) for k in range(2))
    require(trace_square == (28, 0), 'positive global square trace')
    require(times(minus(powers[result[1]], (1, 0)),
                  minus(powers[result[5]], (1, 0))) == (0, -2),
            'old character-rank test genuinely rejects positive control')
    return {'complete_independent_columns': 32,
            'global_square_trace': trace_square,
            'same_character_rank_two_minor': (0, -2),
            'accepted_cross_character_conjugacy': True}


def run():
    cut, algebra = load('cut_model'), load('phase_algebra')
    cut.authenticate()
    original, context = cut.source_context()
    before = {j: list(v) for j, v in context['residual'].items()}
    moved = {j: list(v) for j, v in before.items()}
    moved[10].remove(16)
    moved[12].append(16)
    require(original.orthonormal(moved[10]) and original.orthonormal(moved[12]),
            'orthonormal changed residuals')
    require([len(before[j]) for j in (10, 12)] == [48, 48]
            and [len(moved[j]) for j in (10, 12)] == [47, 49], 'exact recursive ranks')

    baseline_ops, _ = algebra.events(context, before)
    baseline = algebra.identity()
    for event in baseline_ops:
        algebra.left(baseline, event)
    target_phase = algebra.qsum(1 << i for i in range(73))
    require(baseline == algebra.identity(target_phase), 'complete symbolic baseline operator')

    operations, sites = algebra.events(context, moved)
    characters = [0, 16, 33554432, 33554448, 1, 2, 3, 17, 33554449, (1 << 73) - 1]
    literal = {}
    for x in characters:
        target = [[(Fraction(a), Fraction(b)) for a, b in row]
                  for row in original.baseline_target(x)]
        ops, at = cut.operations(original, context, moved, x)
        required, overlay = cut.requirements(ops, at, target)
        require(overlay == original.replay(context, moved, x, original.stage_blocks(context['template'])),
                'canonical complete overlay')
        literal[x] = required

    rows = {}
    squared_five = {4, 6, 8, 13, 14, 15}
    comparisons = 0
    for child, matrix in algebra.required_matrices(operations, sites):
        for x in characters:
            require(algebra.evaluate(matrix, x) == literal[x][child], 'literal cut/transcription')
            comparisons += 1
        trace_poly = {}
        for i in range(8):
            trace_poly = algebra.p_add(trace_poly, matrix[i][i])
        square_poly = algebra.trace_square(matrix)
        t1, t2 = algebra.p_sum(trace_poly), algebra.p_sum(square_poly)
        expected_square = (5 if child in squared_five else 6) * N
        require(t2 == (expected_square, 0), 'source-bound complete square trace')
        require(t2 != (7 * N, 0), 'every positive-rank native tensor rejected')
        centered = minus(t1, (7 * N, 0))
        rank_zero_gap = minus(times(centered, centered),
                              (N * (t2[0] - 7 * N), N * t2[1]))
        require(rank_zero_gap != (0, 0), 'rank-zero arbitrary nonzero scalar rejected')
        if len(moved[child]) == 0:
            require(t1 == (7 * N, 0), 'zero-rank-site first trace')
        # The square expressions actually need only orthogonality of nonzero
        # binary characters. General quadratic sums are used for the first trace.
        require(all(q[0] == 0 and q[2] == 0 for q in square_poly),
                'square trace reduces to ordinary signed binary characters')
        rows[child] = {
            'moved_native_rank': len(moved[child]),
            'literal_elementary_cut': sites[child],
            'matrix_phase_terms': sum(len(v) for row in matrix for v in row),
            'trace': t1, 'trace_square': t2,
            'trace_per_N': [Fraction(v, N) for v in t1],
            'trace_square_per_N': [Fraction(v, N) for v in t2],
            'trace_polynomial': phase_terms(trace_poly, algebra),
            'trace_square_polynomial': phase_terms(square_poly, algebra),
            'rank_zero_scalar_invariant_gap': rank_zero_gap,
            'all_positive_native_ranks_rejected': True,
            'arbitrary_rank_zero_scalar_rejected': True,
        }
    require(set(rows) == set(range(20)), 'complete site coverage')
    require(comparisons == 200, 'literal finite coverage')

    # This control catches the precise rank-zero/global-phase loophole:
    # iI on one stream has square trace6N, but first trace(7+i)N, not7N.
    rank_zero_i = ((7 * N, N), (6 * N, 0))
    require(rank_zero_i[1] == rows[0]['trace_square']
            and rank_zero_i[0] != rows[0]['trace'], 'rank-zero phase needs both invariants')
    return encode({
        'status': 'PASS_IDLE_GLOBAL_CHART_SIMILARITY_OBSTRUCTION',
        'base': cut.BASE, 'address_dimension': 73, 'addresses_per_stream': N,
        'owner_replica': 0, 'port': 0,
        'transfer': {'axis': 16, 'donor': 10, 'receiver': 12,
                     'old_ranks': [48, 48], 'moved_ranks': [47, 49]},
        'sites': rows, 'trace_square_5N_sites': sorted(squared_five),
        'trace_square_6N_sites': sorted(set(rows) - squared_five),
        'native_positive_rank_square_trace': 7 * N,
        'all_address_baseline_exact': True,
        'elementary_events': len(operations), 'canonical_fill_rows_authenticated': original.TOTAL_ROWS,
        'literal_characters': characters, 'literal_cut_comparisons': comparisons,
        'all_address_scope': 'Exact symbolic sums of trace and squared trace on F2^73; no address sampling used for the invariant.',
        'chart_contract': 'Arbitrary invertible reciprocal linear chart on all8 streams and addresses plus any d dirty spectator coordinates restored. One native tensor phase on active volume2^73, any rank0..73, either direction, and any nonzero scalar multiplier.',
        'controls': {'quadratic_sums': test_phase_sum(algebra),
                     'cross_character_positive': test_cross_character_conjugacy(),
                     'rank_zero_active_i_phase': True},
        'sources_sha256': hashlib.sha256((PACKAGE / 'SOURCES.json').read_bytes()).hexdigest(),
        'new_kappa': None,
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='write a new receipt; default checks fixed RESULT.json')
    args = parser.parse_args()
    result = run()
    if args.output:
        with args.output.open('x') as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        require(result == json.loads((PACKAGE / 'RESULT.json').read_text()), 'fixed result mismatch')
    print('PASS_IDLE_GLOBAL_CHART_SIMILARITY_OBSTRUCTION sites=20 addresses=2^73 no_new_kappa')


if __name__ == '__main__':
    main()
