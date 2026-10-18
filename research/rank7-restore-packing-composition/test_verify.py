# SPDX-License-Identifier: Apache-2.0
"""Behavioral checks for the pinned finite composition and rejection paths."""

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("composition_verify", Path(__file__).with_name("verify.py"))
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("verifier import")
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)


class CompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.geometry, cls.moment = verify.retained_checkers()
        cls.data = verify.inputs()
        cls.fill = verify.composed_fill()
        cls.journal = verify.read(verify.PACKAGE / "vendor/pr3018/EXCHANGE.json")
        cls.original = verify.read(verify.MAIN / "allocation/FILL.json.gz")
        cls.edits = verify.read(verify.PACKAGE / "vendor/pr3015/edits/EDITS.json")["edits"]

    def test_literal_complete_composition_and_positive_gain(self):
        receipt = verify.run()
        self.assertEqual(receipt["status"], "PASS_RESTORE_PACKING_COMPOSITION_FINITE")
        self.assertEqual(receipt["profile"], {1: 1644352, 2: 470862, 3: 159472,
            4: 71928, 5: 13710, 8: 5328, 14: 1, 48: 28190})
        self.assertEqual(receipt["gain"], ["2304487940143033/10000000000000000000000000",
                                          "460897588028607/2000000000000000000000000"])
        self.assertEqual((receipt["roles"], receipt["physical"], receipt["private_buffers"]),
                         (271728, 66813, 91))

    def test_missing_role(self):
        fill = copy.deepcopy(self.fill)
        fill["rows"].pop()
        with self.assertRaisesRegex(ValueError, "complete role count"):
            verify.check_allocation(self.geometry, fill, self.data)

    def test_duplicate_helper(self):
        fill = copy.deepcopy(self.fill)
        fill["rows"][1][1] = fill["rows"][0][1]
        with self.assertRaisesRegex(ValueError, "duplicate helper"):
            verify.check_allocation(self.geometry, fill, self.data)

    def test_family_collision(self):
        fill = copy.deepcopy(self.fill)
        fill["rows"][1][2:] = fill["rows"][0][2:]
        with self.assertRaisesRegex(ValueError, "same-call family collision"):
            verify.check_allocation(self.geometry, fill, self.data)

    def test_unavailable_source_window(self):
        fill = copy.deepcopy(self.fill)
        windows = self.geometry.windows(self.data[3], self.data[0], 74)
        owner, child = next(key for key, (_, lower, _) in windows.items() if lower >= 0)
        fill["rows"][0][2:5] = [owner, child, 0]
        with self.assertRaisesRegex(ValueError, "literal source window"):
            verify.check_allocation(self.geometry, fill, self.data)

    def test_overlap_across_calls(self):
        fill = copy.deepcopy(self.fill)
        previous = {}
        for index, row in enumerate(fill["rows"]):
            key = tuple(row[2:5])
            if key in previous and row[0] != previous[key][0]:
                fill["rows"][index][5] = previous[key][5]
                break
            previous[key] = row
        else:
            self.fail("expected a multiply occupied bin")
        with self.assertRaisesRegex(ValueError, "bin overlap"):
            verify.check_allocation(self.geometry, fill, self.data)

    def test_claimed_profile_off_by_one(self):
        claimed = verify.EXPECTED.copy()
        claimed[1] += 1
        with self.assertRaisesRegex(ValueError, "literal complete profile"):
            verify.check_allocation(self.geometry, self.fill, self.data, claimed=claimed)

    def test_private_buffer_omission(self):
        with self.assertRaisesRegex(ValueError, "91 private buffers"):
            verify.check_allocation(self.geometry, self.fill, self.data, buffers=90)

    def test_stale_original_local_profile(self):
        providers = copy.deepcopy(self.data[-1])
        providers["extra"]["actual_paid_profile"]["1"] = 2445
        providers["extra"]["actual_paid_profile"]["2"] = 706
        with self.assertRaisesRegex(ValueError, "provider profile agrees with word"):
            verify.check_providers(providers)

    def test_reordered_widths_with_unchanged_inventory(self):
        providers = copy.deepcopy(self.data[-1])
        widths = providers["extra"]["widths"]
        widths[0], widths[2] = widths[2], widths[0]
        self.assertEqual(sorted(widths), sorted(self.data[-1]["extra"]["widths"]))
        with self.assertRaisesRegex(ValueError, "ordered helper widths"):
            verify.check_providers(providers)

    def test_stale_journal_preimage(self):
        journal = copy.deepcopy(self.journal)
        journal["edits"][0][1][5] += 1
        with self.assertRaisesRegex(ValueError, "journal preimage"):
            verify.apply_exchange(self.original, journal)

    def test_duplicate_journal_edit(self):
        journal = copy.deepcopy(self.journal)
        journal["edits"][1] = journal["edits"][0]
        with self.assertRaisesRegex(ValueError, "duplicate journal edit"):
            verify.apply_exchange(self.original, journal)

    def test_restore_scalar_failure(self):
        old = verify.read(verify.MAIN / "data/WORD-base.json.gz")
        new = verify.read(verify.PACKAGE / "vendor/pr3015/edits/FINAL-WORD-base.json.gz")
        edits = copy.deepcopy(self.edits["base"])
        edits[0]["new"][0][3] = -1
        with self.assertRaisesRegex(ValueError, "R1 scalar identity"):
            verify.check_word(old, new, edits)

    def test_restore_preimage_failure(self):
        old = verify.read(verify.MAIN / "data/WORD-base.json.gz")
        new = verify.read(verify.PACKAGE / "vendor/pr3015/edits/FINAL-WORD-base.json.gz")
        edits = copy.deepcopy(self.edits["base"])
        edits[0]["old"][0][3] = 1
        with self.assertRaisesRegex(ValueError, "R1 preimage"):
            verify.check_word(old, new, edits)

    def test_source_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary)
            (package / "SOURCES.json").write_text(json.dumps({"files": [
                {"path": "input", "usage": "input", "sha256": "0" * 64}]}), encoding="utf-8")
            (package / "VENDOR.json").write_text("[]", encoding="utf-8")
            (package / "input").write_text("changed", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "source drift"):
                verify.authenticate(root=package, package=package)

    def test_no_op_moment_gain(self):
        with self.assertRaisesRegex(ValueError, "strict complete moment improvement"):
            verify.moment_receipt(self.moment, verify.EXPECTED, verify.EXPECTED)


if __name__ == "__main__":
    unittest.main()
