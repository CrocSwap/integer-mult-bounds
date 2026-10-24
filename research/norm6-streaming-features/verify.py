#!/usr/bin/env python3
"""Exact new-result verification; no predecessor executable is imported.

Krzysztof Wojt with substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
from fractions import Fraction
import hashlib
from itertools import product
import json
from math import isqrt
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from compression import (compress_target, elimination_multipliers, evaluation_budget, gram_times,
                         quadratic, require, shell_relations,
                         source_values, validate_gram)
from oracle import audit_compression, audit_relations
from streaming import DENOMINATOR, feature_stream, stream_budget

GRAM_PATH = 'research/norm6-dyadic-decoder/sources/P48p-GRAM.json'


def determinant(matrix):
    """Fraction-free Bareiss; independent of the explicit pivot inverse."""
    a = [list(row) for row in matrix]
    n = len(a)
    sign, previous = 1, 1
    for k in range(n-1):
        pivot = next((i for i in range(k, n) if a[i][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            a[pivot], a[k] = a[k], a[pivot]
            sign = -sign
        current = a[k][k]
        for i in range(k+1, n):
            for j in range(k+1, n):
                value = a[i][j]*current - a[i][k]*a[k][j]
                require(value % previous == 0, 'Bareiss exact divisibility')
                a[i][j] = value // previous
            a[i][k] = 0
        previous = current
    return sign*a[-1][-1]


def inverse(matrix):
    """Exact rational elimination, used only for source-coordinate bounds."""
    n = len(matrix)
    a = [[Fraction(v) for v in row] + [Fraction(i == j) for j in range(n)]
         for i, row in enumerate(matrix)]
    for k in range(n):
        p = next(i for i in range(k, n) if a[i][k])
        a[k], a[p] = a[p], a[k]
        scale = a[k][k]
        a[k] = [v/scale for v in a[k]]
        for i in range(n):
            if i != k and a[i][k]:
                scale = a[i][k]
                a[i] = [u-scale*v for u, v in zip(a[i], a[k])]
    return [row[n:] for row in a]


def rejected(function, label):
    try:
        function()
    except (ValueError, TypeError):
        return label
    raise ValueError('control did not reject: '+label)


def check_stream(gram, x, y, features, pivots, numerators, iterator=None):
    """Materialized reference is verifier-only, never part of the stream."""
    expected_source = source_values(x, features)
    positions = {key: i for i, key in enumerate(features)}
    pivot_set = set(pivots)
    expected_keys = [key for i, key in enumerate(features) if i not in pivot_set]
    frozen = (tuple(map(tuple, gram)), tuple(x), tuple(y))
    production_iterator = iterator is None
    iterator = feature_stream(gram, x, y) if production_iterator else iterator
    count, total, owned_slots_max = 0, 0, 0
    for key, source, target in iterator:
        require(count < len(expected_keys) and key == expected_keys[count], 'stream order/count')
        j = positions[key]
        require(type(source) is int and type(target) is int, 'stream integer types')
        require(source == expected_source[j] and 2*target == numerators[j], 'stream feature mismatch')
        require(abs(source) <= 32768 and abs(target) <= 146804, 'stream global values')
        if production_iterator and count % 1024 == 0:
            frame = iterator.gi_frame.f_locals
            owned = {name: len(value) for name, value in frame.items()
                     if isinstance(value, list) and name not in ('gram', 'x', 'y')}
            require(owned == {name: len(gram) for name in ('v', 'nu', 'xsq', 'vsq')},
                    'unexpected owned stream array')
            owned_slots_max = max(owned_slots_max, sum(owned.values()))
            require(all(abs(value) < 2**18 for value in frame.values()
                        if type(value) is int), 'stream scalar prefix width')
        total += source*target
        count += 1
    require(count == len(expected_keys), 'incomplete stream')
    if production_iterator:
        require(iterator.gi_frame is None, 'completed stream retains frame')
    require(frozen == (tuple(map(tuple, gram)), tuple(x), tuple(y)), 'borrowed inputs mutated')
    v = gram_times(gram, y)
    t = sum(u*w for u, w in zip(x, v))
    require(3*total == 4*(t**3-4*t), 'stream kernel consumer')
    require(abs(total) <= 19600*32768*146804, 'stream accumulator bound')
    return count, owned_slots_max


def run():
    gram_bytes = (ROOT/GRAM_PATH).read_bytes()
    gram = json.loads(gram_bytes)
    require(len(gram) == 48, 'actual source dimension')
    validate_gram(gram)
    require(max(max(row) for row in gram) == 10, 'actual maximum entry')
    require(max(abs(gram[i][j]) for i in range(48) for j in range(48)
                if i != j) == 5, 'actual maximum off-diagonal')
    prepared = shell_relations(gram)
    features, rows, pivots = prepared
    require(len(features) == 19648 and len(set(pivots)) == 48, 'feature counts')
    order = [0, 4] + [i for i in range(48) if i not in (0, 4)]
    minor = [[rows[i].get(j, 0) for j in pivots] for i in order]
    minor_det = determinant(minor)
    require(minor_det == -8, 'actual dyadic-unit minor')
    relation_evidence = list(audit_relations(gram, features, rows))
    # Check the whole inverse map, not just its action at selected targets.
    for k in range(48):
        basis = [int(j == k) for j in range(48)]
        mu_basis = elimination_multipliers(gram, basis)
        for j, feature in enumerate(pivots):
            require(sum(rows[i].get(feature, 0)*mu_basis[i] for i in range(48))
                    == 8*(j == k), 'entire pivot inverse map')

    column_l1 = [0]*len(features)
    for row in rows:
        for j, value in row.items():
            column_l1[j] += abs(value)
    require(max(column_l1) <= 15, 'relation column norm bound')

    # Exact multiplication checks the dual bound's inverse. Positive
    # definiteness remains a cited geometric premise, not a replay target.
    dual = inverse(gram)
    for i in range(48):
        for j in range(48):
            require(sum(gram[i][k]*dual[k][j] for k in range(48)) == (i == j),
                    'inverse identity')
    max_inverse_diagonal = max(dual[i][i] for i in range(48))
    require(max_inverse_diagonal.denominator == 1, 'integral dual diagonal')
    coordinate_bound = isqrt(6*max_inverse_diagonal.numerator)

    # A complete small coefficient cube, not the complete P48p shell.
    shell = []
    for prefix in product(range(-2, 3), repeat=4):
        x = list(prefix) + [0]*44
        if quadratic(gram, x) == 6:
            shell.append(x)
    for i in range(48):
        if gram[i][i] == 6:
            x = [int(j == i) for j in range(48)]
            shell.extend((x, [-v for v in x]))
    shell = [list(x) for x in sorted(set(map(tuple, shell)))]
    require(len(shell) >= 20, 'nonempty actual-shell diagnostics')
    target_indices = sorted(set([0, len(shell)//3, len(shell)//2, len(shell)-1]))
    pairs = 0
    streamed_coordinates = 0
    owned_stream_slots = 0
    polynomial_checks = []
    max_fixture_numerator = 0
    for index in target_indices:
        y = shell[index]
        v = gram_times(gram, y)
        numerators, mu = compress_target(gram, v, prepared=prepared)
        require(max(map(abs, v)) <= 7, 'dual-coordinate Cauchy bound')
        require(max(map(abs, numerators)) <= 293608, 'global numerator bound')
        max_fixture_numerator = max(max_fixture_numerator, max(map(abs, numerators)))
        polynomial_checks.append(audit_compression(gram, v, features, numerators, mu))
        for x in shell:
            value = sum(u*w for u, w in zip(source_values(x, features), numerators))
            t = sum(u*w for u, w in zip(x, v))
            require(3*value == 8*(t**3-4*t), 'literal compressed kernel')
            count, slots = check_stream(gram, x, y, features, pivots, numerators)
            streamed_coordinates += count
            owned_stream_slots = max(owned_stream_slots, slots)
            pairs += 1

    # Arbitrary targets and an off-shell source discriminate the precise
    # shell identity from an incorrect global polynomial identity.
    arbitrary_v = [((i*7+3) % 11)-5 for i in range(48)]
    coefficients, mu = compress_target(gram, arbitrary_v, prepared=prepared)
    polynomial_checks.append(audit_compression(gram, arbitrary_v, features, coefficients, mu))
    offshell = [2] + [0]*47
    lhs = sum(c*f for c, f in zip(coefficients, source_values(offshell, features)))
    t = sum(u*v for u, v in zip(offshell, arbitrary_v))
    defect3 = 3*lhs - 8*(t**3-4*t)
    expected3 = -3*sum(u*x for u, x in zip(mu, offshell))*(quadratic(gram, offshell)-6)//2
    require(defect3 == expected3 and defect3 != 0, 'nonzero off-shell defect')

    small_pairs = 0
    for d in (2, 3, 5):
        small = [[6 if i == j else (-1 if {i, j} == {0, 1} else 0)
                  for j in range(d)] for i in range(d)]
        prep = shell_relations(small, 0, 1)
        sf, sr, sp = prep
        audit_relations(small, sf, sr)
        for v in product(range(-2, 3), repeat=d):
            c, m = compress_target(small, list(v), 0, 1, prep)
            audit_compression(small, list(v), sf, c, m)
            require(all(c[j] == 0 for j in sp), 'small pivot cancellation')
            small_pairs += 1

    controls = []
    bad = [dict(row) for row in rows]
    bad[0][0] += 1
    controls.append(rejected(lambda: audit_relations(gram, features, bad), 'wrong f coefficient'))
    bad = [dict(row) for row in rows]
    bad[0][len(gram)] = 1
    controls.append(rejected(lambda: audit_relations(gram, features, bad), 'wrong shell constant'))
    changed = list(coefficients)
    changed[0] += 1
    controls.append(rejected(lambda: audit_compression(gram, arbitrary_v, features, changed, mu),
                             'corrupted retained feature'))
    changed_mu = list(mu)
    changed_mu[0] += 1
    controls.append(rejected(lambda: audit_compression(gram, arbitrary_v, features, coefficients, changed_mu),
                             'wrong elimination multiplier'))
    controls.append(rejected(lambda: audit_compression(gram, arbitrary_v, features,
                             [8*c for c in coefficients], mu), 'omitted final factor eight'))
    bad_gram = [list(row) for row in gram]
    bad_gram[0][4] = bad_gram[4][0] = 1
    controls.append(rejected(lambda: shell_relations(bad_gram), 'wrong pivot sign'))
    bad_gram = [list(row) for row in gram]
    bad_gram[0][1] += 1
    controls.append(rejected(lambda: shell_relations(bad_gram), 'asymmetric Gram'))
    bad_gram = [list(row) for row in gram]
    bad_gram[1][1] += 1
    controls.append(rejected(lambda: shell_relations(bad_gram), 'odd Gram diagonal'))
    controls.append(rejected(lambda: compress_target(gram, [0]*47), 'short target'))
    controls.append(rejected(lambda: compress_target(gram, [True]+[0]*47), 'boolean coordinate'))
    controls.append(rejected(lambda: shell_relations(gram, 0, 0), 'repeated pivot'))

    y = shell[0]
    c, _ = compress_target(gram, gram_times(gram, y), prepared=prepared)
    early = feature_stream(gram, shell[0], y)
    next(early)
    early.close()
    require(early.gi_frame is None, 'early close retains stream frame')
    omitted = feature_stream(gram, shell[0], y)
    next(omitted)
    controls.append(rejected(lambda: check_stream(gram, shell[0], y, features, pivots, c, omitted),
                             'omitted first stream record'))
    omitted.close()
    def wrong_coefficient():
        first = True
        for key, source, target in feature_stream(gram, shell[0], y):
            yield key, source, target+1 if first else target
            first = False
    changed_stream = wrong_coefficient()
    controls.append(rejected(lambda: check_stream(gram, shell[0], y, features, pivots, c, changed_stream),
                             'corrupted stream target'))
    changed_stream.close()

    bindings = {}
    for name in ('compression.py', 'streaming.py', 'oracle.py', 'verify.py', 'PROOF.md', 'README.md',
                 'TASK.json', 'SOURCES.json', 'VERIFY.json'):
        bindings[name] = hashlib.sha256((HERE/name).read_bytes()).hexdigest()
    return {
        'schema': 'norm6-streaming-features/v1',
        'status': 'PASS_NORM6_STREAMING_FEATURES',
        'gram_sha256': hashlib.sha256(gram_bytes).hexdigest(),
        'package_sha256': bindings,
        'dimension': 48, 'original_features': len(features), 'removed_features': len(pivots),
        'retained_features': len(features)-len(pivots), 'pivot_determinant': minor_det,
        'relation_column_l1_max': max(column_l1), 'relation_oracle': relation_evidence,
        'pivot_inverse_entries_checked': 48*48,
        'polynomial_oracle': polynomial_checks,
        'actual_shell_fixture_count': len(shell), 'actual_shell_pairs': pairs,
        'small_all_polynomial_targets': small_pairs,
        'max_fixture_numerator': max_fixture_numerator,
        'target_denominator': 512, 'global_target_numerator_bound': 293608,
        'max_inverse_diagonal': str(max_inverse_diagonal),
        'source_coordinate_bound': coordinate_bound,
        'source_feature_bound': coordinate_bound**3,
        'streamed_coordinates_checked': streamed_coordinates,
        'observed_owned_stream_vector_slots': owned_stream_slots,
        'stream_target_denominator': DENOMINATOR,
        'stream_target_numerator_bound': 146804,
        'stream_preprocessing_signed_bits': 19,
        'stream_pair_accumulator_signed_bits': 48,
        'stream_pair_accumulator_absolute_bound': 19600*32768*146804,
        'stream_budget': stream_budget(48),
        'offshell_defect_times_3': defect3,
        'rejected_controls': controls, 'evaluation_budget': evaluation_budget(48),
        'scope': 'Written shell identity plus exact finite corroboration; no physical tariff or new kappa.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit-result', action='store_true', help='generate receipt on stdout')
    args = parser.parse_args()
    result = run()
    if args.emit_result:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        expected_path = HERE/'RESULT.json'
        require(expected_path.stat().st_size < 65536, 'receipt size limit')
        expected = json.loads(expected_path.read_text(encoding='utf-8'))
        require(json.dumps(expected, sort_keys=True) == json.dumps(result, sort_keys=True),
                'generated receipt mismatch')
        print(result['status'], 'features=19600 denominator=256 live_slots=320',
              'pairs='+str(result['actual_shell_pairs']),
              'polynomial_targets='+str(result['small_all_polynomial_targets']),
              'controls='+str(len(result['rejected_controls'])))


if __name__ == '__main__':
    main()
