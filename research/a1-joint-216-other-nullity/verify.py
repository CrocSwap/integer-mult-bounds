#!/usr/bin/env python3
"""Geometric multiplicity of eigenvalue 0 on the other three 216 joint sign spaces.

The predecessor package research/a1-joint-216-charpoly pins the joint (+1,+1)
matrix and proves that the four joint sign spaces of g and t share one
characteristic polynomial. Open PR #7018 computes the rational nullity of that
one pinned matrix. This verifier pins the other three matrices and computes
the rational nullity of each. Acceptance uses explicit checks, so -O does not
skip a theorem or a rejection control.
"""

import hashlib
import importlib.util
import json
import pathlib
import re
import sys
from math import gcd, isqrt, lcm

ROOT = pathlib.Path(__file__).resolve().parents[2]
PACKAGE = pathlib.Path(__file__).resolve().parent
PREDECESSOR = ROOT / "research/a1-joint-216-charpoly/verify.py"
BASIS_PATH = ROOT / "research/a1-joint-216-charpoly/evidence/basis.json"
MATRIX_PATH = ROOT / "research/a1-joint-216-charpoly/evidence/matrix.json"
SELECTED = ROOT / "certificates/selected-result.json"
EVIDENCE = PACKAGE / "evidence"
PREDECESSOR_SHA256 = "4ab1cf663cd1d7eb2698f70c7601709ef78415d9dce47746a65f95671d9ee26a"
BASIS_SHA256 = "e198cd71f4100d2629ecc25fb40b135a8c18c7756be8bc80bf24d7b349af418a"
MATRIX_SHA256 = "44f40ad5a12daf7c8493b42e1e9ddc4ef338b317ee5fdfc6de1b413642ca97aa"
SELECTED_SHA256 = "9b8d0eea95b3bf0dfcb7938a732a6439b87a2685dec2a5ab9e525b3b34debbfa"
SELECTED_KAPPA = "781451/250000000"
PRIME = 1000003
PRIME_TWO = 1000033
DIMENSION = 216
RECORDED_ALGEBRAIC_MULTIPLICITY = 24
RECORDED_PINNED_GEOMETRIC_MULTIPLICITY = 24
OTHER_SIGNS = ((1, -1), (-1, 1), (-1, -1))
EVIDENCE_SHA256 = {
    "g-plus-t-minus.json": "f3077453f9009ee4dd6cc4879cbd7ce6fdb8858f6083ce43d0e8c586473a44a8",
    "g-minus-t-plus.json": "b9e60ba3fc977503ef489ddd9b377ff02f8b9f70b580c539422f49d88533301d",
    "g-minus-t-minus.json": "58a4b4c053e1496e8824938b574e7773aaa9ad9da6edf1a031d5ff3a0e0282ed",
}
DISAGREEMENTS = {
    ((1, 1), (1, -1)): 7042,
    ((1, 1), (-1, 1)): 7006,
    ((1, 1), (-1, -1)): 6960,
    ((1, -1), (-1, 1)): 6462,
    ((1, -1), (-1, -1)): 6462,
    ((-1, 1), (-1, -1)): 6304,
}


def fail(message):
    raise SystemExit("FAIL: " + message)


def expect(condition, message):
    if not condition:
        fail(message)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def canonical(obj):
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=True)


def evidence_name(g_value, t_value):
    g_name = "plus" if g_value == 1 else "minus"
    t_name = "plus" if t_value == 1 else "minus"
    return f"g-{g_name}-t-{t_name}.json"


