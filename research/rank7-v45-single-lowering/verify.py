#!/usr/bin/env python3
"""Check one rank-7 joint group against its single-lowering prices.

Group V45 lowers four helper end frames onto one subspace. The pinned prices
say one, two, or three of those helpers lose, and all four pay. This check
recomputes that sign pattern and the frame ranks. It does not admit the
claimed exponent.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PRICES = ROOT / "research/rank7-joint-endframes/construction/STAGE-PRICES.json"
FRAMES = ROOT / "research/rank7-joint-endframes/data/STAGE1-FRAME-EDITS.json"
MARKER = (
    "PASS_RANK7_V45_SINGLE_LOWERING helpers=4 single_margin=-53141 "
    "joint_margin=22972 end_frames=8to7 no_new_kappa"
)


def fail(message):
    raise SystemExit("FAIL_RANK7_V45_SINGLE_LOWERING " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def basis_of(vectors):
    basis = []
    for value in vectors:
        reduced = value
        for row in basis:
            candidate = reduced ^ row
            if candidate < reduced:
                reduced = candidate
        if reduced:
            basis.append(reduced)
            basis.sort(reverse=True)
    return basis


def rank(vectors):
    return len(basis_of(vectors))


def contained(vectors, ambient):
    basis = basis_of(ambient)

    def reduces(value):
        reduced = value
        for row in basis:
            candidate = reduced ^ row
            if candidate < reduced:
                reduced = candidate
        return reduced == 0

    return all(reduces(value) for value in vectors)


def hyperplane(old, new):
    return contained(new, old) and rank(old) == rank(new) + 1


def margin(delta, count, break_even):
    """Local saving minus the idle-width charge of one freed unit per helper."""
    return -delta - count * break_even


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/rank7-joint-endframes/construction/STAGE-PRICES.json",
        "research/rank7-joint-endframes/data/STAGE1-FRAME-EDITS.json",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    prices = json.loads(PRICES.read_text(encoding="utf-8"))
    frames = json.loads(FRAMES.read_text(encoding="utf-8"))
    break_even = prices["weights"]["break_even"]
    require(break_even == 2091300, "break-even constant changed")
    groups = {group["group"]: group for group in prices["stage1"]["groups"]}
    group = groups["V45"]
    helpers = group["helpers"]
    require(helpers == [249, 251, 265, 267], "V45 helpers changed")
    recorded = frames["groups"]["V45"]
    require(recorded[1] == helpers and recorded[0] == group["W"], "V45 frame group diverges from its prices")
    require(rank(group["W"]) == 7, "V45 subspace is not rank 7")

    finals = []
    for helper in helpers:
        change = frames["helper_final_changes"][str(helper)]
        require(change["new"] == group["W"], "helper %s does not end on W" % helper)
        require(hyperplane(change["old"], change["new"]), "helper %s end frame is not a hyperplane" % helper)
        finals.append([rank(change["old"]), rank(change["new"])])
    require(finals == [[8, 7]] * 4, "V45 end frames are not rank 8 to 7")

    subset_rows = []
    for subset in group["subsets"]:
        recomputed = margin(subset["delta"], len(subset["helpers"]), break_even)
        require(recomputed == subset["margin"], "V45 subset margin drifted")
        subset_rows.append({
            "helpers": len(subset["helpers"]),
            "margin": recomputed,
        })
    by_size = {}
    for row in subset_rows:
        by_size.setdefault(row["helpers"], set()).add(row["margin"])
    require(by_size == {1: {-53141}, 2: {-27770}, 3: {-2399}, 4: {22972}}, "V45 sign pattern changed")
    require(all(value < 0 for value in by_size[1]), "a single lowering pays")
    joint = margin(group["joint_delta"], 4, break_even)
    require(joint == 22972 == group["joint_margin"], "V45 joint margin drifted")

    stage_sum = sum(item["joint_delta"] for item in groups.values())
    require(stage_sum == prices["stage1"]["literal_price_units"] == -46150994, "stage-1 prices do not add")

    end_ranks = {}
    for helper, change in frames["helper_final_changes"].items():
        key = (rank(change["old"]), rank(change["new"]))
        end_ranks[key] = end_ranks.get(key, 0) + 1
    require(end_ranks == {(8, 7): 22}, "helper end frames are not uniformly rank 8 to 7")
    gate_ranks = {}
    hyperplanes = 0
    for edit in frames["frame_edits"]:
        key = (rank(edit["old_frame"]), rank(edit["new_frame"]))
        gate_ranks[key] = gate_ranks.get(key, 0) + 1
        if hyperplane(edit["old_frame"], edit["new_frame"]):
            hyperplanes += 1
    require(hyperplanes == len(frames["frame_edits"]) == 139, "a gate frame is not a hyperplane")
    require(
        gate_ranks == {(5, 4): 6, (6, 5): 22, (7, 6): 32, (8, 7): 79},
        "gate-frame rank changes drifted",
    )
    return {
        "group": "V45",
        "subspace_rank": 7,
        "helpers": helpers,
        "end_frame_ranks": [8, 7],
        "break_even": break_even,
        "single_margin": -53141,
        "pair_margin": -27770,
        "triple_margin": -2399,
        "joint_delta": group["joint_delta"],
        "joint_idle_charge": 4 * break_even,
        "joint_margin": joint,
        "subset_counts": {str(size): sum(row["helpers"] == size for row in subset_rows) for size in range(1, 5)},
        "stage1_price_sum": stage_sum,
        "helper_final_ranks": {"8_to_7": 22},
        "gate_frame_ranks": {"5_to_4": 6, "6_to_5": 22, "7_to_6": 32, "8_to_7": 79},
        "admission_replayed": False,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
