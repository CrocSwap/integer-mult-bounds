"""Behavioral controls for source authentication and actual cut48 equations."""

import copy
import json
import unittest

from sources import PACKAGE, authenticate
from verify import verify_witness


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = authenticate()
        _, cls.points, cls.labels, _ = cls.g.root_data()
        cls.manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
        cls.witness = json.loads((PACKAGE / "WITNESS.json").read_text())

    def rejects_witness(self, mutate):
        witness = copy.deepcopy(self.witness)
        mutate(witness)
        with self.assertRaises(ValueError):
            verify_witness(self.g, self.points, self.labels, witness)

    def test_actual_cut48(self):
        self.assertEqual(
            verify_witness(self.g, self.points, self.labels, self.witness)[
                "support_union"
            ],
            34,
        )

    def test_wrong_cut_exposes_nonzero_endpoint(self):
        def mutate(w):
            a, b = w["directions"]
            zero = next(
                j
                for j, r in enumerate(self.points)
                if self.g.dot(a, r) == self.g.dot(b, r) == 0
            )
            w["cut"][0] = zero

        self.rejects_witness(mutate)

    def test_wrong_overlap_coefficient(self):
        def mutate(w):
            j = next(
                j
                for j in range(112)
                if w["twice_pieces"][0][j] and w["twice_pieces"][1][j]
            )
            w["twice_pieces"][0][j] *= 2

        self.rejects_witness(mutate)

    def test_missing_live_coefficient(self):
        def mutate(w):
            j = next(j for j, x in enumerate(w["twice_pieces"][2]) if x)
            w["twice_pieces"][2][j] = 0

        self.rejects_witness(mutate)

    def test_proportional_codewords(self):
        self.rejects_witness(
            lambda w: w["directions"].__setitem__(1, w["directions"][0])
        )

    def test_exact_input_usage_inventory(self):
        for path in (
            "research/p112-root-simplex-exclusion/geometry.py",
            "certificates/selected-result.json",
        ):
            manifest = copy.deepcopy(self.manifest)
            row = next(r for r in manifest["files"] if r["path"] == path)
            row["usage"] = "provenance" if row["usage"] == "input" else "input"
            with self.assertRaisesRegex(ValueError, "pin usage"):
                authenticate(manifest)

    def test_missing_duplicate_and_malformed_source(self):
        for mutation in (
            lambda m: m["retained_files"].pop(),
            lambda m: m["files"].append(m["files"][0]),
            lambda m: m["files"][0].update(extra=True),
            lambda m: m["retained_files"][0].update(sha256="0" * 64),
            lambda m: m["retained_files"][0].update(source_commit="0" * 40),
            lambda m: m["retained_files"][0].update(source_path="unrelated/input.py"),
        ):
            manifest = copy.deepcopy(self.manifest)
            mutation(manifest)
            with self.assertRaises(ValueError):
                authenticate(manifest)


if __name__ == "__main__":
    unittest.main()
