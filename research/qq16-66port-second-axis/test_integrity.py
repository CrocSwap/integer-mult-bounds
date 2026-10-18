"""Relocated positive replay and proof-relevant corruption controls."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
spec = importlib.util.spec_from_file_location("second_axis_verifier", PACKAGE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class IntegrityTests(unittest.TestCase):
    def test_typed_complete_receipt(self):
        good = json.loads((PACKAGE / "RESULT.json").read_text())
        verify.equal_receipt(good, deepcopy(good))
        for field, value in (("observed_port_count", True), ("support", []),
                             ("zero_later_queries", [1]), ("trace", [])):
            with self.subTest(field=field):
                bad = deepcopy(good)
                bad[field] = value
                with self.assertRaisesRegex(ValueError, "typed receipt"):
                    verify.equal_receipt(good, bad)

    def test_relocated_replay_and_corruption(self):
        # Keep disposable copies adjacent to the checkout, never alter frozen inputs.
        with tempfile.TemporaryDirectory(prefix="qq16-integrity-", dir=ROOT.parent) as temp:
            root = Path(temp)
            package = root / "research" / PACKAGE.name
            shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__"))
            sources = json.loads((PACKAGE / "SOURCES.json").read_text())
            for row in sources["files"]:
                if row["usage"] == "input":
                    target = root / row["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(ROOT / row["path"], target)

            def run():
                return subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py")],
                                      cwd=root, capture_output=True, text=True, timeout=90)

            before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            result = run()
            self.assertEqual(result.returncode, 0, result.stderr[-2000:])
            self.assertIn("PASS_QQ16_66PORT_SECOND_AXIS", result.stdout)
            after = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            self.assertEqual(before, after, "replay changed copied input or package bytes")

            receipt = package / "RESULT.json"
            original = receipt.read_text()
            bad = json.loads(original)
            bad["observed_port_count"] = True
            receipt.write_text(json.dumps(bad))
            result = run()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("typed receipt mismatch", result.stderr)
            receipt.write_text(original)

            source = root / "research/joint-query/evidence/CONSERVED-QQ16.md"
            source.write_bytes(source.read_bytes() + b"\ncorrupted source control\n")
            result = run()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source hash mismatch", result.stderr)


if __name__ == "__main__":
    unittest.main()
