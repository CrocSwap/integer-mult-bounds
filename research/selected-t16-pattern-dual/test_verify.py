#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent arithmetic oracles and boundary controls for the scoped proof."""
from copy import deepcopy
from fractions import Fraction as Q
from itertools import product
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as v


def surd_sign(a, b, d):
    """Exact sign of a+b*sqrt(d), using only rational squares."""
    if b == 0:
        return (a > 0) - (a < 0)
    if a == 0:
        return (b > 0) - (b < 0)
    if a > 0 and b > 0:
        return 1
    if a < 0 and b < 0:
        return -1
    gap = a*a - d*b*b
    sign = (gap > 0) - (gap < 0)
    return sign if a > 0 else -sign


def radical_gap_sign(r, A, B):
    """Sign of sqrt(r)-A-B*sqrt(48); no interval engine or isqrt."""
    rhs_sign = surd_sign(A, B, 48)
    if rhs_sign <= 0:
        return 1 if r > 0 or rhs_sign < 0 else 0
    return surd_sign(Q(r)-A*A-48*B*B, -2*A*B, 48)


class PatternProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = v.load_inputs()
        cls.plan, cls.spec, cls.owners = [cls.inputs[v.PREFIX + name]
                                        for name in ("PLAN.json", "SPEC.json", "OWNERS.json.gz")]
        cls.model = v.source_model(cls.plan, cls.spec, cls.owners)
        cls.cert = json.loads((v.HERE / "CERTIFICATE.json").read_text())

    def test_all_patterns_against_cartesian_enumeration(self):
        total = 0
        for capacity in v.CAPS:
            oracle = set()
            for counts in product(*(range(capacity // w + 1) for w in v.WIDTHS)):
                r = capacity - sum(w*n for w, n in zip(v.WIDTHS, counts))
                if r >= 0:
                    oracle.add((counts, r))
            actual = list(v.patterns(capacity))
            self.assertEqual(len(actual), len(set(actual)))
            self.assertEqual(set(actual), oracle)
            total += len(oracle)
        self.assertEqual(total, 1163)

    def test_all_dual_endpoints_by_exact_radical_squares(self):
        constants = [Q(x, self.cert["dual_denominator"]) for x in self.cert["dual_constant_numerators"]]
        powers = [Q(x, self.cert["dual_denominator"]) for x in self.cert["dual_power48_numerators"]]
        signs = {0: 0, 1: 0}
        for capacity in v.CAPS:
            for counts, r in v.patterns(capacity):
                column = [int(capacity == c) for c in v.CAPS] + list(counts)
                A = sum(x*y for x, y in zip(column, constants))
                B = sum(x*y for x, y in zip(column, powers))
                sign = radical_gap_sign(r, A, B)
                self.assertGreaterEqual(sign, 0)
                signs[sign] += 1
        primary = v.check_certificate(self.cert, self.model)
        self.assertEqual(signs[0], primary["symbolic_equalities"])
        self.assertEqual(signs[1], primary["strict_half_endpoint"])
        # A mass-preserving forged empty48 price fails this different oracle too.
        self.assertEqual(radical_gap_sign(48, Q(48, 37), Q(36, 37)), -1)

    def test_power_enclosures_against_exact_integer_powers(self):
        comparisons = 0
        for rank in (0, 1, 2, 3, 7, 16, 48, 73):
            for p in (Q(1), Q(1, 2), Q(1, 4), Q(3, 4), Q(1, 3), Q(2, 3), Q(7, 9), Q(98, 99)):
                lo, hi = v.power_interval(rank, p, exponent_bits=48, fraction_bits=80)
                target = rank**p.numerator
                self.assertLessEqual(lo, hi)
                self.assertLessEqual(lo.numerator**p.denominator, target * lo.denominator**p.denominator)
                self.assertGreaterEqual(hi.numerator**p.denominator, target * hi.denominator**p.denominator)
                comparisons += 1
        self.assertEqual(comparisons, 64)

    def test_exact_square_root_values(self):
        for square, root in ((0, 0), (1, 1), (4, 2), (9, 3), (16, 4), (49, 7)):
            self.assertEqual(v.power_interval(square, Q(1, 2)), (Q(root), Q(root)))

    def test_source_bytes_are_required(self):
        original = Path.read_bytes
        target = v.ROOT / (v.PREFIX + "PLAN.json")

        def forged(path):
            raw = original(path)
            return raw + b" " if path == target else raw

        with patch.object(Path, "read_bytes", forged):
            with self.assertRaisesRegex(ValueError, "^source drift:"):
                v.load_inputs()

    def test_owner_and_certificate_order_is_irrelevant(self):
        shuffled = v.source_model(self.plan, self.spec, list(reversed(self.owners)))
        self.assertEqual(shuffled, self.model)
        cert = deepcopy(self.cert)
        cert["primal_patterns"].reverse()
        self.assertEqual(v.check_certificate(cert, self.model), v.check_certificate(self.cert, self.model))

    def test_paid_local_omission_rejected(self):
        spec = deepcopy(self.spec)
        spec["providers"]["gauge44"]["expected_profile"]["1"] -= 1
        with self.assertRaisesRegex(ValueError, "^fixed paid local profile$"):
            v.source_model(self.plan, spec, self.owners)

    def test_uncertain_sign_cannot_become_a_root_decision(self):
        with patch.object(v, "moment_gap", side_effect=[(Q(-1), Q(-1)), (Q(1), Q(1)), (Q(-1), Q(1))]):
            with self.assertRaisesRegex(ValueError, "^unresolved root interval$"):
                v.root_bracket({1: Q(1)})

    def test_predecessor_claim_mutations(self):
        prior = self.inputs["research/r480-owner-optimum/CERTIFICATE.json"]
        proof = v.check_certificate(self.cert, self.model)
        profile = v.complete_profile(self.model, proof["idle"])
        lo, hi = v.check_predecessor(self.cert, prior, profile)
        for shift in (hi-lo, lo-hi):
            wrong = deepcopy(prior)
            wrong["root_interval"] = [str(lo+shift), str(hi+shift)]
            with self.assertRaisesRegex(ValueError, "^predecessor strict root signs$"):
                v.check_predecessor(self.cert, wrong, profile)
        wrong = deepcopy(prior)
        wrong["packing"][0]["bins"] += 1
        with self.assertRaisesRegex(ValueError, "^predecessor pattern scaling$"):
            v.check_predecessor(self.cert, wrong, profile)
        wrong = deepcopy(prior)
        wrong["width_prices"]["4"] += 1
        with self.assertRaisesRegex(ValueError, "^predecessor dual reconciliation$"):
            v.check_predecessor(self.cert, wrong, profile)


if __name__ == "__main__":
    unittest.main(verbosity=2)
