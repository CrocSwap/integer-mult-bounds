#!/usr/bin/env python3
"""Norm-six Leech cubic centers, with exact mod-prime span certificates."""
from pathlib import Path
from itertools import combinations_with_replacement
import argparse
import json
import time
import numpy as np
from leech_geometry import require
from center_supports import binary_rank


def centers(vectors, count):
    rng = np.random.default_rng(6242600)
    answers, pairs = [], []
    seen = set()
    while len(answers) < count:
        i, j = map(int, rng.integers(0, len(vectors), size=2))
        x, y = vectors[i], vectors[j]
        sign = 1 if int(x @ y) == -8 else -1 if int(x @ y) == 8 else 0
        if not sign:
            continue
        a = x + sign * y
        if a[np.flatnonzero(a)[0]] < 0:
            a = -a
        key = tuple(map(int, a))
        if key in seen:
            continue
        seen.add(key)
        answers.append(a)
        pairs.append((i, j, sign))
    return np.array(answers, dtype=np.int16), pairs


def coefficient_matrix(directions):
    """Raw polynomial: (a.v)^3 - 8(a.v)(v.v), equals512K on norm32 v."""
    monomials = list(combinations_with_replacement(range(24), 3))
    result = np.empty((len(directions), len(monomials)), dtype=np.int32)
    a = directions.astype(np.int32)
    for col, (i, j, k) in enumerate(monomials):
        if i == k:
            result[:, col] = a[:, i] ** 3 - 8 * a[:, i]
        elif i == j:
            result[:, col] = 3 * a[:, i] ** 2 * a[:, k] - 8 * a[:, k]
        elif j == k:
            result[:, col] = 3 * a[:, j] ** 2 * a[:, i] - 8 * a[:, i]
        else:
            result[:, col] = 6 * a[:, i] * a[:, j] * a[:, k]
    return result, monomials


def inverse_mod(matrix, prime):
    n = len(matrix)
    work = np.concatenate((matrix.astype(np.int64), np.eye(n, dtype=np.int64)), axis=1)
    for col in range(n):
        choices = np.flatnonzero(work[col:, col])
        require(len(choices) > 0, 'Singular modular block')
        row = col + int(choices[0])
        work[[col, row]] = work[[row, col]]
        work[col] = (work[col] * pow(int(work[col, col]), -1, prime)) % prime
        factors = work[:, col].copy()
        factors[col] = 0
        work = (work - factors[:, None] * work[col]) % prime
    require(np.array_equal(work[:, :n], np.eye(n, dtype=np.int64)), 'Modular inverse failure')
    return work[:, n:]


