"""Independent historical evidence must not reopen a completed parent review."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pr116_ledger_builder', ROOT / 'scripts/reconcile_pr_queue.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
SOURCE = 'research/pr116-evidence-reconciliation/PARENT-EVIDENCE.json'


class IndependentParentEvidence(unittest.TestCase):
    def setUp(self):
        ledger = json.loads((ROOT / 'docs/research/pr-ledger.json').read_text())
        self.item = deepcopy(next(row for row in ledger['pull_requests'] if row['number'] == 116))
        self.item['evidence'] = [row for row in self.item['evidence'] if row['evidence'] != SOURCE]
        self.companion = json.loads((ROOT / SOURCE).read_text())['pull_requests'][0]

    def test_completed_parent_keeps_every_decision_and_prior_evidence(self):
        before = deepcopy(self.item)
        self.assertEqual(before['disposition'], 'incorporated')
        self.assertEqual(before['github_state'], 'CLOSED')
        self.assertTrue(before['review_completion']['required_execution_complete'])
        self.assertIsNone(before['unresolved_question'])
        builder.apply_independent_parent_evidence(self.item, self.companion, SOURCE)
        added = self.item['evidence'].pop()
        self.assertEqual(self.item, before)
        self.assertEqual(added['head'], before['current_head'])
        self.assertEqual(added['evidence'], SOURCE)
        self.assertEqual(added['kind'], 'independent_consolidation')

    def test_wrong_parent_or_changed_head_cannot_acquire_the_receipt(self):
        for field, wrong in [('number', 117), ('head', '0' * 40)]:
            with self.subTest(field=field):
                before = deepcopy(self.item)
                companion = dict(self.companion, **{field: wrong})
                with self.assertRaisesRegex(ValueError, 'different head'):
                    builder.apply_independent_parent_evidence(self.item, companion, SOURCE)
                self.assertEqual(self.item, before)


if __name__ == '__main__':
    unittest.main()
