#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Build a candidate joint rank-two child-boundary recipe for one pinned word."""
import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = Path(__file__).resolve().parent
WORD = ROOT / "research/r480-owner-optimum/inputs/local/FULL-WORD.json.gz"
SELECTED_WORD_PIN = ROOT / "research/gauge44-slots/construction/slots/SLOT-PINS-k8.json"
WORD_SHA = "c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8"
BASE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}


def span(vectors):
    pivots = {}
    for value in vectors:
        x = value
        for pivot in sorted(pivots, reverse=True):
            if (x >> pivot) & 1:
                x ^= pivots[pivot]
        if x:
            pivot = x.bit_length() - 1
            for k in tuple(pivots):
                if (pivots[k] >> pivot) & 1:
                    pivots[k] ^= x
            pivots[pivot] = x
    return tuple(pivots[k] for k in sorted(pivots, reverse=True))


def complement(old, new):
    assert span(list(old) + list(new)) == new and len(new) == len(old) + 1
    for vector in new:
        if len(span(list(old) + [vector])) == len(old) + 1:
            return vector
    raise AssertionError("codimension-one frame has no complement")


def role(register, v):
    if register < v:
        return "input"
    if register < 2 * v:
        return "target"
    return "helper"


def regs(operation):
    return [operation[1]] + ([operation[2]] if operation[0] == "add" else [])


def gate_pair(stage, section, index, operation, old_frames, new_frame, v, cleanup_index=None):
    assert operation[0] == "add" and len(old_frames) == 2
    coeff = Q(operation[3], operation[4])
    assert coeff != 0
    return {
        "stage": stage,
        "section": section,
        "index": index,
        "cleanup_index": cleanup_index,
        "registers": [operation[1], operation[2]],
        "coefficient": str(coeff),
        "quotient_vectors": [complement(old, new_frame) for old in old_frames],
        "rank": 2,
    }


def terminal_pair(left, right, v):
    return {
        "stage": "terminal",
        "section": "final",
        "index": None,
        "cleanup_index": None,
        "registers": [left[0], right[0]],
        "coefficient": None,
        "quotient_vectors": [complement(old, new) for _, old, new in (left, right)],
        "rank": 2,
    }


