"""Behavioral controls for coefficient and authenticated-export failures."""

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import independent
import verify
from sources import GEOMETRY, PACKAGE, ROOT, authenticate, load_geometry, read_json


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.geometry = load_geometry()
        cls.witness = read_json(PACKAGE / "WITNESS.json")

    def test_actual_witness(self):
        result = verify.verify(self.witness, self.geometry)
        self.assertEqual(result, read_json(PACKAGE / "RESULT.json"))
        self.assertEqual(independent.check(self.witness)["union"], 44)

    def test_cut_mutations(self):
        for cut in (self.witness["cut"][:-1], [self.witness["cut"][0]] * 40):
            changed = copy.deepcopy(self.witness)
            changed["cut"] = cut
            with self.assertRaises(ValueError):
                verify.verify(changed, self.geometry)

    def test_nonzero_wrong_coefficient(self):
        changed = copy.deepcopy(self.witness)
        j = next(j for j, x in enumerate(changed["pieces"][0]) if x)
        changed["pieces"][0][j] *= -1
        with self.assertRaisesRegex(ValueError, "first codeword"):
            verify.verify(changed, self.geometry)
        with self.assertRaisesRegex(ValueError, "first codeword"):
            independent.check(changed)

    def test_false_rank5_relabel(self):
        roots, points, labels, _ = self.geometry.root_data()
        support = [labels[j] for j, x in enumerate(self.witness["pieces"][2]) if x]
        self.assertEqual(verify.binary_rank(support), 6)
        self.assertEqual(independent.span_size(support), 64)
        self.assertEqual(len(roots) - len(points), 8)

    def test_dependent_directions(self):
        changed = copy.deepcopy(self.witness)
        changed["directions"][1] = changed["directions"][0]
        with self.assertRaisesRegex(ValueError, "orthogonal roots"):
            verify.verify(changed, self.geometry)

    def test_source_inventory_and_corruption(self):
        with tempfile.TemporaryDirectory(prefix="mixed-cut40-") as directory:
            root = Path(directory)
            package = root / "research/p112-mixed-sharp39"
            shutil.copytree(PACKAGE, package, copy_function=shutil.copyfile)
            target = root / GEOMETRY
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / GEOMETRY, target)
            authenticate(package, root)
            manifest = read_json(package / "SOURCES.json")
            for mode in ("relabel", "extra", "schema", "boolean-schema"):
                changed = copy.deepcopy(manifest)
                if mode == "relabel":
                    changed["files"][2]["usage"] = "provenance"
                    target.write_text("changed executable input\n")
                elif mode == "extra":
                    changed["files"].append(changed["files"][0])
                elif mode == "schema":
                    changed["schema_version"] = 2
                else:
                    changed["schema_version"] = True
                (package / "SOURCES.json").write_text(json.dumps(changed))
                with self.assertRaisesRegex(ValueError, "fixed source inventory"):
                    authenticate(package, root)
            (package / "SOURCES.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "source SHA256"):
                authenticate(package, root)


if __name__ == "__main__":
    unittest.main()
