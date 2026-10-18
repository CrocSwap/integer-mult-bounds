# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the exact source rewrite and release recipe."""

import copy
import unittest
from unittest.mock import patch

import frame_trace
import reproduce
import rewrite as rw
import verify as v


class SharedRestoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.authenticate()
        cls.parent = v.read(v.PARENT / "data/WORD-base.json.gz")
        cls.specification = v.read(v.PACKAGE / "vendor/R1.json")
        cls.frames = v.load(v.PARENT / "vendor/preload_move.py", "test_bound_frames")

    def test_dirty_sources_and_targets(self):
        self.assertEqual(
            v.scalar_identity(),
            [
                ["1", "0", "0", "0"],
                ["0", "1", "0", "0"],
                ["1", "-2", "1", "0"],
                ["1", "-2", "0", "1"],
            ],
        )

    def test_both_literal_providers(self):
        for variant in ("base", "extra"):
            candidates = v.words(variant, self.frames)
            self.assertEqual(candidates["R1R2"]["report"]["local_profile"], rw.LOCAL)
            self.assertEqual(len(candidates["R1"]["restore"]), 204)
            self.assertEqual(len(candidates["R1R2"]["restore"]), 204)
            self.assertEqual(len(candidates["R1R2"]["helper_final"]), 91)
            self.assertEqual(len(candidates["R1"]["cleanup"]), 5208)
            self.assertEqual(len(candidates["R1R2"]["cleanup"]), 5208)
            for key in (
                "A",
                "B",
                "warps",
                "compensation",
                "helper_final",
                "start_extra",
            ):
                self.assertEqual(candidates["R1R2"][key], candidates["parent"][key])

    def test_frame_gain_and_bad_high_frame(self):
        r1 = rw.r1(self.parent, self.specification, "base")
        candidate = rw.r2(r1)
        old, entry = frame_trace.census(r1)
        new, new_entry = frame_trace.census(candidate)
        self.assertEqual(entry, new_entry)
        self.assertEqual(new["1"] - old["1"], -2)
        self.assertEqual(new["2"] - old["2"], 1)
        candidate["restore"][162][-1] = rw.HIGH
        too_expensive, _ = frame_trace.census(candidate)
        self.assertEqual(too_expensive, old)

    def test_source_addressed_order_refused(self):
        composed = rw.r2(rw.r1(self.parent, self.specification, "base"))
        # R2 shifts R1's original address. Refuse that order instead of silently
        # reinterpreting a source-addressed edit on a different word.
        self.assertEqual(len(composed["restore"]), 204)
        with self.assertRaisesRegex(ValueError, "R1 literal preimage"):
            rw.r1(rw.r2(self.parent), self.specification, "base")

    def test_changed_preimages_refused(self):
        for index, field, value in ((162, 3, -1), (163, -1, rw.FULL), (177, 2, 55)):
            mutant = copy.deepcopy(self.parent)
            mutant["restore"][index][field] = value
            with self.assertRaisesRegex(ValueError, "literal R2 preimage"):
                rw.r2(mutant)

    def test_consumer_observer_refused(self):
        mutant = copy.deepcopy(self.parent)
        mutant["restore"][176] = ["add", 45, 22, 1, 1, rw.HIGH]
        with self.assertRaisesRegex(ValueError, "commuting consumer"):
            rw.r2(mutant)

    def test_hidden_source_contact_refused(self):
        mutant = copy.deepcopy(self.parent)
        mutant["restore"][164] = ["add", 18, 54, 1, 1, rw.HIGH]
        with self.assertRaisesRegex(ValueError, "observer"):
            rw.r2(mutant)

    def test_declared_stage_reconstructs_exact_restore(self):
        original = self.parent
        composed = rw.r2(rw.r1(original, self.specification, "base"))
        actual = copy.deepcopy(original["restore"])
        edits = rw.stage_spec(original, composed)
        for edit in sorted(edits, key=lambda item: -item["start"]):
            self.assertEqual(actual[edit["start"] : edit["stop"]], edit["old"])
            actual[edit["start"] : edit["stop"]] = edit["new"]
        self.assertEqual(actual, composed["restore"])

    def test_source_pin_failure(self):
        with (
            patch.object(v, "digest", return_value="0" * 64),
            self.assertRaisesRegex(ValueError, "source pin"),
        ):
            v.authenticate()

    def test_only_declared_recipe_arguments_change(self):
        recipe = [
            ["declared-edit-stage", ["builder", "--local-package", "original"]],
            [
                "derive-closed-adapters",
                ["derive", "--source-profile", "old", "--source-commit", "old"],
            ],
            [
                "complete-admission",
                ["admit", "--source-profile", "old", "--fill", "unchanged"],
            ],
        ]
        changes = reproduce.retarget(recipe, v.PACKAGE)
        self.assertEqual(len(changes), 4)
        self.assertEqual(recipe[-1][1][-2:], ["--fill", "unchanged"])
        self.assertEqual(recipe[-1][1][2], "rank7-shared-restore-fanin")
        with self.assertRaisesRegex(ValueError, "four|explicit"):
            reproduce.retarget([], v.PACKAGE)


if __name__ == "__main__":
    unittest.main()
