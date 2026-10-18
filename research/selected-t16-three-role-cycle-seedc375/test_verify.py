"""Positive and rejecting controls for the bounded owner-cycle census."""
from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import unittest

_spec = importlib.util.spec_from_file_location("same_call_cycle_verify", Path(__file__).with_name("verify.py"))
verify = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(verify)


class ThreeRoleCycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = verify.verify()

    def test_selected_domain_has_no_improving_transition(self):
        census = self.result["census"]
        self.assertEqual(census["ordered_supported_type_patterns"], 49408)
        self.assertEqual(census["capacity_feasible_type_patterns"], 4417)
        self.assertEqual(census["unique_ordered_transfer_states"], 255)
        self.assertEqual(census["distinct_rank_histogram_transitions"], 35)
        self.assertEqual(census["equal_histogram_transitions"], 19)
        self.assertEqual(census["strictly_more_expensive_transitions"], 16)
        self.assertEqual(census["strictly_cheaper_transitions"], 0)

    def test_known_majorizing_fixture_reduces_both_exact_prices(self):
        old = (0, 3, 3)
        widths = (9, 8, 9)
        new = verify.cycle_slacks(old, widths)
        self.assertEqual(new, (0, 2, 4))
        assembly = verify.read_json(verify.ASSEMBLY_PATH)
        alpha = Q(assembly["complex_lower"])
        M = verify.load_engine(verify.MOMENT_PATH, "positive_control_moment")
        B = verify.load_engine(verify.BASE_TWO_PATH, "positive_control_base_two")
        old_hist, new_hist = verify.rank_histogram(old), verify.rank_histogram(new)
        ranks = set(dict(old_hist)) | set(dict(new_hist))
        for engine_name, values in (
            ("Mercator", {r: M.moment({r: 1}, verify.M, verify.W, alpha, False) for r in ranks}),
            ("base-two", {r: B.moment(verify.M, verify.W, [(r, 1)], alpha) for r in ranks}),
        ):
            delta = verify.interval_difference(old_hist, new_hist, values, engine_name)
            self.assertLess(Q(delta["upper"]), 0, engine_name)

    def test_negative_capacity_control_rejects_overflow(self):
        new = verify.cycle_slacks((0, 0, 0), (9, 4, 7))
        self.assertLess(min(new), 0)

    def test_real_source_witness_is_strictly_worse(self):
        witness = self.result["census"]["minimum_strict_increase"]["feasible_source_witness"]
        groups = {tuple(move["source_group"]) for move in witness["moves"]}
        destinations = {tuple(move["destination_group"]) for move in witness["moves"]}
        self.assertEqual(len(groups), 3)
        self.assertEqual(destinations, groups)
        for engine in ("mercator_delta", "base_two_delta"):
            self.assertGreater(Q(self.result["census"]["minimum_strict_increase"][engine][0]), 0)


if __name__ == "__main__":
    unittest.main()
