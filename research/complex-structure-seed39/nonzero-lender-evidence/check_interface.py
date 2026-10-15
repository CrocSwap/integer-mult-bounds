#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared for Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Independent finite interface checks. No builder/replay/operator imports.

Checks exact target transport, frame-rank obstructions and an illustrative
paid rank-one entrance round trip. This does not construct a helper644 alias.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'anticipatory-stage-evidence/vendor/pr2339'
SOURCE_PINS = {'inputs/blocks.json': 'ddfac1dae1fe7cc0a91e7c7205c6d9d0c07c682880aa34eed83bf4ad7384da9f', 'inputs/extra.canonical.json.gz': 'd7e48dcbafa236a2e1e41f7958244211506f7c7630fe6a2d43d2bdf17b7ae015', 'inputs/gauge44.canonical.json.gz': '65c6d17ffee2eacf27bff438f37fc549c9ed0c909cbc7a52976cc75cf2d15b91', 'witness/witness_80_base.json': '9380f74c032b0616d5b13e8ef94b6d9f80cac36239e329357e7d5fcab5283ad0', 'witness/witness_80_extra.json': '6737072dcca47c6e6526bd62a41585dd09026549550c9e62eb53e64b265a6709', 'words/BORROW-WORD-80base.json.gz': '61290abffd8c8225e0abb3958c1506674e256de688fc4cdf358bbe7c981df493', 'words/BORROW-WORD-80extra.json.gz': '1dd2d6f2ae5b5a27b5f89fb830203f0cca7a78d0323a7845e85e1e80f8f6d1a5'}
H = 9
N = 1 << H

