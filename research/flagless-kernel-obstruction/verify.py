#!/usr/bin/env python3
"""Exact finite corroboration of the coordinate-kernel obstruction."""

import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def outer(x, y):
    return sum(((x >> i & 1) * (y >> j & 1)) << (4 * i + j)
               for i in range(4) for j in range(4))


def action(matrix, vector):
    return sum(((matrix >> (4 * i) & 15 & vector).bit_count() % 2) << i
               for i in range(4))


def transpose(matrix):
    return sum((matrix >> (4 * j + i) & 1) << (4 * i + j)
               for i in range(4) for j in range(4))


def multiply(first, second):
    return sum((action(first, action(second, 1 << j)) >> i & 1)
               << (4 * i + j) for i in range(4) for j in range(4))


def literal_multiply(first, second):
    result = 0
    for i, j in itertools.product(range(4), repeat=2):
        entry = sum((first >> (4 * i + k) & 1) * (second >> (4 * k + j) & 1)
                    for k in range(4)) % 2
        result |= entry << (4 * i + j)
    return result


def off_diagonal(matrix):
    return matrix & ~0x8421


def kernel(matrices):
    return tuple(v for v in range(1, 16)
                 if all(action(matrix, v) == 0 for matrix in matrices))


def lacks_line_plane(matrices):
    for line in range(1, 16):
        if not all(action(matrix, line) in (0, line) for matrix in matrices):
            continue
        for vector in range(1, 16):
            if vector == line:
                continue
            plane = (0, line, vector, line ^ vector)
            if all(action(matrix, v) in plane
                   for matrix in matrices for v in plane):
                return False
    return True


def exceptional_pools():
    """Enumerate only the predecessor's partial-plane triple shape."""
    fibers = defaultdict(list)
    for x, y in itertools.product(range(1, 16), repeat=2):
        if (x & y).bit_count() % 2:
            matrix = outer(x, y)
            fibers[off_diagonal(matrix)].append(matrix)
    pools = []
    for first in sorted(fibers):
        if first == 0 or len(fibers[first]) != 2:
            continue
        for second in sorted(fibers):
            if second == 0 or len(fibers[second]) != 1:
                continue
            if first ^ second in fibers:
                continue
            matrices = tuple(sorted(fibers[first] + fibers[second]))
            if lacks_line_plane(matrices):
                pools.append(matrices)
    require(len(pools) == len(set(pools)), "duplicate exceptional pool")
    return tuple(sorted(pools))


def permute(matrix, permutation):
    return sum((matrix >> (4 * i + j) & 1)
               << (4 * permutation[i] + permutation[j])
               for i in range(4) for j in range(4))


def coordinate_orbit(matrices):
    return {tuple(sorted(permute(matrix, p) for matrix in matrices))
            for p in itertools.permutations(range(4))}


def classify(pools):
    right = coordinate_orbit((0x0003, 0x0022, 0x0DD0))
    left = {tuple(sorted(transpose(matrix) for matrix in pool))
            for pool in right}
    coordinate = coordinate_orbit((0x0003, 0x0022, 0x0550))
    require(len(right) == len(left) == len(coordinate) == 24, "orbit size")
    require(not (right & left or right & coordinate or left & coordinate),
            "coordinate orbits overlap")
    require(set(pools) == right | left | coordinate, "unclassified pool")
    histogram = Counter()
    for pool in pools:
        r = kernel(pool)
        l = kernel(tuple(transpose(matrix) for matrix in pool))
        require(len(r) == len(l) == 1, "kernel dimension is not one")
        require((r[0] & l[0]).bit_count() % 2 == 1, "kernel/image split")
        histogram[r[0].bit_count(), l[0].bit_count(),
                  (r[0] | l[0]).bit_count()] += 1
    require(histogram == {(1, 1, 1): 24, (2, 1, 2): 24, (1, 2, 2): 24},
            "left/right support histogram")
    return tuple(sorted(right | left)), coordinate, histogram


def formal_word(word):
    """Multiply in the full group algebra on independent integer exponents."""
    result = {(0,) * len(word): 0x8421}
    for index, projector in enumerate(word):
        following = {}
        for exponent, coefficient in result.items():
            other = list(exponent)
            other[index] += 1
            shifted = tuple(other)
            first = multiply(coefficient, 0x8421 ^ projector)
            second = multiply(coefficient, projector)
            following[exponent] = following.get(exponent, 0) ^ first
            following[shifted] = following.get(shifted, 0) ^ second
        result = {exponent: value for exponent, value in following.items() if value}
    return result


def formal_kernel_checks(pools):
    words = coefficients = 0
    for pool in pools:
        right = kernel(pool)[0]
        left = kernel(tuple(transpose(matrix) for matrix in pool))[0]
        for length in range(4):
            for word in itertools.product(pool, repeat=length):
                for exponent, coefficient in formal_word(word).items():
                    origin = not any(exponent)
                    require(action(coefficient, right) == (right if origin else 0),
                            "formal right-kernel identity")
                    require(action(transpose(coefficient), left)
                            == (left if origin else 0), "formal left-kernel identity")
                    coefficients += 1
                words += 1
    return words, coefficients


