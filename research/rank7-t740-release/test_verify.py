# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the new materialization and admission boundary."""

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import materialize as m
import reproduce
import verify


class BoundaryTests(unittest.TestCase):
    def test_literal_release_recipe_changes_all_three_inputs(self):
        source, work = Path("/source"), Path("/work")
        recipe = [["native", ["python", "native.py"]], ["complete-admission", [
            "python", "admit.py", "--fill", "/source/allocation/FILL.json.gz",
            "--order", "/source/allocation/ORDER.json", "--dispatch",
            "/source/allocation/DISPATCH.json", "--jobs", "1"]]]
        original = copy.deepcopy(recipe)
        native = copy.deepcopy(recipe[0])
        changes = reproduce.replace_allocation(recipe, source, work)
        self.assertEqual(recipe[0], native)
        self.assertEqual(recipe[1][1], ["python", "admit.py", "--fill",
            "/work/COMPOSED-FILL.json.gz", "--order", "/work/ORDER.json",
            "--dispatch", "/work/DISPATCH.json", "--jobs", "1"])
        self.assertEqual([c["argument"] for c in changes], ["--fill", "--order", "--dispatch"])
        recipe = original
        recipe[1][1][5] = "/stale/ORDER.json"
        with self.assertRaisesRegex(ValueError, "recipe preimage"):
            reproduce.replace_allocation(recipe, source, work)

    def test_full_stock_and_missing_private_buffers(self):
        result = verify.physical_bound()
        self.assertEqual((result["physical"], result["stock_l2_bits"], result["reserve"]),
                         (663549, 1324, 1512))
        with self.assertRaisesRegex(ValueError, "all 91 private buffers"):
            verify.physical_bound(buffers=72)
        with self.assertRaisesRegex(ValueError, "paid prefix payload"):
            verify.physical_bound(payload=1511)
        with self.assertRaisesRegex(ValueError, "T740 physical contract"):
            verify.physical_bound(replicas=74)

    def test_source_drift_rejects_before_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "input.py").write_text("raise RuntimeError('must not execute')\n")
            (root / "PINS.json").write_text(json.dumps({"input.py": "0" * 64}))
            with patch.object(m, "ROOT", root), patch.object(m, "PACKAGE", root):
                with self.assertRaisesRegex(ValueError, "source digest"):
                    m.authenticate()
                with self.assertRaisesRegex(ValueError, "module source digest"):
                    m.load_path(root / "input.py", "must_not_execute")

    def test_streaming_writer_rejects_omitted_roles(self):
        class TruncatedRows:
            def __len__(self):
                return 2717280

            def __iter__(self):
                return iter([[0, 0, 0, 0, 0, 0]])

        with (
            tempfile.TemporaryDirectory() as temporary,
            self.assertRaisesRegex(ValueError, "no omitted materialized role"),
        ):
            m.write_fill(Path(temporary) / "fill.gz", TruncatedRows())

    def test_root_rejects_unpaid_child(self):
        wrong = dict(m.PROFILE)
        wrong[48] -= 1
        with self.assertRaisesRegex(ValueError, "rank-mass identity"):
            verify.moment(wrong)

    def test_r1_scalar_and_dirty_cleanup_controls(self):
        m.authenticate()
        check = m.load("vendor/pr3021/verify.py", "retained_controls")
        old = m.read(m.MAIN / "data/WORD-base.json.gz")
        new = m.read(m.PACKAGE / "vendor/pr3015/edits/FINAL-WORD-base.json.gz")
        edits = m.read(m.PACKAGE / "vendor/pr3015/edits/EDITS.json")["edits"]["base"]
        self.assertEqual(check.check_word(old, new, edits)["private_buffers"], 91)
        bad = copy.deepcopy(edits)
        bad[0]["new"][0][3] += 1
        with self.assertRaisesRegex(ValueError, "R1 scalar identity"):
            check.check_word(old, new, bad)
        new["cleanup"].pop()
        with self.assertRaisesRegex(ValueError, "inverse cleanup"):
            check.check_word(old, new, edits)

    def test_lifted_order_and_dispatch_reach_the_owner_checker(self):
        rows, order, dispatch, providers = m.witness()
        wrong_order = copy.deepcopy(order)
        second = wrong_order.index([1, 0])
        wrong_order[0], wrong_order[second] = wrong_order[second], wrong_order[0]
        with self.assertRaisesRegex(ValueError, "order chronology"):
            verify.owners(rows, wrong_order, dispatch, providers)
        wrong_dispatch = dict(dispatch)
        del wrong_dispatch[0, 0]
        with self.assertRaisesRegex(ValueError, "provider dispatch coverage"):
            verify.owners(rows, order, wrong_dispatch, providers)

    def test_literal_materialized_capacity_fault_rejects(self):
        rows, order, dispatch, providers = m.witness()

        class FaultyRows:
            def __len__(self):
                return len(rows)

            def __iter__(self):
                for index, row in enumerate(rows):
                    if index == 0:
                        row = [*row[:5], 1000]
                    yield row

        with self.assertRaisesRegex(ValueError, "bin capacity"):
            verify.owners(FaultyRows(), order, dispatch, providers)


if __name__ == "__main__":
    unittest.main()
