"""Artifact controls and an optimized replay after read-only relocation."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def run(directory):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(directory / "verify.py")],
                          cwd=directory.parent, text=True, capture_output=True, timeout=180)


class PackageTests(unittest.TestCase):
    def test_read_only_relocation(self):
        with tempfile.TemporaryDirectory(prefix="precision cuts ") as temp:
            dst = Path(temp) / "package with spaces"
            shutil.copytree(HERE, dst, ignore=shutil.ignore_patterns("__pycache__"))
            paths = list(dst.rglob("*")) + [dst]
            for path in paths:
                path.chmod(0o555 if path.is_dir() else 0o444)
            try:
                result = run(dst)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("PASS_PRECISION_CAPPED_UNIPOTENT_CUTS", result.stdout)
            finally:
                for path in paths:
                    path.chmod(0o755 if path.is_dir() else 0o644)

    def test_wrong_mathematical_receipt_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            dst = Path(temp) / "package"
            shutil.copytree(HERE, dst, ignore=shutil.ignore_patterns("__pycache__"))
            path = dst / "RESULT.json"
            data = json.loads(path.read_text())
            data["caps"][5]["word"]["peak"] -= 1
            path.write_text(json.dumps(data))
            result = run(dst)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("receipt mismatch", result.stderr)

    def test_frozen_predecessor_corruption_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            dst = Path(temp) / "package"
            shutil.copytree(HERE, dst, ignore=shutil.ignore_patterns("__pycache__"))
            source = dst / "sources/pr1537-model.py"
            source.write_bytes(source.read_bytes() + b"\n# changed source\n")
            result = run(dst)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("predecessor SHA256", result.stderr)

    def test_saved_duals_and_tampering(self):
        sys.path.insert(0, str(HERE))
        import planner
        import verify
        old = planner.predecessor()
        edges = planner.graph(old.fixture(), 5, old, True)
        receipt = json.loads((HERE / "RESULT.json").read_text())
        for row in receipt["frontier"]:
            verify.dual_check(row, edges, 53)
        wrong = json.loads(json.dumps(receipt["frontier"][-1]))
        wrong["distances"][-1] += 1
        with self.assertRaisesRegex(ValueError, "dual edge inequality"):
            verify.dual_check(wrong, edges, 53)


if __name__ == "__main__":
    unittest.main(verbosity=2)
