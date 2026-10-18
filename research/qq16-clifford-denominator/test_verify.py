#!/usr/bin/env python3
"""Behavior and rejection controls for the standalone checker. Apache-2.0."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


class EntrypointTests(unittest.TestCase):
    def run_checker(self, package, *args, optimized=False):
        flags = ["-Werror", "-I", "-B"] + (["-O"] if optimized else [])
        return subprocess.run(
            [sys.executable, *flags, str(package / "verify.py"), *args],
            capture_output=True, text=True, timeout=30, check=False,
        )

    def export(self, root):
        target = root / "research/qq16-clifford-denominator"
        shutil.copytree(PACKAGE, target, ignore=shutil.ignore_patterns("__pycache__"))
        sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
        self.assertLessEqual(len(sources["files"]), 16)
        for entry in sources["files"]:
            if entry["usage"] == "input":
                path = root / entry["path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / entry["path"], path)
        return target

    def test_normal_and_optimized_cli(self):
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                run = self.run_checker(PACKAGE, optimized=optimized)
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertEqual(run.stdout.strip(),
                                 "PASS_QQ16_CLIFFORD_DENOMINATOR observations=224 "
                                 "tensor_columns=14 primes=3,5 controls=6")

    def test_emitted_observation_and_ring_receipt(self):
        run = self.run_checker(PACKAGE, "--emit", optimized=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(result["two_cut_witness"]["required_residue"], [1, 0, 0, 0])
        self.assertEqual(result["two_cut_witness"]["y2_A"],
                         ["5/2", "-5/2", "0", "5/2", "0", "0", "-5/2", "0"])
        self.assertEqual(result["product_reduction_comparisons"], 578)
        self.assertEqual(result["minors"]["alternative"]["inverse"][0][1], "1/10")

    def test_git_free_read_only_export(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = self.export(root)
            before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            run = self.run_checker(package, optimized=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            after = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            self.assertEqual(after, before)
            self.assertFalse((root / ".git").exists())

    def test_source_corruption_rejects_before_packet_parse(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = self.export(root)
            packet = root / "research/joint-query/certificate.json.gz"
            packet.write_bytes(b"broken input")
            run = self.run_checker(package, optimized=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("source pin differs", run.stderr)

    def test_receipt_corruption_and_missing_receipt_reject(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self.export(Path(directory))
            path = package / "RESULT.json"
            receipt = json.loads(path.read_text(encoding="utf-8"))
            receipt["two_cut_witness"]["observation_residues_zero"] = 1
            path.write_text(json.dumps(receipt), encoding="utf-8")
            run = self.run_checker(package, optimized=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("receipt differs", run.stderr)
            path.unlink()
            run = self.run_checker(package, optimized=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("FileNotFoundError", run.stderr)

    def test_mathematical_defects_reject_under_optimization(self):
        defects = [
            ("require(dyadic(value),", "require(True,", "odd-denominator gate accepted"),
            ("else h\n", "else scalar(1)\n", "H basis column differs"),
            ("Z = (1, 2, 1,", "Z = (2, 2, 1,", "integer witness image differs"),
            ("(-1 if degree >= 4 else 1)", "1", "i squared differs"),
            ("return tuple(int(x.numerator * pow(x.denominator, -1, p) % p) for x in a)",
             "return (0, 0, 0, 0)", "quotient collapses 1 to 0"),
        ]
        for old, new, error in defects:
            with self.subTest(defect=error), tempfile.TemporaryDirectory() as directory:
                package = self.export(Path(directory))
                path = package / "verify.py"
                code = path.read_text(encoding="utf-8")
                self.assertEqual(code.count(old), 1)
                path.write_text(code.replace(old, new), encoding="utf-8")
                run = self.run_checker(package, optimized=True)
                self.assertNotEqual(run.returncode, 0)
                self.assertIn(error, run.stderr)


if __name__ == "__main__":
    unittest.main()
