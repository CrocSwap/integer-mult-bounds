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
        for family in ('family533', 'family588', 'hyperplane599', 'cold617', 'k492', 'frontier741', 'frontier799', 'frontier890', 'reconciliation-fourth100', 'pilot20', 'efficient100', 'efficient200', 'efficient300', 'efficient400', 'efficient500', 'efficient600', 'efficient700', 'efficient800', 'efficient900', 'efficient1000', 'efficient1100', 'efficient1200'):
            path = ROOT / f'research/community-{family}-audit/DISPOSITIONS.json'
            cls.families[family] = json.loads(path.read_text())['pull_requests']
        cls.latest = {row['number']: row for decisions in cls.families.values() for row in decisions}

    def setUp(self):
        self.decision = deepcopy(self.latest[626])
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
        decision = self.latest[620]
        item = deepcopy(self.items[620])
        self.assertIsNone(decision['closure'])
        item.pop('closure')
        with self.assertRaisesRegex(ValueError, '#620:.*closure'):
            checker.check_family_decision(item, decision)

    def test_boolean_completion_flags_cannot_be_replaced_by_integers(self):
        for number in (626, 620):
            decision = self.latest[number]
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
        checker.check_family_decision(deepcopy(decision), decision)

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


class SpectrumRefresh(unittest.TestCase):
    def setUp(self):
        coverage = json.loads((ROOT / 'research/community-frontier890-audit/CONTENT-COVERAGE.json').read_bytes())
        self.items = [deepcopy(item) for row in coverage['pull_requests'].values()
                      for item in row['files'] if item.get('integrated_path') in {
                          'research/single-intersection-spectrum-audit/RESULT.json',
                          'research/single-intersection-spectrum-audit/SOURCE.json'}]
        self.old = b'08ddae46e5621a5b4c525b504e67ae655abe9b49461d894feaa7abc89a51847d'
        self.new = b'6874d41b75590369182ed61e0c6da5b547e035e0e43b50ea2b39e1f3861dca6d'

    def test_exact_accepted_refresh_and_original_bytes_pass(self):
        self.assertEqual(len(self.items), 2)
        for item in self.items:
            checker.check_frontier890_file(item)
            current = (ROOT / item['integrated_path']).read_bytes()
            original = current.replace(self.new, self.old)
            self.assertEqual(sha256(original).hexdigest(), item['integrated_sha256'])
            with patch.object(Path, 'read_bytes', return_value=original):
                checker.check_frontier890_file(item)

    def test_any_other_proof_or_metadata_edit_is_rejected(self):
        for item in self.items:
            current = (ROOT / item['integrated_path']).read_bytes()
            for mutated in (current.replace(b'"assignment_seed": 65', b'"assignment_seed": 66'),
                            current + b' ', current.replace(self.new, b'0' * 64),
                            current + self.new):
                self.assertNotEqual(mutated, current)
                original_read = Path.read_bytes
                def read(path):
                    return mutated if path == ROOT / item['integrated_path'] else original_read(path)
                with patch.object(Path, 'read_bytes', read), self.assertRaises(ValueError):
                    checker.check_frontier890_file(item)

    def test_changed_mathematical_case_is_rejected(self):
        item = next(item for item in self.items if item['integrated_path'].endswith('RESULT.json'))
        current = (ROOT / item['integrated_path']).read_bytes()
        mutated = current.replace(b'"binary_rank": 3,', b'"binary_rank": 4,', 1)
        self.assertNotEqual(current, mutated)
        original_read = Path.read_bytes
        def read(path):
            return mutated if path == ROOT / item['integrated_path'] else original_read(path)
        with patch.object(Path, 'read_bytes', read), self.assertRaisesRegex(ValueError, 'beyond'):
            checker.check_frontier890_file(item)

    def test_forged_historical_pin_is_rejected(self):
        for item in self.items:
            item['integrated_sha256'] = '0' * 64
            with self.assertRaisesRegex(ValueError, 'Changed integrated file'):
                checker.check_frontier890_file(item)

    def test_successor_helper_drift_is_rejected(self):
        original_read = Path.read_bytes
        def read(path):
            return b'changed helper' if path == ROOT / 'scripts/experiments/single_intersection.py' else original_read(path)
        with patch.object(Path, 'read_bytes', read):
            for item in self.items:
                with self.assertRaisesRegex(ValueError, 'Changed spectrum successor source'):
                    checker.check_frontier890_file(item)

    def test_unrelated_file_changes_still_fail(self):
        item = {'integrated_path': 'CONTRIBUTING.md', 'integrated_sha256': '0' * 64}
        with self.assertRaisesRegex(ValueError, 'Changed integrated file'):
            checker.check_frontier890_file(item)


class AssertionSafetyRefresh(unittest.TestCase):
    def setUp(self):
        coverage = json.loads((ROOT / 'research/community-batch932-audit/CONTENT-COVERAGE.json').read_bytes())
        self.items = [deepcopy(item) for row in coverage['pull_requests'].values()
                      for item in row['files'] if item.get('integrated_path') in {
                          'scripts/run_isolated_tests.py', 'tests/test_isolated_test_runner.py'}]

    def test_exact_accepted_successors_pass(self):
        self.assertEqual(len(self.items), 2)
        for item in self.items:
            checker.check_batch932_file(item)

    def test_historical_adapter_cannot_be_disabled(self):
        item = next(item for item in self.items if item['integrated_path'].startswith('scripts/'))
        current = (ROOT / item['integrated_path']).read_bytes()
        mutated = current.replace(b"path.name == 'test_skip_clones.py'", b'False')
        self.assertNotEqual(current, mutated)
        original_read = Path.read_bytes
        def read(path):
            return mutated if path == ROOT / item['integrated_path'] else original_read(path)
        with patch.object(Path, 'read_bytes', read), self.assertRaises(ValueError):
            checker.check_batch932_file(item)

    def test_assertion_guard_removal_and_other_byte_edits_fail(self):
        original_read = Path.read_bytes
        for item in self.items:
            current = (ROOT / item['integrated_path']).read_bytes()
            mutations = [current + b' ']
            if item['integrated_path'].startswith('scripts/'):
                mutations.append(current.replace(b"env.pop('PYTHONOPTIMIZE', None)", b'pass'))
            for mutated in mutations:
                self.assertNotEqual(current, mutated)
                def read(path):
                    return mutated if path == ROOT / item['integrated_path'] else original_read(path)
                with patch.object(Path, 'read_bytes', read), self.assertRaises(ValueError):
                    checker.check_batch932_file(item)

    def test_forged_predecessor_and_cross_file_successor_fail(self):
        for item in self.items:
            item['integrated_sha256'] = '0' * 64
            with self.assertRaises(ValueError):
                checker.check_batch932_file(item)
        other = (ROOT / self.items[1]['integrated_path']).read_bytes()
        with patch.object(Path, 'read_bytes', return_value=other), self.assertRaises(ValueError):
            checker.check_batch932_file(self.items[0])

    def test_unrelated_file_still_needs_exact_bytes(self):
        item = {'integrated_path': 'CONTRIBUTING.md', 'integrated_sha256': '0' * 64}
        with self.assertRaises(ValueError):
            checker.check_batch932_file(item)


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
