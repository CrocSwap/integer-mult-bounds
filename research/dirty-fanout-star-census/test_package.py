"""Failure sensitivity and independent package relocation checks; stdlib only."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("census_verifier", ROOT / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class CensusTests(unittest.TestCase):
    def test_lost_label_multiplicity_is_detected(self):
        original = v.transitions

        def unweighted(state):
            return ((target, 1) for target, _ in original(state))

        with patch.object(v, "transitions", unweighted):
            with self.assertRaisesRegex(ValueError, "minimum-word census"):
                v.census(2)

    def test_permuted_output_labels_preserve_free_endpoint(self):
        compiler = v.source_emitter()
        common, branches = [0, 1], [[2], [3, 4], [5, 6, 7]]
        word, dirt = compiler(common, branches)
        # Reorder whole output/branch contracts, not the factors inside them.
        remap = {1: 3, 2: 1, 3: 2}
        renamed = [(f, remap.get(x, x), remap.get(y, y), s)
                   for f, x, y, s in word]
        v.check_word(renamed, 4 + dirt, common, [branches[1], branches[2], branches[0]])

    def test_dirty_connector_cannot_be_treated_as_clean(self):
        # This word implements the desired signal only if the initial connector
        # is zero: it omits the output cancellation at the restored dirty value.
        word = [(0, 0, 2, 1), (1, 2, 1, 1), (0, 0, 2, -1)]
        with self.assertRaisesRegex(ValueError, "endpoint mismatch"):
            v.check_word(word, 3, [0], [[1]])

    def test_negative_coefficient_cannot_be_erased_as_mod_two(self):
        word = [(0, 0, 2, 1), (1, 2, 1, -1),
                (0, 0, 2, -1), (1, 2, 1, 1)]
        with self.assertRaisesRegex(ValueError, "endpoint mismatch"):
            v.check_word(word, 3, [0], [[1]])

    def test_endpoint_preserving_extra_ports_are_outside_star_model(self):
        compiler = v.source_emitter()
        word, _ = compiler([0], [[1], [2]])
        # An inverse pair is algebraically neutral but uses a forbidden source.
        extended = word + [(1, 0, 1, 1), (1, 0, 1, -1)]
        v.check_word(extended, 4, [0], [[1], [2]])
        with self.assertRaisesRegex(ValueError, "outside star-query alphabet"):
            v.check_star_word(extended, 2, 3)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="star census ")
        self.package = Path(self.temp.name) / "standalone package"
        shutil.copytree(ROOT, self.package, ignore=shutil.ignore_patterns("__pycache__"))

    def tearDown(self):
        self.temp.cleanup()

    def run_package(self):
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(self.package / "verify.py")],
                              cwd=self.temp.name, capture_output=True, text=True, timeout=60)

    def test_standalone_relocation_and_read_only_default(self):
        before = {p.relative_to(self.package): p.read_bytes()
                  for p in self.package.rglob("*") if p.is_file()}
        run = self.run_package()
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("PASS_STAR_CENSUS", run.stdout)
        after = {p.relative_to(self.package): p.read_bytes()
                 for p in self.package.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_changed_source_rejected(self):
        source = self.package / "vendor/pr889/batch.py"
        source.write_text(source.read_text() + "\n# source drift\n")
        run = self.run_package()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("source SHA256", run.stderr)

    def test_missing_source_pin_rejected(self):
        path = self.package / "SOURCES.json"
        manifest = json.loads(path.read_text())
        manifest["files"].pop()
        path.write_text(json.dumps(manifest))
        run = self.run_package()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("source inventory", run.stderr)

    def test_wrong_subject_commit_rejected(self):
        path = self.package / "SOURCES.json"
        manifest = json.loads(path.read_text())
        manifest["commit"] = "0" * 40
        path.write_text(json.dumps(manifest))
        run = self.run_package()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("subject commit", run.stderr)

    def test_changed_receipt_rejected(self):
        path = self.package / "CERTIFICATE.json"
        receipt = json.loads(path.read_text())
        receipt["census"][4]["minimum_word_count"] += 1
        path.write_text(json.dumps(receipt))
        run = self.run_package()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("certificate mismatch", run.stderr)


if __name__ == "__main__":
    unittest.main()
