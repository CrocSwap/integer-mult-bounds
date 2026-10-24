#!/usr/bin/env python3
"""Exact finite check for the proposed A5 semisimple quotient.

This is deliberately self-contained: it uses only Python's standard library,
represents F2/F4 and finite group-algebra elements by small integers, and uses
explicit runtime checks rather than ``assert`` (so ``python -O`` is equivalent).

The output certifies only the computations it performs: the combined action
map has rank 25, its kernel is a two-sided ideal, and the computed powers of
that ideal reach zero.
"""

from __future__ import annotations

import hashlib
import json
from collections import deque
from itertools import permutations
from typing import Callable, Iterable, Sequence


class CheckFailure(RuntimeError):
    """Raised when an exact finite check does not meet its expected result."""


Permutation = tuple[int, int, int, int, int]
F4Matrix = tuple[tuple[int, int], tuple[int, int]]
BinaryMatrix = tuple[int, ...]  # row masks, least significant bit is column 0


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def compose(p: Permutation, q: Permutation) -> Permutation:
    """Return p*q = p after q, matching left column-vector actions."""
    return tuple(p[q[i]] for i in range(5))  # type: ignore[return-value]


def permutation_parity(p: Permutation) -> int:
    inversions = sum(p[i] > p[j] for i in range(5) for j in range(i + 1, 5))
    return inversions & 1


IDENTITY_PERM: Permutation = (0, 1, 2, 3, 4)
X_PERM: Permutation = (1, 0, 3, 2, 4)  # (12)(34)
Y_PERM: Permutation = (2, 1, 4, 3, 0)  # (135)


def f4_add(a: int, b: int) -> int:
    return a ^ b


def f4_mul(a: int, b: int) -> int:
    """Multiply codes a,b in F2[w]/(w^2+w+1), with w=2 and w^2=3."""
    product = 0
    for i in range(2):
        if (a >> i) & 1:
            for j in range(2):
                if (b >> j) & 1:
                    degree = i + j
                    product ^= (1 << degree) if degree < 2 else 3
    return product


def f4_matrix_mul(a: F4Matrix, b: F4Matrix) -> F4Matrix:
    return tuple(
        tuple(
            f4_add(f4_mul(a[i][0], b[0][j]), f4_mul(a[i][1], b[1][j]))
            for j in range(2)
        )
        for i in range(2)
    )  # type: ignore[return-value]


F4_IDENTITY: F4Matrix = ((1, 0), (0, 1))
X_F4: F4Matrix = ((1, 1), (0, 1))
Y_F4: F4Matrix = ((0, 2), (3, 1))


def f4_matrix_power(a: F4Matrix, exponent: int) -> F4Matrix:
    result = F4_IDENTITY
    for _ in range(exponent):
        result = f4_matrix_mul(result, a)
    return result


def binary_matrix_mul(a: BinaryMatrix, b: BinaryMatrix) -> BinaryMatrix:
    """Multiply square F2 matrices stored as row masks."""
    n = len(a)
    require(len(b) == n, "binary matrix dimensions differ")
    rows: list[int] = []
    for row in a:
        value = 0
        for k in range(n):
            if (row >> k) & 1:
                value ^= b[k]
        rows.append(value)
    return tuple(rows)


def binary_identity(n: int) -> BinaryMatrix:
    return tuple(1 << i for i in range(n))


def f4_vector_to_binary(u: int, v: int) -> int:
    """Encode (u,v) in the F2 basis (1,0),(0,1),(w,0),(0,w)."""
    return (u & 1) | ((v & 1) << 1) | ((u & 2) << 1) | ((v & 2) << 2)


def f4_matrix_to_binary(a: F4Matrix) -> BinaryMatrix:
    """View an F4-linear 2x2 map as a 4x4 binary linear map."""
    basis = ((1, 0), (0, 1), (2, 0), (0, 2))
    columns: list[int] = []
    for u, v in basis:
        out_u = f4_add(f4_mul(a[0][0], u), f4_mul(a[0][1], v))
        out_v = f4_add(f4_mul(a[1][0], u), f4_mul(a[1][1], v))
        columns.append(f4_vector_to_binary(out_u, out_v))
    return tuple(
        sum(((columns[col] >> row) & 1) << col for col in range(4))
        for row in range(4)
    )


