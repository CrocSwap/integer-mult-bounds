#!/usr/bin/env python3
"""Package and admission failure tests. Hanson Sun / OpenAI Codex; Apache-2.0."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
spec = importlib.util.spec_from_file_location("shared_source_verifier", PACKAGE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="shared dyadic source ")
        cls.export = Path(cls.temporary.name) / "export without git"
        cls.copy = cls.export / "research" / PACKAGE.name
        shutil.copytree(PACKAGE, cls.copy, ignore=shutil.ignore_patterns("__pycache__"))
        for entry in json.loads((PACKAGE / "SOURCES.json").read_text())["files"]:
            if entry["usage"] == "input":
                target = cls.export / entry["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / entry["path"], target)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def command(self, script, *arguments):
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(script), *map(str, arguments)],
                              cwd=self.export, text=True, capture_output=True, timeout=180)

    def test_relocated_source_export(self):
        result = self.command(self.copy / "verify.py", "--pins-only")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PINS_ONLY", result.stdout)

    def test_source_corruption_rejected(self):
        target = self.export / "research/dyadic-query-runs/PROOF.md"
        original = target.read_bytes()
        try:
            target.write_bytes(original + b"\ncorrupted source\n")
            result = self.command(self.copy / "verify.py", "--pins-only")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source drift", result.stderr)
        finally:
            target.write_bytes(original)

    def test_certificate_corruption_rejected(self):
        target = self.copy / "CERTIFICATE.json"
        original = target.read_bytes()
        corruptions = []
        cert = json.loads(original)
        bad = deepcopy(cert)
        bad["shared"].pop()
        corruptions.append(bad)
        bad = deepcopy(cert)
        bad["invoices"]["shared"]["ordinary_children"] = 12
        corruptions.append(bad)
        bad = deepcopy(cert)
        bad["assignment_seed"] = True
        corruptions.append(bad)
        try:
            for bad in corruptions:
                with self.subTest(corruption=corruptions.index(bad)):
                    target.write_text(json.dumps(bad))
                    result = self.command(self.copy / "verify.py", "--pins-only")
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("certificate differs", result.stderr)
        finally:
            target.write_bytes(original)

    def test_byte_identical_regeneration_and_no_overwrite(self):
        target = self.export / "new certificate.json"
        result = self.command(self.copy / "construct.py", "--output", target)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(target.read_bytes(), (PACKAGE / "CERTIFICATE.json").read_bytes())
        before = target.read_bytes()
        result = self.command(self.copy / "construct.py", "--output", target)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(target.read_bytes(), before)

    def test_paid_child_and_coefficients(self):
        cert = json.loads((PACKAGE / "CERTIFICATE.json").read_text())
        lowerings = deepcopy(cert["lowerings"])
        lowerings["2"] = [event for event in lowerings["2"] if event[0] != "C"]
        bill = v.o.recount(cert["shared"], lowerings)
        self.assertEqual(bill["ordinary_children"], 10)
        self.assertNotEqual(bill, cert["invoices"]["shared"])
        late_control = [["A", 2, [[2, "1"], [5, "1"]]]]
        with self.assertRaisesRegex(ValueError, "affine control"):
            v.o.parse_native(late_control)
        with self.assertRaisesRegex(ValueError, "unit"):
            v.o.parse_native([["A", 2, [[2, "3"], [0, "1"]]]])

    def test_lower_bound_permission_is_explicit(self):
        cert = json.loads((PACKAGE / "CERTIFICATE.json").read_text())
        # The correct target-only baseline is still outside the source-only
        # alphabet of our minimum theorem, even though its endpoint is right.
        self.assertEqual(v.o.laurent(cert["separate"], 7), v.o.wanted_laurent(cert["masks"]))
        with self.assertRaisesRegex(ValueError, "forbidden role"):
            v.o.validate_word(cert["separate"], 5, True)
        with self.assertRaisesRegex(ValueError, "distinct source"):
            v.o.validate_word([["X", 0, 0]], 5, True)

    def test_aggregate_does_not_certify_individual_outputs(self):
        cert = json.loads((PACKAGE / "CERTIFICATE.json").read_text())
        collapsed = [[op, 1 if op == "X" else row, argument] for op, row, argument in cert["shared"]]
        actual = v.o.laurent(collapsed, 7)
        expected = v.o.wanted_laurent(cert["masks"])
        a, b = set(), set()
        for row in range(1, 6):
            a ^= actual[row]
            b ^= expected[row]
        self.assertEqual(a, b)
        self.assertNotEqual(actual, expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
