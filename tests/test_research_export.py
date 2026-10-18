"""Real Git publication fixtures and offline archive corruption controls."""
from pathlib import Path
import io
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import export_research_package as exporter


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.package = 'research/fixture'
        self.output = self.root / 'bundle.tar'
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'core.autocrlf', 'false')
        self.inputs = ['inputs/a\n雪[*].bin']
        self.write(self.inputs[0], b'\x00\xff\r\n')
        self.write(self.package + '/VERIFY.json', json.dumps({'inputs': self.inputs}).encode())
        self.write(self.package + '/verify.py', b'print("PASS_FIXTURE")\n')
        self.write('.gitattributes', b'*.py export-ignore\n')
        self.commit = self.save()

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, stderr=subprocess.PIPE)

    def write(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def save(self):
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture')
        return self.git('rev-parse', 'HEAD').decode().strip()

    def export(self):
        return exporter.export(self.root, self.package, self.commit, self.output)

    def rewrite(self, transform):
        with tarfile.open(self.output) as archive:
            items = [(m, archive.extractfile(m).read()) for m in archive]
        with tarfile.open(self.output, 'w') as archive:
            for name, data, mode, kind in transform(items):
                info, stream = exporter.member(name, data, mode)
                info.type = kind
                archive.addfile(info, stream if info.isfile() else None)

    def test_repeatable_committed_bytes_ignore_worktree_and_attributes(self):
        receipt = self.export()
        self.write(self.package + '/VERIFY.json', b'{"inputs":[]}')
        (self.root / self.inputs[0]).unlink()
        self.write(self.package + '/verify.py', b'raise Exception("dirty")')
        self.write(self.package + '/untracked.py', b'pass')
        other = self.root / 'second.tar'
        exporter.export(self.root, self.package, self.commit, other)
        self.assertEqual(self.output.read_bytes(), other.read_bytes())
        with patch.object(exporter, 'git', side_effect=AssertionError('Git used offline')):
            self.assertEqual(exporter.check_bundle(other), receipt)
        with tarfile.open(other) as archive:
            self.assertEqual(archive.extractfile(self.package + '/verify.py').read(), b'print("PASS_FIXTURE")\n')

    def test_direct_replay_in_git_free_directory(self):
        self.export()
        exporter.check_bundle(self.output)
        target = self.root / 'standalone'
        target.mkdir()
        with tarfile.open(self.output) as archive:
            for item in archive:
                self.assertTrue(item.isfile())
                path = target / item.name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(archive.extractfile(item).read())
        result = subprocess.run([sys.executable, self.package + '/verify.py'], cwd=target,
                                capture_output=True, check=True)
        self.assertEqual(result.stdout, b'PASS_FIXTURE\n')
        self.assertFalse((target / '.git').exists())

    def test_missing_input_and_directory_are_rejected(self):
        for name in ['missing.bin', 'inputs']:
            self.write(self.package + '/VERIFY.json', json.dumps({'inputs': [name]}).encode())
            self.commit = self.save()
            with self.assertRaisesRegex(ValueError, 'missing declared|not a directory'):
                self.export()
            self.assertFalse(self.output.exists())

    def test_symlink_rejected(self):
        (self.root / self.package / 'alias').symlink_to('verify.py')
        self.commit = self.save()
        with self.assertRaisesRegex(ValueError, 'non-regular'):
            self.export()

    def test_bad_declarations_rejected(self):
        for inputs in [['../escape'], ['./a'], ['a', 'a'], 'a', [42]]:
            self.write(self.package + '/VERIFY.json', json.dumps({'inputs': inputs}).encode())
            self.commit = self.save()
            with self.assertRaises((ValueError, TypeError)):
                self.export()

    def test_existing_output_never_overwritten(self):
        self.output.write_bytes(b'keep')
        with self.assertRaisesRegex(ValueError, 'already exists'):
            self.export()
        self.assertEqual(self.output.read_bytes(), b'keep')

    def test_exec_mode_retained(self):
        self.git('update-index', '--chmod=+x', self.package + '/verify.py')
        self.git('commit', '-qm', 'executable')
        self.commit = self.git('rev-parse', 'HEAD').decode().strip()
        receipt = self.export()
        self.assertEqual(next(r['mode'] for r in receipt['files'] if r['path'].endswith('verify.py')), 0o755)
        exporter.check_bundle(self.output)

    def test_payload_mode_inventory_and_duplicate_controls(self):
        def convert(items):
            return [(m.name, b, m.mode, m.type) for m, b in items]
        for change in ['payload', 'mode', 'missing', 'extra', 'duplicate', 'link', 'escape', 'receipt']:
            if self.output.exists():
                self.output.unlink()
            self.export()
            def mutate(items):
                rows = convert(items)
                n, b, mode, kind = rows[0]
                if change == 'payload': rows[0] = (n, b + b'x', mode, kind)
                if change == 'mode': rows[0] = (n, b, 0o755 if mode == 0o644 else 0o644, kind)
                if change == 'missing': rows.pop(0)
                if change == 'extra': rows.append(('extra', b'x', 0o644, tarfile.REGTYPE))
                if change == 'duplicate': rows.append(rows[0])
                if change == 'link': rows[0] = (n, b'', mode, tarfile.SYMTYPE)
                if change == 'escape': rows[0] = ('../escape', b, mode, kind)
                if change == 'receipt': rows.pop()
                return rows
            self.rewrite(mutate)
            with self.subTest(change=change), self.assertRaises(ValueError):
                exporter.check_bundle(self.output)

    def test_failed_git_stream_leaves_no_output(self):
        original = exporter.git_blobs
        def fail(root, specs):
            for row in original(root, specs):
                yield row
            raise ValueError('late Git failure')
        # Use actual inventory then fail only the output stream.
        commit, entries = exporter.inventory(self.root, self.package, self.commit)
        with patch.object(exporter, 'inventory', return_value=(commit, entries)), \
             patch.object(exporter, 'git_blobs', fail), self.assertRaisesRegex(ValueError, 'late Git'):
            self.export()
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.root.glob('.research-export-*')), [])


if __name__ == '__main__':
    unittest.main()
