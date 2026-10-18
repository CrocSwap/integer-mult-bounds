"""Actual Git object/working-tree controls for the publication byte preflight."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import check_research_commit as checker
sys.path.pop(0)


class CommitBytesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.package = 'research/fixture'
        self.path = self.root/self.package
        self.path.mkdir(parents=True)
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'core.autocrlf', 'false')
        self.write('.gitattributes', b'*.lean text eol=lf\n')
        self.write('research/fixture/VERIFY.json', b'{"inputs":["input.bin"]}\n')
        self.write('research/fixture/Proof.lean', b'import Std\nexample : True := by trivial\n')
        self.write('input.bin', b'\x00\r\n\xff')
        self.commit()

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, stderr=subprocess.PIPE)

    def write(self, name, data):
        path = self.root/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def commit(self):
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture')
        return self.git('rev-parse', 'HEAD').decode().strip()

    def check(self, ref='HEAD'):
        return checker.check(self.root, self.package, ref)

    def test_exact_bytes_and_binary_input_pass(self):
        self.assertEqual(self.check()['files'], 3)

    def test_actual_git_normalization_is_detected_then_fixed(self):
        path = self.path/'Proof.lean'
        path.write_bytes(path.read_bytes().replace(b'\n', b'\r\n'))
        self.git('add', '.')
        # Git reports no change although a raw source-hash receipt would
        # describe bytes different from those in a normal LF checkout.
        self.assertEqual(self.git('diff', '--cached', '--name-only'), b'')
        with self.assertRaisesRegex(ValueError, 'bytes differ.*Proof.lean'):
            self.check()
        path.write_bytes(path.read_bytes().replace(b'\r\n', b'\n'))
        self.check()

    def test_untracked_and_staged_new_files_are_not_in_commit(self):
        self.write(self.package+'/helper.py', b'pass\n')
        for staged in (False, True):
            if staged:
                self.git('add', '.')
            with self.assertRaisesRegex(ValueError, 'inventory differs.*helper.py'):
                self.check()
        self.commit()
        self.assertEqual(self.check()['files'], 4)

    def test_input_drift_and_missing_working_file(self):
        self.write('input.bin', b'changed')
        with self.assertRaisesRegex(ValueError, 'bytes differ.*input.bin'):
            self.check()
        (self.root/'input.bin').unlink()
        with self.assertRaisesRegex(ValueError, 'missing or external file'):
            self.check()

    def test_older_ref_and_deleted_package_file(self):
        old = self.git('rev-parse', 'HEAD').decode().strip()
        self.write(self.package+'/Proof.lean', b'import Std\n')
        self.commit()
        self.check()
        with self.assertRaisesRegex(ValueError, 'bytes differ.*Proof.lean'):
            self.check(old)
        (self.path/'Proof.lean').unlink()
        with self.assertRaisesRegex(ValueError, 'missing or external file'):
            self.check()

    def test_ignored_runtime_artifacts_are_outside_scope(self):
        self.write('.gitignore', b'__pycache__/\n')
        self.commit()
        self.write(self.package+'/__pycache__/check.pyc', b'temporary')
        self.assertEqual(self.check()['files'], 3)

    def test_commit_symlink_is_rejected_without_following_it(self):
        # Set Git mode directly: no Windows symlink privilege is required.
        self.write(self.package+'/link', b'Proof.lean')
        obj = self.git('hash-object', '-w', self.package+'/link').decode().strip()
        self.git('update-index', '--add', '--cacheinfo', '120000', obj, self.package+'/link')
        self.git('commit', '-qm', 'symbolic link')
        with self.assertRaisesRegex(ValueError, 'non-regular file'):
            self.check()

    def test_invalid_package_and_missing_input_commit_reject(self):
        with self.assertRaisesRegex(ValueError, 'package must'):
            checker.check(self.root, '../outside')
        self.write('new.bin', b'data')
        self.write(self.package+'/VERIFY.json', b'{"inputs":["new.bin"]}\n')
        with self.assertRaisesRegex(ValueError, 'inventory differs'):
            self.check()

    def test_unicode_and_wildcard_characters_are_literal_input_paths(self):
        name = 'data/δ [α].bin'
        self.write(name, b'exact')
        self.write('data/δ α.bin', b'decoy')
        self.write(self.package+'/VERIFY.json',
                   json.dumps({'inputs':[name]}).encode('utf-8'))
        self.commit()
        self.assertEqual(self.check()['files'], 3)

    def test_cli_pass_fail_and_read_only_behavior(self):
        for name in ('check_research_commit.py', 'research_package.py'):
            self.write('scripts/'+name, (ROOT/'scripts'/name).read_bytes())
        self.commit()
        script = self.root/'scripts/check_research_commit.py'
        before = self.git('rev-parse', 'HEAD'), self.git('ls-files', '--stage', '-z')
        command = [sys.executable, '-B', str(script), '--package', self.package]
        good = subprocess.run(command, cwd=self.root, capture_output=True, timeout=30)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertIn(b'PASS_RESEARCH_COMMIT_BYTES', good.stdout)
        self.write('input.bin', b'drift')
        bad = subprocess.run(command, cwd=self.root, capture_output=True, timeout=30)
        self.assertEqual(bad.returncode, 1)
        self.assertIn(b'working/commit bytes differ: input.bin', bad.stderr)
        self.assertEqual(before, (self.git('rev-parse', 'HEAD'), self.git('ls-files', '--stage', '-z')))
        self.assertEqual((self.root/'input.bin').read_bytes(), b'drift')

    def test_blob_reader_final_failure_is_not_skipped(self):
        original = checker.git_blobs

        def failed_after_payloads(root, specs):
            yield from original(root, specs)
            raise ValueError('reader final exit failure')

        with patch.object(checker, 'git_blobs', side_effect=failed_after_payloads):
            with self.assertRaisesRegex(ValueError, 'reader final exit failure'):
                self.check()


if __name__ == '__main__':
    unittest.main()