def diagonal_checks(pools):
    checks = 0
    for pool in pools:
        r = kernel(pool)[0]
        l = kernel(tuple(transpose(matrix) for matrix in pool))[0]
        for labels in itertools.product((-1, 0, 1), repeat=4):
            for vector in (r, l):
                predicted = all(labels[i] == 0 for i in range(4) if vector >> i & 1)
                actual = {(i, labels[i]): 1 for i in range(4) if vector >> i & 1}
                expected = {(i, 0): 1 for i in range(4) if vector >> i & 1}
                require(predicted == (actual == expected), "fixed-diagonal criterion")
            checks += 1
    return checks


def allocations(total):
    require(0 <= total <= 9, "allocation domain")
    return tuple(v for v in itertools.product(range(total + 1), repeat=4)
                 if sum(v) == total)


def surviving_budgets(pools, total):
    survivors = []
    for pool in pools:
        forced = kernel(pool)[0] | kernel(tuple(transpose(m) for m in pool))[0]
        for auxiliary in range(4):
            active = tuple(i for i in range(4) if i != auxiliary)
            for size in range(3, total + 1):
                for counts in allocations(total - size):
                    capacity = [counts[i] + (0 if forced >> i & 1 else size - 2)
                                for i in active]
                    if min(capacity) >= 3:
                        survivors.append((size, counts, active, forced))
    return survivors


def budget_checks(pools):
    survivors = surviving_budgets(pools, 8)
    require(len(survivors) == 96, "critical allocation count")
    for size, counts, active, forced in survivors:
        require(size == 5 and sum(counts) == 3, "noncritical allocation survived")
        zeros = tuple(i for i in active if forced >> i & 1)
        require(len(zeros) == 1 and counts[zeros[0]] == 3, "forced role bill")
        require(all(counts[i] == 0 for i in active if i not in zeros),
                "remaining targets have coordinate contributions")
        # The cited two-invertible-target theorem requires six S calls.
        require(size < 6, "two-target theorem no longer excludes the budget")
    require(bool(surviving_budgets(pools[:1], 9)), "nine-call budget control")
    return len(survivors)


def controls(pools, coordinate):
    seed = (0x0003, 0x0022, 0x0DD0)
    require(seed in pools, "literal initial fixture missing")
    require(kernel(seed) == (12,), "initial right kernel changed")
    require(kernel(tuple(transpose(m) for m in seed)) == (8,), "initial left kernel")
    require(all((kernel(p)[0] | kernel(tuple(transpose(m) for m in p))[0]).bit_count() == 1
                for p in coordinate), "coordinate control was excluded")
    for pool in pools:
        require(all(multiply(m, m) == m for m in pool), "idempotence")
    require(action(outer(4, 4), 12) != 0, "coordinate interleaving countercontrol")
    require(allocations(0) == ((0, 0, 0, 0),), "zero allocation")
    for invalid in (-1, 10):
        try:
            allocations(invalid)
        except ValueError:
            continue
        raise ValueError("invalid allocation accepted")
    return ("literal_fixture", "right_kernel", "left_kernel", "coordinate_exclusion_boundary",
            "idempotence", "coordinate_interleaving", "zero_allocation",
            "negative_allocation_rejected", "oversized_allocation_rejected")


def arithmetic_checks(pools):
    matrices = sorted({m for pool in pools for m in pool} | {0, 0x8421})
    checks = 0
    for first, second in itertools.product(matrices, repeat=2):
        require(multiply(first, second) == literal_multiply(first, second),
                "literal binary matrix product disagrees")
        checks += 1
    return checks


def main():
    excluded, coordinate, histogram = classify(exceptional_pools())
    arithmetic = arithmetic_checks(excluded)
    words, coefficients = formal_kernel_checks(excluded)
    diagonals = diagonal_checks(excluded)
    critical = budget_checks(excluded)
    control_names = controls(excluded, coordinate)
    root = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "verify.py", "TASK.json", "SOURCES.json", "VERIFY.json")
    hashes = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in names}
    receipt = {"status": "PASS_FLAGLESS_KERNEL_OBSTRUCTION", "excluded_pools": len(excluded),
               "remaining_coordinate_pools": len(coordinate), "formal_words": words,
               "formal_coefficient_matrices": coefficients, "diagonal_label_checks": diagonals,
               "critical_rank_budgets": critical, "controls": list(control_names),
               "literal_matrix_products": arithmetic,
               "kernel_histogram": {str(k): v for k, v in sorted(histogram.items())},
               "pool_sha256": hashlib.sha256(json.dumps(excluded).encode()).hexdigest(),
               "source_sha256": hashes}
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
