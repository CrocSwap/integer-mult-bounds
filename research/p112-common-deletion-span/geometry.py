"""Exact E8 root geometry, independent of the predecessor's direction tables."""

from fractions import Fraction
from itertools import combinations, product
from math import gcd, lcm

SIMPLE = (
    (1, -1, -1, -1, -1, -1, -1, 1),
    (2, 2, 0, 0, 0, 0, 0, 0),
    (-2, 2, 0, 0, 0, 0, 0, 0),
    (0, -2, 2, 0, 0, 0, 0, 0),
    (0, 0, -2, 2, 0, 0, 0, 0),
    (0, 0, 0, -2, 2, 0, 0, 0),
    (0, 0, 0, 0, -2, 2, 0, 0),
    (0, 0, 0, 0, 0, -2, 2, 0),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def dot(a: tuple[int, ...], b: tuple[int, ...]) -> int:
    assert len(a) == len(b) == 8
    return sum(a[j] * b[j] for j in range(8))


def canonical(vector: tuple[int, ...]) -> tuple[int, ...]:
    assert len(vector) == 8 and any(vector)
    divisor = gcd(*vector)
    if next(x for x in vector if x) < 0:
        divisor = -divisor
    return tuple(x // divisor for x in vector)


def roots() -> tuple[tuple[int, ...], ...]:
    """Doubled E8 root lines, with first nonzero coordinate positive."""
    result = []
    for i, j in combinations(range(8), 2):
        for sign in (-2, 2):
            row = [0] * 8
            row[i], row[j] = 2, sign
            result.append(tuple(row))
    for tail in product((-1, 1), repeat=7):
        row = (1,) + tail
        if sum(x < 0 for x in row) % 2 == 0:
            result.append(row)
    assert len(result) == len(set(result)) == 120
    assert all(dot(row, row) == 8 for row in result)
    return tuple(sorted(result))


def coordinates(row: tuple[int, ...]) -> tuple[int, ...]:
    """Solve the triangular Bourbaki simple-root equations over the integers."""
    c = [0] * 8
    c[0] = row[7]
    c[7] = (row[6] + c[0]) // 2
    for j in range(6, 2, -1):
        c[j] = (row[j - 1] + c[0]) // 2 + c[j + 1]
    c[1] = (row[0] + row[1] + 2 * c[3]) // 4
    c[2] = (-row[0] + row[1] + 2 * c[0] + 2 * c[3]) // 4
    require(
        all(sum(c[i] * SIMPLE[i][j] for i in range(8)) == row[j] for j in range(8)),
        "simple-root reconstruction failed",
    )
    require(min(c) >= 0 or max(c) <= 0, "root has mixed simple-coordinate signs")
    return tuple(c)


def label(row: tuple[int, ...]) -> int:
    return 256 + sum((x % 2) << j for j, x in enumerate(coordinates(row)))


def reflection_permutations(lines: tuple[tuple[int, ...], ...]) -> list[list[int]]:
    lookup = {row: i for i, row in enumerate(lines)}
    permutations = []
    for alpha in SIMPLE:
        permutation = []
        for row in lines:
            pairing = dot(alpha, row)
            require(pairing % 4 == 0, "nonintegral root reflection")
            reflected = tuple(row[j] - pairing // 4 * alpha[j] for j in range(8))
            if next(x for x in reflected if x) < 0:
                reflected = tuple(-x for x in reflected)
            require(reflected in lookup, "reflection left the E8 roots")
            permutation.append(lookup[reflected])
        require(sorted(permutation) == list(range(120)), "reflection is not bijective")
        require(
            all(permutation[permutation[i]] == i for i in range(120)), "not involutive"
        )
        permutations.append(permutation)
    return permutations


def permute(mask: int, permutation: list[int]) -> int:
    assert 0 <= mask < 1 << 120 and len(permutation) == 120
    result = 0
    for _ in range(120):
        if not mask:
            break
        bit = mask & -mask
        result |= 1 << permutation[bit.bit_length() - 1]
        mask ^= bit
    assert mask == 0
    return result


def orbit(seed: int, permutations: list[list[int]]) -> set[int]:
    """Breadth-first closure with a hard 4,000-state capacity."""
    queue = [seed]
    seen = {seed}
    for cursor in range(4000):
        if cursor == len(queue):
            return seen
        for permutation in permutations:
            image = permute(queue[cursor], permutation)
            if image not in seen:
                require(len(queue) < 4000, "Weyl orbit exceeded capacity")
                seen.add(image)
                queue.append(image)
    # Exactly 4,000 states also close: every queued state was processed.
    return seen


def orthogonality_systems(lines: tuple, live: int) -> tuple[list[int], list[dict]]:
    """All Weyl translates of proper parabolics with at least 40 root lines."""
    supports = [
        sum(1 << j for j, c in enumerate(coordinates(row)) if c) for row in lines
    ]
    permutations = reflection_permutations(lines)
    seen: set[int] = set()
    candidates = []
    reports = []
    for zero_set in range(255):
        seed = sum(
            1 << i for i, support in enumerate(supports) if not support & ~zero_set
        )
        if seed.bit_count() < 40 or seed in seen:
            continue
        family = orbit(seed, permutations)
        require(len(seen | family) <= 6000, "parabolic inventory exceeded capacity")
        seen |= family
        histogram = {}
        for member in family:
            count = (member & live).bit_count()
            histogram[count] = histogram.get(count, 0) + 1
            if count >= 40:
                candidates.append(member)
        reports.append(
            {
                "seed_zero_set": zero_set,
                "simple_rank": zero_set.bit_count(),
                "full_root_lines": seed.bit_count(),
                "orbit_size": len(family),
                "live_intersection_histogram": {
                    str(k): histogram[k] for k in sorted(histogram)
                },
            }
        )
    require(len(candidates) == len(set(candidates)), "overlapping parabolic orbits")
    return sorted(candidates), reports


def echelon(rows: list[tuple[int, ...]]) -> dict[int, list[Fraction]]:
    assert len(rows) <= 120 and all(len(row) == 8 for row in rows)
    basis: dict[int, list[Fraction]] = {}
    for row in rows:
        vector = list(map(Fraction, row))
        for pivot, old in sorted(basis.items()):
            factor = vector[pivot]
            vector = [vector[j] - factor * old[j] for j in range(8)]
        pivot = next((j for j in range(8) if vector[j]), None)
        if pivot is not None:
            scale = vector[pivot]
            basis[pivot] = [x / scale for x in vector]
    return basis


def normal(lines: tuple, mask: int) -> tuple[int, ...]:
    rows = [lines[i] for i in range(120) if mask >> i & 1]
    basis = echelon(rows)
    require(len(basis) == 7, "candidate is not a one-dimensional direction")
    free = next(j for j in range(8) if j not in basis)
    result = [Fraction(0)] * 8
    result[free] = Fraction(1)
    for pivot, row in sorted(basis.items(), reverse=True):
        result[pivot] = -sum(row[j] * result[j] for j in range(pivot + 1, 8))
    denominator = lcm(*(x.denominator for x in result))
    vector = canonical(tuple(int(x * denominator) for x in result))
    require(
        sum(1 << i for i, row in enumerate(lines) if dot(row, vector) == 0) == mask,
        "normal has a different orthogonality system",
    )
    return vector
