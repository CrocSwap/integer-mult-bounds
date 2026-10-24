"""Independent exact polynomial oracles for norm-six symbolic compression.

This module deliberately has no imports from the research package. Polynomials
are dictionaries from sorted variable-index tuples to integer coefficients;
the empty tuple denotes the constant monomial.

Prepared for Krzysztof Wojt by a bounded Luna supporting agent, with primary
OpenAI Codex review and integration. Apache-2.0.
"""

from __future__ import annotations

from time import perf_counter


Polynomial = dict[tuple[int, ...], int]


def _fail(message: str) -> None:
    raise ValueError(message)


def _is_int(value: object) -> bool:
    return type(value) is int


def _validate_matrix(matrix: object) -> tuple[int, list[list[int]]]:
    if type(matrix) not in (list, tuple):
        _fail("G must be a list or tuple of rows")
    rows = list(matrix)
    dimension = len(rows)
    if dimension == 0:
        _fail("G must have positive dimension")
    checked: list[list[int]] = []
    for index, row in enumerate(rows):
        if type(row) not in (list, tuple) or len(row) != dimension:
            _fail(f"G row {index} must have length {dimension}")
        checked_row: list[int] = []
        for column, value in enumerate(row):
            if not _is_int(value):
                _fail(f"G[{index}][{column}] must be an integer")
            checked_row.append(value)
        checked.append(checked_row)
    for i in range(dimension):
        if checked[i][i] % 2:
            _fail(f"G diagonal entry {i} must be even")
        for j in range(i + 1, dimension):
            if checked[i][j] != checked[j][i]:
                _fail(f"G must be symmetric at ({i}, {j})")
    return dimension, checked


def _validate_features(features: object, dimension: int) -> list[tuple[object, ...]]:
    if type(features) is not list:
        _fail("features must be a list")
    checked: list[tuple[object, ...]] = []
    seen: set[tuple[object, ...]] = set()
    for position, feature in enumerate(features):
        if type(feature) is not tuple or not feature:
            _fail(f"feature {position} must be a nonempty tuple")
        kind = feature[0]
        if type(kind) is not str:
            _fail(f"feature {position} kind must be a string")
        expected_length = {"f": 2, "l": 2, "s": 3, "t": 4}.get(kind)
        if expected_length is None or len(feature) != expected_length:
            _fail(f"feature {position} has an invalid kind or tuple length")
        indices = feature[1:]
        if any(not _is_int(index) for index in indices):
            _fail(f"feature {position} indices must be integers")
        if any(index < 0 or index >= dimension for index in indices):
            _fail(f"feature {position} index is outside dimension {dimension}")
        if kind == "s" and feature[1] == feature[2]:
            _fail(f"feature {position} requires distinct s indices")
        if kind == "t" and not (feature[1] < feature[2] < feature[3]):
            _fail(f"feature {position} requires strictly increasing t indices")
        if feature in seen:
            _fail(f"duplicate feature at position {position}")
        seen.add(feature)
        checked.append(feature)
    return checked


def _validate_integer_vector(value: object, length: int, name: str) -> list[int]:
    if type(value) is not list or len(value) != length:
        _fail(f"{name} must be a list of length {length}")
    result: list[int] = []
    for index, item in enumerate(value):
        if not _is_int(item):
            _fail(f"{name}[{index}] must be an integer")
        result.append(item)
    return result


def _add_term(poly: Polynomial, monomial: tuple[int, ...], coefficient: int) -> None:
    if not coefficient:
        return
    value = poly.get(monomial, 0) + coefficient
    if value:
        poly[monomial] = value
    else:
        poly.pop(monomial, None)


def _add_scaled(target: Polynomial, source: Polynomial, scale: int) -> None:
    for monomial, coefficient in source.items():
        _add_term(target, monomial, scale * coefficient)


def _scale(poly: Polynomial, scale: int) -> Polynomial:
    result: Polynomial = {}
    _add_scaled(result, poly, scale)
    return result


def _add(poly_a: Polynomial, poly_b: Polynomial) -> Polynomial:
    result = dict(poly_a)
    _add_scaled(result, poly_b, 1)
    return result


def _subtract(poly_a: Polynomial, poly_b: Polynomial) -> Polynomial:
    result = dict(poly_a)
    _add_scaled(result, poly_b, -1)
    return result


def _multiply(poly_a: Polynomial, poly_b: Polynomial) -> Polynomial:
    """Multiply by literal monomial-pair convolution, then collect terms."""
    result: Polynomial = {}
    for monomial_a, coefficient_a in poly_a.items():
        for monomial_b, coefficient_b in poly_b.items():
            monomial = tuple(sorted(monomial_a + monomial_b))
            _add_term(result, monomial, coefficient_a * coefficient_b)
    return result


