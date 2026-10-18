"""Independent counts, proof boundaries, and source/CLI rejection controls."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import a5
import history
import verify
from vendor import geometry


def disposable_export(destination):
    package = destination / "research/p112-a5-shortening"
    shutil.copytree(verify.PACKAGE, package)
    for relative in (verify.DATA, verify.FILTER):
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(verify.ROOT / relative, target)
    # These are new disposable copies, including in a read-only source export.
    for path in package.rglob("*"):
        path.chmod(0o700 if path.is_dir() else 0o600)
    return package


class ProofControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roots, cls.points, cls.labels, _ = geometry.root_data()
        _, cls.costs, _ = a5.star_costs(cls.roots)

    def test_explicit_star_by_coordinate_shifts(self):
        star = []
        for j in range(1, 6):
            row = [0] * 8
            row[0] = row[j] = 2
            star.append(tuple(row))
        spectrum = Counter()
        for root in self.roots:
            values = [0] + [
                sum(x * y for x, y in zip(root, v, strict=True)) for v in star
            ]
            spectrum[min(sum(x != shift for x in values) for shift in values)] += 1
        self.assertEqual(spectrum, {0: 4, 1: 36, 2: 60, 3: 20})
        self.assertEqual(spectrum, Counter(self.costs))

    def test_support_frontier_by_separate_greedy_removal(self):
        for small in range(31):
            remaining = Counter({0: 4, 1: 36, 2: 60, 3: 20})
            cuts = 8 + small
            for cost in (3, 2, 1, 0):
                take = min(cuts, remaining[cost])
                remaining[cost] -= take
                cuts -= take
            lower = sum(cost * count for cost, count in remaining.items())
            self.assertEqual(a5.invoice(self.costs, small)["endpoint_lower"], lower)
        self.assertEqual(a5.certify_slice(self.costs, 29)["endpoint_lower"], 122)
        self.assertEqual(a5.invoice(self.costs, 30)["endpoint_lower"], 120)

    def test_new_caller_where_coordinate_bound_fails(self):
        row = verify.application(self.costs)
        bill = row["invoice"]
        self.assertEqual(
            (bill["endpoint_lower"], bill["endpoint_allowance"]), (128, 120)
        )
        self.assertEqual(
            (bill["old_coordinate_lower"], bill["old_coordinate_upper"]), (795, 800)
        )
        self.assertEqual(sum(history.CAP[w] for w in row["small_pieces"]), 26)
        self.assertEqual(len(row["retained"]), 9)

    def test_first_integer_gap_over_coordinate_bound(self):
        self.assertLess(a5.invoice(self.costs, 25)["old_coordinate_upper"], 795)
        self.assertGreaterEqual(a5.invoice(self.costs, 26)["old_coordinate_upper"], 795)

    def test_puncture_charge_is_required(self):
        self.assertEqual(sum(sorted(self.costs)[: 120 - 26]), 144)
        self.assertEqual(a5.invoice(self.costs, 26)["endpoint_lower"], 128)

    def test_root_only_boundary_and_quotient_boundary(self):
        with self.assertRaisesRegex(ValueError, "root-only"):
            a5.certify_slice([3] * 120, 30)
        with self.assertRaisesRegex(ValueError, "quotient"):
            a5.certify_slice([3] * 120, 33)

    def test_strict_budget_even_with_certified_edge_domain(self):
        with self.assertRaisesRegex(ValueError, "not a contradiction"):
            a5.certify_slice([2] * 68 + [0] * 52, 0)

    def test_invalid_support_and_cost_domains(self):
        for budget in (True, -1, 113, 26.0):
            with self.subTest(budget=budget), self.assertRaises(ValueError):
                a5.invoice(self.costs, budget)
        for costs in (self.costs[:-1], [4] * 120, [True] * 120):
            with self.assertRaisesRegex(ValueError, "costs"):
                a5.invoice(costs, 26)

    def test_target_is_an_actual_historical_profile(self):
        result = history.historical_profiles()
        self.assertEqual(result["profiles"].count(history.PROFILE), 1)
        self.assertEqual(
            (result["excess"], result["strict_excess_threshold"]), (35, 36)
        )
        self.assertEqual(len(result["profiles"]), 69)

    def test_prior_covers_by_disjoint_subsets(self):
        weights = (2, 5, 5, 6)
        caps = (2, 12, 12, 20)
        separate = {}
        for dimension in (6, 7):
            best = sum(caps)
            for first in range(16):
                for second in range(16):
                    if first & second:
                        continue
                    if all(
                        sum(weights[i] for i in range(4) if mask >> i & 1) <= dimension
                        for mask in (first, second)
                    ):
                        paid = sum(
                            caps[i] for i in range(4) if not ((first | second) >> i & 1)
                        )
                        best = min(best, paid)
            separate[str(dimension)] = best
        rows = history.weight_only_covers()
        self.assertEqual(len(rows), 1)
        self.assertEqual(separate, {"6": 14, "7": 12})
        self.assertEqual(rows[0]["minimum_paid_cut_budgets"], separate)
        self.assertEqual(rows[0]["nonbasis"], [6] * 5 + [7])

    def test_deleted_dimension_can_lose_one(self):
        # D=<e4,...,e9> in K^10, and T'=ker(x9), attain the loss of one.
        basis = [tuple(int(i == j) for i in range(10)) for j in range(4, 10)]
        self.assertEqual(len(basis), 6)
        self.assertEqual(sum(v[9] == 0 for v in basis), 5)

    def test_changed_input_rejected_before_geometry_import(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = disposable_export(root)
            (package / "vendor/geometry.py").write_text('raise RuntimeError("ran")')
            result = subprocess.run(
                [sys.executable, "-B", str(package / "verify.py")],
                text=True,
                capture_output=True,
                timeout=10,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("changed retained source", result.stderr)
            self.assertNotIn("RuntimeError: ran", result.stderr)
            with (root / verify.DATA).open("ab") as stream:
                stream.write(b"changed")
            with self.assertRaisesRegex(ValueError, "changed live input"):
                verify.check_sources(root, package)

    def test_original_filter_failures_propagate(self):
        for exception in (
            subprocess.TimeoutExpired("filter", 45),
            subprocess.CalledProcessError(1, "filter"),
        ):
            with (
                patch("verify.subprocess.run", side_effect=exception),
                self.assertRaises(type(exception)),
            ):
                verify.original_filter()
        for out, err in (("6 4 69 1\n", ""), ("", "warning")):
            with (
                patch(
                    "verify.subprocess.run",
                    return_value=SimpleNamespace(stdout=out, stderr=err),
                ),
                self.assertRaises(ValueError),
            ):
                verify.original_filter()

    def test_cli_refuses_existing_and_internal_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            existing = Path(temporary) / "keep.json"
            existing.write_text("preserved")
            for target in (existing, verify.PACKAGE / "new-output.json"):
                result = subprocess.run(
                    [
                        sys.executable,
                        "-B",
                        str(verify.PACKAGE / "verify.py"),
                        "--output",
                        str(target),
                    ],
                    text=True,
                    capture_output=True,
                    timeout=10,
                )
                self.assertNotEqual(result.returncode, 0)
            self.assertEqual(existing.read_text(), "preserved")
            self.assertFalse((verify.PACKAGE / "new-output.json").exists())

    def test_complete_original_table_required(self):
        valid = json.loads((verify.PACKAGE / "RESULT.json").read_text())[
            "original_filter"
        ]["rows"]
        malformed = [
            [[6, 4, 69, 1]] * 24,
            [[6, 4, 69, 1]] + [[1]] * 23,
            [*valid[:-1], [8, 6, 1555, 1]],
            list(reversed(valid)),
        ]
        for rows in malformed:
            out = "\n".join(" ".join(map(str, row)) for row in rows)
            with (
                patch(
                    "verify.subprocess.run",
                    return_value=SimpleNamespace(stdout=out, stderr=""),
                ),
                self.assertRaisesRegex(ValueError, "filter count mismatch"),
            ):
                verify.original_filter()

    def test_local_geometry_wins_over_ambient_vendor(self):
        with tempfile.TemporaryDirectory() as temporary:
            ambient = Path(temporary) / "vendor"
            ambient.mkdir()
            (ambient / "__init__.py").write_text("")
            (ambient / "geometry.py").write_text('raise RuntimeError("ambient ran")')
            env = dict(os.environ, PYTHONPATH=temporary)
            result = subprocess.run(
                [sys.executable, "-B", str(verify.PACKAGE / "verify.py")],
                text=True,
                capture_output=True,
                timeout=60,
                env=env,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS_P112_A5_SHORTENING", result.stdout)

    def test_package_initializer_must_be_empty(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = disposable_export(root)
            (package / "vendor/__init__.py").write_text('raise RuntimeError("ran")')
            with self.assertRaisesRegex(ValueError, "initializer must be empty"):
                verify.check_sources(root, package)

    def test_corrupted_committed_receipt_rejects(self):
        with tempfile.TemporaryDirectory() as temporary:
            package = disposable_export(Path(temporary))
            expected = json.loads((package / "RESULT.json").read_text())
            expected["application"]["invoice"]["endpoint_lower"] = 120
            (package / "RESULT.json").write_text(json.dumps(expected))
            result = subprocess.run(
                [sys.executable, "-B", str(package / "verify.py")],
                text=True,
                capture_output=True,
                timeout=60,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("receipt mismatch", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
