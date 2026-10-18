"""End-to-end source/receipt controls; all mutations stay in temporary copies.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


class Integrity(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="dyadic-order-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / "research" / PACKAGE.name
        shutil.copytree(PACKAGE, self.package, ignore=shutil.ignore_patterns("__pycache__"))
        self.sources = json.loads((PACKAGE / "SOURCES.json").read_text())
        for entry in self.sources["files"]:
            if entry["usage"] == "input":
                target = self.root / entry["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / entry["path"], target)

    def replay(self):
        return subprocess.run([sys.executable, "-O", "-B", str(self.package / "verify.py")],
                              cwd=self.root, capture_output=True, text=True, timeout=30)

    def test_relocated_without_git(self):
        self.assertFalse((self.root / ".git").exists())
        result = self.replay()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS_DYADIC_ROOT_ORDER: 24338 pair comparisons", result.stdout)

    def test_changed_source_rejected(self):
        entry = next(x for x in self.sources["files"] if x["usage"] == "input")
        path = self.root / entry["path"]
        path.write_bytes(path.read_bytes() + b"\nsource corruption\n")
        result = self.replay()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source drift:", result.stderr)
        self.assertNotIn("PASS_DYADIC_ROOT_ORDER", result.stdout)

    def test_forged_root_order_rejected(self):
        path = self.package / "RESULT.json"
        data = json.loads(path.read_text())
        data["fixtures"]["retained_pr1048"]["root_order"] = 1
        path.write_text(json.dumps(data))
        result = self.replay()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("committed receipt differs", result.stderr)
        self.assertNotIn("PASS_DYADIC_ROOT_ORDER", result.stdout)

    def test_incomplete_coverage_receipt_rejected(self):
        path = self.package / "RESULT.json"
        data = json.loads(path.read_text())
        data["census"]["pairs"] -= 1
        path.write_text(json.dumps(data))
        result = self.replay()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("committed receipt differs", result.stderr)
        self.assertNotIn("PASS_DYADIC_ROOT_ORDER", result.stdout)


if __name__ == "__main__":
    unittest.main()
