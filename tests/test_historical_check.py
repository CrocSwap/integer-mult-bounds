"""Historical overlays authenticate exact bytes and leave live inputs untouched."""
import hashlib
import importlib.util
import json
from pathlib import Path
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
