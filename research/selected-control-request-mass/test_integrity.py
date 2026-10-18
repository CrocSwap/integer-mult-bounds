"""Behavioral integrity checks; never alter committed evidence or source."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


class Integrity(unittest.TestCase):
    def run_copy(self, change, semantic=False):
        with tempfile.TemporaryDirectory(prefix="request-mass-test-", dir=HERE) as tmp:
            target = Path(tmp) / "package"
            shutil.copytree(HERE, target, ignore=shutil.ignore_patterns(
                "request-mass-test-*", "__pycache__"))
            change(target)
            if semantic:
                path = target / "SOURCES.json"
                sources = json.loads(path.read_text())
                for entry in sources["vendored_sources"]:
                    data = (target / entry["path"]).read_bytes()
                    entry["sha256"] = hashlib.sha256(data).hexdigest()
                    entry["git_blob"] = hashlib.sha1(
                        b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
                path.write_text(json.dumps(sources))
            return subprocess.run([sys.executable, "-I", "-O", "-B",
                                   str(target / "verify.py")],
                                  capture_output=True, text=True, timeout=120)

    def test_receipt_corruption(self):
        def change(target):
            path = target / "RESULT.json"
            result = json.loads(path.read_text())
            result["analytic"]["preparation_exponent"] = 591
            path.write_text(json.dumps(result))
        result = self.run_copy(change)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exact typed receipt equality", result.stderr)

    def test_source_pin(self):
        def change(target):
            with (target / "sources/pr2310/control.py").open("a") as stream:
                stream.write("\n# source drift\n")
        result = self.run_copy(change)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("predecessor SHA256", result.stderr)

    def test_semantic_branch_loss_with_rebound_pins(self):
        def change(target):
            path = target / "sources/pr2310/control.py"
            text = path.read_text()
            old = "bank(table.permutation[step.field])"
            self.assertEqual(text.count(old), 1)
            path.write_text(text.replace(old, '("constant", 1)'))
        result = self.run_copy(change, semantic=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("level recurrence equals unchanged source meters", result.stderr)

    def test_semantic_head_undercharge_with_rebound_pins(self):
        def change(target):
            path = target / "sources/pr2310/control.py"
            text = path.read_text()
            old = "self.meter.head_moves += abs(destination - self.head)"
            self.assertEqual(text.count(old), 1)
            path.write_text(text.replace(old, "self.meter.head_moves += 0"))
        result = self.run_copy(change, semantic=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("level recurrence equals unchanged source meters", result.stderr)


if __name__ == "__main__":
    unittest.main()
