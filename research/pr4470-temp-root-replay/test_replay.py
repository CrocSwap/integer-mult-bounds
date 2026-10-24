"""Alias and rejection controls; no historical package is modified."""
import contextlib
import io
from pathlib import Path
import runpy
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

REPLAY = runpy.run_path(str(Path(__file__).with_name('verify.py')))
LOAD = REPLAY['load_audit']
RUN = REPLAY['replay']
ROOT = REPLAY['ROOT']
REAL_TEMPORARY_DIRECTORY = tempfile.TemporaryDirectory


class ReplayTests(unittest.TestCase):
    def setUp(self):
        self.audit = LOAD()
        self.row = {'path': 'RESULT.json', 'upstream_path': 'probe/result.json'}
        self.process = types.SimpleNamespace(returncode=0, stdout='{}', stderr='')

    def probe(self):
        return self.audit.emit_source([self.row])

    def test_explicit_alias_and_canonical_positive(self):
        with REAL_TEMPORARY_DIRECTORY() as td:
            root = Path(td).resolve()
            real = root / 'real'
            real.mkdir()
            alias = root / 'alias'
            alias.symlink_to(real, target_is_directory=True)
            with patch.object(tempfile, 'tempdir', str(alias)), patch.object(self.audit.subprocess, 'run', return_value=self.process):
                with self.assertRaisesRegex(ValueError, 'invalid upstream snapshot path'):
                    self.probe()
                with patch.dict(RUN.__globals__, load_audit=lambda: self.audit), patch.object(self.audit, 'main', self.probe), patch.object(sys, 'argv', ['verify.py']), contextlib.redirect_stdout(io.StringIO()):
                    RUN()
                self.assertEqual(tempfile.tempdir, str(alias))
            with patch.object(tempfile, 'tempdir', str(real)), patch.object(self.audit.subprocess, 'run', return_value=self.process):
                self.assertEqual(self.probe(), {})

    def test_escape_controls_remain_before_copy(self):
        with REAL_TEMPORARY_DIRECTORY() as td:
            root = Path(td).resolve()
            work = root / 'work'
            work.mkdir()
            outside = root / 'outside'
            outside.mkdir()
            (work / 'escape').symlink_to(outside, target_is_directory=True)
            for destination in ('../outside/payload', str(outside / 'payload'), 'escape/payload'):
                with self.subTest(destination=destination), patch.object(self.audit.tempfile, 'TemporaryDirectory', return_value=contextlib.nullcontext(str(work))), patch.object(self.audit.shutil, 'copyfile') as copy, patch.object(self.audit.subprocess, 'run') as process:
                    row = dict(self.row, upstream_path=destination)
                    with self.assertRaisesRegex(ValueError, 'invalid upstream snapshot path'):
                        self.audit.emit_source([row])
                    copy.assert_not_called()
                    process.assert_not_called()
            self.assertEqual(list(outside.iterdir()), [])

    def test_source_drift_rejected_before_compile(self):
        original = Path.read_bytes
        for relative in ('verify.py', 'emit_source.py', 'UPSTREAM.json', 'RESULT.json', 'source/research/joint-helper-lattice/native_joint.py'):
            target = ROOT / 'research/pr4470-frame-audit' / relative
            def changed(path):
                raw = original(path)
                return raw + b'\n' if path == target else raw
            with self.subTest(source=relative), patch.object(Path, 'read_bytes', changed), patch('builtins.compile') as compiler:
                with self.assertRaisesRegex(ValueError, 'source SHA256 mismatch'):
                    LOAD()
                compiler.assert_not_called()

    def test_temporary_setting_restored_after_failure(self):
        def fail():
            raise ValueError('controlled replay failure')
        with patch.dict(RUN.__globals__, load_audit=lambda: self.audit), patch.object(self.audit, 'main', fail), patch.object(sys, 'argv', ['verify.py']), patch.object(tempfile, 'tempdir', None):
            with self.assertRaisesRegex(ValueError, 'controlled replay failure'):
                RUN()
            self.assertIsNone(tempfile.tempdir)

    def test_authoring_arguments_rejected_before_loading(self):
        for arguments in (['--write'], ['--unknown']):
            with self.subTest(arguments=arguments), patch.object(sys, 'argv', ['verify.py', *arguments]), patch.dict(RUN.__globals__, load_audit=lambda: self.fail('audit loaded')):
                with self.assertRaisesRegex(ValueError, 'verification only'):
                    RUN()


if __name__ == '__main__':
    unittest.main()
