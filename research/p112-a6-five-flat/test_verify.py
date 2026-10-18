"""Behavioral controls for the affine transfer and its source bindings."""

import copy
import json
import shutil
import tempfile
import unittest
from itertools import combinations
from pathlib import Path
from unittest.mock import patch

import cover_transfer as transfer
import verify
from vendor.geometry import root_data


class TransferTests(unittest.TestCase):
    def test_all_subsets_and_boundary(self):
        result = transfer.exhaustive_transfer()
        self.assertEqual(result["admissible_subsets"], 64839)
        self.assertEqual(result["errors"], 0)
        self.assertEqual(result["thirteen_point_controls"], 560)

    def test_twelve_points_need_four_extras(self):
        mask = (1 << 12) - 1
        half, extra = transfer.cover(mask)
        self.assertEqual(extra.bit_count(), 4)
        self.assertEqual(mask & ~(half | extra), 0)
        self.assertEqual(min((mask & ~h).bit_count() for h in transfer.hyperplanes()), 4)

    def test_empty_and_singleton(self):
        for mask in (0, 1, 1 << 15):
            half, extra = transfer.cover(mask)
            self.assertEqual(mask & ~(half | extra), 0)
            self.assertLessEqual(extra.bit_count(), 1)

    def test_invalid_supports_reject(self):
        for mask in (-1, 1 << 16, True, 1.0, (1 << 13) - 1):
            with self.subTest(mask=mask), self.assertRaises(ValueError):
                transfer.cover(mask)

    def test_binary_rank_domain(self):
        self.assertEqual(transfer.binary_rank((1, 2, 4, 8, 16)), 5)
        self.assertEqual(transfer.binary_rank((1, 2, 3)), 2)
        for rows in ((-1,), (32,), (True,), (0,) * 17):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                transfer.binary_rank(rows)

    def test_noncoordinate_embedding(self):
        # An injective affine map of the four-cube into the nine-bit odd half.
        origin, directions = 33, (258, 68, 136, 48)
        for half in transfer.hyperplanes():
            labels = []
            for x in range(16):
                if half >> x & 1:
                    label = origin
                    for i in range(4):
                        if x >> i & 1:
                            label ^= directions[i]
                    labels.append(label)
            basis = {}
            for label in labels:
                for bit in range(8, -1, -1):
                    if label >> bit & 1:
                        if bit in basis:
                            label ^= basis[bit]
                        else:
                            basis[bit] = label
                            break
            self.assertEqual(len(basis), 4)
            self.assertTrue(all(label & 1 for label in labels))

    def test_hyperplane_oracle_uses_all_normals(self):
        planes = transfer.hyperplanes()
        self.assertEqual(set(planes), {transfer.ALL ^ h for h in planes})
        self.assertEqual(len(planes), 30)
        self.assertTrue(all(h.bit_count() == 8 for h in planes))


class BindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roots, cls.points, cls.labels, _ = root_data()
        cls.sources = verify.bind_sources()

    def test_actual_pins(self):
        self.assertEqual(len(self.sources["retained_files"]), 10)
        self.assertEqual(verify.bind_data(verify.ROOT / verify.DATA, self.points,
                                        self.labels, self.sources),
                         self.sources["files"][2]["sha256"])

    def test_changed_source_rejects(self):
        with tempfile.TemporaryDirectory(prefix="source-mutant-") as name:
            package = Path(name) / "package"
            shutil.copytree(verify.PACKAGE / "vendor", package / "vendor")
            shutil.copyfile(verify.PACKAGE / "SOURCES.json", package / "SOURCES.json")
            source = package / "vendor/geometry.py"
            source.chmod(0o600)  # Only this disposable copy must be mutable.
            source.write_bytes(source.read_bytes() + b"\n# mutant\n")
            with patch.object(verify, "PACKAGE", package), self.assertRaises(ValueError):
                verify.bind_sources()

    def test_changed_input_rejects(self):
        with tempfile.TemporaryDirectory(prefix="input-mutant-") as name:
            source = Path(name) / "data.txt"
            source.write_bytes((verify.ROOT / verify.DATA).read_bytes() + b"mutant")
            with self.assertRaises(ValueError):
                verify.bind_data(source, self.points, self.labels, self.sources)

    def test_missing_and_linked_inputs_reject(self):
        with tempfile.TemporaryDirectory(prefix="missing-input-") as name:
            source = Path(name) / "input"
            with self.assertRaises(ValueError):
                verify.read_bytes(source)
            source.symlink_to(verify.PACKAGE / "RESULT.json")
            with self.assertRaises(ValueError):
                verify.read_bytes(source)

    def test_receipt_change_rejects(self):
        result = json.loads(verify.read_bytes(verify.PACKAGE / "RESULT.json"))
        verify.check_receipt(result, copy.deepcopy(result))
        mutant = copy.deepcopy(result)
        mutant["cover_transfer"]["maximum_extra"] = 3
        with self.assertRaises(ValueError):
            verify.check_receipt(result, mutant)

    def test_actual_profile_and_predecessor_cell(self):
        actual = verify.application()
        self.assertEqual(actual["weights"], (5,) + (6,) * 8)
        self.assertEqual(actual["quotient_basis_cap"], 52)
        self.assertEqual(actual["endpoint_allowance"], 140)
        self.assertEqual(len(actual["original_no_seven_profiles"]), 6)
        self.assertEqual(verify.predecessor_table()[8][2], 17)

    def test_only_rank_five_rank_six_quotient_basis(self):
        choices = set(combinations(verify.PROFILE, 3))
        certified = [row for row in choices if sum(verify.CAP[w] for w in row) < 53]
        self.assertEqual(certified, [(5, 6, 6)])
        # Both whole six-flats leave the five-piece's twelve-coordinate cap.
        self.assertEqual(verify.CAP[5], 12)
        self.assertGreater(verify.CAP[5], 10)


if __name__ == "__main__":
    unittest.main()
