"""Behavioral and corruption controls; run with Python optimization enabled."""

import copy
import hashlib
import json
import os
import tempfile
import unittest
from collections import Counter
from itertools import combinations, product
from pathlib import Path

import bound
import independent
import independent_weighted
import verify
import weighted
from vendor.geometry import dot, root_data
from vendor.mixed import (
    ANCHOR,
    alphabet,
    cliques,
    compatibility,
    intersections,
    rational_rank,
)


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roots, cls.points, cls.labels, cls.coordinates = root_data()
        cls.directions, _, _ = alphabet(cls.roots, cls.points)
        cls.vertices = intersections(cls.directions)
        cls.adjacency = compatibility(cls.vertices, cls.directions)
        cls.root_result = bound.all_root_six(cls.roots)
        star = cls.root_result["representative"]
        cls.costs = tuple(7 - max(Counter((0, *(dot(r, v) for v in star))).values())
                          for r in cls.roots)
        cls.layers = weighted.cost_layers(cls.costs)
        cls.full_labels = weighted.full_labels(cls.coordinates)
        cls.six, _ = weighted.selected_six_flats(cls.full_labels, cls.layers)
        cls.four = weighted.high_four_flats(cls.full_labels, cls.layers)
        cls.frames = weighted.frame_inventory(cls.roots)
        cls.sources = verify.bind_sources()

    def test_literal_source_translation(self):
        digest = verify.bind_data(verify.ROOT / verify.DATA, self.points, self.labels, self.sources)
        self.assertEqual(digest, "ac4a48851b922f2a433684b60c74768ae3bb4fc5e8990ffe63e3942bb3c2ea34")
        self.assertEqual(weighted.label_reflections(self.roots, self.full_labels), 960)

    def test_actual_profile_and_old_cover_boundary(self):
        result = bound.application()
        self.assertEqual(result["weights"], (3, 4) + (6,) * 8)
        self.assertEqual(result["original_survivors"], 69)
        bases = {basis for basis in combinations(bound.PROFILE, 4)
                 if sum(bound.CAP[w] for w in basis) < 53}
        self.assertEqual(bases, {(3, 4, 6, 6)})
        basis = (3, 4, 6, 6)
        cuts = [sum(bound.CAP[w] for w, g in zip(basis, assignment, strict=True) if g == 2)
                for assignment in product(range(3), repeat=4)
                if all(sum(w for w, g in zip(basis, assignment, strict=True) if g == group) <= 6
                       for group in (0, 1))]
        self.assertEqual(min(cuts), 12)
        nonbasis = list(bound.PROFILE)
        for weight in basis:
            nonbasis.remove(weight)
        self.assertEqual(nonbasis, [6] * 6)

    def test_alphabet_truncation_is_rejected(self):
        with self.assertRaises(ValueError):
            intersections(self.directions[:-1])
        with self.assertRaises(ValueError):
            alphabet(self.roots[:-1], self.points)

    def test_independent_intersections_and_graph(self):
        directions = independent.direction_inventory()
        vertices = independent.gram_vertices(directions)
        self.assertEqual(vertices, self.vertices)
        self.assertEqual(independent.graph(vertices, directions), self.adjacency)
        with self.assertRaises(ValueError):
            independent.gram_vertices(directions[:-1])

    def test_complete_clique_sets_agree(self):
        primary = set(cliques(self.adjacency, 5))
        alternate = set(independent.split_cliques(self.adjacency))
        self.assertEqual(primary, alternate)
        self.assertEqual(len(primary), 7350)
        with self.assertRaises(ValueError):
            list(cliques(self.adjacency, 8))

    def test_exact_rank_and_minimum_witness(self):
        receipt = json.loads(verify.read_bytes(verify.PACKAGE / "RESULT.json"))
        indices = receipt["mixed"]["witness"]["indices"]
        anchor = tuple(2 * x for x in ANCHOR)
        rows = (anchor, *(self.vertices[i] for i in indices))
        self.assertEqual(rational_rank(rows), 6)
        self.assertEqual(independent.integer_rank(rows), 6)
        self.assertEqual(independent.integer_rank((*rows[:5], rows[0])), 5)
        costs = []
        for root in self.points:
            values = [0] + [dot(root, row) for row in rows]
            costs.append(7 - max(values.count(value) for value in values))
        self.assertEqual(bound.support_lower(costs, 32), 142)
        self.assertEqual(bound.support_lower(costs, 33), 139)

    def test_common_shift_minimum(self):
        for values in product((-1, 0, 1), repeat=7):
            actual = min(sum(value + shift != 0 for value in values) for shift in (-1, 0, 1))
            self.assertEqual(actual, 7 - max(Counter(values).values()))

    def test_root_arbitrary_cut_loses(self):
        self.assertEqual(self.root_result["losing_after_40_cuts"], 137)
        self.assertEqual(independent.root_fixture(), self.root_result["spectrum"])
        self.assertEqual(bound.support_lower(self.costs, 38), 141)
        with self.assertRaises(ValueError):
            bound.support_lower(self.costs, 121)

    def test_high_four_flat_coverage(self):
        exhaustive = {mask for mask in independent_weighted.flat_masks(self.full_labels, 4)
                      if (mask & self.layers[2]).bit_count() >= 7}
        self.assertEqual(exhaustive, set(self.four))
        self.assertEqual(len(exhaustive), 135)
        self.assertEqual(max(mask.bit_count() for mask in exhaustive), 8)

    def test_frame_orbit_is_complete(self):
        self.assertEqual(set(independent_weighted.frame_orbit(self.roots)), set(self.frames))
        self.assertEqual(len(self.frames), 2025)

    def test_weighted_cover_and_oversized_flat_control(self):
        result = weighted.cover_pairs(self.frames, self.six, self.four, self.layers)
        self.assertEqual(result["surviving_lower"], 141)
        with self.assertRaises(ValueError):
            weighted.cover_pairs(self.frames, (weighted.ALL, *self.six[1:]), self.four, self.layers)
        with self.assertRaises(ValueError):
            weighted.cover_pairs(self.frames, self.six, (weighted.ALL, *self.four[1:]), self.layers)
        with self.assertRaises(ValueError):
            weighted.cover_pairs(self.frames[:-1], self.six, self.four, self.layers)

    def test_retaining_only_the_six_flat_still_loses(self):
        result = json.loads(verify.read_bytes(verify.PACKAGE / "RESULT.json"))
        witness = result["weighted"]["cover"]["losing_witness"]
        self.assertIn(tuple(witness["frame"]), self.frames)
        self.assertIn(witness["six_mask"], self.six)
        prefix = witness["six_mask"] | sum(1 << i for i in witness["frame"])
        costs = sorted(c for i, c in enumerate(self.costs) if not (prefix >> i & 1))
        self.assertEqual(sum(costs[:-12]), 139)
        self.assertEqual(weighted.arbitrary_extra(prefix, self.layers, 12), sum(costs[-12:]))
        with self.assertRaises(ValueError):
            weighted.arbitrary_extra(prefix, self.layers, -1)

    def test_source_corruption_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as directory:
            package = Path(directory)
            (package / "vendor").mkdir()
            manifest = copy.deepcopy(self.sources)
            for row in manifest["retained_files"]:
                (package / row["local_path"]).write_bytes(
                    verify.read_bytes(verify.PACKAGE / row["local_path"]))
            (package / "SOURCES.json").write_text(json.dumps(manifest), encoding="utf-8")
            verify.bind_sources(package)
            (package / "vendor/geometry.py").write_text("changed\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                verify.bind_sources(package)
            manifest["retained_files"][0]["local_path"] = "../geometry.py"
            (package / "SOURCES.json").write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(ValueError):
                verify.bind_sources(package)

    def test_input_hash_and_semantic_controls(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as directory:
            path = Path(directory) / "data.txt"
            raw = verify.read_bytes(verify.ROOT / verify.DATA)
            lines = raw.decode("utf-8").splitlines()
            labels = lines[0].split()
            labels[0], labels[1] = labels[1], labels[0]
            lines[0] = " ".join(labels)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                verify.bind_data(path, self.points, self.labels, self.sources)
            sources = copy.deepcopy(self.sources)
            for row in sources["files"]:
                if row["usage"] == "input":
                    row["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            with self.assertRaises(ValueError):
                verify.bind_data(path, self.points, self.labels, sources)

    def test_symlink_and_output_guards(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as directory:
            root = Path(directory)
            target = root / "target"
            target.mkdir()
            (target / "data").write_bytes(b"data")
            (root / "alias").symlink_to(target, target_is_directory=True)
            with self.assertRaises(ValueError):
                verify.read_bytes(root / "alias/data")
            output = root / "receipt.json"
            verify.publish_receipt({"ok": True}, output)
            with self.assertRaises(FileExistsError):
                verify.publish_receipt({"ok": False}, output)
            self.assertEqual(json.loads(output.read_text()), {"ok": True})
            with self.assertRaises(ValueError):
                verify.publish_receipt({}, verify.PACKAGE / "not-written.json")

    def test_changed_receipt_is_rejected(self):
        result = json.loads(verify.read_bytes(verify.PACKAGE / "RESULT.json"))
        changed = copy.deepcopy(result)
        changed["weighted"]["cover"]["surviving_lower"] = 140
        with self.assertRaises(ValueError):
            verify.check_receipt(result, changed)
        verify.check_receipt(result, copy.deepcopy(result))


if __name__ == "__main__":
    unittest.main()
