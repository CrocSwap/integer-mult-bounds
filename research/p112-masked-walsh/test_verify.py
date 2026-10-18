"""Portable replay and corruption controls; standard library only."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent


class PackageChecks(unittest.TestCase):
    def test_portability_and_rejections(self):
        with tempfile.TemporaryDirectory(prefix="p112 replay with spaces ") as directory:
            target = Path(directory) / "standalone"
            shutil.copytree(HERE, target, ignore=shutil.ignore_patterns("__pycache__"))

            def run(*args):
                return subprocess.run([sys.executable, "-I", "-O", "-B",
                                       str(target / "verify.py"), *map(str, args)],
                                      cwd=directory, text=True, capture_output=True, timeout=120)

            result = run()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("cases=572320 minimum=72", result.stdout)
            receipt = target / "RESULT.json"
            original = receipt.read_bytes()
            changed = json.loads(original)
            changed["minimum"] = 64
            receipt.write_text(json.dumps(changed))
            result = run()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("certificate mismatch", result.stderr)
            receipt.write_bytes(original)

            source = target / "vendor/pr845-geometry.py"
            source_bytes = source.read_bytes()
            source.write_bytes(source_bytes + b"\n# corruption control\n")
            result = run()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source mismatch", result.stderr)
            source.write_bytes(source_bytes)

            geometry = target / "GEOMETRY.json"
            geometry_bytes = geometry.read_bytes()
            changed = json.loads(geometry_bytes)
            changed["X"][0][0] += 1
            geometry.write_text(json.dumps(changed))
            result = run()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source mismatch", result.stderr)
            geometry.write_bytes(geometry_bytes)

            protected = Path(directory) / "existing.json"
            protected.write_text("keep this file\n")
            result = run("--write", protected)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(protected.read_text(), "keep this file\n")


if __name__ == "__main__":
    unittest.main()
