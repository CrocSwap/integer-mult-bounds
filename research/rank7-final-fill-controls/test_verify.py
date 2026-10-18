#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the fixed-source capacity certificate."""

from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import itertools
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from allocation import bill, control_case, verify_fill, window_table
from local import V45, basis, contains, recount
import dual
import verify


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files, _ = verify.read_sources()
        cls.local = {name: recount(cls.files[f"data/WORD-{tag}.json.gz"])
                     for name, tag in (("gauge44", "base"), ("extra", "extra"))}
        cls.order = cls.files["allocation/ORDER.json"]
        cls.plan = cls.files["allocation/vendor/PLAN.json.gz"]
        cls.fill = cls.files["allocation/FILL.json.gz"]
        cls.dispatch = cls.files["allocation/DISPATCH.json"]
        cls.windows = window_table(cls.files["allocation/vendor/TEMPLATE.json.gz"],
                                   cls.order, cls.plan)
        cls.bins, cls.counts = cls.check_fill(cls.fill)
        cls.indices = {h: cls.local["gauge44"]["helpers"].index(h) for h in V45}

    @classmethod
    def check_fill(cls, fill):
        return verify_fill(fill, cls.order, cls.dispatch, cls.plan, cls.windows, cls.local)

    def test_binary_elimination_against_explicit_point_sets(self):
        def points(vectors):
            answer = {0}
            for v in vectors:
                answer |= {x ^ v for x in answer}
            return answer
        frames = {()}
        for tag in ("base", "extra"):
            w = self.files[f"data/WORD-{tag}.json.gz"]
            for section in ("A", "B", "restore"):
                frames.update(tuple(g[-1]) for g in w[section])
            frames.update(tuple(b) for b in w["helper_final"].values())
        for frame in frames:
            reduced = basis(frame)
            self.assertEqual(points(frame), points(reduced))
            self.assertEqual(reduced, basis(tuple(reversed(frame))))
            for line in ((), (1,), (30,), (45,), (256,)):
                self.assertEqual(contains(reduced, basis(line)), points(line) <= points(frame))
        with self.assertRaisesRegex(ValueError, "independent"):
            basis((1, 2, 3))
        with self.assertRaisesRegex(ValueError, "nine-bit"):
            basis((True,))

    def test_actual_geometry_rejections(self):
        rows = self.fill["rows"]
        def candidate(new_rows):
            return dict(self.fill, rows=new_rows)
        with self.assertRaisesRegex(ValueError, "row count"):
            self.check_fill(candidate(rows[:-1]))
        duplicate = list(rows)
        duplicate[1] = rows[0]
        with self.assertRaisesRegex(ValueError, "unique call/helper"):
            self.check_fill(candidate(duplicate))
        booleans = list(rows)
        booleans[0] = list(rows[0])
        booleans[0][1] = False
        with self.assertRaisesRegex(ValueError, "integer fill"):
            self.check_fill(candidate(booleans))
        family = list(rows)
        family[1] = list(rows[1])
        family[1][2:5] = rows[0][2:5]
        with self.assertRaisesRegex(ValueError, "physical helper families"):
            self.check_fill(candidate(family))
        deadline = list(rows)
        deadline[0] = list(rows[0])
        deadline[0][2:4] = [0, 12]
        with self.assertRaisesRegex(ValueError, "source window"):
            self.check_fill(candidate(deadline))
        incomplete = deepcopy(self.files["allocation/vendor/TEMPLATE.json.gz"])
        incomplete["idle_children"].pop()
        with self.assertRaisesRegex(ValueError, "complete source bin"):
            window_table(incomplete, self.order, self.plan)

    def test_overlap_and_noncompact_source_slices(self):
        rows = self.fill["rows"]
        moved = list(rows)
        index = next(i for i, row in enumerate(rows) if row[5] > 0)
        moved[index] = list(rows[index])
        moved[index][5] = 0
        with self.assertRaisesRegex(ValueError, "disjoint occupied"):
            self.check_fill(dict(self.fill, rows=moved))
        # A hole without an overlapping slice is still not the promised prefix.
        one = next((key, value[-1]) for key, value in self.bins.items()
                   if self.windows[key[:2]][0] > sum(row[3] for row in value))
        key, row = one
        index = next(i for i, r in enumerate(rows)
                     if (r[2], r[3], r[4]) == key and r[0] == row[1])
        moved = list(rows)
        moved[index] = list(rows[index])
        moved[index][5] += 1
        with self.assertRaisesRegex(ValueError, "compact occupied"):
            self.check_fill(dict(self.fill, rows=moved))

    def test_local_terminal_and_private_controls(self):
        word = self.files["data/WORD-base.json.gz"]
        base = self.local["gauge44"]
        parent = self.files["data/PARENT-base.json.gz"]
        controls = verify.word_controls(word, parent, base)
        self.assertEqual(controls[14]["local_profile"][1], base["profile"][1] + 3)
        self.assertEqual([r[4] for r in controls[14]["terminal_added_ranks"]], [1, 1, 1])
        bad = deepcopy(word)
        del bad["helper_final"]["249"]
        with self.assertRaisesRegex(ValueError, "private names"):
            recount(bad)
        bad_parent = deepcopy(parent)
        bad_parent["helper_final"]["249"] = [1, 2, 4, 8, 16, 32, 64, 128]
        with self.assertRaisesRegex(ValueError, "inside old"):
            verify.word_controls(word, bad_parent, base)

    def test_complete_invoice_and_false_control_invoice(self):
        idle, complete = bill(self.bins, self.windows, self.counts, self.local)
        self.assertEqual(idle, Counter({1: 17310, 3: 4956, 5: 1728, 48: 28190}))
        self.assertEqual(complete, verify.integer_profile(self.files["allocation/PROFILE.json"]))
        missing = deepcopy(self.local)
        missing["gauge44"]["profile"][1] -= 1
        with self.assertRaisesRegex(ValueError, "rank-mass"):
            bill(self.bins, self.windows, self.counts, missing)
        # Reusing the final idle bill with a widened terminal silently exceeds
        # the fixed coverage mass, before any numerical root is evaluated.
        wrong_idle = deepcopy(self.local)
        for provider in wrong_idle.values():
            provider["profile"][1] += 3
        with self.assertRaisesRegex(ValueError, "rank-mass"):
            bill(self.bins, self.windows, self.counts, wrong_idle)

    def test_single_control_witness_and_sharp_deletion_relaxation(self):
        result, witnesses = control_case(self.bins, self.windows, self.indices, [251, 265, 267])
        self.assertEqual((result["overfull_bins"], result["total_excess"],
                          result["moved_width_lower_bound"]), (1938, 1998, 15354))
        selected = {self.indices[h] for h in (251, 265, 267)}
        for witness in witnesses:
            widths = [row[3] + (row[2] in selected) for row in witness["placements"]]
            # Exhaustive small subsets independently price the free-sink
            # deletion relaxation. This does not construct a legal relocation.
            deletions = [sum(group) for n in range(1, len(widths) + 1)
                         for group in itertools.combinations(widths, n)
                         if sum(group) >= witness["excess"]]
            self.assertEqual(min(deletions), witness["minimum_evacuated_width"])
            self.assertGreater(sum(widths), witness["capacity"])
            self.assertLessEqual(sum(widths) - min(deletions), witness["capacity"])

    def test_all_subset_capacity_with_an_axis_counter(self):
        for mask in range(16):
            widened = [h for i, h in enumerate(V45) if mask & (1 << i)]
            selected = {self.indices[h] for h in widened}
            result, witnesses = control_case(self.bins, self.windows, self.indices, widened)
            count, excess = 0, 0
            for key, rows in self.bins.items():
                if not any(row[2] in selected for row in rows):
                    continue
                cursor = 0
                spilled = set()
                capacity = self.windows[key[:2]][0]
                for row in rows:
                    for axis in range(cursor, cursor + row[3] + (row[2] in selected)):
                        if axis >= capacity:
                            spilled.add(axis)
                    cursor += row[3] + (row[2] in selected)
                count += bool(spilled)
                excess += len(spilled)
            self.assertEqual((count, excess), (len(witnesses), result["total_excess"]))

    def test_export_optimized_cli_and_corrupt_input(self):
        with tempfile.TemporaryDirectory(prefix="final-fill-control-") as tmp:
            root = Path(tmp)
            package = root / "research" / verify.PACKAGE.name
            shutil.copytree(verify.PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__"))
            manifest = verify.decode((package / "SOURCES.json").read_bytes())
            for entry in manifest["files"]:
                if entry["usage"] == "input":
                    dest = root / entry["path"]
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(verify.ROOT / entry["path"], dest)
            command = [sys.executable, "-O", "-B", str(package / "verify.py")]
            run = subprocess.run(command, capture_output=True, text=True, timeout=90)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn("PASS_RANK7_FINAL_FILL_CONTROLS", run.stdout)
            corrupt = root / verify.SOURCE / "allocation/ORDER.json"
            corrupt.write_bytes(corrupt.read_bytes() + b" ")
            run = subprocess.run(command, capture_output=True, text=True, timeout=90)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("source SHA256 mismatch", run.stderr)

    def test_strict_receipt_json_and_histograms(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON"):
            verify.decode('{"rank": 7, "rank": 8}')
        with self.assertRaisesRegex(ValueError, "positive integer"):
            verify.integer_profile({"-1": 4})
        with self.assertRaisesRegex(ValueError, "positive integer"):
            verify.integer_profile({"1": True})

    def test_tariff_intervals_against_exact_algebraic_inequalities(self):
        for rank in range(1, 74):
            self.assertEqual(dual.tariff(rank, F(0)), (rank * dual.Q, rank * dual.Q))
            lo, hi = dual.tariff(rank, F(1, 2))
            self.assertLessEqual(lo * lo, rank * dual.Q**2)
            self.assertGreaterEqual(hi * hi, rank * dual.Q**2)
            lo, hi = dual.tariff(rank, F(1, 3))
            self.assertLessEqual(lo**3, rank**2 * dual.Q**3)
            self.assertGreaterEqual(hi**3, rank**2 * dual.Q**3)
            if rank > 1:
                half = dual.tariff(rank, F(1, 2))
                self.assertGreater(lo, half[1])
        self.assertEqual(dual.tariff(0, F(1, 2)), (0, 0))

    def test_exact_pattern_domain(self):
        # A separate recursive multiset walk checks the Cartesian enumerator.
        def walk(remaining, start, prefix):
            answer = {tuple(prefix.count(w) for w in dual.WIDTHS)}
            for i in range(start, len(dual.WIDTHS)):
                w = dual.WIDTHS[i]
                if w <= remaining:
                    answer |= walk(remaining - w, i, prefix + [w])
            return answer
        for capacity in dual.CAPACITIES:
            expected = walk(capacity, 0, [])
            actual = {counts for used, counts in dual.patterns(capacity)}
            self.assertEqual(actual, expected)

    def packing_check(self, source=None):
        return dual.check(source or self.files["certificates/RELAX-CAP.json"],
                          self.local["gauge44"]["profile"],
                          Counter(self.local["gauge44"]["widths"]), self.windows,
                          F(self.files["CLAIM.json"]["complex_lower"]))

    def test_dual_source_binding_and_complete_control_bounds(self):
        result = self.packing_check()
        self.assertEqual(result["pattern_count"], 2551)
        rows = result["per_replica_excess_over_896_times_73_power"]
        self.assertLess(F(rows[0]["upper"]), 0)
        for row in rows[1:]:
            self.assertGreater(F(row["lower"]), 0)
            self.assertGreater(F(row["complete_moment_lower_bound"]), 1)
        self.assertEqual(rows[3]["complete_moment_lower_decimal"], "1.000005090277")
        bad = deepcopy(self.files["certificates/RELAX-CAP.json"])
        bad["inventory_per_call"]["7"] -= 1
        with self.assertRaisesRegex(ValueError, "width binding"):
            self.packing_check(bad)
        bad = deepcopy(self.files["certificates/RELAX-CAP.json"])
        bad["basis_patterns"][0]["count_per_replica"] = "671"
        with self.assertRaisesRegex(ValueError, "primal bin totals"):
            self.packing_check(bad)

    def test_infeasible_dual_and_omitted_pattern_rejected(self):
        alpha, pi = dual.potentials()
        pi[7] = dual.linear((1, pi[7]), (F(1, 1000), dual.unit(1)))
        with patch.object(dual, "potentials", return_value=(alpha, pi)):
            with self.assertRaisesRegex(ValueError, "dual inequality"):
                self.packing_check()
        original = dual.patterns
        with patch.object(dual, "patterns", side_effect=lambda c: original(c)[1:]):
            with self.assertRaisesRegex(ValueError, "pattern domain"):
                self.packing_check()


if __name__ == "__main__":
    unittest.main(verbosity=2)
