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


class IntakeStartingHistory(unittest.TestCase):
    def row(self, number, head):
        return dict(number=number, metadata=dict(number=number, headRefOid=head * 40,
                                                author={'login': 'original'}))

    def test_ordered_first_appearance_and_source_immutability(self):
        history = [[self.row(7, 'a')], [self.row(7, 'b'), self.row(8, 'c')]]
        current = [self.row(7, 'd'), self.row(8, 'e'), self.row(9, 'f')]
        before = deepcopy((history, current))
        got = checker.project_intake_starting_metadata(history, current)
        self.assertEqual({n: row['headRefOid'] for n, row in got.items()},
                         {7: 'a' * 40, 8: 'c' * 40})
        got[7]['author']['login'] = 'mutation'
        self.assertEqual((history, current), before)

    def test_missing_extra_duplicate_and_malformed_history_reject(self):
        current = [self.row(7, 'b')]
        mutations = [[self.row(8, 'a')], [self.row(7, 'a'), self.row(7, 'b')],
                     [self.row(True, 'a')], [dict(number=7, metadata=self.row(8, 'a')['metadata'])],
                     [self.row(7, 'z')]]
        for rows in mutations:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                checker.project_intake_starting_metadata([rows], current)
        with self.assertRaises(ValueError):
            checker.project_intake_starting_metadata([[self.row(7, 'a')]], [])
        with self.assertRaises(ValueError):
            checker.project_intake_starting_metadata([], current + current)

    def test_complete_current_starting_metadata_matches_original_sources(self):
        snapshot = json.loads((checker.AUDIT / 'starting-snapshot.json').read_text())
        expected = {row['number']: row for row in snapshot['pull_requests']}
        for path in checker.decision_paths():
            if not path.exists():
                continue
            rows = json.loads(path.read_text())['pull_requests']
            if path.name == 'pr-intake-decisions.json':
                initial = checker.authenticated_intake_starting_metadata(ROOT, rows)
                for number, metadata in initial.items():
                    expected.setdefault(number, metadata)
            for row in rows:
                expected.setdefault(row['number'], row['metadata'])
        ledger = json.loads((ROOT / 'docs/research/pr-ledger.json').read_text())
        self.assertEqual(len(expected), len(ledger['pull_requests']))
        for item in ledger['pull_requests']:
            with self.subTest(number=item['number']):
                self.assertEqual(item['starting_head'], expected[item['number']]['headRefOid'])
                self.assertEqual(item['contributor'], expected[item['number']]['author'])

    def test_changed_swapped_or_forged_pinned_source_rejects(self):
        rows = json.loads((ROOT / 'docs/research/pr-intake-decisions.json').read_text())['pull_requests']
        directory = ROOT / 'scripts/historical-ci-inputs/intake-starting-heads'
        path = directory / (checker.INTAKE_HISTORY[0][0] + '.json')
        original = path.read_bytes()
        other = (directory / (checker.INTAKE_HISTORY[1][0] + '.json')).read_bytes()
        read_bytes = Path.read_bytes
        for changed in (original + b' ', other):
            def read(p):
                return changed if p == path else read_bytes(p)
            with patch.object(Path, 'read_bytes', read), self.assertRaisesRegex(ValueError, 'Changed historical'):
                checker.authenticated_intake_starting_metadata(ROOT, rows)
        commit, blob, digest = checker.INTAKE_HISTORY[0]
        forged = ((commit, '0' * 40, digest), *checker.INTAKE_HISTORY[1:])
        with patch.object(checker, 'INTAKE_HISTORY', forged), self.assertRaisesRegex(ValueError, 'Git blob mismatch'):
            checker.authenticated_intake_starting_metadata(ROOT, rows)

    def test_missing_and_linked_source_rejects(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(ValueError, 'Missing or linked'):
                checker.authenticated_intake_starting_metadata(root, [])
            directory = root / 'scripts/historical-ci-inputs/intake-starting-heads'
            directory.mkdir(parents=True)
            original = ROOT / 'scripts/historical-ci-inputs/intake-starting-heads' / (checker.INTAKE_HISTORY[0][0] + '.json')
            (directory / original.name).symlink_to(original)
            with self.assertRaisesRegex(ValueError, 'Missing or linked'):
                checker.authenticated_intake_starting_metadata(root, [])

    def test_entrypoint_rejects_forged_starting_and_current_heads(self):
        ledger = json.loads((ROOT / 'docs/research/pr-ledger.json').read_text())
        original_read = Path.read_text
        for number in (3107, 3184, 3251):
            for field in ('starting_head', 'reviewed_head', 'current_head'):
                changed = deepcopy(ledger)
                item = next(row for row in changed['pull_requests'] if row['number'] == number)
                item[field] = '0' * 40
                def read(path, *args, **kwargs):
                    return json.dumps(changed) if path == ROOT / 'docs/research/pr-ledger.json' else original_read(path, *args, **kwargs)
                expected = 'starting head' if field == 'starting_head' else field
                with self.subTest(number=number, field=field), patch.object(Path, 'read_text', read), self.assertRaisesRegex(ValueError, f'#{number}:.*{expected}'):
                    checker.main()

    def test_generator_keeps_original_heads_without_writing_evidence(self):
        spec = importlib.util.spec_from_file_location('history_aware_generator',
                                                     ROOT / 'scripts/reconcile_pr_queue.py')
        generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generator)
        outputs = {}
        permitted = {ROOT / 'docs/research/pr-ledger.json', ROOT / 'docs/research/pr-ledger.md'}
        def capture(path, content, *args, **kwargs):
            self.assertIn(path, permitted)
            outputs[path] = content
            return len(content)
        original = (ROOT / 'docs/research/pr-ledger.json').read_bytes()
        with patch.object(Path, 'write_text', capture), patch('builtins.print'):
            generator.build()
        self.assertEqual((ROOT / 'docs/research/pr-ledger.json').read_bytes(), original)
        self.assertEqual(set(outputs), permitted)
        rebuilt = json.loads(outputs[ROOT / 'docs/research/pr-ledger.json'])
        actual = {row['number']: row for row in json.loads(original)['pull_requests']}
        self.assertEqual(len(rebuilt['pull_requests']), len(actual))
        for row in rebuilt['pull_requests']:
            for field in ('starting_head', 'contributor', 'current_head', 'reviewed_head'):
                with self.subTest(number=row['number'], field=field):
                    self.assertEqual(row.get(field), actual[row['number']].get(field))
        for commit, _blob, digest in checker.INTAKE_HISTORY:
            name = 'scripts/historical-ci-inputs/intake-starting-heads/' + commit + '.json'
            self.assertEqual(rebuilt['source_sha256'][name], digest)


