"""Boundary, corruption and portable reproduction tests; standard library only.

Prepared for Philipp (@mightyOil) with substantial OpenAI Codex assistance.
Apache-2.0. Run with Python 3.11+ from any working directory.
"""
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import crosscheck
import verify


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="jp8 grid test ")
        self.root = Path(self.temp.name) / "minimal checkout with spaces"
        self.package = self.root / "research/jp8-grid-bounded-synthesis"
        shutil.copytree(HERE, self.package, ignore=shutil.ignore_patterns("__pycache__"))
        for name in verify.read(HERE / "SOURCES.json")["files"]:
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dest)

    def tearDown(self):
        self.temp.cleanup()

    def invoke(self, *args):
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(self.package / "verify.py"), *args],
                              cwd=self.temp.name, text=True, capture_output=True, timeout=90)

    def rejection(self, reason, *args):
        result = self.invoke(*args)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(reason, result.stderr)

    def edit_certificate(self, edit):
        path = self.package / "CERTIFICATE.json"
        data = json.loads(path.read_text())
        edit(data)
        path.write_text(json.dumps(data))

    def test_optimized_relocated_recompressed_replay(self):
        path = self.root / verify.PROVIDER.relative_to(ROOT) / "LOCAL-PROGRAMS.json.gz"
        before = path.read_bytes()
        path.write_bytes(gzip.compress(gzip.decompress(before), compresslevel=1, mtime=33))
        self.assertNotEqual(path.read_bytes(), before)
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS_JP8_GRID_BOUNDED_SYNTHESIS", result.stdout)

    def test_source_corruption(self):
        path = self.root / "research/complex-k492-owner-repair/data/SPEC.json"
        path.write_bytes(path.read_bytes() + b" ")
        self.rejection("source pin mismatch")

    def test_reference_corruption(self):
        path = self.package / "vendor/pr837/lower.py"
        path.write_bytes(path.read_bytes() + b"\n# changed\n")
        self.rejection("source pin mismatch")

    def test_missing_source_pin(self):
        path = self.package / "SOURCES.json"
        data = json.loads(path.read_text())
        del data["vendored"]["vendor/pr837/lower.py"]
        path.write_text(json.dumps(data))
        self.rejection("source manifest coverage")

    def test_forged_source_provenance(self):
        path = self.package / "SOURCES.json"
        data = json.loads(path.read_text())
        data["source_heads"]["837"] = "0"*40
        data["base_commit"] = "1"*40
        data["historical_provider"] = "a different provider"
        path.write_text(json.dumps(data))
        self.rejection("source provenance identity")

    def test_boolean_coefficient_denominator(self):
        def change(certificate):
            next(e for e in certificate["entries"] if e["denominator"] == 1)["denominator"] = True
        self.edit_certificate(change)
        self.rejection("certificate reconstruction mismatch")

    def test_float_preparation_count(self):
        def change(certificate):
            entry = certificate["entries"][0]
            entry["preparation_steps"] = float(entry["preparation_steps"])
        self.edit_certificate(change)
        self.rejection("certificate reconstruction mismatch")

    def test_altered_search_domain_type(self):
        self.edit_certificate(lambda c: c["domain"].update(maximum_numerator=127.0))
        self.rejection("certificate search domain")

    def test_float_receipt_count(self):
        path = self.package / "EXPECTED.json"
        data = json.loads(path.read_text())
        data["improved_coefficients"] = float(data["improved_coefficients"])
        path.write_text(json.dumps(data))
        self.rejection("expected receipt mismatch")

    def test_missing_coefficient(self):
        self.edit_certificate(lambda c: c["entries"].pop())
        self.rejection("certificate reconstruction mismatch")

    def test_forged_shorter_path(self):
        self.edit_certificate(lambda c: c["entries"][0]["operations"].pop())
        self.rejection("certificate reconstruction mismatch")

    def test_forged_receipt(self):
        path = self.package / "EXPECTED.json"
        data = json.loads(path.read_text())
        data["programs"]["forward"]["lowerings"]["replacement"]["real_primitives"] -= 1
        path.write_text(json.dumps(data))
        self.rejection("expected receipt mismatch")

    def test_output_preserved(self):
        path = self.root / "existing.json"
        path.write_text("do not replace")
        self.rejection("output already exists", "--write", str(path))
        self.assertEqual(path.read_text(), "do not replace")

    def test_independent_coverage_rejects_omission(self):
        entries = verify.read(HERE / "CERTIFICATE.json")["entries"][:-1]
        with self.assertRaisesRegex(crosscheck.CertificateError, "does not cover"):
            crosscheck.run(entries, source=verify.PROVIDER / "LOCAL-PROGRAMS.json.gz")


if __name__ == "__main__":
    unittest.main()
