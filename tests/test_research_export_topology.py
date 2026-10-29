"""Exported regular files must form an extractable tree, including the receipt.

Builds on Tekalign's committed exporter and integrity tests. Prepared for
roger-sato with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = 'research/fixture'
RECEIPT = '.research-export.json'


class ExportFileTreeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name in ('export_research_package.py', 'research_package.py', 'research_windows_git.py'):
            path = self.root / 'scripts' / name
            path.parent.mkdir(exist_ok=True)
            shutil.copyfile(ROOT / 'scripts' / name, path)
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'core.autocrlf', 'false')

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root,
                                       stderr=subprocess.PIPE, timeout=30)

    def cli(self, *args):
        flags = ['-O'] if sys.flags.optimize else []
        return subprocess.run([sys.executable, *flags, '-B',
                               str(self.root / 'scripts/export_research_package.py'), *args],
                              cwd=self.root, capture_output=True, text=True, timeout=30)

    def commit_inputs(self, inputs):
        payloads = {name: ('payload: ' + name).encode('utf-8') for name in inputs}
        payloads[PACKAGE + '/VERIFY.json'] = json.dumps({'inputs': inputs}).encode('utf-8')
        for name, data in payloads.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture')
        return payloads

    def bundle(self, inputs, reverse=False, receipt_first=False):
        # A fully self-consistent receipt isolates the file-tree requirement.
        payloads = dict(inputs)
        payloads[PACKAGE + '/VERIFY.json'] = json.dumps({'inputs': list(inputs)}).encode('utf-8')
        receipt = {'format': 'research-package-export-v1', 'commit': 'a' * 40,
                   'package': PACKAGE, 'files': [
                       {'path': name, 'mode': 0o644, 'size': len(data),
                        'sha256': hashlib.sha256(data).hexdigest()}
                       for name, data in payloads.items()]}
        rows = list(payloads.items())
        if reverse:
            rows.reverse()
        receipt_row = (RECEIPT, json.dumps(receipt).encode('utf-8'))
        rows.insert(0 if receipt_first else len(rows), receipt_row)
        archive = self.root / 'bundle.tar'
        with tarfile.open(archive, 'w', format=tarfile.PAX_FORMAT) as out:
            for name, data in rows:
                info = tarfile.TarInfo(name)
                info.mode = 0o644
                info.size = len(data)
                out.addfile(info, io.BytesIO(data))
        return archive, payloads

    def assert_rejected_unextractable_bundle(self, archive):
        result = self.cli('check', str(archive))
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn('file/directory collision', result.stderr)
        self.assertNotIn('PASS_RESEARCH_EXPORT', result.stdout)
        # All fixture names are relative and contained; extraction only probes
        # the conflicting file/directory roles in a disposable directory.
        with tempfile.TemporaryDirectory() as target, tarfile.open(archive, 'r:') as bundle:
            with self.assertRaises(OSError):
                bundle.extractall(target, filter='data')

    def test_export_rejects_receipt_descendants_before_publication(self):
        for suffix in ('input.dat', 'nested/input.dat'):
            with self.subTest(suffix=suffix):
                self.commit_inputs([RECEIPT + '/' + suffix])
                archive = self.root / ('export-' + suffix.replace('/', '-') + '.tar')
                result = self.cli('export', '--package', PACKAGE, '--output', str(archive))
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn('file/directory collision', result.stderr)
                self.assertFalse(archive.exists())
                self.assertEqual(list(self.root.glob('.research-export-*')), [])

    def test_checker_rejects_file_ancestors_in_both_member_orders(self):
        for child in ('inputs/a/child', 'inputs/a/nested/child'):
            for reverse in (False, True):
                with self.subTest(child=child, reverse=reverse):
                    archive, _ = self.bundle({'inputs/a': b'parent',
                                              'inputs/a.b': b'lexical neighbor',
                                              child: b'child'}, reverse=reverse)
                    self.assert_rejected_unextractable_bundle(archive)

    def test_checker_rejects_receipt_ancestors_in_both_member_orders(self):
        for receipt_first in (False, True):
            with self.subTest(receipt_first=receipt_first):
                archive, _ = self.bundle({RECEIPT + '/child': b'child'},
                                         receipt_first=receipt_first)
                self.assert_rejected_unextractable_bundle(archive)

    def test_valid_git_export_with_siblings_and_lexical_prefixes_extracts(self):
        inputs = ['inputs/a', 'inputs/a.b', 'inputs/ab/c', 'inputs/nested/x',
                  'inputs/nested/y', RECEIPT + '-extra/input', RECEIPT + '.notes/input']
        payloads = self.commit_inputs(inputs)
        archive = self.root / 'export.tar'
        made = self.cli('export', '--package', PACKAGE, '--output', str(archive))
        self.assertEqual(made.returncode, 0, made.stderr)
        checked = self.cli('check', str(archive))
        self.assertEqual(checked.returncode, 0, checked.stderr)
        with tempfile.TemporaryDirectory() as target, tarfile.open(archive, 'r:') as bundle:
            bundle.extractall(target, filter='data')
            for name, data in payloads.items():
                self.assertEqual((Path(target) / name).read_bytes(), data)
            self.assertTrue((Path(target) / RECEIPT).is_file())

    def test_valid_bundle_does_not_require_sorted_members_or_last_receipt(self):
        for reverse in (False, True):
            for receipt_first in (False, True):
                with self.subTest(reverse=reverse, receipt_first=receipt_first):
                    archive, payloads = self.bundle({'inputs/a': b'a', 'inputs/a.b': b'b',
                                                     'inputs/ab/c': b'c', 'inputs/ab/d': b'd'},
                                                    reverse=reverse, receipt_first=receipt_first)
                    result = self.cli('check', str(archive))
                    self.assertEqual(result.returncode, 0, result.stderr)
                    with tempfile.TemporaryDirectory() as target, tarfile.open(archive, 'r:') as bundle:
                        bundle.extractall(target, filter='data')
                        for name, data in payloads.items():
                            self.assertEqual((Path(target) / name).read_bytes(), data)


if __name__ == '__main__':
    unittest.main()