def augmentation_matrix(p: Permutation) -> BinaryMatrix:
    """Action on even-parity vectors, in basis e_i+e_4 for i=0,...,3."""
    columns: list[int] = []
    for j in range(4):
        column = 0
        for i in range(4):
            bit = (p[j] == i) ^ (p[4] == i)
            column |= int(bit) << i
        columns.append(column)
    return tuple(
        sum(((columns[col] >> row) & 1) << col for col in range(4))
        for row in range(4)
    )


def binary_matrix_mask(matrix: BinaryMatrix) -> int:
    n = len(matrix)
    return sum(
        ((matrix[row] >> col) & 1) << (row * n + col)
        for row in range(n)
        for col in range(n)
    )


def binary_matrix_from_mask(mask: int, n: int) -> BinaryMatrix:
    return tuple(
        sum(((mask >> (row * n + col)) & 1) << col for col in range(n))
        for row in range(n)
    )


def target_image(natural: F4Matrix, augmentation: BinaryMatrix) -> int:
    natural_bits = binary_matrix_mask(f4_matrix_to_binary(natural))
    augmentation_bits = binary_matrix_mask(augmentation)
    return 1 | (natural_bits << 1) | (augmentation_bits << 17)


def target_identity_mask() -> int:
    identity4 = binary_matrix_mask(binary_identity(4))
    return 1 | (identity4 << 1) | (identity4 << 17)


def target_multiply(a: int, b: int) -> int:
    scalar = (a & 1) & (b & 1)
    natural_a = binary_matrix_from_mask((a >> 1) & 0xFFFF, 4)
    natural_b = binary_matrix_from_mask((b >> 1) & 0xFFFF, 4)
    augmentation_a = binary_matrix_from_mask((a >> 17) & 0xFFFF, 4)
    augmentation_b = binary_matrix_from_mask((b >> 17) & 0xFFFF, 4)
    return (
        scalar
        | (binary_matrix_mask(binary_matrix_mul(natural_a, natural_b)) << 1)
        | (binary_matrix_mask(binary_matrix_mul(augmentation_a, augmentation_b)) << 17)
    )


def check_f4() -> None:
    require(f4_mul(2, 2) == 3, "F4 relation w^2=w+1 failed")
    require(f4_mul(1, 2) == 2 and f4_mul(1, 3) == 3, "F4 identity failed")
    for a in range(4):
        for b in range(4):
            require(f4_mul(a, b) == f4_mul(b, a), "F4 multiplication is not commutative")
            for c in range(4):
                require(
                    f4_mul(f4_mul(a, b), c) == f4_mul(a, f4_mul(b, c)),
                    "F4 multiplication is not associative",
                )


def check_generator_relations(
    x_natural: F4Matrix,
    y_natural: F4Matrix,
    x_augmentation: BinaryMatrix,
    y_augmentation: BinaryMatrix,
) -> None:
    require(compose(X_PERM, X_PERM) == IDENTITY_PERM, "x^2 != 1 in permutations")
    require(compose(compose(Y_PERM, Y_PERM), Y_PERM) == IDENTITY_PERM, "y^3 != 1 in permutations")
    xy_perm = compose(X_PERM, Y_PERM)
    xy5 = IDENTITY_PERM
    for _ in range(5):
        xy5 = compose(xy5, xy_perm)
    require(xy5 == IDENTITY_PERM, "(xy)^5 != 1 in permutations")

    require(f4_matrix_power(x_natural, 2) == F4_IDENTITY, "x^2 != 1 in natural module")
    require(f4_matrix_power(y_natural, 3) == F4_IDENTITY, "y^3 != 1 in natural module")
    xy_natural = f4_matrix_mul(x_natural, y_natural)
    require(f4_matrix_power(xy_natural, 5) == F4_IDENTITY, "(xy)^5 != 1 in natural module")

    id4 = binary_identity(4)
    require(binary_matrix_mul(x_augmentation, x_augmentation) == id4, "x^2 != 1 in augmentation module")
    y3 = binary_matrix_mul(binary_matrix_mul(y_augmentation, y_augmentation), y_augmentation)
    require(y3 == id4, "y^3 != 1 in augmentation module")
    xy_augmentation = binary_matrix_mul(x_augmentation, y_augmentation)
    xy5_augmentation = id4
    for _ in range(5):
        xy5_augmentation = binary_matrix_mul(xy5_augmentation, xy_augmentation)
    require(xy5_augmentation == id4, "(xy)^5 != 1 in augmentation module")


