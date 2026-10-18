"""Behavioral and defect-sensitive controls for the invariant interface.

Ross Richardson with OpenAI Codex assistance. Apache-2.0.
"""

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("common_verify", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def run(path, *args):
    return subprocess.run([sys.executable, "-I", "-O", "-Werror", "-B",
                           str(path / "verify.py"), *args],
                          capture_output=True, text=True, timeout=90)


class Behavior(unittest.TestCase):
    def test_changed_contract_controls(self):
        controls = verify.controls(verify.load_model())
        self.assertEqual(controls["linear_address_phase_counterexamples"], 28)
        self.assertEqual(controls["signed_dirty_macros"], 35)
        self.assertTrue(controls["larger_rank_one_exactness_orbit"])

    def test_missing_reverse_mutant(self):
        m = verify.load_model()
        real = m.construct

        def missing(rank):
            gamma, _, first, _ = real(rank)
            return gamma, gamma, first, [0] * rank

        m.construct = missing
        with self.assertRaisesRegex(ValueError, "intersection membership"):
            m.report(2)

    def test_wrong_inverse_mutant(self):
        m = verify.load_model()
        real = m.lift
        m.lift = lambda x, rank, inverse=False: real(x, rank, inverse=False)
        with self.assertRaisesRegex(ValueError, "inverse"):
            m.report(2)

    def test_bad_rank_and_integer_types(self):
        m = verify.load_model()
        for value in (True, 0, 8, 1.0):
            with self.assertRaises(ValueError):
                m.construct(value)
        with self.assertRaises(ValueError):
            m.lift([True, 0, 0, 0], 1)

    def test_optimized_git_free_relocation_and_no_writes(self):
        with tempfile.TemporaryDirectory(prefix="p104-common-relocation-") as temp:
            target = Path(temp) / "artifact"
            shutil.copytree(HERE, target, ignore=shutil.ignore_patterns("__pycache__"))
            before = {p.relative_to(target).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in target.rglob("*") if p.is_file()}
            result = run(target)
            self.assertEqual(result.returncode, 0, result.stderr)
            after = {p.relative_to(target).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in target.rglob("*") if p.is_file()}
            self.assertEqual(before, after)

    def test_source_before_model_execution(self):
        with tempfile.TemporaryDirectory(prefix="p104-common-source-") as temp:
            target = Path(temp) / "artifact"
            shutil.copytree(HERE, target, ignore=shutil.ignore_patterns("__pycache__"))
            (target / "vendor/lattice.py").write_bytes(b"changed source\n")
            (target / "model.py").write_text("raise RuntimeError('MODEL_EXECUTED')\n")
            result = run(target)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source pin", result.stderr)
            self.assertNotIn("MODEL_EXECUTED", result.stderr)

    def test_receipt_types_and_exclusive_generation(self):
        with tempfile.TemporaryDirectory(prefix="p104-common-receipt-") as temp:
            target = Path(temp) / "artifact"
            shutil.copytree(HERE, target, ignore=shutil.ignore_patterns("__pycache__"))
            receipt = json.loads((target / "RESULT.json").read_text())
            receipt["ranks"][0]["gamma_index_bits"] = True
            (target / "RESULT.json").write_text(json.dumps(receipt))
            result = run(target)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("receipt equality", result.stderr)
            result = run(target, "--write")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("FileExistsError", result.stderr)


if __name__ == "__main__":
    unittest.main()
