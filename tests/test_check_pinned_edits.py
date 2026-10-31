"""A branch that changes hash-pinned bytes must report each stale or rewritten pin."""
from contextlib import redirect_stdout
from hashlib import sha256
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('check_pinned_edits', ROOT / 'scripts/check_pinned_edits.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)
ENV = {**os.environ, 'GIT_AUTHOR_NAME': 't', 'GIT_AUTHOR_EMAIL': 't@example.invalid',
       'GIT_COMMITTER_NAME': 't', 'GIT_COMMITTER_EMAIL': 't@example.invalid', 'GIT_CONFIG_GLOBAL': os.devnull}


def digest(data):
    return sha256(data).hexdigest()


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.run_git('init', '-q', '-b', 'main')
        self.write('research/pkg/RESULT.json', b'{"kappa": "1/3"}\n')
        self.write('research/pkg/notes.md', b'unpinned\n')
        self.write('research/pkg/data.bin', b'\0binary\0')
        old = digest(b'{"kappa": "1/3"}\n')
        selected = json.dumps({'source_sha256': old}).encode()
        self.write('certificates/selected.json', selected)
        self.write('research/other/SOURCES.json',
                   json.dumps({'files': [{'path': 'research/pkg/RESULT.json', 'sha256': old}]}).encode())
        # A package records the selected record it was written against: context, not a frozen input.
        self.write('research/other/README.md',
                   ('Pinned at `%s`; selected record `%s`.\n' % (old, digest(selected))).encode())
        self.commit('base')
        self.run_git('switch', '-q', '-c', 'branch')

    def tearDown(self):
        self.tmp.cleanup()

    def run_git(self, *args):
        subprocess.run(['git', *args], cwd=self.root, env=ENV, check=True, capture_output=True)

    def write(self, rel, data):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def commit(self, message):
        self.run_git('add', '-A')
        self.run_git('commit', '-q', '-m', message)

    def report(self):
        return guard.check(self.root, 'main', 'HEAD')

    def test_unpinned_edit_is_clean(self):
        self.write('research/pkg/notes.md', b'edited\n')
        self.commit('edit unpinned note')
        report = self.report()
        self.assertEqual((report['changed_files'], report['pins'], report['stale']), (1, [], 0))
        with redirect_stdout(io.StringIO()):
            self.assertEqual(guard.main(['--root', str(self.root), '--base', 'main']), 0)

    def test_in_place_edit_reports_every_stale_pin(self):
        self.write('research/pkg/RESULT.json', b'{"kappa": "1/2"}\n')
        self.commit('retune in place')
        report = self.report()
        self.assertEqual(report['stale'], 3)
        self.assertEqual({row['pinner'] for row in report['pins']},
                         {'certificates/selected.json', 'research/other/SOURCES.json', 'research/other/README.md'})
        self.assertTrue(all(row['pinned'] == 'research/pkg/RESULT.json' and row['change'] == 'modified'
                            for row in report['pins']))
        with redirect_stdout(io.StringIO()):
            self.assertEqual(guard.main(['--root', str(self.root), '--base', 'main']), 1)

    def test_repinned_and_removed_pinners_are_reported_but_not_stale(self):
        new = digest(b'{"kappa": "1/2"}\n')
        self.write('research/pkg/RESULT.json', b'{"kappa": "1/2"}\n')
        self.write('certificates/selected.json', json.dumps({'source_sha256': new}).encode())
        self.write('research/other/SOURCES.json', json.dumps({'files': [{'path': 'research/pkg/RESULT.json', 'sha256': new}]}).encode())
        (self.root / 'research/other/README.md').unlink()
        self.commit('rewrite pins')
        states = {row['pinner']: row['state'] for row in self.report()['pins']}
        self.assertEqual(states, {'certificates/selected.json': 'repinned', 'research/other/SOURCES.json': 'repinned',
                                  'research/other/README.md': 'pinner_removed'})
        self.assertEqual(self.report()['stale'], 0)

    def test_deletion_and_binary_files(self):
        (self.root / 'research/pkg/RESULT.json').unlink()
        self.write('research/pkg/data.bin', b'\0changed\0')
        self.commit('delete pinned file')
        report = self.report()
        self.assertEqual(report['changed_files'], 2)
        self.assertEqual({row['change'] for row in report['pins']}, {'deleted'})
        self.assertEqual(report['stale'], 3)

    def test_living_record_update_is_advisory_unless_strict(self):
        self.write('certificates/selected.json', b'{"source_sha256": "next record"}')
        self.commit('maintainer updates the selected record')
        report = self.report()
        self.assertEqual((report['stale'], report['frozen_stale']), (1, 0))
        self.assertEqual(report['pins'][0]['pinner'], 'research/other/README.md')
        argv = ['--root', str(self.root), '--base', 'main']
        with redirect_stdout(io.StringIO()):
            self.assertEqual(guard.main(argv), 0)
            self.assertEqual(guard.main(argv + ['--strict']), 1)

    def test_uses_merge_base_not_moved_main(self):
        self.write('research/pkg/notes.md', b'branch edit\n')
        self.commit('branch')
        self.run_git('switch', '-q', 'main')
        self.write('research/pkg/RESULT.json', b'{"kappa": "2/5"}\n')
        self.commit('main moved on')
        self.run_git('switch', '-q', 'branch')
        report = self.report()
        self.assertEqual((report['changed_files'], report['stale']), (1, 0))


if __name__ == '__main__':
    unittest.main()
