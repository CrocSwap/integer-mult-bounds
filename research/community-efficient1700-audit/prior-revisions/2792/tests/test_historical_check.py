"""Historical overlays authenticate exact bytes and leave live inputs untouched."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('historical_check', ROOT/'scripts/replay_historical_check.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class HistoricalReplay(unittest.TestCase):
    def fixture(self, temporary):
        root = Path(temporary)/'source'
        root.mkdir()
        inputs = Path(temporary)/'inputs'
        inputs.mkdir()
        original = b'historical input\n'
        (inputs/'old.txt').write_bytes(original)
        (root/'input.txt').write_bytes(b'new live input\n')
        (root/'unrelated.py').write_bytes(b'unchanged checker bytes\n')
        digest = hashlib.sha256(original).hexdigest()
        (root/'manifest.json').write_text(json.dumps({'files': {'input.txt': digest}}))
        config = dict(manifest='manifest.json', field='files', path='input.txt', input='old.txt', sha256=digest)
        return root, inputs, config, ['input.txt', 'manifest.json', 'unrelated.py']

    def test_overlay_is_isolated_and_other_inputs_stay_exact(self):
        with tempfile.TemporaryDirectory() as td:
            root, inputs, config, paths = self.fixture(td)
            before = {p: (root/p).read_bytes() for p in paths}
            target = Path(td)/'copy'
            expected = checker.materialize(root, target, config, paths, inputs)
            self.assertEqual((target/'input.txt').read_bytes(), (inputs/'old.txt').read_bytes())
            self.assertEqual((target/'unrelated.py').read_bytes(), before['unrelated.py'])
            checker.verify_unchanged(target, expected)
            (target/'unrelated.py').write_bytes(b'regenerated in temporary tree')
            with self.assertRaisesRegex(ValueError, 'Replay changed tracked artifact'):
                checker.verify_unchanged(target, expected)
            self.assertEqual({p: (root/p).read_bytes() for p in paths}, before)

    def test_corrupt_historical_blob_rejects_before_copy(self):
        with tempfile.TemporaryDirectory() as td:
            root, inputs, config, paths = self.fixture(td)
            (inputs/'old.txt').write_bytes(b'corrupted')
            target = Path(td)/'copy'
            with self.assertRaisesRegex(ValueError, 'Changed historical input'):
                checker.materialize(root, target, config, paths, inputs)
            self.assertFalse(target.exists())

    def test_missing_changed_and_nonbyte_pins_reject(self):
        with tempfile.TemporaryDirectory() as td:
            root, inputs, config, paths = self.fixture(td)
            for entry in [None, '0'*64, {'representation': 'gzip-payload', 'sha256': config['sha256']}]:
                (root/'manifest.json').write_text(json.dumps({'files': {'input.txt': entry}}))
                with self.subTest(entry=entry), self.assertRaises(ValueError):
                    checker.authenticated_input(root, config, inputs)

    def test_untracked_replacement_and_existing_destination_reject(self):
        with tempfile.TemporaryDirectory() as td:
            root, inputs, config, paths = self.fixture(td)
            target = Path(td)/'copy'
            with self.assertRaisesRegex(ValueError, 'not tracked'):
                checker.materialize(root, target, config, ['manifest.json'], inputs)
            target.mkdir()
            with self.assertRaisesRegex(ValueError, 'already exists'):
                checker.materialize(root, target, config, paths, inputs)

    def test_path_escape_and_symlinks_reject(self):
        with tempfile.TemporaryDirectory() as td:
            root, inputs, config, paths = self.fixture(td)
            for name in ['/absolute', '../escape', 'C:/escape', 'folder\\escape']:
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'Unsafe'):
                    checker.safe_path(root, name)
            with patch.object(Path, 'is_symlink', return_value=True):
                with self.assertRaisesRegex(ValueError, 'Non-file tracked'):
                    checker.materialize(root, Path(td)/'copy', config, paths, inputs)

    def test_makefile_append_is_allowed_but_original_prefix_mutation_rejects(self):
        with tempfile.TemporaryDirectory() as td:
            root, inputs, config, paths = self.fixture(td)
            config['preserve_prefix'] = True
            original = (inputs/'old.txt').read_bytes()
            (root/'input.txt').write_bytes(original + b'new target\n')
            self.assertEqual(checker.authenticated_input(root, config, inputs), original)
            (root/'input.txt').write_bytes(original.replace(b'historical', b'changed') + b'new target\n')
            with self.assertRaisesRegex(ValueError, 'prefix changed'):
                checker.authenticated_input(root, config, inputs)

    def test_skip_clone_frozen_source_replay_binding(self):
        config = checker.CONFIG['skip-clones']
        predecessor = (ROOT / config['input']).read_bytes()
        pins = json.loads((ROOT / config['manifest']).read_bytes())
        self.assertEqual(hashlib.sha256(predecessor).hexdigest(), config['sha256'])
        self.assertEqual(pins['files'][config['path']], config['sha256'])
        self.assertEqual(checker.authenticated_input(ROOT, config), predecessor)
        suite = checker.CONFIG['skip-clones-tests']
        self.assertEqual(suite['sha256'], config['sha256'])
        self.assertEqual(suite['commands'], config['commands'][-1:])

    def test_skip_clone_overlay_rejects_unknown_live_and_corrupt_baseline(self):
        with tempfile.TemporaryDirectory() as td:
            root, inputs, config, paths = self.fixture(td)
            original = (inputs / 'old.txt').read_bytes()
            (root / 'baseline.txt').write_bytes(original)
            current = hashlib.sha256((root / 'input.txt').read_bytes()).hexdigest()
            config.update(input='baseline.txt', input_from_root=True,
                          accepted_live_sha256=[current])
            self.assertEqual(checker.authenticated_input(root, config, inputs), original)
            (root / 'input.txt').write_bytes(b'unreviewed source edit\\n')
            with self.assertRaisesRegex(ValueError, 'Unrecognized live source update'):
                checker.authenticated_input(root, config, inputs)
            (root / 'input.txt').write_bytes(original)
            self.assertEqual(checker.authenticated_input(root, config, inputs), original)
            (root / 'baseline.txt').write_bytes(b'changed frozen evidence\\n')
            with self.assertRaisesRegex(ValueError, 'Changed historical input'):
                checker.authenticated_input(root, config, inputs)

    def multi_fixture(self, temporary):
        root, inputs, config, paths = self.fixture(temporary)
        original = b'second historical dependency\n'
        (inputs / 'second.txt').write_bytes(original)
        (root / 'second.py').write_bytes(b'current optimized dependency\n')
        digest = hashlib.sha256(original).hexdigest()
        pins = json.loads((root / 'manifest.json').read_bytes())
        pins['files']['second.py'] = digest
        (root / 'manifest.json').write_text(json.dumps(pins))
        config['additional_inputs'] = [dict(
            manifest='manifest.json', field='files', path='second.py',
            input='second.txt', sha256=digest)]
        return root, inputs, config, paths + ['second.py']

    def test_multiple_overlays_preserve_live_bytes_and_each_output_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root, inputs, config, paths = self.multi_fixture(td)
            before = {name: (root / name).read_bytes() for name in paths}
            target = Path(td) / 'copy'
            expected = checker.materialize(root, target, config, paths, inputs)
            self.assertEqual((target / 'input.txt').read_bytes(), (inputs / 'old.txt').read_bytes())
            self.assertEqual((target / 'second.py').read_bytes(), (inputs / 'second.txt').read_bytes())
            checker.verify_unchanged(target, expected)
            for name in ('input.txt', 'second.py', 'unrelated.py'):
                original = (target / name).read_bytes()
                (target / name).write_bytes(original + b'corruption')
                with self.subTest(path=name), self.assertRaisesRegex(ValueError, 'Replay changed'):
                    checker.verify_unchanged(target, expected)
                (target / name).write_bytes(original)
            self.assertEqual({name: (root / name).read_bytes() for name in paths}, before)

    def test_corrupt_additional_input_rejects_before_copy(self):
        with tempfile.TemporaryDirectory() as td:
            root, inputs, config, paths = self.multi_fixture(td)
            (inputs / 'second.txt').write_bytes(b'corrupt baseline')
            target = Path(td) / 'copy'
            with self.assertRaisesRegex(ValueError, 'Changed historical input'):
                checker.materialize(root, target, config, paths, inputs)
            self.assertFalse(target.exists())

    def test_duplicate_and_untracked_dependencies_reject_before_copy(self):
        with tempfile.TemporaryDirectory() as td:
            root, inputs, config, paths = self.multi_fixture(td)
            target = Path(td) / 'copy'
            with self.assertRaisesRegex(ValueError, 'not tracked'):
                checker.materialize(root, target, config, paths[:-1], inputs)
            config['additional_inputs'].append(dict(config['additional_inputs'][0]))
            with self.assertRaisesRegex(ValueError, 'Duplicate'):
                checker.materialize(root, target, config, paths, inputs)
            self.assertFalse(target.exists())

    def test_all_split_skip_dependencies_match_frozen_manifest(self):
        config = checker.CONFIG['split-skip']
        entries = [config, *config['additional_inputs']]
        self.assertEqual({entry['path'] for entry in entries}, {
            'scripts/audit_fused_block.py', 'scripts/exclusion_circuit.py',
            'scripts/shared_point_circuit.py'})
        for entry in entries:
            with self.subTest(path=entry['path']):
                checker.authenticated_input(ROOT, entry)

    def test_real_snapshots_match_unchanged_predecessor_pins(self):
        for name, config in checker.CONFIG.items():
            with self.subTest(package=name):
                checker.authenticated_input(ROOT, config)


class HistoricalReplayEnvironment(unittest.TestCase):
    """Exercise the real CLI without copying or replaying the full repository."""

    def sandbox(self, root, body, test_body=None):
        config = checker.CONFIG['r420']
        (root / 'scripts/historical-ci-inputs').mkdir(parents=True)
        shutil.copyfile(ROOT / 'scripts/replay_historical_check.py',
                        root / 'scripts/replay_historical_check.py')
        shutil.copyfile(checker.INPUTS / config['input'],
                        root / 'scripts/historical-ci-inputs' / config['input'])
        source = root / config['path']
        source.parent.mkdir(parents=True)
        source.write_bytes(b'live selected record\n')
        manifest = root / config['manifest']
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({'files': {config['path']: config['sha256']}}),
                            encoding='utf-8')
        (manifest.parent / 'verify.py').write_text(body, encoding='utf-8')
        (manifest.parent / 'test_fixture.py').write_text(
            test_body or 'import unittest\nclass Fixture(unittest.TestCase):\n'
            '    def test_replay(self):\n        self.assertEqual(2 + 2, 4)\n',
            encoding='utf-8')
        for args in [('init', '-q'), ('add', '.'),
                     ('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                      '-c', 'gc.auto=0', 'commit', '-qm', 'historical replay fixture')]:
            subprocess.run(['git', *args], cwd=root, check=True, capture_output=True)

    def run_cli(self, root, level):
        env = dict(os.environ, PYTHONOPTIMIZE=level,
                   HISTORICAL_REPLAY_SENTINEL='preserved')
        return subprocess.run(
            [sys.executable, '-B', str(root / 'scripts/replay_historical_check.py'), 'r420'],
            cwd=root, env=env, capture_output=True, text=True, timeout=30)

    def test_inherited_optimization_cannot_hide_direct_or_nested_assertions(self):
        bodies = {
            'direct': "assert False, 'direct historical assertion'\n",
            'nested': ("import subprocess, sys\n"
                       "subprocess.run([sys.executable, '-B', '-c', "
                       "\"assert False, 'nested historical assertion'\"], check=True)\n"),
        }
        for kind, body in bodies.items():
            with tempfile.TemporaryDirectory() as td:
                root = Path(td)
                self.sandbox(root, body)
                for level in ('1', '2'):
                    with self.subTest(kind=kind, level=level):
                        result = self.run_cli(root, level)
                        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                        self.assertIn(kind + ' historical assertion', result.stderr)
                        self.assertNotIn('PASS_HISTORICAL_CHECK', result.stdout)

    def test_unittest_command_also_rejects_assertions(self):
        body = ('import unittest\nclass Fixture(unittest.TestCase):\n'
                "    def test_replay(self):\n        assert False, 'unittest historical assertion'\n")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.sandbox(root, "print('PASS_FIRST_HISTORICAL_COMMAND')\n", body)
            for level in ('1', '2'):
                with self.subTest(level=level):
                    result = self.run_cli(root, level)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('PASS_FIRST_HISTORICAL_COMMAND', result.stdout)
                    self.assertIn('unittest historical assertion', result.stderr)
                    self.assertNotIn('PASS_HISTORICAL_CHECK', result.stdout)

    def test_passing_replay_preserves_environment_overlay_and_live_bytes(self):
        body = '''import hashlib, os, pathlib, sys
if sys.flags.optimize != 0 or os.environ.get('PYTHONOPTIMIZE') is not None:
    raise RuntimeError('child optimization still enabled')
if os.environ.get('HISTORICAL_REPLAY_SENTINEL') != 'preserved':
    raise RuntimeError('unrelated environment lost')
root = pathlib.Path(__file__).resolve().parents[2]
if hashlib.sha256((root / 'certificates/selected-result.json').read_bytes()).hexdigest() != %r:
    raise RuntimeError('historical overlay lost')
print('PASS_ASSERTION_ENABLED_HISTORICAL_CHILD')
''' % checker.CONFIG['r420']['sha256']
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.sandbox(root, body)
            before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
            for level in ('1', '2'):
                with self.subTest(level=level):
                    result = self.run_cli(root, level)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIn('PASS_ASSERTION_ENABLED_HISTORICAL_CHILD', result.stdout)
                    self.assertIn('PASS_HISTORICAL_CHECK r420', result.stdout)
                    self.assertEqual({p: p.read_bytes() for p in before}, before)

    def test_optimized_parent_retains_tracked_artifact_mutation_gate(self):
        body = "from pathlib import Path\nPath(__file__).write_text('changed tracked checker\\n')\n"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.sandbox(root, body)
            for level in ('1', '2'):
                with self.subTest(level=level):
                    result = self.run_cli(root, level)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('Replay changed tracked artifact', result.stderr)
                    self.assertNotIn('PASS_HISTORICAL_CHECK', result.stdout)


if __name__ == '__main__':
    unittest.main()
