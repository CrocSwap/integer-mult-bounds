#!/usr/bin/env python3
"""The declared V45 group is one rank-7 intersection, and only its full subset pays.

The four displayed normals are dependent, the listed basis spans their common
hyperplane intersection, and every proper subset in the price table has a
negative margin. The literal word, cleanup, chronology and supplier caps are
not replayed.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
README = ROOT / "research/rank7-joint-endframes/README.md"
PRODUCER = ROOT / "research/rank7-joint-endframes/producer.py"
PRICES = ROOT / "research/rank7-joint-endframes/construction/STAGE-PRICES.json"
MARKER = "PASS_RANK7_V45_MARGIN joint_positive=true singles_negative=true no_new_kappa"
BASIS = (256, 128, 64, 35, 16, 11, 5)
HELPERS = (249, 251, 265, 267)
NORMALS = (7, 42, 45)


def fail(message):
    raise SystemExit("FAIL_RANK7_V45_MARGIN " + message)


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
        "research/rank7-joint-endframes/README.md",
        "research/rank7-joint-endframes/producer.py",
        "research/rank7-joint-endframes/construction/STAGE-PRICES.json",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def even(vector, normal):
    return (vector & normal).bit_count() % 2 == 0


def span_rank(vectors):
    basis = []
    for vector in vectors:
        reduced = vector
        for row in basis:
            reduced = min(reduced, reduced ^ row)
        if reduced:
            basis.append(reduced)
    return len(basis)


def margin(delta, count, break_even):
    return -delta - count * break_even


def evaluate():
    authenticate()
    readme = README.read_text(encoding="utf-8")
    producer = PRODUCER.read_text(encoding="utf-8")
    prices = json.loads(PRICES.read_text(encoding="utf-8"))
    require("(x & normal).bit_count() % 2 == 0" in producer, "the hyperplane test moved")
    require("'V45': ([256, 128, 64, 35, 16, 11, 5], [249, 251, 265, 267])" in producer, "the V45 group moved")
    require("E_7 ∩ E_42 ∩ E_45" in readme, "the intersection claim moved")
    # The family-status page and selected record are provenance pins, checked at base_commit by scripts/research_package.py.
    require("0.001729033982646513517717" in readme, "the headline moved")
    weights = prices["weights"]
    break_even = weights["break_even"]
    require(break_even == weights["c"]["1"] - 25371, "the break-even is not c1 minus 25,371")
    require("margins below are -delta - k * break_even" in weights["break_even_definition"], "the margin formula moved")
    group = next(row for row in prices["stage1"]["groups"] if row["group"] == "V45")
    require(tuple(group["W"]) == BASIS and tuple(group["helpers"]) == HELPERS, "the V45 record moved")
    require(span_rank(BASIS) == 7, "the listed basis is not rank 7")
    require(all(even(vector, normal) for vector in BASIS for normal in NORMALS), "a basis vector leaves a hyperplane")
    require(NORMALS[0] ^ NORMALS[1] == NORMALS[2], "the three normals are independent")
    intersection = [vector for vector in range(512) if all(even(vector, normal) for normal in NORMALS)]
    require(span_rank(intersection) == 7 and span_rank(list(intersection) + list(BASIS)) == 7, "the basis misses the intersection")
    require(set(group["singles_margin"]) == {str(helper) for helper in HELPERS}, "a single margin is missing")
    require(set(group["singles_margin"].values()) == {-53141}, "a single margin changed")
    for subset in group["subsets"]:
        count = len(subset["helpers"])
        require(margin(subset["delta"], count, break_even) == subset["margin"], "a subset margin disagrees with the formula")
        require((count == 4) == (subset["margin"] > 0), "the sign of a subset margin moved")
    require(group["joint_margin"] == margin(group["joint_delta"], 4, break_even) == 22972, "the joint margin moved")
    dropped = [subset["margin"] for subset in group["subsets"] if len(subset["helpers"]) == 3]
    require(dropped and set(group["joint_margin"] - value for value in dropped) == {25371}, "the drop-one gap moved")
    return {
        "group": "V45",
        "subspace_rank": 7,
        "single_margin": -53141,
        "joint_margin": 22972,
        "proper_subsets_negative": True,
        "drop_one_gap": 25371,
        "headline_is_selected": False,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
