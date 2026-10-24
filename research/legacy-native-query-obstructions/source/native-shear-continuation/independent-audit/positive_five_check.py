"""Check the subset products and algebraic identities in the positive proof."""

from fractions import Fraction as F
from hashlib import sha256
from itertools import permutations, product
from pathlib import Path
import json


HERE = Path(__file__).resolve().parent
I2 = (F(1), F(0), F(0), F(1))
Z = tuple(-value for value in I2)
A = tuple(map(F, (1, 2, 0, 1)))
B = tuple(map(F, (1, 0, -2, 1)))
C = tuple(map(F, (3, 2, -2, -1)))


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def multiply(a, b):
    return tuple(sum(a[2 * i + k] * b[2 * k + j] for k in range(2))
                 for i in range(2) for j in range(2))


def det(a):
    return a[0] * a[3] - a[1] * a[2]


def inverse(a):
    return tuple(value / det(a) for value in (a[3], -a[1], -a[2], a[0]))


def binary_multiply(a, b):
    return tuple(sum(a[3 * i + k] * b[3 * k + j] for k in range(3)) % 2
                 for i in range(3) for j in range(3))


def outer(a, b):
    return tuple(x * y for x in a for y in b)


def binary_rank(matrix):
    rows = [list(matrix[3 * i:3 * i + 3]) for i in range(3)]
    count = 0
    for column in range(3):
        pivot = next((i for i in range(count, 3) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[count], rows[pivot] = rows[pivot], rows[count]
        for i in range(3):
            if i != count and rows[i][column]:
                rows[i] = [x ^ y for x, y in zip(rows[i], rows[count])]
        count += 1
    return count


def subset_records(form):
    records = []
    for selected in product((False, True), repeat=5):
        address = I2
        for g, bit in zip(form, selected):
            if bit:
                address = multiply(g, address)
        records.append({"subset": "".join(str(i + 1) for i, bit in enumerate(selected) if bit),
                        "product": list(map(str, address)), "target": address == Z})
    return records


# Each monomial is a word in the five noncommuting projector symbols.
def nc_add(*polynomials):
    answer = set()
    for polynomial in polynomials:
        answer.symmetric_difference_update(polynomial)
    return answer


def nc_multiply(a, b):
    answer = set()
    for left in a:
        for right in b:
            word = left + right
            answer.symmetric_difference_update({word})
    return answer


def nc_chain(*factors):
    answer = {()}
    for factor in factors:
        answer = nc_multiply(answer, factor)
    return answer


def branch_polynomial(subset):
    return nc_chain(*({(i,)} if str(i) in subset else {(), (i,)}
                      for i in range(5, 0, -1)))


# The following polynomials are in Q[s].
def polynomial(*values):
    values = list(map(F, values))
    while values and values[-1] == 0:
        values.pop()
    return tuple(values)


def polynomial_sum(*values):
    answer = [F(0)] * max((len(value) for value in values), default=0)
    for value in values:
        for i, coefficient in enumerate(value):
            answer[i] += coefficient
    return polynomial(*answer)


def polynomial_product(a, b):
    answer = [F(0)] * max(0, len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            answer[i + j] += x * y
    return polynomial(*answer)


def polynomial_matrix_product(a, b):
    return tuple(polynomial_sum(*(polynomial_product(a[2 * i + k], b[2 * k + j])
                                  for k in range(2)))
                 for i in range(2) for j in range(2))


def binary_polynomial_product(a, b):
    answer = 0
    while b:
        if b & 1:
            answer ^= a
        b >>= 1
        a <<= 1
    return answer


def commutative_binary_determinant(matrix):
    answer = 0
    for order in permutations(range(3)):
        term = 1
        for i, j in enumerate(order):
            term = binary_polynomial_product(term, matrix[3 * i + j])
        answer ^= term
    return answer


def main():
    require(det(Z) == 1, "The plane endpoint has the wrong determinant.")
    require(commutative_binary_determinant((1, 0, 0, 0, 1, 0, 0, 0, 1)) == 1,
            "The determinant quotient endpoint is not one.")
    require(multiply(C, multiply(B, A)) == Z, "The canonical triple does not reach z.")
    D = multiply(C, multiply(B, inverse(C)))
    forms = [(A, B, C, A, B), (A, B, C, D, A)]
    require(all(g != I2 and det(g) == 1 and g[0] + g[3] == 2
                for form in forms for g in form), "A canonical map is not a nonidentity unipotent.")
    records = [subset_records(form) for form in forms]
    targets = [sorted(record["subset"] for record in form if record["target"])
               for form in records]
    require(targets == [["123", "234", "345"], ["123", "134", "235", "345"]],
            "The target subset lists differ.")
    inverse_c = list(map(str, inverse(C)))
    full_address_subsets = [record["subset"] for record in records[0]
                           if record["product"] == inverse_c]
    require(full_address_subsets == ["12345"], "The full-word address is not unique.")
    require(inverse(C) != Z, "The full-word address equals z.")

    n = {i: {(i,)} for i in range(1, 6)}
    q = {i: {(), (i,)} for i in range(1, 6)}
    first_terms = [nc_chain(q[5], q[4], n[3], n[2], n[1]),
                   nc_chain(q[5], n[4], n[3], n[2], q[1]),
                   nc_chain(n[5], n[4], n[3], q[2], q[1])]
    require(nc_add(*(branch_polynomial(s) for s in targets[0])) == nc_add(*first_terms),
            "The first target coefficient formula differs.")
    middle = nc_add(nc_chain(q[4], n[3], n[2]), nc_chain(n[4], n[3], q[2]))
    left_term = nc_chain(q[5], middle, n[1])
    right_term = nc_chain(n[5], middle, q[1])
    require(nc_add(*(branch_polynomial(s) for s in targets[1])) == nc_add(left_term, right_term),
            "The second target coefficient does not factor.")
    require(all(word[-1] == 1 for word in left_term)
            and all(word[0] == 5 for word in right_term), "The rank-one factors were lost.")

    vectors = list(product((0, 1), repeat=3))
    projectors = [(a, b, outer(a, b)) for a in vectors for b in vectors
                  if any(a) and any(b) and sum(x * y for x, y in zip(a, b)) % 2]
    require(len(projectors) == 28, "The projector pool has the wrong size.")
    for a, b, matrix in projectors:
        require(binary_rank(matrix) == 1 and binary_multiply(matrix, matrix) == matrix,
                "A role projector has the wrong rank or square.")
        query = tuple((int(i == j) ^ matrix[3 * i + j]) | (matrix[3 * i + j] << 1)
                      for i in range(3) for j in range(3))
        require(commutative_binary_determinant(query) == 2,
                "The determinant of I+N(x-1) is not x.")
    for a, b, first in projectors:
        for c, d, second in projectors:
            coupling = sum(x * y for x, y in zip(d, a)) % 2
            expected = tuple(coupling * value for value in outer(c, b))
            require(binary_multiply(second, first) == expected,
                    "A rank-one coupling factorization differs.")
    scalar_witnesses = []
    for x21, x32, x43, x54 in product((0, 1), repeat=4):
        if x21 * x32 and x43 * x54:
            require(x21 * x32 * x43 * x54 == 1, "The full selected coefficient can vanish.")
            scalar_witnesses.append([x21, x32, x43, x54])
    for a, b, c, d in product(vectors, repeat=4):
        matrix = tuple(x ^ y for x, y in zip(outer(a, b), outer(c, d)))
        require(binary_rank(matrix) <= 2, "Two outer products have rank three.")

    zero, one = polynomial(), polynomial(1)
    param_b = (polynomial(1, 1), polynomial(0, 0, F(1, 2)), polynomial(-2), polynomial(1, -1))
    param_c = (polynomial(3, 1), polynomial(2, 2, F(1, 2)), polynomial(-2), polynomial(-1, -1))
    shear = (one, polynomial(0, F(-1, 2)), zero, one)
    shear_inverse = (one, polynomial(0, F(1, 2)), zero, one)
    const = lambda matrix: tuple(polynomial(value) for value in matrix)
    require(polynomial_matrix_product(shear_inverse, polynomial_matrix_product(param_b, shear)) == const(B),
            "The rational shear does not normalize B.")
    require(polynomial_matrix_product(shear_inverse, polynomial_matrix_product(param_c, shear)) == const(C),
            "The rational shear does not normalize C.")
    require(polynomial_matrix_product(shear_inverse, polynomial_matrix_product(const(A), shear)) == const(A),
            "The rational shear does not preserve A.")
    require(polynomial_matrix_product(param_c, polynomial_matrix_product(param_b, const(A))) == const(Z),
            "The parameterized triple relation differs.")

    result = {
        "status": "EXACT_SUBSET_AND_ALGEBRAIC_WITNESSES_PASS",
        "method": "Standalone standard-library checks. No search module is imported.",
        "canonical_maps": {name: list(map(str, value)) for name, value in zip("ABCD", (A, B, C, D))},
        "forms": [{"name": name, "target_subsets": target, "subsets": subset}
                  for name, target, subset in zip(("A,B,C,A,B", "A,B,C,CBC^-1,A"), targets, records)],
        "first_form_full_address": inverse_c, "first_form_full_address_subsets": full_address_subsets,
        "free_associative_coefficient_identities": True,
        "first_form_scalar_coupling_assignments": 16,
        "first_form_required_couplings": scalar_witnesses,
        "rank_one_pair_factorizations": len(projectors) ** 2,
        "rank_two_outer_sum_assignments": len(vectors) ** 4,
        "commutative_char2_query_determinants": len(projectors),
        "endpoint_after_determinant_map": "I3; determinant one",
        "rational_common_shear_identities_in_Q_s": True,
        "backup_search_repeated": False,
        "scope": "Algebraic witnesses for the proof on three complete roles in the formal group algebra.",
        "script_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "proof_sha256": sha256((HERE.parent / "POSITIVE-FIVE-PROOF.md").read_bytes()).hexdigest(),
    }
    (HERE / "POSITIVE-FIVE-RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key not in ("forms", "canonical_maps")}, indent=2))


if __name__ == "__main__":
    main()