def build_group() -> tuple[list[Permutation], dict[Permutation, tuple[F4Matrix, BinaryMatrix]]]:
    x_aug = augmentation_matrix(X_PERM)
    y_aug = augmentation_matrix(Y_PERM)
    check_generator_relations(X_F4, Y_F4, x_aug, y_aug)

    generator_data = (
        (X_PERM, X_F4, x_aug),
        (Y_PERM, Y_F4, y_aug),
    )
    representations: dict[Permutation, tuple[F4Matrix, BinaryMatrix]] = {
        IDENTITY_PERM: (F4_IDENTITY, binary_identity(4))
    }
    queue: deque[Permutation] = deque([IDENTITY_PERM])
    while queue:
        p = queue.popleft()
        natural, augmentation = representations[p]
        for generator, natural_generator, augmentation_generator in generator_data:
            product = compose(p, generator)
            product_rep = (
                f4_matrix_mul(natural, natural_generator),
                binary_matrix_mul(augmentation, augmentation_generator),
            )
            if product in representations:
                require(
                    representations[product] == product_rep,
                    "generator words give inconsistent module matrices",
                )
            else:
                representations[product] = product_rep
                queue.append(product)

    group = sorted(representations)
    even_permutations = sorted(p for p in permutations(range(5)) if permutation_parity(p) == 0)
    require(len(group) == 60, f"generated group has order {len(group)}, expected 60")
    require(group == even_permutations, "generator closure differs from all even permutations")
    return group, representations


def build_multiplication_table(
    group: Sequence[Permutation],
) -> tuple[tuple[int, ...], ...]:
    index = {p: i for i, p in enumerate(group)}
    require(len(index) == len(group), "group list contains duplicate permutations")
    table = tuple(
        tuple(index[compose(p, q)] for q in group)
        for p in group
    )
    identity_index = index[IDENTITY_PERM]
    require(
        all(table[identity_index][i] == i and table[i][identity_index] == i for i in range(len(group))),
        "multiplication table has an incorrect identity row or column",
    )
    return table


def check_representations_and_table(
    group: Sequence[Permutation],
    representations: dict[Permutation, tuple[F4Matrix, BinaryMatrix]],
    table: Sequence[Sequence[int]],
) -> None:
    for i, p in enumerate(group):
        natural_p, augmentation_p = representations[p]
        for j, q in enumerate(group):
            natural_q, augmentation_q = representations[q]
            product_index = table[i][j]
            natural_product, augmentation_product = representations[group[product_index]]
            require(
                f4_matrix_mul(natural_p, natural_q) == natural_product,
                "natural module disagrees with permutation multiplication",
            )
            require(
                binary_matrix_mul(augmentation_p, augmentation_q) == augmentation_product,
                "augmentation module disagrees with permutation multiplication",
            )


def rank_of_masks(values: Iterable[int]) -> int:
    pivots: dict[int, int] = {}
    for original in values:
        value = original
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def nullspace_basis(columns: Sequence[int], domain_dimension: int) -> tuple[int, list[int]]:
    """Return rank and a basis of column dependencies as domain bit masks."""
    pivots: dict[int, tuple[int, int]] = {}
    kernel: list[int] = []
    for i, original in enumerate(columns):
        value = original
        coefficients = 1 << i
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                pivot_value, pivot_coefficients = pivots[pivot]
                value ^= pivot_value
                coefficients ^= pivot_coefficients
            else:
                pivots[pivot] = (value, coefficients)
                break
        if value == 0:
            kernel.append(coefficients)
    require(len(columns) == domain_dimension, "domain dimension does not match column count")
    return len(pivots), kernel


def independent_basis(values: Iterable[int]) -> list[int]:
    pivots: dict[int, int] = {}
    basis: list[int] = []
    for original in values:
        value = original
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                basis.append(value)
                break
    return basis


def in_span(value: int, basis: Sequence[int]) -> bool:
    pivots: dict[int, int] = {}
    for vector in basis:
        residual = vector
        while residual:
            pivot = residual.bit_length() - 1
            if pivot in pivots:
                residual ^= pivots[pivot]
            else:
                pivots[pivot] = residual
                break
    while value:
        pivot = value.bit_length() - 1
        if pivot not in pivots:
            return False
        value ^= pivots[pivot]
    return True


def algebra_mask_image(mask: int, images: Sequence[int]) -> int:
    result = 0
    while mask:
        bit = mask & -mask
        index = bit.bit_length() - 1
        result ^= images[index]
        mask ^= bit
    return result


