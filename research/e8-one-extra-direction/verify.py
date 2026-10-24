#!/usr/bin/env python3
"""Check the new algebraic steps without replaying the cited E8 premises."""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def rank(rows: list[list[int]]) -> int:
    """Exact rational elimination on fixtures of at most six rows/columns."""
    if not rows:
        return 0
    require(len(rows) <= 6 and len(rows[0]) <= 6, "matrix capacity")
    width = len(rows[0])
    require(all(len(row) == width for row in rows), "ragged matrix")
    work = [[Fraction(value) for value in row] for row in rows]
    pivot = 0
    for column in range(width):
        candidates = [i for i in range(pivot, len(work)) if work[i][column]]
        if not candidates:
            continue
        chosen = candidates[0]
        work[pivot], work[chosen] = work[chosen], work[pivot]
        scale = work[pivot][column]
        work[pivot] = [value / scale for value in work[pivot]]
        for i in range(pivot + 1, len(work)):
            scale = work[i][column]
            work[i] = [a - scale * b for a, b in zip(work[i], work[pivot])]
        pivot += 1
        if pivot == len(work):
            break
    return pivot


def pairing_table() -> tuple[list[list[int]], list[int]]:
    # A separate six-line rational configuration, not the E8 roots.
    labels = [(1, 0, 0), (0, 1, 0), (0, 0, 1),
              (1, 1, 0), (1, 0, 1), (0, 1, 1)]
    supports = [[v for i, v in enumerate(labels) if mask & (1 << i)]
                for mask in range(64)]
    dimensions = [rank([list(v) for v in support]) for support in supports]
    costs = [[rank([[sum(x * y for x, y in zip(a, b)) for b in right]
                    for a in left]) if left and right else 0
              for right in supports] for left in supports]
    return costs, dimensions


def outer(a: int, b: int) -> int:
    require(0 <= a < 64 and 0 <= b < 64, "support capacity")
    return sum(b << (6 * i) for i in range(6) if a & (1 << i))


def operator(terms: list[tuple[int, int]]) -> int:
    result = 0
    for a, b in terms:
        result ^= outer(a, b)
    return result


def price(terms: list[tuple[int, int]], costs: list[list[int]]) -> int:
    return sum(costs[a][b] for a, b in terms)


def binary_rank(masks: list[int]) -> int:
    require(len(masks) <= 16, "binary rank capacity")
    basis = [0] * 6
    for mask in masks:
        require(0 <= mask < 64, "binary vector capacity")
        remainder = mask
        for bit in range(5, -1, -1):
            if not remainder & (1 << bit):
                continue
            if basis[bit]:
                remainder ^= basis[bit]
            else:
                basis[bit] = remainder
                break
    return sum(bool(row) for row in basis)


