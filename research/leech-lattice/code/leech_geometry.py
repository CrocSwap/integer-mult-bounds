#!/usr/bin/env python3
"""Exact integer coordinates for the Leech minimal shell (divide by sqrt(8)).

Construction: Bannai and Sloane, Uniqueness of Certain Spherical Codes,
Canadian J. Math. 33 (1981), 437--449, p.443, equation (12):
https://neilsloane.com/doc/Me71.pdf
Golay systematic generator: SageMath's GolayCode generator_matrix example:
https://doc.sagemath.org/html/en/reference/coding/sage/coding/golay_code.html

No assertion statements are used: checks remain enabled under python -O.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
from itertools import combinations
import json
from pathlib import Path
import numpy as np

RIGHT_ROWS = (
    "101011100011", "111110010010", "110100101011",
    "110001110110", "110011011001", "011001101101",
    "001100110111", "101101111000", "010110111100",
    "001011011110", "101110001101", "010111000111",
)
EXPECTED_WEIGHTS = {0: 1, 8: 759, 12: 2576, 16: 759, 24: 1}
EXPECTED_DOTS = {-32: 1, -16: 4600, -8: 47104, 0: 93150,
                 8: 47104, 16: 4600, 32: 1}


def require(condition, message):
    if not bool(condition):
        raise ValueError(message)


def golay_code():
    matrix = np.concatenate((np.eye(12, dtype=np.int16),
                             np.array([[int(b) for b in row] for row in RIGHT_ROWS],
                                      dtype=np.int16)), axis=1)
    messages = (np.arange(4096, dtype=np.uint16)[:, None] >> np.arange(12)) & 1
    words = ((messages @ matrix) & 1).astype(np.int8)
    require(np.array_equal((matrix @ matrix.T) & 1, np.zeros((12, 12))),
            "Golay generator is not self-orthogonal")
    require(dict(Counter(map(int, words.sum(axis=1)))) == EXPECTED_WEIGHTS,
            "Golay weight enumerator differs")
    require(len(set(map(bytes, words))) == 4096, "Golay words are not distinct")
    return matrix, words


def shell(words):
    vectors = np.zeros((196560, 24), dtype=np.int8)
    at = 0
    for i, j in combinations(range(24), 2):
        for first in (4, -4):
            for second in (4, -4):
                vectors[at, i], vectors[at, j] = first, second
                at += 1
    require(at == 1104, "Type A count")
    for word in words[words.sum(axis=1) == 8]:
        support = np.flatnonzero(word)
        for mask in range(128):
            signs = [-2 if mask >> j & 1 else 2 for j in range(7)]
            signs.append(-2 if mask.bit_count() & 1 else 2)
            vectors[at, support] = signs
            at += 1
    require(at == 98256, "Type B count")
    for word in words:
        signs = 1 - 2 * word
        for i in range(24):
            vectors[at] = signs
            vectors[at, i] = -3 * signs[i]
            at += 1
    require(at == 196560, "Type C count")
    return vectors


def verify(vectors, words, sample_count):
    require(vectors.shape == (196560, 24), "Shell shape")
    wide = vectors.astype(np.int16)
    require(np.all(np.sum(wide * wide, axis=1) == 32), "Shell norm")
    require(np.all((wide - wide[:, :1]) % 2 == 0), "Parity condition")
    require(np.all((wide.sum(axis=1) - 4 * wide[:, 0]) % 8 == 0),
            "Coordinate-sum condition")
    word_masks = set(map(int, words.astype(np.int64) @ (1 << np.arange(24))))
    for residue in range(4):
        masks = ((wide % 4 == residue).astype(np.int64) @ (1 << np.arange(24)))
        require(all(int(mask) in word_masks for mask in np.unique(masks)),
                f"Golay residue-class condition for residue {residue}")
    keys = set(map(bytes, vectors))
    require(len(keys) == 196560, "Distinct vectors")
    require(all(bytes(-v) in keys for v in vectors), "Antipodal completeness")
    first_nonzero = np.argmax(vectors != 0, axis=1)
    keep = vectors[np.arange(len(vectors)), first_nonzero] > 0
    lines = vectors[keep]
    require(lines.shape == (98280, 24), "Antipodal line count")
    indices = sorted(set([0, 1104, 98256] +
                         np.linspace(0, len(vectors) - 1, sample_count, dtype=int).tolist()))
    histograms = {}
    for i in indices:
        values, counts = np.unique(wide @ wide[i], return_counts=True)
        histogram = dict(zip(map(int, values), map(int, counts)))
        require(histogram == EXPECTED_DOTS, f"Inner-product distribution at row {i}")
        histograms[str(i)] = histogram
    return lines, histograms


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).parent)
    parser.add_argument("--sample-count", type=int, default=64)
    args = parser.parse_args()
    require(args.sample_count > 0, "Sample count must be positive")
    args.output.mkdir(parents=True, exist_ok=True)
    matrix, words = golay_code()
    vectors = shell(words)
    lines, histograms = verify(vectors, words, args.sample_count)
    np.save(args.output / "minimal_vectors.npy", vectors)
    np.save(args.output / "minimal_lines.npy", lines)
    np.save(args.output / "golay_words.npy", words)
    report = {
        "normalization": "integer vectors of norm squared 32; divide by sqrt(8) for norm squared 4",
        "generator_right_rows": list(RIGHT_ROWS),
        "golay_weights": EXPECTED_WEIGHTS,
        "shell_counts": {"two_4": 1104, "eight_2": 97152, "one_3_twenty_three_1": 98304},
        "antipodal_lines": len(lines),
        "sampled_rows": len(histograms),
        "inner_product_checks": histograms,
        "sample_scope": "All shell membership/norm/uniqueness/antipodal checks; full inner-product distributions only at specified rows, not all pairs.",
        "integer_vector_sha256": hashlib.sha256(vectors.tobytes()).hexdigest(),
        "integer_line_sha256": hashlib.sha256(lines.tobytes()).hexdigest(),
    }
    (args.output / "GEOMETRY.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "inner_product_checks"}, indent=2))


if __name__ == "__main__":
    main()
