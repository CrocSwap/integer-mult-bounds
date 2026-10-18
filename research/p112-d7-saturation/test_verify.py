"""Behavioral controls and a separate full packing oracle."""

import json
import shutil
import tempfile
import unittest
from collections import Counter
from contextlib import redirect_stdout
from io import StringIO
from itertools import combinations
from pathlib import Path

from model import (
    CAP,
    PROFILE,
    application_receipt,
    binary_rank,
    bits,
    boundary_budget,
    frame_receipt,
    packing_receipt,
    saturated_flats,
    survives,
)
from vendor.geometry import root_data
from verify import (
    DATA,
    PACKAGE,
    ROOT,
    bind_data,
    bind_sources,
    check_receipt,
    read_bytes,
)


class SaturationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roots, cls.points, cls.labels, cls.coords = root_data()
        cls.support, cls.frame, cls.full_labels, cls.frames = frame_receipt(
            cls.roots, cls.coords
        )
        cls.saturated, cls.flats = saturated_flats(cls.full_labels, cls.support)
        cls.candidates = tuple(mask for mask in cls.saturated if not mask & cls.frame)

    def test_sharp_packing_with_separate_subset_oracle(self):
        # Enumerate packings by accumulated support with a separate search order.
        stack, counts = [(0, 0, 0)], Counter()
        for _ in range(50_000):
            if not stack:
                break
            first, depth, used = stack.pop()
            counts[depth] += 1
            self.assertLessEqual(depth, 3)
            for j in range(first, len(self.candidates)):
                if not used & self.candidates[j]:
                    stack.append((j + 1, depth + 1, used | self.candidates[j]))
        self.assertFalse(stack)
        self.assertEqual(counts, {0: 1, 1: 756, 2: 16464, 3: 30016})

    def test_actual_support_ranks_and_sharp_witness(self):
        result = packing_receipt(self.candidates)
        self.assertEqual(result["maximum_disjoint"], 3)
        masks = [sum(1 << i for i in indices) for indices in result["witness"]]
        self.assertEqual(sum(masks), masks[0] | masks[1] | masks[2])
        for mask in self.candidates:
            self.assertEqual(
                binary_rank(tuple(self.full_labels[i] for i in bits(mask, 120))), 5
            )

    def test_four_disjoint_supports_rejected(self):
        masks = tuple(((1 << 12) - 1) << (12 * j) for j in range(4))
        with self.assertRaisesRegex(ValueError, "four disjoint"):
            packing_receipt(masks)
        self.assertEqual(packing_receipt(masks[:3])["triangles"], 1)

    def test_no_positive_witness_rejected(self):
        masks = tuple((1 << 11) - 1 | 1 << (11 + j) for j in range(3))
        with self.assertRaisesRegex(ValueError, "no sharp"):
            packing_receipt(masks)

    def test_support_inventory_boundaries(self):
        for masks in ((), (1,), (self.candidates[0],) * 2):
            with self.assertRaises(ValueError):
                packing_receipt(masks)
        with self.assertRaises(ValueError):
            saturated_flats(self.full_labels[:-1], self.support)

    def test_complete_full120_cap_and_frame_binding(self):
        self.assertEqual(self.flats["subspaces"], 3_309_747)
        self.assertEqual(self.flats["maximum"], 12)
        self.assertEqual(len(self.saturated), 5040)
        self.assertEqual(self.frames["orbit_sizes"], [240])
        self.assertEqual(self.frame.bit_count(), 8)
        self.assertEqual((self.support ^ self.frame).bit_count(), 70)

    def test_missing_frame_root_rejected(self):
        with self.assertRaises(ValueError):
            frame_receipt(self.roots[:-1], self.coords[:-1])

    def test_root_simplex_incidence_gate(self):
        # Enumerate six-coordinate equality patterns from the root argument.
        from itertools import product

        maximum = 0
        for values in product(range(3), repeat=6):
            if min(values) != 0:
                continue
            if max(values) == 2 and (values.count(0) != 1 or values.count(2) != 1):
                continue
            unequal = sum(values[i] != values[j] for i, j in combinations(range(6), 2))
            maximum = max(maximum, unequal)
        self.assertEqual(maximum, 9)
        self.assertEqual(15 * 53 - 9 * 46 - 5 * 72, 21)
        self.assertGreaterEqual(9 * 49 + 5 * 72, 15 * 53)

    def test_exact_boundary_and_losing_budgets(self):
        self.assertEqual(boundary_budget(34, 12)["edge_support"], 70)
        for small, endpoint in ((35, 12), (33, 12), (34, 13), (40, 12)):
            with self.assertRaises(ValueError):
                boundary_budget(small, endpoint)

    def test_original_profile_and_strict_cost_control(self):
        bind_sources()
        output = StringIO()
        with redirect_stdout(output):
            from vendor import bk2b

        self.assertEqual(len(output.getvalue().splitlines()), 24)
        self.assertTrue(bk2b.feasible(PROFILE, 5))
        self.assertFalse(bk2b.killed(PROFILE, 5))
        self.assertTrue(survives(PROFILE))
        self.assertFalse(survives((2,) + (5,) * 10))
        result = application_receipt()
        self.assertEqual(result["deficit"], 1)
        self.assertEqual(sum(result["forced_partition"]), 70)
        self.assertEqual(sum(CAP[w] for w in PROFILE[:4]), 34)
        self.assertEqual(result["required_disjoint_saturated_five_flat_supports"], 5)

    def test_six_piece_support_certificate_does_not_cover_target(self):
        capacities = [
            sum(CAP[PROFILE[i]] for i in subset)
            for subset in combinations(range(11), 6)
        ]
        self.assertEqual(len(capacities), 462)
        self.assertEqual(min(capacities), 58)
        self.assertFalse(any(total < 53 for total in capacities))

    def test_input_binding_rejects_changed_payload(self):
        sources = bind_sources()
        self.assertEqual(
            len(bind_data(ROOT / DATA, self.points, self.labels, sources)), 64
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data"
            path.write_bytes(read_bytes(ROOT / DATA) + b"\n")
            with self.assertRaisesRegex(ValueError, "changed P112"):
                bind_data(path, self.points, self.labels, sources)

    def test_retained_source_and_symlink_controls(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            shutil.copytree(PACKAGE / "vendor", package / "vendor")
            shutil.copyfile(PACKAGE / "SOURCES.json", package / "SOURCES.json")
            path = package / "vendor/geometry.py"
            path.parent.chmod(0o700)
            path.chmod(0o600)
            path.write_bytes(path.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "changed retained"):
                bind_sources(package)
            path.unlink()
            path.symlink_to(PACKAGE / "vendor/geometry.py")
            with self.assertRaisesRegex(ValueError, "linked"):
                bind_sources(package)

    def test_receipt_mutation_rejected(self):
        result = json.loads(read_bytes(PACKAGE / "RESULT.json"))
        check_receipt(result, result)
        changed = json.loads(json.dumps(result))
        changed["packing"]["maximum_disjoint"] = 5
        with self.assertRaisesRegex(ValueError, "receipt differs"):
            check_receipt(result, changed)


if __name__ == "__main__":
    unittest.main()
