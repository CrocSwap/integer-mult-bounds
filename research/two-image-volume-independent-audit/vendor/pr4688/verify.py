#!/usr/bin/env python3
"""Exact Gaussian-integer ranks for a two-image block-3 prefix.

Standard library only; no input files, floating point, assertions, or outputs
other than the report. See README.md for the mathematical scope.
"""

from itertools import combinations, permutations, product


ZERO, ONE, MINUS_I = (0, 0), (1, 0), (0, -1)
I_POWERS = (ONE, (0, 1), (-1, 0), MINUS_I)
SUBSETS = tuple(combinations(range(8), 4))
BASIS = tuple((x, subset) for x in range(8) for subset in SUBSETS)
INDEX = {label: index for index, label in enumerate(BASIS)}
CUTS = (2, 3, 6, 7, 8, 9, 12, 13)
U_PERM = tuple(x ^ ((x & 1) << 2) for x in range(8))
V_PERM = tuple(x ^ (((x ^ (x >> 1)) & 1) * 3) for x in range(8))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def sub(a, b):
    return a[0] - b[0], a[1] - b[1]


def mul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def gaussian_divide(a, b):
    denominator = b[0] ** 2 + b[1] ** 2
    require(denominator != 0, "division by zero")
    real = a[0] * b[0] + a[1] * b[1]
    imag = a[1] * b[0] - a[0] * b[1]
    require(real % denominator == imag % denominator == 0,
            "Gaussian division is not exact")
    return real // denominator, imag // denominator


