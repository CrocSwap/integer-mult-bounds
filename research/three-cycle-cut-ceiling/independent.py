#!/usr/bin/env python3
"""Independent exact regular-representation check for GL(3, F_2).

Group elements are literal permutations of the seven nonzero vectors.  No
matrix package or parent scratch implementation is used.
Prepared by Krzysztof Wojt with substantial OpenAI Codex and Luna assistance.
Apache-2.0. This is same-session implementation corroboration, not human review.
"""

from __future__ import annotations

import json
from copy import deepcopy
from math import isqrt
from typing import Callable, Dict, List, Sequence, Tuple


Perm = Tuple[int, ...]
Vector = List[int]
POINTS: Tuple[int, ...] = tuple(range(1, 8))
IDENTITY_PERM: Perm = POINTS


def compose(a: Perm, b: Perm) -> Perm:
    """Return a after b, using image tuples on points 1 through 7."""
    return tuple(a[b[x - 1] - 1] for x in POINTS)


def cnot_permutation(target: int, source: int) -> Perm:
    """Permutation induced by y_target=x_target XOR x_source."""
    if target == source or target not in range(3) or source not in range(3):
        raise ValueError("CNOT coordinates must be distinct members of 0,1,2")
    return tuple(x ^ (((x >> source) & 1) << target) for x in POINTS)


def cycle_permutation() -> Perm:
    """Return (x0,x1,x2) -> (x1,x2,x0)."""
    def rotate(x: int) -> int:
        x0, x1, x2 = x & 1, (x >> 1) & 1, (x >> 2) & 1
        return x1 | (x2 << 1) | (x0 << 2)

    return tuple(rotate(x) for x in POINTS)


def make_generators() -> List[Perm]:
    return [
        cnot_permutation(target, source)
        for target in range(3)
        for source in range(3)
        if target != source
    ]


def closure(generators: Sequence[Perm]) -> List[Perm]:
    """BFS closure from identity, adjoining each literal permutation on left."""
    group = [IDENTITY_PERM]
    seen = {IDENTITY_PERM}
    cursor = 0
    while cursor < len(group):
        current = group[cursor]
        cursor += 1
        for generator in generators:
            product = compose(generator, current)
            if product not in seen:
                seen.add(product)
                group.append(product)
    return group


def poly_mul(a: Sequence[int], b: Sequence[int]) -> List[int]:
    result = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i + j] += x * y
    return result


def make_polynomials() -> Tuple[List[int], List[int]]:
    factors = [
        [7, -6, 1],
        [42, -14, 1],
        [-5, 1],
        [-6, 1],
        [-7, 1],
        [-9, 1],
    ]
    p = [1]
    for factor in factors:
        p = poly_mul(p, factor)
    q = [1]
    for factor in factors[1:]:
        q = poly_mul(q, factor)
    if poly_mul(factors[0], q) != p:
        raise RuntimeError("quotient construction does not reproduce p")
    return p, q


class RegularOperators:
    """Integer operators on coordinates indexed by the generated group."""

    def __init__(self, group: Sequence[Perm], generators: Sequence[Perm]):
        self.group = list(group)
        self.index = {g: i for i, g in enumerate(self.group)}
        self.size = len(self.group)
        self.product = [
            [self.index[compose(g, h)] for h in self.group]
            for g in self.group
        ]
        self.generator_indices = [self.index[g] for g in generators]

    def apply_p(self, g: int, vector: Sequence[int]) -> Vector:
        result = [0] * self.size
        row_for_column = self.product[g]
        for column, value in enumerate(vector):
            if value:
                result[row_for_column[column]] += value
        return result

    def apply_l(
        self,
        vector: Sequence[int],
        generator_indices: Sequence[int] | None = None,
        diagonal: int = 6,
    ) -> Vector:
        if generator_indices is None:
            generator_indices = self.generator_indices
        result = [diagonal * value for value in vector]
        for generator in generator_indices:
            row_for_column = self.product[generator]
            for column, value in enumerate(vector):
                if value:
                    result[row_for_column[column]] -= value
        return result

    def apply_b(self, vector: Sequence[int], target: int) -> Vector:
        target2 = self.product[target][target]
        result = [2 * value for value in vector]
        target_rows = self.product[target]
        target2_rows = self.product[target2]
        for column, value in enumerate(vector):
            if value:
                result[target_rows[column]] -= value
                result[target2_rows[column]] -= value
        return result


