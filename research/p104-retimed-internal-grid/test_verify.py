"""CLI, fixed-grid arithmetic, source corruption and independent-oracle checks."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import independent
import kernel
import verify

HERE = Path(__file__).resolve().parent


class RetimedGridTests(unittest.TestCase):
    def run_cli(self, package, *args, optimized=False):
        command = [sys.executable, "-I", "-B"]
        if optimized:
            command.append("-O")
        command += [str(package / "verify.py"), *map(str, args)]
        return subprocess.run(command, capture_output=True, text=True, timeout=120)

    def test_literal_c_and_inverse(self):
        vector = ((2, 0),) + kernel.ZERO[1:]
        forward = kernel.c_stage(vector, 0)
        self.assertEqual(forward[:2], ((1, 1), (1, -1)))
        self.assertEqual(kernel.c_stage(forward, 0, -1), vector)
        with self.assertRaisesRegex(ValueError, "inexact internal halving"):
            kernel.c_stage(((1, 0),) + kernel.ZERO[1:], 0)

    def test_independent_all_scalar_prefixes(self):
        word, _ = verify.sources()
        self.assertEqual(
            independent.dense(word),
            {"products": 30007, "zero_erasures": 8, "scaled_l1_peak": 254},
        )

    def test_git_free_optimized_receipt_and_no_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "export"
            shutil.copytree(HERE, target, ignore=shutil.ignore_patterns("__pycache__"))
            before = {
                p.relative_to(target): p.read_bytes()
                for p in target.rglob("*")
                if p.is_file()
            }
            for path in target.rglob("*"):
                if path.is_file():
                    path.chmod(0o444)
            result = self.run_cli(target, optimized=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS_P104_RETIMED_INTERNAL_GRID", result.stdout)
            after = {
                p.relative_to(target): p.read_bytes()
                for p in target.rglob("*")
                if p.is_file()
            }
            self.assertEqual(before, after)
            receipt = target / "RESULT.json"
            receipt.chmod(0o644)
            changed = json.loads(receipt.read_text())
            changed["binding"]["occurrences"] = 1940.0
            receipt.write_text(json.dumps(changed))
            failed = self.run_cli(target, optimized=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("complete typed receipt", failed.stderr)

    def test_source_corruption_and_overwrite_refusal(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "export"
            shutil.copytree(HERE, target, ignore=shutil.ignore_patterns("__pycache__"))
            source = target / "inputs/PR2725-WORD.json"
            source.write_bytes(source.read_bytes() + b"\n")
            failed = self.run_cli(target, "--sources-only", optimized=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("source SHA256", failed.stderr)
            existing = Path(directory) / "existing.json"
            existing.write_text("preserve")
            refused = self.run_cli(target, "--out", existing)
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("exclusive output", refused.stderr)
            self.assertEqual(existing.read_text(), "preserve")

    def test_typed_receipt_and_depth_witness(self):
        value = verify.read(HERE / "RESULT.json")
        changed = json.loads(json.dumps(value))
        changed["binding"]["occurrences"] = 1940.0
        self.assertNotEqual(verify.encoded(changed), verify.encoded(value))
        self.assertEqual(verify.witness_depths()[:6], [7, 11, 16, 20, 25, 29])


if __name__ == "__main__":
    unittest.main()