def _half(poly: Polynomial, context: str) -> Polynomial:
    result: Polynomial = {}
    for monomial, coefficient in poly.items():
        if coefficient % 2:
            _fail(f"{context} has an odd coefficient at monomial {monomial}")
        half = coefficient // 2
        if half:
            result[monomial] = half
    return result


def _feature_threefold(feature: tuple[object, ...]) -> Polynomial:
    """Return the integer polynomial 3*phi for one declared feature."""
    kind = feature[0]
    if kind == "f":
        index = feature[1]
        return {(index, index, index): 1, (index,): -1}
    if kind == "l":
        return {(feature[1],): 3}
    if kind == "s":
        return {tuple(sorted((feature[1], feature[1], feature[2]))): 3}
    if kind == "t":
        return {tuple(sorted(feature[1:])): 3}
    _fail("internal error: unvalidated feature kind")


def _quadratic_minus_six(matrix: list[list[int]]) -> Polynomial:
    """Expand x^T G x by all ordered index pairs, then subtract six."""
    dimension = len(matrix)
    result: Polynomial = {}
    for i in range(dimension):
        for j in range(dimension):
            _add_term(result, tuple(sorted((i, j))), matrix[i][j])
    _add_term(result, (), -6)
    return result


def _linear_form(coefficients: list[int]) -> Polynomial:
    result: Polynomial = {}
    for index, coefficient in enumerate(coefficients):
        _add_term(result, (index,), coefficient)
    return result


def _monomial_comparison_count(left: Polynomial, right: Polynomial) -> int:
    return len(left.keys() | right.keys())


def _compare_exact(left: Polynomial, right: Polynomial, context: str) -> int:
    comparisons = _monomial_comparison_count(left, right)
    if left != right:
        monomial = next(
            monomial
            for monomial in sorted(left.keys() | right.keys())
            if left.get(monomial, 0) != right.get(monomial, 0)
        )
        _fail(
            f"{context} mismatch at monomial {monomial}: "
            f"left={left.get(monomial, 0)}, right={right.get(monomial, 0)}"
        )
    return comparisons


def audit_relations(
    G: list[list[int]],
    features: list[tuple[object, ...]],
    relation_rows: list[dict[int, int]],
) -> tuple[int, int]:
    """Check every relation against literal 3*x_i*(x^T G x - 6)/2.

    Returns ``(number_of_rows, number_of_monomial_comparisons)``. A comparison
    is one monomial key in the union of the two collected row polynomials.
    Every input violation or polynomial mismatch raises ``ValueError``.
    """
    dimension, matrix = _validate_matrix(G)
    checked_features = _validate_features(features, dimension)
    if type(relation_rows) is not list or len(relation_rows) != dimension:
        _fail(f"relation_rows must be a list of length {dimension}")
    feature_polynomials = [_feature_threefold(feature) for feature in checked_features]
    quadratic = _quadratic_minus_six(matrix)
    total_comparisons = 0
    for row_index, row in enumerate(relation_rows):
        if type(row) is not dict:
            _fail(f"relation row {row_index} must be a dict")
        left: Polynomial = {}
        for feature_index, coefficient in row.items():
            if not _is_int(feature_index) or feature_index < 0 or feature_index >= len(checked_features):
                _fail(f"relation row {row_index} has an invalid feature index")
            if not _is_int(coefficient):
                _fail(f"relation row {row_index} coefficient must be an integer")
            _add_scaled(left, feature_polynomials[feature_index], coefficient)

        variable = {(row_index,): 1}
        literal_numerator = _scale(_multiply(variable, quadratic), 3)
        right = _half(literal_numerator, f"relation row {row_index} right-hand side")
        total_comparisons += _compare_exact(
            left, right, f"relation row {row_index}"
        )
    return dimension, total_comparisons


