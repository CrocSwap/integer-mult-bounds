"""Independent local and complete-suffix controls for the 12-helper exchange."""
from collections import Counter
import unittest

import check_coretime
import check_complete_suffix as scalar
import check_suffix_frames as frames


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.local = check_coretime.run(minimal=True)
        cls.size, cls.before, cls.after, cls.scalar = scalar.build()

    def test_minimal_selection(self):
        self.assertEqual(self.local['selected'], 12)
        self.assertEqual(self.local['undone_old_restorations'], 6)
        groups = Counter(z['old_restored_helper_stream'] for z in self.local['candidates'])
        self.assertEqual(set(groups.values()), {2})

    def test_integer_local_map(self):
        self.assertTrue(self.local['exact_integer_root_schedule_identity'])
        self.assertTrue(self.local['missing_restoration_control_rejected'])

    def test_all_columns_forward(self):
        self.assertEqual(self.size, 18954)
        self.assertEqual(scalar.evaluate(self.before, self.size),
                         scalar.evaluate(self.after, self.size))

    def test_all_columns_reverse(self):
        self.assertEqual(scalar.evaluate(self.before, self.size, True),
                         scalar.evaluate(self.after, self.size, True))

    def test_exact_integer_operators_and_majorants(self):
        for reverse in (False, True):
            for absolute in (False, True):
                self.assertEqual(scalar.integer_operator(self.before, self.size, reverse, absolute),
                                 scalar.integer_operator(self.after, self.size, reverse, absolute))

    def test_complete_scalar_multiset(self):
        self.assertEqual(len(self.before), 55985)
        self.assertEqual(Counter(x[:3] for x in self.before),
                         Counter(x[:3] for x in self.after))
        self.assertEqual(self.scalar['co_retimed_partner_deliveries'], 12)

    def test_missing_restoration_is_detected(self):
        bad = self.after[:]
        index = next(i for i, row in enumerate(bad) if row[3].startswith('new_restore:'))
        del bad[index]
        self.assertNotEqual(scalar.evaluate(self.before, self.size),
                            scalar.evaluate(bad, self.size))

    def test_measured_paid_delta(self):
        result = frames.run()
        self.assertEqual(result['local_histogram_delta'], {1: 18, 2: -12})
        self.assertEqual(result['affected_streams'], 60)
        self.assertTrue(result['both_reflected_ledgers'])
        self.assertEqual(result['partner_setup_descent_replacements_applied'], 12)

    def test_missing_partner_promotion_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'nonnested'):
            frames.run('omit_partner_promotion')

    def test_missing_old_restoration_undo_rejected(self):
        with self.assertRaises(AssertionError):
            frames.run('omit_old_undo')


if __name__ == '__main__':
    unittest.main()
