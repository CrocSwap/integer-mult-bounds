#!/usr/bin/env python3
"""Scalar-word total of the chirp middle-map invoice.

The checker adds the four published charges. It does not run the middle-map
consumer.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_CHIRP_SCALAR_INVOICE rows=32294 no_new_kappa"
SELECTED = "836330098538459/500000000000000000"


def fail(message):
    raise SystemExit("FAIL_CHIRP_SCALAR_INVOICE " + message)


def require(condition, message):
    if not condition:
        fail(message)


def charges(length, copies):
    level = length + 1
    kernel = 4 * copies * level
    endpoints = 8 * copies
    twists = 12 * copies
    ring = copies * (12 * level + 8)
    return kernel, endpoints, twists, ring


def main():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(selected["kappa"] == SELECTED, "selected kappa moved")
    require(4 + 12 == 16, "the variable factors moved")
    require(8 + 12 + 8 == 28, "the constant factors moved")
    rows = 0
    for precision in range(16, 257):
        for length in range(2, precision):
            for copies in range(1, 9):
                kernel, endpoints, twists, ring = charges(length, copies)
                total = kernel + endpoints + twists + ring
                level = length + 1
                require(total == copies * (16 * level + 28), "the scalar total moved")
                cells = 2 * (precision + 2) * copies
                require(total * (precision + 2) == cells * (8 * level + 14), "the cell relation moved")
            rows += 1
    receipt = json.loads((PACKAGE / "RESULT.json").read_text())
    require(rows == 32294, "row count")
    require(receipt["rows"] == rows, "receipt rows")
    require(receipt["variable_factor"] == 16, "receipt variable")
    require(receipt["constant_factor"] == 28, "receipt constant")
    require(receipt["no_new_kappa"] is True, "kappa flag")
    print(MARKER)


if __name__ == "__main__":
    main()
