#!/usr/bin/env python3
"""Exercise allocation behavior, a separate forward access oracle and CLI faults."""

import copy
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("allocation", PACKAGE / "verify.py")
allocation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(allocation)


def cli(directory, *args):
    return subprocess.run([sys.executable, "-Werror", "-I", "-O", "-B",
                           str(directory / "verify.py"), *args],
                          capture_output=True, text=True, timeout=30)


def forward_edges(word, intervals):
    """No gap construction: find each bank's first future touch or delivery."""
    uses = {f"{p}{i}": [] for p in "ZW" for i in range(112)}
    for index, event in enumerate(word):
        if event[0] == "checkpoint":
            for field in uses:
                uses[field].append((index, "checkpoint", False))
        if event[0] in ("clear", "line", "map", "add"):
            fields = event[1:3] if event[0] == "add" else event[1:2]
            for field in fields:
                if field in uses:
                    uses[field].append((index, event[0], event[1] == field))
    edges = []
    for row in intervals:
        for bank, access in uses.items():
            future = next((a for a in access if a[0] >= row["first"]),
                          (len(word), "deliver", False))
            if future[0] > row["last"] and future[1:] == ("clear", True):
                edges.append((row["scope"], row["field"], bank))
    return edges


class AllocationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.word = allocation.read_json(PACKAGE / "WORD.json")
        cls.rows = allocation.lifetimes(cls.word)
        cls.gaps = allocation.output_gaps(cls.word)

    def test_positive_and_independent_access_oracle(self):
        result = allocation.run(PACKAGE)
        self.assertEqual(result["minimum_extra_arrays_fixed_binding"], 16)
        self.assertEqual(result["clique_event"], 2925)
        self.assertEqual(forward_edges(self.word, self.rows), [])
        # The oracle accepts an initial-dirt gap in a small literal example.
        toy = [["clear", "F0", "wide"], ["clear", "F0", "identity"],
               ["clear", "Z0", "wide"], ["add", "Z0", "X0", "1"]]
        row = {"scope": "toy", "field": "F0", "first": 0, "last": 1}
        self.assertEqual(forward_edges(toy, [row]), [("toy", "F0", "Z0")])
        self.assertIsNone(allocation.check_allocation(
            [row], [{"field": "Z0", "after": -1, "before": 2}],
            {("toy", "F0"): "Z0"}, 0))

    def test_allocations_and_cleanup_counterexample(self):
        binding = allocation.baseline(self.rows)
        self.assertIsNone(allocation.check_allocation(self.rows, self.gaps, binding, 16))
        self.assertEqual(allocation.semantic_controls(self.word), 6)
        row = next(r for r in self.rows if r["scope"] == "F0_inverse" and r["field"] == "F4")
        gap = next(g for g in self.gaps if g["field"] == "Z76" and g["before"] == 3765)
        self.assertTrue(allocation.fits(row, gap, cleanup=False))
        self.assertFalse(allocation.fits(row, gap))
        # Literal scalar values demonstrate both corruptions, independent of native semantics.
        w0, f0 = 7, 13
        f0 = 0
        f0 += w0
        self.assertEqual((w0, f0), (7, 7))
        aliased_w0 = 0
        aliased_w0 += aliased_w0
        self.assertNotEqual(aliased_w0, f0)
        z76_after_reconstruction = 11
        alias_after_f4_cleanup = 0
        self.assertNotEqual(alias_after_f4_cleanup, z76_after_reconstruction)

    def test_word_failures(self):
        mutations = [(698, ["add", "F0", "G0", "1"]),
                     (697, ["clear", "X0", "wide"]),
                     (3794, ["add", "F4", "Z76", "1"]),
                     (2853, ["begin", "F0_inverse", True]),
                     (696, ["end", "B1_current_query", 8])]
        for index, event in mutations:
            with self.subTest(index=index):
                word = copy.deepcopy(self.word)
                word[index] = event
                with self.assertRaises(ValueError):
                    allocation.validate(word)
                    allocation.lifetimes(word)
        with self.assertRaisesRegex(ValueError, "event capacity"):
            allocation.validate(self.word[:-1])
        with self.assertRaisesRegex(ValueError, "private slot capacity"):
            allocation.check_allocation(self.rows, self.gaps, allocation.baseline(self.rows), True)

    def test_cli_export_and_exclusive_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "export"
            shutil.copytree(PACKAGE, directory, ignore=shutil.ignore_patterns("__pycache__"))
            before = {p.name: p.read_bytes() for p in directory.iterdir() if p.is_file()}
            run = cli(directory)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn("alias_edges=0 minimum_extra=16", run.stdout)
            after = {p.name: p.read_bytes() for p in directory.iterdir() if p.is_file()}
            self.assertEqual(before, after)
            run = cli(directory, "--write")
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("FileExistsError", run.stderr)
            (directory / "RESULT.json").unlink()
            run = cli(directory, "--write")
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual((directory / "RESULT.json").read_bytes(), before["RESULT.json"])

    def test_cli_source_and_typed_receipt_faults(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "export"
            shutil.copytree(PACKAGE, directory, ignore=shutil.ignore_patterns("__pycache__"))
            word_path = directory / "WORD.json"
            word_path.write_bytes(word_path.read_bytes() + b" ")
            run = cli(directory)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("source word drift", run.stderr)
            shutil.copyfile(PACKAGE / "WORD.json", word_path)
            receipt = directory / "RESULT.json"
            baseline = receipt.read_bytes()
            for kind in ("boolean", "changed", "duplicate", "missing", "oversized"):
                with self.subTest(kind=kind):
                    value = json.loads(baseline)
                    if kind in ("boolean", "changed"):
                        value["minimum_extra_arrays_fixed_binding"] = True if kind == "boolean" else 15
                        receipt.write_text(json.dumps(value))
                    elif kind == "duplicate":
                        receipt.write_text('{"schema_version":1,"schema_version":1}')
                    elif kind == "missing":
                        receipt.unlink()
                    else:
                        receipt.write_bytes(b" " * (allocation.MAX_BYTES + 1))
                    run = cli(directory)
                    self.assertNotEqual(run.returncode, 0)
                    receipt.write_bytes(baseline)


if __name__ == "__main__":
    unittest.main()
