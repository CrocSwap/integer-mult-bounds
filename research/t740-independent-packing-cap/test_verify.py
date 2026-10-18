# SPDX-License-Identifier: Apache-2.0
"""Positive checks and semantic failure controls, independent of source hashes."""

from copy import deepcopy
from fractions import Fraction as Q
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import verify as v


def taylor_bounds(x):
    """Test oracle only: unrelated exact Taylor enclosure, through degree 80."""
    term = total = Q(1)
    for k in range(1, 81):
        term *= x / k
        total += term
    next_term = term * x / 81
    return total, total + next_term / (1 - x / 82)


class CapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = v.inputs()

    def altered(self, index, mutation, reason):
        values = deepcopy(self.fixture)
        mutation(values[index])
        with self.assertRaisesRegex(ValueError, reason):
            v.audit(*values)

    def test_positive_and_published_receipt(self):
        result = v.audit(*self.fixture)
        self.assertEqual(result, json.loads((v.PACKAGE / "RESULT.json").read_text()))
        self.assertEqual(result["necessary_T_divisor"], 20)
        self.assertEqual(result["first_multiple_of_74"], 740)
        self.assertGreater(Q(result["minimum_reduced_cost_lower"]), Q("0.0040828"))

    def test_euler_bounds_against_separate_taylor_oracle(self):
        for x in (Q(0), Q(1, 1000), Q(1), Q(4), Q(8)):
            with self.subTest(x=x):
                lo, hi = v.exp_bounds(x)
                a, b = taylor_bounds(x)
                self.assertLessEqual(lo, a)
                self.assertLessEqual(b, hi)
                self.assertLess(hi - lo, Q(1, 10**30))

    def test_inverse_logarithms_against_separate_taylor_oracle(self):
        self.assertEqual(v.log_bounds(Q(1)), (0, 0))
        for value in (Q(73, 48), Q(2), Q(73)):
            lo, hi = v.log_bounds(value)
            self.assertLess(taylor_bounds(lo)[1], value)
            self.assertGreater(taylor_bounds(hi)[0], value)
            self.assertEqual(hi - lo, Q(8, 2**112))
        with self.assertRaisesRegex(ValueError, "exponential domain"):
            v.exp_bounds(Q(-1))

    def test_inventory_mutation(self):
        self.altered(0, lambda c: c["inventory_per_call"].update({"4": 25}),
                     "fixed width inventory")

    def test_unbalanced_primal_amount(self):
        self.altered(0, lambda c: c["basis_patterns"][0].update(count_per_replica="671"),
                     "primal supplies complete")

    def test_infeasible_bin(self):
        self.altered(0, lambda c: c["basis_patterns"][0].update(widths=[9]),
                     "infeasible basis pattern")

    def test_duplicate_basis(self):
        self.altered(0, lambda c: c["basis_patterns"].__setitem__(1, c["basis_patterns"][0]),
                     "ten distinct basis")

    def test_negative_primal(self):
        self.altered(0, lambda c: c["basis_patterns"][0].update(count_per_replica="-1"),
                     "negative primal")

    def test_stale_idle_histogram(self):
        self.altered(0, lambda c: c["idle_per_replica"].update({"48": "380"}),
                     "primal idle histogram")

    def test_actual_helper_inventory(self):
        self.altered(1, lambda p: p["gauge44"]["widths"].__setitem__(0, 4),
                     "actual ordered helper inventory")

    def test_provider_disagreement(self):
        self.altered(1, lambda p: p["extra"]["actual_paid_profile"].update({"1": 2434}),
                     "common actual local profile")

    def test_old_local_profile_is_not_silently_admitted(self):
        def stale(p):
            for provider in p.values():
                provider["actual_paid_profile"].update({"1": 2445, "2": 706})
        self.altered(1, stale, "literal six-skip profile")

    def test_mass_preserving_profile_corruption(self):
        def change(c):
            c["profile"]["1"] -= 2
            c["profile"]["2"] += 1
        self.altered(2, change, "literal six-skip profile")

    def test_omitted_idle_children(self):
        self.altered(2, lambda c: c["idle"].pop("48"), "T740 idle agreement")

    def test_wrong_replica_domain(self):
        self.altered(2, lambda c: c.update(replicas=74), "T740 finite domain")

    def test_old_root_with_correct_new_profile(self):
        def change(c):
            c["moment"]["root"] = [str(Q("0.001729035764875516181444")),
                                    str(Q("0.0017290357648755161814441"))]
        self.altered(2, change, "independently certified cap root")

    def test_missing_pattern(self):
        patterns = v.enumerate_patterns()
        with patch.object(v, "enumerate_patterns", return_value=patterns[:-1]):
            with self.assertRaisesRegex(ValueError, "complete pattern domain"):
                v.audit(*self.fixture)

    def test_published_cap_relations(self):
        for key, value, reason in (
            ("cap_lower", "1/1000", "published cap bracket"),
            ("idle_per_replica", {}, "published cap idle"),
            ("invariant", {"cap_requires_T_multiple_of": 10, "first_multiple_of_74": 740},
             "published divisibility claim"),
        ):
            with self.subTest(key=key):
                self.altered(2, lambda c: c["moment"]["fixed_inventory_cap"].update({key: value}),
                             reason)

    def test_residual_checks_include_ranks_outside_complete_profile(self):
        original = v.rank_bounds
        def bad_cost(rank, lo, hi):
            return (Q(0), Q(0)) if rank == 44 else original(rank, lo, hi)
        # Rank 44 is absent from the complete profile but occurs as bin idle.
        # The root still passes; an all-pattern reduced cost must now reject.
        with patch.object(v, "rank_bounds", side_effect=bad_cost):
            with self.assertRaisesRegex(ValueError, "strict reduced cost"):
                v.audit(*self.fixture)

    def test_source_bytes(self):
        sources = json.loads((v.PACKAGE / "SOURCES.json").read_text())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for row in sources["files"]:
                if row["usage"] == "input":
                    dest = root / row["path"]
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes((v.ROOT / row["path"]).read_bytes())
            relative = "research/rank7-t740-carrier-skips/evidence/FINITE.json"
            target = root / relative
            target.write_bytes(target.read_bytes() + b" ")
            with patch.object(v, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "source bytes: " + relative):
                    v.inputs()


if __name__ == "__main__":
    unittest.main()
