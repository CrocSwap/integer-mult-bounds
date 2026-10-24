"""Historical helper authentication and current-helper replay remain separate.

Arham Tahir's source-bound differential and registered commands are unchanged.
Prepared for roger-sato with substantial OpenAI Codex assistance. Apache-2.0.
"""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = '20ecf2891d80b5acf18d980b2164fb44ea7faa90'
PACKAGE = 'research/isolated-descendant-bytecode'
HELPER = 'scripts/research_package.py'
HISTORY_TEST = 'tests/test_research_source_history.py'


def git(root, *args):
    return subprocess.check_output(['git', '--no-replace-objects', *args], cwd=root,
                                   stderr=subprocess.PIPE, timeout=30)


class DescendantSourceRoleTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.original = json.loads(git(ROOT, 'show', ORIGINAL + ':' + PACKAGE + '/SOURCES.json'))
        self.manifest = json.loads((ROOT / PACKAGE / 'VERIFY.json').read_bytes())
        names = set(self.manifest['inputs']) | {
            PACKAGE + '/' + name for name in
            ('SOURCES.json', 'VERIFY.json', 'TASK.json', 'README.md', 'verify.py', 'RESULT.json')}
        for name in names:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        # These tests vary HELPER/HISTORY_TEST source roles. Keep the unrelated
        # checker input at this package's authenticated historical bytes; a live
        # checker successor otherwise masks the predicate each test exercises.
        checker = 'scripts/check_research_commit.py'
        row = next(row for row in self.original['files'] if row['path'] == checker)
        (self.root / checker).write_bytes(git(ROOT, 'cat-file', 'blob', row['git_blob']))
        git(self.root, 'init', '-q')
        objects = Path(git(ROOT, 'rev-parse', '--git-path', 'objects').decode().strip())
        if not objects.is_absolute():
            objects = ROOT / objects
        (self.root / '.git/objects/info/alternates').write_text(str(objects.resolve()) + '\n')
        git(self.root, 'config', 'user.name', 'Fixture')
        git(self.root, 'config', 'user.email', 'fixture@example.invalid')
        git(self.root, 'config', 'core.autocrlf', 'false')
        self.commit()

    def commit(self):
        git(self.root, 'add', '.')
        git(self.root, 'commit', '-qm', 'fixture')

    def write_sources(self, value):
        (self.root / PACKAGE / 'SOURCES.json').write_text(json.dumps(value), encoding='utf-8')

    def cli(self, script='research_package.py', arguments=None, timeout=60):
        if arguments is None:
            arguments = ['--package', PACKAGE, '--check-only']
        flags = ['-O'] if sys.flags.optimize else []
        return subprocess.run([sys.executable, *flags, '-B', str(self.root / 'scripts' / script),
                               *arguments], cwd=self.root, capture_output=True, text=True, timeout=timeout)

    def test_only_source_role_changes_and_frozen_evidence_is_retained(self):
        expected = copy.deepcopy(self.original)
        for name in (HELPER, HISTORY_TEST):
            row = next(row for row in expected['files'] if row['path'] == name)
            self.assertEqual(row['usage'], 'input')
            row['usage'] = 'provenance'
        self.assertEqual(json.loads((ROOT / PACKAGE / 'SOURCES.json').read_bytes()), expected)
        for name in ('VERIFY.json', 'TASK.json', 'verify.py', 'RESULT.json'):
            with self.subTest(name=name):
                self.assertEqual((ROOT / PACKAGE / name).read_bytes(),
                                 git(ROOT, 'show', ORIGINAL + ':' + PACKAGE + '/' + name))
        self.assertIn(HELPER, self.manifest['inputs'])
        self.assertIn(HISTORY_TEST, self.manifest['inputs'])
        self.assertEqual(len(self.manifest['commands']), 3)

    def test_original_gate_rejects_but_correct_role_accepts_current_helper(self):
        # The same harmless change demonstrates the old gate on any successor.
        helper = self.root / HELPER
        helper.write_bytes(helper.read_bytes() + b'\n# compatible fixture comment\n')
        migrated = json.loads((self.root / PACKAGE / 'SOURCES.json').read_bytes())
        self.write_sources(self.original)
        before = self.cli()
        self.assertNotEqual(before.returncode, 0)
        self.assertIn('working source drift: ' + HELPER, before.stderr)
        self.write_sources(migrated)
        after = self.cli()
        self.assertEqual(after.returncode, 0, after.stderr)
        self.assertIn('PASS_PACKAGE_METADATA_AND_PINS', after.stdout)

    def test_live_history_guard_is_not_a_historical_source_substitution(self):
        # An unimportable live test must not replace the authenticated original
        # test copied by verify.py's pinned_sources() into the historical runs.
        live = self.root / HISTORY_TEST
        live.write_bytes(live.read_bytes() + b'\nraise RuntimeError("LIVE_HISTORY_SENTINEL")\n')
        # The complete hook has three separately bounded commands, not one
        # metadata check. Allow their declared budgets plus startup overhead.
        budget = sum(c['timeout_seconds'] for c in self.manifest['commands']) + 30
        result = self.cli(arguments=['--package', PACKAGE], timeout=budget)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('PASS_ISOLATED_DESCENDANT_BYTECODE', result.stdout)
        self.assertIn('PASS_REGISTERED_RESEARCH_PACKAGE', result.stdout)
        self.assertNotIn('LIVE_HISTORY_SENTINEL', result.stderr)

    def test_original_history_input_role_rejects_live_guard_successor(self):
        migrated = json.loads((self.root / PACKAGE / 'SOURCES.json').read_bytes())
        original_role = copy.deepcopy(migrated)
        next(row for row in original_role['files']
             if row['path'] == HISTORY_TEST)['usage'] = 'input'
        self.write_sources(original_role)
        before = self.cli()
        self.assertNotEqual(before.returncode, 0)
        self.assertIn('working source drift: ' + HISTORY_TEST, before.stderr)
        self.write_sources(migrated)
        after = self.cli()
        self.assertEqual(after.returncode, 0, after.stderr)

    def test_historical_history_test_pin_corruption_rejects(self):
        sources = json.loads((self.root / PACKAGE / 'SOURCES.json').read_bytes())
        for field, value, message in (
                ('git_blob', '0' * 40, 'source blob provenance mismatch'),
                ('sha256', '0' * 64, 'source SHA256 provenance mismatch')):
            with self.subTest(field=field):
                corrupted = copy.deepcopy(sources)
                next(row for row in corrupted['files']
                     if row['path'] == HISTORY_TEST)[field] = value
                self.write_sources(corrupted)
                result = self.cli()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message + ': ' + HISTORY_TEST, result.stderr)
                self.assertNotIn('PASS_PACKAGE', result.stdout)

    def test_live_history_test_remains_a_planner_and_publication_input(self):
        base = git(self.root, 'rev-parse', 'HEAD').decode().strip()
        live = self.root / HISTORY_TEST
        live.write_bytes(live.read_bytes() + b'\n# maintenance guard successor\n')
        result = self.cli('check_research_commit.py', ['--package', PACKAGE])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('working/commit bytes differ: ' + HISTORY_TEST, result.stderr)
        self.commit()
        explanation = self.root / 'history-plan.json'
        result = self.cli(arguments=['--changed-since', base, '--explain-plan', str(explanation)])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {'include': [{'package': PACKAGE}]})
        causes = json.loads(explanation.read_bytes())['selected'][0]['causes']
        self.assertEqual(causes['declared_inputs'], [HISTORY_TEST])

    def test_historical_blob_and_hash_corruption_still_rejects(self):
        sources = json.loads((self.root / PACKAGE / 'SOURCES.json').read_bytes())
        for field, value, message in (
                ('git_blob', '0' * 40, 'source blob provenance mismatch'),
                ('sha256', '0' * 64, 'source SHA256 provenance mismatch')):
            with self.subTest(field=field):
                corrupted = copy.deepcopy(sources)
                next(row for row in corrupted['files'] if row['path'] == HELPER)[field] = value
                self.write_sources(corrupted)
                result = self.cli()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message + ': ' + HELPER, result.stderr)
                self.assertNotIn('PASS_PACKAGE', result.stdout)

    def test_unrelated_live_input_drift_still_rejects(self):
        name = 'scripts/check_research_commit.py'
        path = self.root / name
        path.write_bytes(path.read_bytes() + b'\n# unpinned fixture change\n')
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('working source drift: ' + name, result.stderr)

    def test_current_helper_remains_a_planner_and_publication_input(self):
        base = git(self.root, 'rev-parse', 'HEAD').decode().strip()
        helper = self.root / HELPER
        helper.write_bytes(helper.read_bytes() + b'\n# current input change\n')
        result = self.cli('check_research_commit.py', ['--package', PACKAGE])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('working/commit bytes differ: ' + HELPER, result.stderr)
        self.commit()
        explanation = self.root / 'plan.json'
        result = self.cli(arguments=['--changed-since', base, '--explain-plan', str(explanation)])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {'include': [{'package': PACKAGE}]})
        selected = json.loads(explanation.read_bytes())['selected']
        self.assertEqual(selected[0]['causes']['declared_inputs'], [HELPER])

    def test_broken_live_cache_isolation_fails_the_unchanged_registered_command(self):
        helper = self.root / HELPER
        source = helper.read_bytes()
        protected = b'run_command(isolated_python_argv(argv, cache), cwd, timeout)'
        self.assertEqual(source.count(protected), 1)
        helper.write_bytes(source.replace(protected, b'run_command(argv, cwd, timeout)'))
        command = self.manifest['commands'][2]
        argv = [sys.executable if value == '{python}' else value.replace('{package}', PACKAGE)
                for value in command['argv']]
        env = os.environ.copy()
        env.pop('PYTHONOPTIMIZE', None)
        result = subprocess.run(argv, cwd=self.root, env=env, capture_output=True, text=True,
                                timeout=command['timeout_seconds'])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Ran 8 tests', result.stderr)
        self.assertIn('UNVERIFIED_BYTECODE_SENTINEL', result.stderr)
        self.assertIn('FAILED', result.stderr)


if __name__ == '__main__':
    unittest.main()
