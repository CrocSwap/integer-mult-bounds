"""Independent fixtures and corruption controls for the R14 finite F2 audit."""
import copy
import unittest
from independent_bit import AuditError, Budget, IdentityError, Protocol, check


def fixture():
    graph = dict(v=3, roots=[dict(kind='center', targets=[2]),
                 dict(kind='side', targets=[0]), dict(kind='side', targets=[1])])
    word = dict(ops=[[4, 1, 0], [2, 4, 0], [5, 1, 0], [7, 6, 0]],
                sources={'0': 0, '1': 1, '2': 6}, rootroles=[7, 2, 5],
                phase1=[3], gauges=[dict(role=5), dict(role=2)],
                reads={'5': 3, '2': 1}, pairs=[[4, 5]])
    k = dict(entries=[dict(carrier=0, passive=1, receivers=[0], deliver_after_root=1)])
    return graph, word, k


class TestAudit(unittest.TestCase):
    def test_every_basis_column_and_native_chronology(self):
        result = check(*fixture())['scalar_identity']
        self.assertEqual(result['target_rows'], 3)
        self.assertEqual(result['physical_dirty_rows_restored'], 7)
        self.assertEqual(result['independent_basis_columns'], 10)
        self.assertEqual(result['unpaired_gauge_reads'], 1)
        self.assertEqual(result['explicit_late_reads'], 1)

    def protocol(self):
        return Protocol(*fixture(), Budget())

    def test_omitted_paired_read_exposes_dirty_column(self):
        with self.assertRaisesRegex(IdentityError, 'target identity.*basis column'):
            self.protocol().run('omit_read', 5)

    def test_omitted_unpaired_read_exposes_dirty_column(self):
        with self.assertRaisesRegex(IdentityError, 'target identity.*basis column'):
            self.protocol().run('omit_read', 2)

    def test_read_before_donor_dies(self):
        with self.assertRaisesRegex(IdentityError, 'target identity'):
            self.protocol().run('premature_read', 5)

    def test_execution_position_is_not_operation_index(self):
        p = self.protocol()
        self.assertEqual(p.order, [3, 0, 1, 2])
        self.assertEqual(p.when[5][0], 3)
        with self.assertRaisesRegex(IdentityError, 'target identity'):
            p.run('read_position_as_index')

    def test_native_K_updated_carrier_required(self):
        with self.assertRaisesRegex(IdentityError, 'target identity'):
            self.protocol().run('wrong_K_injection')

    def test_reverse_gate_order_restores_arbitrary_dirty_values(self):
        g = dict(v=1, roots=[dict(kind='side', targets=[0])])
        w = dict(ops=[[1, 0, 0], [2, 1, 1]], sources={'0': 0},
                 rootroles=[2], phase1=[], gauges=[], pairs=[], reads={})
        p = Protocol(g, w, dict(entries=[]), Budget())
        p.run()
        with self.assertRaisesRegex(IdentityError, 'dirty restoration'):
            p.run('wrong_inverse_order')

    def test_missing_K_delivery_changes_identity(self):
        g, w, k = fixture()
        with self.assertRaisesRegex(IdentityError, 'target identity'):
            check(g, w, dict(entries=[]))

    def test_bad_target_assignment_changes_identity(self):
        g, w, k = fixture()
        g['roots'][2]['targets'] = [0]
        with self.assertRaisesRegex(IdentityError, 'target identity'):
            check(g, w, k)

    def test_alias_lifetime_checked(self):
        g, w, k = fixture()
        w['reads']['5'] = 2
        with self.assertRaisesRegex(AuditError, 'pair lifetime'):
            check(g, w, k)

    def test_duplicate_pair_rejected(self):
        g, w, k = fixture()
        w['pairs'] *= 2
        with self.assertRaisesRegex(AuditError, 'disjoint pair'):
            check(g, w, k)

    def test_no_normalization_of_duplicate_target_occurrences(self):
        g, w, k = fixture()
        g['roots'][2]['targets'] = [1, 1]
        with self.assertRaisesRegex(IdentityError, 'target identity'):
            check(g, w, k)

    def test_missing_source_rejected(self):
        g, w, k = fixture()
        del w['sources']['1']
        with self.assertRaisesRegex(AuditError, 'source bijection'):
            check(g, w, k)


if __name__ == '__main__':
    unittest.main()
