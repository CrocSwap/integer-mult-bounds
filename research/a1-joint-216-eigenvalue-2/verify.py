#!/usr/bin/env python3
"""Geometric multiplicity of eigenvalue 2 on the pinned 216-by-216 matrix.

The matrix M is the integer matrix of B = 4 A_1 in the basis pinned by
research/a1-joint-216-charpoly/. The matrix of A_1 is M/4, so eigenvalue 2
of A_1 is eigenvalue 8 of M. The geometric multiplicity is the nullity of
M - 8 I. Acceptance uses explicit checks, so -O does not skip a theorem or
a rejection control.
"""

import hashlib
import json
import pathlib
import re
import sys
from math import gcd, isqrt, lcm

ROOT = pathlib.Path(__file__).resolve().parents[2]
PACKAGE = pathlib.Path(__file__).resolve().parent
MATRIX_PATH = ROOT / "research/a1-joint-216-charpoly/evidence/matrix.json"
BASIS_PATH = ROOT / "research/a1-joint-216-charpoly/evidence/basis.json"
PREDECESSOR = ROOT / "research/a1-joint-216-charpoly/verify.py"
SELECTED = ROOT / "certificates/selected-result.json"
KERNEL_PATH = PACKAGE / "evidence" / "kernel.json"
MATRIX_SHA256 = "44f40ad5a12daf7c8493b42e1e9ddc4ef338b317ee5fdfc6de1b413642ca97aa"
BASIS_SHA256 = "e198cd71f4100d2629ecc25fb40b135a8c18c7756be8bc80bf24d7b349af418a"
SELECTED_SHA256 = "9b8d0eea95b3bf0dfcb7938a732a6439b87a2685dec2a5ab9e525b3b34debbfa"
SELECTED_KAPPA = "781451/250000000"
PRIME = 1000003
PRIME_TWO = 1000033
DIMENSION = 216
SHIFT = 8
EIGENVALUE = 2
RECORDED_ALGEBRAIC_MULTIPLICITY = 12
RECORDED_FACTOR = "(12, (-2, 1))"


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


def shift_matrix(matrix, shift):
    shifted = [row[:] for row in matrix]
    for index in range(len(shifted)):
        shifted[index][index] -= shift
    return shifted


def load_pinned():
    matrix_bytes = MATRIX_PATH.read_bytes()
    basis_bytes = BASIS_PATH.read_bytes()
    expect(sha256_bytes(matrix_bytes) == MATRIX_SHA256, "pinned matrix SHA256 changed")
    expect(sha256_bytes(basis_bytes) == BASIS_SHA256, "pinned basis SHA256 changed")
    matrix = json.loads(matrix_bytes)["rows"]
    basis = json.loads(basis_bytes)
    expect(len(matrix) == DIMENSION and all(len(row) == DIMENSION for row in matrix), "matrix is not 216 by 216")
    expect(len(basis["vectors"]) == DIMENSION, "basis does not have 216 vectors")
    expect(basis["eigenvalues"] == {"H": 1, "g": 1, "t": 1}, "basis is not the joint (+1,+1) space")
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
    rank_two, pivots_two, _rows_two, _reduced_two = rref(matrix, PRIME_TWO)
    expect(pivots_two == pivots, "the second prime used different pivot columns")
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


def recorded_algebraic_multiplicity(source):
    match = re.search(r"\((\d+), \(-2, 1\)\)", source)
    if match is None:
        return None
    return int(match.group(1))


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
    shifted = shift_matrix([[8, 1], [0, 3]], SHIFT)
    expect(shifted == [[0, 1], [0, -5]], "the 2-by-2 shift fixture is not M - 8 I")
    rank, pivots, _rows, reduced = rref(shifted, PRIME)
    expect(rank == 1 and pivots == [1], "the shift fixture does not have rank 1")
    recovered = integer_kernel(reduced, pivots, PRIME)
    expect(recovered is not None and recovered[1] == [[1, 0]], "the shift fixture kernel is not (1, 0)")
    expect(annihilates(shifted, recovered[1]), "the shift fixture kernel is not exact")


