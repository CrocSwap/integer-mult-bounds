"""Independent endpoint and triangular-factor controls for the F3 transfer."""
import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1]/'research/partial-swap-ternary/controls.py'
SPEC = importlib.util.spec_from_file_location('partial_swap_ternary_controls', PATH)
controls = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(controls)


class PartialSwapTernary(unittest.TestCase):
    def test_rational_factorization_and_necessary_correction(self):
        result = controls.rational_controls()
        self.assertEqual(result['field'], 'Q')
        self.assertEqual(result['projector_cases'], 54)
        self.assertGreater(result['nonsymmetric_cases'], 0)
        self.assertGreater(result['omitted_K_negative_controls'], 0)
        self.assertTrue(result['incomparable_edge_rejected'])

    def test_dirty_auxiliaries_and_all_address_symbols(self):
        for relocated in (False, True):
            result = controls.dirty_network(relocated=relocated)
            self.assertEqual(result['independent_input_symbols'], 2500)
            self.assertTrue(result['complete_linear_map_matches'])

    def test_missing_cleanup_and_wrong_endpoint_are_detected(self):
        for options in ({'omit_cleanup': True}, {'wrong_target': True},
                        {'extra_outer_shear': True}):
            result = controls.dirty_network(**options)
            self.assertFalse(result['complete_linear_map_matches'])
            self.assertIsNotNone(result['negative_control'])

    def test_scalar_producer_is_identity_over_ternary_field(self):
        # V=(1,1)^t, L=[[1,1],[0,1]], J=(1,2), so JLV=4=1.
        value = controls.mul(controls.mul([[1, 2]], [[1, 1], [0, 1]]), [[1], [1]])
        self.assertEqual(value[0][0] % 3, 1)
        self.assertNotEqual(value[0][0] % 2, 1)


if __name__ == '__main__':
    unittest.main()
