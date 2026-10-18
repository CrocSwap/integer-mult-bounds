"""Behavioral controls, including a separate direct multiplicity oracle."""

import copy
import itertools
import json
import tempfile
import unittest
from pathlib import Path

import model
import verify
from vendor.geometry import dot, root_data, root_lines


class SupportBudgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roots = root_lines()
        cls.simplex = model.simplex_receipt(cls.roots)

    def test_complete_stabilizer_partition(self):
        steps = self.simplex["steps"]
        self.assertEqual([r["candidates"] for r in steps], [240, 56, 27, 16, 10, 6, 3])
        self.assertEqual([r["normal_lines"] for r in steps], [120, 63, 36, 20, 10, 4, 1])
        self.assertEqual([r["orbit_sizes"] for r in steps],
                         [[240], [56], [27], [16], [10], [6], [2, 1]])

    def test_both_seven_root_branches_are_required(self):
        self.assertEqual(self.simplex["lower_after_36_deletions"],
                         {6: [145], 7: [180, 166]})
        self.assertNotEqual(min(self.simplex["lower_after_36_deletions"][7]), 180)

    def test_source_order_is_irrelevant(self):
        self.assertEqual(model.simplex_receipt(tuple(reversed(self.roots))), self.simplex)

    def test_nonroot_and_duplicate_sources_rejected(self):
        for roots in (self.roots[:-1], self.roots[:-1] + (self.roots[0],),
                      ((0,) * 8,) + self.roots[1:]):
            with self.assertRaises(ValueError):
                model.simplex_receipt(roots)

    def test_nonstar_rejected(self):
        with self.assertRaises(ValueError):
            model.extension_orbits((self.roots[0], self.roots[0]), self.roots)
        with self.assertRaises(ValueError):
            model.extension_orbits(((0,) * 8,), self.roots)

    def test_direct_common_shift_oracle(self):
        # This oracle enumerates shifts and does not use Counter or the formula.
        cases = 0
        for n in range(1, 7):
            for values in itertools.product(range(3), repeat=n):
                direct = min(sum(v + shift != 0 for v in values) for shift in range(-2, 2))
                multiplicity = max(sum(v == selected for v in values) for selected in values)
                self.assertEqual(direct, n - multiplicity)
                cases += 1
        self.assertEqual(cases, 1092)

    def test_spectrum_from_direct_zero_shift_search(self):
        prefix = []
        for _ in range(6):
            classes, _, _ = model.extension_orbits(tuple(prefix), self.roots)
            prefix.append(classes[0][0])
        counts = {}
        for root in self.roots:
            values = [0] + [dot(root, vertex) for vertex in prefix]
            cost = min(sum(v != shift for v in values) for shift in set(values))
            counts[cost] = counts.get(cost, 0) + 1
        self.assertEqual(model.cost_spectrum(tuple(prefix), self.roots), counts)

    def test_support_bound_against_exhaustive_deletions(self):
        # A 120-coordinate spectrum with only six positive coordinates permits
        # an exhaustive independent check without sharing the sorting formula.
        spectrum = {0: 114, 1: 2, 2: 2, 3: 2}
        positive = (1, 1, 2, 2, 3, 3)
        for removed in range(7):
            oracle = min(sum(positive) - sum(positive[i] for i in cut)
                         for cut in itertools.combinations(range(6), removed))
            self.assertEqual(model.support_lower(spectrum, removed), oracle)

    def test_deletion_and_spectrum_boundaries(self):
        spectrum = model.EXPECTED[6][0]
        self.assertEqual(model.support_lower(spectrum, 0), 252)
        self.assertEqual(model.support_lower(spectrum, 120), 0)
        for removed in (-1, 121, True):
            with self.assertRaises(ValueError):
                model.support_lower(spectrum, removed)
        for bad in ({0: 119}, {-1: 120}, {0: 0, 1: 120}):
            with self.assertRaises(ValueError):
                model.support_lower(bad, 36)

    def test_named_applications_and_losing_prior_bound(self):
        rows = model.application_rows(self.simplex["spectra"])
        self.assertEqual([r["margin"] for r in rows], [5, 5, 6, 6])
        self.assertEqual([r["old_margin"] for r in rows], [-7, -7, -8, -8])
        self.assertTrue(all(r["basis_cap"] == 48 and r["edge_cap"] == 68 for r in rows))

    def test_original_survivors_and_no_anchor(self):
        for b, count in ((6, 69), (7, 154)):
            rows = model.original_survivors(b)
            self.assertEqual(len(rows), count)
            for weights in model.profiles(b):
                self.assertIn(weights, rows)
                audit = model.cover_audit(weights)
                self.assertEqual(audit[0]["minimum_cuts"], 16)
                self.assertFalse(audit[0]["rank_four_anchor"])
        with self.assertRaises(ValueError):
            model.profiles(8)

    def test_retained_source_binding(self):
        source = verify.bind_sources()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "SOURCES.json").write_text(json.dumps(source))
            (path / "vendor").mkdir()
            for row in source["retained_files"]:
                local = Path(row["local_path"])
                (path / local).write_bytes((verify.PACKAGE / local).read_bytes())
            self.assertEqual(verify.bind_sources(path), source)
            target = path / "vendor/geometry.py"
            target.write_bytes(target.read_bytes() + b"\n")
            with self.assertRaises(ValueError):
                verify.bind_sources(path)

    def test_p112_binding_mutants(self):
        source = verify.bind_sources()
        _, points, labels, _ = root_data()
        self.assertEqual(verify.bind_data(verify.ROOT / verify.DATA, points, labels, source),
                         source["files"][-1]["sha256"])
        with self.assertRaises(ValueError):
            verify.bind_data(verify.ROOT / verify.DATA, points, labels[::-1], source)
        with self.assertRaises(ValueError):
            verify.bind_data(verify.ROOT / verify.DATA, points[::-1], labels, source)

    def test_receipt_mutations_rejected(self):
        expected = json.loads((verify.PACKAGE / "RESULT.json").read_text())
        for field in ("margin", "endpoint_lower", "edge_cap"):
            mutant = copy.deepcopy(expected)
            mutant["applications"][0][field] += 1
            with self.assertRaises(ValueError):
                verify.check_receipt(mutant, expected)
        mutant = copy.deepcopy(expected)
        mutant["simplices"]["spectra"]["7"].pop()
        with self.assertRaises(ValueError):
            verify.check_receipt(mutant, expected)


if __name__ == "__main__":
    unittest.main()
