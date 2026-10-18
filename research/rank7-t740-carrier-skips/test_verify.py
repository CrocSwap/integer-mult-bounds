# SPDX-License-Identifier: Apache-2.0
"""Behavioral rejection controls for the composed scientific boundary."""

import copy
import unittest
from pathlib import Path
from unittest.mock import patch

import materialize as m
import reproduce
import verify
import word_check


class CompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = m.read(m.MAIN / "data/WORD-base.json.gz")
        cls.new = m.read(m.PACKAGE / "vendor/pr3042/edits/FINAL-WORD-base.json.gz")
        cls.edits = m.read(m.PACKAGE / "vendor/pr3042/edits/EDITS.json")["edits"]["base"]
        cls.check = m.load("vendor/pr3021/verify.py", "test_retained_cleanup")

    def check_word(self, old=None, new=None, edits=None):
        return word_check.check_word(
            self.old if old is None else old, self.new if new is None else new,
            self.edits if edits is None else edits, self.check.cleanup)

    def test_dirty_action_positive_and_wrong_coefficient(self):
        self.assertEqual(self.check_word()["skips"], 6)
        changed = copy.deepcopy(self.edits)
        gate = next(g for g in changed[0]["new"] if g[0] == "add")
        gate[3] += gate[4]
        with self.assertRaisesRegex(ValueError, "dirty-input block action"):
            self.check_word(edits=changed)

    def test_private_endpoint_and_inverse_cleanup(self):
        for field in ("helper_final", "cleanup"):
            changed = copy.deepcopy(self.new)
            if field == "helper_final":
                changed[field].pop(next(iter(changed[field])))
            else:
                changed[field][0][3] += 1
            with self.assertRaises(ValueError):
                self.check_word(new=changed)

    def test_ordered_widths_not_only_inventory(self):
        old = m.read(m.MAIN / "allocation/PROVIDERS.json")
        new = m.read(m.PACKAGE / "vendor/pr3042/allocation/PROVIDERS.json")
        declared = m.read(m.PACKAGE / "vendor/pr3042/edits/EDITS.json")["declared"]
        word_check.check_providers(old, new, declared)
        widths = new["gauge44"]["widths"]
        other = next(i for i, x in enumerate(widths) if x != widths[0])
        widths[0], widths[other] = widths[other], widths[0]
        with self.assertRaisesRegex(ValueError, "ordered helper widths"):
            word_check.check_providers(old, new, declared)

    def test_actual_three_admission_arguments(self):
        source, work = Path("/source"), Path("/work")
        command = ["python", "admit.py"]
        for flag, name in (("--fill", "FILL.json.gz"), ("--order", "ORDER.json"),
                           ("--dispatch", "DISPATCH.json")):
            command += [flag, str(source / "allocation" / name)]
        original = command.copy()
        self.assertEqual(len(reproduce.replace_allocation(
            [("complete-admission", command)], source, work)), 3)
        self.assertEqual(command[command.index("--fill") + 1], "/work/COMPOSED-FILL.json.gz")
        original[original.index("--order") + 1] = "/stale/ORDER.json"
        with self.assertRaisesRegex(ValueError, "preimage"):
            reproduce.replace_allocation([("complete-admission", original)], source, work)

    def test_full_physical_and_prefix_charge(self):
        self.assertEqual(verify.physical_bound()["physical"], 663549)
        self.assertEqual(verify.physical_bound()["reserve"], 1512)
        for arguments in ({"buffers": 72}, {"payload": 1511}, {"replicas": 74}):
            with self.assertRaises(ValueError):
                verify.physical_bound(**arguments)

    def test_input_drift_rejects_before_source_execution(self):
        with (patch.object(m, "digest", return_value="0" * 64),
              self.assertRaisesRegex(ValueError, "source digest")):
            m.load("vendor/pr3024/lift.py", "must_not_execute")

    def test_truncated_materialization_rejects(self):
        with self.assertRaisesRegex(ValueError, "role count"):
            m.write_fill(Path("/must-not-create.json.gz"), [])

    def test_unpaid_child_rejects_before_root_calculation(self):
        root = m.load_path(m.MAIN / "tools/root.py", "test_exact_root")
        changed = m.PROFILE.copy()
        changed[1] += 1
        with self.assertRaisesRegex(ValueError, "rank-mass identity"):
            root.kappa_from_profile(changed, 740)


if __name__ == "__main__":
    unittest.main()
