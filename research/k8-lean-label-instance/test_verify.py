# SPDX-License-Identifier: Apache-2.0
"""Behavior and adapter-boundary controls, without another matrix replay."""
import copy
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import check_lean
import generate
import translate as t
import verify as v


class TranslationTests(unittest.TestCase):
    def test_label_domains_are_disjoint(self):
        labels = {t.label(7)}
        for tag in t.TAGS:
            for owner in (0, 111, 224, 703):
                labels.add(t.label(7, tag, owner))
        self.assertEqual(len(labels), 17)
        for value in (-1, 1004, True):
            with self.assertRaises(ValueError):
                t.label(value)

    def test_private_copy_overwrites_and_clear_relabels(self):
        start = [9, 45, 88]
        self.assertEqual(t.observe(start, [["copy", 2, 0, 9], ["clear", 2, 7]]), [9, 45, 7])
        with self.assertRaisesRegex(ValueError, "COPY source"):
            t.observe(start, [["copy", 2, 0, 88]])
        with self.assertRaisesRegex(ValueError, "ADD common"):
            t.observe(start, [["add", 0, 1, 1, 1]])

    def test_all_scalar_constructor_fields(self):
        self.assertEqual(t.scalar(["add", ["L", 3], ["C", 7], -6, 4], 9),
                         ["add", 3, 711, -3, 2])
        self.assertEqual(t.scalar(["scale", ["C", 0], 2, -4], 9), ["scale", 704, -1, 2])
        self.assertEqual(t.scalar(["copy", ["C", 0], ["L", 5]], 11), ["copy", 704, 5, 11])
        self.assertEqual(t.scalar(["clear", ["C", 1]], 13), ["clear", 705, 13])
        for operation in (["clear", ["C", 8]], ["scale", ["L", 1], True, 1],
                          ["add", ["L", 1], ["L", 1], 1, 1], ["unknown"]):
            with self.assertRaises(ValueError):
                t.scalar(operation, 0)

    def test_adapters_and_cold_hpe_wrapper(self):
        c = {"start": [0] * 704, "final": [1] * 704}
        c["final"][273] = 124
        self.assertEqual(t.translate_event(c, ["adapter", "old_to_new", 5, 9]),
                         ["relabel", 5, t.label(9, "pre", 5), 9])
        self.assertEqual(t.translate_event(c, ["adapter", "new_to_old", 112, 778]),
                         ["relabel", 112, 778, t.label(778, "post", 112)])
        self.assertEqual(t.translate_event(c, ["residual_adapter", "pre", 273, 0, 124]),
                         ["relabel", 273, t.label(0, "prew", 273), 0])
        self.assertEqual(t.translate_event(c, ["residual_adapter", "post", 273, 0, 124]),
                         ["relabel", 273, 124, t.label(124, "done", 273)])
        with self.assertRaisesRegex(ValueError, "wrapper terminal"):
            t.translate_event(c, ["residual_adapter", "pre", 273, 0, 1])

    def test_exact_lean_coefficients_and_transport(self):
        self.assertEqual(t.lean_event(["add", 1, 2, -3, 4]), ".add 1 2 ((-3 : Rat) / 4)")
        self.assertEqual(t.translate_event({}, ["climb", "A", 3, 9, 11, 1]),
                         ["relabel", 3, 9, 11])
        self.assertEqual(t.translate_event({}, ["center", 2, 9, 11, 1]),
                         ["relabel", 706, 9, 11])
        with self.assertRaises(ValueError):
            t.translate_event({}, ["new_kind", 1])

    def test_typed_receipt_and_duplicate_keys(self):
        self.assertNotEqual(v.encoded({"x": 1}), v.encoded({"x": True}))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            v.unique([("x", 1), ("x", 2)])

    def test_step_preserves_unrelated_labels(self):
        start = [7, 7, 20, 30]
        operations = [["add", 0, 1, 3, 2], ["scale", 1, -1, 1],
                      ["relabel", 2, 20, 4], ["copy", 3, 2, 4]]
        self.assertEqual(t.observe(start, operations), [7, 7, 4, 4])
        self.assertEqual(start, [7, 7, 20, 30])
        wrong = copy.deepcopy(operations)
        wrong[2][2] = 21
        with self.assertRaisesRegex(ValueError, "relabel source"):
            t.observe(start, wrong)

    def test_generated_tree_indexing(self):
        labels = list(range(1024))
        literal = generate.tree(labels)
        leaves = list(map(int, re.findall(r"leaf (\d+)", literal)))
        self.assertEqual(len(leaves), 1024)
        for index in range(1024):
            reversed_bits = int(f"{index:010b}"[::-1], 2)
            self.assertEqual(leaves[reversed_bits], index)

    @unittest.skipUnless(os.name == "posix", "formal driver uses POSIX process groups")
    def test_compiler_driver_success_failure_and_timeout(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env = dict(os.environ)
            result = check_lean.command_result([sys.executable, "-c", "print('ok')"], root, env, 5)
            self.assertEqual((result.returncode, result.stdout), (0, "ok\n"))
            result = check_lean.command_result([sys.executable, "-c", "raise SystemExit(7)"], root, env, 5)
            self.assertEqual(result.returncode, 7)
            with self.assertRaises(subprocess.TimeoutExpired):
                check_lean.command_result([sys.executable, "-c", "import time; time.sleep(3)"], root, env, 0.05)

    def test_proof_snapshot_detects_mid_run_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("TreeCheckpoint.lean", "generate.py", "translate.py"):
                (root / name).write_text("initial bytes")
            before = check_lean.package_snapshot(root)
            (root / "TreeCheckpoint.lean").write_text("uncompiled replacement")
            after = check_lean.package_snapshot(root)
            self.assertNotEqual(before["TreeCheckpoint.lean"], after["TreeCheckpoint.lean"])
            with self.assertRaisesRegex(ValueError, "changed"):
                check_lean.verify_snapshot(before, root)


if __name__ == "__main__":
    unittest.main()
