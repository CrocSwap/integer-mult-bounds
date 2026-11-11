import unittest

import check_bank_assignment as banks


class BankAssignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = banks.run()

    def test_complete_role_and_replica_bijection(self):
        x = self.result
        self.assertEqual(x['helper_roles'], 15427)
        self.assertEqual(x['checked_role_replica_assignments_per_stage'], 925620)
        self.assertEqual(x['total_stage_assignments'], 4628100)
        self.assertTrue(x['stages_have_disjoint_bank_namespaces'])

    def test_frozen_assignment_and_stock(self):
        x = self.result
        self.assertEqual(x['assignment_sha256'],
                         '0317c568260dafde4cbc6ac1b88cae8afaa66d164ea454c372c01ea551af5f5b')
        self.assertEqual(x['banks_per_stage'], 161467)
        self.assertEqual(x['literal_stock'], 1229735)
        self.assertTrue(x['all_banks_full'])

    def test_duplicated_role_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'Missing or duplicated helper role'):
            banks.run(mutation='duplicate_role')


if __name__ == '__main__':
    unittest.main()
