#!/usr/bin/env python3
"""Additional full-basis checks using integer arithmetic only."""
import argparse
import json
from pathlib import Path
import time
import numpy as np
from leech_geometry import require
from center_supports import binary_rank
from norm6_centers import coefficient_matrix, inverse_mod


def integer_full_rank(matrix, prime=251, block_size=64):
    work = (matrix % prime).astype(np.int64)
    require(work.shape[0] == work.shape[1], 'Square basis matrix required')
    rank = 0
    for offset in range(0, len(matrix), block_size):
        size = min(block_size, len(work))
        panel = work[:, :size].copy()
        permutation = np.arange(len(panel))
        for col in range(size):
            choices = np.flatnonzero(panel[col:, col])
            require(len(choices) > 0, f'Integer modular basis rank failure at{offset + col}')
            row = col + int(choices[0])
            panel[[col, row]] = panel[[row, col]]
            permutation[[col, row]] = permutation[[row, col]]
            panel[col] = (panel[col] * pow(int(panel[col, col]), -1, prime)) % prime
            panel[col + 1:] = (panel[col + 1:] - panel[col + 1:, col:col + 1] * panel[col]) % prime
        work = work[permutation]
        inverse = inverse_mod(work[:size, :size], prime)
        c = (work[size:, :size] @ inverse) % prime
        work = (work[size:, size:] - c @ work[:size, size:]) % prime
        rank += size
        if rank % 512 == 0 or rank == len(matrix):
            print(json.dumps({'integer_verified_rank': rank}), flush=True)
    return rank


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    path = parser.parse_args().output
    report = json.loads((path / 'NORM6-CENTERS.json').read_text())
    basis = np.load(path / 'norm6_basis_directions.npy').astype(np.int16)
    lines = np.load(path / 'minimal_lines.npy').astype(np.int16)
    labels = np.load(path / 'binary_labels_packed.npy')
    rng = np.random.default_rng(246000025)
    probe_indices = np.sort(rng.choice(len(lines), 512, replace=False))
    probes = lines[probe_indices]
    dots = basis @ probes.T
    require(not (dots % 8).any(), 'Nonintegral basis/probe pairings')
    t = dots // 8
    require(np.all(abs(t) <= 3), 'Probe pairing bound')
    support_witnesses = []
    for index in range(len(basis)):
        subset = probe_indices[np.flatnonzero(t[index] % 2)]
        rank, chosen = binary_rank(labels[subset])
        require(rank == 24, f'Encoder support basis{index} has rank{rank} on probes')
        support_witnesses.append(subset[chosen].tolist())
    require(np.all((basis.astype(np.int32) ** 2).sum(axis=1) == 48), 'All basis centers norm6')
    start = time.monotonic()
    matrix, monomials = coefficient_matrix(basis)
    rank = integer_full_rank(matrix)
    result = {
        'basis_count': len(basis),
        'all_encoder_support_ranks': 24,
        'witnesses': support_witnesses,
        'integer_coefficient_rank_mod251': rank,
        'arithmetic': 'Signed64-bit integer arrays only; each block dot product has at most64 terms with residue operands0..250, so its magnitude is at most4,000,000. No overflow or floating-point arithmetic.',
    }
    (path / 'NORM6-BASIS-VERIFICATION.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'witnesses'}, indent=2))


if __name__ == '__main__':
    main()
