#!/usr/bin/env python3
"""Check the complete sum-one witness using integer error and norm arithmetic."""

from collections import Counter
from itertools import product
import json


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def norm_squared(first: tuple[int, int]) -> int:
    real, imag = first
    return real**2 + (1 - real)**2 + 2 * imag**2


def twice_error_squared(first: tuple[int, int], output: tuple[int, int]) -> int:
    real, imag = first
    out_real, out_imag = output
    return (2 * out_real - (1 - 2 * imag))**2 + (2 * out_imag - (2 * real - 1))**2


def jump_at_most(before: int, after: int, numerator: int, denominator: int) -> bool:
    """Compare sqrt(after) - sqrt(before) to numerator/denominator."""
    remainder = (after - before) * denominator**2 - numerator**2
    return remainder <= 0 or remainder**2 <= 4 * numerator**2 * denominator**2 * before


def verify() -> dict[str, int | str]:
    require(not jump_at_most(3, 5, 1, 2), "threshold must exceed 1/2")
    require(jump_at_most(3, 5, 51, 100), "threshold must be at most 51/100")

    expected_shells = {1: {1: 2, 3: 2}, 3: {1: 1, 3: 1, 5: 1, 7: 1}, 5: {3: 2, 9: 2}}
    inputs = [first for first in product(range(-2, 3), repeat=2) if norm_squared(first) <= 5]
    require(Counter(map(norm_squared, inputs)) == {1: 2, 3: 4, 5: 2}, "input shells")
    strict_edges = set()
    tied_edges = set()
    total_edges = 0
    output_box = tuple(product(range(-3, 4), repeat=2))
    for first in inputs:
        before = norm_squared(first)
        outputs = Counter()
        for output in output_box:
            error = twice_error_squared(first, output)
            if error > 2:
                continue
            require(error == 2, f"unexpected sub-unit error for {first}, {output}")
            after = norm_squared(output)
            outputs[after] += 1
            if after <= before:
                strict_edges.add((first, output))
            elif (before, after) == (3, 5):
                tied_edges.add((first, output))
            else:
                require(not jump_at_most(before, after, 51, 100), f"unclassified edge {first}, {output}")
        require(outputs == expected_shells[before], f"output shells for {first}")
        total_edges += outputs.total()

    strict_neighbors = {output for _, output in strict_edges}
    require(len(strict_neighbors) == 6 < len(inputs), "strict Hall deficit")
    require((total_edges, len(strict_edges), len(tied_edges)) == (32, 16, 4), "edge counts")

    matching = ((0, -1), (1, -1), (0, 0), (-1, 0), (2, 0), (1, 0), (0, 1), (1, 1))
    require(len(set(matching)) == len(inputs), "matching must be injective")
    matching_edges = set(zip(inputs, matching, strict=True))
    require(matching_edges <= strict_edges | tied_edges, "matching contains a forbidden edge")
    require(len(matching_edges & tied_edges) == 2, "two exact threshold edges")
    return {
        "status": "PASS_GAUSSIAN_EXACT_SUM_FORWARD_SLACK",
        "inputs": len(inputs),
        "error_one_edges": total_edges,
        "strict_edges": len(strict_edges),
        "strict_neighbors": len(strict_neighbors),
        "threshold_edges": len(tied_edges),
        "matching_edges": len(matching_edges),
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
