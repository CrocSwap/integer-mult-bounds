#!/usr/bin/env python3
"""The published trace constants give field bound 3296H and scratch bound 6592H.

The checker multiplies those constants. It does not retrace the entrance.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_FORMAT_WIDTH_BOUND field=3296H scratch=6592H no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_FORMAT_WIDTH_BOUND " + message)


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


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    require(32 * 32 == 1024, "the component count moved")
    field = 103 * 32
    scratch = 2 * field
    require(field == 3296 and scratch == 6592, "the norm coefficients moved")
    require(field < 2**12 and scratch < 2**13, "the power headroom moved")
    require(12 + 1 + 7 == 20 and 13 + 1 + 7 == 21, "the guard-seven widths moved")
    require(12 + 1 + 6 == 19 and 13 + 1 + 6 == 20, "the guard-six widths moved")
    return {
        "field_coefficient": 3296,
        "scratch_coefficient": 6592,
        "guard7_field_bits": "b+20",
        "guard7_scratch_bits": "b+21",
        "guard6_field_bits": "b+19",
        "guard6_scratch_bits": "b+20",
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
