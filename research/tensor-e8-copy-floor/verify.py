#!/usr/bin/env python3
"""Exact finite premises for the tensor E8 copy-floor note. Standard library only.

No producer code, floating point, SAT solver, or precomputed rank is imported.
The all-depth argument is in README.md, not inferred from the finite controls.
"""

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def bits(word):
    while word:
        low = word & -word
        yield low.bit_length() - 1
        word ^= low


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def roots():
    """Coordinate roots and signed affine planes of F_2^3, modulo sign."""
    out = [tuple(2 * (i == j) for j in range(8)) for i in range(8)]
    planes = sorted({tuple(x for x in range(8) if (a & x).bit_count() % 2 == b)
                     for a in range(1, 8) for b in range(2)})
    for plane in planes:
        for signs in product((1, -1), repeat=3):
            row = [0] * 8
            for i, sign in zip(plane, (1,) + signs):
                row[i] = sign
            out.append(tuple(row))
    require(len(out) == len(set(out)) == 120, "root count")
    require(all(dot(r, r) == 4 for r in out), "root norm")
    return out


def binary_basis(rows):
    echelon = {}
    original = []
    for row in rows:
        value = row
        for pivot in sorted(echelon, reverse=True):
            if (value >> pivot) & 1:
                value ^= echelon[pivot]
        if value:
            echelon[value.bit_length() - 1] = value
            original.append(row)
    return original


def coordinates(rows, basis):
    echelon = {}
    for i, row in enumerate(basis):
        value, coeff = row, 1 << i
        for pivot in sorted(echelon, reverse=True):
            if (value >> pivot) & 1:
                v, c = echelon[pivot]
                value, coeff = value ^ v, coeff ^ c
        require(value != 0, "dependent binary basis")
        echelon[value.bit_length() - 1] = (value, coeff)
    out = []
    for row in rows:
        value, coeff = row, 0
        for pivot in sorted(echelon, reverse=True):
            if (value >> pivot) & 1:
                v, c = echelon[pivot]
                value, coeff = value ^ v, coeff ^ c
        require(value == 0, "word outside code")
        out.append(coeff)
    return out


def combine(mask, vectors):
    result = 0
    for i in bits(mask):
        result ^= vectors[i]
    return result


def q_basis_indices(rows, indices, dimension):
    """Fraction elimination; returns an actual independent subset."""
    echelon, chosen = {}, []
    for i in indices:
        row = list(map(Fraction, rows[i]))
        for pivot, old in sorted(echelon.items()):
            factor = row[pivot]
            if factor:
                row = [x - factor * y for x, y in zip(row, old)]
        pivot = next((j for j, x in enumerate(row) if x), None)
        if pivot is not None:
            factor = row[pivot]
            echelon[pivot] = [x / factor for x in row]
            chosen.append(i)
            if len(chosen) == dimension:
                break
    return chosen


