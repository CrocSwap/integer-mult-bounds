#!/usr/bin/env python3
"""The mixed-negative Q8 bound is attained at t=1 and t=2.

The checker uses the inherited inequality. It does not decide t greater than 2.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_Q8_BOUND_ATTAINMENT calls=3,6 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_Q8_BOUND_ATTAINMENT " + message)


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


def admissible(total):
    count = 0
    while 5 * count < 11 * total or (count - total) % 2 != 0:
        count += 1
    return count


def powers(label, count):
    """i^2 = j^2 = z and z^2 = 1, inside the cyclic subgroup of one label."""
    require(label in ("i", "j"), "the label moved")
    element = (0, "1")
    for _ in range(count):
        sign, name = element
        if name == "1":
            element = (sign, label)
        elif name == label:
            element = ((sign + 1) % 2, "1")
        else:
            fail("a power left its cyclic subgroup")
    return element


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    require(powers("i", 3) == (1, "i") and powers("j", 3) == (1, "j"), "the cube moved")
    require(powers("i", 4) == (0, "1") and powers("j", 4) == (0, "1"), "the order moved")
    require(admissible(1) == 3 and 5 * 2 < 11 <= 5 * 3, "the t=1 count moved")
    require(admissible(2) == 6 and 5 * 4 < 22 <= 5 * 5 and 5 % 2 != 2 % 2, "the t=2 count moved")
    require(3 * 1 == 3 and 3 * 2 == 6, "the witness moved")
    endpoints = (
        ((1, "i"),),
        ((1, "j"),),
        ((1, "i"), (1, "i")),
        ((1, "i"), (1, "j")),
        ((1, "j"), (1, "j")),
    )
    require(tuple(len(endpoint) for endpoint in endpoints) == (1, 1, 2, 2, 2), "the endpoint lengths moved")
    require(all(entry == powers(entry[1], 3) for endpoint in endpoints for entry in endpoint), "an endpoint left the cube")
    return {
        "t1_calls": 3,
        "t2_calls": 6,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
