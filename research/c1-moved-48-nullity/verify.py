#!/usr/bin/env python3
"""Geometric multiplicity of eigenvalue 0 on the pinned 48-by-48 matrix.

The matrix is the integer matrix of B = 4 A_1 in the eigenvalue-+1 basis of
s pinned by research/c1-moved-48-charpoly/ at commit 0a670e4d. Those bytes
are vendored here because that commit is not on main. Eigenvalue 0 of A_1
and of B have the same kernel. Acceptance uses explicit checks, so -O does
not skip a theorem or a rejection control.
"""

import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
from math import gcd, isqrt, lcm

ROOT = pathlib.Path(__file__).resolve().parents[2]
PACKAGE = pathlib.Path(__file__).resolve().parent
MATRIX_PATH = PACKAGE / "evidence" / "matrix.json"
BASIS_PATH = PACKAGE / "evidence" / "basis.json"
KERNEL_PATH = PACKAGE / "evidence" / "kernel.json"
SELECTED = ROOT / "certificates" / "selected-result.json"
MATRIX_SHA256 = "32b45cef4c1461f81b7b04b07ad388058cd872159a3f29107c6fe47ada6c4eae"
BASIS_SHA256 = "c18744f28d41c76a9b4299539a8c56e197a16850dd7ccc32aa7d227a48ef6764"
SELECTED_SHA256 = "9b8d0eea95b3bf0dfcb7938a732a6439b87a2685dec2a5ab9e525b3b34debbfa"
SELECTED_KAPPA = "781451/250000000"
PREDECESSOR_COMMIT = "0a670e4db89c79e6536dd4f448da0664d3f73890"
PREDECESSOR_MATRIX = "research/c1-moved-48-charpoly/evidence/matrix.json"
PREDECESSOR_BASIS = "research/c1-moved-48-charpoly/evidence/basis.json"
PREDECESSOR_VERIFY = "research/c1-moved-48-charpoly/verify.py"
PREDECESSOR_VERIFY_SHA256 = "c44474de799a8b3d461b604aeac01c5f372838e4bbea484b99f55535060c54ca"
PRIME = 1000003
PRIME_TWO = 1000033
DIMENSION = 48
RECORDED_ALGEBRAIC_MULTIPLICITY = 10
CANONICAL_SIGNATURE = (1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1)


def fail(message):
    raise SystemExit("FAIL: " + message)


def expect(condition, message):
    if not condition:
        fail(message)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def canonical(obj):
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=True)


