#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Read-only exact finite-premise checker for PROOF.md, not a formal proof engine.
Python 3.10+ standard library. No Git, network, imports from other packages or writes.
GPT-6 Astra implementation; E8 source-order attribution is in SOURCES.json.
"""
import argparse
import copy
import hashlib
import itertools
import json
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODEL_SHA256 = '084c49e50987f40f4787d5d1ade73cbd1e6420224f94df74719812939537066c'
NORMALS = [0, 1, 56, 87]
CAPACITIES = [3, 2, 2, 2]
ANCHOR_A = [2, 6, 10]
ANCHOR_B = [14, 18, 22]
RESIDUAL = [87, 80, 62]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        require(key not in obj, 'duplicate JSON key: ' + key)
        obj[key] = value
    return obj


def invalid_constant(value):
    raise ValueError('non-finite JSON constant: ' + value)


def parse_json(raw):
    return json.loads(raw, object_pairs_hook=unique_object, parse_constant=invalid_constant)


def read_json(path):
    try:
        return parse_json(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, ValueError) as exc:
        raise ValueError('cannot read valid ' + path.name + ': ' + str(exc)) from exc


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def rational_rank(matrix):
    rows = [[Q(x) for x in row] for row in matrix]
    height = 0
    for col in range(len(rows[0]) if rows else 0):
        pivot = next((i for i in range(height, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[height], rows[pivot] = rows[pivot], rows[height]
        scale = rows[height][col]
        rows[height] = [x / scale for x in rows[height]]
        for i in range(height + 1, len(rows)):
            scale = rows[i][col]
            rows[i] = [a - scale * b for a, b in zip(rows[i], rows[height])]
        height += 1
        if height == len(rows):
            break
    return height


def geometry():
    # This direct line enumeration equals first representatives of the 240-root
    # source ordering, without generating or importing that predecessor program.
    lines = []
    for i, j in itertools.combinations(range(8), 2):
        for sign in (1, -1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            lines.append(row)
    for tail in itertools.product((1, -1), repeat=7):
        if tail.count(-1) % 2 == 0:
            lines.append([1, *tail])
    require(len(lines) == len(set(map(tuple, lines))) == 120, '120 distinct source lines')
    products = [[dot(x, y) for y in lines] for x in lines]
    require(all(x % 4 == 0 for row in products for x in row), 'integral true inner products')
    gram = [[x // 4 for x in row] for row in products]
    require(all(gram[i][i] == 2 for i in range(120)), 'root squared norm 2')
    require({gram[i][j] for i in range(120) for j in range(120) if i != j} == {-1, 0, 1}, 'off-diagonal inner products')
    frame = []
    for i in range(0, 8, 2):
        for sign in (1, -1):
            row = [0] * 8
            row[i], row[i + 1] = 2, 2 * sign
            frame.append(lines.index(row))
    require(frame == [0, 1, 26, 27, 44, 45, 54, 55], 'source puncture')
    require(all(gram[i][j] == 0 for i, j in itertools.combinations(frame, 2)), 'orthogonal puncture')
    live = set(range(120)) - set(frame)
    supports = [{r for r in live if gram[a][r] == 0 or r == a} for a in NORMALS]
    mask = [[r, s] for r in sorted(live) for s in sorted(live) if gram[r][s] % 2 == 0]
    require(len(mask) == 6720, 'all ordered even entries, including diagonals')
    require(all([s, r] in mask for r, s in mask), 'both mask orientations')
    return lines, gram, frame, live, supports, mask


def check_premises(geo, A, B, R, capacities, multiplier=2):
    """Check the precise finite hypotheses of the written rank-two crown argument."""
    lines, gram, frame, live, supports, mask = geo
    require(capacities == CAPACITIES, 'fixed capacity assignment [3,2,2,2]')
    require(multiplier == 2, 'source target is 2G, not a free diagonal parameter')
    require(len(A) == len(B) == len(R) == 3 and len(set(A + B + R)) == 9, 'nine distinct certificate roots')
    require(set(A + B + R) <= live, 'all nine roots live')
    require(all([a in s for s in supports] == [False, False, False, True] for a in A + B), 'exclusive anchors')
    require(all((gram[a][b] == 0) == (i != j) for i, a in enumerate(A) for j, b in enumerate(B)), 'crown off-matching edges only')
    for side, other in ((A, B), (B, A)):
        require(all(any(gram[a][c] == gram[b][c] == 0 for c in other) for a, b in itertools.combinations(side, 2)), 'common opposite neighbour for every same-side pair')
    require(all(multiplier * gram[a][a] == 4 for a in A + B), 'nonzero anchor diagonals')
    witnesses = []
    for r in R:
        require([r in s for s in supports] == [False, True, False, True], 'residual group memberships')
        a = next((a for a in A if gram[r][a] == 0), None)
        b = next((b for b in B if gram[r][b] == 0), None)
        require(a is not None and b is not None, 'orthogonal neighbour in each anchor part')
        witnesses.append([a, b])
    require(all([r, s] in mask for r in R for s in R), 'entire residual matrix is masked')
    target = [[multiplier * gram[r][s] for s in R] for r in R]
    require(target == [[4, 0, 0], [0, 4, 0], [0, 0, 4]], 'residual target 4I3')
    require(rational_rank(target) == 3 > capacities[1], 'residual rank exceeds remaining capacity')
    return witnesses, target


def derive_certificate(model):
    # Canonical comparison rejects changed domains, added verdicts, booleans in
    # integer fields, weakened support/mask clauses and unknown fields alike.
    require(digest(model) == MODEL_SHA256, 'MODEL.json differs from the fixed theorem domain')
    geo = geometry()
    lines, gram, frame, live, supports, mask = geo
    require([lines[n] for n in NORMALS] == model['normal_doubled_coordinates'], 'normal index/coordinate binding')
    A, B, R = ANCHOR_A, ANCHOR_B, RESIDUAL
    witnesses, target = check_premises(geo, A, B, R, CAPACITIES)
    equations = {(x, x) for x in A + B + R}
    for i, a in enumerate(A):
        for j, b in enumerate(B):
            if i != j:
                equations.update(((a, b), (b, a)))
    for r, pair in zip(R, witnesses):
        for x in pair:
            equations.update(((r, x), (x, r)))
    equations.update(itertools.product(R, R))
    require(len(equations) == 39 and all([r, s] in mask for r, s in equations), '39 ordered proof equations are source-masked')
    certificate = dict(
        schema_version=1, model_sha256=MODEL_SHA256,
        normal_source_indices=NORMALS, term_capacities=CAPACITIES,
        normal_doubled_coordinates=[lines[n] for n in NORMALS],
        punctured_source_indices=frame, live_count=len(live),
        source_lines_sha256=digest(lines), ordered_mask_count=len(mask), ordered_mask_sha256=digest(mask),
        co_star_sizes=[len(s) for s in supports], co_star_sha256=[digest(sorted(s)) for s in supports],
        anchor_A=A, anchor_B=B, residual_roots=R,
        nine_root_coordinates={str(i): lines[i] for i in sorted(A + B + R)},
        memberships={str(i): [i in s for s in supports] for i in sorted(A + B + R)},
        anchor_cross_gram=[[gram[a][b] for b in B] for a in A],
        residual_anchor_gram=[[gram[r][a] for a in A + B] for r in R],
        forced_zero_anchor_pairs=witnesses, residual_target=target, residual_target_rank=rational_rank(target),
        remaining_group_normal=1, remaining_group_capacity=2,
        ordered_proof_equations=[[r, s, 2 * gram[r][s]] for r, s in sorted(equations)])
    return certificate, geo


def same_document(actual, expected, label):
    require(canonical(actual) == canonical(expected), label + ' differs from independently derived data')


def controls(model, certificate, geo):
    passed = []

    def reject(label, call):
        try:
            call()
        except ValueError:
            passed.append(label)
        else:
            raise ValueError('negative control accepted: ' + label)

    for label, A, R, cap, factor in [
        ('crown_capacity_three', ANCHOR_A, RESIDUAL, [3, 2, 2, 3], 2),
        ('remaining_capacity_three', ANCHOR_A, RESIDUAL, [3, 3, 2, 2], 2),
        ('zero_target', ANCHOR_A, RESIDUAL, CAPACITIES, 0),
        ('nonexclusive_anchor', [3, 6, 10], RESIDUAL, CAPACITIES, 2),
        ('repeated_root', ANCHOR_A, [87, 80, 80], CAPACITIES, 2)]:
        reject(label, lambda A=A, R=R, cap=cap, factor=factor: check_premises(geo, A, ANCHOR_B, R, cap, factor))
    bad = copy.deepcopy(certificate)
    bad['nine_root_coordinates']['87'][2] = 1
    reject('tampered_certificate_coordinate', lambda: same_document(bad, certificate, 'certificate'))
    bad_model = copy.deepcopy(model)
    bad_model['ordered_mask'] = 'diagonal only'
    reject('weakened_mask', lambda: derive_certificate(bad_model))
    reject('malformed_json', lambda: parse_json('{'))
    reject('duplicate_json_key', lambda: parse_json('{"capacity":2,"capacity":3}'))
    reject('nonfinite_json_value', lambda: parse_json('{"x":NaN}'))

    # Dense asymmetric factors: all coordinates nonzero, neither PSD nor d=t assumed.
    D = [[Q(s), Q(s)] for s in (2, 3, 4)] + [[Q(s), Q(2*s)] for s in (-2, -3, -4)]
    T = [[Q(8, s), Q(-4, s)] for s in (2, 3, 4)] + [[Q(-4, s), Q(4, s)] for s in (-2, -3, -4)]
    require(all(dot(D[i], T[i]) == 4 for i in range(6)), 'asymmetric anchor diagonals')
    require(all(dot(D[i], T[j+3]) == dot(D[j+3], T[i]) == 0 for i in range(3) for j in range(3) if i != j), 'both oriented asymmetric crown edges')
    require(all(rational_rank(part) == 1 for part in (D[:3], D[3:], T[:3], T[3:])), 'same-side lines')
    require(rational_rank([D[0], D[3]]) == rational_rank([T[0], T[3]]) == 2, 'distinct side lines')
    passed.append('asymmetric_dense_rank_two_crown')

    # The full rank-three counterexample to the forced-collinearity step (P4).
    E = [[2 * int(i == j) for j in range(3)] for i in range(3)]
    U, V = E, E
    require(all(dot(x, x) == 4 for x in U + V), 'rank-three crown six diagonals')
    require(all(dot(U[i], V[j]) == dot(V[j], U[i]) == 0 for i in range(3) for j in range(3) if i != j), 'rank-three crown both oriented edges')
    escape = [0, 1, 0]
    require(any(escape) and all(dot(escape, x) == dot(x, escape) == 0 for x in (U[0], V[0])), 'nonzero rank-three escape vector')
    require(rational_rank(U) == rational_rank(V) == 3, 'rank-three sides do not collapse')
    passed.append('rank_three_crown_with_nonzero_escape')
    require([[dot(x, y) for y in E] for x in E] == certificate['residual_target'], 'three remaining terms realize 4I3')
    passed.append('three_terms_realize_residual_target')
    return passed


def evaluate(model, supplied):
    certificate, geo = derive_certificate(model)
    same_document(supplied, certificate, 'CERTIFICATE.json')
    checked = controls(model, certificate, geo)
    return dict(status='PASS_P112_COSTAR_CROWN_PREMISES', schema_version=1,
                model_sha256=MODEL_SHA256, certificate_sha256=digest(certificate),
                checked_ordered_equations=39, full_ordered_mask_count=6720,
                residual_rank=3, remaining_capacity=2, controls=checked,
                scope='Fixed [0,1,56,87] / [3,2,2,2] rational masked candidate only.',
                proof_status='Finite premises checked; universal impossibility is the written argument in PROOF.md, not kernel formalization.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true', help='print the deterministic checked result')
    args = parser.parse_args()
    try:
        result = evaluate(read_json(HERE/'MODEL.json'), read_json(HERE/'CERTIFICATE.json'))
        same_document(read_json(HERE/'EXPECTED.json'), result, 'EXPECTED.json')
    except (ValueError, TypeError, KeyError, IndexError) as exc:
        parser.exit(1, 'FAIL_P112_COSTAR_CROWN: ' + str(exc) + '\n')
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result['status'] + ' equations=39 controls=' + str(len(result['controls'])) + ' written_proof=PROOF.md no_kappa')


if __name__ == '__main__':
    main()
