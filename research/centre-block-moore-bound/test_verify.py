#!/usr/bin/env python3
"""Independent small graph and source-boundary controls for the Moore repair."""

from itertools import combinations
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as v


def affine_lines():
    return [tuple(3 * x + (slope * x + offset) % 3 for x in range(3))
            for slope in range(3) for offset in range(3)]


def fano_lines():
    return [triple for triple in combinations(range(7), 3)
            if (triple[0] + 1) ^ (triple[1] + 1) ^ (triple[2] + 1) == 0]


def matchings(items):
    if not items:
        yield ()
        return
    first, *rest = items
    for partner in rest:
        for tail in matchings([item for item in rest if item != partner]):
            yield ((first, partner),) + tail


def duad_lines():
    duads = list(combinations(range(6), 2))
    return [tuple(duads.index(pair) for pair in matching)
            for matching in matchings(list(range(6)))]


def literal_six_cycles(neighborhoods):
    """Count line triples with three distinct pairwise intersection points."""
    lines = [set(line) for line in neighborhoods]
    b_count = 1 + max(point for line in lines for point in line)
    per_b, per_d = [0] * b_count, [0] * len(lines)
    total = 0
    for a, b, c in combinations(range(len(lines)), 3):
        intersections = (lines[a] & lines[b], lines[b] & lines[c], lines[c] & lines[a])
        if not all(len(points) == 1 for points in intersections):
            continue
        points = set.union(*intersections)
        if len(points) != 3:
            continue
        total += 1
        for point in points:
            per_b[point] += 1
        for line in (a, b, c):
            per_d[line] += 1
    return total, per_b, per_d


class MooreControls(unittest.TestCase):
    def test_complement_triangles_break_the_predecessor_bound(self):
        cert = v.graph_certificate(affine_lines())
        self.assertEqual((cert["B"], cert["D"], cert["E"]), (9, 9, 27))
        self.assertEqual((cert["min_degree"], cert["c4"]), (3, 0))
        self.assertEqual(cert["distance2_triangles"], 27)
        self.assertEqual(cert["complement_triangles"], 3)
        self.assertEqual(cert["source_triangle_claim"], 30)
        source_check = v.predecessor_triangle(cert)
        self.assertEqual((source_check["counterexample_bound"], source_check["actual_triangles"]),
                         (30, 27))
        self.assertEqual(cert["sound_triangle_bound"], 27)
        self.assertEqual(literal_six_cycles(affine_lines()), (18, [6] * 9, [6] * 9))
        self.assertEqual(cert["c6"], 18)
        with self.assertRaises(ValueError):
            v.validate_caps(cert)

    def test_sound_triangle_bound_on_every_graph_through_five_vertices(self):
        checked = 0
        for size in range(3, 6):
            pairs = list(combinations(range(size), 2))
            for mask in range(1 << len(pairs)):
                edges = {edge for bit, edge in enumerate(pairs) if mask >> bit & 1}
                triangles = sum(all(edge in edges for edge in combinations(triple, 2))
                                for triple in combinations(range(size), 3))
                self.assertLessEqual(v.triangle_lower_bound(size, len(pairs) - len(edges)),
                                     triangles)
                checked += 1
        self.assertEqual(checked, 1096)

    def test_degree_three_cycle_cap_is_essential(self):
        lines = fano_lines()
        cert = v.graph_certificate(lines)
        self.assertEqual(literal_six_cycles(lines), (28, [12] * 7, [12] * 7))
        self.assertEqual(cert["c4"], 0)
        with self.assertRaises(ValueError):
            v.validate_caps(cert)
        with patch.object(v, "cap", return_value=12):
            v.validate_caps(cert)

    def test_c4_and_minimum_degree_hypotheses_are_checked(self):
        complete = v.graph_certificate([(0, 1, 2)] * 3)
        self.assertGreater(complete["c4"], 0)
        # Relax the cycle cap so rejection specifically needs the C4 hypothesis.
        with patch.object(v, "cap", return_value=10**9):
            with self.assertRaises(ValueError):
                v.validate_caps(complete)
        cycle = v.graph_certificate([(0, 1), (1, 2), (0, 2)])
        self.assertEqual((cycle["c4"], cycle["c6"], cycle["min_degree"]), (0, 1, 2))
        with self.assertRaises(ValueError):
            v.validate_caps(cycle)

    def test_fifteen_point_positive_and_literal_cycle_counts(self):
        lines = duad_lines()
        self.assertEqual(len(lines), 15)
        cert = v.graph_certificate(lines)
        self.assertEqual((cert["B"], cert["D"], cert["E"]), (15, 15, 45))
        self.assertEqual(cert["B_degrees"], [3] * 15)
        self.assertEqual(cert["D_degrees"], [3] * 15)
        self.assertEqual(literal_six_cycles(lines), (0, [0] * 15, [0] * 15))
        self.assertEqual((cert["c4"], cert["c6"]), (0, 0))
        v.validate_caps(cert)
        self.assertEqual(v.floor_certificate()["minimum_nonzero_owner_support"], cert["B"])
        original_cap = v.cap
        with patch.object(v, "cap", side_effect=lambda degree: 2 if degree == 3 else original_cap(degree)):
            with self.assertRaises(ValueError):
                v.floor_certificate()
        # Independently enumerate cycles on both nonempty examples as well.
        for graph in (affine_lines(), fano_lines()):
            with self.subTest(vertices=1 + max(map(max, graph))):
                actual = v.graph_certificate(graph)
                total, per_b, per_d = literal_six_cycles(graph)
                self.assertEqual((actual["c6"], actual["per_B_c6"], actual["per_D_c6"]),
                                 (total, per_b, per_d))

    def test_relation_inventory_rejects_missing_duplicate_and_nonbraid_words(self):
        receipt = json.loads((Path(__file__).resolve().parent / "RESULT.json").read_text())
        relations = [tuple(word) for word in receipt["source_premises"]["cyclic_relations"]]
        histogram = {1: 1379852, 2: 50}
        self.assertEqual(len(v.validate_relations(1379952, histogram, relations)), 50)
        malformed = list(relations)
        word = list(malformed[0])
        word[2] = next(label for label in range(112) if label not in word)
        malformed[0] = tuple(word)
        for changed in (relations[:-1], relations[:-1] + [relations[0]], malformed):
            with self.subTest(length=len(changed)):
                with self.assertRaises(ValueError):
                    v.validate_relations(1379952, histogram, changed)

    def test_changed_scientific_source_is_rejected(self):
        here = Path(__file__).resolve().parent
        manifest = json.loads((here / "SOURCES.json").read_text())
        pin = next(row for row in manifest["files"] if row["usage"] == "input")
        predecessor = json.loads((here / "PREDECESSOR.json").read_text())
        cert = v.graph_certificate(affine_lines())
        original_read = Path.read_bytes
        checks = [(v.ROOT / pin["path"], v.authenticate),
                  (here / predecessor["excerpt"], lambda: v.predecessor_triangle(cert))]
        for target, check in checks:
            with self.subTest(source=target.name):
                intercepted = []

                def changed_read(path):
                    data = original_read(path)
                    if path == target:
                        intercepted.append(path)
                        return data + b"\nsynthetic source corruption\n"
                    return data

                with patch.object(Path, "read_bytes", changed_read):
                    with self.assertRaisesRegex(ValueError, "SHA256"):
                        check()
                self.assertEqual(intercepted, [target])


if __name__ == "__main__":
    unittest.main()
