"""Public replay and deliberate operational mutations for the local cost audit."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("cost_audit", HERE / "verify.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class Check(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.words, cls.records, cls.stream = audit.authenticate()

    def test_redundant_motion_invalidates_exact_bill(self):
        old = self.stream.Counter.decrement
        def extra_read(counter):
            old(counter)
            counter.tape.read()
        self.stream.Counter.decrement = extra_read
        try:
            with self.assertRaisesRegex(ValueError, "exact countdown lifecycle bill"):
                audit.countdowns(self.words, self.stream)
        finally:
            self.stream.Counter.decrement = old

    def test_omitted_erasure_is_detected(self):
        old = self.stream.Counter.close
        self.stream.Counter.close = lambda _counter: None
        try:
            with self.assertRaisesRegex(ValueError, "erased local tape"):
                audit.countdowns(self.words, self.stream)
        finally:
            self.stream.Counter.close = old

    def test_semantic_controls(self):
        self.assertEqual(len(audit.controls(self.words, self.records, self.stream)), 5)

    def test_export_and_authentication(self):
        with tempfile.TemporaryDirectory(prefix="binary-add-audit-") as tmp:
            dest = Path(tmp) / "export"
            shutil.copytree(HERE, dest, ignore=shutil.ignore_patterns("__pycache__"))
            def run():
                return subprocess.run([sys.executable, "-I", "-O", "-B", str(dest / "verify.py")],
                                      cwd=tmp, text=True, encoding="utf8", capture_output=True, timeout=90)
            files = list(dest.rglob("*"))
            try:
                for path in files:
                    if path.is_file():
                        path.chmod(0o444)
                good = run()
                self.assertEqual(good.returncode, 0, good.stderr)
                self.assertIn("PASS_BINARY_ADD_COST_AUDIT", good.stdout)
            finally:
                for path in files:
                    if path.is_file():
                        path.chmod(0o666)
            source = dest / "source" / "stream.py"
            original = source.read_bytes()
            source.write_bytes(original + b"\n# source mutation\n")
            bad = run()
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("source hash source/stream.py", bad.stderr)
            source.write_bytes(original)
            receipt = dest / "RESULT.json"
            data = json.loads(receipt.read_text())
            data["countdowns"]["cases"] += 1
            receipt.write_text(json.dumps(data), encoding="utf8")
            bad = run()
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("receipt mismatch", bad.stderr)
            receipt.unlink()
            missing = run()
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("RESULT.json", missing.stderr)

    def test_duplicate_json_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"x":1,"x":2}', object_pairs_hook=audit.unique)


if __name__ == "__main__":
    unittest.main()
