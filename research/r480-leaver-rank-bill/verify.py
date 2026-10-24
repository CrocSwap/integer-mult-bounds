#!/usr/bin/env python3
"""Check the R480 leaver's rank bill and packing ceiling.

The paid profile exchanges fourteen rank-3 children and fourteen rank-5
children for twenty-eight rank-4 children. Seventy-two calls plus the idle
remainder are the global bill. The packing ceiling is the screen.
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

MARKER = "PASS_R480_LEAVER_RANK_BILL ceiling_above_selected=false no_new_kappa"
SPEC_PATH = "research/gauge44-leaver8/data/SPEC.json"
SELECTED = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
CALLS = 72
MARGIN = Fraction(21, 20)
SPEC_SHA = "1208c7c3ae84c158c21b80d69f0f448d376680a7d37e15d0abc77541d3cd61d8"


def fail(message):
    raise SystemExit("FAIL_R480_LEAVER_RANK_BILL " + message)


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
        SPEC_PATH,
        "research/heterogeneous-owner-assembly/controls.py",
        "research/heterogeneous-owner-assembly/README.md",
        "research/complex-local-word-ceiling/ceiling.py",
        "research/complex-local-word-ceiling/README.md",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def counts(raw):
    return {int(rank): int(count) for rank, count in raw.items()}


def mass(profile):
    return sum(rank * count for rank, count in profile.items())


def screen(local):
    return ceiling_mod.ceiling(local, 73, 896, 9, 64, grid=Fraction(1, 10**12), unpaid=1)[1]


def exchange(before, after):
    ranks = sorted(set(before) | set(after))
    return {rank: after.get(rank, 0) - before.get(rank, 0) for rank in ranks if after.get(rank, 0) != before.get(rank, 0)}


def evaluate():
    authenticate()
    spec_bytes = (ROOT / SPEC_PATH).read_bytes()
    require(hashlib.sha256(spec_bytes).hexdigest() == SPEC_SHA, "the leaver spec digest moved")
    spec = json.loads(spec_bytes)
    controls = (ROOT / "research/heterogeneous-owner-assembly/controls.py").read_text(encoding="utf-8")
    note = (ROOT / "research/heterogeneous-owner-assembly/README.md").read_text(encoding="utf-8")
    ceiling_readme = (ROOT / "research/complex-local-word-ceiling/README.md").read_text(encoding="utf-8")
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(SPEC_SHA in controls, "the control lost the spec digest")
    require('{"1": 2412, "2": 418, "3": 418, "4": 170, "5": 68, "8": 8}' in controls, "the control profile moved")
    require('{"4": 56, "5": 32, "7": 30, "8": 122, "9": 240}' in controls, "the control inventory moved")
    require("outside the base catalogue" in controls, "the control scope moved")
    require("the R489 and R480 interfaces from PR1004/1005" in note, "the outside-catalogue sentence moved")
    require("Their reduced costs are negative." in note, "the reduced-cost sentence moved")
    require("`{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`, local mass 5,586" in ceiling_readme, "the selected word moved")
    provider = spec["providers"]["gauge44"]
    paid = counts(provider["expected_profile"])
    contract = counts(provider["complete_contract"]["paid_profile"])
    inventory = counts(provider["inventory"])
    width = counts(provider["complete_contract"]["width_inventory"])
    require(paid == contract == {1: 2412, 2: 418, 3: 418, 4: 170, 5: 68, 8: 8}, "the paid profile moved")
    require(inventory == width == {4: 56, 5: 32, 7: 30, 8: 122, 9: 240}, "the helper inventory moved")
    require(sum(inventory.values()) == provider["complete_contract"]["helpers"] == 480, "the helper count moved")
    require(spec["expected"]["provider_counts"] == {"gauge44": CALLS}, "the call count moved")
    require(exchange(SELECTED, paid) == {3: -14, 4: 28, 5: -14}, "the rank exchange moved")
    require(14 * (3 + 5) == 28 * 4 == 112, "the exchange mass moved")
    require(mass(paid) == mass(SELECTED) == 5586, "the local mass moved")
    idle = counts(spec["expected"]["idle_remainder_profile"])
    global_profile = counts(spec["expected"]["global_profile"])
    built = {}
    for rank, count in paid.items():
        built[rank] = built.get(rank, 0) + CALLS * count
    for rank, count in idle.items():
        built[rank] = built.get(rank, 0) + count
    require(built == global_profile, "the global rank bill moved")
    rank_mass = sum(rank * count for rank, count in global_profile.items())
    require(rank_mass == spec["expected"]["rank_mass"] == 520704, "the rank mass moved")
    require(mass(idle) == 1646 * CALLS, "the idle bill moved")
    live = CALLS * 896 // 9
    require(live == spec["expected"]["live"] == 7168, "the live count moved")
    endpoint = Fraction(spec["expected"]["kappa"])
    selected_kappa = Fraction(selected["kappa"])
    require(endpoint < selected_kappa, "the pinned endpoint reached the selected kappa")
    profile_ceiling = screen(paid)
    selected_ceiling = screen(SELECTED)
    require(profile_ceiling < selected_ceiling, "the profile ceiling reached the selected word")
    require(profile_ceiling / selected_ceiling < MARGIN, "the profile cleared five percent")
    return {
        "calls": CALLS,
        "helpers": 480,
        "local_mass": 5586,
        "rank_mass": rank_mass,
        "live": live,
        "exchange_mass": 112,
        "endpoint_kappa": spec["expected"]["kappa"],
        "endpoint_below_selected": True,
        "profile_ceiling": str(profile_ceiling),
        "selected_ceiling": str(selected_ceiling),
        "ceiling_above_selected": False,
        "above_five_percent": False,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
