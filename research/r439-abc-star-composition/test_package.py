#!/usr/bin/env python3
"""Artifact admission controls; no compiler or third-party Python dependency."""
import copy
import gzip
import json
from pathlib import Path
import runpy
import shutil
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class PackageAdmission(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="composition-admission-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "relocated"
        self.package = self.root / "research/r439-abc-star-composition"
        shutil.copytree(HERE, self.package, ignore=shutil.ignore_patterns("__pycache__"))
        manifest = json.loads((HERE / "SOURCES.json").read_text())
        for name in manifest["files"]:
            destination = self.root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)
        self.verifier = runpy.run_path(str(self.package / "verify.py"))

    def admit(self):
        return self.verifier["artifacts"](self.root)

    def test_relocated_artifacts(self):
        _, words, _ = self.admit()
        self.assertEqual(len(words), 8)

    def test_regenerated_compression_is_not_mathematical_equality(self):
        candidate = self.package / "candidate.json.gz"
        raw = gzip.decompress(candidate.read_bytes())
        for level in (1, 9):
            candidate.write_bytes(gzip.compress(raw, compresslevel=level, mtime=123456))
            self.admit()

    def test_immutable_source_pin(self):
        source = self.root / "research/e8-bit-p111-tuned/code/xcheck_p.py"
        source.write_bytes(source.read_bytes() + b"\n# changed source\n")
        with self.assertRaisesRegex(ValueError, "source hash mismatch"):
            self.admit()

    def test_pinned_vendor_container_is_immutable(self):
        source = self.package / "vendor/pr1062/candidate.json.gz"
        source.write_bytes(gzip.compress(gzip.decompress(source.read_bytes()), mtime=123456))
        with self.assertRaisesRegex(ValueError, "source hash mismatch"):
            self.admit()

    def test_rebound_candidate_digest_cannot_hide_changed_phase(self):
        c = self.verifier["C"]
        candidate = c["load"](self.package / "candidate.json.gz")
        candidate["D"].pop()
        (self.package / "candidate.json.gz").write_bytes(gzip.compress(c["canonical"](candidate), mtime=0))
        cert = c["load"](self.package / "CERTIFICATE.json")
        cert["corners"]["7"]["sha256"] = c["digest"](candidate)
        (self.package / "CERTIFICATE.json").write_text(json.dumps(cert))
        with self.assertRaisesRegex(ValueError, "certificate regeneration"):
            self.admit()

    def test_receipt_omits_failed_precision_corner(self):
        path = self.package / "CERTIFICATE.json"
        cert = json.loads(path.read_text())
        del cert["corners"]["4"]
        path.write_text(json.dumps(cert))
        with self.assertRaisesRegex(ValueError, "certificate regeneration"):
            self.admit()

    def test_undercharged_cost(self):
        path = self.package / "CERTIFICATE.json"
        cert = json.loads(path.read_text())
        cert["corners"]["7"]["ADDs"] = 10628
        path.write_text(json.dumps(cert))
        with self.assertRaisesRegex(ValueError, "certificate regeneration"):
            self.admit()

    def test_nonphase_payload_edit(self):
        c = self.verifier["C"]
        path = self.package / "candidate.json.gz"
        candidate = c["load"](path)
        candidate["stats"]["junk_wires"] += 1
        path.write_bytes(gzip.compress(c["canonical"](candidate), mtime=0))
        with self.assertRaisesRegex(ValueError, "candidate regeneration"):
            self.admit()

    def test_duplicate_and_nonfinite_json(self):
        path = self.package / "CERTIFICATE.json"
        for raw in ('{"x":0,"x":1}', '{"x":NaN}', '{"x":Infinity}', '{"x":-Infinity}'):
            with self.subTest(raw=raw):
                path.write_text(raw)
                with self.assertRaisesRegex(ValueError, "duplicate JSON|nonfinite JSON"):
                    self.admit()

    def test_boolean_numeric_receipt(self):
        path = self.package / "CERTIFICATE.json"
        cert = json.loads(path.read_text())
        cert["corners"]["7"]["ADDs"] = True
        path.write_text(json.dumps(cert))
        with self.assertRaisesRegex(ValueError, "certificate regeneration"):
            self.admit()


if __name__ == "__main__":
    unittest.main()
