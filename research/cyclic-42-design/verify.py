#!/usr/bin/env python3
"""Exact second moments and orthogonality for the fixed cyclic 42-ray design."""

from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path


EXPONENTS = (0, 1, 4, 10, 12, 17)
ORDER = 36
DIMENSION = 6
PHI36 = (1, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 1)
CYCLOTOMICS = {
    2: (1, 1),
    3: (1, 1, 1),
    4: (1, 0, 1),
    6: (1, -1, 1),
    9: (1, 0, 0, 1, 0, 0, 1),
    12: (1, 0, -1, 0, 1),
    18: (1, 0, 0, -1, 0, 0, 1),
    36: PHI36,
}


def require(condition: bool, message: str) -> None:
    """Keep mathematical checks active under optimized Python."""
    if not condition:
        raise ValueError(message)


def remainder(coefficients: tuple[int, ...], modulus: tuple[int, ...]) -> tuple[int, ...]:
    require(1 < len(modulus) <= 37 and modulus[-1] == 1, "monic modulus bound")
    require(len(coefficients) <= 72, "polynomial degree bound")
    degree = len(modulus) - 1
    values = list(coefficients) + [0] * max(0, degree - len(coefficients))
    for index in range(len(values) - 1, degree - 1, -1):
        leading = values[index]
        for offset in range(degree + 1):
            values[index - degree + offset] -= leading * modulus[offset]
    require(not any(values[degree:]), "division did not clear high coefficients")
    return tuple(values[:degree])


def polynomial(exponents: tuple[int, ...]) -> tuple[int, ...]:
    require(len(exponents) <= 36, "term bound")
    values = [0] * ORDER
    for exponent in exponents:
        values[exponent % ORDER] += 1
    return tuple(values)


