"""Keep PR closure state attached to completed review and preserved replay evidence."""
from copy import deepcopy
from hashlib import sha256
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('family_review_check', ROOT / 'scripts/verify_pr_reconciliation.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class ReviewCompletion(unittest.TestCase):
    def setUp(self):
        self.decision = {
            'review_completion': dict(changed_file_coverage=True, scoped_mechanism_review=True,
                                      required_execution_complete=True, published=True),
            'verification_evidence': ['research/family/RESULT.json'],
        }
        self.item = dict(deepcopy(self.decision), disposition='incorporated',
                         reviewed_head='a' * 40, current_head='a' * 40,
                         integration_location=['research/contribution'])

    def test_complete_review_can_be_incorporated(self):
        checker.check_review_completion(self.item, self.decision)

    def test_each_missing_gate_blocks_incorporation(self):
        for gate in self.decision['review_completion']:
            decision, item = deepcopy(self.decision), deepcopy(self.item)
            decision['review_completion'][gate] = False
            item['review_completion'][gate] = False
            with self.subTest(gate=gate), self.assertRaisesRegex(ValueError, 'before review'):
                checker.check_review_completion(item, decision)

    def test_partial_review_can_record_incomplete_execution(self):
        self.item['disposition'] = 'partially_reviewed'
        for obj in (self.item, self.decision):
            obj['review_completion']['published'] = False
            obj['review_completion']['required_execution_complete'] = False
        checker.check_review_completion(self.item, self.decision)

    def test_updated_head_and_missing_location_block_incorporation(self):
        for field, value in [('current_head', 'b' * 40), ('integration_location', [])]:
            item = deepcopy(self.item)
            item[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                checker.check_review_completion(item, self.decision)

    def test_ledger_cannot_drop_or_disagree_with_evidence(self):
        for field in ['review_completion', 'verification_evidence']:
            item = deepcopy(self.item)
            item.pop(field)
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'Ledger lost'):
                checker.check_review_completion(item, self.decision)
        self.decision['review_completion']['published'] = 1
        with self.assertRaisesRegex(ValueError, 'Invalid review-completion'):
            checker.check_review_completion(self.item, self.decision)

    def test_archived_artifact_changes_and_escapes_are_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = root / 'result.json'
            path.write_text('{"passed":true}\n')
            digest = sha256(path.read_bytes()).hexdigest()
            records = [{'files': {'result.json': digest}}]
            checker.check_archived_files(root, records)
            path.write_text('{"passed":false}\n')
            with self.assertRaisesRegex(ValueError, 'Changed archived replay'):
                checker.check_archived_files(root, records)
            with self.assertRaisesRegex(ValueError, 'Invalid replay evidence path'):
                checker.check_archived_files(root, [{'files': {'../outside.json': digest}}])
            with self.assertRaisesRegex(ValueError, 'Empty replay evidence'):
                checker.check_archived_files(root, [{'files': {}}])


if __name__ == '__main__':
    unittest.main()
