#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Behavioral checks of actual retimed words and deliberate coverage limits."""
import copy
import gzip
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("cut_audit", HERE / "verify.py")
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


def read_word(tag):
    return json.loads(gzip.decompress((HERE / "inputs" / f"eight-alias-{tag}.json.gz").read_bytes()))


def replay(word, events):
    live = set(range(704)) - set(word["removed"])
    rows = {r: {(r, ()): V.Q(1)} for r in live}
    for gate in V.prefix(word):
        V.apply(rows, gate)
    for _, gate in events:
        V.apply(rows, gate)
    return rows


def frame_replay(word, events, block_labels):
    live = set(range(704)) - set(word["removed"])
    state = {r: V.frame([word["ports"][r]]) if r < 112 else V.frame([]) for r in live}
    for register, values in word["start_extra"].items():
        state[int(register)] = V.frame(values)
    for gate in word["A"]:
        V.advance_frame(state, gate, word)
    for label, gate in events:
        if label in block_labels:
            V.need(all(state[r] == V.frame(gate[-1]) for r in V.incident(gate)),
                   "relocated recovery requires an additional climb")
        V.advance_frame(state, gate, word)
    return state


class CutAuditTests(unittest.TestCase):
    def test_noncommutative_forward_backward(self):
        V.algebra_controls()

    def test_pair_order_is_essential(self):
        word = read_word("base")
        word["B"][687], word["B"][688] = word["B"][688], word["B"][687]
        with self.assertRaisesRegex(V.AuditError, "lender 80"):
            V.check_cuts(word, reverse=False)

    def test_older_lenders_need_not_be_original_inputs(self):
        result = V.check_cuts(read_word("base"))
        old = {x["lender"]: x["row"] for x in result["older_partner_handoffs"]}
        self.assertEqual(old[4], [[4, [], "1/2"], [68, [], "-1/2"]])
        self.assertEqual(old[12], [[12, [], "1"], [31, [], "1"]])
        self.assertEqual(old[33], [[33, [], "1"]])

    def test_target_prelude_is_outside_scope(self):
        word = read_word("base")
        original = V.check_cuts(word, reverse=False)
        altered = copy.deepcopy(word)
        next(g for g in altered["A"][:altered["prelude_events"]]
             if g[0] == "add")[3] *= 2
        self.assertEqual(V.check_cuts(altered, reverse=False), original)
        self.assertNotEqual(replay(altered, V.timeline(altered)),
                            replay(word, V.timeline(word)))

    def test_retimed_extremes_and_adjacent_blockers(self):
        # Rebuild and replay all 28 endpoint placements on every one of the
        # 646 input columns. This catches timeline/indexing errors that a
        # collection of locally correct commutators alone would not catch.
        successful = rejected = frame_only = 0
        for tag in ("base", "extra"):
            word = read_word(tag)
            events = V.timeline(word)
            baseline = replay(word, events)
            end_frames = frame_replay(word, events, set())
            for window in V.movement_windows(word):
                labels = {f"B:{i}:gate" for i in window["original_B_indices"]}
                block = [item for item in events if item[0] in labels]
                skeleton = [item for item in events if item[0] not in labels]
                left, right = window["skeleton_cuts_inclusive"]
                for position in (left, right):
                    moved = skeleton[:position] + block + skeleton[position:]
                    self.assertEqual(replay(word, moved), baseline,
                                     (tag, window["block"], position))
                    self.assertEqual(frame_replay(word, moved, labels), end_frames)
                    successful += 1
                for position in (left - 1, right + 1):
                    self.assertTrue(0 <= position <= len(skeleton))
                    moved = skeleton[:position] + block + skeleton[position:]
                    same_map = replay(word, moved) == baseline
                    try:
                        same_frames = frame_replay(word, moved, labels) == end_frames
                    except V.AuditError:
                        same_frames = False
                    self.assertFalse(same_map and same_frames)
                    rejected += 1
                    frame_only += same_map and not same_frames
        self.assertEqual((successful, rejected, frame_only), (28, 28, 2))


if __name__ == "__main__":
    unittest.main()