def determinant(rows):
    """Independent fraction-free Bareiss determinant, including row swaps."""
    a = [list(row) for row in rows]
    n, previous, sign = len(a), 1, 1
    require(all(len(row) == n for row in a), "square determinant")
    for k in range(n - 1):
        pivot = next((i for i in range(k, n) if a[i][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = a[k][k] * a[i][j] - a[i][k] * a[k][j]
                require(numerator % previous == 0, "inexact Bareiss division")
                a[i][j] = numerator // previous
            a[i][k] = 0
        previous = a[k][k]
    return sign * a[-1][-1]


def kron_vector(a, b):
    return tuple(x * y for x in a for y in b)


def kron_support(a, b, size):
    return sum(b << (i * size) for i in bits(a))


def mod_basis_indices(rows, indices, dimension, prime=3):
    """A nonzero minor modulo 3 also certifies full rational rank."""
    echelon, chosen = {}, []
    for i in indices:
        row = [x % prime for x in rows[i]]
        for pivot, old in sorted(echelon.items()):
            factor = row[pivot]
            if factor:
                row = [(x - factor * y) % prime for x, y in zip(row, old)]
        pivot = next((j for j, x in enumerate(row) if x), None)
        if pivot is not None:
            inv = pow(row[pivot], -1, prime)
            echelon[pivot] = [(x * inv) % prime for x in row]
            chosen.append(i)
            if len(chosen) == dimension:
                break
    return chosen


def tensor_basis_control(matrix, base_basis, physical):
    """One seeded nonseparable 81-total factorization; every matrix entry checked."""
    n, rank = len(matrix), len(base_basis)
    left_rows = coordinates(matrix, base_basis)
    left = [sum(1 << i for i, row in enumerate(left_rows) if (row >> k) & 1)
            for k in range(rank)]
    lcols = [kron_support(a, b, n) for a in left for b in left]
    rcols = [kron_support(a, b, n) for a in base_basis for b in base_basis]
    lcoeff = [1 << i for i in range(rank * rank)]
    rcoeff = lcoeff.copy()
    rng = random.Random(43)
    operations = [tuple(rng.sample(range(rank * rank), 2)) for _ in range(3 * rank * rank)]
    for dst, src in operations:
        lcols[dst] ^= lcols[src]
        lcoeff[dst] ^= lcoeff[src]
        rcols[src] ^= rcols[dst]
        rcoeff[src] ^= rcoeff[dst]
    require(len(binary_basis(lcoeff)) == len(binary_basis(rcoeff)) == 81,
            "singular tensor basis")
    entangled = sum(len(binary_basis([(c >> (9 * j)) & 511 for j in range(9)])) > 1
                    for c in lcoeff + rcoeff)
    require(entangled > 0, "tensor control did not mix factors")
    for i, a in enumerate(matrix):
        for j, b in enumerate(matrix):
            t = i * n + j
            actual = combine(sum(1 << k for k, col in enumerate(lcols) if (col >> t) & 1), rcols)
            require(actual == kron_support(a, b, n), "tensor decoder identity")
    proots = [kron_vector(a, b) for a in physical for b in physical]
    witnesses = []
    for support in lcols + rcols:
        witness = mod_basis_indices(proots, bits(support), 64)
        require(len(witness) == 64, "tensor support rank")
        witnesses.append(witness)
    return {
        "seed": 43, "basis_changes": len(operations), "totals": 81,
        "nonseparable_factors": entangled, "full_rank_supports": len(witnesses),
        "support_dimension": 64, "minor_prime": 3,
        "matrix_entries_checked": n ** 4, "copy_rank_sum": 5184,
        "operations_sha256": digest(operations), "minor_indices_sha256": digest(witnesses),
    }


def toy_tensor_controls():
    # Every nonzero word of this [3,2] code selects two independent Q^2 vectors.
    code = [0b101, 0b110]
    vectors = [(1, 0), (0, 1), (1, 1)]
    receipt = []
    for depth in (1, 2):
        basis, labels, size = code, vectors, 3
        for _ in range(1, depth):
            basis = [kron_support(a, b, 3) for a in basis for b in code]
            labels = [kron_vector(a, b) for a in labels for b in vectors]
            size *= 3
        for mask in range(1, 1 << len(basis)):
            support = combine(mask, basis)
            require(len(q_basis_indices(labels, bits(support), 2 ** depth)) == 2 ** depth,
                    "toy tensor premise")
        receipt.append({"depth": depth, "all_nonzero_words": (1 << len(basis)) - 1,
                        "physical_dimension": 2 ** depth, "ports": size})
    return receipt


def negative_controls(physical, matrix, base_basis, witnesses):
    passed = []

    def rejects(name, f):
        try:
            f()
        except ValueError:
            passed.append(name)
        else:
            raise ValueError("negative control accepted: " + name)

    bad = [list(row) for row in physical]
    bad[0][0] += 1
    rejects("corrupt_root_norm", lambda: require(all(dot(r, r) == 4 for r in bad), "root norm"))
    mutant = matrix.copy()
    mutant[0] ^= 1
    rejects("corrupt_decoder_diagonal", lambda: require(all((r >> i) & 1 for i, r in enumerate(mutant)), "diagonal"))
    rejects("omit_independent_total", lambda: coordinates(matrix, base_basis[:-1]))
    bad_minor = witnesses[0]["minor_indices"].copy()
    bad_minor[-1] = bad_minor[0]
    rejects("duplicate_minor_row", lambda: require(determinant([physical[i] for i in bad_minor]) != 0, "minor"))
    # A single deleted root breaks the full-span premise: its B row now
    # selects exactly the 63 roots orthogonal to it, which have rank seven.
    reader = matrix[0] & ~1
    rank = len(q_basis_indices(physical, bits(reader), 8))
    require(rank == 7, "puncture control rank")
    rejects("apply_full_span_claim_after_one_puncture", lambda: require(rank == 8, "puncture"))
    # Extra factors need not lie in the code. B = sum_i e_i (row_i B)
    # is an explicit valid 120-total factorization with rank-one source supports.
    outside = next(1 << i for i in range(120) if len(binary_basis(base_basis + [1 << i])) == 10)
    rejects("extend_to_unrestricted_overcomplete_factors", lambda: coordinates([outside], base_basis))
    # Degenerate physical pairing: full spans alone do not force full pairing rank.
    gram = [[sum(a[k] * b[k] for k in range(7)) for b in physical[:8]] for a in physical[:8]]
    rejects("drop_nondegeneracy_hypothesis", lambda: require(determinant(gram) != 0, "degenerate form"))
    # Tensor identities require inverse-transpose changes on the other side.
    left = [0b01, 0b11]
    wrong_right = [0b01, 0b10]
    rejects("omit_inverse_transpose_update", lambda: require(
        [combine(sum(1 << k for k, c in enumerate(left) if (c >> i) & 1), wrong_right)
         for i in range(2)] == [1, 2], "factorization"))
    return passed


def verify():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for path, sha in sources["local_source_sha256"].items():
        require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == sha, "source hash: " + path)
    physical = roots()
    prototype = json.loads((ROOT / sources["prototype"]).read_text())
    require(set(physical) == set(map(tuple, prototype["root_lines"])), "prototype root set")
    matrix = []
    for a in physical:
        require(all(dot(a, b) % 2 == 0 for b in physical), "integral Gram matrix")
        matrix.append(sum(((1 + dot(a, b) // 2) % 2) << i for i, b in enumerate(physical)))
    require(all((row >> i) & 1 for i, row in enumerate(matrix)), "decoder diagonal")
    port_by_root = dict(zip(map(tuple, prototype["root_lines"]), prototype["binary_ports"]))
    labels = [port_by_root[r] for r in physical]
    require(all(((matrix[i] >> j) & 1) == ((labels[i] & labels[j]).bit_count() % 2)
                for i in range(120) for j in range(120)), "prototype binary pairing")
    base_basis = binary_basis(matrix)
    require(len(base_basis) == 9, "binary decoder rank")
    witnesses, histogram = [], Counter()
    for coeff in range(1, 512):
        support = combine(coeff, base_basis)
        chosen = q_basis_indices(physical, bits(support), 8)
        require(len(chosen) == 8, "base reader span")
        det = determinant([physical[i] for i in chosen])
        require(det != 0, "base exact minor")
        histogram[support.bit_count()] += 1
        witnesses.append({"coefficient": coeff, "support_hex": hex(support),
                          "minor_indices": chosen, "determinant": det})
    require(dict(histogram) == {56: 255, 64: 255, 120: 1}, "reader weight census")
    return {
        "status": "PASS_TENSOR_E8_COPY_FLOOR", "base_commit": sources["base_commit"],
        "scope": "Exact base premises and finite controls; all-depth theorem is a written proof.",
        "base": {"ports": 120, "binary_rank": 9, "physical_dimension": 8,
                 "nonzero_codewords": 511, "weight_histogram": dict(sorted(histogram.items())),
                 "roots_sha256": digest(physical), "binary_matrix_sha256": digest(matrix),
                 "basis_rows_hex": list(map(hex, base_basis)), "minors": witnesses},
        "tensor_control": tensor_basis_control(matrix, base_basis, physical),
        "exhaustive_toy_controls": toy_tensor_controls(),
        "negative_controls": negative_controls(physical, matrix, base_basis, witnesses),
        "theorem_prices": [{"depth": d, "ports": 120 ** d, "totals": 9 ** d,
                            "rank_per_copy": 8 ** d, "copy_rank_sum": 72 ** d,
                            "copy_per_port": str(Fraction(3, 5) ** d)} for d in range(1, 7)],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a new receipt instead of comparing the committed receipt")
    args = parser.parse_args()
    result = verify()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        args.write.write_text(encoded)
    else:
        require(encoded == (HERE / "RESULTS.json").read_text(), "committed receipt mismatch")
    print("PASS_TENSOR_E8_COPY_FLOOR: 511 exact base minors; 162 tensor supports; 8 negative controls; cost 72^d")


if __name__ == "__main__":
    main()
