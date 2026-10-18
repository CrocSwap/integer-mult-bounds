"""Boundary controls and a separate subset-span capacity check. Apache-2.0."""

import json
import sys
import tempfile
import unittest
from itertools import combinations
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify


def independent_span(vectors):
    values = {0}
    for vector in vectors:
        values |= {x ^ vector for x in tuple(values)}
    return frozenset(values)


def subset_capacity(labels):
    """Every rank-five supported set has a basis among its own labels."""
    if len(labels) != 27 or len(set(labels)) != 27:
        raise ValueError("expected 27 distinct labels")
    inventory = set(labels)
    seen = set()
    maximum = 0
    attempts = 0
    for basis in combinations(labels, 5):
        attempts += 1
        space = independent_span(basis)
        if len(space) == 32 and space not in seen:
            seen.add(space)
            maximum = max(maximum, len(inventory & space))
    if attempts != 80730 or maximum != 10:
        raise ValueError("independent slice capacity differs")
    return attempts, len(seen), maximum


class BoundaryTests(unittest.TestCase):
    def test_output_ownership_and_exclusive_creation(self):
        with self.assertRaisesRegex(ValueError, "external output"):
            verify.write_result(verify.PACKAGE / "forbidden-output.json", {})
        with tempfile.TemporaryDirectory(prefix="a2-output-control-") as directory:
            output = Path(directory) / "receipt.json"
            verify.write_result(output, {"value": 1})
            with self.assertRaises(FileExistsError):
                verify.write_result(output, {"value": 2})
            self.assertEqual(json.loads(output.read_text()), {"value": 1})

    def test_common_support_boundary(self):
        self.assertTrue(verify.support_bound(44)["excluded_by_count"])
        self.assertFalse(verify.support_bound(45)["excluded_by_count"])
        self.assertEqual(verify.support_bound(45)["residual_union_cap"], 33)

    def test_union_only_control(self):
        self.assertTrue(verify.support_bound(41, 12, 12)["excluded_by_count"])
        self.assertFalse(verify.support_bound(42, 12, 12)["excluded_by_count"])
        self.assertFalse(verify.support_bound(44, 13, 10)["excluded_by_count"])

    def test_invalid_support_and_capacity(self):
        for value in (-1, 113, True, "44"):
            with self.assertRaises(ValueError):
                verify.support_bound(value)
        for arguments in ((44, 0, 0), (44, 12, 13), (44, 12, True)):
            with self.assertRaises(ValueError):
                verify.support_bound(*arguments)

    def test_projective_zero_sign_and_scale(self):
        self.assertEqual(verify.projective((0, 0)), (0, 0))
        self.assertEqual(verify.projective((-8, 4)), (2, -1))
        self.assertEqual(verify.projective((16, -8)), (2, -1))
        with self.assertRaises(ValueError):
            verify.projective((1, 2, 3))

    def test_source_drift_rejected(self):
        with tempfile.TemporaryDirectory(prefix="a2-source-control-") as directory:
            root = Path(directory)
            path = root / verify.SOURCE
            path.parent.mkdir(parents=True)
            path.write_bytes((verify.ROOT / verify.SOURCE).read_bytes() + b"\n")
            with (
                patch.object(verify, "ROOT", root),
                self.assertRaisesRegex(ValueError, "source differs"),
            ):
                verify.source_geometry()

    def test_incomplete_slice_rejected(self):
        with self.assertRaisesRegex(ValueError, "27-line"):
            verify.slice_capacity(tuple(range(1, 27)))
        with self.assertRaisesRegex(ValueError, "seven binary"):
            verify.slice_capacity(tuple(range(1, 28)))

    def test_sharp_slice_and_separate_enumeration(self):
        geometry = verify.source_geometry()
        roots, _, _, coordinates = geometry.root_data()
        labels = tuple(
            1 | sum((int(x) % 2) << (i + 1) for i, x in enumerate(row))
            for row in coordinates
        )
        # Find the first root triple directly, without the primary plane census.
        index = {root: i for i, root in enumerate(roots)}
        planes = set()
        for i, j in combinations(range(120), 2):
            pairing = sum(a * b for a, b in zip(roots[i], roots[j], strict=True))
            if abs(pairing) == 4:
                sign = 1 if pairing > 0 else -1
                row = tuple(
                    a - sign * b for a, b in zip(roots[i], roots[j], strict=True)
                )
                if next(x for x in row if x) < 0:
                    row = tuple(-x for x in row)
                planes.add(tuple(sorted((i, j, index[row]))))
        a, b = (roots[i] for i in min(planes)[:2])
        classes = {}
        for row, label in zip(roots, labels, strict=True):
            pair = verify.projective((geometry.dot(a, row), geometry.dot(b, row)))
            classes.setdefault(str(pair), []).append(label)
        receipt = json.loads((verify.PACKAGE / "RESULT.json").read_text())
        for key, expected in receipt["full_e8_projective_slice_capacities"].items():
            candidates = tuple(classes[key])
            self.assertEqual(subset_capacity(candidates)[2], 10)
            witness = expected["witness"]
            self.assertEqual(len(witness), 10)
            self.assertTrue(set(witness) <= set(candidates))
            self.assertEqual(len(independent_span(witness)), 32)
            # Every eleventh line increases this particular witness's rank.
            for label in set(candidates) - set(witness):
                self.assertEqual(len(independent_span((*witness, label))), 64)


if __name__ == "__main__":
    unittest.main(verbosity=2)