def add(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    require(len(left) == len(right) == 12, "field element shape")
    return tuple(a + b for a, b in zip(left, right, strict=True))


def sidon(exponents: tuple[int, ...]) -> bool:
    require(len(exponents) == DIMENSION, "six exponents required")
    sums = [(a + b) % ORDER for i, a in enumerate(exponents) for b in exponents[i:]]
    return len(set(sums)) == len(sums)


def check_moment(exponents: tuple[int, ...], coordinate_count: int = 6,
                 denominator: int = 42) -> int:
    """Sum all 36 literal characters for every tensor matrix entry."""
    require(len(exponents) == DIMENSION, "moment dimension")
    require(0 <= coordinate_count <= DIMENSION, "coordinate-ray bound")
    require(1 <= denominator <= 84, "weight denominator bound")
    powers = tuple(remainder(polynomial((n,)), PHI36) for n in range(ORDER))
    checked = 0
    for a, c, b, d in product(range(DIMENSION), repeat=4):
        frequency = exponents[a] + exponents[c] - exponents[b] - exponents[d]
        actual = (0,) * 12
        for k in range(ORDER):
            actual = add(actual, powers[(k * frequency) % ORDER])
        # Multiply the unnormalized moment by 36 to keep every entry integral.
        coordinate = int(a == b == c == d and a < coordinate_count)
        actual = add(actual, (36 * coordinate,) + (0,) * 11)
        target = 36 * denominator * (int(a == b and c == d) + int(a == d and c == b))
        scaled = tuple(42 * entry for entry in actual)
        require(scaled == (target,) + (0,) * 11, f"second moment failed at {(a,c,b,d)}")
        checked += 1
    return checked


def flat_inner_numerator(exponents: tuple[int, ...], difference: int) -> tuple[int, ...]:
    require(len(exponents) == DIMENSION and 0 <= difference < ORDER, "inner-product domain")
    return remainder(polynomial(tuple(difference * s for s in exponents)), PHI36)


def check_orthogonality(exponents: tuple[int, ...]) -> tuple[int, list[list[int]]]:
    require(len(exponents) == DIMENSION, "orthogonality dimension")
    neighbors = [[] for _ in range(42)]
    checked = 0
    for left, right in combinations(range(42), 2):
        if right < 6:
            zero = True
        elif left < 6:
            zero = False  # Every flat coordinate has squared modulus 1/6.
        else:
            zero = not any(flat_inner_numerator(exponents, right - left))
        if zero:
            neighbors[left].append(right)
            neighbors[right].append(left)
        checked += 1
    expected = [[j for j in range(6) if j != i] if i < 6 else [] for i in range(42)]
    require(neighbors == expected, "orthogonality graph is not K6 plus 36 isolated vertices")
    return checked, neighbors


def check_distinctness(exponents: tuple[int, ...]) -> int:
    require(len(exponents) == DIMENSION, "distinctness dimension")
    checked = 0
    for left, right in combinations(range(ORDER), 2):
        phases = {((right - left) * (s - exponents[0])) % ORDER for s in exponents}
        require(phases != {0}, "two flat rays coincide")
        checked += 1
    # Flat rays have six nonzero coordinates, so none equals a coordinate ray.
    return checked


def count_bases(neighbors: list[list[int]]) -> int:
    require(len(neighbors) == 42 and max(map(len, neighbors)) <= 5, "clique search bound")
    bases = set()
    for vertex in range(42):
        for others in combinations(neighbors[vertex], 5):
            candidate = tuple(sorted((vertex,) + others))
            if all(b in neighbors[a] for a, b in combinations(candidate, 2)):
                bases.add(candidate)
    require(bases == {tuple(range(6))}, "unexpected orthonormal bases")
    return len(bases)


def check_order_table() -> dict[str, list[int]]:
    table = {}
    for order, modulus in CYCLOTOMICS.items():
        value = remainder(polynomial(EXPONENTS), modulus)
        require(any(value), f"orthogonal flat difference of order {order}")
        table[str(order)] = list(value)
    # Independently connect every actual difference to its Galois-order class.
    for difference in range(1, ORDER):
        require(any(flat_inner_numerator(EXPONENTS, difference)), "zero actual inner product")
    return table


def expect_rejection(action: str) -> None:
    try:
        if action == "collision":
            require(sidon((0, 1, 2, 3, 4, 5)), "colliding pair sums")
        elif action == "bad-moment":
            check_moment((0, 1, 2, 3, 4, 5))
        elif action == "missing-axis":
            check_moment(EXPONENTS, coordinate_count=5)
        elif action == "extra-orthogonality":
            check_orthogonality((0, 1, 2, 3, 4, 5))
        elif action == "repeated-rays":
            check_distinctness(tuple(2 * s for s in EXPONENTS))
        elif action == "wrong-normalization":
            check_moment(EXPONENTS, denominator=84)
        else:
            raise RuntimeError("unknown control")
    except ValueError:
        return
    raise RuntimeError(f"control did not reject: {action}")


def source_hashes() -> dict[str, str]:
    root = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        with (root / name).open("rb") as source:
            data = source.read(2 * 1024 * 1024 + 1)
        require(len(data) <= 2 * 1024 * 1024, "package source size bound")
        hashes[name] = sha256(data).hexdigest()
    return hashes


def main() -> None:
    require(len(set(EXPONENTS)) == DIMENSION and EXPONENTS[:2] == (0, 1), "fixed fixture")
    require(sidon(EXPONENTS), "candidate is not Sidon")
    require(remainder(polynomial((0, 18)), PHI36) == (0,) * 12, "zeta^18 = -1 control")
    table = check_order_table()
    moments = check_moment(EXPONENTS)
    pairs, neighbors = check_orthogonality(EXPONENTS)
    bases = count_bases(neighbors)
    distinct = check_distinctness(EXPONENTS)
    controls = ("collision", "bad-moment", "missing-axis", "extra-orthogonality",
                "repeated-rays", "wrong-normalization")
    for control in controls:
        expect_rejection(control)
    result = {
        "status": "PASS_CYCLIC_42_DESIGN",
        "claim_type": "scoped proof with finite exact certificate",
        "dimension": DIMENSION,
        "rays": 42,
        "uniform_weight": "1/42",
        "exponents": EXPONENTS,
        "pair_sums": len({(a + b) % ORDER for i, a in enumerate(EXPONENTS) for b in EXPONENTS[i:]}),
        "second_moment_entries": moments,
        "unordered_ray_pairs": pairs,
        "flat_distinctness_pairs": distinct,
        "orthogonal_pairs": sum(map(len, neighbors)) // 2,
        "orthogonality_degrees": list(map(len, neighbors)),
        "orthonormal_bases": bases,
        "cyclotomic_remainders": table,
        "rejection_controls": list(controls),
        "source_sha256": source_hashes(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