class FamilyClosureProjection(unittest.TestCase):
    def decision(self, number=7):
        return dict(number=number, reviewed_head='a' * 40, current_head='a' * 40,
                    disposition='partially_reviewed', github_state='OPEN',
                    integration_location=[], unresolved_question='Review remains open.')

    def test_closure_inheritance_and_explicit_overrides(self):
        first = {'receipt': 'first.json', 'verified': True}
        second = {'receipt': 'second.json', 'verified': True}
        cases = [
            ('baseline receipt survives omission', {'7': {'closure': first}},
             [[{'number': 7}]], first),
            ('baseline null survives omission', {'7': {'closure': None}},
             [[{'number': 7}]], None),
            ('new family record defaults to null', {}, [[{'number': 8}]], None),
            ('family receipt survives omission', {},
             [[{'number': 7, 'closure': first}], [{'number': 7}]], first),
            ('explicit null clears prior receipt', {'7': {'closure': first}},
             [[{'number': 7, 'closure': None}], [{'number': 7}]], None),
            ('explicit receipt replaces prior receipt', {'7': {'closure': first}},
             [[{'number': 7, 'closure': second}]], second),
        ]
        for label, baseline, rounds, expected in cases:
            with self.subTest(case=label):
                result = checker.project_family_closures([7], baseline, rounds)
                self.assertEqual(result[rounds[-1][-1]['number']], expected)

    def test_projection_does_not_mutate_sources_or_raw_latest_records(self):
        baseline = {'7': {'closure': {'receipt': 'baseline.json', 'checks': [True]}}}
        rounds = [[self.decision()], [self.decision()]]
        before = deepcopy((baseline, rounds))
        latest = {row['number']: row for rows in rounds for row in rows}
        result = checker.project_family_closures([7], baseline, rounds)
        self.assertEqual((baseline, rounds), before)
        self.assertIs(latest[7], rounds[-1][0])
        self.assertNotIn('closure', latest[7])
        result[7]['checks'].append(False)
        self.assertEqual((baseline, rounds), before)
        self.assertEqual(latest[7], before[1][-1][0])

    def test_missing_or_fabricated_ledger_closure_rejects_expected_null(self):
        raw = self.decision()
        closure = checker.project_family_closures([7], {}, [[raw]])[7]
        expected = {**raw, 'closure': closure}
        checker.check_family_decision(dict(expected), expected)
        for operation in ('missing', 'fabricated'):
            item = dict(expected)
            if operation == 'missing':
                item.pop('closure')
            else:
                item['closure'] = {'receipt': 'unapproved.json'}
            with self.subTest(operation=operation), self.assertRaisesRegex(ValueError, '#7:.*closure'):
                checker.check_family_decision(item, expected)

    def test_inherited_receipt_rejects_null_forgery_and_boolean_integer_mutation(self):
        receipt = {'receipt': 'approved.json', 'checks': {'published': True}}
        raw = self.decision()
        closure = checker.project_family_closures([7], {'7': {'closure': receipt}}, [[raw]])[7]
        expected = {**raw, 'closure': closure}
        checker.check_family_decision(deepcopy(expected), expected)
        for mutation in (None, {'receipt': 'other.json', 'checks': {'published': True}},
                         {'receipt': 'approved.json', 'checks': {'published': 1}}):
            item = deepcopy(expected)
            item['closure'] = mutation
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, '#7:.*closure'):
                checker.check_family_decision(item, expected)

    def test_baseline_decision_outside_starting_snapshot_rejects(self):
        with self.assertRaisesRegex(ValueError, 'outside the starting snapshot'):
            checker.project_family_closures([7], {'8': {'closure': None}}, [])


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
        snapshot = json.loads((checker.AUDIT / 'starting-snapshot.json').read_text())
        baseline = json.loads((checker.AUDIT / 'decisions.json').read_text())['decisions']
        cls.closures = checker.project_family_closures(
            (row['number'] for row in snapshot['pull_requests']), baseline, cls.families.values())

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
                checker.check_family_decision(
                    self.items[number], {**decision, 'closure': self.closures[number]})

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
        # This frozen decision recorded null; PR620's latest review has a merge receipt.
        decision = next(row for row in self.families['k492'] if row['number'] == 620)
        self.assertIsNone(decision['closure'])
        checker.check_family_decision(deepcopy(decision), decision)
        for operation in ('missing', 'fabricated'):
            item = deepcopy(decision)
            if operation == 'missing':
                item.pop('closure')
            else:
                item['closure'] = {'receipt': 'unapproved.json'}
            with self.subTest(operation=operation), self.assertRaisesRegex(
                    ValueError, '#620:.*closure'):
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


