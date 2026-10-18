#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Cinna Davis (@1337isnot1337), with substantial OpenAI Codex assistance.
"""Mathematical fixtures, failure controls and portable package replay.

The short-word family is an implementation regression domain, not a proof
of the arbitrary-length theorem in PROOF.md.
"""
import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("cleanup_floor_verifier", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class PackageTests(unittest.TestCase):
    def run_verifier(self, package, *args):
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py"), *args],
                              cwd=package.parent, text=True, capture_output=True, timeout=30)

    def copy_package(self, temporary):
        destination = Path(temporary) / "portable package with spaces"
        shutil.copytree(HERE, destination, ignore=shutil.ignore_patterns("__pycache__"))
        return destination

    def test_all_three_register_words_through_length_five(self):
        gates = tuple((d, s) for d in range(3) for s in range(3) if d != s)
        cases = 0
        for length in range(6):
            for operations in itertools.product(gates, repeat=length):
                target = v.column_replay(3, operations)
                signed_inverse = v.column_replay(3, tuple(reversed(operations)), -1)
                cleanup = v.product(3, tuple(reversed(operations)))
                self.assertEqual(v.multiply(target, signed_inverse), v.identity(3))
                self.assertTrue(v.admissible_bound(signed_inverse, cleanup))
                floor = v.floor_from_inverse(signed_inverse)
                self.assertTrue(all(cleanup[i][j] >= floor[i][j] for i in range(3) for j in range(3)))
                cases += 1
        self.assertEqual(cases, 9331)

    def test_same_target_nineteen_gate_fixture(self):
        _, source, _ = v.load_inputs()
        old = v.word(source["old_operations"], 6)
        current = v.word(source["operations"], 6)
        self.assertEqual(len(old), 19)
        self.assertEqual(v.column_replay(6, old), v.product(6, current))
        reverse = v.column_replay(6, tuple(reversed(old)))
        self.assertEqual(v.norm_inf(reverse), 46)
        self.assertTrue(v.admissible_bound(v.inverse(v.product(6, current)), reverse))

    def test_permutation_scope_control(self):
        swap = ((0, 1), (1, 0))
        self.assertEqual(v.norm_inf(swap), 1)
        self.assertEqual(v.norm_inf(v.floor_from_inverse(swap)), 3)
        self.assertFalse(v.admissible_bound(swap, swap))

    def test_invalid_gate_alphabet(self):
        for operations in (((0, 0),), ((0, 2),), (("SWAP", 0, 1),), ((0, True),)):
            with self.subTest(operations=operations), self.assertRaises(ValueError):
                v.word(operations, 2)

    def test_relocated_optimized_replay(self):
        with tempfile.TemporaryDirectory() as temporary:
            package = self.copy_package(temporary)
            result = self.run_verifier(package)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("lower=9 attained=9 adds=11", result.stdout)

    def test_archive_corruptions_fail(self):
        for name in ("PR1058-CIRCUIT.json", "PR1266-RESULT.json"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                package = self.copy_package(temporary)
                source = package / "inputs" / name
                source.write_bytes(source.read_bytes() + b" ")
                result = self.run_verifier(package)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("source pin mismatch", result.stderr)

    def test_false_lower_bound_receipt_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            package = self.copy_package(temporary)
            receipt = package / "CERTIFICATE.json"
            data = json.loads(receipt.read_text())
            data["all_length_lower_bound"] = 8
            receipt.write_text(json.dumps(data))
            result = self.run_verifier(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("committed certificate differs", result.stderr)

    def test_receipt_writer_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            package = self.copy_package(temporary)
            destination = Path(temporary) / "new-receipt.json"
            first = self.run_verifier(package, "--write-receipt", str(destination))
            self.assertEqual(first.returncode, 0, first.stderr)
            before = destination.read_bytes()
            second = self.run_verifier(package, "--write-receipt", str(destination))
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(before, destination.read_bytes())


if __name__ == "__main__":
    unittest.main()
