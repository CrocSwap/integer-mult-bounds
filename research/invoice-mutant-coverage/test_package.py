"""Package tests for research/invoice-mutant-coverage: positive control and failure control."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as V  # noqa: E402


class TestInvoiceMutantCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='invoice-mutant-test.')
        cls.src, cls.global_dir = V.prepare(Path(cls.tmp.name))
        cls.mod = V.load_invoice(cls.src)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_positive_control_reproduces_archived_invoice(self):
        out = Path(self.tmp.name) / 'out-positive'
        V.run_invoice(self.mod, self.global_dir, out, V.RETAINED)
        archived = json.loads((self.global_dir / 'audit/PREFIX-AND-INVOICE.json').read_bytes())
        self.assertEqual(json.loads((out / 'PREFIX-AND-INVOICE.json').read_bytes()), archived)
        archived_prefix = json.loads((self.global_dir / 'audit/GLOBAL-PREFIX.json').read_bytes())
        self.assertEqual(json.loads((out / 'GLOBAL-PREFIX.json').read_bytes()), archived_prefix)

    def test_halving_guard_mutant_rejected_at_recorded_statement(self):
        tree = V.InputTree(self.global_dir)
        edit = {name: fn for name, cls_, fn in V.mutants()}['C3_owner_profile_halving_guard']
        edit(tree)
        verdict, detail, summary = V.failure(self.mod, self.global_dir,
                                             Path(self.tmp.name) / 'out-c3', V.RETAINED)
        tree.restore()
        self.assertEqual(verdict, 'rejected')
        self.assertIsNone(summary)
        self.assertIn('line 284', detail)
        expected = json.loads(V.EXPECT.read_text(encoding='utf-8'))['records']
        recorded = next(r for r in expected if r['name'] == 'C3_owner_profile_halving_guard')
        self.assertEqual(recorded['detail'], detail)

    def test_expected_receipt_covers_declared_census(self):
        expected = json.loads(V.EXPECT.read_text(encoding='utf-8'))
        names = [r['name'] for r in expected['records']]
        self.assertEqual(len(names), 37)
        self.assertEqual(len(set(names)), 37)
        self.assertEqual(expected['checked_mutants'], 37)
        self.assertEqual(expected['rejected'], 31)
        self.assertEqual(expected['accepted'], 6)
        for record in expected['records']:
            self.assertIn(record['verdict'], ('rejected', 'accepted'))
            if record['verdict'] == 'accepted':
                self.assertTrue(record['downstream'])
                self.assertIn('assemble_rejected', record['downstream'])
            else:
                self.assertIn('line ', record['detail'])


if __name__ == '__main__':
    unittest.main()
