#!/usr/bin/env python3
"""The count 1e-10000 has eight characters and a 33220-bit denominator.

The checker expands that one fraction. It does not reprice the queue.
"""

import hashlib
import json
import re
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_COUNT_EXPONENT_BUDGET bits=33220 exponent_budget=60 no_new_kappa"
EXPONENT = re.compile(r"[eE]([+-]?\d+)\s*\Z")


def fail(message):
    raise SystemExit("FAIL_COUNT_EXPONENT_BUDGET " + message)


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


def decimal_exponent(count):
    match = EXPONENT.search(count.replace("_", ""))
    if match is None:
        return None
    return int(match.group(1))


def within_budget(count):
    exponent = decimal_exponent(count)
    if exponent is not None and abs(exponent) > 60:
        return False
    value = Fraction(count)
    return abs(value.numerator) <= 10**60 and value.denominator <= 10**60


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    count = "1e-10000"
    require(len(count) == 8 and len(count) <= 60, "the character length moved")
    value = Fraction(count)
    require(value == Fraction(1, 10**10000), "the expanded fraction moved")
    require(value.denominator.bit_length() == 33220, "the denominator width moved")
    require(decimal_exponent(count) == -10000 and not within_budget(count), "the exponent budget accepted the count")
    require(within_budget("1e-60") and not within_budget("1e-61"), "the budget boundary moved")
    return {
        "text_length": 8,
        "denominator_bits": 33220,
        "exponent_budget": 60,
        "rejected": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
