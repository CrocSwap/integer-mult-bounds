"""Behavioral and rejection controls for the scoped P112 exclusion."""

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from itertools import combinations
from pathlib import Path

from bound import (
    PROFILE,
    application,
    frame_inventory,
    frame_orbits,
    mixed_seven,
    pair_bound,
    reflection_permutations,
    root_types,
    selected_flats,
    weight,
)
from independent import binary_basis, generated_flats, span, split_six
from vendor.geometry import frame_lines, require, root_data
from vendor.mixed import alphabet, compatibility, intersections
from verify import (
    DATA,
    PACKAGE,
    ROOT,
    bind_data,
    bind_sources,
    check_receipt,
    full_labels,
    read_bytes,
)


class WeightedFlatTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roots, cls.points, cls.labels, coordinates = root_data()
        cls.full = full_labels(coordinates)
        cls.prefixes, cls.costs, _ = root_types(cls.roots)
        cls.selected, _, _ = generated_flats(cls.full, cls.costs[1])
        cls.frames, _ = frame_inventory(cls.roots)
        cls.permutations = reflection_permutations(
            cls.roots, cls.prefixes[1], cls.costs[1]
        )
        cls.orbits = frame_orbits(cls.frames, cls.permutations)
        cls.high = sum(1 << i for i, cost in enumerate(cls.costs[1]) if cost == 4)
        cls.zero = sum(1 << i for i, cost in enumerate(cls.costs[1]) if cost == 0)
        directions, _, _ = alphabet(cls.roots, cls.points)
        cls.vertices = intersections(directions)
        cls.adjacency = compatibility(cls.vertices, directions)

    def test_actual_original_profile(self):
        actual = application()
        self.assertEqual(tuple(actual["profile"]), PROFILE)
        self.assertEqual(actual["original_survivors"], 154)
        self.assertEqual(actual["allowance"] + actual["margin"], 162)

    def test_mixed_positive_and_independent_cliques(self):
        result = mixed_seven(self.vertices, self.adjacency, self.points)
        self.assertEqual(result["minimum"], 162)
        self.assertEqual(sum(result["ranks"].values()), len(split_six(self.adjacency)))

    def test_missing_edge_rejects(self):
        adjacency = list(self.adjacency)
        i = next(i for i, row in enumerate(adjacency) if row)
        j = (adjacency[i] & -adjacency[i]).bit_length() - 1
        adjacency[i] &= ~(1 << j)
        adjacency[j] &= ~(1 << i)
        with self.assertRaisesRegex(ValueError, "census"):
            mixed_seven(self.vertices, tuple(adjacency), self.points)

    def test_arbitrary_deletions_are_a_losing_control(self):
        self.assertEqual(sum(sorted(self.costs[1])[:80]), 158)
        self.assertLessEqual(158, application()["allowance"])
        self.assertEqual(sum(sorted(self.costs[0])[:80]), 168)

    def test_all_frame_orbits_and_pair_witnesses(self):
        self.assertEqual(sum(n for _, n in self.orbits), 2025)
        for frame, _ in self.orbits:
            result = pair_bound(frame, self.selected, self.high, self.zero)
            if result["frame_cost"] != 16:
                a, b = result["pair_witness"]
                self.assertEqual(
                    weight(a | b, self.high, self.zero), result["pair_maximum"]
                )
                self.assertLess(result["high_case_loss_upper"], 148)

    def test_planted_large_cover_rejects(self):
        frame = next(
            f for f, _ in self.orbits if sum(self.costs[1][i] for i in f) == 24
        )
        with self.assertRaisesRegex(ValueError, "does not exclude"):
            pair_bound(frame, ((1 << 120) - 1,), self.high, self.zero)

    def test_invalid_flat_inputs_reject(self):
        with self.assertRaisesRegex(ValueError, "label inventory"):
            selected_flats(self.full[:-1], self.costs[1])
        with self.assertRaisesRegex(ValueError, "cost inventory"):
            selected_flats(self.full, (2,) * 120)

    def test_invalid_frame_inventory_rejects(self):
        with self.assertRaisesRegex(ValueError, "root count"):
            frame_inventory(self.roots[:-1])

    def test_binary_basis_against_xor_closure(self):
        for count in range(1, 5):
            for chosen in combinations(range(1, 16), count):
                closure = {0}
                for value in chosen:
                    closure |= {x ^ value for x in tuple(closure)}
                basis = binary_basis(chosen)
                self.assertEqual(set(span(basis)), closure)
                self.assertEqual(basis, binary_basis(tuple(reversed(chosen))))
        with self.assertRaisesRegex(ValueError, "basis input"):
            binary_basis((512,))
        with self.assertRaisesRegex(ValueError, "dependent"):
            span((1, 1))

    def test_retained_bytes_and_changed_source(self):
        self.assertEqual(len(bind_sources()["retained_files"]), 8)
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "package"
            (package / "vendor").mkdir(parents=True)
            names = ["SOURCES.json"] + [
                row["local_path"] for row in bind_sources()["retained_files"]
            ]
            for name in names:
                shutil.copyfile(PACKAGE / name, package / name)
            path = package / "vendor/mixed.py"
            path.write_bytes(path.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "changed retained"):
                bind_sources(package)

    def test_removed_source_pin_rejects(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            sources = json.loads(read_bytes(PACKAGE / "SOURCES.json"))
            sources["retained_files"].pop()
            (package / "SOURCES.json").write_text(json.dumps(sources))
            with self.assertRaisesRegex(ValueError, "source inventory"):
                bind_sources(package)

    def test_live_input_hash_and_semantic_controls(self):
        sources = bind_sources()
        self.assertEqual(
            bind_data(ROOT / DATA, self.points, self.labels, sources),
            hashlib.sha256(read_bytes(ROOT / DATA)).hexdigest(),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.txt"
            raw = read_bytes(ROOT / DATA)
            path.write_bytes(raw + b"\n")
            with self.assertRaisesRegex(ValueError, "changed P112"):
                bind_data(path, self.points, self.labels, sources)
            path.write_bytes(raw)
            with self.assertRaisesRegex(ValueError, "label order"):
                bind_data(path, self.points, tuple(reversed(self.labels)), sources)
            with self.assertRaisesRegex(ValueError, "root order"):
                bind_data(path, tuple(reversed(self.points)), self.labels, sources)

    def test_receipt_mutation_rejects(self):
        expected = json.loads(read_bytes(PACKAGE / "RESULT.json"))
        changed = copy.deepcopy(expected)
        changed["exceptional"]["surviving_lower"] = 160
        with self.assertRaisesRegex(ValueError, "receipt differs"):
            check_receipt(changed, expected)
        check_receipt(expected, expected)
        check_receipt({"counts": {2: 3, 10: 4}}, {"counts": {"10": 4, "2": 3}})

    def test_missing_and_linked_inputs_reject(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing"
            with self.assertRaisesRegex(ValueError, "missing, linked"):
                read_bytes(path)
            path.symlink_to(PACKAGE / "RESULT.json")
            with self.assertRaisesRegex(ValueError, "missing, linked"):
                read_bytes(path)

    def test_frame_preserves_the_puncture_control(self):
        frame = frame_lines()
        self.assertEqual(len(frame), 8)
        self.assertEqual(set(frame) | set(self.points), set(self.roots))
        self.assertTrue(
            all(
                sum(x * y for x, y in zip(a, b, strict=True)) == 0
                for a, b in combinations(frame, 2)
            )
        )

    def test_guards_remain_active_under_optimization(self):
        with self.assertRaisesRegex(ValueError, "deliberate invalid premise"):
            require(False, "deliberate invalid premise")


if __name__ == "__main__":
    unittest.main()
