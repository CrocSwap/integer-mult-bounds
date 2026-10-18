#!/usr/bin/env python3
"""25-bit labels with p(u).p(v)=1+(u.v/8) mod 2 for integer Leech rows."""
from pathlib import Path
import argparse
import json
import numpy as np
from leech_geometry import require


def inverse(matrix):
    n = len(matrix)
    work = np.concatenate((matrix.copy(), np.eye(n, dtype=np.uint8)), axis=1)
    for col in range(n):
        pivots = np.flatnonzero(work[col:, col])
        require(len(pivots) > 0, "Singular binary matrix")
        pivot = col + int(pivots[0])
        work[[col, pivot]] = work[[pivot, col]]
        for row in range(n):
            if row != col and work[row, col]:
                work[row] ^= work[col]
    return work[:, n:]


def symplectic(matrix):
    n = len(matrix)
    require(n % 2 == 0 and np.array_equal(matrix, matrix.T) and not np.diag(matrix).any(),
            "Symplectic input must be even-dimensional alternating")
    work = matrix.copy()
    transform = np.eye(n, dtype=np.uint8)
    for first in range(0, n, 2):
        candidates = np.argwhere(work[first:, first:])
        require(len(candidates) > 0, "Degenerate alternating matrix")
        a, b = map(lambda x: int(x) + first, candidates[0])
        for current, target in ((a, first), (b if b != first else a, first + 1)):
            work[[current, target]] = work[[target, current]]
            work[:, [current, target]] = work[:, [target, current]]
            transform[[current, target]] = transform[[target, current]]
        require(work[first, first + 1] == 1, "Failed symplectic pivot")
        for j in range(first + 2, n):
            x, y = int(work[j, first + 1]), int(work[j, first])
            if x:
                transform[j] ^= transform[first]
            if y:
                transform[j] ^= transform[first + 1]
        work = (transform @ matrix @ transform.T) & 1
    target = np.zeros((n, n), dtype=np.uint8)
    for i in range(0, n, 2):
        target[i, i + 1] = target[i + 1, i] = 1
    require(np.array_equal(work, target), "Symplectic factorization mismatch")
    return transform


def pick_basis(vectors):
    rng = np.random.default_rng(24098280)
    candidates = np.sort(rng.choice(len(vectors), 256, replace=False))
    v = vectors[candidates].astype(np.int16)
    gram_integer = v @ v.T
    require(not (gram_integer % 8).any(), "Nonintegral lattice pairing")
    work = ((gram_integer // 8) & 1).astype(np.uint8)
    selected = []
    active = list(range(len(candidates)))
    while work[np.ix_(active, active)].any():
        sub = work[np.ix_(active, active)]
        aa, bb = np.argwhere(sub)[0]
        a, b = active[int(aa)], active[int(bb)]
        selected.extend((a, b))
        row_a, row_b = work[a].copy(), work[b].copy()
        work ^= np.outer(row_a, row_b) ^ np.outer(row_b, row_a)
        active.remove(a)
        active.remove(b)
    require(len(selected) == 24, f"Expected mod-2 lattice rank24, got {len(selected)}")
    return candidates[selected]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    path = parser.parse_args().output
    vectors = np.load(path / "minimal_lines.npy").astype(np.int16)
    indices = pick_basis(vectors)
    basis = vectors[indices]
    full_pairings = vectors @ basis.T
    require(not (full_pairings % 8).any(), "Nonintegral shell-basis pairing")
    a = ((full_pairings // 8) & 1).astype(np.uint8)
    gram = a[indices]
    gram_inv = inverse(gram)
    even_gram = np.ones((24, 24), dtype=np.uint8) ^ np.eye(24, dtype=np.uint8)
    t = symplectic(gram_inv)
    u = symplectic(even_gram)
    r = (inverse(t) @ u) & 1
    require(np.array_equal((r @ even_gram @ r.T) & 1, gram_inv), "Even-space isometry")
    e = np.concatenate((np.eye(24, dtype=np.uint8), np.ones((24, 1), dtype=np.uint8)), axis=1)
    labels = ((a @ r @ e) & 1) ^ 1
    require(np.all(labels.sum(axis=1) % 2 == 1), "Labels must have odd norm")
    packed = labels.astype(np.uint32) @ (1 << np.arange(25, dtype=np.uint32))
    require(len(set(map(int, packed))) == len(vectors), "Labels are not distinct")
    samples = np.unique(np.concatenate((indices, np.linspace(0, len(vectors) - 1, 64, dtype=int))))
    for index in samples:
        pairings = vectors @ vectors[index]
        require(not (pairings % 8).any(), "Nonintegral sample pairing")
        require(np.array_equal((labels @ labels[index]) & 1, 1 ^ ((pairings // 8) & 1)),
                f"Label identity failed at index {index}")
    np.save(path / "binary_labels.npy", labels)
    np.save(path / "binary_labels_packed.npy", packed)
    report = {
        "dimension": 25,
        "label_count": len(labels),
        "basis_indices": indices.tolist(),
        "basis_vectors": basis.tolist(),
        "gram_mod2": gram.tolist(),
        "gram_inverse_mod2": gram_inv.tolist(),
        "label_coordinate_map": ((r @ e) & 1).tolist(),
        "verified_sample_rows": samples.tolist(),
        "identity": "p(u) dot p(v) = 1 + (u dot v / 8) mod 2",
        "proof": "The selected integral lattice Gram matrix is nonsingular modulo2, so its integer determinant is odd. Its rational inverse reduces modulo2 to gram_inverse_mod2. Since its24 underlying real vectors are a basis, the ordinary inner product is exactly a(u) G^-1 a(v)^T over rational numbers. Thus the identity holds for every pair with integer pairings, not only the tested rows. The explicit coordinate map is an isometry into the even-weight subspace of F2^25; adding its all-ones orthogonal vector adds1 to every pairing.",
    }
    (path / "BINARY-LABELS.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"dimension": 25, "count": len(labels), "sample_rows": len(samples), "basis_indices": indices.tolist()}))


if __name__ == "__main__":
    main()
