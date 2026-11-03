import unittest

import check_kernel70_bank_assignment as banks


class KernelBankAssignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = banks.run()

    def test_complete_role_rebinding(self):
        x = self.result
        self.assertEqual(x['new_shared_kernel_pivots'], 70)
        self.assertEqual(x['helper_roles'], 15427)
        self.assertEqual(x['checked_role_replica_assignments_per_stage'], 925620)
        self.assertEqual(x['total_stage_assignments'], 4628100)
        self.assertEqual(x['family_counts'][23], 1644)
        self.assertEqual(x['family_counts'][24], 11403)

    def test_bank_addresses_and_stock(self):
        x = self.result
        self.assertEqual(x['assignment_sha256'],
                         '69841a26beddd5a1d4cea70c745d831fe36e6543270b515a8beb4ffb2c61bee5')
        self.assertEqual(x['banks_per_stage'], 161432)
        self.assertEqual(x['literal_stock'], 1229560)
        self.assertEqual(x['unreplicated_stock'], '61478/3')
        self.assertTrue(x['all_banks_full'])
        self.assertTrue(x['stages_have_disjoint_bank_namespaces'])

    def test_duplicated_role_is_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'Missing or duplicated helper role'):
            banks.run(mutation='duplicate_role')


if __name__ == '__main__':
    unittest.main()
