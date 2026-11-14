#!/usr/bin/env python3
"""Independent exact challenge of the proposed R/M/E odd-coset map."""

from __future__ import annotations

import itertools
import json


H = (
    (1, 1, 1, 1),
    (1, -1, 1, -1),
    (1, 1, -1, -1),
    (1, -1, -1, 1),
)
J = (1, 1, 1, -1)
S = (1, -1, -1, 1)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def matvec(matrix, vector):
    return tuple(sum(matrix[i][j] * vector[j] for j in range(4))
                 for i in range(4))


def norm_squared(vector):
    return sum(value * value for value in vector)


def parity(vector):
    return sum(vector) & 1


def score2(twice_t, axis):
    """Twice the invariant lower-magnitude score of this coordinate pair."""
    magnitude = abs(twice_t[axis])
    require(magnitude % 2 == 1, "coordinate is not half-integral")
    if axis < 2:
        return 4 * ((magnitude - 1) // 4) + 1
    if magnitude == 1:
        return 0
    return 4 * ((magnitude - 3) // 4) + 3


def toggle_pair(twice_t):
    """The coordinate-magnitude involution M, in doubled coordinates."""
    require(len(twice_t) == 4 and all(value % 2 for value in twice_t),
            "M requires four half-integer coordinates")
    axis = min(range(4), key=lambda i: (score2(twice_t, i), i))
    result = list(twice_t)
    magnitude = abs(result[axis])
    if axis >= 2 and magnitude == 1:
        result[axis] = -result[axis]
    else:
        low = score2(twice_t, axis)
        high = low + 2
        require(magnitude in (low, high), "coordinate is outside its pair")
        sign = 1 if result[axis] > 0 else -1
        result[axis] = sign * (high if magnitude == low else low)
    return tuple(result)


def odd_map(x):
    """F(x)=E M R x for odd x; all arithmetic is integer exact."""
    require(parity(x) == 1, "odd map requires odd-total-parity input")
    dot = sum(S[i] * x[i] for i in range(4))
    require(dot % 2 == 1, "s dot x must be odd")
    twice_t = tuple(2 * x[i] - dot * S[i] for i in range(4))
    require(all(value % 2 for value in twice_t),
            "R must produce four half-integer coordinates")
    require((sum(twice_t) // 2) % 2 == 1,
            "R must produce odd coordinate sum")
    twice_m = toggle_pair(twice_t)
    require((sum(twice_m) // 2) % 2 == 0,
            "M must flip odd coordinate sum to even")
    hjm = matvec(H, twice_m)
    require(all(value % 4 == 0 for value in hjm),
            "E must produce an integer output")
    y = tuple(J[i] * (hjm[i] // 4) for i in range(4))
    require(parity(y) == 1, "E must produce odd-total-parity output")
    return y


def odd_inverse(y):
    """F^{-1}(y)=R M E^{-1} y for odd y."""
    require(parity(y) == 1, "odd inverse requires odd output")
    jy = tuple(J[i] * y[i] for i in range(4))
    twice_t = matvec(H, jy)  # t=UJy, represented as 2t.
    require(all(value % 2 for value in twice_t),
            "E inverse must produce half-integers")
    require((sum(twice_t) // 2) % 2 == 0,
            "E inverse must produce even-sum half-integers")
    twice_m = toggle_pair(twice_t)
    require((sum(twice_m) // 2) % 2 == 1,
            "M inverse step must return to odd-sum half-integers")
    dot = sum(S[i] * twice_m[i] for i in range(4))
    numerator = tuple(2 * twice_m[i] - dot * S[i] for i in range(4))
    require(all(value % 4 == 0 for value in numerator),
            "R must return integer coordinates")
    x = tuple(value // 4 for value in numerator)
    require(parity(x) == 1, "odd inverse must return odd input")
    return x


def even_map(x):
    require(parity(x) == 0, "even map requires even-total-parity input")
    hx = matvec(H, x)
    require(all(value % 2 == 0 for value in hx),
            "even input must have integral U image")
    y = tuple(value // 2 for value in hx)
    require(parity(y) == 0, "exact U must preserve even total parity")
    return y


def even_inverse(y):
    require(parity(y) == 0, "even inverse requires even output")
    hy = matvec(H, y)
    require(all(value % 2 == 0 for value in hy),
            "even output must have integral U inverse")
    return tuple(value // 2 for value in hy)


def full_map(x):
    return even_map(x) if parity(x) == 0 else odd_map(x)


def full_inverse(y):
    return even_inverse(y) if parity(y) == 0 else odd_inverse(y)


def half_slack_exact(m, n):
    d = 4 * m + 4 * n - 1
    return d <= 0 or d * d <= 64 * m * n


def check_matrix_identities():
    h2 = tuple(
        tuple(sum(H[i][k] * H[k][j] for k in range(4)) for j in range(4))
        for i in range(4)
    )
    require(h2 == tuple(tuple(4 if i == j else 0 for j in range(4))
                        for i in range(4)), "H^2 != 4I")
    # Directly check U J U = I - ss^T/2 after clearing denominators.
    for i in range(4):
        for j in range(4):
            numerator = sum(H[i][k] * J[k] * H[k][j] for k in range(4))
            expected = 4 * (1 if i == j else 0) - 2 * S[i] * S[j]
            require(numerator == expected, "R=UJU reflection formula fails")
    return {
        "H_symmetric": all(H[i][j] == H[j][i]
                           for i in range(4) for j in range(4)),
        "H_squared_equals_4I": True,
        "R_equals_I_minus_ssT_over_2": True,
    }


def check_pair_involution():
    values = tuple(range(-15, 16, 2))
    tested = 0
    tie_examples = 0
    central_examples = 0
    for point in itertools.product(values, repeat=4):
        moved = toggle_pair(point)
        require(toggle_pair(moved) == point, "M is not an involution")
        differences = [moved[i] - point[i] for i in range(4)]
        require(sum(value != 0 for value in differences) == 1
                and all(value == 0 or abs(value) == 2 for value in differences),
                "M must toggle exactly one coordinate by one")
        require(abs(sum(point) - sum(moved)) == 2,
                "M must change coordinate sum by exactly one")
        require((sum(point) // 2) % 2 != (sum(moved) // 2) % 2,
                "M must flip integer sum parity")
        scores = [score2(point, i) for i in range(4)]
        selected = min(range(4), key=lambda i: (scores[i], i))
        after_scores = [score2(moved, i) for i in range(4)]
        require(scores == after_scores, "pair scores changed under M")
        require(selected == min(range(4), key=lambda i: (after_scores[i], i)),
                "tie-broken selected coordinate changed")
        tie_examples += len(set(scores)) < 4
        central_examples += scores[selected] == 0
        tested += 1
    return {
        "half_integer_vectors_tested": tested,
        "tie_examples": tie_examples,
        "central_pair_examples": central_examples,
    }


def check_point(x):
    y = full_map(x)
    back = full_inverse(y)
    require(back == x, f"inverse fails for {x} -> {y} -> {back}")
    require(parity(y) == parity(x), "full map fails parity preservation")
    if parity(x) == 0:
        hx = matvec(H, x)
        error2_numerators = tuple(2 * y[i] - hx[i] for i in range(4))
        require(error2_numerators == (0, 0, 0, 0),
                "even map is not exact U")
        require(norm_squared(y) == norm_squared(x),
                "even map changes norm")
        return y

    hx = matvec(H, x)
    error2_numerators = tuple(2 * y[i] - hx[i] for i in range(4))
    require(all(abs(value) == 1 for value in error2_numerators),
            "odd map output is not one of the 16 nearest corners")
    require(sum(value * value for value in error2_numerators) == 4,
            "odd map error is not exactly one")
    m = norm_squared(y)
    n = norm_squared(x)
    require(half_slack_exact(m, n),
            f"bilateral radial half-slack fails for {x}: m={m}, n={n}")
    return y


def odd_points_in_ball(radius):
    for x in itertools.product(range(-radius, radius + 1), repeat=4):
        if parity(x) == 1 and norm_squared(x) <= radius * radius:
            yield x


def check_named_balls():
    results = []
    for radius in (5, 9, 11):
        seen = set()
        count = 0
        for x in odd_points_in_ball(radius):
            y = check_point(x)
            require(y not in seen, f"finite map collision at R={radius}: {y}")
            seen.add(y)
            count += 1
        results.append({"radius": radius, "odd_inputs_checked": count,
                        "distinct_outputs": len(seen)})
    return results


def check_large_inputs():
    cases = []
    for exponent in (0, 1, 2, 10, 64, 256, 1024):
        n = 1 << exponent
        second = (-n, 0, 0, 1) if exponent else (-1, 0, 0, 0)
        for x in (
            (n, 1, -n, 0),
            second,
            (n, -n + 1, 2, 0),
            (0, n, -1, -n),
        ):
            require(parity(x) == 1, "large test vector is not odd")
            y = check_point(x)
            require(full_inverse(y) == x, "large explicit inverse failed")
            cases.append({
                "exponent": exponent,
                "input": [str(value) for value in x],
                "output": [str(value) for value in y],
                "input_norm_squared_digits": len(str(norm_squared(x))),
                "output_norm_squared_digits": len(str(norm_squared(y))),
            })
    return cases


def check_even_examples():
    cases = []
    for exponent in (0, 1, 64, 1024):
        n = 1 << exponent
        for x in ((n, -n, 0, 0), (n, n, 0, 0)):
            y = even_map(x)
            require(even_inverse(y) == x, "even exact-U inverse failed")
            require(norm_squared(y) == norm_squared(x),
                    "even exact-U map changed norm")
            cases.append({
                "exponent": exponent,
                "input": [str(value) for value in x],
                "output": [str(value) for value in y],
            })
    return cases


def check_exact_radial_bound_algebra():
    # The symbolic proof uses q=2a+1 and r^2 >= q^2+1.
    checks = []
    for twice_a in range(1, 2001, 2):
        # a is a positive half-integer; q=2a+1 is integer.
        q = twice_a + 1
        lower_norm_squared = twice_a * twice_a + 2 * twice_a + 2
        # With a=twice_a/2, this is 4a^2+4a+2 = q^2+1.
        require(lower_norm_squared == q * q + 1,
                "radial lower endpoint identity fails")
        high_norm_squared = lower_norm_squared + q
        # Both endpoint radii exceed q, so q/(r+r') < 1/2 exactly.
        require(lower_norm_squared > q * q and high_norm_squared > q * q,
                "radial denominator is not strictly greater than 2q")
        checks.append(q)
    return {"half_integer_lower_scores_checked": len(checks),
            "max_q_checked": max(checks)}


def main():
    matrix = check_matrix_identities()
    pairing = check_pair_involution()
    balls = check_named_balls()
    large = check_large_inputs()
    even = check_even_examples()
    radial = check_exact_radial_bound_algebra()
    print(json.dumps({
        "status": "PASS",
        "method": "separate exact integer matrix/coordinate-pair implementation",
        "matrix_identities": matrix,
        "pairing_check": pairing,
        "named_odd_balls": balls,
        "large_round_trip_examples": large,
        "even_exact_round_trip_examples": even,
        "large_exponents": [0, 1, 2, 10, 64, 256, 1024],
        "radial_algebra_check": radial,
        "limitations": [
            "finite point checks are only R=5,9,11",
            "the uniform radial proof is algebraic and uses the stated phase-score rules",
            "no finite-period construction or global claim is inferred from the finite balls",
        ],
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