def main():
    fixture()
    expect(4 * EIGENVALUE == SHIFT, "eigenvalue 2 of A_1 is not eigenvalue 8 of M")
    matrix, basis = load_pinned()
    sizes = support_sizes(basis)
    expect(set(sizes) == {1, 4, 8, 16}, "support sizes are not the pinned set {1, 4, 8, 16}")
    expect(all(size > 0 for size in sizes), "a support size is not positive")
    shifted = shift_matrix(matrix, SHIFT)
    expect(symmetric_scaling(matrix, sizes), "size_i M_ij is not equal to size_j M_ji")
    expect(symmetric_scaling(shifted, sizes), "size_i (M - 8 I)_ij is not equal to size_j (M - 8 I)_ji")
    certificate = certify(shifted)
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
    entry_bound = max(abs(entry) for vector in vectors for entry in vector)
    expect(entry_bound * entry_bound * 2 < PRIME, "kernel height is not below the one-prime reconstruction bound")
    gram = gram_det(vectors, sizes, PRIME)
    gram_two = gram_det(vectors, sizes, PRIME_TWO)
    expect(gram != 0 and gram_two != 0, "the weighted Gram determinant of the kernel vanishes")
    # D (M - 8 I) is symmetric and the form is nondegenerate on the kernel, so
    # ker(M - 8 I) meets im(M - 8 I) only at 0. The ascent of eigenvalue 8 is
    # 1, and the algebraic multiplicity equals the geometric multiplicity.
    # See PROOF.md. The predecessor records the factor (x - 2)^12 of chi_{A_1}.
    algebraic = geometric
    predecessor = PREDECESSOR.read_text(encoding="utf-8")
    recorded = recorded_algebraic_multiplicity(predecessor)
    expect(recorded == RECORDED_ALGEBRAIC_MULTIPLICITY, "the recorded factor (x - 2)^12 changed")
    expect("(12, (2, 1))" in predecessor, "the distinct factor (x + 2)^12 is missing")
    expect(algebraic == recorded, "ascent multiplicity disagrees with the recorded factor (x - 2)^12")
    selected_bytes = SELECTED.read_bytes()
    expect(sha256_bytes(selected_bytes) == SELECTED_SHA256, "selected-result SHA256 changed")
    selected = json.loads(selected_bytes)
    expect(selected["kappa"] == SELECTED_KAPPA, "selected kappa changed")
    diagonal = certificate["free_diagonal"]
    diagonal_product = 1
    for entry in diagonal:
        diagonal_product *= entry
    nonzero_entries = sum(1 for vector in vectors for entry in vector if entry)
    payload = {
        "prime": PRIME,
        "second_prime": PRIME_TWO,
        "dimension": DIMENSION,
        "shift": SHIFT,
        "eigenvalue_of_A1": EIGENVALUE,
        "eigenvalue_of_M": SHIFT,
        "rational_rank": rational_rank,
        "geometric_multiplicity": geometric,
        "algebraic_multiplicity": algebraic,
        "recorded_factor": RECORDED_FACTOR,
        "modular_rank_lower_bound": rank_mod,
        "pivot_rows": certificate["pivot_rows"],
        "pivot_columns": certificate["pivot_columns"],
        "free_columns": certificate["free_columns"],
        "free_diagonal": diagonal,
        "free_diagonal_product": diagonal_product,
        "minor_det_mod_prime": certificate["minor_det_mod_prime"],
        "minor_det_mod_second_prime": certificate["minor_det_mod_second_prime"],
        "gram_det_mod_prime": gram,
        "gram_det_mod_second_prime": gram_two,
        "entry_bound": entry_bound,
        "nonzero_entries": nonzero_entries,
        "vectors": vectors,
    }
    if "--dump-evidence" in sys.argv:
        KERNEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        KERNEL_PATH.write_text(canonical(payload) + "\n", encoding="utf-8")
        print("dumped", KERNEL_PATH)
    else:
        pinned = json.loads(KERNEL_PATH.read_text(encoding="utf-8"))
        expect(pinned == payload, "pinned kernel certificate does not match the recomputation")

    # Rejection controls. Each must fail closed.
    expect(not annihilates(matrix, vectors), "the unshifted matrix annihilated the eigenvalue-8 kernel")
    bumped = shift_matrix(matrix, SHIFT - 1)
    expect(not annihilates(bumped, vectors), "M - 7 I still annihilated the kernel of M - 8 I")
    broken = [row[:] for row in matrix]
    broken[0][1] += 1
    expect(not symmetric_scaling(broken, sizes), "an off-diagonal increment still satisfied the scaling identity")
    zeroed = [vector[:] for vector in vectors]
    zeroed[0] = [0] * DIMENSION
    expect(
        free_diagonal(zeroed, certificate["free_columns"]) is None
        or free_diagonal(zeroed, certificate["free_columns"])[0] == 0,
        "a zero kernel vector still had a positive free diagonal",
    )
    repeated = [row[:] for row in shifted]
    repeated[certificate["pivot_rows"][0]] = repeated[certificate["pivot_rows"][1]][:]
    expect(
        minor_det(repeated, certificate["pivot_rows"], certificate["pivot_columns"], PRIME) == 0,
        "a repeated pivot row still had a nonzero minor",
    )
    replaced = predecessor.replace(RECORDED_FACTOR, "(11, (-2, 1))", 1)
    expect(recorded_algebraic_multiplicity(replaced) == 11, "the multiplicity parser missed a changed factor")
    expect(recorded_algebraic_multiplicity(replaced) != algebraic, "a changed recorded factor still matched")

    print("PASS_A1_JOINT_216_EIGENVALUE_2")
    print("evidence class: proof for the pinned matrix")
    print("selected kappa", SELECTED_KAPPA)
    print("rational rank", rational_rank)
    print("geometric multiplicity", geometric)
    print("algebraic multiplicity", algebraic)
    print("modular rank lower bound", rank_mod, "at", PRIME, "and", PRIME_TWO)
    print("kernel entry bound", entry_bound)
    print("nonzero kernel entries", nonzero_entries)
    print("free columns", certificate["free_columns"])
    print("free diagonal", diagonal)
    print("free diagonal product", diagonal_product)
    print("minor", certificate["minor_det_mod_prime"], certificate["minor_det_mod_second_prime"])
    print("gram", gram, gram_two)


if __name__ == "__main__":
    main()
