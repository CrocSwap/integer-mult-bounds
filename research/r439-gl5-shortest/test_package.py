#!/usr/bin/env python3
"""Artifact, completeness and source-admission failure cases. Apache-2.0."""
import copy
import gzip
from pathlib import Path
import runpy
import shutil
import tempfile
import unittest

V = runpy.run_path(str(Path(__file__).resolve().with_name("verify.py")))
C = V["C"]


class AdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent = C["load"](C["HERE"] / C["PARENT"])
        cls.candidate = C["load"](C["HERE"] / "candidate.json.gz")
        cls.rows = C["load"](C["HERE"] / "WINDOWS.json.gz")
        cls.cert = C["load"](C["HERE"] / "CERTIFICATE.json")

    def test_recompressed_candidate_and_census(self):
        with tempfile.TemporaryDirectory() as tmp:
            for i, value in enumerate((self.candidate, self.rows)):
                path = Path(tmp) / (str(i) + ".json.gz")
                path.write_bytes(gzip.compress(C["canonical"](value), compresslevel=1, mtime=987654))
                C["same"](C["load"](path), value, "recompressed payload")
            C["same"](V["reconstruct"](self.parent, self.rows, self.cert["accepted"]),
                      self.candidate, "candidate reconstruction")

    def test_wrong_candidate_destination(self):
        bad = copy.deepcopy(self.candidate)
        bad["A"][0][1] += 1
        with self.assertRaisesRegex(ValueError, "candidate reconstruction"):
            C["same"](V["reconstruct"](self.parent, self.rows, self.cert["accepted"]), bad,
                      "candidate reconstruction")

    def test_census_duplicate(self):
        rows = self.rows + [self.rows[0]]
        with self.assertRaisesRegex(ValueError, "complete window domain"):
            V["verify_windows"](self.parent, rows, b"")

    def test_exaggerated_interval_floor(self):
        with self.assertRaisesRegex(ValueError, "maximum interval saving"):
            V["independent_interval"](self.rows, self.cert["chosen"], self.cert["interval_saving_A"] + 1)

    def test_ceiling_comparison_cannot_use_seven_add_replacement(self):
        index = next(i for i in self.cert["accepted"] if self.rows[i]["distance"] > 6)
        with self.assertRaisesRegex(ValueError, "ineligible interval"):
            V["independent_interval"](self.rows, [index], self.rows[index]["gain"], 6)

    def test_omitted_precision_trial(self):
        bad = copy.deepcopy(self.cert)
        del bad["trials"][0]
        with self.assertRaisesRegex(ValueError, "complete admission order"):
            V["admission"](self.parent, self.candidate, self.rows, bad)

    def test_duplicate_json_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "bad.json"
            p.write_text('{"a":1,"a":2}')
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                C["load"](p)

    def test_nonfinite_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "bad.json"
            p.write_text('{"a":NaN}')
            with self.assertRaisesRegex(ValueError, "nonfinite JSON"):
                C["load"](p)

    def test_missing_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                C["pins"](tmp)

    def test_executable_source_rejected_before_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in C["load"](C["HERE"] / "SOURCES.json")["files"]:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(C["ROOT"] / name, target)
            (root / C["CHECKER"]).write_text('raise RuntimeError("corrupt source must not execute")\n')
            with self.assertRaisesRegex(ValueError, "source hash mismatch"):
                V["run"](root, root / "output")
            self.assertFalse((root / "output").exists())


if __name__ == "__main__":
    unittest.main()
