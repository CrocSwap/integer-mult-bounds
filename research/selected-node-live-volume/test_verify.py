#!/usr/bin/env python3
"""Behavioral failure controls and a Git-free read-only export replay."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("node_volume_verifier", PACKAGE / "verify.py")
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class Controls(unittest.TestCase):
    def test_geometry_and_key_contract(self):
        self.assertEqual(verifier.composite_geometry(4, 3, 48, 1, 1, 81, 16), (15552, 4212))
        for values, message in (
            ((4, 3, 48, True, 1, 81, 16), "positive integer"),
            ((4, 3, 48, 0, 1, 81, 16), "positive integer"),
            ((4, 3, 48, 1, 1, 81, 82), "route key"),
            ((1, 3, 1, 1, 1, 81, 16), "extras fit"),
        ):
            with self.subTest(values=values), self.assertRaisesRegex(ValueError, message):
                verifier.composite_geometry(*values)

    def test_receipt_types_and_missing_phase(self):
        expected = {"peak": 1, "phases": {"peel": 1}}
        verifier.compare_receipt(dict(expected), expected)
        for bad in ({"peak": True, "phases": {"peel": 1}}, {"peak": 1},
                    {"peak": 1.0, "phases": {"peel": 1}}):
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, "typed receipt"):
                verifier.compare_receipt(bad, expected)

    def test_actual_peel_rejects_four_input_budget(self):
        m = verifier.modules(verifier.authenticate())
        original = m.records.Tape.write
        for budget in (4 * 729, 6 * 729 - 1):
            with self.subTest(budget=budget), self.assertRaisesRegex(ValueError, "complete-node content cap"):
                verifier.peel_fixture(m, 1, 1, budget=budget)
            self.assertIs(m.records.Tape.write, original)

    def test_direct_census_catches_missed_write(self):
        m = verifier.modules(verifier.authenticate())
        tape = m.records.Tape()
        meter = verifier.Meter(m, 10)
        meter.mark(tape, "borrowed")
        unobserved_write = m.records.Tape.write
        with meter.install():
            tape.append(0)
            unobserved_write(tape, 1)
            with self.assertRaisesRegex(ValueError, "direct content census"):
                meter.census()

    def test_read_only_git_free_export_and_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            exported = Path(directory) / "package"
            shutil.copytree(PACKAGE, exported, ignore=shutil.ignore_patterns("__pycache__"))
            files = tuple(path for path in exported.rglob("*") if path.is_file())
            directories = (exported,) + tuple(path for path in exported.rglob("*") if path.is_dir())
            for path in files:
                path.chmod(0o444)
            for path in directories:
                path.chmod(0o555)
            try:
                result = self.command(exported, "--peel-only", success=True)
                self.assertEqual(len(result.stdout.splitlines()), 4)
                self.assertEqual(json.loads(result.stdout.splitlines()[0])["peak"], 4374)
            finally:
                for path in directories:
                    path.chmod(0o755)
                for path in files:
                    path.chmod(0o644)
            for name in ("vendor/node.py", "vendor/peel.py", "vendor/driver.py",
                         "vendor/vendor/selection.py", "vendor/vendor/bitstream.py"):
                path = exported / name
                original = path.read_bytes()
                path.write_bytes(original + b"\n# changed input\n")
                result = self.command(exported, "--peel-only", success=False)
                self.assertIn("source SHA256", result.stderr)
                path.write_bytes(original)
            path = exported / "SNAPSHOTS.json"
            original = path.read_bytes()
            path.write_bytes(original + b" ")
            result = self.command(exported, "--peel-only", success=False)
            self.assertIn("manifest binding", result.stderr)
            path.write_bytes(original)
            (exported / "vendor/extra.py").write_text("raise RuntimeError('unbound')\n")
            self.assertIn("source inventory", self.command(exported, "--peel-only", success=False).stderr)

    def test_output_refuses_internal_or_existing_path(self):
        result = self.command(PACKAGE, "--write-result", str(PACKAGE / "RESULT.json"), success=False)
        self.assertIn("external receipt", result.stderr)
        with tempfile.NamedTemporaryFile() as existing:
            result = self.command(PACKAGE, "--write-result", existing.name, success=False)
            self.assertIn("must not exist", result.stderr)

    def command(self, package, *arguments, success):
        result = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py"), *arguments],
                                cwd=package, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result


if __name__ == "__main__":
    unittest.main()