def audit_compression(
    G: list[list[int]],
    v: list[int],
    features: list[tuple[object, ...]],
    compressed8: list[int],
    mu: list[int],
) -> int:
    """Check the exact compressed polynomial identity over every source x.

    ``compressed8`` is indexed by the complete feature list; eliminated
    features are represented by zero coefficients. Returns the number of
    monomial comparisons. Any input violation or mismatch raises ``ValueError``.
    """
    dimension, matrix = _validate_matrix(G)
    checked_features = _validate_features(features, dimension)
    checked_v = _validate_integer_vector(v, dimension, "v")
    checked_mu = _validate_integer_vector(mu, dimension, "mu")
    checked_compressed = _validate_integer_vector(
        compressed8, len(checked_features), "compressed8"
    )

    feature_polynomials = [_feature_threefold(feature) for feature in checked_features]
    left: Polynomial = {}
    for coefficient, feature_poly in zip(checked_compressed, feature_polynomials):
        _add_scaled(left, feature_poly, coefficient)

    linear_v = _linear_form(checked_v)
    linear_v_cubed = _multiply(_multiply(linear_v, linear_v), linear_v)
    first_rhs_term = _scale(
        _subtract(linear_v_cubed, _scale(linear_v, 4)), 8
    )

    linear_mu = _linear_form(checked_mu)
    quadratic = _quadratic_minus_six(matrix)
    correction_product = _multiply(linear_mu, quadratic)
    correction_term = _scale(
        _half(correction_product, "compression correction term"), 3
    )
    right = _subtract(first_rhs_term, correction_term)
    return _compare_exact(left, right, "compression identity")


def _selfcheck() -> float:
    start = perf_counter()
    features: list[tuple[object, ...]] = [
        ("f", 0), ("f", 1), ("f", 2),
        ("l", 0), ("l", 1), ("l", 2),
        ("s", 0, 1), ("s", 0, 2), ("s", 1, 0),
        ("s", 1, 2), ("s", 2, 0), ("s", 2, 1),
        ("t", 0, 1, 2),
    ]
    feature_index = {feature: index for index, feature in enumerate(features)}
    matrix = [
        [6, 1, 2],
        [1, 6, 3],
        [2, 3, 6],
    ]
    rows = [
        {
            feature_index[("f", 0)]: 9,
            feature_index[("s", 0, 1)]: 1,
            feature_index[("s", 0, 2)]: 2,
            feature_index[("s", 1, 0)]: 3,
            feature_index[("s", 2, 0)]: 3,
            feature_index[("t", 0, 1, 2)]: 3,
        },
        {
            feature_index[("f", 1)]: 9,
            feature_index[("s", 0, 1)]: 3,
            feature_index[("s", 1, 0)]: 1,
            feature_index[("s", 1, 2)]: 3,
            feature_index[("s", 2, 1)]: 3,
            feature_index[("t", 0, 1, 2)]: 2,
        },
        {
            feature_index[("f", 2)]: 9,
            feature_index[("s", 0, 2)]: 3,
            feature_index[("s", 1, 2)]: 3,
            feature_index[("s", 2, 0)]: 2,
            feature_index[("s", 2, 1)]: 3,
            feature_index[("t", 0, 1, 2)]: 1,
        },
    ]
    row_count, relation_comparisons = audit_relations(matrix, features, rows)
    if row_count != 3 or relation_comparisons != 21:
        _fail("relation selfcheck returned unexpected counts")

    compressed = [0] * len(features)
    compressed[feature_index[("f", 0)]] = 46
    compressed[feature_index[("s", 0, 1)]] = -2
    compressed[feature_index[("s", 0, 2)]] = -4
    compressed[feature_index[("s", 1, 0)]] = -6
    compressed[feature_index[("s", 2, 0)]] = -6
    compressed[feature_index[("t", 0, 1, 2)]] = -6
    compression_comparisons = audit_compression(
        matrix, [2, 0, 0], features, compressed, [2, 0, 0]
    )
    if compression_comparisons != 7:
        _fail("compression selfcheck returned unexpected comparison count")

    bad_rows = [dict(row) for row in rows]
    bad_rows[0][feature_index[("f", 0)]] -= 1
    try:
        audit_relations(matrix, features, bad_rows)
    except ValueError:
        pass
    else:
        _fail("relation corruption control was accepted")

    bad_compressed = list(compressed)
    bad_compressed[feature_index[("s", 0, 1)]] -= 1
    try:
        audit_compression(matrix, [2, 0, 0], features, bad_compressed, [2, 0, 0])
    except ValueError:
        pass
    else:
        _fail("compression corruption control was accepted")

    try:
        audit_relations([[6, 0], [1, 6]], [("f", 0)], [{0: 9}, {}])
    except ValueError:
        pass
    else:
        _fail("invalid-matrix control was accepted")

    try:
        audit_compression([[6]], [2], [([], 0)], [0], [0])
    except ValueError:
        pass
    else:
        _fail("invalid-feature-type control was accepted")

    return perf_counter() - start


if __name__ == "__main__":
    elapsed = _selfcheck()
    print(f"PASS_NORM6_SYMBOLIC_POLYNOMIAL_ORACLE elapsed_s={elapsed:.6f}")
