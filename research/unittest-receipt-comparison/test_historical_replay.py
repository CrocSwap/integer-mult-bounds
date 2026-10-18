#!/usr/bin/env python3
"""Fail-closed controls for the PR1926 historical migration, not suite timing.
Douglas Colkitt with OpenAI Codex assistance; Apache-2.0.
"""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('historical1926', HERE / 'historical_replay.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class HistoricalReplay(unittest.TestCase):
    def fixture(self, root):
        paths = [m.PACKAGE + '/' + ('historical/' if n in m.ARCHIVED_METADATA else '') + n
                 for n in m.ORIGINAL_FILES]
        paths += [row['physical'] for row in m.INPUTS.values()]
        for relative in paths:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(m.ROOT / relative, target)
        return paths

    def test_exact_context_and_every_changed_source_rejects_before_copy(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / 'source'
            paths = self.fixture(root)
            target = Path(td) / 'positive'
            expected = m.prepare(root, target)
            self.assertEqual(m.inventory(target), expected)
            self.assertEqual(len(expected), len(m.ORIGINAL_FILES) + len(m.INPUTS))
            for relative in paths:
                f = root / relative
                original = f.read_bytes()
                f.write_bytes(original + b'\ncorruption\n')
                destination = Path(td) / 'rejected'
                with self.subTest(path=relative), self.assertRaises(ValueError):
                    m.prepare(root, destination)
                self.assertFalse(destination.exists())
                f.write_bytes(original)
            archive = root / m.INPUTS['scripts/run_isolated_tests.py']['physical']
            archive.unlink()
            with self.assertRaises(FileNotFoundError):
                m.prepare(root, Path(td) / 'missing')

    def test_existing_destination_rejects(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(ValueError, 'already exists'):
                m.prepare(m.ROOT, root)

    def test_failed_or_silent_successful_child_rejects(self):
        for code, out, error in [(1, m.MARKER + '\n', 'failed'),
                                 (0, '', 'did not report'),
                                 (0, m.MARKER + '\npartial\n', 'did not report')]:
            result = subprocess.CompletedProcess([], code, out, '')
            with self.subTest(code=code, out=out), patch.object(m.subprocess, 'run', return_value=result):
                with self.assertRaisesRegex(ValueError, error):
                    m.replay()

    def test_post_replay_mutation_rejects(self):
        def child(command, **kw):
            source = Path(kw['cwd']) / m.PACKAGE / 'RESULT.json'
            source.write_bytes(source.read_bytes() + b' ')
            return subprocess.CompletedProcess(command, 0, m.MARKER + '\n', '')
        with patch.object(m.subprocess, 'run', side_effect=child):
            with self.assertRaisesRegex(ValueError, 'inputs changed'):
                m.replay(optimized=True)


if __name__ == '__main__':
    unittest.main()
