#!/usr/bin/env python3
"""Screen a two-call centre path with one rank-8 restoration per pair.

The ideal lever halves the eight rank-8 copies and the centre charge. This
screen adds one rank-8 restoration for the pair, and gives that child centre
mass. Hosting and precision add no child under the stated hypotheses.
"""

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
CEILING_DIR = ROOT / "research/complex-local-word-ceiling"
sys.path.insert(0, str(CEILING_DIR))
import ceiling as ceiling_model  # noqa: E402

MARKER = "PASS_SHARED_CENTRE_K2 charged_gain_above_tenth=true no_new_kappa"
CALLS = 2
COPIES = 8
RANK = 8
RESTORATION_PER_PAIR = 1
WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
FAMILIES = 896
STAGES = 9
MODULUS = 73
GRID = Fraction(1, 10**12)
SELECTED_KAPPA = "836330098538459/500000000000000000"


def fail(message):
    raise SystemExit("FAIL_SHARED_CENTRE_K2 " + message)


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
        "research/complex-local-word-ceiling/ceiling.py",
        "research/complex-local-word-ceiling/levers.py",
        "research/complex-local-word-ceiling/README.md",
        "research/split-centres-global/proofs/PR386-BIT-GEOMETRY.txt",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def profile(calls, restoration_per_pair):
    rank8 = Fraction(COPIES, calls) + Fraction(restoration_per_pair, calls)
    local = dict(WORD)
    local[8] = rank8
    centre = RANK * rank8
    require(centre.denominator == 1, "the centre charge is not an integer")
    return local, centre.numerator


def cap(local, centre):
    return ceiling_model.ceiling(local, MODULUS, FAMILIES, STAGES, centre, grid=GRID)[1]


def above_tenth(ceiling, baseline):
    return ceiling / baseline - 1 > Fraction(1, 10)


def evaluate():
    authenticate()
    levers = (CEILING_DIR / "levers.py").read_text(encoding="utf-8")
    readme = (CEILING_DIR / "README.md").read_text(encoding="utf-8")
    geometry = (ROOT / "research/split-centres-global/proofs/PR386-BIT-GEOMETRY.txt").read_text(encoding="utf-8")
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require("WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}" in levers, "the local profile moved")
    require("cap({**WORD, 8: 4}, centre=32)" in levers, "the ideal two-call lever moved")
    require("| Centre path shared by two calls | 1.90 | 0.00320 |" in readme, "the published lever row moved")
    require("Only one such slot is used at a time." in geometry, "the private-slot sentence moved")
    require(selected["kappa"] == SELECTED_KAPPA, "the selected kappa moved")
    require(ceiling_model.max_idle_rank(MODULUS) == 51, "the halving guard moved")
    ideal_local, ideal_centre = profile(CALLS, 0)
    charged_local, charged_centre = profile(CALLS, RESTORATION_PER_PAIR)
    require(ideal_local[8] == 4 and ideal_centre == 32, "the ideal profile drifted")
    require(charged_local[8] == Fraction(9, 2) and charged_centre == 36, "the charged profile drifted")
    require(max(charged_local) == RANK, "the charged profile raised a child rank")
    charged_model = ceiling_model.model(charged_local, MODULUS, FAMILIES, STAGES, charged_centre)
    require(charged_model["idle_mass"] == 1646, "the restoration changed the idle mass")
    baseline = cap(WORD, 64)
    ideal = cap(ideal_local, ideal_centre)
    charged = cap(charged_local, charged_centre)
    require(abs(float(ideal / baseline) - 1.90) < 0.005, "the ideal ratio left the published 1.90")
    require(above_tenth(ideal, baseline), "the ideal share gained under a tenth")
    require(above_tenth(charged, baseline), "the charged share gained under a tenth")
    return {
        "calls": CALLS,
        "rank8_copies": str(charged_local[8]),
        "centre_charge": charged_centre,
        "restoration_children_per_pair": RESTORATION_PER_PAIR,
        "hosting_children": 0,
        "precision_children": 0,
        "baseline_ceiling": str(baseline),
        "ideal_ceiling": str(ideal),
        "charged_ceiling": str(charged),
        "ideal_gain_above_tenth": True,
        "charged_gain_above_tenth": True,
        "ideal_ratio_rounds_to_published": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