def gaussian_gcd(a, b):
    """Euclidean gcd, up to a unit, using nearest integer quotients."""
    while b != ZERO:
        denominator = b[0] ** 2 + b[1] ** 2
        quotient = (
            (a[0] * b[0] + a[1] * b[1] + denominator // 2) // denominator,
            (a[1] * b[0] - a[0] * b[1] + denominator // 2) // denominator,
        )
        a, b = b, sub(a, mul(quotient, b))
    return a


def accumulate(vector, index, coefficient):
    value = add(vector.get(index, ZERO), coefficient)
    if value == ZERO:
        vector.pop(index, None)
    else:
        vector[index] = value


def wedge_sign(addresses):
    if len(set(addresses)) != len(addresses):
        return 0
    inversions = sum(addresses[i] > addresses[j]
                     for i in range(len(addresses))
                     for j in range(i + 1, len(addresses)))
    return -1 if inversions % 2 else 1


def lift_direction(direction):
    """Columns of rho(I - i X_direction) on V tensor exterior^4 V."""
    require(1 <= direction < 8, "direction must be nonzero")
    columns = []
    for x, subset in BASIS:
        column = {}
        for choices in product((0, 1), repeat=5):
            images = tuple(t ^ (direction if choice else 0)
                           for t, choice in zip(subset, choices[1:]))
            sign = wedge_sign(images)
            if not sign:
                continue
            phase = I_POWERS[-sum(choices) % 4]
            row = INDEX[x ^ (direction if choices[0] else 0), tuple(sorted(images))]
            accumulate(column, row, (sign * phase[0], sign * phase[1]))
        columns.append(column)
    return columns


def apply_permutation(permutation, columns):
    """Apply rho(P), retaining the sign from sorting each exterior basis."""
    require(sorted(permutation) == list(range(8)), "not a permutation")
    action = []
    for x, subset in BASIS:
        images = tuple(permutation[t] for t in subset)
        action.append((INDEX[permutation[x], tuple(sorted(images))], wedge_sign(images)))
    return [{action[j][0]: (action[j][1] * value[0], action[j][1] * value[1])
             for j, value in column.items()} for column in columns]


def compose(left, right):
    columns = []
    for column in right:
        result = {}
        for j, coefficient in column.items():
            for i, value in left[j].items():
                accumulate(result, i, mul(value, coefficient))
        columns.append(result)
    return columns


def add_columns(left, right):
    columns = []
    for a, b in zip(left, right):
        result = a.copy()
        for i, value in b.items():
            accumulate(result, i, value)
        columns.append(result)
    return columns


def scale_columns(columns, scalar):
    return [{j: mul((scalar, 0), value) for j, value in column.items()}
            for column in columns]


def orbit_number(x, subset):
    nonplane = int(bool(subset[0] ^ subset[1] ^ subset[2] ^ subset[3]))
    return 2 * int(x not in subset) + nonplane


def cut_indices(mask):
    return tuple(i for i, label in enumerate(BASIS)
                 if mask & (1 << orbit_number(*label)))


def project(columns, indices):
    """Rows of the map N -> H/N, in coordinate bases."""
    inside = set(indices)
    rows = {i: {} for i in range(len(BASIS)) if i not in inside}
    for column_index, j in enumerate(indices):
        for i, value in columns[j].items():
            if i in rows:
                rows[i][column_index] = value
    return list(rows.values())


def rank_exact(rows):
    """Rank over Q(i), using span-preserving operations in Z[i].

    Multiply a row by a nonzero pivot, subtract a pivot-row multiple, and
    divide by a nonzero common Gaussian divisor. Content removal keeps the
    coefficients small. This computes exact rank, not a modular lower bound.
    """
    pivots = {}
    for source in rows:
        row = source.copy()
        while row:
            column = min(row)
            if column not in pivots:
                pivots[column] = row
                break
            pivot = pivots[column]
            a, b = row[column], pivot[column]
            row = {j: mul(b, value) for j, value in row.items()}
            for j, value in pivot.items():
                coefficient = mul(a, value)
                accumulate(row, j, (-coefficient[0], -coefficient[1]))
            if row:
                common = ZERO
                for value in row.values():
                    common = gaussian_gcd(common, value)
                    if common[0] ** 2 + common[1] ** 2 == 1:
                        break
                if common[0] ** 2 + common[1] ** 2 > 1:
                    row = {j: gaussian_divide(value, common) for j, value in row.items()}
    return len(pivots)


def check_lift(direction):
    """Check every entry against a separate determinant definition."""
    matrix = [[ZERO for _ in range(8)] for _ in range(8)]
    for x in range(8):
        matrix[x][x] = ONE
        matrix[x ^ 1][x] = MINUS_I
    orders = tuple((order, wedge_sign(order)) for order in permutations(range(4)))
    minors = {}
    for rows in SUBSETS:
        for cols in SUBSETS:
            total = ZERO
            for order, sign in orders:
                term = (sign, 0)
                for i in range(4):
                    term = mul(term, matrix[rows[i]][cols[order[i]]])
                total = add(total, term)
            minors[rows, cols] = total
    for j, (x, cols) in enumerate(BASIS):
        for i, (y, rows) in enumerate(BASIS):
            expected = mul(matrix[y][x], minors[rows, cols])
            require(direction[j].get(i, ZERO) == expected, "exterior lift disagrees with minor")


def reject_rank(rows, incorrect, label):
    observed = rank_exact(rows)
    require(observed != incorrect, "negative control was accepted: " + label)


def main():
    require(tuple(sum(orbit_number(*label) == j for label in BASIS) for j in range(4))
            == (56, 224, 56, 224), "coordinate class sizes changed")
    direction = lift_direction(1)
    check_lift(direction)
    identity = [{j: ONE} for j in range(len(BASIS))]
    shift = apply_permutation(tuple(x ^ 1 for x in range(8)), identity)
    expected_square = [{i: mul((0, -32), value) for i, value in column.items()}
                       for column in shift]
    require(compose(direction, direction) == expected_square,
            "rho(I-iX)^2 must equal -32i rho(X)")
    first_branch = compose(direction, apply_permutation(U_PERM, direction))
    second_branch = compose(direction, apply_permutation(V_PERM, direction))
    combined = add_columns(first_branch, scale_columns(second_branch, 2))
    singular_variant = add_columns(first_branch, second_branch)
    target = compose(lift_direction(4), compose(lift_direction(2), direction))

    print("mask dim first U-only V-only joint final lambda=1-final target", flush=True)
    for mask in CUTS:
        indices = cut_indices(mask)
        first = project(direction, indices)
        values = (rank_exact(first),
                  rank_exact(first + project(first_branch, indices)),
                  rank_exact(first + project(second_branch, indices)),
                  rank_exact(first + project(combined, indices)),
                  rank_exact(project(combined, indices)),
                  rank_exact(project(singular_variant, indices)),
                  rank_exact(project(target, indices)))
        require(values == (80, 152, 152, 160, 160, 160, 224),
                "rank profile failed for cut " + str(mask))
        print(mask, len(indices), *values, flush=True)

    indices = cut_indices(2)
    first = project(direction, indices)
    reject_rank(first + project(first_branch, indices), 160, "delete V branch")
    reject_rank(first + project(second_branch, indices), 160, "delete U branch")
    reject_rank(first + project(add_columns(first_branch, first_branch), indices),
                160, "duplicate U branch")
    square = compose(direction, direction)
    reject_rank(first + project(add_columns(first_branch, square), indices),
                160, "replace V by identity")
    reject_rank(first, 79, "undercount first call")

    # R = U^{-1} V has cycles of lengths 1, 1, 2, 4. Its fourth power is I.
    require(all(U_PERM[U_PERM[x]] == V_PERM[V_PERM[x]] == x for x in range(8)),
            "U and V must be involutions")
    ratio = tuple(U_PERM[V_PERM[x]] for x in range(8))
    remaining, lengths = set(range(8)), []
    while remaining:
        start = min(remaining)
        cycle, x = [], start
        while x not in cycle:
            cycle.append(x)
            remaining.remove(x)
            x = ratio[x]
        require(x == start, "invalid permutation cycle")
        lengths.append(len(cycle))
    require(sorted(lengths) == [1, 1, 2, 4], "ratio cycle type changed")

    # Polynomial identity (I+2R)(I-2R+4R^2-8R^3) = -15I for R^4=I.
    polynomial = [0] * 4
    for i, a in enumerate((1, 2)):
        for j, b in enumerate((1, -2, 4, -8)):
            polynomial[(i + j) % 4] += a * b
    require(polynomial == [-15, 0, 0, 0], "uniform inverse identity failed")

    # Independent cycle enumeration at widths 1, 2, 3 checks the all-width
    # nullity formula of the lambda=1 negative control.
    for width in (1, 2, 3):
        remaining = set(product(range(8), repeat=width))
        even_cycles = 0
        while remaining:
            start = min(remaining)
            x, length = start, 0
            while True:
                remaining.remove(x)
                length += 1
                x = tuple(ratio[t] for t in x)
                if x == start:
                    break
            even_cycles += int(length % 2 == 0)
        require(even_cycles == (8 ** width + 4 ** width - 2 * 2 ** width) // 4,
                "singular-variant nullity formula failed")
        require(even_cycles > 0, "lambda=1 incorrectly accepted as invertible")

    # Mixing acts outside the tensor lift: on e_1 tensor e_1, the incorrect
    # (U+V) tensor (U+V) has the cross term e_5 tensor e_2; the true sum does not.
    tensor_sum, sum_tensor = {}, {}
    for permutation in (U_PERM, V_PERM):
        accumulate(tensor_sum, (permutation[1], permutation[1]), ONE)
    for p, q in product((U_PERM, V_PERM), repeat=2):
        accumulate(sum_tensor, (p[1], q[1]), ONE)
    require(tensor_sum.get((5, 2), ZERO) == ZERO
            and sum_tensor[(5, 2)] == ONE, "width-two lift control failed")
    print("PASS_CONTROLS 7", flush=True)
    print("PASS_COMPLEX_TWO_IMAGE_HOOK_PREFIX", flush=True)


if __name__ == "__main__":
    main()
