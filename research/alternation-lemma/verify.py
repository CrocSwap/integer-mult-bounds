#!/usr/bin/env python3
"""A linear functional changes by the walked bit.

The checker tests the step identity. It does not classify words.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_ALTERNATION_LEMMA widths=6 all_ones_only=true no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_ALTERNATION_LEMMA " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    require(set(pinned) == set(), "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def dot(mask, vector):
    return (mask & vector).bit_count() & 1


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    for width in range(1, 7):
        full = (1 << width) - 1
        for mask in range(1 << width):
            for vector in range(1 << width):
                for label in range(width):
                    step = 1 << label
                    changed = (mask & (vector ^ step)) ^ (mask & vector)
                    require(changed == (mask & step), "the mask failed to isolate the walked bit")
                    require((dot(mask, vector ^ step) ^ dot(mask, vector)) == ((mask >> label) & 1), "the step difference moved")
            state = 0
            for label in range(width):
                state ^= 1 << label
                require(dot(full, state) == (label + 1) & 1, "all ones failed to alternate")
            if mask != full:
                quiet = (mask & full).bit_count()
                require(quiet < width, "a partial mask became all ones")
                missing = next(label for label in range(width) if ((mask >> label) & 1) == 0)
                require(dot(mask, 1 << missing) == 0, "a missing bit flipped")
    return {
        "widths": 6,
        "all_ones_only": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