def ratrecon(residue, modulus):
    """Return the unique n/d in lowest terms with n/d ≡ residue mod modulus
    and n^2 + d^2 small enough to be unique, or None."""
    residue %= modulus
    if residue == 0:
        return 0, 1
    bound = isqrt(modulus // 2)
    remainder_prev, remainder = modulus, residue
    cofactor_prev, cofactor = 0, 1
    while remainder > bound and remainder:
        quote = remainder_prev // remainder
        remainder_prev, remainder = remainder, remainder_prev - quote * remainder
        cofactor_prev, cofactor = cofactor, cofactor_prev - quote * cofactor
    if cofactor < 0:
        remainder, cofactor = -remainder, -cofactor
    if cofactor == 0 or abs(cofactor) > bound or abs(remainder) > bound:
        return None
    if (remainder - residue * cofactor) % modulus != 0:
        return None
    common = gcd(abs(remainder), cofactor)
    return remainder // common, cofactor // common


def rref(matrix, prime):
    """Greedy row-reduced echelon form over F_prime.

    Returns rank, pivot columns, original indices of the pivot rows, and the
    reduced rows. Pivot column i and pivot row i correspond.
    """
    size = len(matrix)
    reduced = [[entry % prime for entry in row] for row in matrix]
    origin = list(range(size))
    rank = 0
    pivots = []
    for col in range(size):
        pivot = None
        for row in range(rank, size):
            if reduced[row][col]:
                pivot = row
                break
        if pivot is None:
            continue
        if pivot != rank:
            reduced[rank], reduced[pivot] = reduced[pivot], reduced[rank]
            origin[rank], origin[pivot] = origin[pivot], origin[rank]
        inverse = pow(reduced[rank][col], -1, prime)
        pivot_row = reduced[rank]
        for index in range(size):
            pivot_row[index] = pivot_row[index] * inverse % prime
        for row in range(size):
            if row == rank:
                continue
            factor = reduced[row][col]
            if not factor:
                continue
            destination = reduced[row]
            for index in range(size):
                destination[index] = (destination[index] - factor * pivot_row[index]) % prime
        pivots.append(col)
        rank += 1
    return rank, pivots, origin[:rank], reduced


def integer_kernel(reduced, pivots, prime):
    """Clear-denominator kernel basis for the normalized free columns."""
    size = len(reduced)
    pivot_set = set(pivots)
    free = [col for col in range(size) if col not in pivot_set]
    row_of = {col: index for index, col in enumerate(pivots)}
    vectors = []
    for col in free:
        fractions = []
        for index in range(size):
            if index == col:
                fractions.append((1, 1))
            elif index in pivot_set:
                entry = reduced[row_of[index]][col]
                recovered = ratrecon(0 if entry == 0 else prime - entry, prime)
                if recovered is None:
                    return None
                fractions.append(recovered)
            else:
                fractions.append((0, 1))
        denominator = 1
        for _numerator, den in fractions:
            denominator = lcm(denominator, den)
        vector = [numerator * (denominator // den) for numerator, den in fractions]
        common = 0
        for entry in vector:
            common = gcd(common, abs(entry))
        if common == 0:
            return None
        vector = [entry // common for entry in vector]
        if vector[col] < 0:
            vector = [-entry for entry in vector]
        vectors.append(vector)
    return free, vectors


def annihilates(matrix, vectors):
    for vector in vectors:
        for row in matrix:
            total = 0
            for coeff, entry in zip(row, vector):
                if coeff and entry:
                    total += coeff * entry
            if total:
                return False
    return True


def free_diagonal(vectors, free):
    diagonal = []
    for index, vector in enumerate(vectors):
        for column, position in enumerate(free):
            entry = vector[position]
            if column == index:
                diagonal.append(entry)
            elif entry:
                return None
    return diagonal


def det_mod(matrix, prime):
    """Determinant of a square matrix modulo prime. Zero means singular."""
    size = len(matrix)
    reduced = [[entry % prime for entry in row] for row in matrix]
    sign = 1
    determinant = 1
    for col in range(size):
        pivot = None
        for row in range(col, size):
            if reduced[row][col]:
                pivot = row
                break
        if pivot is None:
            return 0
        if pivot != col:
            reduced[col], reduced[pivot] = reduced[pivot], reduced[col]
            sign = -sign
        pivot_entry = reduced[col][col]
        determinant = determinant * pivot_entry % prime
        inverse = pow(pivot_entry, -1, prime)
        for row in range(col + 1, size):
            factor = reduced[row][col]
            if not factor:
                continue
            factor = factor * inverse % prime
            destination = reduced[row]
            source = reduced[col]
            for index in range(col, size):
                destination[index] = (destination[index] - factor * source[index]) % prime
    if sign < 0:
        determinant = (prime - determinant) % prime
    return determinant


def minor_det(matrix, rows, cols, prime):
    submatrix = [[matrix[row][col] for col in cols] for row in rows]
    return det_mod(submatrix, prime)


def support_sizes(basis):
    sizes = []
    for vector in basis["vectors"]:
        indices = [index for index, _coeff in vector]
        expect(len(indices) == len(set(indices)), "a basis vector repeats a coordinate")
        expect(all(coeff in (-1, 1) for _index, coeff in vector), "a basis coefficient is outside ±1")
        sizes.append(len(vector))
    return sizes


def symmetric_scaling(matrix, sizes):
    for row_index, row_size in enumerate(sizes):
        row = matrix[row_index]
        for col_index, col_size in enumerate(sizes):
            if row_size * row[col_index] != col_size * matrix[col_index][row_index]:
                return False
    return True


def gram_det(vectors, sizes, prime):
    count = len(vectors)
    gram = [[0] * count for _ in range(count)]
    for left in range(count):
        for right in range(left, count):
            total = 0
            for index, (first, second) in enumerate(zip(vectors[left], vectors[right])):
                if first and second:
                    total += first * sizes[index] * second
            gram[left][right] = total
            gram[right][left] = total
    return det_mod(gram, prime)


def load_pinned():
    matrix_bytes = MATRIX_PATH.read_bytes()
    basis_bytes = BASIS_PATH.read_bytes()
    expect(sha256_bytes(matrix_bytes) == MATRIX_SHA256, "pinned matrix SHA256 changed")
    expect(sha256_bytes(basis_bytes) == BASIS_SHA256, "pinned basis SHA256 changed")
    matrix = json.loads(matrix_bytes)["rows"]
    basis = json.loads(basis_bytes)
    expect(len(matrix) == DIMENSION and all(len(row) == DIMENSION for row in matrix), "matrix is not 48 by 48")
    expect(all(-16 <= entry <= 16 for row in matrix for entry in row), "a matrix entry lies outside -16..16")
    expect(len(basis["vectors"]) == DIMENSION, "basis does not have 48 vectors")
    expect(basis["eigenvalue_of_s"] == 1, "basis is not the eigenvalue-+1 space of s")
    expect(tuple(basis["character_values"]) == CANONICAL_SIGNATURE, "basis is not the character eps[1]*eps[2]")
    return matrix, basis


def certify(matrix):
    rank, pivots, pivot_rows, reduced = rref(matrix, PRIME)
    recovered = integer_kernel(reduced, pivots, PRIME)
    expect(recovered is not None, "rational reconstruction of the kernel was not unique at the working prime")
    free, vectors = recovered
    expect(len(vectors) == DIMENSION - rank, "kernel count disagrees with the modular corank")
    expect(annihilates(matrix, vectors), "a reconstructed vector is not an exact integer kernel vector")
    diagonal = free_diagonal(vectors, free)
    expect(diagonal is not None and all(entry > 0 for entry in diagonal), "free columns are not a positive diagonal")
    rank_two, _pivots_two, _rows_two, _reduced_two = rref(matrix, PRIME_TWO)
    minor = minor_det(matrix, pivot_rows, pivots, PRIME)
    minor_two = minor_det(matrix, pivot_rows, pivots, PRIME_TWO)
    expect(minor != 0, "the pivot minor vanishes modulo the working prime")
    return {
        "prime": PRIME,
        "second_prime": PRIME_TWO,
        "rank_mod_prime": rank,
        "rank_mod_second_prime": rank_two,
        "pivot_rows": pivot_rows,
        "pivot_columns": pivots,
        "free_columns": free,
        "free_diagonal": diagonal,
        "minor_det_mod_prime": minor,
        "minor_det_mod_second_prime": minor_two,
        "vectors": vectors,
    }


def git_blob(path):
    """Return predecessor bytes when that commit is in this clone, else None."""
    spec = PREDECESSOR_COMMIT + ":" + path
    env = os.environ.copy()
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    probe = subprocess.run(
        ["git", "-C", str(ROOT), "cat-file", "-e", spec],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if probe.returncode != 0:
        return None
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "cat-file", "blob", spec],
        env=env,
    )


def recorded_algebraic_multiplicity(source):
    match = re.search(r"FACTORS = \(\s*\((\d+), \(0, 1\)\)", source)
    if match is None:
        return None
    return int(match.group(1))


def confirm_predecessor():
    """When commit 0a670e4d is present, the vendored bytes and the factor x^10
    must be that commit's objects. Absence does not replace the rank proof."""
    matrix_blob = git_blob(PREDECESSOR_MATRIX)
    basis_blob = git_blob(PREDECESSOR_BASIS)
    verify_blob = git_blob(PREDECESSOR_VERIFY)
    present = matrix_blob is not None or basis_blob is not None or verify_blob is not None
    if not present:
        return False
    expect(matrix_blob is not None and basis_blob is not None and verify_blob is not None,
           "predecessor commit is only partly present")
    expect(sha256_bytes(matrix_blob) == MATRIX_SHA256, "predecessor matrix blob disagrees with the vendored matrix")
    expect(matrix_blob == MATRIX_PATH.read_bytes(), "vendored matrix is not the predecessor blob")
    expect(sha256_bytes(basis_blob) == BASIS_SHA256, "predecessor basis blob disagrees with the vendored basis")
    expect(basis_blob == BASIS_PATH.read_bytes(), "vendored basis is not the predecessor blob")
    expect(sha256_bytes(verify_blob) == PREDECESSOR_VERIFY_SHA256, "predecessor verify.py SHA256 changed")
    recorded = recorded_algebraic_multiplicity(verify_blob.decode("utf-8"))
    expect(recorded == RECORDED_ALGEBRAIC_MULTIPLICITY, "the recorded characteristic factor x^10 changed")
    return True


def fixture():
    sample = [[1, 2, 3], [2, 4, 6], [1, 1, 1]]
    rank, pivots, _rows, reduced = rref(sample, PRIME)
    expect(rank == 2 and pivots == [0, 1], "the rank fixture does not have pivots in columns 0 and 1")
    recovered = integer_kernel(reduced, pivots, PRIME)
    expect(recovered is not None, "the rank fixture kernel did not reconstruct")
    _free, vectors = recovered
    expect(len(vectors) == 1 and annihilates(sample, vectors), "the rank fixture kernel is wrong")
    expect(vectors[0] == [1, -2, 1], "the rank fixture kernel changed")
    singular = [[0, 0], [0, 0]]
    expect(det_mod(singular, PRIME) == 0, "a zero matrix had nonzero determinant")
    expect(det_mod([[1, 2], [3, 4]], PRIME) == (1 * 4 - 2 * 3) % PRIME, "a 2-by-2 determinant changed")
    # p ≡ 0 mod p, so the modular corank is 1, while the rational rank is 1.
    # Exact annihilation refuses that modular kernel vector.
    concealed = [[PRIME]]
    concealed_rank, concealed_pivots, _concealed_rows, concealed_reduced = rref(concealed, PRIME)
    expect(concealed_rank == 0 and concealed_pivots == [], "a multiple of the working prime had positive modular rank")
    concealed_kernel = integer_kernel(concealed_reduced, concealed_pivots, PRIME)
    expect(concealed_kernel is not None, "the modular kernel of a prime multiple did not reconstruct")
    _concealed_free, concealed_vectors = concealed_kernel
    expect(concealed_vectors == [[1]], "the modular kernel of a prime multiple changed")
    expect(not annihilates(concealed, concealed_vectors), "a modular kernel vector was accepted as a rational kernel vector")
    factor_text = "FACTORS = (\n    (10, (0, 1)),\n"
    expect(recorded_algebraic_multiplicity(factor_text) == 10, "the multiplicity parser missed the factor x^10")
    replaced = factor_text.replace("(10, (0, 1))", "(9, (0, 1))", 1)
    expect(recorded_algebraic_multiplicity(replaced) == 9, "the multiplicity parser missed a changed factor")


def main():
    fixture()
    matrix, basis = load_pinned()
    sizes = support_sizes(basis)
    expect(sizes.count(8) == 8 and sizes.count(16) == 32 and sizes.count(32) == 8,
           "support sizes are not eight 8s, thirty-two 16s and eight 32s")
    expect(symmetric_scaling(matrix, sizes), "size_i M_ij is not equal to size_j M_ji")
    certificate = certify(matrix)
    vectors = certificate["vectors"]
    rank_mod = certificate["rank_mod_prime"]
    nullity = len(vectors)
    # Modular rank is a lower bound on the rational rank. The explicit kernel
    # is an upper bound. The nonzero pivot minor is the same lower bound,
    # witnessed by one integer minor.
    expect(rank_mod == certificate["rank_mod_second_prime"], "two modular ranks disagree")
    expect(certificate["minor_det_mod_second_prime"] != 0, "the same pivot minor vanishes at the second prime")
    rational_rank_at_least = rank_mod
    rational_rank_at_most = DIMENSION - nullity
    expect(rational_rank_at_least == rational_rank_at_most, "kernel corank does not meet the modular lower bound")
    rational_rank = rational_rank_at_least
    geometric = DIMENSION - rational_rank
    gram = gram_det(vectors, sizes, PRIME)
    gram_two = gram_det(vectors, sizes, PRIME_TWO)
    expect(gram != 0 and gram_two != 0, "the weighted Gram determinant of the kernel vanishes")
    # D M symmetric and the form nondegenerate on the kernel imply
    # ker M ∩ im M = 0, so the ascent of eigenvalue 0 is 1 and the algebraic
    # multiplicity equals the geometric multiplicity. See PROOF.md.
    algebraic = geometric
    expect(algebraic == RECORDED_ALGEBRAIC_MULTIPLICITY, "ascent multiplicity is not the recorded value 10")
    predecessor_present = confirm_predecessor()
    selected_bytes = SELECTED.read_bytes()
    expect(sha256_bytes(selected_bytes) == SELECTED_SHA256, "selected-result SHA256 changed")
    selected = json.loads(selected_bytes)
    expect(selected["kappa"] == SELECTED_KAPPA, "selected kappa changed")
    payload = {
        "prime": PRIME,
        "second_prime": PRIME_TWO,
        "dimension": DIMENSION,
        "rational_rank": rational_rank,
        "geometric_multiplicity": geometric,
        "algebraic_multiplicity": algebraic,
        "modular_rank_lower_bound": rank_mod,
        "pivot_rows": certificate["pivot_rows"],
        "pivot_columns": certificate["pivot_columns"],
        "free_columns": certificate["free_columns"],
        "free_diagonal": certificate["free_diagonal"],
        "minor_det_mod_prime": certificate["minor_det_mod_prime"],
        "minor_det_mod_second_prime": certificate["minor_det_mod_second_prime"],
        "gram_det_mod_prime": gram,
        "gram_det_mod_second_prime": gram_two,
        "entry_bound": max(abs(entry) for vector in vectors for entry in vector),
        "vectors": vectors,
    }
    if "--dump-evidence" in sys.argv:
        KERNEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        KERNEL_PATH.write_text(canonical(payload) + "\n", encoding="utf-8")
    else:
        pinned = json.loads(KERNEL_PATH.read_text(encoding="utf-8"))
        expect(pinned == payload, "pinned kernel certificate does not match the recomputation")

    shifted = [row[:] for row in matrix]
    for index in range(DIMENSION):
        shifted[index][index] += 1
    expect(not annihilates(shifted, vectors), "adding the identity still annihilated the kernel")
    broken = [row[:] for row in matrix]
    broken[0][1] += 1
    expect(not symmetric_scaling(broken, sizes), "an off-diagonal increment still satisfied the scaling identity")
    zeroed = [vector[:] for vector in vectors]
    zeroed[0] = [0] * DIMENSION
    zero_diagonal = free_diagonal(zeroed, certificate["free_columns"])
    expect(zero_diagonal is None or zero_diagonal[0] == 0,
           "a zero kernel vector still had a positive free diagonal")
    repeated = [row[:] for row in matrix]
    repeated[certificate["pivot_rows"][0]] = repeated[certificate["pivot_rows"][1]][:]
    expect(minor_det(repeated, certificate["pivot_rows"], certificate["pivot_columns"], PRIME) == 0,
           "a repeated pivot row still had a nonzero minor")

    print("PASS_C1_MOVED_48_NULLITY")
    print("evidence class: proof for the pinned matrix")
    print("selected kappa", SELECTED_KAPPA)
    print("rational rank", rational_rank)
    print("geometric multiplicity", geometric)
    print("algebraic multiplicity", algebraic)
    print("modular rank lower bound", rank_mod, "at", PRIME, "and", PRIME_TWO)
    print("kernel entry bound", payload["entry_bound"])
    print("free columns", certificate["free_columns"])
    print("free diagonal", certificate["free_diagonal"])
    print("minor residues", certificate["minor_det_mod_prime"], certificate["minor_det_mod_second_prime"])
    print("gram residues", gram, gram_two)
    print("predecessor commit checked" if predecessor_present else "predecessor commit absent from this clone")


if __name__ == "__main__":
    main()
