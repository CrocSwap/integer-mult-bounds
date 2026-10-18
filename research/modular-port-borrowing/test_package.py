#!/usr/bin/env python3
"""Fault injection into the same fast admission used by the complete replay."""
import gzip
import json
from pathlib import Path
import runpy
import shutil
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="modular-package-")
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "relocated"
        shutil.copytree(HERE, self.path, ignore=shutil.ignore_patterns("__pycache__"))
        self.v = runpy.run_path(str(self.path / "verify.py"))

    def admit(self):
        case, program, _ = self.v["admit_artifacts"]()
        self.v["admit_certificate"](case, program)

    def put(self, name, value):
        raw = json.dumps(value, sort_keys=True).encode()
        (self.path / name).write_bytes(gzip.compress(raw, mtime=0) if name.endswith(".gz") else raw)

    def test_offline_relocation(self):
        self.admit()

    def test_generated_recompression(self):
        for name in ("CASE.json.gz", "PROGRAM.json.gz"):
            path = self.path / name
            raw = gzip.decompress(path.read_bytes())
            for level in (1, 9):
                path.write_bytes(gzip.compress(raw, compresslevel=level, mtime=12345))
                self.admit()

    def test_source_code_pin(self):
        path = self.path / "vendor/pr1057/borrow.py"
        path.write_bytes(path.read_bytes() + b"\nraise RuntimeError('unpinned parent executed')\n")
        with self.assertRaisesRegex(ValueError, "source hash mismatch"):
            runpy.run_path(str(self.path / "verify.py"))
        with self.assertRaisesRegex(ValueError, "source hash mismatch"):
            self.admit()

    def test_selected_context_pin(self):
        path = self.path / "BASE-SELECTION.json"
        path.write_bytes(path.read_bytes() + b" ")
        with self.assertRaisesRegex(ValueError, "source hash mismatch"):
            self.admit()

    def test_wrong_width_with_rebound_digest(self):
        case = self.v["C"]["load"](self.path / "CASE.json.gz")
        case["width"] -= 1
        self.put("CASE.json.gz", case)
        receipt = self.v["C"]["load"](self.path / "CERTIFICATE.json")
        receipt["case_sha256"] = self.v["C"]["digest"](case)
        self.put("CERTIFICATE.json", receipt)
        with self.assertRaisesRegex(ValueError, "case regeneration"):
            self.admit()

    def test_removed_reduction_with_rebound_digest(self):
        program = self.v["C"]["load"](self.path / "PROGRAM.json.gz")
        program.remove(["low", "p"])
        self.put("PROGRAM.json.gz", program)
        receipt = self.v["C"]["load"](self.path / "CERTIFICATE.json")
        receipt["program_sha256"] = self.v["C"]["digest"](program)
        self.put("CERTIFICATE.json", receipt)
        with self.assertRaisesRegex(ValueError, "primitive regeneration"):
            self.admit()

    def test_undercharged_reductions(self):
        receipt = self.v["C"]["load"](self.path / "CERTIFICATE.json")
        for key in ("invoice", "execution"):
            receipt["concrete"]["bounded_positive"][key]["counts"]["low"] -= 1
        self.put("CERTIFICATE.json", receipt)
        with self.assertRaisesRegex(ValueError, "complete invoice"):
            self.admit()

    def test_free_product_work(self):
        receipt = self.v["C"]["load"](self.path / "CERTIFICATE.json")
        receipt["concrete"]["dirty_bits_positive"]["invoice"]["work_bits"] = 4 * 56
        self.put("CERTIFICATE.json", receipt)
        with self.assertRaisesRegex(ValueError, "complete invoice"):
            self.admit()

    def test_omitted_negative_direction(self):
        receipt = self.v["C"]["load"](self.path / "CERTIFICATE.json")
        del receipt["concrete"]["dirty_bits_negative"]
        self.put("CERTIFICATE.json", receipt)
        with self.assertRaisesRegex(ValueError, "concrete inventory"):
            self.admit()

    def test_dropped_tree_coverage(self):
        receipt = self.v["C"]["load"](self.path / "CERTIFICATE.json")
        receipt["all_trees"]["cases"] -= 1
        self.put("CERTIFICATE.json", receipt)
        with self.assertRaisesRegex(ValueError, "matrix coverage"):
            self.admit()

    def test_boolean_numeric_receipt(self):
        receipt = self.v["C"]["load"](self.path / "CERTIFICATE.json")
        receipt["endpoint_bound"]["width"] = True
        self.put("CERTIFICATE.json", receipt)
        with self.assertRaisesRegex(ValueError, "endpoint allowance"):
            self.admit()

    def test_duplicate_nonfinite_json(self):
        for raw in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}', '{"x":-Infinity}'):
            with self.subTest(raw=raw):
                (self.path / "CERTIFICATE.json").write_text(raw)
                with self.assertRaisesRegex(ValueError, "duplicate JSON|nonfinite JSON"):
                    self.admit()


if __name__ == "__main__":
    unittest.main()
