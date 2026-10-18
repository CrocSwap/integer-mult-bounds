"""Check evidence corruption and a minimal relocated optimized replay.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="bit-one-relation-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package = self.root / "research" / HERE.name
        shutil.copytree(HERE, self.package, ignore=shutil.ignore_patterns("__pycache__"))
        for row in json.loads((HERE / "SOURCES.json").read_text())["files"]:
            if row["usage"] == "input":
                target = self.root / row["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / row["path"], target)
        self.cwd = self.root / "unrelated-working-directory"
        self.cwd.mkdir()

    def run_replay(self):
        return subprocess.run(
            [sys.executable, "-I", "-O", "-B", str(self.package / "verify.py")],
            cwd=self.cwd, capture_output=True, text=True, timeout=30,
        )

    def snapshot(self):
        return {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.root.rglob("*") if p.is_file()}

    def test_relocated_optimized_replay_does_not_write(self):
        before = self.snapshot()
        result = self.run_replay()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS_BIT_ONE_RELATION", result.stdout)
        self.assertEqual(self.snapshot(), before)

    def test_changed_source_is_rejected(self):
        source = self.root / "research/bit-three-register-lower-bound/README.md"
        source.write_bytes(source.read_bytes() + b"\nChanged pinned evidence.\n")
        result = self.run_replay()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source SHA256", result.stderr)

    def test_changed_certificate_is_rejected(self):
        path = self.package / "CERTIFICATE.json"
        data = json.loads(path.read_text())
        data["census"][3]["conjugations"] += 1
        path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        result = self.run_replay()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("certificate differs from exact replay", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
