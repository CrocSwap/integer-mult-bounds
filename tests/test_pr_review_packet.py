import importlib.util
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('packets', Path(__file__).resolve().parents[1] / 'scripts/pr_review_packet.py')
packets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packets)


class PacketTests(unittest.TestCase):
    def test_complete_diff_and_mode_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def g(*args):
                return subprocess.check_output(['git', '-C', tmp, '-c', 'user.name=Test',
                                                '-c', 'user.email=test@example.invalid', *args], stderr=subprocess.DEVNULL).decode().strip()
            g('init')
            (root / 'old').write_text('old')
            (root / 'script').write_text('same')
            g('add', '.'); g('commit', '-m', 'base')
            base = g('rev-parse', 'HEAD')
            (root / 'old').unlink()
            (root / 'new').write_text('new')
            g('add', '-A'); g('update-index', '--chmod=+x', 'script'); g('commit', '-m', 'change')
            head = g('rev-parse', 'HEAD')
            metadata = dict(number=1, title='test', author={'login': 'test'}, headRefOid=head,
                            baseRefOid=base, files=[{'path': 'new'}])
            result = packets.packet(root, metadata, base)
            self.assertEqual(result['complete_git_file_count'], 3)
            bypath = {r['path']: r for r in result['files']}
            self.assertEqual(bypath['old']['change'], 'delete')
            self.assertEqual(bypath['script']['baseline_relation'], 'different_on_baseline')
            self.assertEqual(bypath['new']['baseline_relation'], 'absent_on_baseline')
            same = packets.packet(root, metadata, head)
            self.assertTrue(all(r['baseline_relation'] == 'identical' for r in same['files']))
            self.assertIsNone(same['decision'])


class PacketIdentityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        def git(*args):
            return subprocess.check_output(['git', '-C', str(self.root), '-c', 'user.name=Fixture',
                                            '-c', 'user.email=fixture@example.invalid', *args],
                                           stderr=subprocess.DEVNULL).decode().strip()
        git('init')
        git('config', 'core.autocrlf', 'false')
        (self.root / 'base').write_bytes(b'base')
        git('add', '.'); git('commit', '-m', 'base')
        self.base = git('rev-parse', 'HEAD')
        self.heads = []
        for name in ('first', 'second'):
            (self.root / name).write_bytes(name.encode())
            git('add', name); git('commit', '-m', name)
            self.heads.append(git('rev-parse', 'HEAD'))
        self.metadata = [dict(number=7, title='Fixture', author={'login': 'fixture'},
                              headRefOid=head, baseRefOid=self.base, files=[])
                         for head in self.heads]

    def cli(self, rows, label):
        paths = []
        for i, row in enumerate(rows):
            path = self.root / (label + '-' + str(i) + '.json')
            path.write_text(json.dumps(row), encoding='utf-8')
            paths.append(path)
        output = self.root / label
        run = subprocess.run([sys.executable, str(Path(packets.__file__)), '--repo', str(self.root),
                              '--baseline', self.base, '--output', str(output), *map(str, paths)],
                             capture_output=True, timeout=30)
        return run, output, paths

    def test_duplicate_snapshots_reject_before_any_output_for_same_or_different_heads(self):
        for i, other in enumerate((self.metadata[0], self.metadata[1])):
            with self.subTest(different_head=bool(i)):
                run, output, _ = self.cli([self.metadata[0], other], 'duplicate-' + str(i))
                self.assertNotEqual(run.returncode, 0, run.stdout)
                self.assertIn(b'duplicate PR number', run.stderr)
                self.assertFalse(output.exists(), 'duplicate batch must not leave misleading packets')

    def test_number_is_a_positive_integer_not_an_output_path(self):
        for i, number in enumerate((True, False, 0, -1, '7', '../escaped')):
            with self.subTest(number=number):
                row = {**self.metadata[0], 'number': number}
                run, output, _ = self.cli([row], 'invalid-' + str(i))
                self.assertNotEqual(run.returncode, 0)
                self.assertIn(b'positive integer', run.stderr)
                self.assertFalse(output.exists())
        self.assertFalse((self.root / 'escaped.json').exists())

    def test_distinct_ids_preserve_full_diff_metadata_hashes_and_index(self):
        rows = [self.metadata[0], {**self.metadata[1], 'number': 8}]
        run, output, paths = self.cli(rows, 'valid')
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn(b'Wrote 2 packets', run.stdout)
        self.assertEqual({p.name for p in output.iterdir()}, {'7.json', '8.json', 'INDEX.md'})
        for index, row in enumerate(rows):
            result = json.loads((output / (str(row['number']) + '.json')).read_bytes())
            self.assertEqual(result['head'], row['headRefOid'])
            self.assertEqual(result['metadata_sha256'], hashlib.sha256(paths[index].read_bytes()).hexdigest())
            self.assertEqual(result['complete_git_file_count'], index + 1)
            self.assertEqual(result['github_reported_file_count'], 0)
            self.assertIsNone(result['decision'])
        self.assertIn('| #7 |', (output / 'INDEX.md').read_text())
        self.assertIn('| #8 |', (output / 'INDEX.md').read_text())

    def test_metadata_hash_binds_the_parsed_snapshot_if_file_changes_after_read(self):
        path = self.root / 'moving-metadata.json'
        raw = json.dumps(self.metadata[0]).encode()
        replacement = json.dumps({**self.metadata[0], 'title': 'later snapshot'}).encode()
        path.write_bytes(raw)
        read = Path.read_bytes
        def change_after_read(target):
            captured = read(target)
            if target == path:
                path.write_bytes(replacement)
            return captured
        with patch.object(Path, 'read_bytes', change_after_read):
            rows = packets.load_metadata([path])
        self.assertEqual(rows, [(self.metadata[0], hashlib.sha256(raw).hexdigest())])
        self.assertEqual(path.read_bytes(), replacement)


if __name__ == '__main__':
    unittest.main()