def apply_polynomial(
    coefficients: Sequence[int],
    vector: Sequence[int],
    apply_l: Callable[[Sequence[int]], Vector],
) -> Vector:
    """Horner evaluation with coefficients listed from constant upward."""
    result = [coefficients[-1] * value for value in vector]
    for coefficient in reversed(coefficients[:-1]):
        result = apply_l(result)
        result = [value + coefficient * base for value, base in zip(result, vector)]
    return result


def first_nonzero(vector: Sequence[int]) -> int | None:
    return next((i for i, value in enumerate(vector) if value), None)


def check_annihilation(
    operators: RegularOperators,
    polynomial: Sequence[int],
    target: int,
    generator_indices: Sequence[int] | None = None,
    diagonal: int = 6,
) -> Dict[str, object]:
    def selected_l(vector: Sequence[int]) -> Vector:
        return operators.apply_l(vector, generator_indices, diagonal)

    failing_columns = 0
    first_failure = None
    for column in range(operators.size):
        basis = [0] * operators.size
        basis[column] = 1
        residual = apply_polynomial(
            polynomial, operators.apply_b(basis, target), selected_l
        )
        row = first_nonzero(residual)
        if row is not None:
            failing_columns += 1
            if first_failure is None:
                first_failure = {
                    "column_index": column,
                    "column_permutation": list(operators.group[column]),
                    "row_index": row,
                    "row_permutation": list(operators.group[row]),
                    "value": residual[row],
                }
    return {
        "basis_columns_checked": operators.size,
        "failing_columns": failing_columns,
        "first_failure": first_failure,
        "zero_on_all_basis_columns": failing_columns == 0,
    }


def vector_summary(vector: Sequence[int]) -> Dict[str, object]:
    l2_squared = sum(value * value for value in vector)
    root = isqrt(l2_squared)
    return {
        "l2_norm_exact": str(root) if root * root == l2_squared else "sqrt(" + str(l2_squared) + ")",
        "l2_squared": l2_squared,
        "nonzero_entries": sum(value != 0 for value in vector),
        "l1": sum(abs(value) for value in vector),
    }


def target_order(operators: RegularOperators, target: int) -> int:
    power = target
    order = 1
    while power != 0:
        power = operators.product[target][power]
        order += 1
        if order > 1000:
            raise AssertionError("finite permutation unexpectedly has large order")
    return order


