#!/usr/bin/env python3
"""Public-CLI, literal endpoint and contract-failure controls."""
from __future__ import annotations

import copy
import json
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
V = runpy.run_path(str(PACKAGE / "verify.py"))


class CompositionTests(unittest.TestCase):
    def test_literal_borrowing_word(self) -> None:
        # A nontrivial C reverses the two body coordinates. The full endpoint
        # must nevertheless swap only the whole original chunks.
        word = V["wrapper_word"](1, 3)
        actual = V["evaluate"](word, 3, 3)
        self.assertEqual(actual, [
            [0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1]])

    def test_cancelled_row_fault_is_invisible_at_whole_endpoint(self) -> None:
        word = V["wrapper_word"](2, 4, "cancelled_row")
        endpoint = V["evaluate"](word, 4, 3, False)
        self.assertEqual(endpoint, V["expected_swap"](4))
        self.assertEqual(V["cancelled_row_trace"](word, 4, 3), [2, 1])
        with self.assertRaisesRegex(V["Rejected"], "child spectator/row return"):
            V["evaluate"](word, 4, 3)

    def test_missing_final_high_exchange(self) -> None:
        word = V["wrapper_word"](2, 4, "omit_high")
        self.assertNotEqual(V["evaluate"](word, 4, 3), V["expected_swap"](4))

    def test_nested_stage_fixture_and_capacities(self) -> None:
        word = V["wrapper_word"](7, 9)
        self.assertEqual(len(word), 2162)
        self.assertEqual(V["evaluate"](word, 9, 5), V["expected_swap"](9))
        for level, width in ((8, 9), (7, 10), (True, 3), (0, 0)):
            with self.assertRaises(V["Rejected"]):
                V["wrapper_word"](level, width)

    def test_all_fourteen_guards_with_inherited_not_measured_coefficient(self) -> None:
        assembly, _ = V["authenticated_inputs"]()
        records = V["stage_records"](assembly, 6748)
        self.assertEqual(len(records), 14)
        self.assertEqual(records[0], dict(branch="native", stage=1, previous_stage=0,
                                         cutoff_log2="4785575287428", sigma=6748,
                                         ell=16, external_leaf_factor_hypothesis=1))
        self.assertEqual(records[7]["cutoff_log2"], "4785575320504")
        self.assertTrue(all(r["external_leaf_factor_hypothesis"] == 1 for r in records))

    def test_source_stage_mutations(self) -> None:
        assembly, _ = V["authenticated_inputs"]()
        for field in ("exponent", "gap", "cutoff_log2"):
            bad = copy.deepcopy(assembly)
            bad["bootstrap"][1][field] = "1"
            with self.assertRaises(V["Rejected"]):
                V["stage_records"](bad, 6748)
        for sigma in (0, 8195, True):
            with self.assertRaises(V["Rejected"]):
                V["stage_records"](assembly, sigma)

    def test_source_hash_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input"
            path.write_bytes(b"source")
            with self.assertRaisesRegex(V["Rejected"], "source pin"):
                V["source_bytes"](path, "0" * 64)

    def test_public_cli_integrity_under_optimization(self) -> None:
        # One isolated copy. Every mutated file is restored before the next
        # control, and the actual public CLI is used rather than a mock.
        manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "research" / PACKAGE.name
            shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__"))
            for entry in manifest["files"]:
                if entry["usage"] == "input":
                    target = root / entry["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(ROOT / entry["path"], target)
            command = [sys.executable, "-I", "-O", "-Werror", "-B", str(package / "verify.py")]
            passed = subprocess.run(command, capture_output=True, text=True, timeout=30)
            self.assertEqual(passed.returncode, 0, passed.stderr)
            paths = [root / entry["path"] for entry in manifest["files"] if entry["usage"] == "input"]
            paths += [package / entry["path"] for entry in manifest["pending_sources"]]
            paths += [package / "RESULT.json"]
            for path in paths:
                original = path.read_bytes()
                path.write_bytes(original + b" ")
                if path.name == "RESULT.json":
                    changed = json.loads(original)
                    changed["actual_packet_implementation_checked"] = True
                    path.write_text(json.dumps(changed))
                failed = subprocess.run(command, capture_output=True, text=True, timeout=30)
                self.assertNotEqual(failed.returncode, 0, str(path))
                self.assertIn("FAIL_SELECTED_RESERVE_COMPOSITION", failed.stderr)
                path.write_bytes(original)
            source_manifest = package / "SOURCES.json"
            original_manifest = source_manifest.read_bytes()
            changed_manifest = json.loads(original_manifest)
            changed_manifest["archive_members"][0]["sha256"] = "0" * 64
            source_manifest.write_text(json.dumps(changed_manifest))
            failed = subprocess.run(command, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("member pin", failed.stderr)
            source_manifest.write_bytes(original_manifest)
            receipt = package / "RESULT.json"
            receipt.unlink()
            failed = subprocess.run(command, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(failed.returncode, 0)
            self.assertFalse(receipt.exists())


if __name__ == "__main__":
    unittest.main()
