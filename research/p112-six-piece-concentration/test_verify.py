#!/usr/bin/env python3
"""Behavior and failure controls for the six-piece proof certificate."""

import copy
import itertools
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import independent  # noqa: E402
import model  # noqa: E402
import verify  # noqa: E402


def write_fixture(path, data):
    payload = data.encode() if isinstance(data, str) else data
    if path.write_bytes(payload) != len(payload):
        raise OSError("short fixture write")


class ConcentrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g, cls.roots, _, cls.labels, cls.coordinates = model.geometry()
        cls.a, cls.b, cls.fibers = model.canonical_fibers(cls.g, cls.roots)
        cls.expected = model.read_json(HERE / "RESULT.json")

    def test_independent_full_root_and_label_reconstruction(self):
        roots, labels = independent.roots_and_labels()
        self.assertEqual(roots, list(self.roots))
        self.assertEqual(labels, list(self.labels))

    def test_complete_six_dimensional_hyperplane_fixture(self):
        labels, ambient = list(range(1, 64)), [1 << i for i in range(6)]
        observed = list(model.flat_masks(labels, ambient, 5))
        expected = {
            sum(
                1 << i
                for i, value in enumerate(labels)
                if (value & normal).bit_count() % 2 == 0
            )
            for normal in range(1, 64)
        }
        self.assertEqual(len(observed), 63)
        self.assertEqual(set(observed), expected)
        self.assertTrue(all(mask.bit_count() == 31 for mask in observed))

    def test_all_small_generating_spans(self):
        labels = list(range(1, 16))
        for size in range(6):
            for subset in itertools.combinations(labels, size):
                rows = model.basis(subset)
                separate = independent.echelon(subset)
                self.assertEqual(len(rows), len(separate))
                expected = sum(
                    1 << i
                    for i, label in enumerate(labels)
                    if label in model.span(rows)
                )
                self.assertEqual(independent.closure(separate, labels), expected)

    def test_concentration_rejects_leak_and_rank_loss(self):
        axis = next(value for value in self.fibers.values() if len(value) == 33)
        axis_mask = sum(1 << i for i in axis)
        ambient = model.basis([self.labels[i] for i in axis])
        mask = next(
            mask
            for mask in model.flat_masks(self.labels, ambient, 5)
            if (mask & axis_mask).bit_count() >= 10
        )
        model.check_concentration(mask, axis_mask, self.labels, 5)
        outside = next(i for i in range(120) if i not in axis)
        with self.assertRaisesRegex(ValueError, "escapes"):
            model.check_concentration(mask | (1 << outside), axis_mask, self.labels, 5)
        with self.assertRaisesRegex(ValueError, "does not span"):
            model.check_concentration(1 << axis[0], axis_mask, self.labels, 5)

    def test_incidence_and_losing_capacity_controls(self):
        self.assertEqual(model.incidence_certificate(), self.expected["incidence"])
        self.assertEqual(sum(model.incidence_certificate()["excluded_profile"]), 55)
        for capacities in [(8, 13, 12, 12, 20, 20), (8, 12, 12, 12, 21, 20)]:
            with self.assertRaisesRegex(ValueError, "concentration allowance"):
                model.incidence_certificate(capacities)
        for capacities in [(8,), (True, 12, 12, 12, 20, 20), (0, 12, 12, 12, 20, 20)]:
            with self.assertRaisesRegex(ValueError, "capacity bounds"):
                model.incidence_certificate(capacities)

    def test_same_inventory_wrong_weyl_labels(self):
        labels = list(self.labels)
        labels[0], labels[1] = labels[1], labels[0]
        self.assertEqual(len(set(labels)), 120)
        with self.assertRaisesRegex(ValueError, "label linearity"):
            model.reflection_orbit(
                self.g, self.roots, labels, self.coordinates, (self.a, self.b)
            )

    def test_geometry_source_corruption(self):
        with tempfile.TemporaryDirectory(prefix="six-piece-source-") as directory:
            path = Path(directory) / "geometry.py"
            write_fixture(path, model.SOURCE.read_bytes() + b"\n# changed\n")
            with (
                patch.object(model, "SOURCE", path),
                self.assertRaisesRegex(ValueError, "source hash"),
            ):
                model.geometry()

    def test_predecessor_bytes_and_usage(self):
        with tempfile.TemporaryDirectory(prefix="six-piece-context-") as directory:
            root = Path(directory)
            (root / "predecessors").mkdir()
            manifest = model.read_json(HERE / "PREDECESSORS.json")
            for row in manifest["files"]:
                name = row["retained_path"]
                write_fixture(root / name, (HERE / name).read_bytes())
            path = root / "PREDECESSORS.json"
            write_fixture(path, json.dumps(manifest))
            verify.authenticate_predecessors(root)
            origin = manifest["files"][0]["source_path"]
            manifest["files"][0]["source_path"] = "wrong/PROOF.md"
            write_fixture(path, json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "pin and usage"):
                verify.authenticate_predecessors(root)
            manifest["files"][0]["source_path"] = origin
            manifest["files"][0]["usage"] = "caller-context"
            write_fixture(path, json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "pin and usage"):
                verify.authenticate_predecessors(root)
            manifest["files"][0]["usage"] = "inherited-premises"
            write_fixture(path, json.dumps(manifest))
            write_fixture(
                root / manifest["files"][0]["retained_path"], b"changed proof"
            )
            with self.assertRaisesRegex(ValueError, "predecessor bytes"):
                verify.authenticate_predecessors(root)

    def test_json_capacity_and_duplicate_key(self):
        with tempfile.TemporaryDirectory(prefix="six-piece-json-") as directory:
            path = Path(directory) / "input.json"
            for data in ['{"a":1,"a":2}', " " * 262145]:
                write_fixture(path, data)
                for reader in (model.read_json, independent.load):
                    with self.assertRaises(ValueError):
                        reader(path)

    def test_actual_result_boundary(self):
        changed = copy.deepcopy(self.expected)
        changed["incidence"]["retained_code_dimension"] = 1
        with (
            patch.object(sys, "argv", ["verify.py"]),
            patch.object(verify, "authenticate_predecessors", return_value=None),
            patch.object(model, "result", return_value=self.expected),
            patch.object(model, "read_json", return_value=changed),
            self.assertRaisesRegex(ValueError, "result differs"),
        ):
            verify.main()


if __name__ == "__main__":
    unittest.main(verbosity=2)
