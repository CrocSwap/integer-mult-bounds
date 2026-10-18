"""Keep PR closure state attached to completed review and preserved replay evidence."""
from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('family_review_check', ROOT / 'scripts/verify_pr_reconciliation.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class FamilyDecision(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads((ROOT / 'docs/research/pr-ledger.json').read_text())
        cls.items = {row['number']: row for row in cls.ledger['pull_requests']}
        cls.families = {}
        for family in ('family533', 'family588', 'hyperplane599', 'cold617', 'k492', 'frontier741', 'frontier799'):
            path = ROOT / f'research/community-{family}-audit/DISPOSITIONS.json'
            cls.families[family] = json.loads(path.read_text())['pull_requests']

    def setUp(self):
        self.decision = deepcopy(next(row for row in self.families['k492']
                                      if row['number'] == 626))
        self.item = deepcopy(self.items[626])

    def test_current_family_projections_match_authoritative_decisions(self):
        final = {}
        for family, decisions in self.families.items():
            for decision in decisions:
                final[decision['number']] = (family, decision)
        for number, (family, decision) in final.items():
            with self.subTest(family=family, number=number):
                checker.check_family_decision(self.items[number], decision)

    def test_equal_forged_heads_do_not_establish_review_provenance(self):
        self.item['reviewed_head'] = self.item['current_head'] = '0' * 40
        with self.assertRaisesRegex(ValueError, '#626:.*reviewed_head'):
            checker.check_family_decision(self.item, self.decision)

    def test_changed_or_missing_projection_fields_are_rejected(self):
        replacements = {
            'number': 625,
            'reviewed_head': '0' * 40,
            'current_head': '0' * 40,
            'disposition': 'superseded',
            'github_state': 'OPEN',
            'integration_location': ['research/unrelated'],
            'unresolved_question': 'A different remaining question.',
            'closure': None,
            'review_completion': {},
            'verification_evidence': ['research/unrelated/RESULT.json'],
        }
        for field, value in replacements.items():
            for operation in ('replace', 'drop'):
                item = deepcopy(self.item)
                if operation == 'replace':
                    item[field] = value
                else:
                    item.pop(field)
                with self.subTest(field=field, operation=operation), self.assertRaisesRegex(
                        ValueError, '#626:.*' + field):
                    checker.check_family_decision(item, self.decision)

    def test_missing_closure_is_distinct_from_recorded_null(self):
        decision = next(row for row in self.families['k492'] if row['number'] == 620)
        item = deepcopy(self.items[620])
        self.assertIsNone(decision['closure'])
        item.pop('closure')
        with self.assertRaisesRegex(ValueError, '#620:.*closure'):
            checker.check_family_decision(item, decision)

    def test_boolean_completion_flags_cannot_be_replaced_by_integers(self):
        for number in (626, 620):
            decision = next(row for row in self.families['k492'] if row['number'] == number)
            for flag in decision['review_completion']:
                item = deepcopy(self.items[number])
                item['review_completion'][flag] = int(item['review_completion'][flag])
                with self.subTest(number=number, flag=flag), self.assertRaisesRegex(
                        ValueError, f'#{number}:.*review_completion'):
                    checker.check_family_decision(item, decision)

    def test_earlier_family_without_completion_metadata_remains_valid(self):
        decision = next(row for row in self.families['family533'] if row['number'] == 463)
        self.assertNotIn('review_completion', decision)
        self.assertNotIn('verification_evidence', decision)
        checker.check_family_decision(self.items[463], decision)

    def test_partial_decisions_can_preserve_distinct_reviewed_and_current_heads(self):
        for disposition in ('partially_reviewed', 'changed_since_review'):
            decision = deepcopy(next(row for row in self.families['k492']
                                     if row['number'] == 620))
            decision['disposition'] = disposition
            decision['current_head'] = '0' * 40
            item = deepcopy(decision)
            with self.subTest(disposition=disposition):
                self.assertNotEqual(item['reviewed_head'], item['current_head'])
                self.assertFalse(item['review_completion']['required_execution_complete'])
                checker.check_family_decision(item, decision)
                checker.check_review_completion(item, decision)

    def test_entrypoint_rejects_forged_ledger_heads(self):
        ledger = deepcopy(self.ledger)
        item = next(row for row in ledger['pull_requests'] if row['number'] == 626)
        item['reviewed_head'] = item['current_head'] = '0' * 40
        ledger_text = json.dumps(ledger)
        original_read_text = Path.read_text

        def read_text(path, *args, **kwargs):
            if path == ROOT / 'docs/research/pr-ledger.json':
                return ledger_text
            return original_read_text(path, *args, **kwargs)

        with patch.object(Path, 'read_text', read_text), self.assertRaisesRegex(
                ValueError, '#626:.*reviewed_head'):
            checker.main()


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
