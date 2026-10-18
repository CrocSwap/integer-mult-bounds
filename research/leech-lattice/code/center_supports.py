#!/usr/bin/env python3
"""Exact binary span dimensions of homogeneous cubic monomial supports."""
from collections import Counter
import argparse
from itertools import combinations_with_replacement
import json
from pathlib import Path
import numpy as np
from leech_geometry import require


def binary_rank(values):
    basis = {}
    selected = []
    for index, raw in enumerate(values):
        value = int(raw)
        while value:
            bit = value.bit_length() - 1
            if bit in basis:
                value ^= basis[bit]
            else:
                basis[bit] = value
                selected.append(index)
                break
        if len(basis) == 25:
            break
    return len(basis), selected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    path = parser.parse_args().output
    vectors = np.load(path / "minimal_lines.npy")
    packed = np.load(path / "binary_labels_packed.npy")
    odd = np.flatnonzero(np.all(vectors % 2 != 0, axis=1))
    require(len(odd) == 49152, "Odd orbit line count")
    rank, witness_local = binary_rank(packed[odd])
    require(rank == 24, "Expected binary span24 for odd orbit")
    witness = odd[witness_local]
    require(np.all(vectors[witness] != 0), "Witness in all monomial supports")
    monomials = list(combinations_with_replacement(range(24), 3))
    require(len(monomials) == 2600, "Cubic monomial count")
    histogram = Counter()
    rank_histogram = Counter()
    outside_witness = {}
    for monomial in monomials:
        support = np.flatnonzero(np.all(vectors[:, list(set(monomial))] != 0, axis=1))
        count = len(support)
        histogram[count] += 1
        support_rank, chosen = binary_rank(np.concatenate((packed[witness], packed[support])))
        rank_histogram[support_rank] += 1
        require(support_rank == 25, f"Cubic support rank: {monomial}")
        outside_witness[",".join(map(str, monomial))] = int(support[chosen[-1] - len(witness)])
    report = {
        "homogeneous_cubic_monomials": 2600,
        "support_binary_rank_histogram": dict(rank_histogram),
        "odd_orbit_binary_rank": rank,
        "extra_witness_per_monomial": outside_witness,
        "common_odd_orbit_size": len(odd),
        "common_full_rank_witness_indices": witness.tolist(),
        "support_size_histogram": dict(histogram),
        "proof": "Every cubic monomial is nonzero on the entire odd-coordinate orbit, whose labels have rank24. For each monomial, an additional support label outside this common24-space is recorded. Thus every monomial support spans all F2^25. This only prices the literal monomial factorization; it does not preclude alternative factorizations or support splitting.",
    }
    (path / "CENTER-SUPPORTS.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k:v for k,v in report.items() if k != "extra_witness_per_monomial"}, indent=2))


if __name__ == "__main__":
    main()