def build():
    raw = gzip.decompress(WORD.read_bytes())
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == WORD_SHA, (digest, WORD_SHA)
    assert json.loads(SELECTED_WORD_PIN.read_text())["word_sha256"] == digest
    word = json.loads(raw)
    v, helpers = word["report"]["v"], word["report"]["R"]
    n = 2 * v + helpers
    assert word["report"]["m"] == 73 and word["report"]["h"] == 9
    assert {int(r): c for r, c in word["report"]["local_profile"].items()} == BASE

    current = [() for _ in range(n)]
    for i, port in enumerate(word["ports"]):
        current[i] = span([port])
    for r, frame in word.get("start_extra", {}).items():
        current[int(r)] = span(frame)
    local_profile = Counter()
    pairs = []

    for section in ("A", "B"):
        for index, operation in enumerate(word[section]):
            target = span(operation[-1])
            touched = regs(operation)
            old = [current[r] for r in touched]
            deltas = [len(target) - len(frame) for frame in old]
            assert all(span(list(frame) + list(target)) == target for frame in old)
            for delta in deltas:
                if delta:
                    local_profile[delta] += 1
            if len(touched) == 2 and deltas == [1, 1]:
                pairs.append(gate_pair("gate", section, index, operation, old, target, v))
            for r in touched:
                current[r] = target

    for schedule_index, (cleanup_index, frame) in enumerate(word.get("early_cleanup", [])):
        operation = word["cleanup"][cleanup_index]
        target = span(frame)
        touched = regs(operation)
        old = [current[r] for r in touched]
        deltas = [len(target) - len(x) for x in old]
        assert all(span(list(x) + list(target)) == target for x in old)
        for delta in deltas:
            if delta:
                local_profile[delta] += 1
        if len(touched) == 2 and deltas == [1, 1]:
            pairs.append(gate_pair("early-cleanup", "cleanup", schedule_index, operation, old, target, v,
                                   cleanup_index))
        for r in touched:
            current[r] = target

    full = span([1 << i for i in range(9)])
    finals = {int(r): span(frame) for r, frame in word.get("helper_final", {}).items()}
    terminal = []
    for r in range(n):
        if v <= r < 2 * v:
            target = span([x for x in range(1, 512) if (x & word["ports"][r - v]).bit_count() % 2 == 0])
        else:
            target = finals.get(r, full)
        old = current[r]
        assert span(list(old) + list(target)) == target
        delta = len(target) - len(old)
        if delta:
            local_profile[delta] += 1
        if delta == 1:
            terminal.append((r, old, target))
        current[r] = target

    local_profile.update(Counter(word["report"]["centre_ranks"]))
    assert dict(sorted(local_profile.items())) == BASE
    assert len(terminal) == 326 and [x[0] for x in terminal] == sorted(x[0] for x in terminal)
    assert len(terminal) % 2 == 0
    for i in range(0, len(terminal), 2):
        pairs.append(terminal_pair(terminal[i], terminal[i + 1], v))

    paired = len(pairs)
    profile_after = dict(BASE)
    profile_after[1] -= 2 * paired
    profile_after[2] += paired
    assert profile_after == {1: 906, 2: 1171, 3: 432, 4: 142, 5: 82, 8: 8}
    assert sum(r * c for r, c in profile_after.items()) == sum(r * c for r, c in BASE.items()) == 5586
    keys = {(p["stage"], p["section"], tuple(p["registers"]) if p["stage"] == "terminal" else p["index"])
            for p in pairs}
    assert len(keys) == paired

    return {
        "schema_version": 1,
        "source": {
            "path": "research/r480-owner-optimum/inputs/local/FULL-WORD.json.gz",
            "decompressed_sha256": digest,
        },
        "model": {"m": 73, "stages": 9, "families": 896, "centre": 64, "idle_rank_cap": 51},
        "pairing_rule": "pair two codimension-one gate participants at each shared target frame; pair all codimension-one early-cleanup gate participants at their scheduled frame; pair terminal codimension-one register transitions in increasing register order",
        "counts": {
            "gate_pairs": sum(p["stage"] == "gate" for p in pairs),
            "early_cleanup_pairs": sum(p["stage"] == "early-cleanup" for p in pairs),
            "terminal_pairs": sum(p["stage"] == "terminal" for p in pairs),
            "total_rank_two_children": paired,
            "a_gate_count": len(word["A"]),
            "b_gate_count": len(word["B"]),
            "source_gate_count": len(word["A"]) + len(word["B"]),
            "scheduled_early_cleanup_entries": len(word.get("early_cleanup", [])),
            "terminal_rank_one_transitions": len(terminal),
        },
        "profile_before": {str(k): v for k, v in sorted(BASE.items())},
        "profile_after_ideal_joint_interfaces": {str(k): v for k, v in sorted(profile_after.items())},
        "rank_mass_before_and_after": 5586,
        "pairs": pairs,
        "charge_ledger": {
            "native_scalar_gates_added": 0,
            "frame_edits": 0,
            "additional_source_copies_assumed": 0,
            "additional_restoration_gates_assumed": 0,
            "additional_precision_cost_assumed": 0,
            "recursive_profile_change": "753 pairs of rank-1 children are replaced by 753 rank-2 joint-interface children",
            "unpriced_obligation": "prove and physically host the new joint rank-two child boundary, including source access, copies, restoration, phase/precision transfer, and complete-call ownership",
        },
        "scope": "Conditional local cost-interface mechanism only; no supplier admission, global assembly, or new kappa.",
    }


if __name__ == "__main__":
    result = build()
    output = PKG / "PAIR-RECIPE.json"
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print("PASS_BUILD_JOINT_CHILD_RECIPE", result["counts"], hashlib.sha256(output.read_bytes()).hexdigest())