def normalize(terms: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Delete zeros and merge one equal-column pair per bounded pass."""
    require(len(terms) <= 16, "normalization capacity")
    current = list(terms)
    for _ in range(len(terms) + 1):
        current = [(a, b) for a, b in current if a and b]
        replacement = None
        for i, (a, b) in enumerate(current):
            for j in range(i + 1, len(current)):
                c, d = current[j]
                if a == c:
                    replacement = (i, j, (a, b ^ d))
                    break
                if b == d:
                    replacement = (i, j, (a ^ c, b))
                    break
            if replacement is not None:
                break
        if replacement is None:
            return current
        i, j, merged = replacement
        current = [term for k, term in enumerate(current) if k not in (i, j)]
        current.append(merged)
    raise ValueError("normalization did not decrease term count")


def check_pairings(costs: list[list[int]], dimensions: list[int]) -> dict:
    merge_cases = 0
    for a, b, c in product(range(64), repeat=3):
        require(costs[a][b ^ c] <= costs[a][b] + costs[a][c], "merge rank")
        merge_cases += 1
    pairing_cases = 0
    for a, b in product(range(64), repeat=2):
        require(costs[a][b] == costs[b][a], "transpose")
        require(costs[a][b] >= dimensions[a] + dimensions[b] - 3,
                "nondegenerate pairing bound")
        pairing_cases += 1
    return {"merge_inequalities": merge_cases, "pairing_inequalities": pairing_cases}


def check_normalization(costs: list[list[int]]) -> int:
    count = 0
    for alphabet, length in ((8, 2), (4, 3)):
        for flat in product(range(alphabet), repeat=2 * length):
            terms = list(zip(flat[::2], flat[1::2]))
            reduced = normalize(terms)
            require(operator(terms) == operator(reduced), "changed binary product")
            require(price(reduced, costs) <= price(terms, costs), "increased price")
            require(len({a for a, _ in reduced}) == len(reduced), "left repeats")
            require(len({b for _, b in reduced}) == len(reduced), "right repeats")
            require(all(a and b for a, b in reduced), "zero retained")
            for side in (0, 1):
                require(binary_rank([term[side] for term in reduced]) <=
                        binary_rank([term[side] for term in terms]), "rank increased")
            r_left = binary_rank([a for a, _ in terms])
            r_right = binary_rank([b for _, b in terms])
            rows = [(operator(terms) >> (6 * i)) & 63 for i in range(6)]
            require(binary_rank(rows) >= r_left + r_right - length,
                    "binary product-rank inequality")
            count += 1
    return count


def floor_from_budgets(left_excess: int, right_excess: int, count: int) -> int:
    require(left_excess in (0, 1) and right_excess in (0, 1), "excess scope")
    require(count >= 9 + left_excess + right_excess, "product rank")
    return 8 * count - 8 * left_excess - 8 * right_excess


def check_arithmetic() -> dict:
    cases = 0
    for left_excess, right_excess in product(range(2), repeat=2):
        start = 9 + left_excess + right_excess
        require(floor_from_budgets(left_excess, right_excess, start) == 72,
                "sharp arithmetic endpoint")
        for count in range(start, 33):
            require(floor_from_budgets(left_excess, right_excess, count) >= 72,
                    "rank-pair floor")
            cases += 1
    require(floor_from_budgets(1, 1, 12) == 80, "twelve-term rank-(10,10)")
    one_sided = 0
    for other_rank in (9, 10, 11):
        for count in range(other_rank, 33):
            require(72 + count - other_rank >= 72, "basis selection")
            one_sided += 1
    return {"arithmetic_cases": cases, "one_sided_cases": one_sided}


def expect_rejected(action, name: str) -> None:
    try:
        action()
    except ValueError:
        return
    raise ValueError("control was accepted: " + name)


def check_controls(costs: list[list[int]]) -> int:
    invalid = [
        (lambda: floor_from_budgets(2, 0, 11), "two extra directions"),
        (lambda: floor_from_budgets(1, 1, 10), "missing product rank"),
        (lambda: normalize([(1, 1)] * 17), "unbounded fixture"),
        (lambda: outer(64, 1), "oversize support"),
        (lambda: rank([[1], [1, 2]]), "ragged matrix"),
        (lambda: binary_rank([1] * 17), "binary rank capacity"),
        (lambda: binary_rank([64]), "binary vector capacity"),
    ]
    count = 0
    for action, name in invalid:
        expect_rejected(action, name)
        count += 1
    counterexamples = [
        (operator([(1, 1), (1, 1)]) != operator([(1, 1 | 1)]), "OR mutant"),
        (price([(1, 1), (1, 1)], costs) > price([], costs), "zero cost mutant"),
        (floor_from_budgets(1, 1, 11) < 80, "overstated eighty floor"),
        (2 * (8 - 1) > 8 and normalize([(1, 1), (1, 1)]) == [], "distinctness"),
    ]
    for condition, name in counterexamples:
        require(condition, name)
        count += 1
    return count


def main() -> None:
    costs, dimensions = pairing_table()
    receipt = check_pairings(costs, dimensions)
    receipt["normalization_cases"] = check_normalization(costs)
    receipt.update(check_arithmetic())
    receipt["controls"] = check_controls(costs)
    receipt["claim_type"] = "scoped proof from cited E8 premises"
    receipt["predecessor_geometry_replayed"] = False
    package = Path(__file__).resolve().parent
    receipt["source_sha256"] = {
        name: sha256((package / name).read_bytes()).hexdigest()
        for name in ("verify.py", "PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json")
    }
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_E8_ONE_EXTRA_DIRECTION factor_rank_sum<=20 pairing_floor=72")


if __name__ == "__main__":
    main()
