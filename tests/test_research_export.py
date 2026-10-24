"""Real Git publication fixtures and offline archive corruption controls.

Native Windows fixture repair prepared for Mihir Srivastava with substantial
OpenAI Codex assistance, retaining Tekalign's exporter tests. Apache-2.0.
"""
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
        # Extraction needs a filename the host can materialize. The separate
        # Git-only test retains the newline and wildcard path coverage.
        self.inputs = ['inputs/雪.bin']
        self.write(self.inputs[0], b'\x00\xff\r\n')
        self.write(self.package + '/VERIFY.json', json.dumps({'inputs': self.inputs}).encode())
        self.write(self.package + '/verify.py', b'print("PASS_FIXTURE")\n')
        self.write('.gitattributes', b'*.py export-ignore\n')
        self.commit = self.save()

    def git(self, *args, data=None):
        return subprocess.check_output(['git', *args], cwd=self.root,
                                       input=data, stderr=subprocess.PIPE, timeout=30)

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

    def test_git_only_newline_unicode_wildcard_path_preserves_bytes(self):
        # Git objects can contain names that Windows cannot check out. Use the
        # actual object store and exporter, without an index or worktree alias.
        name = 'inputs/a\n雪[*].bin'
        payload = b'\x00\xff\r\n'
        blob = self.git('hash-object', '-w', '--stdin', data=payload).decode().strip()
        manifest = self.git('hash-object', '-w', '--stdin', data=json.dumps(
            {'inputs': [name]}).encode('utf-8')).decode().strip()

        def tree(*entries):
            raw = ''.join(f'{mode} {kind} {obj}\t{path}\0'
                          for mode, kind, obj, path in entries).encode('utf-8')
            return self.git('mktree', '-z', data=raw).decode().strip()

        inputs = tree(('100644', 'blob', blob, name.split('/', 1)[1]))
        fixture = tree(('100644', 'blob', manifest, 'VERIFY.json'))
        research = tree(('040000', 'tree', fixture, 'fixture'))
        root = tree(('040000', 'tree', inputs, 'inputs'),
                    ('040000', 'tree', research, 'research'))
        self.commit = self.git('commit-tree', root, '-m', 'Git-only names').decode().strip()
        self.assertEqual(self.git('ls-tree', '-r', '-z', '--name-only', self.commit),
                         (name + '\0' + self.package + '/VERIFY.json\0').encode('utf-8'))

        receipt = self.export()
        other = self.root / 'second.tar'
        exporter.export(self.root, self.package, self.commit, other)
        self.assertEqual(self.output.read_bytes(), other.read_bytes())
        with patch.object(exporter, 'git', side_effect=AssertionError('Git used offline')):
            self.assertEqual(exporter.check_bundle(other), receipt)
        self.assertEqual({row['path'] for row in receipt['files']},
                         {name, self.package + '/VERIFY.json'})
        with tarfile.open(other) as archive:
            self.assertEqual(archive.extractfile(name).read(), payload)
            self.assertEqual(json.load(archive.extractfile(self.package + '/VERIFY.json')),
                             {'inputs': [name]})

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
        self.assertEqual((target / self.inputs[0]).read_bytes(), b'\x00\xff\r\n')
        result = subprocess.run([sys.executable, self.package + '/verify.py'], cwd=target,
                                capture_output=True, check=True, text=True, encoding='utf-8',
                                timeout=30)
        # Only the console receipt uses universal newlines; archive payloads
        # above remain byte-exact, including their embedded CRLF.
        self.assertEqual(result.stdout, 'PASS_FIXTURE\n')
        self.assertFalse((target / '.git').exists())

    def test_missing_input_and_directory_are_rejected(self):
        for name in ['missing.bin', 'inputs']:
            self.write(self.package + '/VERIFY.json', json.dumps({'inputs': [name]}).encode())
            self.commit = self.save()
            with self.assertRaisesRegex(ValueError, 'missing declared|not a directory'):
                self.export()
            self.assertFalse(self.output.exists())

    def test_symlink_rejected(self):
        # The exporter reads committed modes, so no OS symlink privilege is
        # needed to exercise its real non-regular-file rejection.
        link = self.git('hash-object', '-w', '--stdin', data=b'verify.py').decode().strip()
        self.git('update-index', '--add', '--cacheinfo', '120000', link,
                 self.package + '/alias')
        self.git('commit', '-qm', 'symbolic link')
        self.commit = self.git('rev-parse', 'HEAD').decode().strip()
        self.assertIn(b'120000 blob ' + link.encode() + b'\t',
                      self.git('ls-tree', self.commit, '--', self.package + '/alias'))
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
