"""Finite exact word enumeration for the order-21 semilinear mixed tariff.

Implemented by OpenAI Codex at Krzysztof Wojt's request, 2026-10-23.  This is
finite computational corroboration in the full formal group algebra, not an
independent human review or a proof beyond the enumerated dimensions/word
length.

Apache-2.0. Separately implemented supporting checker; inspected and integrated
by the primary Codex agent.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from itertools import product
import json


Element = tuple[int, int]
Matrix = tuple[int, ...]  # Rows, each encoded as an r-bit integer.
AlgebraMatrix = dict[int, Matrix]


def require(condition: bool, message: str) -> None:
    """Raise in normal and optimized Python alike when a check fails."""
    if not condition:
        raise RuntimeError(message)


ELEMENTS: tuple[Element, ...] = tuple((i, j) for i in range(7) for j in range(3))
ELEMENT_INDEX = {g: i for i, g in enumerate(ELEMENTS)}
IDENTITY = (0, 0)
IDENTITY_INDEX = ELEMENT_INDEX[IDENTITY]


def group_product(a: Element, b: Element) -> Element:
    """Multiply (i,j)(k,l)=(i+2^j k mod 7,j+l mod 3)."""
    i, j = a
    k, ell = b
    return ((i + pow(2, j, 7) * k) % 7, (j + ell) % 3)


GROUP_TABLE: tuple[tuple[int, ...], ...] = tuple(
    tuple(ELEMENT_INDEX[group_product(a, b)] for b in ELEMENTS)
    for a in ELEMENTS
)


def valid_group_table(table: tuple[tuple[int, ...], ...] | list[list[int]]) -> bool:
    """Check identity and associativity for a finite multiplication table."""
    size = len(table)
    if size == 0 or any(len(row) != size for row in table):
        return False
    if any(not (0 <= table[a][b] < size) for a in range(size) for b in range(size)):
        return False
    if any(table[IDENTITY_INDEX][a] != a or table[a][IDENTITY_INDEX] != a for a in range(size)):
        return False
    return all(
        table[table[a][b]][c] == table[a][table[b][c]]
        for a in range(size)
        for b in range(size)
        for c in range(size)
    )


def zero_matrix(r: int) -> Matrix:
    return (0,) * r


def identity_matrix(r: int) -> Matrix:
    return tuple(1 << row for row in range(r))


def matrix_xor(a: Matrix, b: Matrix) -> Matrix:
    return tuple(x ^ y for x, y in zip(a, b))


@lru_cache(maxsize=None)
def matrix_product(a: Matrix, b: Matrix) -> Matrix:
    """Multiply binary matrices represented by row bitmasks."""
    out: list[int] = []
    for row in a:
        value = 0
        remaining = row
        while remaining:
            bit = remaining & -remaining
            column = bit.bit_length() - 1
            value ^= b[column]
            remaining ^= bit
        out.append(value)
    return tuple(out)


def rank_one_idempotents(r: int) -> tuple[tuple[int, int, Matrix], ...]:
    """Enumerate N=xy^T with nonzero x,y and y^T x=1 over F2."""
    result: list[tuple[int, int, Matrix]] = []
    for x in range(1, 1 << r):
        for y in range(1, 1 << r):
            if bin(x & y).count("1") % 2 != 1:
                continue
            matrix = tuple(y if (x >> row) & 1 else 0 for row in range(r))
            require(matrix_product(matrix, matrix) == matrix, "generated matrix is not idempotent")
            result.append((x, y, matrix))
    return tuple(result)


def add_coefficient(coefficients: AlgebraMatrix, group_index: int, matrix: Matrix) -> None:
    old = coefficients.get(group_index)
    coefficients[group_index] = matrix if old is None else matrix_xor(old, matrix)


def factor_coefficients(r: int, g: Element, n: Matrix) -> AlgebraMatrix:
    """Coefficients of D_N(g)=I+([g]+[1])N in M_r(F2[G])."""
    coefficients: AlgebraMatrix = {}
    add_coefficient(coefficients, IDENTITY_INDEX, matrix_xor(identity_matrix(r), n))
    add_coefficient(coefficients, ELEMENT_INDEX[g], n)
    return coefficients


def normalized_signature(coefficients: AlgebraMatrix) -> tuple[tuple[int, Matrix], ...]:
    return tuple(
        (group_index, matrix)
        for group_index, matrix in sorted(coefficients.items())
        if any(matrix)
    )


def algebra_matrix_product(
    a: AlgebraMatrix,
    b: AlgebraMatrix,
    table: tuple[tuple[int, ...], ...] | list[list[int]] = GROUP_TABLE,
) -> AlgebraMatrix:
    """Full formal group-algebra matrix product, with coefficient XOR."""
    out: AlgebraMatrix = {}
    for ga, ma in a.items():
        for gb, mb in b.items():
            group_index = table[ga][gb]
            add_coefficient(out, group_index, matrix_product(ma, mb))
    return {g: m for g, m in out.items() if any(m)}


def scalar_coefficients(matrix: Matrix) -> AlgebraMatrix:
    """Embed a binary scalar matrix as the identity-group coefficient."""
    return {IDENTITY_INDEX: matrix}


def apply_algebra_to_vector(
    coefficients: AlgebraMatrix,
    vector: int,
    table: tuple[tuple[int, ...], ...] | list[list[int]] = GROUP_TABLE,
) -> int:
    """Apply M_r(F2[G]) to a packed vector in the left regular module."""
    out = 0
    remaining = vector
    while remaining:
        bit = remaining & -remaining
        input_index = bit.bit_length() - 1
        input_role, input_group = divmod(input_index, len(ELEMENTS))
        for group_index, matrix in coefficients.items():
            output_group = table[group_index][input_group]
            for output_role, row in enumerate(matrix):
                if (row >> input_role) & 1:
                    output_index = output_role * len(ELEMENTS) + output_group
                    out ^= 1 << output_index
        remaining ^= bit
    return out


def inverse_binary_matrix(matrix: Matrix) -> Matrix:
    """Invert a square binary matrix by exact Gauss-Jordan elimination."""
    r = len(matrix)
    augmented = [matrix[row] | (1 << (r + row)) for row in range(r)]
    for column in range(r):
        pivot = next((row for row in range(column, r) if (augmented[row] >> column) & 1), None)
        require(pivot is not None, "scalar matrix is singular")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        for row in range(r):
            if row != column and ((augmented[row] >> column) & 1):
                augmented[row] ^= augmented[column]
    left_mask = (1 << r) - 1
    require(all((row & left_mask) == (1 << i) for i, row in enumerate(augmented)), "scalar inverse elimination failed")
    return tuple(row >> r for row in augmented)


def target_coefficients(r: int, roles: tuple[int, int], labels: tuple[Element, Element]) -> AlgebraMatrix:
    """Literal diagonal monomial target, with identity on every dirty role."""
    coefficients: AlgebraMatrix = {}
    targeted = dict(zip(roles, labels))
    for role in range(r):
        label = targeted.get(role, IDENTITY)
        diagonal_unit = tuple((1 << role) if row == role else 0 for row in range(r))
        add_coefficient(coefficients, ELEMENT_INDEX[label], diagonal_unit)
    return {g: m for g, m in coefficients.items() if any(m)}


def label_kind(g: Element) -> str:
    return "normal" if g[1] == 0 else "outside"


def endpoint_class(labels: tuple[Element, Element]) -> str:
    left, right = (label_kind(g) for g in labels)
    return "mixed" if left != right else f"homogeneous_{left}"


def factor_is_rigid(
    factor: tuple[Element, int, int, Matrix],
    roles: tuple[int, int],
    labels: tuple[Element, Element],
) -> bool:
    """Require both x and y to avoid dirty roles and opposite-type targets."""
    g, x, y, _matrix = factor
    kind = label_kind(g)
    allowed = 0
    for role, label in zip(roles, labels):
        if label_kind(label) == kind:
            allowed |= 1 << role
    return (x & ~allowed) == 0 and (y & ~allowed) == 0


def noncoordinate_control(r: int) -> None:
    """Check complementary noncoordinate idempotents realize diag([g],[g])."""
    require(r >= 2, "noncoordinate control needs two target roles")
    g = (1, 0)
    # In the first 2x2 block, N=[[1,1],[0,0]] and M=I+N=[[0,1],[0,1]].
    # Their decompositions are x y^T with (x,y)=(01,11),(11,10) in bit order.
    n = (0b11, 0) + (0,) * (r - 2)
    m = (0b10, 0b10) + (0,) * (r - 2)
    require(matrix_product(n, n) == n and matrix_product(m, m) == m, "control idempotents invalid")
    require(matrix_xor(n, m) == tuple(0b01 << row for row in range(2)) + (0,) * (r - 2), "control N+M mismatch")
    require(matrix_product(n, m) == zero_matrix(r), "control idempotents are not complementary")
    word = algebra_matrix_product(factor_coefficients(r, g, n), factor_coefficients(r, g, m))
    target = target_coefficients(r, (0, 1), (g, g))
    require(normalized_signature(word) == normalized_signature(target), "noncoordinate equal-label word failed")
    require((n[0] & 0b10) != 0 and (m[0] & 0b10) != 0, "control accidentally coordinate-only")


def arbitrary_dirty_basis_replay() -> dict[str, object]:
    """Replay a mixed four-call word on every basis vector of F2[G]^5."""
    r = 5
    # Dense invertible circulant matrix; every row and column has weight 3.
    scalar = (0b00111, 0b01110, 0b11100, 0b11001, 0b10011)
    scalar_inverse = inverse_binary_matrix(scalar)
    require(matrix_product(scalar, scalar_inverse) == identity_matrix(r), "S*S^-1 is not identity")
    require(matrix_product(scalar_inverse, scalar) == identity_matrix(r), "S^-1*S is not identity")
    require(all(bin(row).count("1") > 1 for row in scalar), "S is not role-mixing")
    require(all(bin(row).count("1") > 1 for row in scalar_inverse), "S^-1 is not role-mixing")
    require(
        all(sum((scalar[row] >> column) & 1 for row in range(r)) > 1 for column in range(r)),
        "S has an unmixed input role",
    )
    require(
        all(sum((scalar_inverse[row] >> column) & 1 for row in range(r)) > 1 for column in range(r)),
        "S^-1 has an unmixed input role",
    )

    labels = ((1, 0), (2, 1), (3, 2), (4, 0), IDENTITY)
    scalar_op = scalar_coefficients(scalar)
    inverse_op = scalar_coefficients(scalar_inverse)
    paid_ops: list[AlgebraMatrix] = []
    for role, label in enumerate(labels[:4]):
        coordinate = tuple((1 << role) if row == role else 0 for row in range(r))
        conjugated = matrix_product(matrix_product(scalar_inverse, coordinate), scalar)
        x = sum(1 << row for row in range(r) if (scalar_inverse[row] >> role) & 1)
        y = scalar[role]
        factorization = tuple(y if (x >> row) & 1 else 0 for row in range(r))
        require(factorization == conjugated, "conjugated paid idempotent factorization mismatch")
        require(matrix_product(conjugated, conjugated) == conjugated, "conjugated paid matrix is not idempotent")
        paid_ops.append(factor_coefficients(r, label, conjugated))

    # As a matrix word this is S D_0 D_1 D_2 D_3 S^-1.  The paid
    # idempotents are S^-1 E_ii S, so conjugation leaves the exact diagonal
    # endpoint; the surrounding free maps do mix the dirty fifth role.
    operators = [scalar_op, *paid_ops, inverse_op]

    def replay(input_vector: int, ops: list[AlgebraMatrix]) -> int:
        value = input_vector
        for operator in reversed(ops):
            value = apply_algebra_to_vector(operator, value)
        return value

    basis_count = r * len(ELEMENTS)
    mismatches = 0
    dirty_restored = 0
    inputs_by_role = [0] * r
    for input_index in range(basis_count):
        role, group_index = divmod(input_index, len(ELEMENTS))
        input_vector = 1 << input_index
        inputs_by_role[role] += 1
        actual = replay(input_vector, operators)
        endpoint_label = labels[role]
        output_group = GROUP_TABLE[ELEMENT_INDEX[endpoint_label]][group_index]
        expected = 1 << (role * len(ELEMENTS) + output_group)
        if actual != expected:
            mismatches += 1
        if role == r - 1 and actual == input_vector:
            dirty_restored += 1
    require(mismatches == 0, f"regular-action basis replay has {mismatches} endpoint mismatches")
    require(dirty_restored == len(ELEMENTS), "dirty role was not restored on every group basis state")

    # Check free-map inverse restoration alone on every basis input.
    inverse_cancellation_mismatches = sum(
        replay(1 << input_index, [scalar_op, inverse_op]) != (1 << input_index)
        for input_index in range(basis_count)
    )
    require(inverse_cancellation_mismatches == 0, "free S/S^-1 restoration failed")

    dirty_basis = 1 << ((r - 1) * len(ELEMENTS) + IDENTITY_INDEX)
    mixed_dirty = apply_algebra_to_vector(scalar_op, dirty_basis)
    mixed_dirty_roles = {
        index // len(ELEMENTS)
        for index in range(basis_count)
        if (mixed_dirty >> index) & 1
    }
    require(len(mixed_dirty_roles) > 1 and r - 1 in mixed_dirty_roles, "S did not mix the dirty role")

    # Mutate one paid label while preserving the free maps and idempotents.
    mutated_labels = ((5, 0), labels[1], labels[2], labels[3], IDENTITY)
    mutated_paid_ops = list(paid_ops)
    first_role = 0
    first_coordinate = tuple((1 << first_role) if row == first_role else 0 for row in range(r))
    first_conjugated = matrix_product(matrix_product(scalar_inverse, first_coordinate), scalar)
    mutated_paid_ops[0] = factor_coefficients(r, mutated_labels[0], first_conjugated)
    mutated_operators = [scalar_op, *mutated_paid_ops, inverse_op]
    mutation_mismatches = 0
    for input_index in range(basis_count):
        role, group_index = divmod(input_index, len(ELEMENTS))
        expected_label = labels[role]
        output_group = GROUP_TABLE[ELEMENT_INDEX[expected_label]][group_index]
        expected = 1 << (role * len(ELEMENTS) + output_group)
        if replay(1 << input_index, mutated_operators) != expected:
            mutation_mismatches += 1
    require(mutation_mismatches > 0, "mutated paid label escaped basis comparison")

    return {
        "registers": r,
        "basis_inputs_checked": basis_count,
        "basis_inputs_by_role": inputs_by_role,
        "endpoint_mismatches": mismatches,
        "dirty_group_basis_inputs_restored": dirty_restored,
        "inverse_cancellation_basis_mismatches": inverse_cancellation_mismatches,
        "dirty_role_mixed_by_S": sorted(mixed_dirty_roles),
        "mutated_paid_label_basis_mismatches": mutation_mismatches,
        "endpoint_labels": [list(label) for label in labels],
    }


def negative_controls(r: int) -> dict[str, bool]:
    """Exercise mutation detectors independently of the enumerated result."""
    # A valid semidirect product is noncommutative; this catches direct-product
    # or wrong-action substitutions before the word enumeration starts.
    require(group_product((0, 1), (1, 0)) == (2, 1), "semidirect action product wrong")
    require(group_product((1, 0), (0, 1)) == (1, 1), "reverse product wrong")
    require(group_product((0, 1), (1, 0)) != group_product((1, 0), (0, 1)), "group control lost noncommutativity")
    require(valid_group_table(GROUP_TABLE), "constructed multiplication table is invalid")
    corrupted = [list(row) for row in GROUP_TABLE]
    corrupted[1][1] = (corrupted[1][1] + 1) % len(ELEMENTS)
    require(not valid_group_table(corrupted), "corrupted multiplication table escaped detection")

    g, h = (1, 0), (2, 1)
    n = tuple(1 if row == 0 else 0 for row in range(r))
    m = tuple((1 << 1) if row == 1 else 0 for row in range(r))
    first = factor_coefficients(r, g, n)
    second = factor_coefficients(r, h, m)
    target = target_coefficients(r, (0, 1), (g, h))
    require(normalized_signature(algebra_matrix_product(first, second)) == normalized_signature(target), "coordinate control word failed")

    # Dropping either summand ([g]N or [1]N) changes the target word.
    dropped_g = dict(first)
    dropped_g.pop(ELEMENT_INDEX[g])
    dropped_identity = dict(first)
    dropped_identity[IDENTITY_INDEX] = identity_matrix(r)
    require(normalized_signature(algebra_matrix_product(dropped_g, second)) != normalized_signature(target), "dropped [g]N term escaped detection")
    require(normalized_signature(algebra_matrix_product(dropped_identity, second)) != normalized_signature(target), "dropped [1]N term escaped detection")

    # The support detector must reject a rank-one factor on a dirty role.
    dirty = tuple(1 << row if row == r - 1 else 0 for row in range(r))
    dirty_factor = (g, 1 << (r - 1), 1 << (r - 1), dirty)
    require(not factor_is_rigid(dirty_factor, (0, 1), (g, h)), "dirty-role support escaped detection")

    wrong_target = target_coefficients(r, (0, 1), (g, (3, 1)))
    require(normalized_signature(algebra_matrix_product(first, second)) != normalized_signature(wrong_target), "deliberate wrong target escaped detection")
    return {
        "corrupted_multiplication_detected": True,
        "dropped_factor_terms_detected": True,
        "forbidden_dirty_support_detected": True,
        "wrong_target_detected": True,
    }


def enumerate_dimension(r: int) -> dict[str, object]:
    idempotents = rank_one_idempotents(r)
    nonidentity = tuple(g for g in ELEMENTS if g != IDENTITY)
    factors: list[tuple[Element, int, int, Matrix, AlgebraMatrix]] = []
    for g in nonidentity:
        for x, y, n in idempotents:
            factors.append((g, x, y, n, factor_coefficients(r, g, n)))

    targets: dict[tuple[tuple[int, Matrix], ...], tuple[tuple[int, int], tuple[Element, Element]]] = {}
    endpoints_by_class: Counter[str] = Counter()
    roles_list = tuple((i, j) for i in range(r) for j in range(i + 1, r))
    for roles in roles_list:
        for labels in product(nonidentity, repeat=2):
            labels_pair = (labels[0], labels[1])
            endpoint = normalized_signature(target_coefficients(r, roles, labels_pair))
            require(endpoint not in targets, "duplicate literal target encoding")
            targets[endpoint] = (roles, labels_pair)
            endpoints_by_class[endpoint_class(labels_pair)] += 1

    word_counts: Counter[str] = Counter()
    rigidity_violations: Counter[str] = Counter()
    first_violation: list[dict[str, object]] = []
    counts_by_endpoint: Counter[tuple[tuple[int, Matrix], ...]] = Counter()

    for g1, x1, y1, n1, coeffs1 in factors:
        for g2, x2, y2, n2, coeffs2 in factors:
            word = normalized_signature(algebra_matrix_product(coeffs1, coeffs2))
            endpoint = targets.get(word)
            if endpoint is None:
                continue
            roles, labels = endpoint
            cls = endpoint_class(labels)
            target_type_counts = Counter(label_kind(label) for label in labels)
            paid_type_counts = Counter(label_kind(g) for g in (g1, g2))
            require(
                paid_type_counts == target_type_counts,
                f"matched word has wrong paid-label type counts: {paid_type_counts} != {target_type_counts}",
            )
            word_counts[cls] += 1
            counts_by_endpoint[word] += 1
            first_factor = (g1, x1, y1, n1)
            second_factor = (g2, x2, y2, n2)
            if not factor_is_rigid(first_factor, roles, labels) or not factor_is_rigid(second_factor, roles, labels):
                rigidity_violations[cls] += 1
                if len(first_violation) < 3:
                    first_violation.append({
                        "factor_labels": [list(g1), list(g2)],
                        "factor_x": [x1, x2],
                        "factor_y": [y1, y2],
                        "target_roles": list(roles),
                        "target_labels": [list(labels[0]), list(labels[1])],
                    })

    require(all(counts_by_endpoint[target] > 0 for target in targets), "some two-target endpoint lacks a length-two word")
    require(
        sum(rigidity_violations.values()) == 0,
        "enumerated realizing word violates type-restricted target support: "
        + json.dumps(first_violation, sort_keys=True),
    )
    total_words = len(factors) ** 2
    expected_idempotents = {2: 6, 3: 28}.get(r)
    require(expected_idempotents is not None and len(idempotents) == expected_idempotents, "unexpected idempotent inventory size")
    expected_endpoints = (r * (r - 1) // 2) * (len(nonidentity) ** 2)
    require(len(targets) == expected_endpoints, "unexpected endpoint inventory size")

    return {
        "registers": r,
        "rank_one_idempotents": len(idempotents),
        "paid_factors": len(factors),
        "ordered_length_two_words": total_words,
        "literal_two_target_endpoints": len(targets),
        "endpoint_counts": dict(sorted(endpoints_by_class.items())),
        "realizable_endpoints": len(counts_by_endpoint),
        "matching_ordered_words": sum(word_counts.values()),
        "matching_words_by_class": dict(sorted(word_counts.items())),
        "max_words_for_one_endpoint": max(counts_by_endpoint.values()),
        "rigidity_violation_words": sum(rigidity_violations.values()),
        "rigidity_violations_by_class": dict(sorted(rigidity_violations.items())),
        "first_rigidity_violations": first_violation,
    }


def run_checks() -> dict[str, object]:
    """Run exact full-algebra enumeration and deterministic negative controls."""
    require(valid_group_table(GROUP_TABLE), "group multiplication table failed validation")
    noncoordinate_control(2)
    noncoordinate_control(3)
    return {
        "group_order": len(ELEMENTS),
        "group_noncommutative_control": True,
        "noncoordinate_equal_label_control": True,
        "negative_controls": negative_controls(3),
        "regular_action_basis_replay": arbitrary_dirty_basis_replay(),
        "dimensions": [enumerate_dimension(2), enumerate_dimension(3)],
    }


if __name__ == "__main__":
    print(json.dumps(run_checks(), sort_keys=True, indent=2))