def multiply_algebra_masks(
    left: int,
    right: int,
    table: Sequence[Sequence[int]],
) -> int:
    result = 0
    left_bits = left
    while left_bits:
        left_bit = left_bits & -left_bits
        i = left_bit.bit_length() - 1
        right_bits = right
        while right_bits:
            right_bit = right_bits & -right_bits
            j = right_bit.bit_length() - 1
            result ^= 1 << table[i][j]
            right_bits ^= right_bit
        left_bits ^= left_bit
    return result


def multiply_by_group_basis(
    value: int,
    group_index: int,
    table: Sequence[Sequence[int]],
    group_on_left: bool,
) -> int:
    result = 0
    bits = value
    while bits:
        bit = bits & -bits
        j = bit.bit_length() - 1
        product_index = table[group_index][j] if group_on_left else table[j][group_index]
        result ^= 1 << product_index
        bits ^= bit
    return result


def check_group_table(
    group: Sequence[Permutation],
    table: Sequence[Sequence[int]],
) -> None:
    index = {p: i for i, p in enumerate(group)}
    for i, p in enumerate(group):
        for j, q in enumerate(group):
            require(table[i][j] == index[compose(p, q)], "multiplication table entry is corrupted")


def check_image_homomorphism(images: Sequence[int], table: Sequence[Sequence[int]]) -> None:
    require(len(images) == len(table), "group-image count mismatch")
    require(images[0] == target_identity_mask(), "identity image is not the target identity")
    for i, left in enumerate(images):
        for j, right in enumerate(images):
            require(
                images[table[i][j]] == target_multiply(left, right),
                "group-basis images fail multiplication consistency",
            )


def expect_rejected(label: str, check: Callable[[], None]) -> None:
    try:
        check()
    except CheckFailure:
        return
    raise CheckFailure(f"negative control was not rejected: {label}")


def run_negative_controls(
    group: Sequence[Permutation],
    table: Sequence[Sequence[int]],
    images: Sequence[int],
    actual_rank: int,
) -> dict[str, bool]:
    x_aug = augmentation_matrix(X_PERM)
    y_aug = augmentation_matrix(Y_PERM)
    expect_rejected(
        "wrong generator alignment",
        lambda: check_generator_relations(Y_F4, X_F4, x_aug, y_aug),
    )

    corrupted_images = list(images)
    corrupted_images[0] ^= 1 << 33  # add a spurious, independent target coordinate
    corrupted_rank = rank_of_masks(corrupted_images)
    require(corrupted_rank == actual_rank + 1, "rank-corruption control did not raise rank by one")
    expect_rejected(
        "corrupted image matrix rank",
        lambda: require(corrupted_rank == 25, "combined map rank is not 25"),
    )

    corrupted_table = [list(row) for row in table]
    corrupted_table[0][0] = (corrupted_table[0][0] + 1) % len(group)
    expect_rejected(
        "corrupted multiplication table",
        lambda: check_group_table(group, corrupted_table),
    )
    return {
        "wrong_generator_alignment_rejected": True,
        "corrupted_image_matrix_rank_rejected": True,
        "corrupted_multiplication_table_rejected": True,
    }


def hash_json(value: object) -> str:
    encoded = json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def matrix_as_lists(matrix: BinaryMatrix) -> list[list[int]]:
    n = len(matrix)
    return [[(matrix[row] >> col) & 1 for col in range(n)] for row in range(n)]


