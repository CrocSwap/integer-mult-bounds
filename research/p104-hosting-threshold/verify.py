#!/usr/bin/env python3
"""Price the P104 channel plus its unit-step side correction.

The published histogram plus 208 nine-step helpers is the local bill.
Extra rank-1 hosting is added until the moment at the selected saving
crosses one.
"""

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "research/complex-local-word-ceiling"))
import ceiling as ceiling_mod  # noqa: E402

MARKER = "PASS_P104_HOSTING_THRESHOLD moment_below_one=true no_new_kappa"
CHANNEL = {1: 1074, 2: 58, 3: 86, 4: 104, 5: 48, 6: 24, 7: 8, 8: 8}
UNITS = 208
STEP = 9
TOTAL = 6712
SHOWN = "0.9988962438816702"


def fail(message):
    raise SystemExit("FAIL_P104_HOSTING_THRESHOLD " + message)


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
        "research/p104-endpoint-geometric-budget/README.md",
        "research/p104-native-channel/README.md",
        "research/complex-local-word-ceiling/ceiling.py",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def mass(profile):
    return sum(rank * count for rank, count in profile.items())


def bill():
    paid = dict(CHANNEL)
    paid[1] += UNITS * STEP
    return paid


def moment(profile, saving):
    return ceiling_mod.relax(profile, 73, 832, 9, 56, saving, unpaid=1)


def evaluate():
    authenticate()
    budget = (ROOT / "research/p104-endpoint-geometric-budget/README.md").read_text(encoding="utf-8")
    native = (ROOT / "research/p104-native-channel/README.md").read_text(encoding="utf-8")
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    for sentence in (
        "1074 H1 + 58 H2 + 86 H3 + 104 H4 + 48 H5 + 24 H6 + 8 H7 + 8 H8.",
        "Its rank mass is 2368. Every added lifetime consumes nine more rank units,",
        "The minimizing profile has `H1=2946`",
        "local rank mass 4240 and idle rank mass 2472",
        SHOWN,
        "Native ADDs, owners, routing, precision, tape and\nall other physical charges are unknown and additional.",
        "centre charge 56, total paid\nrank mass 6712",
    ):
        require(sentence in budget, "the budget sentence moved")
    require("chronological global hosting, precision and all-size admission remain open." in native, "the hosting sentence moved")
    require(mass(CHANNEL) == 2368, "the channel mass moved")
    paid = bill()
    require(paid[1] == 2946 and mass(paid) == 4240, "the side-correction bill moved")
    idle = TOTAL - mass(paid)
    require(idle == 2472 and Fraction(idle, 51) == Fraction(824, 17), "the idle children moved")
    kappa = Fraction(selected["kappa"])
    saving = kappa / (1 - kappa)
    low, high = moment(paid, saving)
    require(high < 1 and f"{float(low):.16f}" == SHOWN and f"{float(high):.16f}" == SHOWN, "the side-correction moment moved")
    below = dict(paid)
    below[1] += 1126
    above = dict(paid)
    above[1] += 1127
    require(moment(below, saving)[1] < 1, "1126 rank-1 hosting met moment one")
    require(moment(above, saving)[0] > 1, "1127 rank-1 hosting stayed under moment one")
    require(1127 <= idle, "the hosting cut left the template")
    return {
        "channel_mass": 2368,
        "unit_steps": UNITS * STEP,
        "local_mass": 4240,
        "idle_mass": idle,
        "idle_children": "824/17",
        "moment_below_one": True,
        "hosting_rank1_below": 1126,
        "hosting_rank1_above": 1127,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
