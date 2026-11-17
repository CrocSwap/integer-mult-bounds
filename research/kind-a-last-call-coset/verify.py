"""Exact target-orbit span checks for the kind A finishing criterion."""

from fractions import Fraction


Matrix = tuple[int, ...]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def apply(matrix: Matrix, vector: int) -> int:
    image = 0
    for index, column in enumerate(matrix):
        if vector & (1 << index):
            image ^= column
    return image


def compose(left: Matrix, right: Matrix) -> Matrix:
    return tuple(apply(left, column) for column in right)


def transvection(m: int, normal: int) -> Matrix:
    x_mask = (1 << m) - 1
    paired = ((normal & x_mask) << m) | (normal >> m)
    return tuple(
        (1 << index) ^ (normal if paired & (1 << index) else 0)
        for index in range(2 * m)
    )


def axis_permutation(axes: tuple[int, ...]) -> Matrix:
    m = len(axes)
    return tuple(1 << (index + shift) for shift in (0, m) for index in axes)


def level(matrix: Matrix) -> int:
    m = len(matrix) // 2
    mask = (1 << m) - 1
    images = {apply(matrix, z << m) & mask for z in range(1 << m)}
    return len(images).bit_length() - 1


def is_free(matrix: Matrix) -> bool:
    m = len(matrix) // 2
    mask = (1 << m) - 1
    return all(column & mask == 0 for column in matrix[m:])


def target_orbit(target: Matrix, gamma: Matrix, order: int) -> list[Matrix]:
    orbit = [target]
    for _ in range(1, order):
        orbit.append(compose(orbit[-1], gamma))
    require(len(set(orbit)) == order, "target orbit closed early")
    require(compose(orbit[-1], gamma) == target, "target orbit did not close")
    return orbit


def orbit_columns(
    orbit: list[Matrix], first: Matrix, shared: Matrix, last: Matrix, c: Fraction
) -> list[list[Fraction]]:
    """Restrict each possible generator to the orbit of the normalized target."""
    size = len(orbit)
    columns = []
    for index, term in enumerate(orbit):
        after_last_inverse = compose(last, term)
        for candidate in (term, after_last_inverse):
            if is_free(candidate) or is_free(compose(candidate, first)):
                column = [Fraction(0)] * size
                column[index] = Fraction(1)
                columns.append(column)
            if is_free(compose(candidate, shared)):
                column = [Fraction(0)] * size
                column[index] = Fraction(1)
                column[(index + 1) % size] += c
                columns.append(column)
    return columns


def rank(columns: list[list[Fraction]], size: int) -> int:
    pivots: dict[int, list[Fraction]] = {}
    for column in columns:
        for index in range(size):
            entry = column[index]
            if not entry:
                continue
            if index not in pivots:
                pivots[index] = [value / entry for value in column]
                break
            column = [
                value - entry * pivot
                for value, pivot in zip(column, pivots[index], strict=True)
            ]
    return len(pivots)


def spans_target(columns: list[list[Fraction]], size: int) -> bool:
    target = [Fraction(1)] + [Fraction(0)] * (size - 1)
    return rank(columns, size) == rank([*columns, target], size)


def check_case(
    name: str, gamma: Matrix, order: int, c: Fraction, same_frame: bool, expected: bool
) -> None:
    m = len(gamma) // 2
    first, shared, last = (transvection(m, 1 << axis) for axis in range(3))
    target = compose(last, shared)
    second = compose(shared, gamma)
    require(is_free(gamma), f"{name}: gamma must be free")
    require(level(compose(shared, first)) == 2, f"{name}: middle level")
    require(level(compose(target, first)) == 3, f"{name}: target level")
    require(is_free(compose(second, shared)) == same_frame, f"{name}: frame relation")
    raw_extra = is_free(compose(second, first))
    require(raw_extra == (name == "raw extra term"), f"{name}: raw support")
    orbit = target_orbit(target, gamma, order)
    columns = orbit_columns(orbit, first, shared, last, c)
    require(spans_target(columns, order) == expected, f"{name}: wrong finishability")

    if name == "post-call free operation":
        require(compose(gamma, target) == orbit[1], "free translate must swap endpoints")
        require([Fraction(1), c] in columns, "missing direct paid output")
        with_post_call_free = [*columns, [c, Fraction(1)]]
        require(spans_target(with_post_call_free, order), "post-call control must finish")


def main() -> None:
    cross = compose(
        transvection(5, (1 << 6) | (1 << 8)),
        compose(transvection(5, 1 << 6), transvection(5, 1 << 8)),
    )
    require(
        compose(cross, transvection(5, 2)) != compose(transvection(5, 2), cross),
        "same-frame fixture must distinguish stabilizing a frame from commuting",
    )
    order_three = axis_permutation((0, 1, 2, 4, 5, 3))
    cases = (
        ("distinct frames on one axis", transvection(5, 1 << 6), 2, Fraction(3), False, False),
        ("distinct frames on two axes", axis_permutation((0, 3, 2, 1, 4, 5)),
         2, Fraction(-2, 3), False, False),
        ("same frame order two with invertible binomial", cross, 2, Fraction(-2, 3), True, True),
        ("same frame order two with singular binomial", cross, 2, Fraction(1), True, False),
        ("same frame order three with invertible binomial", order_three, 3, Fraction(3, 2), True, True),
        ("same frame order three with singular binomial", order_three, 3, Fraction(-1), True, False),
        ("raw extra term", axis_permutation((1, 0, 2, 3, 4)), 2, Fraction(3), False, True),
        ("post-call free operation", axis_permutation((0, 2, 1, 3, 4)), 2, Fraction(3), False, False),
    )
    for case in cases:
        check_case(*case)
    print(f"PASS_KIND_A_LAST_CALL_COSET cases={len(cases)} post_call_control=1")


if __name__ == "__main__":
    main()
