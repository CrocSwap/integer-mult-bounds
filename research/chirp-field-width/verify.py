#!/usr/bin/env python3
"""Axis residues fit their fields and reduce by one subtraction.

The checker tests those pairs. It does not run the middle-map consumer.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_CHIRP_FIELD_WIDTH pairs=22369616 no_new_kappa"
SELECTED = "836330098538459/500000000000000000"
MIN_WIDTH = 2
MAX_WIDTH = 12
FIELDS = 5


def fail(message):
    raise SystemExit("FAIL_CHIRP_FIELD_WIDTH " + message)


def require(condition, message):
    if not condition:
        fail(message)


def main():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(selected["kappa"] == SELECTED, "selected kappa moved")
    pairs = 0
    for width in range(MIN_WIDTH, MAX_WIDTH + 1):
        modulus = 1 << width
        require((modulus - 1).bit_length() == width, "a residue left its field")
        require(modulus.bit_length() == width + 1, "the modulus fit in the field")
        require(FIELDS * width == 5 * width, "the five-field width moved")
        for left in range(modulus):
            require(left.bit_length() <= width, "a residue needed another bit")
            for right in range(modulus):
                total = left + right
                require(total < 2 * modulus, "a sum needed two subtractions")
                if total >= modulus:
                    total -= modulus
                require(total == (left + right) % modulus, "the reduced sum moved")
                pairs += 1
    require(pairs == 22369616, "the pair count moved")
    receipt = json.loads((PACKAGE / "RESULT.json").read_text())
    require(receipt["min_width"] == MIN_WIDTH, "receipt minimum")
    require(receipt["max_width"] == MAX_WIDTH, "receipt maximum")
    require(receipt["pairs"] == pairs, "receipt pairs")
    require(receipt["fields"] == FIELDS, "receipt fields")
    require(receipt["no_new_kappa"] is True, "kappa flag")
    print(MARKER)


if __name__ == "__main__":
    main()
