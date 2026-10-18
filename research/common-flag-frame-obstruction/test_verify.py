"""Exact controls for the claimed hypothesis, endpoint and Laurent replay."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest


class CommonFlagTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).with_name("verify.py")
        if not path.is_file():
            self.fail("The common-flag verifier is not implemented")
        spec = importlib.util.spec_from_file_location("flag_verify", path)
        self.v = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.v)

    def test_untouched_arbitrary_roles_attain_the_bound(self):
        # Omitting a source/sink edge would undercount these six rank units.
        c = dict(W=3, m=2, rho=[0, 1, 2], gates=[],
                 source_frames=[[[0, 0], [0, 0]]] * 3,
                 sink_frames=[[[1, 0], [0, 1]]] * 3)
        result = self.v.check_flag(c, [[1, 0], [0, 1]], [[0, 0], [0, 0]])
        self.assertEqual(result["edge_ranks"], [2, 2, 2])
        self.assertEqual(result["character_counts"], [3, 3])
        self.assertEqual(result["rank_mass"], 6)

    def test_common_gauge_and_conjugation_preserve_edge_costs(self):
        cases = self.v.cases()
        plain = self.v.check_flag(**cases["noncommuting_jordan"])
        dense = self.v.check_flag(**cases["conjugated_affine"])
        self.assertEqual(plain, dense)
        self.assertGreater(plain["nilpotent_rank_excess"], 0)

    def test_bad_flag_is_rejected_even_when_endpoint_contract_passes(self):
        case = deepcopy(self.v.cases()["noncommuting_jordan"])
        # The frames stay valid rational matrices, but no longer preserve
        # the *supplied* flag. This does not claim absence of another flag.
        case["candidate"]["gates"][0]["frame"][2][0] = 1
        with self.assertRaisesRegex(ValueError, "flag"):
            self.v.check_flag(**case)

    def test_singular_basis_is_not_a_flag_certificate(self):
        case = deepcopy(self.v.cases()["noncommuting_jordan"])
        case["basis"][1] = case["basis"][0][:]
        with self.assertRaisesRegex(ValueError, "singular"):
            self.v.check_flag(**case)

    def test_changed_endpoint_and_wrong_rho_are_rejected(self):
        case = deepcopy(self.v.cases()["noncommuting_jordan"])
        case["candidate"]["sink_frames"][0][0][0] += 1
        with self.assertRaisesRegex(ValueError, "endpoint"):
            self.v.check_flag(**case)
        case = deepcopy(self.v.cases()["noncommuting_jordan"])
        case["candidate"]["rho"] = list(range(case["candidate"]["W"]))
        with self.assertRaisesRegex(ValueError, "permutation"):
            self.v.check_flag(**case)

    def test_missing_xor_and_unlisted_source_are_rejected(self):
        case = deepcopy(self.v.cases()["noncommuting_jordan"])
        case["candidate"]["gates"].pop()
        with self.assertRaisesRegex(ValueError, "permutation"):
            self.v.check_flag(**case)
        case = deepcopy(self.v.cases()["noncommuting_jordan"])
        case["candidate"]["gates"][0]["roles"] = [0]
        with self.assertRaisesRegex(ValueError, "ports"):
            self.v.check_flag(**case)

    def test_fractional_exponents_do_not_reduce_modulo_two(self):
        # z^(1/2)*z^(1/2)=z, whereas reducing rational coefficients
        # into F2 is undefined. The exponent group stays characteristic zero.
        from fractions import Fraction as Q
        one = [frozenset({(Q(0),)})]
        shifted = self.v.shift(self.v.shift(one, (Q(1, 2),)), (Q(1, 2),))
        self.assertEqual(shifted, [frozenset({(Q(1),)})])
        self.assertEqual(self.v.shift(shifted, (Q(-1),)), one)

    def test_different_gate_incidence_frames_are_not_silently_ignored(self):
        case = deepcopy(self.v.cases()["noncommuting_jordan"])
        case["candidate"]["gates"][0]["incidence_frames"] = ["different", "frames"]
        with self.assertRaisesRegex(ValueError, "common frame"):
            self.v.check_flag(**case)

    def test_rank_is_over_rationals_not_the_payload_field(self):
        self.assertEqual(self.v.rank([[1, 1], [1, -1]]), 2)

    def test_laurent_endpoint_check_rejects_wrong_characters(self):
        candidate = self.v.cases()["noncommuting_jordan"]["candidate"]
        frames, edges = self.v.contract(candidate)
        for characters in ([(0,) for a in frames], [(2 * a[0][0],) for a in frames]):
            with self.assertRaisesRegex(ValueError, "Laurent endpoint"):
                self.v.replay(candidate, characters, edges)

    def test_nonsplit_commuting_frames_use_both_characters(self):
        result = self.v.rotation_case()
        self.assertEqual(result["character_counts"][0], result["character_counts"][1])
        self.assertEqual(result["rank_mass"], sum(result["character_counts"]))
        self.assertGreaterEqual(result["rank_mass"], result["baseline"])

    def test_nonsplit_eigenvector_equations_are_checked(self):
        candidate = self.v.rotation_candidate()
        candidate["gates"][0]["frame"][0][1] += 1
        with self.assertRaisesRegex(ValueError, "eigenvector"):
            self.v.check_rotation(candidate)

    def test_dense_rank_one_diagonal_is_not_a_rank_lower_bound(self):
        # Prevent extending the triangular diagonal bound to arbitrary frames.
        dense = [[1, 1], [1, 1]]
        self.assertEqual(self.v.rank(dense), 1)
        self.assertEqual(sum(dense[i][i] != 0 for i in range(2)), 2)


if __name__ == "__main__":
    unittest.main()