class HistoricalReviewCompletion(unittest.TestCase):
    def setUp(self):
        self.ledger = json.loads((ROOT / 'docs/research/pr-ledger.json').read_text())
        self.actual = {row['number']: row for row in self.ledger['pull_requests']}
        self.path = ROOT / 'research/community-batch1099-audit/DISPOSITIONS.json'
        self.historical = json.loads(self.path.read_text())['pull_requests']
        self.latest = {}
        for path in checker.decision_paths():
            if path.exists():
                for row in json.loads(path.read_text())['pull_requests']:
                    self.latest[row['number']] = row
        self.decision = next(row for row in self.historical if row['number'] == 1048)

    def test_all_batch1099_historical_and_current_projections(self):
        before = deepcopy((self.actual, self.historical, self.latest))
        changed = []
        for decision in self.historical:
            number = decision['number']
            item, latest = self.actual[number], self.latest[number]
            with self.subTest(number=number):
                checker.check_historical_review_completion(item, decision, latest)
            if any(item[field] != decision[field] for field in
                   ('review_completion', 'verification_evidence')):
                changed.append(number)
        self.assertEqual(changed, [1048])
        self.assertEqual((self.actual, self.historical, self.latest), before)
        self.assertTrue(self.decision['review_completion']['changed_file_coverage'])
        self.assertFalse(self.latest[1048]['review_completion']['changed_file_coverage'])
        self.assertTrue(set(self.decision['verification_evidence']).issubset(
            self.actual[1048]['verification_evidence']))
        with self.assertRaisesRegex(ValueError, 'Ledger lost'):
            checker.check_review_completion(self.actual[1048], self.decision)

    def test_latest_ledger_mutations_and_missing_fields_reject(self):
        fields = ('reviewed_head', 'current_head', 'disposition', 'closure',
                  'review_completion', 'verification_evidence')
        for field in fields:
            for remove in (False, True):
                item = deepcopy(self.actual[1048])
                if remove:
                    item.pop(field)
                else:
                    item[field] = 'forged'
                with self.subTest(field=field, remove=remove), self.assertRaises(ValueError):
                    checker.check_historical_review_completion(item, self.decision, self.latest[1048])
        item = deepcopy(self.actual[1048])
        item['review_completion']['published'] = 0
        with self.assertRaisesRegex(ValueError, 'review_completion'):
            checker.check_historical_review_completion(item, self.decision, self.latest[1048])

    def test_historical_incorporation_and_schema_invariants_reject(self):
        mutations = [dict(disposition='incorporated'), dict(verification_evidence=[])]
        flags = deepcopy(self.decision['review_completion'])
        flags['published'] = 0
        mutations.append(dict(review_completion=flags))
        for mutation in mutations:
            decision = dict(deepcopy(self.decision), **mutation)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                checker.check_historical_review_completion(self.actual[1048], decision, self.latest[1048])
        for field in ('review_completion', 'verification_evidence'):
            latest = deepcopy(self.latest[1048])
            latest.pop(field)
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'Latest family decision lacks'):
                checker.check_historical_review_completion(self.actual[1048], self.decision, latest)
        latest = dict(self.latest[1048], number=1049)
        with self.assertRaisesRegex(ValueError, 'different PR'):
            checker.check_historical_review_completion(self.actual[1048], self.decision, latest)
        latest = dict(deepcopy(self.latest[1048]), disposition='incorporated')
        item = dict(deepcopy(self.actual[1048]), disposition='incorporated')
        with self.assertRaisesRegex(ValueError, 'before review'):
            checker.check_historical_review_completion(item, self.decision, latest)

    def test_current_review_still_requires_exact_completion_binding(self):
        checker.check_historical_review_completion(self.actual[1048], self.latest[1048], self.latest[1048])
        item = deepcopy(self.actual[1048])
        item['verification_evidence'] = self.decision['verification_evidence']
        with self.assertRaisesRegex(ValueError, 'verification_evidence'):
            checker.check_historical_review_completion(item, self.latest[1048], self.latest[1048])

    def test_entrypoint_authenticates_superseded_source_bytes(self):
        original = self.path.read_bytes()
        original_read = Path.read_bytes
        # The historical row is no longer the latest ledger projection. Its
        # source hash must nevertheless reject even a whitespace-only change.
        def read(path):
            return original + b' ' if path == self.path else original_read(path)
        with patch.object(Path, 'read_bytes', read), self.assertRaisesRegex(ValueError, 'Stale source:.*batch1099'):
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
