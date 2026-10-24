"""Export containment must not depend on the producer's path platform.

Git-object fixture portability prepared for Mihir Srivastava with substantial
OpenAI Codex assistance. Retains roger-sato's boundary regressions, Tekalign's
exporter and the object-tree fixture precedent in PR4579. Apache-2.0.
"""
import hashlib
import json
import ntpath
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import export_research_package as exporter
from research_package import canonical_relative_path
sys.path.pop(0)


class ExportDrivePathTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.package = 'research/fixture'
        self.input_payload = b'\x00\xffcommitted input\r\n'

    def bundle(self, names, receipt_name=None):
        payloads = {self.package + '/VERIFY.json': b'{"inputs": []}\n',
                    **{name: b'fixture input\n' for name in names}}
        receipt = {'format': exporter.FORMAT, 'commit': 'a' * 40,
                   'package': self.package, 'files': []}
        archive = self.root / 'fixture.tar'
        with tarfile.open(archive, 'w', format=tarfile.PAX_FORMAT) as stream:
            for name, data in payloads.items():
                stream.addfile(*exporter.member(name, data))
                receipt['files'].append({'path': receipt_name if name in names and receipt_name else name,
                                         'mode': 0o644, 'size': len(data),
                                         'sha256': hashlib.sha256(data).hexdigest()})
            stream.addfile(*exporter.member(exporter.RECEIPT, json.dumps(receipt).encode()))
        return archive

    def check_cli(self, archive):
        original = archive.read_bytes()
        result = subprocess.run([sys.executable, *(['-O'] if sys.flags.optimize else []),
                                 '-B', str(ROOT / 'scripts/export_research_package.py'),
                                 'check', str(archive)], capture_output=True, text=True,
                                env={**os.environ, 'PATH': ''}, timeout=30)
        self.assertEqual(archive.read_bytes(), original)
        return result

    def test_cli_rejects_absolute_and_relative_drive_members(self):
        destination = r'C:\fresh-export'
        contained_prefix = destination + ntpath.sep
        self.assertTrue(ntpath.join(destination, 'safe-input.txt').startswith(contained_prefix))
        for name in ('C:/outside.txt', 'D:outside.txt', 'z:', 'x:sub/file'):
            with self.subTest(name=name):
                # These are legal repository-relative POSIX names; the exporter
                # adds a stricter boundary without changing source pin policy.
                canonical_relative_path(name)
                self.assertTrue(ntpath.splitdrive(name)[0])
                self.assertFalse(ntpath.join(destination, name).startswith(contained_prefix))
                result = self.check_cli(self.bundle([name]))
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn('drive-qualified export path: ' + name, result.stderr)
                self.assertNotIn('PASS_RESEARCH_EXPORT', result.stdout)

    def test_cli_rejects_drive_paths_in_receipts(self):
        for name in ('C:/outside.txt', 'D:outside.txt'):
            with self.subTest(name=name):
                result = self.check_cli(self.bundle(['safe-input.txt'], receipt_name=name))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('drive-qualified export path: ' + name, result.stderr)

    def test_cli_preserves_colons_that_are_not_drive_prefixes(self):
        archive = self.bundle(['inputs/part:one.txt', 'archive:notes.txt'])
        result = self.check_cli(archive)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('PASS_RESEARCH_EXPORT', result.stdout)
        self.assertEqual(len(exporter.check_bundle(archive)['files']), 3)

    def git_fixture(self, names):
        repo = Path(tempfile.mkdtemp(prefix='repo-', dir=self.root))
        scripts = repo / 'scripts'
        scripts.mkdir()
        for name in ('export_research_package.py', 'research_package.py'):
            shutil.copyfile(ROOT / 'scripts' / name, scripts / name)
        def git(*args, data=None):
            return subprocess.check_output(['git', *args], cwd=repo, input=data,
                                           stderr=subprocess.PIPE, timeout=30)
        git('init', '-q')
        git('config', 'user.name', 'Fixture')
        git('config', 'user.email', 'fixture@example.invalid')

        # These are Git/POSIX names, not host paths. Build the real committed
        # inputs without asking Windows to create a colon-bearing filename.
        payloads = {name: self.input_payload for name in names}
        payloads[self.package + '/VERIFY.json'] = json.dumps({'inputs': names}).encode('utf-8')
        tree = {}
        for name, data in payloads.items():
            parts = name.split('/')
            parent = tree
            for part in parts[:-1]:
                parent = parent.setdefault(part, {})
            parent[parts[-1]] = data

        def write_tree(entries):
            records = []
            for name, value in sorted(entries.items()):
                if isinstance(value, dict):
                    mode, kind, obj = '040000', 'tree', write_tree(value)
                else:
                    mode, kind = '100644', 'blob'
                    obj = git('hash-object', '-w', '--stdin', data=value).decode().strip()
                records.append(f'{mode} {kind} {obj}\t{name}\0'.encode('utf-8'))
            return git('mktree', '-z', data=b''.join(records)).decode().strip()

        commit = git('commit-tree', write_tree(tree), '-m', 'Git-only path fixture').decode().strip()
        self.assertEqual(git('ls-tree', '-r', '-z', '--name-only', commit),
                         ''.join(name + '\0' for name in sorted(payloads)).encode('utf-8'))
        self.assertEqual({path.name for path in repo.iterdir()}, {'.git', 'scripts'})
        output = repo / 'export.tar'
        result = subprocess.run([sys.executable, *(['-O'] if sys.flags.optimize else []),
                                 '-B', str(scripts / 'export_research_package.py'),
                                 'export', '--package', self.package, '--ref', commit,
                                 '--output', str(output)],
                                cwd=repo, capture_output=True, text=True, timeout=30)
        return result, output

    def test_real_git_export_rejects_drive_paths_before_publishing(self):
        for name in ('C:/outside.txt', 'D:outside.txt'):
            with self.subTest(name=name):
                result, output = self.git_fixture([name])
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn('drive-qualified export path: ' + name, result.stderr)
                self.assertNotIn('PASS_RESEARCH_EXPORT', result.stdout)
                self.assertFalse(output.exists())
                self.assertFalse(list(output.parent.glob('.research-export-*')))

    def test_real_git_export_preserves_nondrive_colons_and_bytes(self):
        names = ['inputs/part:one.txt', 'archive:notes.txt']
        result, output = self.git_fixture(names)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('PASS_RESEARCH_EXPORT', result.stdout)
        receipt = exporter.check_bundle(output)
        self.assertEqual({row['path'] for row in receipt['files']},
                         {*names, self.package + '/VERIFY.json'})
        checked = self.check_cli(output)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertIn('PASS_RESEARCH_EXPORT', checked.stdout)
        with tarfile.open(output) as archive:
            for name in names:
                self.assertEqual(archive.extractfile(name).read(), self.input_payload)
            self.assertEqual(json.load(archive.extractfile(self.package + '/VERIFY.json')),
                             {'inputs': names})


if __name__ == '__main__':
    unittest.main()