def run_check() -> Dict[str, object]:
    generators = make_generators()
    group = closure(generators)
    operators = RegularOperators(group, generators)
    group_index = operators.index

    target_perm = cycle_permutation()
    target = group_index[target_perm]
    target2 = operators.product[target][target]
    p, q = make_polynomials()

    annihilation = check_annihilation(operators, p, target)

    identity_basis = [0] * operators.size
    identity_basis[group_index[IDENTITY_PERM]] = 1
    b_identity = operators.apply_b(identity_basis, target)
    v = apply_polynomial(q, b_identity, operators.apply_l)
    lv = operators.apply_l(v)
    w = [value - 3 * base for value, base in zip(lv, v)]
    lw = operators.apply_l(w)
    shifted_w = [value - 3 * base for value, base in zip(lw, w)]
    bv = operators.apply_b(v, target)
    twice_v = [2 * value for value in v]
    thrice_v = [3 * value for value in v]

    v_summary = vector_summary(v)
    w_summary = vector_summary(w)
    dot_vw = sum(x * y for x, y in zip(v, w))
    main_vectors = {
        "v_nonzero": any(v),
        "w_nonzero": any(w),
        "(L_minus_3I)w_equals_2v": shifted_w == twice_v,
        "Bv_equals_3v": bv == thrice_v,
        "v": v_summary,
        "w": w_summary,
        "v_dot_w": dot_vw,
    }

    altered_p = list(p)
    altered_p[0] += 1
    altered_constant = check_annihilation(operators, altered_p, target)

    omitted_generator = 0
    remaining_generator_indices = operators.generator_indices[1:]
    missing_generator = check_annihilation(
        operators,
        p,
        target,
        generator_indices=remaining_generator_indices,
        diagonal=5,
    )
    missing_generator["omitted_permutation"] = list(generators[omitted_generator])

    identity_target = group_index[IDENTITY_PERM]
    identity_b = operators.apply_b(identity_basis, identity_target)
    identity_v = apply_polynomial(q, identity_b, operators.apply_l)
    identity_w = [
        value - 3 * base
        for value, base in zip(operators.apply_l(identity_v), identity_v)
    ]

    incorrect_target = operators.generator_indices[0]
    incorrect_order = target_order(operators, incorrect_target)
    incorrect_target_annihilation = check_annihilation(
        operators, p, incorrect_target
    )
    incorrect_b_identity = operators.apply_b(identity_basis, incorrect_target)
    incorrect_v = apply_polynomial(q, incorrect_b_identity, operators.apply_l)
    incorrect_w = [
        value - 3 * base
        for value, base in zip(operators.apply_l(incorrect_v), incorrect_v)
    ]

    return {
        "schema": "regular-gl3-f2-spectral-check/v1",
        "representation": "literal permutations of the seven nonzero 3-bit vectors",
        "group_order": operators.size,
        "generator_count": len(generators),
        "target_permutation": list(target_perm),
        "target_order": target_order(operators, target),
        "polynomial_coefficients_low_to_high": p,
        "quotient_coefficients_low_to_high": q,
        "p_of_l_times_b": annihilation,
        "vectors": main_vectors,
        "controls": {
            "altered_polynomial_constant_plus_one": altered_constant,
            "one_cnot_generator_omitted": missing_generator,
            "identity_target": {
                "b_on_identity_is_zero": not any(identity_b),
                "v_nonzero_expected_but_actual": any(identity_v),
                "w_nonzero_expected_but_actual": any(identity_w),
                "v": vector_summary(identity_v),
                "w": vector_summary(identity_w),
            },
            "incorrect_order_two_target": {
                "target_permutation": list(generators[0]),
                "target_order": incorrect_order,
                "p_of_l_times_b": incorrect_target_annihilation,
                "v_nonzero": any(incorrect_v),
                "w_nonzero": any(incorrect_w),
                "v": vector_summary(incorrect_v),
                "w": vector_summary(incorrect_w),
            },
        },
        "interpretation_limit": "finite implementation check only; the abstract regular-group-algebra implication requires a separate written proof",
    }


