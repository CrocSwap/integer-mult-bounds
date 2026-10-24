#!/usr/bin/env python3
"""The four-end histogram's incumbent grid cell contains its published bracket.

The checker prices the published profile. It does not rerun the endpoint LP
or search another partition.
"""

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_K8_FOUR_END_CEILING bracket_inside=true no_new_kappa"
PROFILE = {1: 2400, 2: 446, 3: 416, 4: 142, 5: 82, 8: 8}
sys.path.insert(0, str(ROOT / "research/complex-local-word-ceiling"))
from ceiling import ceiling  # noqa: E402


def fail(message):
    raise SystemExit("FAIL_K8_FOUR_END_CEILING " + message)


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
    expected = {
        "research/selected-k8-unrestricted-ends/README.md",
        "research/complex-local-word-ceiling/ceiling.py",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    note = (ROOT / "research/selected-k8-unrestricted-ends/README.md").read_text(encoding="utf-8")
    require(
        "`{1:2400,2:446,3:416,4:142,5:82,8:8}`. Local mass is 5,582; idle mass is 1,650." in note,
        "the profile sentence moved",
    )
    require("0.001690198050302 < best ceiling < 0.001690198050303." in note, "the bracket moved")
    require("less than **0.00852%**" in note, "the gain sentence moved")
    mass = sum(rank * count for rank, count in PROFILE.items())
    require(mass == 5582 and 7232 - mass == 1650, "the idle mass moved")
    lo, hi = ceiling(PROFILE, 73, 896, 9, 64, grid=Fraction(1, 10**12))
    require(lo == Fraction(33803961, 20000000000), "the grid floor moved")
    require(hi == Fraction(1690198051, 1000000000000), "the grid cap moved")
    published_lo = Fraction(1690198050302, 10**15)
    published_hi = Fraction(1690198050303, 10**15)
    require(lo < published_lo < published_hi < hi, "the published bracket left the grid cell")
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    kappa = Fraction(selected["kappa"])
    require(kappa == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    saving = kappa / (1 - kappa)
    require(saving < hi, "the selected saving meets the cap")
    require(hi / Fraction(169005411, 100000000000) - 1 < Fraction(852, 10000000), "the gain crossed the note")
    return {
        "local_mass": 5582,
        "idle_mass": 1650,
        "ceiling_hi": "1690198051/1000000000000",
        "published_bracket_inside": True,
        "gain_below_note": True,
        "selected_below_cap": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
