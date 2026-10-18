"""Mathematical failure and real artifact controls. Apache-2.0."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import engine as e
import verify as v


class AuditTests(unittest.TestCase):
    def run_export(self, root, *extra):
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(root / "verify.py"), *extra],
                              cwd=root.parent, text=True, capture_output=True, timeout=120)

    def export(self, parent):
        root = Path(parent) / "audit with spaces"
        shutil.copytree(HERE, root, ignore=shutil.ignore_patterns("__pycache__"))
        return root

    def test_integral_grid_is_a_prefix_obligation(self):
        word = [("SCALE", 0, 0, 1, 2), ("SCALE", 0, 0, 2, 1)]
        rational, peak, integral = e.rational_trace(word, e.identity(2))
        self.assertEqual(rational, e.identity(2))
        self.assertEqual(peak, 1)
        self.assertFalse(integral)
        with self.assertRaisesRegex(ValueError, "nonintegral"):
            e.apply(word, e.identity(2))

    def test_all_negative_cases_and_complete_small_partition_control(self):
        certificate = v.load_json(HERE / "CERTIFICATE.json")
        source = v.source_receipt()
        readers = e.fixture()
        states = e.chronological_contexts(readers, 5)
        self.assertEqual(v.controls(readers, certificate["edges"], states, source), certificate["controls"])
        self.assertEqual(v.small_partition_control(), certificate["small_exhaustion"])
        self.assertEqual(len(certificate["controls"]["rejected"]), 14)

    def test_source_and_pin_corruption_reject_before_math(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.export(directory)
            source = root / "sources/pr1537-model.py"
            source.write_bytes(source.read_bytes()+b"\n# changed source\n")
            result = self.run_export(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source SHA256", result.stderr)
            shutil.copy2(HERE / "sources/pr1537-model.py", source)
            pins = root / "PREDECESSOR.json"
            data = json.loads(pins.read_text())
            data["construction_head"] = "0"*40
            pins.write_text(json.dumps(data))
            result = self.run_export(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("pin manifest drift", result.stderr)

    def test_unused_terminal_corruption_rejects_on_disk(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.export(directory)
            path = root / "CERTIFICATE.json"
            data = json.loads(path.read_text())
            edge = next(x for x in data["edges"] if (x["a"], x["b"]) == (0, 53))
            edge["contexts"][1] += 1
            # Even rehashing the edited graph cannot forge a fresh rebuild.
            data["edges_sha256"] = v.digest(data["edges"])
            path.write_text(json.dumps(data))
            result = self.run_export(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("audit certificate mismatch", result.stderr)

    def test_type_sensitive_receipt_and_duplicate_json(self):
        self.assertNotEqual(v.canonical({"cap": True}), v.canonical({"cap": 1}))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"frontier":[],"frontier":[]}')
            with self.assertRaisesRegex(ValueError, "duplicate JSON"):
                v.load_json(path)
            path.write_text('{"cap":NaN}')
            with self.assertRaisesRegex(ValueError, "nonfinite"):
                v.load_json(path)

    def test_read_only_relocation_and_byte_identical_regeneration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.export(directory)
            try:
                for path in root.rglob("*"):
                    path.chmod(0o555 if path.is_dir() else 0o444)
                root.chmod(0o555)
                result = self.run_export(root)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("PASS_INDEPENDENT_CANCELLED_RETURN_GRAPH", result.stdout)
                emitted = self.run_export(root, "--emit")
                self.assertEqual(emitted.returncode, 0, emitted.stderr)
                self.assertEqual(emitted.stdout.encode(), (root / "CERTIFICATE.json").read_bytes())
                self.assertFalse(any(root.rglob("__pycache__")))
            finally:
                root.chmod(0o755)
                for path in root.rglob("*"):
                    path.chmod(0o755 if path.is_dir() else 0o644)


if __name__ == "__main__":
    unittest.main()
