#!/usr/bin/env python3
"""Behavioral and public-CLI controls, including optimized execution."""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("guard_stock_verify", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class ArithmeticTests(unittest.TestCase):
    def test_zero_depth(self):
        self.assertEqual(verify.reserve(6, 5, 0), 1)
        self.assertTrue(verify.guard_chain(7, 6, 5, 0))

    def test_minimum_and_multiples(self):
        for packet, compatibility in ((2, 3), (6, 6), (8, 4), (1, 9)):
            for levels in range(1, 6):
                stock = verify.reserve(packet, compatibility, levels)
                self.assertTrue(verify.guard_chain(stock, packet, compatibility, levels))
                self.assertTrue(verify.guard_chain(3 * stock, packet, compatibility, levels))
                if stock > 1:
                    self.assertFalse(verify.guard_chain(stock - 1, packet, compatibility, levels))

    def test_omitted_terminal_guard(self):
        self.assertFalse(verify.guard_chain(6**3, 6, 6, 3))
        self.assertTrue(verify.guard_chain(6**4, 6, 6, 3))

    def test_local_acceptance_does_not_supply_two_levels(self):
        stock = verify.reserve(28416, 9475, 1)
        self.assertTrue(verify.guard_chain(stock, 28416, 9475, 1))
        self.assertFalse(verify.guard_chain(stock, 28416, 9475, 2))

    def test_old_two_format_obligation_is_retained(self):
        for levels in range(2, 8):
            changed = verify.reserve(28416, 9475, levels)
            self.assertNotEqual(changed % 28425**levels, 0)
            self.assertEqual((269241600**levels) // changed, 9475**(levels - 1))

    def test_depth_and_domain(self):
        self.assertEqual([verify.depth(n) for n in (0, 63, 64, 127, 128)], [0, 0, 1, 1, 2])
        for width in (-1, True, 2**256):
            with self.assertRaises(ValueError):
                verify.depth(width)
        for args in ((0, 5, 1), (3, 0, 1), (3, 5, -1), (3, 5, 65)):
            with self.assertRaises(ValueError):
                verify.reserve(*args)


class PublicCliTests(unittest.TestCase):
    def fixture(self, directory):
        root = Path(directory)
        package = root / "research/selected-runtime-guard-stock"
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
        for row in json.loads((HERE / "SOURCES.json").read_bytes())["files"]:
            if row["usage"] == "input":
                target = root / row["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(verify.ROOT / row["path"], target)
        return root, package

    def run_cli(self, package, *args):
        command = [sys.executable, "-Werror", "-I", "-O", "-B", str(package / "verify.py"), *args]
        return subprocess.run(command, capture_output=True, text=True, timeout=60, check=False)

    def test_optimized_positive(self):
        result = self.run_cli(HERE)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS_RUNTIME_GUARD_STOCK", result.stdout)

    def test_missing_and_corrupt_receipt(self):
        with tempfile.TemporaryDirectory(prefix="guard-stock-test-") as directory:
            _root, package = self.fixture(directory)
            receipt = package / "RESULT.json"
            receipt.unlink()
            result = self.run_cli(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(receipt.exists())
            receipt.write_text('{}\n')
            result = self.run_cli(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("required stored receipt mismatch", result.stderr)
            typed_mutant = json.loads((HERE / "RESULT.json").read_bytes())
            typed_mutant["literal_probes"][0]["atom_width"] = True
            receipt.write_text(json.dumps(typed_mutant))
            result = self.run_cli(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("required stored receipt mismatch", result.stderr)

    def test_changed_executable_source(self):
        with tempfile.TemporaryDirectory(prefix="guard-stock-test-") as directory:
            root, package = self.fixture(directory)
            source = root / verify.PREFIX / "fresh_rows.py"
            source.write_text(source.read_text().replace(
                'need(unused.divide_small(families)==0', 'need(True or unused.divide_small(families)==0'))
            result = self.run_cli(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source mismatch", result.stderr)
            self.assertNotIn("PASS_RUNTIME_GUARD_STOCK", result.stdout)

    def test_changed_manifest(self):
        with tempfile.TemporaryDirectory(prefix="guard-stock-test-") as directory:
            _root, package = self.fixture(directory)
            source = package / "SOURCES.json"
            source.write_text(source.read_text() + "\n")
            result = self.run_cli(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source manifest changed", result.stderr)

    def test_explicit_emission_never_overwrites(self):
        with tempfile.TemporaryDirectory(prefix="guard-stock-test-") as directory:
            target = Path(directory) / "receipt.json"
            result = self.run_cli(HERE, "--emit-to", str(target))
            self.assertEqual(result.returncode, 0, result.stderr)
            before = target.read_bytes()
            result = self.run_cli(HERE, "--emit-to", str(target))
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(target.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
