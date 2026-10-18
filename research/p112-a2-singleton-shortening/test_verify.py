"""Mathematical fixtures and failure controls for the public A2 contract."""

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))

import independent_check as independent
import model
import verify
from vendor.geometry import root_data


class A2Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roots, cls.points, cls.labels, cls.coordinates = root_data()
        cls.full_labels = tuple(
            1 | sum((int(x) % 2) << (i + 1) for i, x in enumerate(c))
            for c in cls.coordinates
        )
        cls.classes, cls.doubles = model.singleton_classes(cls.roots)
        cls.expected = json.loads((PACKAGE / "RESULT.json").read_bytes())

    def test_actual_deletion_contract(self):
        row = model.application()
        self.assertEqual(row["retained_weights"], (2, 2, 2, 5, 6, 6, 6))
        self.assertEqual(
            (
                row["retained_code_dimension_lower"],
                row["common_support_cap"],
                row["basis_support_cap"],
                row["edge_support_cap"],
            ),
            (2, 18, 38, 58),
        )
        self.assertEqual(
            (row["endpoint_lower"], row["endpoint_allowance"], row["margin"]),
            (68, 60, 8),
        )

    def test_dimension_and_deletion_guards(self):
        for dimension, deleted in ((5, 4), (6, 5), (6, 3), (True, 4)):
            with (
                self.subTest(dimension=dimension, deleted=deleted),
                self.assertRaises(ValueError),
            ):
                model.application(dimension, deleted)

    def test_support_threshold_and_losing_controls(self):
        self.assertEqual(model.support_lower(21), 62)
        self.assertEqual(model.support_lower(22), 60)
        self.assertLessEqual(model.support_lower(21, singleton_cap=17), 60)
        self.assertLessEqual(model.support_lower(21, punctures=9), 60)
        for common in (-1, 30, True):
            with self.assertRaises(ValueError):
                model.support_lower(common)

    def test_singleton_geometry(self):
        self.assertEqual([s.bit_count() for s in self.classes], [27, 27, 27])
        self.assertEqual(self.doubles.bit_count(), 3)
        self.assertEqual(sum(self.classes).bit_count(), 81)
        with self.assertRaises(ValueError):
            model.singleton_classes(self.roots[:-1])

    def test_hyperplane_cap_and_missing_label_rejection(self):
        reports = model.singleton_hyperplane_receipt(self.full_labels, self.classes)
        self.assertEqual([r["maximum"] for r in reports], [16] * 3)
        self.assertEqual([r["span_rank"] for r in reports], [7] * 3)
        self.assertEqual(
            reports[0]["histogram"], {0: 1, 11: 27, 12: 36, 15: 36, 16: 27}
        )
        bad = self.full_labels[:-1] + (self.full_labels[0],)
        with self.assertRaises(ValueError):
            model.singleton_hyperplane_receipt(bad, self.classes)

    def test_binary_ranks_and_transported_spans(self):
        self.assertEqual(model.binary_rank((1, 2, 3, 4)), 3)
        columns = self.expected["original_label_binding"]["binary_map_columns"]
        self.assertEqual(model.binary_rank(columns), 9)
        with self.assertRaises(ValueError):
            model.binary_rank((512,))

    def test_all_root_pairs_and_wrong_star_rejection(self):
        _, transport = model.transport_receipt(self.roots, self.coordinates)
        self.assertEqual(transport["ordered_pairs"], 13440)
        with (
            patch.object(model, "STAR", (model.STAR[0], model.STAR[0])),
            self.assertRaises(ValueError),
        ):
            model.transport_receipt(self.roots, self.coordinates)

    def test_nonmodal_shifts_are_not_dropped(self):
        values, shift = (0, 0, 1), -1
        support = tuple(v + shift != 0 for v in values)
        self.assertEqual(support, (True, True, False))
        self.assertEqual(sum(support), 2 - support[2])
        self.assertEqual(independent.shift_controls(), 1125)

    def test_independent_generated_span_and_real_attainment(self):
        roots, labels = independent.root_labels()
        classes = independent.independent_classes(roots, labels)
        result = independent.generated_span_cap(classes[0])
        self.assertEqual(
            (result["six_label_tuples"], result["generated_spans"]), (296010, 3189)
        )
        self.assertEqual((result["maximum"], result["maximizers"]), (16, 27))
        self.assertEqual(
            result["maximizer_sha256"],
            self.expected["singleton_hyperplanes"][0]["maximizer_sha256"],
        )
        with self.assertRaises(ValueError):
            independent.generated_span_cap(classes[0][:-1])

    def test_changed_original_label_map_is_rejected(self):
        sources = verify.bind_sources()
        by_root = dict(zip(self.roots, self.full_labels, strict=True))
        columns = self.expected["original_label_binding"]["binary_map_columns"]
        self.assertEqual(
            independent.original_caller_binding(sources, by_root, columns), 112
        )
        for changed in (columns[:-1], [0] + columns[1:], list(reversed(columns))):
            with self.assertRaises(ValueError):
                independent.original_caller_binding(sources, by_root, changed)

    def test_source_pin_and_corrupt_retained_bytes(self):
        self.assertEqual(len(verify.bind_sources()["retained_files"]), 3)
        with tempfile.TemporaryDirectory() as scratch:
            package = Path(scratch)
            shutil.copyfile(PACKAGE / "SOURCES.json", package / "SOURCES.json")
            shutil.copytree(PACKAGE / "vendor", package / "vendor")
            target = package / "vendor/geometry.py"
            target.chmod(target.stat().st_mode | 0o200)  # Only the private mutant copy.
            target.write_bytes(target.read_bytes() + b"\n# altered retained bytes\n")
            with self.assertRaises(ValueError):
                verify.bind_sources(package)

    def test_semantic_receipt_mutants_are_rejected(self):
        verify.check_receipt(self.expected, copy.deepcopy(self.expected))
        mutants = []
        for key, value in (
            ("margin", 0),
            ("deleted_pieces", 3),
            ("endpoint_lower", 60),
        ):
            changed = copy.deepcopy(self.expected)
            changed["application"][key] = value
            mutants.append(changed)
        changed = copy.deepcopy(self.expected)
        changed["singleton_hyperplanes"][0]["maximum"] = 17
        mutants.append(changed)
        for mutant in mutants:
            with self.assertRaises(ValueError):
                verify.check_receipt(self.expected, mutant)

    def test_cli_rejects_unsafe_outputs_without_writing(self):
        with tempfile.TemporaryDirectory() as scratch:
            existing = Path(scratch) / "existing.json"
            existing.write_text("preserve me", encoding="utf-8")
            for args in (
                ("--unknown",),
                ("--output", str(existing)),
                ("--output", str(PACKAGE / "forbidden.json")),
            ):
                result = subprocess.run(
                    [sys.executable, "-I", "-B", str(PACKAGE / "verify.py"), *args],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
            self.assertEqual(existing.read_text(encoding="utf-8"), "preserve me")
            self.assertFalse((PACKAGE / "forbidden.json").exists())


if __name__ == "__main__":
    unittest.main()
