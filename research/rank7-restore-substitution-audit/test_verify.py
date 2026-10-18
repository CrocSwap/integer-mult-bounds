# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the independently checked implication."""

import copy
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import verify as audit
from frames import span, trace


class SubstitutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = audit.read(audit.PACKAGE / "vendor/EDITS.json")
        cls.parents = {tag: audit.read(audit.PARENT / f"data/WORD-{tag}.json.gz")
                       for tag in ("base", "extra")}
        cls.candidates = {
            tag: audit.read(audit.PACKAGE / f"vendor/FINAL-WORD-{tag}.json.gz")
            for tag in ("base", "extra")}

    def test_both_literal_candidates(self):
        result = audit.audit()
        self.assertEqual(result["status"], "PASS_RANK7_RESTORE_SUBSTITUTION_AUDIT")
        self.assertEqual(result["bill"]["delta"], {1: -7992, 2: 3996})
        for tag in ("base", "extra"):
            edits = result["variants"][tag]["edits"]
            self.assertEqual([(e["old_gates"], e["new_gates"]) for e in edits],
                             [(26, 33), (13, 15)])
            self.assertEqual([e["skipped_registers"] for e in edits],
                             [[22, 40, 54, 63], [5, 73]])

    def test_every_hunk_rejects_dropped_gate(self):
        for tag in ("base", "extra"):
            for edit in self.spec["edits"][tag]:
                with (self.subTest(tag=tag, edit=edit["id"]),
                      self.assertRaisesRegex(ValueError, "dirty-state")):
                    audit.equal_operators(edit["old"], edit["new"][:-1])

    def test_every_hunk_rejects_wrong_coefficient(self):
        for tag in ("base", "extra"):
            for edit in self.spec["edits"][tag]:
                mutant = copy.deepcopy(edit["new"])
                mutant[0][3] *= -1
                with (self.subTest(tag=tag, edit=edit["id"]),
                      self.assertRaisesRegex(ValueError, "dirty-state")):
                    audit.equal_operators(edit["old"], mutant)

    def test_dirty_source_restoration_is_observable(self):
        frame = [1]
        old = [["add", 2, 0, 1, 1, frame], ["add", 2, 1, -2, 1, frame],
               ["add", 3, 0, 1, 1, frame], ["add", 3, 1, -2, 1, frame]]
        new = [["add", 0, 1, -2, 1, frame], ["add", 2, 0, 1, 1, frame],
               ["add", 3, 0, 1, 1, frame], ["add", 0, 1, 2, 1, frame]]
        self.assertEqual(audit.equal_operators(old, new), 4)
        self.assertEqual(audit.operator(old, range(4))[2],
                         audit.operator(new[:-1], range(4))[2])
        with self.assertRaisesRegex(ValueError, "dirty-state"):
            audit.equal_operators(old, new[:-1])

    def test_literal_preimage_is_required(self):
        edits = copy.deepcopy(self.spec["edits"]["base"])
        edits[0]["old"][0][3] *= -1
        with self.assertRaisesRegex(ValueError, "preimage"):
            audit.apply_hunks(self.parents["base"], edits)

    def test_unlisted_gate_change_is_rejected(self):
        mutant = copy.deepcopy(self.candidates["base"])
        mutant["restore"][0][3] *= -1
        with self.assertRaisesRegex(ValueError, "literal final restore"):
            audit.check_variant(self.parents["base"], mutant, self.spec["edits"]["base"])

    def test_nonmonotone_frame_is_rejected(self):
        mutant = copy.deepcopy(self.candidates["base"])
        mutant["restore"][162][-1] = mutant["restore"][162][-1][1:]
        with self.assertRaisesRegex(ValueError, "nonmonotone"):
            trace(mutant)

    def test_dependent_frame_generators_are_rejected(self):
        self.assertEqual(span((1, 2)), frozenset({0, 1, 2, 3}))
        with self.assertRaisesRegex(ValueError, "independent"):
            span((1, 2, 3))

    def test_stale_cleanup_is_rejected(self):
        mutant = copy.deepcopy(self.candidates["base"])
        mutant["cleanup"] = copy.deepcopy(self.parents["base"]["cleanup"])
        with self.assertRaisesRegex(ValueError, "exact changed sections"):
            audit.check_variant(self.parents["base"], mutant, self.spec["edits"]["base"])

    def test_incomplete_new_cleanup_is_rejected(self):
        mutant = copy.deepcopy(self.candidates["base"])
        mutant["cleanup"].pop()
        with self.assertRaisesRegex(ValueError, "derived cleanup"):
            audit.check_variant(self.parents["base"], mutant, self.spec["edits"]["base"])

    def test_stale_profile_is_rejected(self):
        mutant = copy.deepcopy(self.candidates["base"])
        mutant["report"]["local_profile"]["1"] += 1
        with self.assertRaisesRegex(ValueError, "reported local profile"):
            audit.check_variant(self.parents["base"], mutant, self.spec["edits"]["base"])

    def test_complete_bill_rejects_unpaid_child(self):
        original = audit.read(audit.PARENT / "allocation/PROFILE.json")
        parent = {int(r): n for r, n in original.items()}
        final = {int(r): n for r, n in audit.read(audit.PACKAGE / "vendor/PROFILE.json").items()}
        self.assertEqual(audit.whole_bill(parent, final)["rank_mass"], 4816512)
        final[1] -= 1
        with self.assertRaisesRegex(ValueError, "complete profile"):
            audit.whole_bill(parent, final)

    def test_actual_changed_source_bytes_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix="restore-audit-test-") as temporary:
            package = Path(temporary)
            shutil.copytree(audit.PACKAGE / "vendor", package / "vendor")
            for name in ("VENDOR.json", "SOURCES.json"):
                shutil.copyfile(audit.PACKAGE / name, package / name)
            source = package / "vendor/FINAL-WORD-base.json.gz"
            source.write_bytes(source.read_bytes() + b" ")
            with (patch.object(audit, "PACKAGE", package),
                  self.assertRaisesRegex(ValueError, "source digest")):
                audit.check_pins()


if __name__ == "__main__":
    unittest.main(verbosity=2)
