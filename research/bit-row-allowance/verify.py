#!/usr/bin/env python3
"""The nine-stage BIT row against the external cap.

The checker adds the published allowance to the two family degrees.
It does not recompute the fourteen stage headrooms.
"""

import hashlib
import json
import re
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_BIT_ROW_ALLOWANCE row=18355 cap=20161 no_new_kappa"
ASSEMBLE = "research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/code/assemble9.py"
PARENT = "research/selected-bit-parent-reserve/README.md"
GAUGE = "notes/partial-gauge-assembly.tex"


def fail(message):
    raise SystemExit("FAIL_BIT_ROW_ALLOWANCE " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def evaluate():
    require(sha256(ROOT / ASSEMBLE) == "4bf6768224a3fac81ccda26df24f3763f9a4fbc35ad62bef2888595cdae519fe", "assembler drift")
    require(sha256(ROOT / PARENT) == "16b84730b7a604e805034008e11bae4f90fe6c91db6098d5bd5d011dded5f4ee", "parent note drift")
    require(sha256(ROOT / GAUGE) == "ef27afc3a70656d3139bf3661ac0b2088622f37221141cc386d41324b7c563d0", "gauge note drift")
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    source = (ROOT / ASSEMBLE).read_text(encoding="utf-8")
    require("row = DEPTH * (m * m + 1) + 9909 + 252; assert row == 18355 and row < 20161" in source, "the BIT row assert moved")
    require("2*(64^2+1)=8194" in (ROOT / PARENT).read_text(encoding="utf-8"), "the depth allowance moved")
    gauge = (ROOT / GAUGE).read_text(encoding="utf-8")
    pairs = re.search(r"\$\((\d+),(\d+)\),\((\d+),(\d+)\),\((\d+),(\d+)\)\$", gauge)
    require(pairs is not None, "the family pairs moved")
    coarse_h, coarse_w, leaf_h, leaf_w = map(int, pairs.groups()[:4])
    coarse, leaf = coarse_h * coarse_w, leaf_h * leaf_w
    allowance = 2 * (64 * 64 + 1)
    row = allowance + coarse + leaf
    require((allowance, coarse, leaf, row) == (8194, 9909, 252, 18355), "the BIT row moved")
    require(row < 20161, "the BIT row left the cap")
    return {"allowance": 8194, "coarse_degree": 9909, "leaf_degree": 252, "row": 18355, "cap": 20161, "no_new_kappa": True}


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
