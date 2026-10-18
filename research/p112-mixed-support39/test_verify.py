"""Export authentication and overlap controls. Nick Petalas. Apache-2.0."""

import copy
import hashlib
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("cut39", PACKAGE / "verify.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("verifier loader")
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


class Controls(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / "research/p112-mixed-support39"
        self.package.mkdir(parents=True)
        self.source = copy.deepcopy(V.EXPECTED_SOURCES)
        for row in self.source["files"]:
            if row["usage"] == "input":
                target = self.root / row["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(V.ROOT / row["path"], target)
        for row in self.source["retained_files"]:
            target = self.package / row["local_path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(PACKAGE / row["local_path"], target)
        self.write_source()

    def write_source(self):
        (self.package / "SOURCES.json").write_text(json.dumps(self.source))

    def test_git_free_exact_inventory(self):
        self.assertFalse((self.root / ".git").exists())
        self.assertEqual(V.authenticate(self.package, self.root), self.source)

    def test_usage_cannot_hide_changed_live_input(self):
        row = next(r for r in self.source["files"] if r["usage"] == "input")
        (self.root / row["path"]).write_text("raise RuntimeError('changed input')\n")
        row["usage"] = "provenance"
        self.write_source()
        with self.assertRaisesRegex(ValueError, "fixed source inventory"):
            V.authenticate(self.package, self.root)

    def test_rehashed_retained_input_cannot_change_premise(self):
        row = self.source["retained_files"][1]
        target = self.package / row["local_path"]
        result = json.loads(target.read_text())
        result["D6"]["axis_maximum_histogram"] = {"19": 896}
        raw = json.dumps(result).encode()
        target.write_bytes(raw)
        row["sha256"] = hashlib.sha256(raw).hexdigest()
        row["git_blob"] = hashlib.sha1(
            b"blob " + str(len(raw)).encode() + b"\0" + raw
        ).hexdigest()
        self.write_source()
        with self.assertRaisesRegex(ValueError, "fixed source inventory"):
            V.authenticate(self.package, self.root)

    def test_malformed_and_extra_inventories(self):
        for mutation in ("extra", "missing", "type", "pin", "bool_schema", "float_pr"):
            with self.subTest(mutation=mutation):
                self.source = copy.deepcopy(V.EXPECTED_SOURCES)
                if mutation == "extra":
                    self.source["retained_files"].append(
                        self.source["retained_files"][0]
                    )
                elif mutation == "missing":
                    self.source["files"].pop()
                elif mutation == "type":
                    self.source["retained_files"] = {}
                elif mutation == "pin":
                    self.source["retained_files"][0]["commit"] = "0" * 40
                elif mutation == "bool_schema":
                    self.source["schema_version"] = True
                else:
                    self.source["retained_files"][0]["pr"] = 3267.0
                self.write_source()
                with self.assertRaisesRegex(ValueError, "fixed source inventory"):
                    V.authenticate(self.package, self.root)

    def test_retained_byte_corruption(self):
        row = self.source["retained_files"][0]
        target = self.package / row["local_path"]
        target.write_bytes(target.read_bytes() + b"changed")
        with self.assertRaisesRegex(ValueError, "SHA256"):
            V.authenticate(self.package, self.root)

    def test_exclusive_cover_allows_overlap(self):
        first, second = set(range(12)), set(range(12, 24))
        third = set(range(24, 42)) | {0, 12}
        union = first | second | third
        exclusive = union - first - second
        self.assertEqual([len(first), len(second), len(third)], [12, 12, 20])
        self.assertEqual([len(union), len(exclusive)], [42, 18])
        self.assertTrue(third & first and third & second)
        # Abstract cardinalities only. This is not a root-code/rank witness.
        self.assertEqual(V.budget(40)["D6_required_union"], len(union))
        self.assertGreater(V.budget(39)["D6_required_union"], len(union))

    def test_unpunctured_capacity_cannot_prove_cut39(self):
        # Full E8 axis capacity20 loses the strict gap, unlike live capacity18.
        self.assertLessEqual(V.budget(39)["D6_required_union"], 12 + 12 + 20)
        for invalid in (-1, 113, True, 39.0):
            with self.assertRaises(ValueError):
                V.budget(invalid)


if __name__ == "__main__":
    unittest.main(verbosity=2)
