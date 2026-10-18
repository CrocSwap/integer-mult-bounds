#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact source-bound census of all rank-seven terminal supports.

The existing PR2918 forward operator/frame engine is reused, not independent.
It is executed directly from the authenticated source bytes (no pyc importer).
The complete endpoint enumeration and certificate extraction are new here.
"""
import argparse
from collections import Counter, defaultdict
import copy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent / 'helper408-rank7-pairing'
PIN = '9360ba7312cf8961e672e9eb26c612719028d39d'
ENGINE_SHA = '56ca12652c45f57c74341a06be2dbce4617415656e65dfe08223a4afcf8de541'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(raw, expected, message):
    need(hashlib.sha256(raw).hexdigest() == expected, message)


def dyadic_unit(value):
    numerator = abs(value.numerator)
    denominator = value.denominator
    return bool(numerator) and numerator & (numerator - 1) == 0 and denominator & (denominator - 1) == 0


def engine():
    source = (PACKAGE / 'verify_boundary.py').read_bytes()
    authenticate(source, ENGINE_SHA, 'engine source pin mismatch')
    module = types.ModuleType('pinned_pr2918_boundary')
    module.__file__ = str(PACKAGE / 'verify_boundary.py')
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    return module


def endpoint_classes(frames):
    """Every codim-two endpoint is annihilator of unique triple {a,b,a^b}.

    Choose its two least nonzero members a<b<a^b. Distinct annihilator
    planes have distinct orthogonal complements. Lower-dimensional endpoints
    embed into rank-seven endpoints, and R(E) grows monotonically with E.
    """
    registers = sorted(frames)
    masks = [sum((1 << i) for i, r in enumerate(registers)
                 if all((a & f).bit_count() % 2 == 0 for f in frames[r]))
             for a in range(512)]
    classes = {}
    total = 0
    for a in range(1, 512):
        for b in range(a + 1, 512):
            if b >= (a ^ b):
                continue
            total += 1
            mask = masks[a] & masks[b]
            if mask not in classes:
                classes[mask] = {'R': [r for i, r in enumerate(registers) if (mask >> i) & 1],
                                 'annihilator': [a, b], 'multiplicity': 0}
            classes[mask]['multiplicity'] += 1
    need(total == 43435, 'rank-seven endpoint coverage mismatch')
    need(sum(c['multiplicity'] for c in classes.values()) == total, 'endpoint partition mismatch')
    return sorted(classes.values(), key=lambda c: (len(c['R']), c['R']))


def row_pivots(rows):
    """Exact row elimination returns rank and original pivot columns."""
    pivots = {}
    for original in rows:
        row = dict(original)
        while row:
            lead = min(row)
            if lead not in pivots:
                d = row[lead]
                pivots[lead] = {k: c / d for k, c in row.items()}
                break
            d = -row[lead]
            for k, c in pivots[lead].items():
                value = row.get(k, Q(0)) + d * c
                if value:
                    row[k] = value
                else:
                    row.pop(k, None)
    return sorted(pivots)


def exact_determinant(matrix):
    n = len(matrix)
    need(all(len(row) == n for row in matrix), 'nonsquare determinant')
    a = [list(row) for row in matrix]
    determinant = Q(1)
    for i in range(n):
        pivot = next((j for j in range(i, n) if a[j][i]), None)
        if pivot is None:
            return Q(0)
        if pivot != i:
            a[i], a[pivot] = a[pivot], a[i]
            determinant = -determinant
        d = a[i][i]
        determinant *= d
        for j in range(i + 1, n):
            c = a[j][i] / d
            for k in range(i + 1, n):
                a[j][k] -= c * a[i][k]
            a[j][i] = Q(0)
    return determinant


def screen(module, M, H, item):
    R = item['R']
    allowed = set(H)
    forbidden = set(M) - allowed
    nonscalar_columns = {c for r in R for c, word in M[r] if word}
    safe = forbidden - nonscalar_columns
    scalar_rows = [{c: a for (c, word), a in M[r].items() if c in safe and not word} for r in R]
    pivots = row_pivots(scalar_rows)
    result = dict(item)
    result['H_eligible'] = sorted(allowed.intersection(R))
    result['pure_scalar_forbidden_rank'] = len(pivots)
    if len(pivots) == len(R):
        determinant = exact_determinant([[M[r].get((c, ()), Q(0)) for c in pivots] for r in R])
        need(determinant != 0, 'chosen scalar minor singular')
        need(dyadic_unit(determinant), 'chosen scalar minor not dyadic unit')
        result['forbidden_minor_columns'] = pivots
        result['forbidden_minor_determinant'] = str(determinant)
        result['status'] = 'UNIVERSAL_SCALAR_MINOR_OBSTRUCTION'
        return result
    constraints = defaultdict(dict)
    for r in R:
        for (c, word), a in M[r].items():
            if c not in allowed or word:
                constraints[c, word][r] = a
    A, info = module.kernel(constraints.values(), R)
    result['A_dimension'] = len(A)
    result['A_info'] = info
    if not A:
        result['status'] = 'FREE_WORD_COEFFICIENT_OBSTRUCTION'
    else:
        exact = module.analyze(M, H, R)
        result['V_dimension'] = len(exact['V'])
        result['pairing_rank'] = len(row_pivots([{j: a for j, a in enumerate(row) if a} for row in exact['pairing']]))
        result['status'] = 'POSITIVE_PAIRING' if result['pairing_rank'] else 'ZERO_PAIRING_OBSTRUCTION'
        for field in ['V', 'Y', 'Alpha', 'U']:
            result[field] = [module.encode_vector(v) for v in exact[field]]
        result['pairing'] = [[str(a) for a in row] for row in exact['pairing']]
    return result


def run(label):
    v = engine()
    raw = (PACKAGE / 'sources/data' / ('PARENT-' + label + '.json.gz')).read_bytes()
    authenticate(raw, v.EXPECTED_SHA256[label], 'provider pin mismatch')
    p = json.loads(gzip.decompress(raw))
    frames, counts = v.terminal_frames(p)
    need(all(isinstance(x, int) and 0 <= x < 512 for frame in frames.values() for x in frame),
         'terminal frame outside F2^9')
    protected = set(map(int, p['helper_final'])) | set(map(int, p['start_extra'])) | {r['source'] for r in p['initial_corrections']}
    H = sorted(r for r in frames if r >= 224 and r not in protected)
    prelude_lenders = {g[1] for g in p['A'][:p['prelude_events']] if g[0] == 'warp'}
    need(not prelude_lenders.intersection(H), 'eligible input helper affected by prelude warp')
    classes = endpoint_classes(frames)
    M = v.replay(p)
    need(set(M) == set(frames), 'operator and frame coordinate sets differ')
    screens = [screen(v, M, H, c) for c in classes]
    need(all(c['status'] == 'UNIVERSAL_SCALAR_MINOR_OBSTRUCTION' for c in screens),
         'an endpoint lacks a dyadic scalar minor')
    report = {'label': label, 'pin': PIN, 'engine_sha256': ENGINE_SHA, 'source_sha256': hashlib.sha256(raw).hexdigest(),
            'operator_sha256': v.operator_digest(M), 'reuse': 'PR2918 forward operator and frame engine; new endpoint census',
            'H': H, 'H_rank_distribution': dict(sorted(Counter(len(frames[r]) for r in H).items())),
            'all_rank_distribution': dict(sorted(Counter(map(len, frames.values())).items())),
            'frame_replay_counts': counts, 'rank7_endpoint_count': 43435,
            'support_class_count': len(classes), 'status_distribution': dict(Counter(c['status'] for c in screens)),
            'weighted_status_distribution': dict(sum((Counter({c['status']: c['multiplicity']}) for c in screens), Counter())),
            'classes': screens}
    return report, {'module': v, 'provider_raw': raw, 'M': M, 'H': H, 'frames': frames}


def dyadic_inverse(matrix):
    """Construct a rational inverse, then verify both complete products."""
    n = len(matrix)
    a = [[Q(c) for c in row] + [Q(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for i in range(n):
        pivot = next((j for j in range(i, n) if a[j][i]), None)
        need(pivot is not None, 'minor singular')
        a[i], a[pivot] = a[pivot], a[i]
        d = a[i][i]
        a[i] = [c / d for c in a[i]]
        for j in range(n):
            if j != i:
                d = a[j][i]
                a[j] = [c - d * b for c, b in zip(a[j], a[i])]
    inverse = [row[n:] for row in a]
    need(all(c.denominator & (c.denominator - 1) == 0 for row in inverse for c in row), 'minor inverse not dyadic')
    for left, right in [(matrix, inverse), (inverse, matrix)]:
        need(all(sum(left[i][k] * right[k][j] for k in range(n)) == Q(i == j)
                 for i in range(n) for j in range(n)), 'inverse product identity failed')
    return inverse


def validate_class(item, M, H, frames):
    a, b = item['annihilator']
    need(0 < a < 512 and 0 < b < 512 and a != b, 'annihilator dimension mismatch')
    expected = {r for r, f in frames.items()
                if all((a & x).bit_count() % 2 == 0 and (b & x).bit_count() % 2 == 0 for x in f)}
    R = item['R']
    need(len(R) == len(set(R)) and set(R) == expected, 'terminal support incomplete')
    J = item['forbidden_minor_columns']
    need(len(J) == len(R) and len(set(J)) == len(J), 'minor dimensions mismatch')
    need(set(J) <= set(frames) - set(H), 'minor input is not forbidden')
    matrix = []
    for r in R:
        row = []
        for c in J:
            poly = {w: coefficient for (j, w), coefficient in M[r].items() if j == c}
            need(set(poly) <= {()}, 'minor contains nonempty word')
            row.append(poly.get((), Q(0)))
        matrix.append(row)
    determinant = exact_determinant(matrix)
    need(determinant and str(determinant) == item['forbidden_minor_determinant'], 'minor determinant mismatch')
    need(dyadic_unit(determinant), 'minor determinant not dyadic unit')
    inverse = dyadic_inverse(matrix)
    return max((c.denominator.bit_length() - 1 for row in inverse for c in row), default=0)


def validate_partition(items, partition):
    received = Counter()
    for item in items:
        key = tuple(sorted(item['R']))
        need(key not in received, 'duplicate support class')
        need(isinstance(item['multiplicity'], int) and item['multiplicity'] > 0, 'invalid support multiplicity')
        received[key] = item['multiplicity']
    need(received == partition, 'support partition incomplete')


def verify_provider(fixed, regenerated, context):
    """Check complete certificate semantics before canonical regeneration equality."""
    M, H, frames = (context[k] for k in ['M', 'H', 'frames'])
    partition = Counter({tuple(item['R']): item['multiplicity'] for item in regenerated['classes']})
    validate_partition(fixed['classes'], partition)
    inverse_bits = [validate_class(item, M, H, frames) for item in fixed['classes']]
    need(fixed == regenerated, 'fixed certificate differs from exact regeneration')
    controls = {}

    def rejects(name, action, expected):
        try:
            action()
        except ValueError as error:
            need(str(error) == expected, 'wrong control rejection: ' + str(error))
            controls[name] = {'rejected': True, 'reason': expected}
            return
        raise ValueError('invalid certificate accepted: ' + name)

    selected = next(item for item in fixed['classes'] if len(item['R']) > 1)
    rejects('source_drift', lambda: authenticate(context['provider_raw'] + b'!', fixed['source_sha256'],
                                                'provider pin mismatch'), 'provider pin mismatch')
    mutant = copy.deepcopy(selected)
    mutant['forbidden_minor_determinant'] = str(Q(mutant['forbidden_minor_determinant']) * 2)
    rejects('determinant_coefficient_mutation', lambda: validate_class(mutant, M, H, frames), 'minor determinant mismatch')
    mutant = copy.deepcopy(selected)
    mutant['forbidden_minor_columns'][0] = H[0]
    rejects('allow_eligible_input_as_nuisance', lambda: validate_class(mutant, M, H, frames), 'minor input is not forbidden')
    mutant = copy.deepcopy(selected)
    mutant['R'].pop()
    rejects('omit_terminal_register', lambda: validate_class(mutant, M, H, frames), 'terminal support incomplete')
    rejects('omit_support_class', lambda: validate_partition(fixed['classes'][1:], partition), 'support partition incomplete')
    mutant_matrix = copy.deepcopy(M)
    first_r, first_c = selected['R'][0], selected['forbidden_minor_columns'][0]
    mutant_matrix[first_r][first_c, (99,)] = Q(1)
    rejects('hidden_nonempty_operator_word', lambda: validate_class(selected, mutant_matrix, H, frames), 'minor contains nonempty word')
    mutant_matrix = copy.deepcopy(M)
    columns = set(selected['forbidden_minor_columns'])
    mutant_matrix[first_r] = {key: a for key, a in mutant_matrix[first_r].items() if key[0] not in columns}
    rejects('singular_nuisance_block', lambda: validate_class(selected, mutant_matrix, H, frames), 'minor determinant mismatch')
    mutant_matrix = copy.deepcopy(M)
    mutant_matrix[first_r] = {key: 3 * a for key, a in mutant_matrix[first_r].items()}
    mutant = copy.deepcopy(selected)
    mutant['forbidden_minor_determinant'] = str(3 * Q(mutant['forbidden_minor_determinant']))
    rejects('rational_but_not_dyadic_unit', lambda: validate_class(mutant, mutant_matrix, H, frames), 'minor determinant not dyadic unit')
    positive = copy.deepcopy(selected)
    positive['R'] = list(reversed(positive['R']))
    positive['forbidden_minor_columns'] = list(reversed(positive['forbidden_minor_columns']))
    validate_class(positive, M, H, frames)
    controls['simultaneous_row_column_reversal'] = {'accepted': True}
    v = context['module']
    transform_raw = (PACKAGE / 'sources/data/TRANSFORM.json').read_bytes()
    authenticate(transform_raw, v.TRANSFORM_SHA256, 'calibration transform pin mismatch')
    calibration = v.calibrate(M, H, frames, json.loads(transform_raw))
    return {'rank7_endpoints': fixed['rank7_endpoint_count'], 'support_classes': len(fixed['classes']),
            'nonempty_support_classes': sum(bool(c['R']) for c in fixed['classes']),
            'classes_with_eligible_H_slot': sum(bool(c['H_eligible']) for c in fixed['classes']),
            'endpoints_with_eligible_H_slot': sum(c['multiplicity'] for c in fixed['classes'] if c['H_eligible']),
            'eligible_H_slots': len({r for c in fixed['classes'] for r in c['H_eligible']}),
            'scalar_minor_determinants': dict(sorted(Counter(c['forbidden_minor_determinant'] for c in fixed['classes']).items())),
            'max_support_size': max(len(c['R']) for c in fixed['classes']),
            'max_minor_inverse_denominator_bits': max(inverse_bits),
            'all_minor_entries_scalar': True, 'all_minor_inverses_dyadic': True,
            'source_sha256': fixed['source_sha256'], 'operator_sha256': fixed['operator_sha256'],
            'H_rank_distribution': fixed['H_rank_distribution'],
            'controls': controls, 'rank8_calibration': calibration}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='explicitly regenerate the fixed certificate before verifying')
    args = parser.parse_args()
    path = HERE / 'certificates.json'
    # Missing evidence is a failure unless generation was explicitly requested.
    if not args.write:
        need(path.is_file(), 'fixed certificates.json is missing')
    generated, contexts = {}, {}
    for label in ['base', 'extra']:
        generated[label], contexts[label] = run(label)
        generated[label] = json.loads(json.dumps(generated[label], sort_keys=True))
    envelope = {'schema_version': 1, 'providers': generated}
    if args.write:
        path.write_text(json.dumps(envelope, indent=2, sort_keys=True) + '\n')
    fixed = json.loads(path.read_text())
    need(set(fixed) == {'schema_version', 'providers'} and fixed['schema_version'] == 1,
         'certificate schema mismatch')
    need(set(fixed['providers']) == {'base', 'extra'}, 'certificate provider coverage mismatch')
    summaries = {label: verify_provider(fixed['providers'][label], generated[label], contexts[label])
                 for label in ['base', 'extra']}
    need(fixed == envelope, 'canonical certificate envelope mismatch')
    print(json.dumps({'status': 'PASS_ALL_RANK_LE7_ENDPOINTS_DYADIC_NUISANCE_SURJECTIVITY',
                      'schema_version': 1, 'scientific_pin': PIN, 'engine_sha256': ENGINE_SHA,
                      'certificate_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                      'providers': summaries}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
