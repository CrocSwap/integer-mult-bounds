#!/usr/bin/env python3
"""Check the changed Gaussian edges and orbit lengths using integers."""

type Point = tuple[int, int]
type Pair = tuple[int, int, int, int]
type Cycle = tuple[Point, Point, Point, Point]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def negate(point: Point) -> Point:
    x, y = point
    return -x, -y


def tangent_cycle(left_x: int, y: int, inner: bool) -> Cycle:
    """Use one top-side pair of the specified annular matching."""
    low, high = (-y + 2, y - 2) if inner else (-y + 4, y)
    require(low <= left_x <= high - 2 and (left_x - low) % 4 == 0,
            "top side does not contain the required pair")
    left, right = (left_x, y), (left_x + 2, y)
    source, mate = (right, left) if (left_x + y) % 4 else (left, right)
    rotated_mate = (mate[1], -mate[0])
    return source, rotated_mate, negate(source), negate(rotated_mate)


def splice(cycles: list[Cycle], switches: int) -> dict[Point, Point]:
    require(0 <= switches < len(cycles), "invalid number of switches")
    successors: dict[Point, Point] = {}
    for cycle in cycles:
        for index, source in enumerate(cycle):
            successors[source] = cycle[(index + 1) % 4]
    for index in range(switches):
        side = 2 * (index % 2)
        left = cycles[index][side]
        right = cycles[index + 1][side]
        successors[left], successors[right] = successors[right], successors[left]
    return successors


def orbit_length(start: Point, successors: dict[Point, Point]) -> int:
    point = start
    for length in range(1, len(successors) + 1):
        point = successors[point]
        if point == start:
            return length
    raise ValueError("orbit did not close within the population")


def gaussian_pair(point: Point) -> Pair:
    """Invert the doubled half-grid coordinates in the sum-one fiber."""
    x, y = point
    require(x % 2 == 1 and y % 2 == 1 and (x + y) % 4 == 0,
            "point lies outside the sum-one source color")
    difference_real, difference_imag = (x - y) // 2, -(x + y) // 2
    return ((1 + difference_real) // 2, difference_imag // 2,
            (1 - difference_real) // 2, -difference_imag // 2)


def four_times_error(source: Pair, target: Pair) -> int:
    left_real, left_imag, right_real, right_imag = source
    dr, di = left_real - right_real, left_imag - right_imag
    twice_ideal = (1 - di, dr, 1 + di, -dr)
    return sum((2 * actual - ideal) ** 2
               for actual, ideal in zip(target, twice_ideal, strict=True))


def within_radial_bound(source: Pair, target: Pair, num: int, den: int) -> bool:
    """Compare the squared absolute norm change with num/den."""
    u = sum(value * value for value in source)
    v = sum(value * value for value in target)
    scaled_sum = den * (u + v) - num
    return scaled_sum <= 0 or scaled_sum ** 2 <= 4 * den ** 2 * u * v


def check_case(period: int, cutoff: int) -> tuple[int, int]:
    require(period % 4 == 0 and cutoff >= 5 and cutoff % 2 == 1,
            "invalid period fixture")
    require(period % cutoff != 0 and all(period % r == 0 for r in range(5, cutoff, 2)),
            "fixture does not use the first incompatible ring")
    count = period // 4
    radius = cutoff + 4 * (cutoff * (2 * count + 4) + 1)
    cycles = [tangent_cycle(radius - 4, radius + 2 * j, j % 2 == 0)
              for j in range(count)]
    before = splice(cycles, 0)
    after = splice(cycles, count - 1)
    require(len(after) == period and set(after) == set(after.values()),
            "edited orbits do not form a permutation")
    require(orbit_length(cycles[0][0], after) == period, "incorrect least orbit period")

    changed = 0
    bound_num, bound_den = (4 * cutoff + 1) ** 2, 32 * cutoff ** 2
    for source, target in after.items():
        source_pair, target_pair = gaussian_pair(source), gaussian_pair(target)
        require(four_times_error(source_pair, target_pair) == 4, "incorrect Gaussian error")
        require(within_radial_bound(source_pair, target_pair, bound_num, bound_den),
                "Gaussian edge exceeds the radial allowance")
        changed += target != before[source]
    require(changed == 2 * (count - 1), "incorrect count of switched successors")
    return len(after), changed


def check_controls() -> None:
    cycles = [tangent_cycle(177 - 4, 177 + 2 * j, j % 2 == 0) for j in range(3)]
    start = cycles[0][0]
    require(orbit_length(start, splice(cycles, 0)) == 4, "missing switches control failed")
    require(orbit_length(start, splice(cycles, 1)) == 8, "skipped last switch control failed")

    same_side = splice(cycles, 1)
    left, right = cycles[1][0], cycles[2][0]
    same_side[left], same_side[right] = same_side[right], same_side[left]
    require(four_times_error(gaussian_pair(right), gaussian_pair(same_side[right])) > 4,
            "overlapping same-side switches should create a nonunit edge")

    axis_cycles = [tangent_cycle(1, 169, True), tangent_cycle(1, 171, False)]
    axis_map = splice(axis_cycles, 1)
    source = axis_cycles[0][0]
    source_pair, target_pair = gaussian_pair(source), gaussian_pair(axis_map[source])
    require(four_times_error(source_pair, target_pair) == 4, "axis edge lost unit error")
    require(not within_radial_bound(source_pair, target_pair, 16, 25),
            "near-axis switch should exceed even the looser radial bound 4/5")


def main() -> None:
    fixtures = (
        (4, 5), (8, 5), (12, 5), (16, 5), (20, 7),
        (24, 5), (28, 5), (36, 5), (48, 5), (56, 5),
        (60, 7), (72, 5), (84, 5), (140, 9), (180, 7),
        (252, 5), (360, 7), (420, 9), (1260, 11), (13860, 13),
    )
    edges = switched = 0
    for period, cutoff in fixtures:
        checked_edges, changed_edges = check_case(period, cutoff)
        edges += checked_edges
        switched += changed_edges
    check_controls()
    print("PASS_GAUSSIAN_ROUNDER_EXACT_PERIOD")
    print(f"{len(fixtures)} orbit fixtures; {edges} Gaussian edges; "
          f"{switched} switched successors; 4 controls")


if __name__ == "__main__":
    main()
