"""Behavioral controls and separate finite oracles for the six exclusions."""

import copy
import hashlib
import json
import tempfile
import unittest
from itertools import combinations, product
from pathlib import Path

from model import (
    CAP,
    coordinate_bound,
    cover_audit,
    exclusions,
    partition_controls,
    profiles,
)
from vendor.geometry import canonical, dot, root_data
from verify import (
    DATA,
    PACKAGE,
    ROOT,
    bind_data,
    bind_sources,
    bounded_bytes,
    check_receipt,
)


class TestCoordinateBound(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = bind_sources()
        cls.roots, cls.points, cls.labels, _ = root_data()
        cls.result = json.loads(bounded_bytes(PACKAGE / "RESULT.json"))

    def test_six_actual_rows_and_old_losing_control(self):
        rows = exclusions([tuple(row) for row in self.result["original_survivor_table"]])
        self.assertEqual([r["bound"]["margin"] for r in rows], [33, 33, 40, 40, 60, 60])
        self.assertEqual([r["bound"]["old_margin"] for r in rows], [-15, -15, -28, -28, -28, -28])
        self.assertTrue(all(r["bound"]["basis_support_cap"] == 48 for r in rows))
        self.assertTrue(all(r["bound"]["edge_support_cap"] == 68 for r in rows))

    def test_unrestricted_coordinate_inequality(self):
        # Algebraic extremum with all nonzero values distinct, separate from partitions.
        for n in range(6, 10):
            for k in range(n + 1):
                maximum = k * (n - k) + k * (k - 1) // 2
                self.assertLessEqual(maximum, (n - 2) * k + 1)
                if k in (1, 2):
                    self.assertEqual(maximum, (n - 2) * k + 1)

    def test_all_equality_patterns(self):
        controls = [partition_controls(n) for n in range(6, 10)]
        self.assertEqual(sum(r["patterns"] for r in controls), 142139)
        for r in controls:
            n = r["vertices"]
            self.assertEqual(r["maxima"], [k * (n - k) + k * (k - 1) // 2
                                          for k in range(n + 1)])

    def test_intercept_is_necessary(self):
        for n in range(6, 10):
            values = [0] * (n - 2) + [1, 2]
            unequal = sum(x != y for x, y in combinations(values, 2))
            self.assertEqual(unequal, 2 * n - 3)
            self.assertGreater(unequal, (n - 2) * 2)

    def test_literal_root_simplices(self):
        # PR3170's explicit fixtures, checked directly here rather than imported.
        for b in (6, 7, 8):
            vertices = [(0,) * 8]
            for i in range(1, min(b, 7) + 1):
                row = [0] * 8
                row[0], row[i] = (-2 if b == 7 else 2), 2
                vertices.append(tuple(row))
            if b == 8:
                vertices.append((1,) * 8)
            for a, c in combinations(vertices, 2):
                self.assertIn(canonical(tuple(x - y for x, y in zip(a, c, strict=True))),
                              self.roots)
            n = b + 1
            for root in self.points:
                values = [dot(root, v) for v in vertices]
                unequal = sum(x != y for x, y in combinations(values, 2))
                self.assertLessEqual(unequal, max(n * n // 4, 2 * n - 3))

    def test_quotient_and_root_thresholds_reject(self):
        with self.assertRaisesRegex(ValueError, "quotient independence"):
            coordinate_bound(7, 33, [12] + [20] * 6)
        with self.assertRaisesRegex(ValueError, "root-edge"):
            coordinate_bound(7, 30, [12] + [20] * 6)

    def test_uncertified_sizes_reject(self):
        for args in ((5, 28, [20] * 5), (7, -1, [20] * 7),
                     (7, 28, [20] * 6), (7, 28, [20.0] * 7)):
            with self.assertRaises(ValueError):
                coordinate_bound(*args)

    def test_distance_failure_control(self):
        for b in (6, 7, 8):
            result = coordinate_bound(b + 1, 28, [12] + [20] * b)
            self.assertLessEqual(51 * result["edges"], result["upper"])

    def test_prior_six_vertex_count(self):
        result = coordinate_bound(6, 28, [12] + [20] * 5)
        self.assertEqual(result["margin"], 11)
        self.assertEqual(result["old_margin"], -17)

    def test_cover_audit_against_explicit_subsets(self):
        for b in (6, 7, 8):
            for weights in profiles(b):
                options = []
                anchors = []
                # Enumerate actual piece indices, rather than weight multisets.
                for indices in combinations(range(len(weights)), 4):
                    basis = [weights[i] for i in indices]
                    if sum(CAP[w] for w in basis) >= 53:
                        continue
                    remaining = [w for i, w in enumerate(weights) if i not in indices]
                    for a in product(range(3), repeat=4):
                        left = sum(basis[i] for i in range(4) if a[i] == 0)
                        right = sum(basis[i] for i in range(4) if a[i] == 1)
                        if left <= 6 and right <= 6:
                            cost = sum(CAP[basis[i]] for i in range(4) if a[i] == 2)
                            options.append(cost)
                            if min(remaining) <= 4:
                                anchors.append(cost)
                result = cover_audit(weights)
                self.assertEqual(result["minimum_cuts"], min(options))
                self.assertEqual(result["anchored_minimum_cuts"], min(anchors, default=None))

    def test_changed_receipt_rejects(self):
        changed = copy.deepcopy(self.result)
        changed["exclusions"][0]["bound"]["margin"] += 1
        with self.assertRaisesRegex(ValueError, "receipt differs"):
            check_receipt(self.result, changed)

    def test_wrong_original_table_rejects(self):
        changed = [tuple(row) for row in self.result["original_survivor_table"]]
        i = next(i for i, row in enumerate(changed) if row[:2] == (6, 4))
        changed[i] = (6, 4, 68, 4)
        with self.assertRaisesRegex(ValueError, "original survivor count"):
            exclusions(changed)

    def test_data_binding_and_hash_failure(self):
        bind_data(ROOT / DATA, self.points, self.labels, self.sources)
        with tempfile.TemporaryDirectory(prefix="simplex-data-") as directory:
            path = Path(directory) / "changed.txt"
            path.write_bytes((ROOT / DATA).read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "changed P112 input"):
                bind_data(path, self.points, self.labels, self.sources)

    def test_geometry_translation_failure(self):
        labels = (self.labels[0] ^ 2,) + self.labels[1:]
        with self.assertRaisesRegex(ValueError, "label binding"):
            bind_data(ROOT / DATA, self.points, labels, self.sources)
        points = (tuple(-x for x in self.points[0]),) + self.points[1:]
        with self.assertRaisesRegex(ValueError, "root binding"):
            bind_data(ROOT / DATA, points, self.labels, self.sources)

    def test_retained_source_mutation(self):
        with tempfile.TemporaryDirectory(prefix="simplex-source-") as directory:
            package = Path(directory)
            (package / "vendor").mkdir()
            for row in self.sources["retained_files"]:
                (package / row["local_path"]).write_bytes((PACKAGE / row["local_path"]).read_bytes())
            (package / "SOURCES.json").write_text(json.dumps(self.sources), encoding="utf-8")
            path = package / "vendor/geometry.py"
            path.write_bytes(path.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "changed retained source"):
                bind_sources(package)
            modified = copy.deepcopy(self.sources)
            for row in modified["retained_files"]:
                if row["local_path"] == "vendor/geometry.py":
                    row["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            (package / "SOURCES.json").write_text(json.dumps(modified), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "changed retained Git bytes"):
                bind_sources(package)

    def test_bounded_input_rejects(self):
        with self.assertRaisesRegex(ValueError, "oversized"):
            bounded_bytes(PACKAGE / "SOURCES.json", limit=1)
        with self.assertRaisesRegex(ValueError, "missing"):
            bounded_bytes(PACKAGE / "missing.json")


if __name__ == "__main__":
    unittest.main()