def load_predecessor():
    raw = PREDECESSOR.read_bytes()
    expect(sha256_bytes(raw) == PREDECESSOR_SHA256, "predecessor verifier SHA256 changed")
    spec = importlib.util.spec_from_file_location("a1_joint_216_charpoly", PREDECESSOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, raw.decode("utf-8")


def ratrecon(residue, modulus):
    """Unique n/d in lowest terms with n/d ≡ residue and n^2 + d^2 <= modulus/2."""
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

    Pivot column i and pivot row i correspond. The returned row origins are the
    original indices of the pivot rows, in pivot order.
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
            gram[left][right] = total % prime
            gram[right][left] = gram[left][right]
    return det_mod(gram, prime)


def differing_entries(left, right):
    return sum(item != other for row, other_row in zip(left, right) for item, other in zip(row, other_row))


def certify(matrix, sizes):
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
    expect(minor != 0 and minor_two != 0, "the pivot minor vanishes at a working prime")
    expect(rank == rank_two, "two modular ranks disagree")
    # Modular rank is only a lower bound. The integer kernel supplies the
    # matching upper bound, and the nonzero minor is the same lower bound.
    expect(rank == DIMENSION - len(vectors), "kernel corank does not meet the modular lower bound")
    gram = gram_det(vectors, sizes, PRIME)
    gram_two = gram_det(vectors, sizes, PRIME_TWO)
    expect(gram != 0 and gram_two != 0, "the weighted Gram determinant of the kernel vanishes")
    entry_bound = max(abs(entry) for vector in vectors for entry in vector)
    expect(2 * entry_bound * entry_bound < PRIME, "kernel entries are outside the unique reconstruction range")
    nonzero = sum(1 for vector in vectors for entry in vector if entry)
    return {
        "prime": PRIME,
        "second_prime": PRIME_TWO,
        "rational_rank": rank,
        "geometric_multiplicity": DIMENSION - rank,
        "algebraic_multiplicity": DIMENSION - rank,
        "algebraic_multiplicity_source": "ascent",
        "rank_mod_prime": rank,
        "rank_mod_second_prime": rank_two,
        "pivot_rows": pivot_rows,
        "pivot_columns": pivots,
        "free_columns": free,
        "free_diagonal": diagonal,
        "minor_det_mod_prime": minor,
        "minor_det_mod_second_prime": minor_two,
        "gram_det_mod_prime": gram,
        "gram_det_mod_second_prime": gram_two,
        "entry_bound": entry_bound,
        "nonzero_kernel_entries": nonzero,
        "kernel_vectors": vectors,
    }


def payload_for(g_value, t_value, vectors, matrix, sizes, rank_certificate):
    return {
        "eigenvalues": {"H": 1, "g": g_value, "t": t_value},
        "index": "coordinate*512+address",
        "roots": [root for root, _items in vectors],
        "vectors": [[[index, coeff] for index, coeff in items] for _root, items in vectors],
        "support_sizes": sizes,
        "matrix_rows": matrix,
        "rank": rank_certificate,
    }


def build_spaces(module):
    columns, ports = module.load_query()
    port_of, lookup, port_basis, coords = module.prepare(columns, ports)
    group = module.sign_group(port_of, lookup, port_basis, coords, module.C1)
    expect(len(group) == 16, "c=1 sign stabilizer does not have order 16")
    first = module.operator(module.G_INV, module.G_EPS, port_of, lookup, port_basis, coords)
    second = module.operator(module.T_INV, module.T_EPS, port_of, lookup, port_basis, coords)
    expect(first is not None and second is not None, "an explicit splitter is not a symmetry")
    identity = {
        "inv": tuple(range(8)),
        "eps": (1, 1, 1, 1, 1, 1, 1, 1),
        "T": tuple(1 << bit for bit in range(9)),
    }
    expect(module.same_operator(module.compose(first, first), identity), "g is not an involution")
    expect(module.same_operator(module.compose(second, second), identity), "t is not an involution")
    expect(
        module.same_operator(module.compose(first, second), module.compose(second, first)),
        "g and t do not commute",
    )
    actions = [module.action_tables(element) for element in group]
    g_dest, g_sign = module.action_tables(first)
    t_dest, t_sign = module.action_tables(second)
    trivial_dimension, joint_dimension = module.character_joint_dimension(group, (first, second))
    expect(trivial_dimension == 864, "trivial character dimension is not 864")
    expect(joint_dimension == 216, "trace formula does not give a 216-dimensional (+1,+1) space")
    columns_b = module.column_table(columns, ports)
    for dest, sign in actions:
        expect(module.operators_commute(columns_b, dest, sign), "B does not commute with a sign symmetry")
    expect(module.operators_commute(columns_b, g_dest, g_sign), "B does not commute with g")
    expect(module.operators_commute(columns_b, t_dest, t_sign), "B does not commute with t")
    spaces = {}
    for g_value in (1, -1):
        for t_value in (1, -1):
            lattice = module.Lattice()
            for dest, sign in actions:
                lattice.add_operator(dest, sign, 1)
            lattice.add_operator(g_dest, g_sign, g_value)
            lattice.add_operator(t_dest, t_sign, t_value)
            vectors = lattice.basis()
            expect(len(vectors) == DIMENSION, "a joint eigenspace does not have dimension 216")
            for dest, sign in actions:
                for _root, items in vectors:
                    expect(module.fixed_by(dest, sign, items, 1), "a basis vector is not fixed by the sign stabilizer")
            for _root, items in vectors:
                expect(module.fixed_by(g_dest, g_sign, items, g_value), "a basis vector misses the g eigenvalue")
                expect(module.fixed_by(t_dest, t_sign, items, t_value), "a basis vector misses the t eigenvalue")
                expect(items[0][1] == 1, "the least-index coefficient is not +1")
                expect(all(coeff in (-1, 1) for _index, coeff in items), "a basis coefficient is outside ±1")
            matrix, sizes = module.restriction_matrix(columns_b, columns, ports, vectors)
            expect(all(size > 0 for size in sizes), "a basis vector has empty support")
            expect(set(sizes) == {1, 4, 8, 16}, "support sizes are not {1, 4, 8, 16}")
            expect(symmetric_scaling(matrix, sizes), "size_r M_rs is not equal to size_s M_sr")
            expect(max(abs(entry) for row in matrix for entry in row) <= 28, "a matrix entry lies outside -28..28")
            expect(sum(entry != 0 for row in matrix for entry in row) == 3972, "a joint sign matrix changed its nonzero count")
            expect(sum(matrix[index][index] for index in range(DIMENSION)) == 0, "a joint sign matrix has nonzero trace")
            spaces[(g_value, t_value)] = (vectors, matrix, sizes)
    return spaces


def recorded_algebraic_multiplicity(source):
    match = re.search(r"FACTORS = \(\s*\((\d+), \(0, 1\)\)", source)
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
    expect(det_mod([[0, 0], [0, 0]], PRIME) == 0, "a zero matrix had nonzero determinant")
    expect(det_mod([[1, 2], [3, 4]], PRIME) == (1 * 4 - 2 * 3) % PRIME, "a 2-by-2 determinant changed")


def main():
    dump = "--dump-evidence" in sys.argv
    fixture()
    selected_bytes = SELECTED.read_bytes()
    expect(sha256_bytes(selected_bytes) == SELECTED_SHA256, "selected-result SHA256 changed")
    selected = json.loads(selected_bytes)
    expect(selected["kappa"] == SELECTED_KAPPA, "selected kappa changed")
    basis_bytes = BASIS_PATH.read_bytes()
    matrix_bytes = MATRIX_PATH.read_bytes()
    expect(sha256_bytes(basis_bytes) == BASIS_SHA256, "pinned (+1,+1) basis SHA256 changed")
    expect(sha256_bytes(matrix_bytes) == MATRIX_SHA256, "pinned (+1,+1) matrix SHA256 changed")
    pinned_basis = json.loads(basis_bytes)
    pinned_matrix = json.loads(matrix_bytes)["rows"]
    module, predecessor_source = load_predecessor()
    expect(module.FACTORS[0] == (RECORDED_ALGEBRAIC_MULTIPLICITY, (0, 1)), "the recorded factor x^24 changed")
    expect(
        recorded_algebraic_multiplicity(predecessor_source) == RECORDED_ALGEBRAIC_MULTIPLICITY,
        "the recorded characteristic factor x^24 changed",
    )
    spaces = build_spaces(module)
    plus_vectors, plus_matrix, _plus_sizes = spaces[(1, 1)]
    plus_roots = [root for root, _items in plus_vectors]
    plus_basis_vectors = [[[index, coeff] for index, coeff in items] for _root, items in plus_vectors]
    expect(plus_roots == pinned_basis["roots"], "rebuilt (+1,+1) roots do not match the pinned basis")
    expect(plus_basis_vectors == pinned_basis["vectors"], "rebuilt (+1,+1) basis does not match the pin")
    expect(plus_matrix == pinned_matrix, "rebuilt (+1,+1) matrix does not match the pin")
    expect(pinned_basis["eigenvalues"] == {"H": 1, "g": 1, "t": 1}, "pinned basis is not the joint (+1,+1) space")

    certificates = {}
    for g_value, t_value in OTHER_SIGNS:
        vectors, matrix, sizes = spaces[(g_value, t_value)]
        expect(matrix != plus_matrix, "an other sign space reproduced the pinned (+1,+1) matrix")
        rank_certificate = certify(matrix, sizes)
        geometric = rank_certificate["geometric_multiplicity"]
        algebraic = rank_certificate["algebraic_multiplicity"]
        expect(geometric == RECORDED_ALGEBRAIC_MULTIPLICITY, "geometric multiplicity is not 24")
        expect(algebraic == recorded_algebraic_multiplicity(predecessor_source), "ascent multiplicity disagrees with x^24")
        expect(
            geometric == RECORDED_PINNED_GEOMETRIC_MULTIPLICITY,
            "geometric multiplicity disagrees with the multiplicity 24 recorded for the (+1,+1) matrix",
        )
        # The equality algebraic == geometric is the ascent argument in PROOF.md:
        # D M is symmetric, the kernel Gram form is nondegenerate, so ker M
        # meets im M only at 0 and the ascent of eigenvalue 0 is 1.
        expect(algebraic == geometric, "ascent did not equate algebraic and geometric multiplicity")
        certificates[(g_value, t_value)] = payload_for(g_value, t_value, vectors, matrix, sizes, rank_certificate)

    keys = ((1, 1),) + OTHER_SIGNS
    for left_index, left in enumerate(keys):
        for right in keys[left_index + 1 :]:
            count = differing_entries(spaces[left][1], spaces[right][1])
            expect(count == DISAGREEMENTS[(left, right)], "two joint sign matrices changed their entry disagreements")
    for left in OTHER_SIGNS:
        for right in OTHER_SIGNS:
            if left == right:
                continue
            expect(
                not annihilates(spaces[right][1], certificates[left]["rank"]["kernel_vectors"]),
                "a kernel of one sign space is annihilated by another sign matrix",
            )

    if dump:
        EVIDENCE.mkdir(parents=True, exist_ok=True)
    for g_value, t_value in OTHER_SIGNS:
        name = evidence_name(g_value, t_value)
        path = EVIDENCE / name
        text = canonical(certificates[(g_value, t_value)]) + "\n"
        digest = sha256_bytes(text.encode("utf-8"))
        if dump:
            path.write_text(text, encoding="utf-8")
            print("evidence", name, digest)
        else:
            expect(path.read_text(encoding="utf-8") == text, "pinned sign-space certificate does not match the recomputation")
            expect(sha256_bytes(path.read_bytes()) == EVIDENCE_SHA256[name], "pinned sign-space SHA256 changed")
            expect(digest == EVIDENCE_SHA256[name], "recomputed certificate SHA256 changed")

    replaced = predecessor_source.replace("(24, (0, 1))", "(23, (0, 1))", 1)
    expect(recorded_algebraic_multiplicity(replaced) == 23, "the multiplicity parser missed a changed factor")
    expect(recorded_algebraic_multiplicity(replaced) != RECORDED_ALGEBRAIC_MULTIPLICITY, "a changed recorded factor still matched")
    for g_value, t_value in OTHER_SIGNS:
        vectors, matrix, sizes = spaces[(g_value, t_value)]
        kernel = certificates[(g_value, t_value)]["rank"]["kernel_vectors"]
        free = certificates[(g_value, t_value)]["rank"]["free_columns"]
        pivot_rows = certificates[(g_value, t_value)]["rank"]["pivot_rows"]
        pivot_columns = certificates[(g_value, t_value)]["rank"]["pivot_columns"]
        shifted = [row[:] for row in matrix]
        for index in range(DIMENSION):
            shifted[index][index] += 1
        expect(not annihilates(shifted, kernel), "adding the identity still annihilated a kernel")
        broken = [row[:] for row in matrix]
        broken[0][1] += 1
        expect(not symmetric_scaling(broken, sizes), "an off-diagonal increment still satisfied the scaling identity")
        zeroed = [vector[:] for vector in kernel]
        zeroed[0] = [0] * DIMENSION
        zero_diagonal = free_diagonal(zeroed, free)
        expect(zero_diagonal is None or zero_diagonal[0] == 0, "a zero kernel vector still had a positive free diagonal")
        repeated = [row[:] for row in matrix]
        repeated[pivot_rows[0]] = repeated[pivot_rows[1]][:]
        expect(minor_det(repeated, pivot_rows, pivot_columns, PRIME) == 0, "a repeated pivot row still had a nonzero minor")

    print("PASS_A1_JOINT_216_OTHER_NULLITY")
    print("evidence class: proof for each of the three pinned matrices")
    print("selected kappa", SELECTED_KAPPA)
    for g_value, t_value in OTHER_SIGNS:
        rank = certificates[(g_value, t_value)]["rank"]
        print(
            "sign",
            (g_value, t_value),
            "rational rank",
            rank["rational_rank"],
            "geometric",
            rank["geometric_multiplicity"],
            "algebraic",
            rank["algebraic_multiplicity"],
            "entry bound",
            rank["entry_bound"],
            "minor",
            rank["minor_det_mod_prime"],
            rank["minor_det_mod_second_prime"],
            "gram",
            rank["gram_det_mod_prime"],
            rank["gram_det_mod_second_prime"],
            "nonzero kernel entries",
            rank["nonzero_kernel_entries"],
        )
        print("free diagonal", rank["free_diagonal"])


if __name__ == "__main__":
    main()
