#!/usr/bin/env python3
"""Focused CLI/relocation/source/receipt controls; no repository-wide suite.

Prepared for Adam Gall with substantial OpenAI Codex assistance. Apache-2.0.
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


class PackageControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="connectivity-export-")
        self.root = Path(self.temp.name)
        self.package = self.root / "research" / PACKAGE.name
        shutil.copytree(PACKAGE, self.package, ignore=shutil.ignore_patterns("__pycache__"))
        manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
        for item in manifest["files"]:
            if item["usage"] == "input":
                destination = self.root / item["path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / item["path"], destination)

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, script="verify.py", args=(), succeeds=True, diagnostic=""):
        result = subprocess.run([sys.executable, "-I", "-O", "-B",
                                 str(self.package / script), *args],
                                cwd=self.root, text=True, capture_output=True, timeout=120)
        if succeeds:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("PASS_", result.stdout)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn(diagnostic, result.stderr)
        return result

    def test_relocated_optimized_replay_and_canonical_regeneration(self):
        # This is a source export without .git, with only declared external inputs.
        for script, receipt in (("verify.py", "RESULT.json"), ("independent.py", "DENSE.json")):
            before = (self.package / receipt).read_bytes()
            self.run_cli(script)
            self.run_cli(script, ("--write",))
            self.assertEqual((self.package / receipt).read_bytes(), before)

    def test_source_corruption_fails_closed(self):
        path = self.root / "research/mutable-source-minimum-queries/CERTIFICATE.json"
        path.write_text(path.read_text() + "\n")
        for script in ("verify.py", "independent.py"):
            self.run_cli(script, succeeds=False, diagnostic="source hash mismatch")

    def test_proof_and_invoice_receipt_mutations_reject(self):
        path = self.package / "RESULT.json"
        original = path.read_text()
        mutations = [lambda result: result["single_gate_census"]["4"].update(transitions=0),
                     lambda result: result["eight_factor_invoice"].update(X=0),
                     lambda result: result["serial_connectivity_control"].update(minimum_current_components=1)]
        for mutation in mutations:
            result = json.loads(original)
            mutation(result)
            path.write_text(json.dumps(result))
            self.run_cli(succeeds=False, diagnostic="differs from exact recomputation")
        path.write_text(original)

    def test_independent_coverage_mutation_rejects(self):
        path = self.package / "DENSE.json"
        result = json.loads(path.read_text())
        result["forward_inverse_pairs"] -= 1
        path.write_text(json.dumps(result))
        self.run_cli("independent.py", succeeds=False, diagnostic="DENSE.json mismatch")

    def test_selection_mismatch_rejects(self):
        path = self.package / "SELECTION.json"
        selection = json.loads(path.read_text())
        selection["seed"] = "0" * 32
        path.write_text(json.dumps(selection))
        self.run_cli(succeeds=False, diagnostic="selection seed mismatch")


if __name__ == "__main__":
    unittest.main(verbosity=2)
