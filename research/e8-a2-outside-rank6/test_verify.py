"""Behavioral controls for the exact support claim and its source boundary."""

import copy
import json
import runpy
import stat
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
V = runpy.run_path(str(PACKAGE / "verify.py"))


class Controls(unittest.TestCase):
    def test_actual_witness(self):
        r, live, a, _ = V["model"]()
        receipt = json.loads((PACKAGE / "RESULT.json").read_text())
        space = set(V["span"](receipt["witness"]["basis"]))
        self.assertEqual(len(space & r), 20)
        self.assertEqual(len(space & a), 10)
        self.assertTrue(space & r <= live)
        self.assertFalse(space <= set(V["span"](V["basis"](tuple(a)))))

    def test_contained_countercontrol(self):
        r, _, a, _ = V["model"]()
        prior = json.loads((PACKAGE / "vendor/pr3288-RESULT.json").read_text())
        space = set(V["span"](V["basis"](prior["canonical"]["witness_labels"])))
        self.assertEqual(len(space & r) + len(space & a), 32)
        self.assertTrue(space <= set(V["span"](V["basis"](tuple(a)))))

    def test_rank_seven_countercontrol(self):
        r, _, a, _ = V["model"]()
        w = set(V["span"](V["basis"](tuple(a))))
        self.assertEqual(len(w & r) + len(w & a), 55)
        self.assertEqual(len(V["basis"](tuple(w))), 7)

    def test_bad_binary_contracts(self):
        for values in ([True], [-1], [512], [1.0], list(range(513))):
            with self.subTest(values=values[:2]), self.assertRaises(ValueError):
                V["basis"](values)
        with self.assertRaises(ValueError):
            V["span"]((1, 1))

    def test_manifest_types_and_usage(self):
        original = json.loads((PACKAGE / "SOURCES.json").read_text())
        mutations = []
        for key, value in (("schema_version", True), ("schema_version", 1.0)):
            bad = copy.deepcopy(original)
            bad[key] = value
            mutations.append(bad)
        bad = copy.deepcopy(original)
        bad["retained_files"][0]["usage"] = "unused"
        mutations.append(bad)
        bad = copy.deepcopy(original)
        bad["files"].append(copy.deepcopy(bad["files"][0]))
        mutations.append(bad)
        for bad in mutations:
            with self.subTest(manifest=bad), self.assertRaisesRegex(ValueError, "inventory"):
                V["authenticate"](manifest=bad)

    def test_private_source_mutations(self):
        # These copies are private writable regular files, never chmodded sources.
        with tempfile.TemporaryDirectory(prefix="outside-control-") as directory:
            root = Path(directory)
            package = root / "package"
            package.mkdir()
            entries = tuple(PACKAGE.rglob("*"))
            self.assertLessEqual(len(entries), 32)
            for original in entries:
                target = package / original.relative_to(PACKAGE)
                mode = original.lstat().st_mode
                if stat.S_ISDIR(mode):
                    target.mkdir(exist_ok=True)
                else:
                    self.assertTrue(stat.S_ISREG(mode))
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(original.read_bytes())
            source = root / V["GEOMETRY"]
            source.parent.mkdir(parents=True)
            source.write_bytes((V["ROOT"] / V["GEOMETRY"]).read_bytes())
            V["authenticate"](root, package)
            source.write_bytes(source.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "live source hash"):
                V["authenticate"](root, package)
            source.write_bytes((V["ROOT"] / V["GEOMETRY"]).read_bytes())
            retained = package / "vendor/pr3288-PROOF.md"
            retained.write_bytes(retained.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "retained source hash"):
                V["authenticate"](root, package)

    def test_private_link_rejected(self):
        with tempfile.TemporaryDirectory(prefix="outside-link-") as directory:
            path = Path(directory) / "link"
            path.symlink_to(PACKAGE / "SOURCES.json")
            with self.assertRaisesRegex(ValueError, "regular input"):
                V["read_regular"](path)


if __name__ == "__main__":
    unittest.main()
