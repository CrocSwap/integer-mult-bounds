"""Small exact controls for the three-coordinate temporal optimizer."""

import importlib.util
import itertools
import unittest
from fractions import Fraction as Q
from pathlib import Path


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("seed21_verify", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class ThreeCoordinateTests(unittest.TestCase):
    def test_separable_distance_transform_matches_dense(self):
        dims = (tuple(range(-1, 2)),) * 3
        states = tuple(itertools.product(*dims))
        costs = {state: ((7 * state[0] - 3 * state[1] + state[2]) ** 2) % 17 - 4
                 for state in states}
        got_costs, got_origins = verify.distance_transform(costs, dims)
        for state in states:
            expected = min((costs[source] + verify.l1(state, source), source) for source in states)
            self.assertEqual((got_costs[state], got_origins[state]), expected)

    def test_bounded_three_axis_path_matches_dense_recurrence(self):
        helpers = (1, 2, 3)
        block = [(10, Q(2), (1, -1, 0)), (11, Q(1, 2), (0, 1, -1))]
        schedule, optimum, _ = verify.optimize([block], helpers, bound=1)
        states = tuple(itertools.product(range(-1, 2), repeat=3))
        dp = {(0, 0, 0): 0}
        for _, q, signs in block:
            next_dp = {}
            for state in states:
                price_delta = verify.price(q * verify.power(sum(x * y for x, y in zip(state, signs)))) - verify.price(q)
                next_dp[state] = min(cost + verify.l1(state, old) for old, cost in dp.items()) + price_delta
            dp = next_dp
        expected = min(cost + verify.l1(state, (0, 0, 0)) for state, cost in dp.items())
        self.assertEqual(optimum, expected)
        self.assertEqual(verify.schedule_cost([block], schedule, helpers, bound=1), expected)

    def test_completed_receipt_has_negative_controls_and_both_orientations(self):
        import json
        receipt = json.loads((HERE / "RESULT.json").read_text())
        self.assertEqual(receipt["coordinates"], [225, 350, 367])
        self.assertEqual(receipt["domain"], [-4, 4])
        self.assertEqual(set(receipt["orientations"]), {"forward", "backward"})
        self.assertEqual(receipt["controls"]["missing_schedule_event_rejected"], "PASS")
        self.assertEqual(receipt["controls"]["out_of_domain_exponent_rejected"], "PASS")
        self.assertEqual(receipt["controls"]["wrong_sign_shared_ADD_rejected_by_712_column_replay"], "PASS")


if __name__ == "__main__":
    unittest.main(verbosity=2)
