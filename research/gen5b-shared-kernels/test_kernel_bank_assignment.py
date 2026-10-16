import unittest

import check_kernel_bank_assignment as banks


class KernelBankAssignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = banks.run()

    def test_complete_role_rebinding(self):
        x = self.result
        self.assertEqual(x['new_shared_kernel_pivots'], 72)
        self.assertEqual(x['helper_roles'], 15427)
        self.assertEqual(x['checked_role_replica_assignments_per_stage'], 925620)
        self.assertEqual(x['total_stage_assignments'], 4628100)
        self.assertEqual(x['family_counts'][23], 1646)
        self.assertEqual(x['family_counts'][24], 11401)

    def test_bank_addresses_and_stock(self):
        x = self.result
        self.assertEqual(x['assignment_sha256'],
                         '70da321406af20759213ffdfd5bb440ea2fd2757d89101c4f56d2efec01a951a')
        self.assertEqual(x['banks_per_stage'], 161431)
        self.assertEqual(x['literal_stock'], 1229555)
        self.assertTrue(x['all_banks_full'])
        self.assertTrue(x['stages_have_disjoint_bank_namespaces'])

    def test_duplicated_role_is_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'Missing or duplicated helper role'):
            banks.run(mutation='duplicate_role')


if __name__ == '__main__':
    unittest.main()
