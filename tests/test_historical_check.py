"""Historical overlays authenticate exact bytes and leave live inputs untouched."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
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
            'scripts/partial_swap/shared.py', 'scripts/shared_point_circuit.py',
            'scripts/audit_sparse_fusion.py'})
        for entry in entries:
            with self.subTest(path=entry['path']):
                checker.authenticated_input(ROOT, entry)

    def test_clone_overlays_cover_every_changed_frozen_input(self):
        for package in ('skip-clones', 'skip-clones-tests', 'split-skip'):
            config = checker.CONFIG[package]
            replacements = {
                entry['path']: checker.authenticated_input(ROOT, entry)
                for entry in checker.input_configs(config)
            }
            pins = json.loads((ROOT / config['manifest']).read_bytes())['files']
            for path, digest in pins.items():
                with self.subTest(package=package, path=path):
                    data = replacements[path] if path in replacements else (ROOT / path).read_bytes()
                    self.assertEqual(hashlib.sha256(data).hexdigest(), digest)

    def test_split_skip_replay_preserves_native_make_recipe(self):
        makefile = (ROOT / 'Makefile').read_text()
        recipe = makefile.split('\nsplit-skip-producer:\n', 1)[1].splitlines()[0]
        command = shlex.split(recipe)
        self.assertEqual(command[0], 'python3')
        self.assertEqual(checker.CONFIG['split-skip']['commands'][0], command[1:])

    def test_root_baselines_must_be_tracked_before_copy(self):
        for additional in (False, True):
            with self.subTest(additional=additional), tempfile.TemporaryDirectory() as td:
                root, inputs, config, paths = self.multi_fixture(td)
                entry = config['additional_inputs'][0] if additional else config
                original = (inputs / entry['input']).read_bytes()
                (root / 'baseline.txt').write_bytes(original)
                entry.update(input='baseline.txt', input_from_root=True)
                target = Path(td) / 'copy'
                with self.assertRaisesRegex(ValueError, 'Historical baseline is not tracked'):
                    checker.materialize(root, target, config, paths, inputs)
                self.assertFalse(target.exists())
                expected = checker.materialize(root, target, config, paths + ['baseline.txt'], inputs)
                self.assertEqual((target / entry['path']).read_bytes(), original)
                checker.verify_unchanged(target, expected)

    def test_real_snapshots_match_unchanged_predecessor_pins(self):
        for name, config in checker.CONFIG.items():
            for item in checker.input_configs(config):
                with self.subTest(package=name, path=item['path']):
                    checker.authenticated_input(ROOT, item)

    def add_input(self, root, inputs, config, paths):
        data = b'second historical input\n'
        (inputs/'second.txt').write_bytes(data)
        (root/'second.py').write_bytes(b'current optimized implementation\n')
        digest = hashlib.sha256(data).hexdigest()
        manifest = json.loads((root/'manifest.json').read_text())
        manifest['files']['second.py'] = digest
        (root/'manifest.json').write_text(json.dumps(manifest))
        config['additional_inputs'] = [dict(path='second.py', input='second.txt', sha256=digest)]
        paths.append('second.py')

    def test_every_replacement_is_authenticated_and_drift_checked(self):
        with tempfile.TemporaryDirectory() as td:
            root, inputs, config, paths = self.fixture(td)
            self.add_input(root, inputs, config, paths)
            before = {p: (root/p).read_bytes() for p in paths}
            target = Path(td)/'copy'
            expected = checker.materialize(root, target, config, paths, inputs)
            for item in checker.input_configs(config):
                self.assertEqual((target/item['path']).read_bytes(), (inputs/item['input']).read_bytes())
            checker.verify_unchanged(target, expected)
            (target/'second.py').write_bytes(b'corrupted replacement')
            with self.assertRaisesRegex(ValueError, 'Replay changed tracked artifact: second.py'):
                checker.verify_unchanged(target, expected)
            self.assertEqual({p: (root/p).read_bytes() for p in paths}, before)

    def test_bad_additional_input_pin_or_tracking_rejects_before_copy(self):
        for corruption in ('blob', 'pin', 'untracked', 'duplicate'):
            with self.subTest(corruption=corruption), tempfile.TemporaryDirectory() as td:
                root, inputs, config, paths = self.fixture(td)
                self.add_input(root, inputs, config, paths)
                if corruption == 'blob':
                    (inputs/'second.txt').write_bytes(b'changed historical input')
                elif corruption == 'pin':
                    manifest = json.loads((root/'manifest.json').read_text())
                    del manifest['files']['second.py']
                    (root/'manifest.json').write_text(json.dumps(manifest))
                elif corruption == 'untracked':
                    paths.remove('second.py')
                else:
                    config['additional_inputs'].append(config['additional_inputs'][0])
                target = Path(td)/'copy'
                with self.assertRaises(ValueError):
                    checker.materialize(root, target, config, paths, inputs)
                self.assertFalse(target.exists())

    def test_context_checks_drift_and_removes_scratch_tree(self):
        with tempfile.TemporaryDirectory() as td:
            root, inputs, config, paths = self.fixture(td)
            materialize = checker.materialize
            def copy(*args):
                return materialize(*args, inputs=inputs)
            with patch.dict(checker.CONFIG, fixture=config), \
                 patch.object(checker, 'tracked_paths', return_value=paths), \
                 patch.object(checker, 'materialize', side_effect=copy):
                with self.assertRaisesRegex(ValueError, 'Replay changed tracked artifact'):
                    with checker.replay_tree('fixture', root) as snapshot:
                        self.assertEqual(snapshot.parent.parent, root/'build')
                        (snapshot/'unrelated.py').write_bytes(b'changed during replay')
                self.assertFalse(snapshot.exists())
                self.assertEqual((root/'unrelated.py').read_bytes(), b'unchanged checker bytes\n')


if __name__ == '__main__':
    unittest.main()