def validate_report(report: Dict[str, object]) -> None:
    """Fail closed unless the computed report matches every required check."""
    if not isinstance(report, dict):
        raise RuntimeError("report must be a JSON object")

    expected = {
        "schema": "regular-gl3-f2-spectral-check/v1",
        "group_order": 168,
        "generator_count": 6,
        "target_permutation": [4, 1, 5, 2, 6, 3, 7],
        "target_order": 3,
        "polynomial_coefficients_low_to_high": [
            555660, -1006362, 741006, -295897, 70871, -10494, 942, -47, 1
        ],
        "quotient_coefficients_low_to_high": [79380, -75726, 29610, -6073, 689, -41, 1],
    }
    for key, value in expected.items():
        if report.get(key) != value:
            raise RuntimeError(f"unexpected report field {key}: {report.get(key)!r}")

    annihilation = report.get("p_of_l_times_b")
    if not isinstance(annihilation, dict):
        raise RuntimeError("missing p(L)B result")
    if annihilation.get("basis_columns_checked") != 168:
        raise RuntimeError("p(L)B did not check all 168 basis columns")
    if annihilation.get("failing_columns") != 0:
        raise RuntimeError("p(L)B failed on one or more basis columns")
    if annihilation.get("zero_on_all_basis_columns") is not True:
        raise RuntimeError("p(L)B zero status is false")
    if annihilation.get("first_failure") is not None:
        raise RuntimeError("p(L)B unexpectedly reports a failing column")

    vectors = report.get("vectors")
    if not isinstance(vectors, dict):
        raise RuntimeError("missing vector checks")
    for key in (
        "v_nonzero",
        "w_nonzero",
        "(L_minus_3I)w_equals_2v",
        "Bv_equals_3v",
    ):
        if vectors.get(key) is not True:
            raise RuntimeError(f"required vector check failed: {key}")

    expected_v = {
        "l2_norm_exact": "sqrt(117151272)",
        "l2_squared": 117151272,
        "nonzero_entries": 165,
        "l1": 108360,
    }
    expected_w = {
        "l2_norm_exact": "sqrt(234302544)",
        "l2_squared": 234302544,
        "nonzero_entries": 165,
        "l1": 153216,
    }
    for label, values in (("v", expected_v), ("w", expected_w)):
        summary = vectors.get(label)
        if not isinstance(summary, dict):
            raise RuntimeError(f"missing {label} summary")
        for key, value in values.items():
            if summary.get(key) != value:
                raise RuntimeError(f"unexpected {label}.{key}: {summary.get(key)!r}")
    if vectors.get("v_dot_w") != -165676896:
        raise RuntimeError("unexpected v dot w")

    controls = report.get("controls")
    if not isinstance(controls, dict):
        raise RuntimeError("missing controls")
    for key in (
        "altered_polynomial_constant_plus_one",
        "one_cnot_generator_omitted",
    ):
        control = controls.get(key)
        if not isinstance(control, dict):
            raise RuntimeError(f"missing control {key}")
        if control.get("basis_columns_checked") != 168:
            raise RuntimeError(f"control {key} did not check all columns")
        if control.get("failing_columns") != 168:
            raise RuntimeError(f"control {key} did not reject every column")
        if control.get("zero_on_all_basis_columns") is not False:
            raise RuntimeError(f"control {key} reports unexpected annihilation")
        if control.get("first_failure") is None:
            raise RuntimeError(f"control {key} lacks a failure witness")

    identity = controls.get("identity_target")
    if not isinstance(identity, dict):
        raise RuntimeError("missing identity-target control")
    if identity.get("b_on_identity_is_zero") is not True:
        raise RuntimeError("identity target did not make B zero")
    if identity.get("v_nonzero_expected_but_actual") is not False:
        raise RuntimeError("identity-target v control is not zero")
    if identity.get("w_nonzero_expected_but_actual") is not False:
        raise RuntimeError("identity-target w control is not zero")
    zero_summary = {
        "l2_norm_exact": "0",
        "l2_squared": 0,
        "nonzero_entries": 0,
        "l1": 0,
    }
    for label in ("v", "w"):
        if identity.get(label) != zero_summary:
            raise RuntimeError(f"identity-target {label} is not the zero vector")

    incorrect = controls.get("incorrect_order_two_target")
    if not isinstance(incorrect, dict):
        raise RuntimeError("missing incorrect-target control")
    if incorrect.get("target_order") != 2:
        raise RuntimeError("incorrect-target control is not order two")
    incorrect_annihilation = incorrect.get("p_of_l_times_b")
    if not isinstance(incorrect_annihilation, dict):
        raise RuntimeError("missing incorrect-target annihilation result")
    if incorrect_annihilation.get("basis_columns_checked") != 168:
        raise RuntimeError("incorrect-target control did not check all columns")
    if incorrect_annihilation.get("failing_columns") != 168:
        raise RuntimeError("incorrect-target control did not reject every column")
    if incorrect_annihilation.get("zero_on_all_basis_columns") is not False:
        raise RuntimeError("incorrect-target control reports unexpected annihilation")
    if incorrect_annihilation.get("first_failure") is None:
        raise RuntimeError("incorrect-target control lacks a failure witness")


def run_validator_self_tests(report: Dict[str, object]) -> int:
    """Prove key report corruptions are rejected without mutating report."""
    cases = []

    corrupt = deepcopy(report)
    corrupt["controls"]["identity_target"]["b_on_identity_is_zero"] = False
    cases.append(("identity status", corrupt))

    corrupt = deepcopy(report)
    corrupt["group_order"] = 167
    cases.append(("group order", corrupt))

    corrupt = deepcopy(report)
    corrupt["vectors"]["v"]["l2_squared"] += 1
    cases.append(("norm", corrupt))

    for control_name in (
        "altered_polynomial_constant_plus_one",
        "one_cnot_generator_omitted",
    ):
        corrupt = deepcopy(report)
        corrupt["controls"][control_name]["failing_columns"] = 0
        cases.append((control_name, corrupt))

    corrupt = deepcopy(report)
    corrupt["controls"]["incorrect_order_two_target"]["p_of_l_times_b"][
        "failing_columns"
    ] = 0
    cases.append(("incorrect order-two target", corrupt))

    for name, corrupted_report in cases:
        try:
            validate_report(corrupted_report)
        except RuntimeError:
            continue
        raise RuntimeError(f"validator self-test failed to reject {name}")
    return len(cases)


def main() -> None:
    report = run_check()
    validate_report(report)
    self_tests_passed = run_validator_self_tests(report)
    report["validator_self_tests_passed"] = self_tests_passed
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
