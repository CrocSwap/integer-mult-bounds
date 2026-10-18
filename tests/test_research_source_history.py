"""Publication history controls use synthetic Git objects, without remote fetches."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import check_research_commit as checker

sys.path.pop(0)


class SourceHistoryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = 'research/fixture'
        self.path = self.root / self.package
        self.path.mkdir(parents=True)
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'core.autocrlf', 'false')
        (self.path / 'VERIFY.json').write_text('{"inputs":[]}\n', encoding='utf-8')
        (self.path / 'input.txt').write_text('unchanged source\n', encoding='utf-8')
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture base')
        self.base = self.git('rev-parse', 'HEAD').strip()

    def git(self, *args, data=None):
        result = subprocess.run(['git', *args], cwd=self.root, input=data,
                                capture_output=True, text=True, timeout=30, check=True)
        return result.stdout

    def publish(self, rows=(), base=None):
        sources = {'base_commit': base or self.base, 'files': list(rows)}
        (self.path / 'SOURCES.json').write_text(json.dumps(sources), encoding='utf-8')
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture publication')
        return self.git('rev-parse', 'HEAD').strip()

    def row(self, commit=None, name='research/fixture/input.txt'):
        row = {'path': name, 'usage': 'provenance'}
        if commit is not None:
            row['pin'] = 'head:' + commit + ':' + name
        return row

    def check(self, ref='HEAD', history=True):
        return checker.check(self.root, self.package, ref, check_source_history=history)

    def test_base_and_explicit_ancestor_pins_are_deduplicated(self):
        head = self.publish([self.row(), self.row(self.base), self.row(self.base)])
        result = self.check()
        self.assertEqual(result['commit'], head)
        self.assertEqual(result['source_history_commits'], [self.base])
        self.assertEqual(self.check(history=False),
                         {'commit': head, 'files': 3, 'package': self.package})

    def test_cached_side_commit_passes_bytes_but_not_publication_history(self):
        tree = self.git('rev-parse', self.base + '^{tree}').strip()
        foreign = self.git('commit-tree', tree, '-p', self.base,
                           data='unmerged dependency\n').strip()
        head = self.publish([self.row(foreign)])
        self.assertEqual(self.git('cat-file', '-t', foreign).strip(), 'commit')
        reachable = self.git('rev-list', '--objects', head).splitlines()
        self.assertFalse(any(line.split()[0] == foreign for line in reachable))
        self.assertEqual(self.check(history=False)['commit'], head)
        with self.assertRaisesRegex(ValueError, 'not an ancestor.*' + foreign):
            self.check()
        # A separate local branch does not change the publication's history.
        self.git('update-ref', 'refs/heads/other-research', foreign)
        with self.assertRaisesRegex(ValueError, 'not an ancestor'):
            self.check()
        self.assertEqual(self.git('status', '--porcelain'), '')

    def test_synthetic_cold_object_inventory_has_no_foreign_commit(self):
        tree = self.git('rev-parse', self.base + '^{tree}').strip()
        foreign = self.git('commit-tree', tree, '-p', self.base, data='foreign\n').strip()
        head = self.publish([self.row(foreign)])
        pack = subprocess.run(['git', 'pack-objects', '--stdout', '--revs'],
                              cwd=self.root, input=(head + '\n').encode('ascii'),
                              capture_output=True, check=True, timeout=30).stdout
        # This is an empty synthetic bare test repository, not a clone or
        # another project checkout. Only this publication's object closure enters.
        cold = self.root / 'cold.git'
        subprocess.run(['git', 'init', '--bare', '-q', str(cold)],
                       capture_output=True, check=True, timeout=30)
        subprocess.run(['git', 'index-pack', '--stdin'], cwd=cold, input=pack,
                       capture_output=True, check=True, timeout=30)
        missing = subprocess.run(['git', 'cat-file', '-e', foreign], cwd=cold,
                                 capture_output=True, check=False, timeout=30)
        self.assertNotEqual(missing.returncode, 0)
        with self.assertRaisesRegex(ValueError, 'unavailable source commit.*' + foreign):
            checker.source_history(cold, self.package, head)
        repaired = self.publish([self.row(self.base)])
        pack = subprocess.run(['git', 'pack-objects', '--stdout', '--revs'],
                              cwd=self.root, input=(repaired + '\n').encode('ascii'),
                              capture_output=True, check=True, timeout=30).stdout
        subprocess.run(['git', 'index-pack', '--stdin'], cwd=cold, input=pack,
                       capture_output=True, check=True, timeout=30)
        self.assertEqual(checker.source_history(cold, self.package, repaired), [self.base])

    def test_local_replacements_and_grafts_cannot_supply_publication_ancestry(self):
        tree = self.git('rev-parse', self.base + '^{tree}').strip()
        foreign = self.git('commit-tree', tree, '-p', self.base, data='foreign\n').strip()
        head = self.publish([self.row(foreign)])
        self.git('replace', '--graft', head, foreign)
        self.git('merge-base', '--is-ancestor', foreign, head)
        with self.assertRaisesRegex(ValueError, 'not an ancestor'):
            self.check()
        self.git('replace', '-d', head)
        grafts = self.root / '.git/info/grafts'
        grafts.write_text(head + ' ' + foreign + '\n', encoding='ascii')
        self.git('merge-base', '--is-ancestor', foreign, head)
        before = grafts.read_bytes()
        with self.assertRaisesRegex(ValueError, 'not an ancestor'):
            self.check()
        self.assertEqual(grafts.read_bytes(), before)

    def test_history_uses_committed_metadata_and_transport_rejects_working_drift(self):
        head = self.publish()
        (self.path / 'SOURCES.json').write_text(
            json.dumps({'base_commit': head, 'files': [self.row('1' * 40)]}), encoding='utf-8')
        self.assertEqual(checker.source_history(self.root, self.package, head), [self.base])
        with self.assertRaisesRegex(ValueError, 'bytes differ.*SOURCES.json'):
            self.check()

    def test_unavailable_and_noncommit_base_are_rejected(self):
        self.publish(base='1' * 40)
        with self.assertRaisesRegex(ValueError, 'unavailable source commit'):
            self.check()
        blob = self.git('rev-parse', self.base + ':research/fixture/input.txt').strip()
        self.publish(base=blob)
        with self.assertRaisesRegex(ValueError, 'unavailable source commit'):
            self.check()

    def test_malformed_pin_and_base_are_rejected(self):
        for base, pin in [('main', None), (self.base, 'external:somewhere'),
                          (self.base, 'head:' + self.base + ':different-path')]:
            with self.subTest(base=base, pin=pin):
                row = self.row()
                if pin is not None:
                    row['pin'] = pin
                self.publish([row], base)
                with self.assertRaisesRegex(ValueError, 'base_commit|supported pin form'):
                    self.check()

    def test_missing_source_inventory_is_rejected_only_when_requested(self):
        self.assertEqual(self.check(history=False)['files'], 2)
        with self.assertRaisesRegex(ValueError, 'missing publication SOURCES.json'):
            self.check()

    def test_shallow_history_fails_closed_without_changing_it(self):
        self.publish()
        shallow = self.root / '.git/shallow'
        shallow.write_text(self.base + '\n', encoding='ascii')
        with self.assertRaisesRegex(ValueError, 'full Git history'):
            self.check()
        self.assertEqual(shallow.read_text(encoding='ascii'), self.base + '\n')

    def test_metadata_shape_and_resource_bounds(self):
        self.publish()
        for value in [[], {'base_commit': self.base, 'files': {}},
                      {'base_commit': self.base, 'files': [None]},
                      {'base_commit': self.base, 'files': [{'path': None}]}]:
            with self.subTest(value=value):
                (self.path / 'SOURCES.json').write_text(json.dumps(value), encoding='utf-8')
                self.git('add', '.')
                self.git('commit', '-qm', 'malformed metadata')
                with self.assertRaises(ValueError):
                    self.check()
        with (patch.object(checker, 'MAX_SOURCE_METADATA_BYTES', 8),
              self.assertRaisesRegex(ValueError, 'source metadata byte limit')):
            self.check()
        with patch.object(checker, 'MAX_SOURCE_ROWS', 1):
            self.publish([self.row(), self.row()])
            with self.assertRaisesRegex(ValueError, 'source row limit'):
                self.check()
        with patch.object(checker, 'MAX_SOURCE_COMMITS', 1):
            self.publish([self.row('2' * 40)])
            with self.assertRaisesRegex(ValueError, 'source commit limit'):
                self.check()

    def test_real_cli_is_read_only_and_reports_no_pass_on_history_failure(self):
        for name in ('check_research_commit.py', 'research_package.py'):
            destination = self.root / 'scripts' / name
            destination.parent.mkdir(exist_ok=True)
            destination.write_bytes((ROOT / 'scripts' / name).read_bytes())
        self.publish([self.row()])
        command = [sys.executable, '-B', str(self.root / 'scripts/check_research_commit.py'),
                   '--package', self.package, '--check-source-history']
        good = subprocess.run(command, cwd=self.root, capture_output=True, check=False, timeout=30)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertIn(b'"source_history_commits"', good.stdout)
        tree = self.git('rev-parse', self.base + '^{tree}').strip()
        foreign = self.git('commit-tree', tree, '-p', self.base, data='foreign\n').strip()
        self.publish([self.row(foreign)])
        before = self.git('rev-parse', 'HEAD'), self.git('ls-files', '--stage', '-z')
        bad = subprocess.run(command, cwd=self.root, capture_output=True, check=False, timeout=30)
        self.assertEqual(bad.returncode, 1)
        self.assertIn(b'not an ancestor', bad.stderr)
        self.assertNotIn(b'PASS_', bad.stdout)
        self.assertEqual(before, (self.git('rev-parse', 'HEAD'),
                                  self.git('ls-files', '--stage', '-z')))
        default = subprocess.run(command[:-1], cwd=self.root, capture_output=True, check=False, timeout=30)
        self.assertEqual(default.returncode, 0, default.stderr)

    def test_git_errors_and_timeout_are_not_accepted_as_ancestry(self):
        self.publish([self.row()])
        with (patch.object(checker, 'history_git', side_effect=subprocess.TimeoutExpired('git', 30)),
              self.assertRaises(subprocess.TimeoutExpired)):
            self.check()
        original = checker.history_git

        def broken(root, *args):
            if args[0] == 'merge-base':
                return subprocess.CompletedProcess(args, 128, b'', b'fatal: history read failed')
            return original(root, *args)

        with (patch.object(checker, 'history_git', side_effect=broken),
              self.assertRaisesRegex(ValueError, 'history read failed')):
            self.check()


if __name__ == '__main__':
    unittest.main()