def require(ok, message):
    if not ok:
        raise ValueError(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def span(basis):
    out = {0}
    for a in basis:
        out |= {a ^ b for b in tuple(out)}
    return out

def linear(columns, value):
    answer = 0
    while value:
        bit = value & -value
        answer ^= columns[bit.bit_length() - 1]
        value ^= bit
    return answer

def permutations(columns):
    fwd = [linear(columns, x) for x in range(N)]
    require(len(set(fwd)) == N, 'singular binary map')
    inv = [0] * N
    for x, y in enumerate(fwd):
        inv[y] = x
    return fwd, inv

def phase_recipe(columns):
    """Literal quadratic phase definition of K_G; all arithmetic integral."""
    forward, reverse = permutations(columns)
    gi = [reverse[1 << j] for j in range(H)]
    git = [sum(((gi[j] >> i) & 1) << j for j in range(H)) for i in range(H)]
    matrix = [(1 << j) ^ linear(git, gi[j]) for j in range(H)]
    require(all((matrix[j] >> i & 1) == (matrix[i] >> j & 1)
                for i in range(H) for j in range(H)), 'quadratic matrix symmetry')
    phases = []
    for y in forward:
        diagonal = sum((matrix[i] >> i & 1) for i in range(H) if y >> i & 1)
        cross = sum((matrix[j] >> i & 1) for i in range(H) for j in range(i + 1, H)
                    if y >> i & 1 and y >> j & 1)
        phases.append((diagonal + 2 * cross) % 4)
    return forward, reverse, phases

def rotate(z, p):
    r, i = z
    return ((r, i), (-i, r), (-r, -i), (i, -r))[p % 4]

def mono(state, recipe, sign):
    values, exponent = state
    forward, reverse, phase = recipe
    result = {}
    for x, z in values.items():
        y = forward[x] if sign == 1 else reverse[x]
        result[y] = rotate(z, phase[x] if sign == 1 else -phase[y])
    return result, exponent

def coordinate_one(state, sign):
    values, exponent = state
    out = {}
    for x, (r, i) in values.items():
        for y, z in ((x, (r - sign * i, i + sign * r)),
                     (x ^ 1, (r + sign * i, i - sign * r))):
            a, b = out.get(y, (0, 0))
            out[y] = (a + z[0], b + z[1])
    return {x: z for x, z in out.items() if z != (0, 0)}, exponent + 1

def one_frame_recipe(vector):
    columns = [vector]
    for j in range(H):
        if (1 << j) not in span(columns):
            columns.append(1 << j)
    require(len(columns) == H, 'frame extension')
    return phase_recipe(columns)

def frame_one(state, recipe, sign):
    return mono(coordinate_one(mono(state, recipe, -1), sign), recipe, 1)

def equal(a, b):
    av, ae = a
    bv, be = b
    return all(tuple(t << be for t in av.get(k, (0, 0))) ==
               tuple(t << ae for t in bv.get(k, (0, 0))) for k in av.keys() | bv.keys())

def lagrangian(frame):
    u = span(frame)
    perpendicular = [z for z in range(N) if all((z & a).bit_count() % 2 == 0 for a in frame)]
    return {x | ((x ^ z) << H) for x in u for z in perpendicular}

def symplectic_map(columns, value):
    forward, reverse = permutations(columns)
    inverse_cols = [reverse[1 << j] for j in range(H)]
    inverse_transpose = [sum(((inverse_cols[j] >> i) & 1) << j for j in range(H))
                         for i in range(H)]
    x, z = value & (N - 1), value >> H
    gx = forward[x]
    return gx | ((gx ^ linear(inverse_transpose, x ^ z)) << H)

def add_row(dst, src, q):
    for k, v in list(src.items()):
        value = dst.get(k, Q(0)) + q * v
        if value:
            dst[k] = value
        else:
            dst.pop(k, None)

def target_gate(rows, gate, v):
    if gate[0] == 'scale' and v <= gate[1] < 2 * v:
        q = Q(gate[2], gate[3])
        rows[gate[1] - v] = {k: q * x for k, x in rows[gate[1] - v].items()}
    elif gate[0] == 'add' and v <= gate[2] < 2 * v:
        require(v <= gate[1] < 2 * v, 'a non-target reads a target')
        add_row(rows[gate[1] - v], rows[gate[2] - v], Q(gate[3], gate[4]))

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=HERE / 'INTERFACE-CHECK.json')
    args = ap.parse_args()
    results = {}
    first_g = None
    pins = {}
    for name in ('base', 'extra'):
        path = SOURCE / 'words' / ('BORROW-WORD-80' + name + '.json.gz')
        pins[str(path.relative_to(SOURCE))] = sha(path)
        require(pins[str(path.relative_to(SOURCE))] == SOURCE_PINS[str(path.relative_to(SOURCE))], 'immutable source pin')
        word = json.loads(gzip.decompress(path.read_bytes()))
        v = word['report']['v']
        require(v == 112 and word['report']['h'] == H, 'geometry')
        rows = [{i: Q(1)} for i in range(v)]
        counts = {}
        pre_matrix = None
        for section in ('precondition', 'compensation', 'A', 'cut', 'B', 'restore', 'cleanup'):
            gates = word[section]
            counts[section] = {
                'target_adds': sum(e[0] == 'add' and v <= e[1] < 2 * v and v <= e[2] < 2 * v for e in gates),
                'target_scales': sum(e[0] == 'scale' and v <= e[1] < 2 * v for e in gates),
            }
            for e in gates:
                target_gate(rows, e, v)
            if section == 'precondition':
                pre_matrix = [dict(r) for r in rows]
        require(rows == [{i: Q(1)} for i in range(v)], 'complete target matrix is not identity')
        require(pre_matrix != rows, 'precondition is unexpectedly trivial')
        # Moving a correction through precondition requires its actual matrix.
        transformed = [sum(row.values(), Q(0)) for row in pre_matrix]
        naive = [Q(1)] * v
        require(transformed != naive, 'missing-target-transport control failed')
        for e in word['cut']:
            require(e[0] == 'add' and v <= e[1] < 2 * v and not v <= e[2] < 2 * v,
                    'COPY target/source separation')
        targets = [[x for x in range(1, N) if (x & p).bit_count() % 2 == 0]
                   for p in word['ports']]
        target_lag = [lagrangian(t) for t in targets]
        full = lagrangian([1 << i for i in range(H)])
        zero = lagrangian([])
        rank_hist = Counter()
        for _, lender, g, u, e in word['warps']:
            if first_g is None and g != [1 << i for i in range(H)]:
                first_g = g
            # Form the map only once per operator; no original checker is imported.
            images = [symplectic_map(g, 1 << i) for i in range(2 * H)]
            move = lambda x: linear(images, x)
            require({move(x) for x in zero} == zero, 'zero-frame monomial condition')
            require({move(x) for x in full} == full, 'FULL-frame monomial condition')
            require({move(x) for x in lagrangian(u)} == lagrangian(e), 'actual handoff frame map')
            image_full = {move(x) for x in full}
            for target in target_lag:
                intersection = len(image_full & target)
                require(intersection > 0 and intersection & (intersection - 1) == 0, 'binary intersection')
                rank_hist[H - (intersection.bit_length() - 1)] += 1
        require(rank_hist == {1: 80 * 112}, 'late FULL-to-target rank obstruction')
        results[name] = dict(target_columns=v, target_matrix_identity=True, target_gate_counts=counts,
                             missing_target_transport_rejected=True, cut_target_writes_commute=True,
                             actual_warps_checked=len(word['warps']), full_to_target_rank_histogram=dict(rank_hist))
    # Interface-only illustration. Helper644 has entrance [30]; this is NOT a viable lender nomination.
    require(first_g is not None, 'no nontrivial source operator')
    source_frame = one_frame_recipe(30)
    warp = phase_recipe(first_g)
    omitted_descent = omitted_inverse_warp = wrong_correction_sign = 0
    for column in range(N):
        unit = ({column: (1, 0)}, 0)
        initial = frame_one(unit, source_frame, 1)
        lowered = frame_one(initial, source_frame, -1)
        require(equal(lowered, unit), 'exact lowering to zero frame')
        twisted = mono(lowered, warp, 1)
        expected_correction = mono(unit, warp, 1)
        require(equal(twisted, expected_correction), 'target reads wrong transformed input')
        restored = frame_one(mono(twisted, warp, -1), source_frame, 1)
        require(equal(restored, initial), 'source physical input not restored')
        omitted_descent += not equal(mono(initial, warp, 1), expected_correction)
        omitted_inverse_warp += not equal(frame_one(twisted, source_frame, 1), initial)
        negated = ({x: (-r, -i) for x, (r, i) in twisted[0].items()}, twisted[1])
        wrong_correction_sign += not equal(negated, expected_correction)
    require(omitted_descent == N and omitted_inverse_warp > 0 and wrong_correction_sign == N,
            'paid prelude mutation controls')
    out = dict(status='PASS_INDEPENDENT_INTERFACE_CONDITIONS_NO_CANDIDATE_NO_NEW_KAPPA',
               immutable_head='bf1742aee4d855efb8bbd44a8419eddb33a679e5', source_sha256=pins,
               variants=results, paid_prelude_illustration=dict(source_frame=[30], G_columns=first_g,
               all_exact_columns=N, paid_recursive_profile={'1': 2}, private_buffers=0,
               source_restored=True, omitted_descent_failed_columns=omitted_descent,
               omitted_inverse_warp_failed_columns=omitted_inverse_warp,
               wrong_correction_sign_failed_columns=wrong_correction_sign),
               scope='Finite exact interface arithmetic only. No viable helper644 lender, emitted native program, recursive labels, owner hosting, outer release or new kappa is certified.')
    args.out.write_text(json.dumps(out, indent=2) + '\n')
    print(out['status'])

if __name__ == '__main__':
    main()
