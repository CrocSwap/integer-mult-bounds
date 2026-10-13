"""Negative controls for source correspondence, independently of Lean execution."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import check


class BindingTests(unittest.TestCase):
    def setUp(self):
        self.original = check.PACKAGE
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name) / "repo"
        self.package = self.repo / "research/r420-scatter-lifecycle"
        self.package.mkdir(parents=True)
        for source in [*self.original.glob("*.lean"), self.original / "MANIFEST.json"]:
            shutil.copyfile(source, self.package / source.name)
        self.manifest = json.loads((self.package / "MANIFEST.json").read_text())
        for row in self.manifest["repository_inputs"]:
            destination = self.repo / row["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.original.parents[1] / row["path"], destination)
        check.PACKAGE = self.package

    def tearDown(self):
        check.PACKAGE = self.original
        self.temp.cleanup()

    def data_mutation(self, before, after):
        path = self.package / "R420ScatterData.lean"
        text = path.read_text()
        self.assertIn(before, text)
        path.write_text(text.replace(before, after, 1))
        # Refreshing the local source hash must not defeat source correspondence.
        for row in self.manifest["modules"]:
            if row["name"] == "R420ScatterData":
                row["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        (self.package / "MANIFEST.json").write_text(json.dumps(self.manifest))
        with self.assertRaisesRegex(ValueError, "exact source projection"):
            check.bind(self.repo)

    def test_valid_relocated_inputs(self):
        self.assertEqual(len(check.bind(self.repo)["modules"]), 4)

    def test_missing_module_inventory(self):
        original = self.manifest["modules"]
        for incomplete in ([], original[:-1]):
            with self.subTest(modules=len(incomplete)):
                self.manifest["modules"] = incomplete
                (self.package / "MANIFEST.json").write_text(json.dumps(self.manifest))
                with self.assertRaisesRegex(ValueError, "four-module inventory"):
                    check.bind(self.repo)

    def test_missing_lifecycle_probe(self):
        self.manifest["modules"][-1]["probes"].remove("CurrentMain.R420ScatterLifecycle.exact_lifecycle")
        (self.package / "MANIFEST.json").write_text(json.dumps(self.manifest))
        with self.assertRaisesRegex(ValueError, "required probe inventory"):
            check.bind(self.repo)

    def test_missing_exporter_input(self):
        self.manifest["repository_inputs"].pop(1)
        (self.package / "MANIFEST.json").write_text(json.dumps(self.manifest))
        with self.assertRaisesRegex(ValueError, "three-source inventory"):
            check.bind(self.repo)

    def test_redirected_word_path(self):
        self.manifest["word"] = self.manifest["repository_inputs"][1]["path"]
        (self.package / "MANIFEST.json").write_text(json.dumps(self.manifest))
        with self.assertRaisesRegex(ValueError, "fixed word/core manifest paths"):
            check.bind(self.repo)

    def test_retained_order_even_with_refreshed_hash(self):
        self.data_mutation("[603, 568, 597", "[568, 603, 597")

    def test_scatter_index_with_same_shape(self):
        self.data_mutation("def scatter : List (List Nat) := [[0, 1]",
                           "def scatter : List (List Nat) := [[0, 2]")

    def test_exported_destination_order_with_same_count(self):
        self.data_mutation("(603, [120, 121, 122", "(603, [121, 120, 122")

    def test_proof_source_change(self):
        path = self.package / "R420ScatterLifecycle.lean"
        path.write_text(path.read_text().replace("def temp : Register := ⟨660,", "def temp : Register := ⟨659,"))
        with self.assertRaisesRegex(ValueError, "Lean source hash"):
            check.bind(self.repo)

    def test_changed_exporter(self):
        path = self.repo / "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
        path.write_bytes(path.read_bytes().replace(b"if k in row:", b"if k not in row:"))
        with self.assertRaisesRegex(ValueError, "source hash"):
            check.bind(self.repo)

    def test_changed_generic_semantics(self):
        path = self.package / "BitCopyScatterWindow.lean"
        path.write_text(path.read_text().replace("then false else s r", "then true else s r"))
        with self.assertRaisesRegex(ValueError, "Lean source hash"):
            check.bind(self.repo)


if __name__ == "__main__":
    unittest.main()
