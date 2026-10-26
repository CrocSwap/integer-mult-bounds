"""Exact head-pin filenames through the real metadata and publication CLIs.

Builds on Aaron Wang's PR2737 head pins and Douglas Colkitt's package runner.
Prepared for roger-sato with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from research_package import source_pin
sys.path.pop(0)


class HeadPinPathTests(unittest.TestCase):
    def fixture(self, name):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.package = 'research/fixture'
        self.name = name
        (self.root / 'scripts').mkdir()
        for script in ('research_package.py', 'check_research_commit.py', 'research_windows_git.py'):
            shutil.copyfile(ROOT / 'scripts' / script, self.root / 'scripts' / script)
        self.card = {'id': 'fixture', 'question': 'Check exact source paths'}
        self.catalog = 'docs/research/agent-task-catalog.json'
        self.save(self.catalog, {'tracks': [{'tasks': [self.card]}]})
        (self.root / name).parent.mkdir(parents=True, exist_ok=True)
        (self.root / name).write_bytes(b'base input\n')
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'core.autocrlf', 'false')
        self.commit('base')
        self.base = self.git('rev-parse', 'HEAD').strip()
        self.sources = {'schema_version': 1, 'base_commit': self.base,
                        'files': [self.row(self.catalog, 'provenance'), self.row(name, 'input')]}
        self.save(self.package + '/TASK.json', {
            'schema_version': 1, 'base_commit': self.base, 'task_id': 'fixture',
            'scope_status': 'unchanged', 'original_card': self.card,
            'actual_scope': self.card['question'], 'bottleneck_link': 'Tooling fixture',
            'stop_rule': 'Complete bounded fixture', 'evidence': 'Exact source pins',
            'author': 'Fixture', 'ai_assistance': 'Test fixture', 'outcome': 'partial',
            'open_questions': [], 'no_open_questions_reason': 'Bounded regression fixture'})
        self.save(self.package + '/VERIFY.json', {
            'schema_version': 1, 'status': 'ready', 'python': '3.12', 'inputs': [name],
            'commands': [{'argv': ['{python}', '-c', 'pass'],
                          'checks': 'Fixture only', 'timeout_seconds': 1}]})
        (self.root / self.package / 'README.md').write_text('## Open next questions\n')

    def save(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding='utf-8')

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root,
                                       stderr=subprocess.PIPE, timeout=30).decode('utf-8')

    def commit(self, message):
        self.git('add', '.')
        self.git('commit', '-qm', message)

    def row(self, name, usage, commit=None):
        commit = self.base if commit is None else commit
        return {'path': name, 'usage': usage,
                'git_blob': self.git('rev-parse', commit + ':' + name).strip(),
                'sha256': hashlib.sha256((self.root / name).read_bytes()).hexdigest()}

    def cli(self, publication=False):
        self.save(self.package + '/SOURCES.json', self.sources)
        script = 'check_research_commit.py' if publication else 'research_package.py'
        if publication:
            self.commit('publication')
        flags = ['-O'] if sys.flags.optimize else []
        return subprocess.run([sys.executable, *flags, '-B', str(self.root / 'scripts' / script),
                               '--package', self.package,
                               '--check-source-history' if publication else '--check-only'],
                              cwd=self.root, capture_output=True, text=True, timeout=30)

    @unittest.skipIf(os.name == 'nt', 'fixture creates POSIX filenames containing LF')
    def test_base_and_head_pins_preserve_multiline_paths_in_both_clis(self):
        for name in ('inputs/line\nbreak.txt', 'inputs/line\r\nbreak.txt', 'inputs/trailing\n'):
            with self.subTest(name=name):
                self.fixture(name)
                for prefix in ('base_commit:', 'head:' + self.base + ':'):
                    self.sources['files'][1]['pin'] = prefix + name
                    for publication in (False, True):
                        result = self.cli(publication)
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertIn('PASS_RESEARCH_COMMIT_BYTES' if publication else
                                      'PASS_PACKAGE_METADATA_AND_PINS', result.stdout)

    @unittest.skipIf(os.name == 'nt', 'fixture creates POSIX filenames containing LF')
    def test_later_head_is_resolved_and_all_source_checks_remain_active(self):
        self.fixture('inputs/later\nhead.txt')
        (self.root / self.name).write_bytes(b'later head input\n')
        self.commit('later source')
        head = self.git('rev-parse', 'HEAD').strip()
        row = self.row(self.name, 'input', head)
        row['pin'] = 'head:' + head + ':' + self.name
        self.sources['files'][1] = row
        for publication in (False, True):
            result = self.cli(publication)
            self.assertEqual(result.returncode, 0, result.stderr)
        for field, value, message in (
                ('pin', 'base_commit:' + self.name, 'source blob provenance mismatch'),
                ('git_blob', '0' * 40, 'source blob provenance mismatch'),
                ('sha256', '0' * 64, 'source SHA256 provenance mismatch')):
            with self.subTest(field=field):
                self.sources['files'][1] = {**row, field: value}
                result = self.cli()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)
        self.sources['files'][1] = row
        (self.root / self.name).write_bytes(b'working drift\n')
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('working source drift', result.stderr)

    def test_malformed_head_pins_and_path_aliases_still_reject(self):
        base, name = 'a' * 40, 'inputs/line\nbreak.txt'
        for pin in ('head:' + base[:-1] + ':' + name, 'head:' + base + 'a:' + name,
                    'head:' + base.upper() + ':' + name, 'head:\n' + base + ':' + name,
                    'head:' + base + ':', 'head:' + base + ':' + name + '\n',
                    'head:' + base + ':' + name.replace('\n', '\r\n'),
                    'tag:' + base + ':' + name, 1, {}):
            with self.subTest(pin=pin), self.assertRaisesRegex(ValueError, 'supported pin form'):
                source_pin({'path': name, 'pin': pin}, base)


if __name__ == '__main__':
    unittest.main()
