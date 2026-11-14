#!/usr/bin/env python3
"""Standalone lower-bound check for the two-exclusion invariant Hall set.

This checker does not load the R5 matching, Hall list, or any sibling file.
It generates all W(D4) orbit representatives of T1, checks their orbit
capacities, enumerates each representative's complete error-one outputs, and
proves N_beta(T1) is contained in the closed-form set N1.
"""

from __future__ import annotations

import itertools
import json
from collections import Counter
from math import factorial


H = (
    (1, 1, 1, 1),
    (1, -1, 1, -1),
    (1, 1, -1, -1),
    (1, -1, -1, 1),
)
BETA = (21, 19)
RADIUS_SQUARED = 25
B19_SQUARED = 19
EXCLUDED_ABS_PATTERNS = {(0, 0, 3, 3), (0, 1, 3, 3)}
SPECIAL_PLUS_PATTERN = (2, 2, 2, 3)


def require(condition: bool, explanation: str) -> None:
    if not condition:
        raise RuntimeError(explanation)


def norm_squared(point):
    return sum(value * value for value in point)


def sorted_abs(point):
    return tuple(sorted(abs(value) for value in point))


def sign_product(point):
    require(all(value != 0 for value in point),
            "sign product is defined only for nonzero coordinates")
    result = 1
    for value in point:
        result *= 1 if value > 0 else -1
    return result


def orbit_capacity(pattern, epsilon):
    multiplicities = Counter(pattern)
    zero_count = multiplicities.pop(0, 0)
    denominator = factorial(zero_count)
    for multiplicity in multiplicities.values():
        denominator *= factorial(multiplicity)
    permutation_count = factorial(4) // denominator
    nonzero_signs = 1 << (4 - zero_count)
    if zero_count == 0:
        require(epsilon in (-1, 1), "nonzero orbit needs a sign-product label")
        nonzero_signs //= 2
    else:
        require(epsilon is None, "orbit with zeros has no sign-product label")
    return permutation_count * nonzero_signs


def canonical_representatives():
    """Generate exactly T1's 38 W(D4) orbit representatives."""
    patterns = {
        tuple(sorted(values))
        for values in itertools.product(range(5), repeat=4)
        if sum(value * value for value in values) <= B19_SQUARED
    }
    patterns -= EXCLUDED_ABS_PATTERNS
    representatives = []
    for pattern in sorted(patterns):
        if 0 in pattern:
            representatives.append((pattern, None, pattern))
        else:
            representatives.append((pattern, 1, pattern))
            negative = (-pattern[0], pattern[1], pattern[2], pattern[3])
            representatives.append((pattern, -1, negative))
    representatives.append((SPECIAL_PLUS_PATTERN, 1, SPECIAL_PLUS_PATTERN))
    return representatives


def signed_permutation_matrices(even_signs_only):
    matrices = []
    for permutation in itertools.permutations(range(4)):
        for signs in itertools.product((-1, 1), repeat=4):
            if even_signs_only and signs[0] * signs[1] * signs[2] * signs[3] != 1:
                continue
            matrix = [[0] * 4 for _ in range(4)]
            for row, column in enumerate(permutation):
                matrix[row][column] = signs[row]
            matrices.append(tuple(tuple(row) for row in matrix))
    return matrices


def matrix_multiply(left, right):
    return tuple(
        tuple(sum(left[i][k] * right[k][j] for k in range(4))
              for j in range(4))
        for i in range(4)
    )


def matrix_transpose(matrix):
    return tuple(tuple(matrix[i][j] for i in range(4)) for j in range(4))


