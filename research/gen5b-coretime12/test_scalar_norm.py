import unittest

import scalar_norm_transport as transport


class ScalarNormTests(unittest.TestCase):
    def test_commuting_same_destination_updates(self):
        old = [(0, 1, 1, 'a'), (0, 2, -1, 'b')]
        result = transport.check(old, old[::-1])
        self.assertEqual(result['commuting_adjacent_swaps'], 1)
        self.assertEqual(result['forward_norm_factor'], 2)

    def test_noncommuting_swap_rejected(self):
        old = [(0, 1, 1, 'a'), (1, 2, 1, 'b')]
        with self.assertRaisesRegex(AssertionError, 'noncommuting'):
            transport.check(old, old[::-1])

    def test_changed_coefficient_rejected(self):
        with self.assertRaises(AssertionError):
            transport.check([(0, 1, 1, 'a')], [(0, 1, -1, 'a')])

    def test_complete_transport(self):
        result = transport.run()
        self.assertEqual(result['commuting_adjacent_swaps'], 172944)
        self.assertEqual(len(result['destinations_with_changed_update_order']), 12)
        self.assertEqual(result['payload_bits'], 103)
        self.assertLess(result['payload_upper'], 2 ** 104)


if __name__ == '__main__':
    unittest.main()
