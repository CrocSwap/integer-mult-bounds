#!/usr/bin/env python3
"""Artifact admission and portable verification failure modes. Apache-2.0."""
import copy
import gzip
from pathlib import Path
import runpy
import shutil
import tempfile
import unittest

V = runpy.run_path(str(Path(__file__).resolve().with_name("verify.py")))
C = V["C"]


class ArtifactAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent = C["load"](C["ROOT"] / C["PARENT"] / "candidate.json.gz")
        cls.candidate = C["load"](C["HERE"] / "candidate.json.gz")
        cls.cert = C["load"](C["HERE"] / "CERTIFICATE.json")

    def test_semantic_candidate_recompression(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidate.json.gz"
            path.write_bytes(gzip.compress(C["canonical"](self.candidate), compresslevel=1, mtime=12345))
            V["check_certificate"](self.parent, C["load"](path), self.cert)

    def test_corrupted_candidate_rejected(self):
        bad = copy.deepcopy(self.candidate)
        bad["A"][0][1] += 1
        with self.assertRaisesRegex(ValueError, "candidate digest"):
            V["check_certificate"](self.parent, bad, self.cert)

    def test_corrupted_parent_rejected(self):
        bad = copy.deepcopy(self.parent)
        bad["D"][0][2].pop()
        with self.assertRaisesRegex(ValueError, "parent digest"):
            V["check_certificate"](bad, self.candidate, self.cert)

    def test_duplicate_keys_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.json"
            path.write_text('{"seed":3,"seed":18}')
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                C["load"](path)

    def test_nonfinite_json_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.json"
            path.write_text('{"saving":NaN}')
            with self.assertRaisesRegex(ValueError, "invalid JSON constant"):
                C["load"](path)

    def test_missing_source_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                C["pins"](Path(tmp))

    def test_modified_pinned_source_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = C["load"](C["HERE"] / "SOURCES.json")
            for name in manifest["files"]:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(C["ROOT"] / name, target)
            changed = root / C["CHECKER"]
            changed.write_bytes(changed.read_bytes() + b"\n# corrupted source\n")
            with self.assertRaisesRegex(ValueError, "source hash mismatch"):
                C["pins"](root)


if __name__ == "__main__":
    unittest.main()
