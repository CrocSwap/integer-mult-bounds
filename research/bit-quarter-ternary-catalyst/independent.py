#!/usr/bin/env python3
"""Independent finite census for the dyadic ternary rank-one alphabet.

Adapted from Tuafo / PR1604 at c5f5bef84f6648d5573f801c283e01a333ea5f89.
Apache-2.0; substantial OpenAI assistance for Maximooch.

Uses ordered depth-first tuple enumeration, coordinate bounds, and final-frame
lookup. Does not import the primary verifier. Every repeated occurrence remains
a separate position for coefficient-subset counts. Standard library only.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
from math import comb
from pathlib import Path
import json
import platform
import time

if not __debug__:
    raise RuntimeError("Run this independent verifier without -O: its proof checks use assertions.")

ZERO = (0,) * 9
T = (4, 0, 0, 0, 4, 0, 0, 0, 4)
C = tuple(2 * v for v in T)
TOTAL = tuple(3 * v for v in T)


def alphabet():
    vectors = [v for v in product((-1, 0, 1), repeat=3) if any(v)]
    return tuple(sorted({tuple(s * x * y for x in u for y in v)
                         for s in (1, 2) for u in vectors for v in vectors}))


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def sum_frames(ids, frames):
    return tuple(sum(frames[i][j] for i in ids) for j in range(9))


def decompositions(frames, size, target):
    """All nondecreasing index tuples summing to target, repetitions allowed.

    If one selected frame f leaves size-1 entries in [-2,2], then each
    target[j]-f[j] must lie in [-2*(size-1),2*(size-1)]. This initial filter is
    necessary. Recursion uses the same bound at every node. The final frame
    is determined uniquely by the residual matrix, so a dictionary lookup
    completes each branch without any symmetry or sign-orbit reduction.
    """
    allowed = [i for i, f in enumerate(frames)
               if all(abs(target[j] - f[j]) <= 2 * (size - 1) for j in range(9))]
    lookup = {frames[i]: i for i in allowed}
    output = []
    counts = Counter()

    def descend(start, remaining, residual, chosen):
        counts['nodes'] += 1
        if remaining == 1:
            last = lookup.get(residual)
            if last is not None and last >= start:
                output.append(chosen + (last,))
            return
        bound = 2 * (remaining - 1)
        for idx in allowed:
            if idx < start:
                continue
            counts['trials'] += 1
            f = frames[idx]
            # Test diagonal coordinates first; these reject most branches.
            d0 = residual[0] - f[0]
            d4 = residual[4] - f[4]
            d8 = residual[8] - f[8]
            if abs(d0) > bound or abs(d4) > bound or abs(d8) > bound:
                continue
            next_residual = (d0, residual[1] - f[1], residual[2] - f[2],
                             residual[3] - f[3], d4, residual[5] - f[5],
                             residual[6] - f[6], residual[7] - f[7], d8)
            if any(abs(next_residual[j]) > bound for j in (1, 2, 3, 5, 6, 7)):
                continue
            descend(idx, remaining - 1, next_residual, chosen + (idx,))

    descend(0, size, target, ())
    assert output == sorted(set(output))
    assert all(sum_frames(ids, frames) == target for ids in output)
    return output, {'allowed_frames': len(allowed), **dict(counts)}


def positional_masks(ids, frames, target=T):
    """Exhaust all 2^k positional subsets by recurrence from the least bit."""
    sums = [ZERO] * (1 << len(ids))
    matches = []
    for mask in range(1, 1 << len(ids)):
        bit = mask & -mask
        pos = bit.bit_length() - 1
        sums[mask] = add(sums[mask ^ bit], frames[ids[pos]])
        if sums[mask] == target:
            matches.append(mask)
    return matches


def weighted_subsets(ids, frames, target=T):
    """Independent multiplicity count via submultisets and binomial weights."""
    counts = sorted(Counter(ids).items())
    total = 0
    matching = []
    for multiplicities in product(*(range(n + 1) for _, n in counts)):
        sub = tuple(i for (i, _), m in zip(counts, multiplicities) for _ in range(m))
        if sum_frames(sub, frames) == target:
            weight = 1
            for (_, n), m in zip(counts, multiplicities):
                weight *= comb(n, m)
            total += weight
            matching.append({'multiplicities': list(multiplicities), 'positional_weight': weight})
    return total, matching


def candidates(left, right):
    return sorted({tuple(sorted(a + b)) for a in left for b in right})


def analyze(items, frames):
    hist = Counter()
    rows = []
    for ids in items:
        assert sum_frames(ids, frames) == TOTAL
        masks = positional_masks(ids, frames)
        weighted, submultisets = weighted_subsets(ids, frames)
        assert len(masks) == weighted, (ids, masks, submultisets)
        assert masks
        hist[len(masks)] += 1
        common = (1 << len(ids)) - 1
        for mask in masks:
            common &= mask
        rows.append({'frames': list(ids), 'target_masks': masks,
                     'common_positions_mask': common,
                     'target_submultisets': submultisets})
    return {str(k): hist[k] for k in sorted(hist)}, rows


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode('utf8')


def run():
    start = time.perf_counter()
    frames = alphabet()
    assert len(frames) == 676
    # Positive fixture: each coordinate matrix occurs and has exact rank one.
    for j in (0, 4, 8):
        assert tuple(int(k == j) for k in range(9)) in frames
    lists, diagnostics = {}, {}
    for name, n, target in [('target3', 3, T), ('target4', 4, T),
                            ('complement4', 4, C), ('complement5', 5, C)]:
        lists[name], diagnostics[name] = decompositions(frames, n, target)
    seven = candidates(lists['target3'], lists['complement4'])
    eight = sorted(set(candidates(lists['target3'], lists['complement5'])) |
                   set(candidates(lists['target4'], lists['complement4'])))
    hist7, rows7 = analyze(seven, frames)
    hist8, rows8 = analyze(eight, frames)
    survivors = [row for row in rows8 if len(row['target_masks']) >= 3]
    result = {
        'schema': 'independent-dyadic-ternary-census-v1',
        'method': 'ordered tuple DFS with coordinate bounds and terminal lookup; independent positional and binomial-multiplicity subset counts',
        'frames': [list(f) for f in frames],
        'decompositions': {key: [list(x) for x in value] for key, value in lists.items()},
        'counts': {key: len(value) for key, value in lists.items()},
        'seven': {'count': len(seven), 'target_subset_census': hist7, 'candidates': rows7},
        'eight': {'count': len(eight), 'target_subset_census': hist8, 'candidates': rows8},
        'survivors': survivors,
    }
    assert result['counts'] == {'target3': 8, 'target4': 552, 'complement4': 1, 'complement5': 28}
    assert len(seven) == 8 and hist7 == {'1': 8}
    assert len(eight) == 776 and hist8 == {'1': 690, '2': 80, '4': 6}
    assert len(survivors) == 6
    result['independently_constructed_characters'] = [construct_character(tuple(r['frames']), frames) for r in survivors]
    result['self_checks'] = self_checks(frames)
    return result, {'python': platform.python_version(), 'seconds': time.perf_counter()-start,
                    'diagnostics': diagnostics, 'proof_data_sha256': sha256(canonical(result)).hexdigest()}


def dot(functional, matrix):
    return sum((a * b for a, b in zip(functional, matrix)), Fraction(0))


def solve_linear(rows, values):
    """Exact reduced row elimination; free variables are set to zero."""
    mat = [[Fraction(v) for v in row] + [Fraction(value)]
           for row, value in zip(rows, values)]
    pivots = []
    for col in range(9):
        pivot = next((r for r in range(len(pivots), len(mat)) if mat[r][col]), None)
        if pivot is None:
            continue
        row = len(pivots)
        mat[row], mat[pivot] = mat[pivot], mat[row]
        scale = mat[row][col]
        mat[row] = [v / scale for v in mat[row]]
        for r in range(len(mat)):
            if r != row and mat[r][col]:
                scale = mat[r][col]
                mat[r] = [x - scale * y for x, y in zip(mat[r], mat[row])]
        pivots.append(col)
    if any(not any(row[:9]) and row[9] for row in mat):
        return None
    solution = [Fraction(0)] * 9
    for row, col in enumerate(pivots):
        solution[col] = mat[row][9]
    assert all(dot(solution, row) == value for row, value in zip(rows, values))
    return solution


def construct_character(ids, frames):
    """Find a fresh exact character without reading a predecessor functional."""
    rows = [frames[i] for i in ids] + [T]
    for odd in range(len(ids)):
        for even in range(len(ids)):
            if odd == even:
                continue
            values = [0] * len(ids)
            values[odd], values[even] = 1, 2
            functional = solve_linear(rows, values + [1])
            if functional is not None:
                return {'frames': list(ids), 'functional': [str(v) for v in functional],
                        'frame_values': values, 'target_value': 1}
    raise AssertionError('No singleton-odd character found')


def self_checks(frames):
    # Repeated occurrences of the same matrix really are separate subsets.
    unit = (1, 0, 0, 0, 0, 0, 0, 0, 0)
    other = (0, 0, 0, 0, 1, 0, 0, 0, 0)
    i, j = frames.index(unit), frames.index(other)
    assert positional_masks((i, i, j), frames, unit) == [1, 2]
    assert weighted_subsets((i, i, j), frames, unit)[0] == 2
    assert decompositions(frames, 1, unit)[0] == [(i,)]
    impossible = tuple(5 * v for v in unit)
    assert decompositions(frames, 2, impossible)[0] == []
    assert solve_linear([ZERO], [1]) is None
    return ['duplicate positional multiplicity', 'one-frame positive fixture',
            'coordinate-bound impossible fixture', 'inconsistent exact linear system']


def validate_certificate_data(result, other):
    assert other['schema_version'] == 1
    assert other['frame_denominator'] == 4
    assert other['target_scaled'] == list(T)
    assert other['alphabet'] == result['frames']
    mappings = {'target3': 'decompositions_three', 'target4': 'decompositions_four',
                'complement5': 'complements_five'}
    for ours, theirs in mappings.items():
        assert sorted(result['decompositions'][ours]) == sorted(other[theirs]), theirs
    for number in ('seven', 'eight'):
        assert sorted(r['frames'] for r in result[number]['candidates']) == sorted(other['candidates_' + number])
        assert result[number]['target_subset_census'] == other['subset_census_' + number]
    survivors = sorted(r['frames'] for r in result['survivors'])
    assert survivors == sorted(other['rank_survivors_eight'])
    characters = other['character_obstructions']
    assert sorted(c['frames'] for c in characters) == survivors
    frames = result['frames']
    for character in characters:
        functional = [Fraction(v) for v in character['functional']]
        assert len(functional) == 9
        actual = [dot(functional, frames[i]) for i in character['frames']]
        assert all(v.denominator == 1 for v in actual)
        assert actual == character['frame_values']
        assert sum(int(v) % 2 for v in actual) == 1
        assert dot(functional, T) == character['target_value'] == 1
    # Each role is an independent diagonal action. Its exponents must sum to T.
    witness = other['nine_call_witness']
    assert len(witness) == 9
    assert all(isinstance(w['frame_id'], int) and 0 <= w['frame_id'] < len(frames)
               and w['role'] in (0, 1, 2) for w in witness)
    for role in range(3):
        assert sum_frames([w['frame_id'] for w in witness if w['role'] == role], frames) == T


def compare_certificate(result, filename):
    payload = Path(filename).read_bytes()
    other = json.loads(payload)
    validate_certificate_data(result, other)
    rejected = []
    for mutation in ('missing_decomposition', 'zero_character'):
        corrupt = json.loads(payload)
        if mutation == 'missing_decomposition':
            corrupt['decompositions_four'].pop()
        else:
            corrupt['character_obstructions'][0]['functional'] = ['0'] * 9
        try:
            validate_certificate_data(result, corrupt)
        except AssertionError:
            rejected.append(mutation)
        else:
            raise AssertionError('Corrupt certificate accepted: ' + mutation)
    return {'file': str(filename), 'sha256': sha256(payload).hexdigest(),
            'status': 'all census lists, exact parity characters, and nine-call witness agree',
            'rejected_controls': rejected}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--certificate', type=Path, default=Path(__file__).with_name('CERTIFICATE.json'))
    args = parser.parse_args()
    result, receipt = run()
    receipt['certificate_comparison'] = compare_certificate(result, args.certificate)
    if args.output:
        args.output.write_text(json.dumps({'proof_data': result, 'receipt': receipt}, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'counts': result['counts'], 'seven': result['seven']['target_subset_census'],
                      'eight': result['eight']['target_subset_census'], 'survivors': len(result['survivors']),
                      **receipt}, indent=2))


if __name__ == '__main__':
    main()
