# SPDX-License-Identifier: Apache-2.0
"""Mathematical boundary and corruption controls, active with python -O."""

from fractions import Fraction as F
import importlib.util
import json
from pathlib import Path
import unittest

PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("normal45_independent_moments", PACKAGE / "moments.py")
moments = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(moments)


class MomentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        inputs = Path(__file__).resolve().parent / "inputs"
        read = lambda name: json.loads((inputs / name).read_text(encoding="utf-8"))
        cls.profile = moments.normalize(read("PROFILE.json"))
        cls.baseline = moments.normalize(read("baseline-PROFILE.json"))
        cls.claim = read("baseline-CLAIM.json")

    def test_full_exact_comparison_and_true_rejection_signs(self):
        result = moments.certify(self.profile, self.baseline, self.claim)
        self.assertEqual(result["status"], "PASS_INDEPENDENT_COMPLETE_PROFILE_MOMENT_NO_NEW_KAPPA")
        for name in ("extra_rank5_at_old", "extra_rank32_at_old", "extra_rank32_at_candidate_lower"):
            self.assertGreater(F(result["sensitivity"][name][0]), 1)
        self.assertLess(F(result["sensitivity"]["extra_rank4_at_old"][1]), 1)

    def test_omission_fails_complete_mass_even_if_numerically_favorable(self):
        omitted = dict(self.profile)
        del omitted[14]
        self.assertLess(moments.moment(omitted, F(self.claim["kappa"]))[1], 1)
        with self.assertRaisesRegex(ValueError, "candidate complete rank-mass"):
            moments.certify(omitted, self.baseline, self.claim)

    def test_written_coarse_rational_enclosures(self):
        result = moments.certify(self.profile, self.baseline, self.claim)
        sensitivity = result["sensitivity"]
        rows = [
            (result["at_exact_previous_headline"]["candidate_slack"], F(901400918, 10**15), F(901400920, 10**15)),
            (result["at_pinned_candidate_complex_lower"]["slack"], F(6, 10**26), F(61, 10**27)),
            ([F(x) - 1 for x in result["upper_probe"]["moment"]], F(284, 10**22), F(285, 10**22)),
            (sensitivity["omitted_rank14_charge_at_old"], F(290068663, 10**14), F(290068664, 10**14)),
            (sensitivity["omitted_rank14_charge_over_complete_slack"], F(321797612, 10**8), F(321797614, 10**8)),
            ([1 - F(x) for x in reversed(sensitivity["extra_rank4_at_old"])], F(7, 10**8), F(72, 10**9)),
            ([F(x) - 1 for x in sensitivity["extra_rank5_at_old"]], F(136, 10**9), F(137, 10**9)),
        ]
        for interval, lower, upper in rows:
            self.assertLess(lower, F(interval[0]))
            self.assertLess(F(interval[1]), upper)

    def test_zero_parameter_and_integer_powers(self):
        self.assertEqual(moments.power_bounds(F(73, 5), 0), (1, 1))
        self.assertEqual(moments.power_bounds(1, F(1, 7)), (1, 1))
        for value in (F(1), F(2), F(73, 48), F(73), F(511, 7)):
            lower, upper = moments.power_bounds(value, 1)
            self.assertLessEqual(lower, value)
            self.assertGreaterEqual(upper, value)

    def test_rational_square_and_cube_root_enclosures(self):
        # Compare with exact integer powers, not an approximate root oracle.
        for q in (F(73), F(73, 48), F(2), F(9, 4), F(27, 8)):
            for denominator in (2, 3, 7):
                lower, upper = moments.power_bounds(q, F(1, denominator))
                self.assertLessEqual(lower**denominator, q)
                self.assertGreaterEqual(upper**denominator, q)

    def test_low_precision_encloses_higher_precision(self):
        # A separate degree/precision pair must contain an independently refined
        # interval in this fixture; no monotonicity of arbitrary enclosures is assumed.
        for rank in (1, 3, 14, 48):
            q, b = F(73, rank), moments.CANDIDATE_COMPLEX_LOWER
            low = moments.power_bounds(q, b, bits=64, terms=32)
            high = moments.power_bounds(q, b)
            self.assertLessEqual(low[0], high[0])
            self.assertGreaterEqual(low[1], high[1])

    def test_invalid_profiles_parameters_and_pinned_headline(self):
        for bad in ({0: 1}, {73: 1}, {1: -1}, {1: 0}, {1: True}, {True: 1}, {"1": 1, 1: 2}, {}):
            with self.assertRaises(ValueError):
                moments.moment(bad, F(1, 1000))
        for bad in (F(-1), F(1001, 1000)):
            with self.assertRaises(ValueError):
                moments.power_bounds(2, bad)
        changed = dict(self.claim)
        changed["kappa"] = changed["complex_lower"]
        with self.assertRaisesRegex(ValueError, "full PR2930 guarded headline"):
            moments.certify(self.profile, self.baseline, changed)

    def test_failed_sufficient_upper_test_is_inconclusive(self):
        # Deliberately weak bounds straddle one.  Neither strict sign follows.
        lower, upper = moments.moment(self.profile, moments.CANDIDATE_COMPLEX_LOWER,
                                      bits=8, terms=1)
        self.assertLessEqual(lower, 1)
        self.assertGreaterEqual(upper, 1)
        self.assertFalse(lower > 1)
        self.assertFalse(upper < 1)


if __name__ == "__main__":
    unittest.main()
