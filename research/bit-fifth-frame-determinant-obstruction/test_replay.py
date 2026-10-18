"""Exercise the published CLI, including real corrupted inputs and code."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


class ReplayTests(unittest.TestCase):
    def invoke(self, script, *arguments, optimized=False):
        command = [sys.executable, "-I", "-B"]
        if optimized:
            command.append("-O")
        command.extend([str(script), *map(str, arguments)])
        return subprocess.run(command, capture_output=True, text=True, timeout=30,
                              check=False)

    def assert_receipt(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["status"], "PASS_FIFTH_FRAME_DETERMINANT_OBSTRUCTION")
        self.assertEqual(receipt["minimum_calls"], 8)
        self.assertEqual(receipt["R_calls_in_any_exact_word"], 0)
        self.assertEqual(receipt["enumerated_multisets"], 1287)
        self.assertEqual(receipt["formal_positive_fixtures"], 6)
        self.assertEqual(receipt["formal_R_mutation_controls"], 48)
        self.assertEqual(receipt["determinant_profiles"],
                         [[0, 0, 4, 4, 0], [1, 1, 3, 3, 0], [2, 2, 2, 2, 0],
                          [3, 3, 1, 1, 0], [4, 4, 0, 0, 0]])

    def test_normal_cli(self):
        self.assert_receipt(self.invoke(HERE / "verify.py"))

    def test_optimized_relocated_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("verify.py", "RESULT.json"):
                shutil.copyfile(HERE / name, root / name)
            self.assert_receipt(self.invoke(root / "verify.py", optimized=True))

    def test_altered_receipts(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            changes = (("minimum_calls", 7), ("R_calls_in_any_exact_word", False))
            for field, value in changes:
                receipt = json.loads((HERE / "RESULT.json").read_text())
                receipt[field] = value
                path.write_text(json.dumps(receipt))
                result = self.invoke(HERE / "verify.py", "--receipt", path,
                                     optimized=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("receipt mismatch", result.stderr)

    def test_invalid_receipt_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text("{")
            result = self.invoke(HERE / "verify.py", "--receipt", path)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("JSONDecodeError", result.stderr)

    def test_receipt_size_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "large.json"
            path.write_text(" " * 65537)
            result = self.invoke(HERE / "verify.py", "--receipt", path)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("receipt exceeds 64 KiB", result.stderr)

    def test_omitted_factor_update_mutant(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutant.py"
            source = (HERE / "verify.py").read_text()
            old = "state = apply_factor(state, projector, LABELS[label])"
            self.assertEqual(source.count(old), 1)
            path.write_text(source.replace(old, "state = state"))
            result = self.invoke(path, "--receipt", HERE / "RESULT.json",
                                 optimized=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("direct word failed", result.stderr)

    def test_wrong_lattice_mutant(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutant.py"
            source = (HERE / "verify.py").read_text()
            old = "(3, 3, -4)"
            self.assertEqual(source.count(old), 1)
            path.write_text(source.replace(old, "(3, 3, -3)"))
            result = self.invoke(path, "--receipt", HERE / "RESULT.json",
                                 optimized=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("lattice coordinate mismatch", result.stderr)


if __name__ == "__main__":
    unittest.main()
