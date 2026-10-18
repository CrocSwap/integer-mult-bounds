"""Behavioral controls for the finite census, source binding and cut boundary."""

import copy
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import domain
import reference
import verify


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = domain.geometry()
        cls.roots, cls.points, cls.labels, coordinates = cls.g.root_data()
        cls.flats = domain.seven_flats(cls.labels)
        _, cls.supports, _ = domain.directions(
            cls.g, cls.roots, cls.points, coordinates
        )
        cls.expected = json.loads((domain.PACKAGE / "RESULT.json").read_text())
        cls.reps = tuple(int(x) for x in cls.expected["representative_masks"])
        cls.witness = json.loads((domain.PACKAGE / "WITNESS.json").read_text())

    def check_witness(self, witness):
        return verify.check_witness(
            witness, self.g, self.roots, self.points, self.labels
        )

    def census_text(self):
        lines = []
        for f, (maximum, entries) in enumerate(self.expected["classes"]):
            lines.append(f"F {f} {maximum}")
            for h, k, cut in entries:
                lines.append(f"C {h} {k} {verify.encode_mask(int(cut))}")
        return "\n".join(lines) + "\n"

    def parse(self, text):
        return verify.parse_census(text, self.flats, self.reps, self.supports)

    def test_positive_six_and_five_boundary(self):
        self.assertEqual(self.check_witness(self.witness)["gram_determinant"], 512)
        result = verify.common_cut_bound(self.expected["classes"])
        self.assertEqual(result["maximum_directions_with_five_common_cuts"], 2)
        self.assertEqual(result["compatible_distinct_direction_pairs"], 28)

    def test_missing_common_coordinate(self):
        witness = copy.deepcopy(self.witness)
        witness["common_deleted_lines"][0] = 0
        with self.assertRaisesRegex(ValueError, "common cuts"):
            self.check_witness(witness)

    def test_dependent_triple(self):
        witness = copy.deepcopy(self.witness)
        witness["directions"][2] = copy.deepcopy(witness["directions"][0])
        with self.assertRaisesRegex(ValueError, "independent root triple"):
            self.check_witness(witness)

    def test_separate_cuts_do_not_imply_common_five(self):
        self.assertTrue(
            all(len(row["deleted_lines"]) <= 5 for row in self.witness["directions"])
        )
        witness = copy.deepcopy(self.witness)
        witness["common_deleted_lines"].pop()
        with self.assertRaisesRegex(ValueError, "six common cuts"):
            self.check_witness(witness)

    def test_annihilator_must_be_independent(self):
        for rows in ([0, 65], [65, 65], [65, 512]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                domain.flat_mask(self.labels, rows)

    def test_binary_rank_and_input_capacity(self):
        self.assertEqual(domain.binary_rank(tuple(1 << i for i in range(9))), 9)
        for columns in ((0,), (512,), (True,), tuple([1] * 113)):
            with self.subTest(columns=columns), self.assertRaises(ValueError):
                domain.binary_rank(columns)

    def test_common_five_counterexample_is_rejected(self):
        fake = [[68, [[0, 0, "3"], [1, 1, "5"], [2, 2, "6"]]]]
        with self.assertRaisesRegex(ValueError, "three directions"):
            verify.common_cut_bound(fake)
        with self.assertRaisesRegex(ValueError, "common-five bound failed"):
            reference.common_five_bound(fake)

    def test_complete_census_round_trip(self):
        text = self.census_text()
        self.assertEqual(
            hashlib.sha256(text.encode()).hexdigest(), self.expected["census_sha256"]
        )
        self.assertEqual(self.parse(text), self.expected["classes"])

    def test_bad_cut_and_duplicate_cut(self):
        text = self.census_text()
        lines = text.splitlines()
        index = next(i for i, line in enumerate(lines) if line.startswith("C "))
        fields = lines[index].split()
        fields[3] = str(int(fields[3]) ^ 1)
        changed = lines.copy()
        changed[index] = " ".join(fields)
        with self.assertRaisesRegex(ValueError, "cut predicate"):
            self.parse("\n".join(changed))
        lines.insert(index, lines[index])
        with self.assertRaisesRegex(ValueError, "duplicate cut"):
            self.parse("\n".join(lines))

    def test_missing_flat_and_false_union_cap(self):
        text = self.census_text()
        with self.assertRaisesRegex(ValueError, "coverage"):
            self.parse(text[: text.rfind("F 120 ")])
        with self.assertRaisesRegex(ValueError, "union exceeds"):
            self.parse(text.replace("F 0 36", "F 0 69", 1))

    def test_source_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / domain.GEOMETRY_PATH
            target.parent.mkdir(parents=True)
            target.write_text("raise RuntimeError('must not execute')\n")
            with (
                patch.object(domain, "ROOT", root),
                self.assertRaisesRegex(ValueError, "source changed"),
            ):
                domain.geometry()

    def test_orbit_exhaustion_and_escaped_trace(self):
        table = (((0, 2) + (0,) * 254),)
        with self.assertRaisesRegex(ValueError, "capacity"):
            domain.mask_orbit(1, (table,), 1)
        with self.assertRaisesRegex(ValueError, "left its domain"):
            domain.mask_orbit(1, (table,), 4, {1})

    def test_compiled_census_mutants(self):
        source = (domain.PACKAGE / "census.cpp").read_text()
        data = verify.census_input(self.flats, self.reps, self.supports)
        for bound in (4, 6):
            with self.subTest(bound=bound), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                mutant = source.replace(
                    "if (size(cut) <= 5)", f"if (size(cut) <= {bound})"
                )
                self.assertNotEqual(source, mutant)
                (root / "census.cpp").write_text(mutant)
                with patch.object(verify, "PACKAGE", root):
                    output = verify.execute_census(
                        data, os.environ.get("TMPDIR"), "c++"
                    )
                with self.assertRaisesRegex(ValueError, "receipt changed"):
                    domain.require(output == self.census_text(), "receipt changed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
