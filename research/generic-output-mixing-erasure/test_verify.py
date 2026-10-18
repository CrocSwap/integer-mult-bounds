#!/usr/bin/env python3
"""Behavioral controls for complete dirt coverage and immutable evidence."""
import copy
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
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("mix_verify", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class ErasureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="output-mixing-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.pkg = self.root / "research/generic-output-mixing-erasure"
        shutil.copytree(HERE, self.pkg, ignore=shutil.ignore_patterns("__pycache__"))
        for pin in json.loads((HERE / "SOURCES.json").read_text())["files"]:
            if pin["usage"] == "input":
                target = self.root / pin["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / pin["path"], target)

    def command(self, *args, optimized=False):
        return subprocess.run([sys.executable, "-I", "-B"] + (["-O"] if optimized else [])
                              + [str(self.pkg / "verify.py"), *map(str, args)],
                              cwd=self.root, capture_output=True, text=True)

    def expect_rejection(self, result, phrase):
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(phrase, result.stderr)

    def hashes(self):
        return {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.root.rglob("*") if p.is_file()}

    def test_relocated_read_only_normal_and_optimized(self):
        before = self.hashes()
        for optimized in (False, True):
            result = self.command(optimized=optimized)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS_GENERIC_OUTPUT_MIXING_ERASURE", result.stdout)
        self.assertEqual(before, self.hashes())

    def test_missing_evidence_and_explicit_no_overwrite_generation(self):
        expected = self.pkg / "EXPECTED.json"
        original = expected.read_bytes()
        expected.unlink()
        self.expect_rejection(self.command(), "FileNotFoundError")
        self.assertFalse(expected.exists())
        result = self.command("--write-expected", expected)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(expected.read_bytes(), original)
        self.expect_rejection(self.command("--write-expected", expected), "FileExistsError")
        self.assertEqual(expected.read_bytes(), original)
        (self.pkg / "CERTIFICATE.json").unlink()
        self.expect_rejection(self.command(), "FileNotFoundError")

    def test_typed_and_balanced_receipt_corruption(self):
        path = self.pkg / "EXPECTED.json"
        original = json.loads(path.read_text())
        mutants = []
        x = copy.deepcopy(original)
        x["schema_version"] = True  # Python equality would confuse this with 1.
        mutants.append(x)
        x = copy.deepcopy(original)
        x["fixtures"][0]["map_calls"] += 1
        x["fixtures"][1]["map_calls"] -= 1
        mutants.append(x)
        x = copy.deepcopy(original)
        x["coverage_histogram"]["31"] -= 1
        x["coverage_histogram"]["28"] += 1
        mutants.append(x)
        for x in mutants:
            path.write_text(json.dumps(x))
            self.expect_rejection(self.command(), "expected receipt mismatch")

    def test_fixture_coverage_and_declared_erasure(self):
        path = self.pkg / "CERTIFICATE.json"
        original = json.loads(path.read_text())
        x = copy.deepcopy(original)
        x["fixtures"].pop()
        path.write_text(json.dumps(x))
        self.expect_rejection(self.command(), "fixture coverage")
        x = copy.deepcopy(original)
        x["fixtures"][1] = x["fixtures"][0]
        path.write_text(json.dumps(x))
        self.expect_rejection(self.command(), "fixture identities")
        x = copy.deepcopy(original)
        x["fixtures"][1]["expected_erased"].pop()
        path.write_text(json.dumps(x))
        self.expect_rejection(self.command(), "erasure receipt")

    def test_source_drift(self):
        path = self.root / "research/universal-connector-boundary/CERTIFICATE.json"
        path.write_bytes(path.read_bytes() + b"\n")
        self.expect_rejection(self.command(), "source drift")

    def test_real_detector_removal_is_detected(self):
        path = self.pkg / "verify.py"
        source = path.read_text()
        mutations = [
            ("require(coefficients[row][reader] == expected,", "require(True,",
             "control unexpectedly accepted: reader coefficient"),
            ('require(inv == [1 << i for i in range(r)], "output dirt frame")',
             'require(True, "output dirt frame")', "control unexpectedly accepted: output dirt frame"),
        ]
        for before, after, message in mutations:
            self.assertEqual(source.count(before), 1)
            path.write_text(source.replace(before, after))
            self.expect_rejection(self.command(), message)

    def test_empty_and_inactive_domains(self):
        for f in [dict(source_count=0, logical_outputs=0, bank_size=0, masks=[], word=[]),
                  dict(source_count=0, logical_outputs=1, bank_size=2, masks=[0],
                       word=[["A", 0, 1], ["A", 0, 1]])]:
            erased = v.check(f)
            v.check(dict(f, word=erased))


if __name__ == "__main__":
    unittest.main()