def full_column_rank_mod(matrix, prime=251, block_size=64):
    """Exact integer block Schur elimination modulo251.

    Every block product has at most64 terms bounded by250**2.
    """
    original_rows, columns = matrix.shape
    require(original_rows >= columns, 'Need at least as many rows as columns')
    require(prime == 251 and 1 <= block_size <= 64, 'Verified exact arithmetic bounds')
    work = (matrix % prime).astype(np.int64)
    row_ids = np.arange(original_rows)
    selected = []
    blocks = []
    offset = 0
    while work.shape[1]:
        size = min(block_size, work.shape[1])
        panel = work[:, :size].astype(np.int64)
        permutation = np.arange(len(panel))
        for col in range(size):
            choices = np.flatnonzero(panel[col:, col])
            require(len(choices) > 0, f'Modular rank deficient at column {offset + col}')
            row = col + int(choices[0])
            panel[[col, row]] = panel[[row, col]]
            permutation[[col, row]] = permutation[[row, col]]
            panel[col] = (panel[col] * pow(int(panel[col, col]), -1, prime)) % prime
            factors = panel[col + 1:, col].copy()
            panel[col + 1:] = (panel[col + 1:] - factors[:, None] * panel[col]) % prime
        work = work[permutation]
        row_ids = row_ids[permutation]
        b = work[:size, :size].astype(np.int64)
        inv = inverse_mod(b, prime).astype(np.int64)
        selected.extend(map(int, row_ids[:size]))
        blocks.append({'offset': offset, 'size': size, 'source_rows': row_ids[:size].tolist()})
        if work.shape[1] > size:
            c = (work[size:, :size] @ inv) % prime
            work = (work[size:, size:] - c @ work[:size, size:]) % prime
        else:
            work = np.empty((work.shape[0] - size, 0), dtype=np.int64)
        row_ids = row_ids[size:]
        offset += size
        if offset % 512 == 0 or offset == columns:
            print(json.dumps({'modular_rank_so_far': offset}), flush=True)
    require(len(selected) == columns, 'Wrong basis size')
    return selected, blocks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--count', type=int, default=2700)
    parser.add_argument('--rank', action='store_true')
    args = parser.parse_args()
    path = args.output
    vectors = np.load(path / 'minimal_lines.npy').astype(np.int16)
    packed = np.load(path / 'binary_labels_packed.npy')
    directions, pairs = centers(vectors, args.count)
    require(np.all((directions.astype(np.int32) ** 2).sum(axis=1) == 48), 'Norm-six direction')
    support_reports = []
    for index in range(min(20, len(directions))):
        a = directions[index]
        dots = vectors @ a
        require(not (dots % 8).any(), 'Nonintegral norm-six pairing')
        require(np.all(np.abs(dots) <= 24), 'Norm-six minimal-shell bound')
        t = dots // 8
        support = np.flatnonzero(t * (t * t - 4) != 0)
        require(np.array_equal(support, np.flatnonzero(t % 2)), 'Cubic support is not exactly odd-pairing set')
        rank, chosen = binary_rank(packed[support])
        i, j, sign = pairs[index]
        annihilator = int(packed[i]) ^ int(packed[j]) ^ ((1 << 25) - 1)
        require(annihilator != 0, 'Zero support annihilator')
        require(all((int(p) & annihilator).bit_count() % 2 == 0 for p in packed[support]), 'Support annihilator failure')
        require(rank == 24, f'Norm-six cubic support rank{rank}, expected24')
        values, counts = np.unique(t, return_counts=True)
        support_reports.append({'index': index, 'minimal_line_pair': list(pairs[index]),
                                'direction': a.tolist(), 'support_count': len(support),
                                'support_rank': rank, 'annihilator_packed': annihilator,
                                'witness_line_indices': support[chosen].tolist(),
                                'dot_distribution': dict(zip(map(str, values), map(int, counts)))})
    np.save(path / 'norm6_directions.npy', directions)
    report = {'direction_count': len(directions), 'raw_norm_squared': 48,
              'sample_supports': support_reports,
              'support_proof': 'For a=x±y, p(a)=p(x)+p(y) has pairing a.v/8 with p(v). On the norm-six/minimal-shell pair, integral t has |t|<=3. Thus K(t)=t(t²−4) is nonzero exactly when t is odd. All odd-norm p(v) in that support are perpendicular to nonzero p(x)+p(y)+allones, so their span has dimension at most24.'}
    if args.rank:
        start = time.monotonic()
        matrix, monomials = coefficient_matrix(directions)
        selected, blocks = full_column_rank_mod(matrix)
        report['coefficient_rank_mod251'] = len(selected)
        report['basis_direction_indices'] = selected
        report['modular_elimination_blocks'] = blocks
        np.save(path / 'norm6_basis_directions.npy', directions[selected])
        # Independently spot-check the homogeneous coefficient convention.
        for center_index, vector_index in [(0, 0), (19, 49128), (100, 12345)]:
            a, v = directions[center_index].astype(np.int64), vectors[vector_index].astype(np.int64)
            evaluation = sum(int(matrix[center_index, col]) * int(v[i] * v[j] * v[k])
                             for col, (i, j, k) in enumerate(monomials))
            dot = int(a @ v)
            require(evaluation == dot ** 3 - 256 * dot, 'Homogeneous coefficient formula mismatch')
    (path / 'NORM6-CENTERS.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('sample_supports', 'basis_direction_indices', 'modular_elimination_blocks')}, indent=2))


if __name__ == '__main__':
    main()
