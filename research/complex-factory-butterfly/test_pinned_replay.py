#!/usr/bin/env python3
"""Small adverse controls for the historical export, without the full search.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('pinned_replay', HERE / 'pinned_replay.py')
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)


class PinnedReplayTests(unittest.TestCase):
    def test_original_manifest_is_authenticated(self):
        pins = replay.manifest(HERE / 'SOURCES.json')
        self.assertEqual(pins['base_commit'], replay.BASE)
        self.assertEqual(len(pins['files']), 29)

    def test_manifest_corruption_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'SOURCES.json'
            path.write_bytes((HERE / 'SOURCES.json').read_bytes() + b' ')
            with self.assertRaisesRegex(replay.ReplayError, 'digest differs'):
                replay.manifest(path)

    def test_path_escape_and_bytecode_paths_are_rejected(self):
        for name in ('.', '', '../escape', '/absolute', 'a/../escape', 'a//b', './a',
                     '.git/config', 'a/__pycache__/x.pyc', 'a.pyc', 'a\\b', 'a\0b'):
            with self.subTest(name=name), self.assertRaises(replay.ReplayError):
                replay.safe_relative(name)
        self.assertEqual(str(replay.safe_relative('research/source.py')), 'research/source.py')

    def fixture(self, path):
        root = path / 'checkout'
        root.mkdir()
        for args in (('init', '-q'), ('config', 'user.name', 'Fixture'),
                     ('config', 'user.email', 'fixture@example.invalid')):
            subprocess.run(['git', '-C', str(root), *args], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        content = b'exact historical source\n'
        (root / 'source.py').write_bytes(content)
        subprocess.run(['git', '-C', str(root), 'add', 'source.py'], check=True)
        subprocess.run(['git', '-C', str(root), 'commit', '-qm', 'fixture'], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        base = replay.git(root, 'rev-parse', 'HEAD').decode().strip()
        return root, {'base_commit': base, 'files': {'source.py': hashlib.sha256(content).hexdigest()}}

    def test_exact_git_blob_export_and_corrupt_hash_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            root, pins = self.fixture(path)
            exported = path / 'export'
            replay.export_sources(root, exported, pins)
            self.assertEqual((exported / 'source.py').read_bytes(), b'exact historical source\n')
            pins['files']['source.py'] = '0' * 64
            with self.assertRaisesRegex(replay.ReplayError, 'source digest differs'):
                replay.export_sources(root, path / 'bad export', pins)
            self.assertFalse((path / 'bad export/source.py').exists())

    def test_missing_history_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            root, pins = self.fixture(path)
            pins['base_commit'] = '0' * 40
            with self.assertRaisesRegex(replay.ReplayError, 'history unavailable'):
                replay.export_sources(root, path / 'export', pins)

    def test_package_symlinks_rejected_and_bytecode_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            source = path / 'package'
            source.mkdir()
            (source / 'verify.py').write_text('pass\n')
            (source / 'old.pyc').write_bytes(b'cache')
            (source / '__pycache__').mkdir()
            (source / '__pycache__/old.pyc').write_bytes(b'cache')
            replay.copy_package(source, path / 'copy')
            self.assertEqual([p.name for p in (path / 'copy').iterdir()], ['verify.py'])
            (source / 'linked.py').symlink_to(source / 'verify.py')
            with self.assertRaisesRegex(replay.ReplayError, 'symlink'):
                replay.copy_package(source, path / 'bad copy')

    def test_optimized_caller_does_not_disable_exported_assertions(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / 'probe.py'
            script.write_text("import os\nassert __debug__\nassert all(name not in os.environ for name in ('PYTHONOPTIMIZE', 'PYTHONPATH', 'PYTHONHOME'))\nprint('ASSERTIONS_ACTIVE')\n")
            with patch.dict(os.environ, {'PYTHONOPTIMIZE': '2', 'PYTHONPATH': '/untrusted-import-path', 'PYTHONHOME': '/untrusted-python-home'}):
                result = subprocess.run(replay.verifier_command(script),
                    env=replay.verifier_environment(), capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), 'ASSERTIONS_ACTIVE')

    def test_checkout_change_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _ = self.fixture(Path(tmp))
            before = replay.checkout_state(root)
            replay.unchanged(root, before)
            (root / 'source.py').write_text('changed\n')
            with self.assertRaisesRegex(replay.ReplayError, 'checkout changed'):
                replay.unchanged(root, before)


if __name__ == '__main__':
    unittest.main()