def run_checks() -> dict[str, object]:
    check_f4()

    group, representations = build_group()
    table = build_multiplication_table(group)
    check_representations_and_table(group, representations, table)

    natural_images: list[int] = []
    augmentation_images: list[int] = []
    combined_images: list[int] = []
    for p in group:
        natural, augmentation = representations[p]
        natural_bits = binary_matrix_mask(f4_matrix_to_binary(natural))
        augmentation_bits = binary_matrix_mask(augmentation)
        natural_images.append(natural_bits)
        augmentation_images.append(augmentation_bits)
        combined_images.append(1 | (natural_bits << 1) | (augmentation_bits << 17))

    check_image_homomorphism(combined_images, table)
    natural_rank = rank_of_masks(natural_images)
    augmentation_rank = rank_of_masks(augmentation_images)
    combined_rank, kernel = nullspace_basis(combined_images, domain_dimension=60)
    require(natural_rank == 8, f"natural F4 block rank is {natural_rank}, expected 8")
    require(augmentation_rank == 16, f"augmentation block rank is {augmentation_rank}, expected 16")
    require(combined_rank == 25, f"combined map rank is {combined_rank}, expected 25")
    require(len(kernel) == 35, f"kernel dimension is {len(kernel)}, expected 35")
    require(all(algebra_mask_image(v, combined_images) == 0 for v in kernel), "kernel basis image is nonzero")

    ideal_basis = independent_basis(kernel)
    require(len(ideal_basis) == 35, "computed kernel basis is not independent")
    for j in ideal_basis:
        for g in range(60):
            left = multiply_by_group_basis(j, g, table, group_on_left=True)
            right = multiply_by_group_basis(j, g, table, group_on_left=False)
            require(algebra_mask_image(left, combined_images) == 0, "kernel is not left-stable")
            require(algebra_mask_image(right, combined_images) == 0, "kernel is not right-stable")
            require(in_span(left, ideal_basis), "left product escaped the kernel span")
            require(in_span(right, ideal_basis), "right product escaped the kernel span")

    powers = [ideal_basis]
    power_dimensions = [len(ideal_basis)]
    for _ in range(60):
        current = powers[-1]
        next_basis = independent_basis(
            multiply_algebra_masks(a, b, table)
            for a in current
            for b in ideal_basis
        )
        power_dimensions.append(len(next_basis))
        require(
            all(in_span(v, current) for v in next_basis),
            "computed ideal powers are not descending",
        )
        if not next_basis:
            powers.append([])
            break
        require(
            len(next_basis) < len(current),
            "a nonzero computed ideal power failed to decrease",
        )
        powers.append(next_basis)
    else:
        raise CheckFailure("kernel powers did not reach zero within 60 steps")
    require(power_dimensions[-1] == 0, "last kernel power is not zero")
    require(
        power_dimensions == [35, 27, 17, 9, 0],
        f"kernel power dimensions are {power_dimensions}, expected [35, 27, 17, 9, 0]",
    )

    controls = run_negative_controls(group, table, combined_images, combined_rank)
    group_digest = hash_json([list(p) for p in group])
    kernel_digest = hash_json([f"{v:015x}" for v in kernel])
    x_aug = augmentation_matrix(X_PERM)
    y_aug = augmentation_matrix(Y_PERM)
    f4_names = {0: "0", 1: "1", 2: "w", 3: "w^2"}
    return {
        "result": "PASS_A5_SIMPLE_QUOTIENT",
        "scope": "finite algebra checks only; no theorem beyond these checks is asserted",
        "group": {
            "name": "A5",
            "order": len(group),
            "permutation_convention": "p*q = p after q; images are one-based",
            "x_images": [i + 1 for i in X_PERM],
            "y_images": [i + 1 for i in Y_PERM],
            "group_basis_sha256": group_digest,
        },
        "modules": {
            "natural": {
                "field": "F2[w]/(w^2+w+1)",
                "dimension_over_F4": 2,
                "dimension_over_F2": 4,
                "X_F4": [[f4_names[v] for v in row] for row in X_F4],
                "Y_F4": [[f4_names[v] for v in row] for row in Y_F4],
                "X_as_F2_matrix": matrix_as_lists(f4_matrix_to_binary(X_F4)),
                "Y_as_F2_matrix": matrix_as_lists(f4_matrix_to_binary(Y_F4)),
                "group_image_span_rank": natural_rank,
            },
            "augmentation_subspace": {
                "description": "even-parity subspace of F2^5, basis e_i+e_4 for i=0,...,3",
                "dimension_over_F2": 4,
                "X_matrix": matrix_as_lists(x_aug),
                "Y_matrix": matrix_as_lists(y_aug),
                "group_image_span_rank": augmentation_rank,
            },
        },
        "algebra_map": {
            "domain_dimension": 60,
            "ambient_binary_target_dimension": 33,
            "declared_target_dimension": 25,
            "block_dimensions": {"F2": 1, "End_F4_F4^2": 8, "End_F2_F2^4": 16},
            "rank": combined_rank,
            "kernel_dimension": len(kernel),
            "kernel_basis_sha256": kernel_digest,
            "two_sided_ideal_checked": True,
            "kernel_power_dimensions": power_dimensions,
            "nilpotence_index": len(power_dimensions),
        },
        "checks": {
            "all_60_even_permutations_aligned": True,
            "all_3600_group_products_checked": True,
            "target_image_homomorphism_checked": True,
            **controls,
        },
    }


def main() -> int:
    try:
        result = run_checks()
    except CheckFailure as exc:
        print(json.dumps({"result": "FAIL_A5_SIMPLE_QUOTIENT", "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    print("PASS_A5_SIMPLE_QUOTIENT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