def graph_group_check():
    """Check every even-sign input action has an even-sign output action."""
    input_group = signed_permutation_matrices(even_signs_only=True)
    all_signed = set(signed_permutation_matrices(even_signs_only=False))
    require(len(input_group) == 192 and len(all_signed) == 384,
            "signed-permutation group cardinalities changed")
    ht = matrix_transpose(H)
    output_group = set()
    for a in input_group:
        numerator = matrix_multiply(matrix_multiply(H, a), ht)
        require(all(value % 4 == 0 for row in numerator for value in row),
                "W(D4) action did not produce an integral output action")
        b = tuple(tuple(value // 4 for value in row) for row in numerator)
        require(b in all_signed and b in set(input_group),
                "input action does not map to an even-sign output action")
        require(matrix_multiply(b, H) == matrix_multiply(H, a),
                "paired action fails B H=H A")
        output_group.add(b)
    require(output_group == set(input_group),
            "paired action is not onto the output W(D4) projection")
    return len(input_group), len(output_group)


def sum_sqrt_le(a: int, b: int, c: int, d: int) -> bool:
    """Exact comparison sqrt(a)+sqrt(b) <= sqrt(c)+sqrt(d)."""
    require(min(a, b, c, d) >= 0, "negative radical")
    k = c + d - a - b
    p = a * b
    q = c * d
    if k >= 0:
        if p <= q:
            return True
        if k == 0:
            return False
        e = 4 * (p - q) - k * k
        if e <= 0:
            return True
        return e * e <= 16 * k * k * q
    r = -k
    e = 4 * (q - p) - r * r
    if e < 0:
        return False
    return e * e >= 16 * r * r * p


def compare_gaps(m: int, n: int, a: int, b: int) -> int:
    """Sign of (sqrt(m)-sqrt(n))-(sqrt(a)-sqrt(b)), exactly."""
    left_le = sum_sqrt_le(m, b, a, n)
    right_le = sum_sqrt_le(a, n, m, b)
    require(left_le or right_le, "radical comparison is inconsistent")
    if left_le and right_le:
        return 0
    return -1 if left_le else 1


def strict_beta_gap(point, output) -> bool:
    return compare_gaps(norm_squared(output), norm_squared(point), *BETA) < 0


def error_one_candidates(point):
    """Return exactly the 9 integer-image or 16 half-integer-image neighbors."""
    hx = tuple(sum(H[i][j] * point[j] for j in range(4)) for i in range(4))
    parity = sum(point) & 1
    require(all((value & 1) == parity for value in hx),
            "Hadamard image coordinates do not have common parity")
    if parity == 0:
        center = tuple(value // 2 for value in hx)
        outputs = {center}
        for coordinate in range(4):
            for sign in (-1, 1):
                changed = list(center)
                changed[coordinate] += sign
                outputs.add(tuple(changed))
        require(len(outputs) == 9, "integer-image candidate count is not nine")
    else:
        floors = tuple(value // 2 for value in hx)
        outputs = {
            tuple(floors[i] + bit[i] for i in range(4))
            for bit in itertools.product((0, 1), repeat=4)
        }
        require(len(outputs) == 16, "half-integer candidate count is not sixteen")
    for output in outputs:
        error_numerator = sum((2 * output[i] - hx[i]) ** 2 for i in range(4))
        require(error_numerator <= 4,
                "enumerated output exceeds Euclidean error one")
        if parity == 1:
            require(error_numerator == 4,
                    "half-integer candidate has unexpected error")
    return sorted(outputs), parity


def output_in_n1(output):
    return (
        norm_squared(output) <= B19_SQUARED
        and sorted_abs(output) not in EXCLUDED_ABS_PATTERNS
    )


def b19_shell_counts():
    """Coefficients through degree 19 of (1+2z+2z^4+2z^9+2z^16)^4."""
    one_coordinate = ((0, 1), (1, 2), (4, 2), (9, 2), (16, 2))
    coefficients = [1] + [0] * 19
    for _ in range(4):
        next_coefficients = [0] * 20
        for degree, coefficient in enumerate(coefficients):
            if coefficient == 0:
                continue
            for added_degree, multiplicity in one_coordinate:
                target = degree + added_degree
                if target <= 19:
                    next_coefficients[target] += coefficient * multiplicity
        coefficients = next_coefficients
    return coefficients


def main():
    group_input_count, group_output_count = graph_group_check()
    representatives = canonical_representatives()
    keys = [(pattern, epsilon) for pattern, epsilon, _ in representatives]
    require(len(keys) == len(set(keys)) == 38,
            "closed-form T1 orbit representative count changed")

    t1_count = 0
    b19_shells = b19_shell_counts()
    n1_count = sum(b19_shells)
    require(n1_count == 1897, "four-square count for B19 changed")

    excluded_orbit_sizes = {
        "O0033": orbit_capacity((0, 0, 3, 3), None),
        "O0133": orbit_capacity((0, 1, 3, 3), None),
    }
    require(excluded_orbit_sizes == {"O0033": 24, "O0133": 96},
            "two excluded orbit sizes changed")
    n1_count -= sum(excluded_orbit_sizes.values())
    require(n1_count == 1777, "closed-form N1 count changed")

    rows = []
    total_strict_representative_edges = 0
    for pattern, epsilon, representative in representatives:
        orbit_size = orbit_capacity(pattern, epsilon)
        require(norm_squared(representative) <= RADIUS_SQUARED,
                "T1 representative is outside S5")
        require(sorted_abs(representative) == pattern,
                "representative absolute-coordinate key changed")
        if epsilon is not None:
            require(sign_product(representative) == epsilon,
                    "representative sign-product key changed")
        t1_count += orbit_size

        outputs, parity = error_one_candidates(representative)
        strict_neighbors = [y for y in outputs
                            if strict_beta_gap(representative, y)]
        outside = [y for y in strict_neighbors if not output_in_n1(y)]
        require(not outside,
                f"strict-beta neighbor escaped N1 at representative {representative}")
        total_strict_representative_edges += len(strict_neighbors)
        rows.append({
            "representative": list(representative),
            "sorted_abs": list(pattern),
            "sign_product": epsilon,
            "orbit_size": orbit_size,
            "norm_squared": norm_squared(representative),
            "image_parity": "integer" if parity == 0 else "half-integer",
            "error_one_candidates": len(outputs),
            "strict_beta_neighbors_checked": len(strict_neighbors),
            "neighbors_outside_N1": len(outside),
        })
    require(t1_count == 1809, "closed-form T1 orbit-capacity count changed")
    require(t1_count - n1_count == 32,
            "closed-form Hall deficiency is not 32")

    print(json.dumps({
        "status": "PASS",
        "scope": "certificate-independent Hall lower bound at strict beta on S5",
        "operator_numerator": [list(row) for row in H],
        "beta": "sqrt(21)-sqrt(19)",
        "paired_W_D4_group": {
            "input_projection_order": group_input_count,
            "output_projection_order": group_output_count,
            "checked_identity": "B H=H A",
        },
        "sets": {
            "B19_count_from_polynomial_coefficients": n1_count + 24 + 96,
            "excluded_orbit_sizes": excluded_orbit_sizes,
            "N1_count": n1_count,
            "T1_count": t1_count,
            "Hall_deficiency_lower_bound": t1_count - n1_count,
            "T1_orbit_count": len(representatives),
        },
        "neighbor_check": {
            "representatives_checked": len(rows),
            "integer_image_representatives": sum(row["image_parity"] == "integer" for row in rows),
            "half_integer_representatives": sum(row["image_parity"] == "half-integer" for row in rows),
            "representative_strict_edges_checked": total_strict_representative_edges,
            "all_strict_neighbors_in_N1": True,
        },
        "B19_shell_counts_from_polynomial": [[n, count] for n, count in enumerate(b19_shells)],
        "representative_checks": rows,
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
