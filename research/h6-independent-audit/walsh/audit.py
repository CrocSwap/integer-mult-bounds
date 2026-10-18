#!/usr/bin/env python3
"""Independent exact audit of the frozen H6 Walsh proposal.

Every matrix entry is checked; no floating-point rank or sampled identity
is used. Run from any directory with Python >= 3.11 and NumPy.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import platform
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "niemeier-lattices" / "code"))
# Only geometry is imported. All field arithmetic and identity checks below
# are independent of the proposed walsh.py and its predecessor label code.
import e8_cubed


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def binary_inverse(matrix):
    size = len(matrix)
    work = np.concatenate((matrix.copy() & 1, np.eye(size, dtype=np.uint8)), axis=1)
    for col in range(size):
        choices = np.flatnonzero(work[col:, col])
        require(len(choices), "singular binary matrix")
        pivot = col + int(choices[0])
        work[[col, pivot]] = work[[pivot, col]]
        for row in range(size):
            if row != col and work[row, col]:
                work[row] ^= work[col]
    require(np.array_equal(work[:, :size], np.eye(size, dtype=np.uint8)), "binary elimination")
    return work[:, size:]


def binary_rank_witnesses(rows):
    basis, witnesses = {}, []
    for index, row in enumerate(rows):
        word = sum(int(value & 1) << col for col, value in enumerate(row))
        while word:
            pivot = word.bit_length() - 1
            if pivot in basis:
                word ^= basis[pivot]
            else:
                basis[pivot] = word
                witnesses.append(index)
                break
    return witnesses


def rational_inverse_and_determinant(matrix):
    size = len(matrix)
    work = [[Fraction(int(matrix[row, col])) for col in range(size)]
            + [Fraction(row == col) for col in range(size)] for row in range(size)]
    determinant = Fraction(1)
    for col in range(size):
        pivot = next(row for row in range(col, size) if work[row][col])
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            determinant *= -1
        divisor = work[col][col]
        determinant *= divisor
        work[col] = [value / divisor for value in work[col]]
        for row in range(size):
            if row != col:
                coefficient = work[row][col]
                work[row] = [left - coefficient * right
                             for left, right in zip(work[row], work[col])]
    require(determinant.denominator == 1, "integral Gram determinant")
    inverse = [[value for value in row[size:]] for row in work]
    require(all(value.denominator == 1 for row in inverse for value in row),
            "unimodular Gram inverse")
    return np.array([[int(value) for value in row] for row in inverse], dtype=np.int64), int(determinant)


def pack(rows):
    return rows.astype(np.uint32) @ (1 << np.arange(rows.shape[1], dtype=np.uint32))


def source_hash(relative):
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunk-rows", type=int, default=256)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    require(args.chunk_rows > 0, "positive chunk size")
    started = time.monotonic()
    roots, fourth, ports, profiles = e8_cubed.construct_shell()
    roots = roots.astype(np.int64)
    P = ports[(profiles & 4) == 0, :16].astype(np.int64)
    N = len(P)
    require(N == 30960 and np.all(np.sum(P * P, axis=1) == 16), "selected norm-four shell")
    require(len({row.tobytes() for row in P}) == N, "distinct oriented ports")
    require(np.all(P[np.arange(N), np.argmax(P != 0, axis=1)] > 0), "antipodal orientation")

    root_raw = roots @ roots.T
    require(np.all(root_raw % 4 == 0), "integer root pairings")
    root_gram = root_raw // 4
    root_basis_indices = binary_rank_witnesses(root_gram & 1)
    require(len(root_basis_indices) == 8, "root parity rank eight")
    Q = roots[root_basis_indices]
    G = root_gram[np.ix_(root_basis_indices, root_basis_indices)]
    G_inverse, determinant = rational_inverse_and_determinant(G)
    require(determinant == 1, "root Gram determinant one")
    require(np.array_equal(G @ G_inverse, np.eye(8, dtype=np.int64)), "exact Gram inverse")
    M = np.zeros((16, 16), dtype=np.uint8)
    labels = np.zeros((N, 16), dtype=np.uint8)
    for block in range(2):
        raw_pairings = P[:, 8 * block:8 * (block + 1)] @ Q.T
        require(np.all(raw_pairings % 4 == 0), "integer shell-basis pairings")
        labels[:, 8 * block:8 * (block + 1)] = (raw_pairings // 4) & 1
        M[8 * block:8 * (block + 1), 8 * block:8 * (block + 1)] = G_inverse & 1
    require(np.array_equal(M, M.T) and not np.diag(M).any(), "alternating form")
    require(len(binary_rank_witnesses(M)) == 16, "nondegenerate form")
    label_witnesses = binary_rank_witnesses(labels)
    require(len(label_witnesses) == 16, "full label span")
    packed = pack(labels)
    twisted = pack((labels @ M) & 1)
    multiplicity = Counter(packed.tolist())
    require(len(multiplicity) == 14670, "label count")
    require(Counter(multiplicity.values()) == Counter({2: 14400, 8: 270}), "label multiplicities")

    # The exact principal minor and coordinate convention used by the frozen
    # proposal are also recovered, with its seed and trial numbering.
    rng = np.random.default_rng(3)
    seed_indices = rng.choice(N, 16, replace=False)
    seed_gram = ((P[seed_indices] @ P[seed_indices].T) // 4) & 1
    seed_inverse = binary_inverse(seed_gram.astype(np.uint8))
    seed_labels = (((P @ P[seed_indices].T) // 4) & 1).astype(np.uint8)
    seed_packed = pack(seed_labels)
    seed_twisted = pack((seed_labels @ seed_inverse) & 1)
    require(Counter(Counter(seed_packed.tolist()).values()) == Counter({2: 14400, 8: 270}),
            "proposal coordinate multiplicities")

    parity = np.array([value.bit_count() & 1 for value in range(65536)], dtype=np.uint8)
    histogram = np.zeros(9, dtype=np.int64)
    degree_min, degree_max = N, 0
    observed = set()
    checked = 0
    for start in range(0, N, args.chunk_rows):
        stop = min(start + args.chunk_rows, N)
        raw = P[start:stop] @ P.T
        require(np.all(raw % 4 == 0), f"integer pairings rows {start}:{stop}")
        t = (raw // 4).astype(np.int16)
        require(np.all((t >= -3) & (t <= 4)), "attainable dot-product range")
        require(np.count_nonzero(t == 4) == stop - start, "t=4 only on diagonal")
        require(np.all(t[np.arange(stop - start), np.arange(start, stop)] == 4), "diagonal t=4")
        B = (t & 1).astype(np.uint8)
        predicted = parity[np.bitwise_and(twisted[start:stop, None], packed[None, :])]
        require(np.array_equal(B, predicted), f"universal-basis parity rows {start}:{stop}")
        proposed = parity[np.bitwise_and(seed_twisted[start:stop, None], seed_packed[None, :])]
        require(np.array_equal(B, proposed), f"frozen-proposal parity rows {start}:{stop}")

        # 48(I-K) = 48 delta - (t^3 - 4t), all int16 intermediates
        # are bounded by 108. This includes every diagonal entry.
        left = 4 * t - t ** 3
        left[np.arange(stop - start), np.arange(start, stop)] += 48
        right = 3 * t * B - 24 * np.sign(t) * (np.abs(t) == 3)
        require(np.array_equal(left, right), f"scaled compensation identity rows {start}:{stop}")
        require(np.array_equal(left != 0, B != 0), "support is exactly odd pairings")
        degree = B.sum(axis=1)
        degree_min = min(degree_min, int(degree.min()))
        degree_max = max(degree_max, int(degree.max()))
        histogram += np.bincount((t + 4).ravel(), minlength=9)
        observed.update(np.unique(t).tolist())
        checked += t.size
        if start == 0 or stop == N or (start // args.chunk_rows) % 20 == 0:
            print(f"checked {checked}/{N*N} ordered pairs", file=sys.stderr, flush=True)
    require(checked == N * N, "all ordered pairs checked")
    require(observed == set(range(-3, 5)), "all and only asserted attainable pairings")
    expected_histogram = {-3: 568960, -2: 37564800, -1: 200240000, 0: 365458320,
                          1: 276734080, 2: 75129600, 3: 2794880, 4: 30960}
    actual_histogram = {value - 4: int(count) for value, count in enumerate(histogram) if count}
    require(actual_histogram == expected_histogram, "exact complete histogram")
    nnz = sum(count for t, count in actual_histogram.items() if t & 1)
    exceptional = actual_histogram[-3] + actual_histogram[3]
    require(nnz == 480337920 and exceptional == 3363840, "support and exceptional counts")
    require((degree_min, degree_max) == (15488, 15872), "row-degree endpoints")

    # All 2^16 characters have sum zero except the zero character. This is
    # the orthogonality identity for the full symplectic Walsh matrix, with
    # no 65536-square matrix allocation.
    all_words = np.arange(65536, dtype=np.uint32)
    full_labels = ((all_words[:, None] >> np.arange(16)) & 1).astype(np.uint8)
    require(len(np.unique(pack((full_labels @ M) & 1))) == 65536,
            "full label-space bijection under the alternating form")
    transform = np.ones(65536, dtype=np.int64)
    for bit in range(16):
        blocks = transform.reshape(-1, 2, 1 << bit)
        left, right = blocks[:, 0].copy(), blocks[:, 1].copy()
        blocks[:, 0] = left + right
        blocks[:, 1] = left - right
    # The transform evaluates all 65536 binary character sums. For a
    # nonzero difference choosing a set bit also gives a direct proof:
    # pairing x and x+e_bit cancels each summand.
    require(np.count_nonzero(transform) == 1 and transform[0] == 65536,
            "full binary character transform normalization")

    scalar_identity = []
    negative_maxima = {"omit_exception": 0, "reverse_exception_sign": 0,
                       "use_raw_dot_instead_of_t": 0}
    for t in sorted(observed):
        diagonal = int(t == 4)
        left = 48 * diagonal + 4 * t - t ** 3
        odd, scalar_exceptional = t & 1, int(abs(t) == 3)
        sign = (t > 0) - (t < 0)
        right = 3 * t * odd - 24 * sign * scalar_exceptional
        require(left == right, "every attainable scalar pairing")
        scalar_identity.append({"t": t, "scaled_48_I_minus_K": left})
        variants = {"omit_exception": 3 * t * odd,
                    "reverse_exception_sign": 3 * t * odd + 24 * sign * scalar_exceptional,
                    "use_raw_dot_instead_of_t": 12 * t * odd - 24 * sign * scalar_exceptional}
        for name, alternative in variants.items():
            negative_maxima[name] = max(negative_maxima[name], abs(left - alternative))
    require(negative_maxima == {"omit_exception": 24, "reverse_exception_sign": 48,
                                "use_raw_dot_instead_of_t": 27}, "defect-sensitive controls")

    root_labels = (((roots @ Q.T) // 4) & 1).astype(np.uint8)
    norm4_raw = fourth.astype(np.int64) @ Q.T
    require(np.all(norm4_raw % 4 == 0), "norm-four basis pairings")
    norm4_labels = ((norm4_raw // 4) & 1).astype(np.uint8)
    require(len(set(pack(root_labels).tolist())) == 120, "distinct root labels")
    norm4_counts = Counter(pack(norm4_labels).tolist())
    require(len(norm4_counts) == 135 and set(norm4_counts.values()) == {8}, "norm-four label fibers")
    require(0 not in norm4_counts and not set(pack(root_labels).tolist()) & set(norm4_counts),
            "root and norm-four label sets disjoint, zero absent")

    buffer = io.BytesIO()
    np.save(buffer, P)
    result = {
        "status": "PASS_EXHAUSTIVE_INTEGER_H6_WALSH",
        "ports": N,
        "ordered_pairs_checked": checked,
        "pairing_histogram": actual_histogram,
        "compensation_nonzeros": nnz,
        "compensation_row_degree": [degree_min, degree_max],
        "exceptional_abs_t_3_pairs": exceptional,
        "exceptional_share_of_nonzeros_exact": str(Fraction(exceptional, nnz)),
        "exceptional_share_of_nonzeros_percent": 100 * exceptional / nnz,
        "binary_rank": 16,
        "root_basis_indices": root_basis_indices,
        "root_basis_doubled_vectors": Q.tolist(),
        "root_gram": G.tolist(),
        "root_gram_determinant": determinant,
        "root_gram_inverse": G_inverse.tolist(),
        "alternating_form": M.tolist(),
        "label_span_witness_indices": label_witnesses,
        "distinct_labels": len(multiplicity),
        "label_multiplicity_histogram": sorted(Counter(multiplicity.values()).items()),
        "root_label_count": 120,
        "norm4_label_count_per_block": 135,
        "norm4_label_multiplicity": 8,
        "proposal_seed_3_principal_minor_indices": seed_indices.tolist(),
        "proposal_seed_3_principal_minor_inverse": seed_inverse.tolist(),
        "walsh_full_dimension": 65536,
        "walsh_orthogonal_normalization_divisor": 256,
        "all_attainable_scalar_identities": scalar_identity,
        "negative_control_max_absolute_errors": {
            name: str(Fraction(value, 48)) for name, value in negative_maxima.items()},
        "p_npy_sha256": hashlib.sha256(buffer.getvalue()).hexdigest(),
        "p_canonical_little_endian_int64_sha256": hashlib.sha256(P.astype("<i8").tobytes()).hexdigest(),
        "inputs_sha256": {relative: source_hash(relative) for relative in (
            "h6-banked-breakeven/walsh.py", "h6-banked-breakeven/structure.py",
            "h6-banked-breakeven/README.md", "niemeier-lattices/code/e8_cubed.py")},
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "platform": platform.platform(), "chunk_rows": args.chunk_rows},
        "elapsed_seconds": time.monotonic() - started,
        "scope": "Finite exhaustive parity and compensation identities; algebraic rank-16 proof; no arithmetic circuit, helper-loading, or kappa claim.",
    }
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload)
        print(json.dumps({key: result[key] for key in (
            "status", "ports", "ordered_pairs_checked", "binary_rank",
            "compensation_nonzeros", "exceptional_abs_t_3_pairs", "elapsed_seconds")}, sort_keys=True))
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
