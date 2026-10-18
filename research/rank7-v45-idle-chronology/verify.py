#!/usr/bin/env python3
"""Read V45 widths, the recorded idle histograms, and the shipped call order.

Width is the predecessor formula: the end-frame length minus the start-extra
length. Idle is recomputed from each stored basis pattern. The order check is a
byte comparison. None of this re-solves a cap.
"""

import gzip
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
DATA = ROOT / "research/rank7-joint-endframes"
HELPERS = (249, 251, 265, 267)
MARKER = (
    "PASS_RANK7_V45_IDLE_CHRONOLOGY helpers=4 width=8to7 "
    "order_matches_predecessor calls=666 no_new_kappa"
)


def fail(message):
    raise SystemExit("FAIL_RANK7_V45_IDLE_CHRONOLOGY " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)


def width_of(word, helper):
    final = word["helper_final"].get(str(helper), [0] * 9)
    extra = word["start_extra"].get(str(helper), [])
    return len(final) - len(extra)


def live_widths(word):
    removed = set(word["removed"])
    widths = {}
    for helper in range(224, 704):
        if helper in removed:
            continue
        widths[helper] = width_of(word, helper)
    return widths


def idle_of(stage):
    idle = {}
    for pattern in stage["basis_patterns"]:
        rank = pattern["capacity"] - sum(pattern["widths"])
        if rank:
            count = Fraction(pattern["count_per_replica"])
            idle[rank] = idle.get(rank, 0) + count
    stored = {int(rank): Fraction(count) for rank, count in stage["idle_per_replica"].items()}
    require(idle == stored, "stored idle does not match the basis patterns")
    return {str(rank): str(count) for rank, count in sorted(idle.items())}


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/rank7-joint-endframes/data/WORD-base.json.gz",
        "research/rank7-joint-endframes/data/WORD-extra.json.gz",
        "research/rank7-joint-endframes/data/PARENT-base.json.gz",
        "research/rank7-joint-endframes/data/PARENT-extra.json.gz",
        "research/rank7-joint-endframes/certificates/RELAX-STAGES.json",
        "research/rank7-joint-endframes/certificates/RELAX-CAP.json",
        "research/rank7-joint-endframes/allocation/ORDER.json",
        "research/rank7-joint-endframes/allocation/DISPATCH.json",
        "research/rank7-joint-endframes/allocation/baseline/ORDER.json",
        "research/paired-helper-extension/allocation/ORDER.json",
        "research/paired-helper-extension/allocation/DISPATCH.json",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    shipped = [load(DATA / "data" / name) for name in ("WORD-base.json.gz", "WORD-extra.json.gz")]
    parents = [load(DATA / "data" / name) for name in ("PARENT-base.json.gz", "PARENT-extra.json.gz")]
    require(all(width_of(word, helper) == 7 and not word["start_extra"].get(str(helper), []) for word in shipped for helper in HELPERS), "a shipped V45 width moved")
    require(all(width_of(word, helper) == 8 for word in parents for helper in HELPERS), "a parent V45 width moved")
    parent_widths = live_widths(parents[0])
    shipped_widths = live_widths(shipped[0])
    require(parent_widths == live_widths(parents[1]) and shipped_widths == live_widths(shipped[1]), "providers disagree on widths")
    changes = {}
    for helper in sorted(set(parent_widths) | set(shipped_widths)):
        if parent_widths.get(helper) != shipped_widths.get(helper):
            changes.setdefault((parent_widths.get(helper), shipped_widths.get(helper)), []).append(helper)
    require(changes[(8, 7)] == [249, 251, 265, 267, 299, 331], "the width-8 drops changed")
    require(changes[(9, 8)] == [226, 228, 230, 363, 395], "the extraction widths changed")
    require(len(changes[(7, 6)]) == 16 and set(changes) == {(8, 7), (9, 8), (7, 6)}, "an unexpected width change appeared")

    stages = load(DATA / "certificates/RELAX-STAGES.json")
    final = load(DATA / "certificates/RELAX-CAP.json")
    idle = {
        "parent": idle_of(stages["parent"]),
        "stage1": idle_of(stages["stage1"]),
        "stage2": idle_of(stages["stage2"]),
        "final": idle_of(final),
    }
    require(idle["parent"] != idle["stage1"], "stage 1 left the parent idle histogram")
    require(idle["stage2"] == idle["final"], "the final idle histogram left stage 2")

    order = (DATA / "allocation/ORDER.json").read_bytes()
    dispatch = (DATA / "allocation/DISPATCH.json").read_bytes()
    predecessor = ROOT / "research/paired-helper-extension/allocation"
    require(order == (predecessor / "ORDER.json").read_bytes(), "ORDER left the predecessor chronology")
    require(dispatch == (predecessor / "DISPATCH.json").read_bytes(), "DISPATCH left the predecessor chronology")
    require(order != (DATA / "allocation/baseline/ORDER.json").read_bytes(), "the baseline order is the shipped order")
    parsed = json.loads(order)
    require(len(parsed) == 666 and all(len(row) == 2 for row in parsed), "the call order changed shape")
    require(len(json.loads(dispatch)) == 666, "DISPATCH length changed")
    return {
        "helpers": list(HELPERS),
        "parent_width": 8,
        "shipped_width": 7,
        "providers": 2,
        "width_changes": {
            "8_to_7": changes[(8, 7)],
            "7_to_6": changes[(7, 6)],
            "9_to_8": changes[(9, 8)],
        },
        "idle_per_replica": idle,
        "stage1_idle_moves": True,
        "final_idle_equals_stage2": True,
        "order_calls": 666,
        "order_matches_predecessor": True,
        "baseline_order_matches": False,
        "cap_basis_resolved": False,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
