"""Artifact-level positive and rejecting controls, with frozen inputs untouched."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class ArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="qq16-adaptive-")
        cls.root = Path(cls.temp.name)
        cls.package = cls.root / "research" / HERE.name
        shutil.copytree(HERE, cls.package, ignore=shutil.ignore_patterns("__pycache__"))
        source = json.loads((HERE / "SOURCES.json").read_text())
        for row in source["files"]:
            if row["usage"] == "input":
                target = cls.root / row["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row["path"], target)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def invoke(self):
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(self.package / "verify.py")],
                              cwd=self.root, capture_output=True, text=True, timeout=120)

    def test_1_relocated_positive_is_read_only(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("optimal_sets=45", result.stdout)
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_2_corrupted_optimal_set_is_rejected(self):
        path = self.package / "RESULT.json"
        original = path.read_bytes()
        data = json.loads(original)
        data["optimal_omissions"][0] = 1  # A port required by every optimal set.
        path.write_text(json.dumps(data))
        try:
            result = self.invoke()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("complete receipt equality", result.stderr)
        finally:
            path.write_bytes(original)

    def test_3_changed_source_is_rejected(self):
        path = self.root / "research/joint-query/evidence/JOINT-QUERY-TRANSFER.md"
        original = path.read_bytes()
        path.write_bytes(original + b"\nchanged source\n")
        try:
            result = self.invoke()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source hash", result.stderr)
        finally:
            path.write_bytes(original)

    def test_4_dropped_input_pin_is_rejected(self):
        path = self.package / "SOURCES.json"
        original = path.read_bytes()
        data = json.loads(original)
        data["files"] = [r for r in data["files"] if r["path"] != "research/joint-query/certificate.json.gz"]
        path.write_text(json.dumps(data))
        try:
            result = self.invoke()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("complete declared source set", result.stderr)
        finally:
            path.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
