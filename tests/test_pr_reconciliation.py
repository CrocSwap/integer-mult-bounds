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


class StartingHeadIntegrity(unittest.TestCase):
    def setUp(self):
        self.item = {
            'number': 3107,
            'starting_head': 'initial',
            'current_head': 'revised',
            'previously_reviewed_heads': ['initial'],
        }

    def test_frozen_snapshot_requires_the_exact_initial_head(self):
        with self.assertRaisesRegex(ValueError, '#3107: starting head changed'):
            checker.check_starting_head(self.item, 'revised', True)

    def test_later_family_metadata_can_bind_a_revised_current_head(self):
        checker.check_starting_head(self.item, 'revised', False)

    def test_later_head_requires_the_initial_head_in_review_history(self):
        item = deepcopy(self.item)
        item['previously_reviewed_heads'] = []
        with self.assertRaisesRegex(ValueError, '#3107: starting head changed'):
            checker.check_starting_head(item, 'revised', False)

    def test_later_metadata_must_match_the_ledger_current_head(self):
        with self.assertRaisesRegex(ValueError, '#3107: starting head changed'):
            checker.check_starting_head(self.item, 'other-current', False)


class FamilyDecision(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads((ROOT / 'docs/research/pr-ledger.json').read_text())
        cls.items = {row['number']: row for row in cls.ledger['pull_requests']}
        cls.families = {}
        # The former test stopped at efficient1200, so later valid reviews
        # looked like forged projections. Follow the actual authoritative order.
        for path in checker.decision_paths():
            if path.exists():
                cls.families[path.parent.name.removeprefix('community-').removesuffix('-audit')] = json.loads(path.read_text())['pull_requests']
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
        decision = next(row for row in self.families['k492'] if row['number'] == 620)
        self.assertIsNone(decision['closure'])
        item = deepcopy(decision)
        checker.check_family_decision(item, decision)
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

    def test_reviewed_parallel_verifier_successor_passes_without_rewriting_pin(self):
        checker.check_frontier890_file({
            'integrated_path': 'scripts/verify_complex741_parallel.py',
            'integrated_sha256':
                '616cff67233958647dd1e6f33dcc5ffc6132df68e0e1230dc768e820d00155a1',
        })

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


class ReviewedFamilySourceSuccessor(unittest.TestCase):
    def test_reviewed_utf8_successor_passes_without_rewriting_source_pin(self):
        checker.check_reviewed_family_source(
            'scripts/verify_hpe_lean_binding.py',
            '52aa1d23641e4c716b43c98f6b883ad042087dd03a9d01369e8e6a735b07aa03')

    def test_reviewed_integer_row_successor_passes_without_rewriting_source_pin(self):
        checker.check_reviewed_family_source(
            'research/complex-k492-owner-repair/code/hpe_audit_and_transport.py',
            'c9a05ff291016b870b4fc925b317abd9c3a604c73ffc8920dfdbbeb475e20aa3')

    def test_reviewed_frontier741_successors_pass_without_rewriting_pins(self):
        for path, digest in (
                ('research/complex-factory5-resynthesis/SOURCE-PINS.json',
                 '79e00db34b721dc38830a7816f3126a09615d49c12f1b6a630147f1f50378f63'),
                ('research/complex-factory5-resynthesis/verify.py',
                 'edbae43b68c0e4f65978a2f9b9a739867128f4ef19d8bbe81d06ed2e5bc165f1'),
                ('research/supplier-circuit-consolidation/SOURCES.json',
                 'ef2568aac251c94d86736936b9d8c7507d224b129da2907d1bc6a1c2b5546742'),
                ('docs/ci-verification.md',
                 'a854022e0e1d5d4db4d60e586be3ea56005013ef14a1fc06d02bc06e8529c4b0'),
                ('scripts/verify_selected_result.py',
                 'd7fd929726b326aeeaf0a3996475adec88eee9aac09ae0bebeeaa0bc1fc8f199')):
            with self.subTest(path=path):
                checker.check_reviewed_family_source(path, digest)

    def test_unreviewed_source_successor_is_rejected(self):
        with patch.object(Path, 'read_bytes', return_value=b'unreviewed source'), \
                self.assertRaisesRegex(ValueError, 'Changed reviewed family source'):
            checker.check_reviewed_family_source(
                'scripts/verify_hpe_lean_binding.py',
                '52aa1d23641e4c716b43c98f6b883ad042087dd03a9d01369e8e6a735b07aa03')


class ReviewedArchiveSuccessors(unittest.TestCase):
    def test_batch1047_and_batch1099_successors_keep_historical_pins(self):
        cases = (
            (checker.check_batch1047_file,
             'research/p112-free-sink-audit97/README.md',
             'c792fc8f5de0c784049904c6febf3eed9b20e2462b30dc643c72730470d72b79'),
            (checker.check_batch1047_file,
             'research/p112-free-sink-audit97/independent.py',
             '46806efe1ee7744c810a69981d471b42dfceaa336fee226991c55ba1edfd129f'),
            (checker.check_batch1099_file,
             'research/r439-omission-atlas-seed81/README.md',
             '6fc756df2aa0afe5b63985c1a5b4878659a3387250092e9ae5167f3316d5de9f'),
            (checker.check_batch1099_file,
             'research/r439-omission-atlas-seed81/verify.py',
             '127d7679fb26e264018548a1301b2f0f437d834eb1f0ffa215556243077ff866'),
        )
        for check, path, predecessor in cases:
            item = {'integrated_path': path, 'integrated_sha256': predecessor}
            with self.subTest(path=path):
                check(item)
                forged = dict(item, integrated_sha256='0' * 64)
                with self.assertRaises(ValueError):
                    check(forged)
                original_read = Path.read_bytes
                def read(target):
                    return original_read(target) + b' ' if target == ROOT / path else original_read(target)
                with patch.object(Path, 'read_bytes', read), self.assertRaises(ValueError):
                    check(item)


class AssertionSafetyRefresh(unittest.TestCase):
    def setUp(self):
        coverage = json.loads((ROOT / 'research/community-batch932-audit/CONTENT-COVERAGE.json').read_bytes())
        self.items = [deepcopy(item) for row in coverage['pull_requests'].values()
                      for item in row['files'] if item.get('integrated_path') in {
                          'scripts/run_isolated_tests.py', 'tests/test_isolated_test_runner.py',
                          'research/data-corner-performance/README.md',
                          'research/data-corner-performance/SOURCE.json',
                          'research/data-corner-performance/replay.py',
                          'research/data-corner-performance/test_replay.py'}]

    def test_exact_accepted_successors_pass(self):
        self.assertEqual(len(self.items), 6)
        for item in self.items:
            checker.check_batch932_file(item)

    def test_historical_adapter_cannot_be_disabled(self):
        item = next(item for item in self.items if item['integrated_path'].startswith('scripts/'))
        current = (ROOT / item['integrated_path']).read_bytes()
        mutated = current.replace(b"path.name in legacy", b'False')
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
