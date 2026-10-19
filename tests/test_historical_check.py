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
        config = {'manifest': 'manifest.json', 'field': 'files', 'path': 'input.txt', 'input': 'old.txt', 'sha256': digest}
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

    def test_copy_keeps_empty_binary_and_large_files_independent(self):
        with tempfile.TemporaryDirectory() as td:
            root, inputs, config, paths = self.fixture(td)
            contents = {'empty': b'', 'binary': bytes(range(256)),
                        'large': bytes(range(256)) * 8193}
            for name, data in contents.items():
                (root / name).write_bytes(data)
            target = Path(td) / 'copy'
            expected = checker.materialize(root, target, config, paths + list(contents), inputs)
            self.assertEqual(set(expected), set(paths) | set(contents))
            for name, data in contents.items():
                with self.subTest(name=name):
                    self.assertEqual((target / name).read_bytes(), data)
                    self.assertEqual(expected[name], hashlib.sha256(data).hexdigest())
            checker.verify_unchanged(target, expected)
            (target / 'binary').write_bytes(b'changed in replay')
            self.assertEqual((root / 'binary').read_bytes(), bytes(range(256)))
            (root / 'large').write_bytes(b'changed in source')
            self.assertEqual((target / 'large').read_bytes(), contents['large'])

    def test_short_copy_rejects_instead_of_recording_a_false_digest(self):
        with tempfile.TemporaryDirectory() as td:
            root, inputs, config, paths = self.fixture(td)
            original_write = Path.write_bytes
            target = Path(td) / 'copy'

            def short_write(path, data):
                if path == target / 'unrelated.py':
                    return original_write(path, data[:-1])
                return original_write(path, data)

            with (patch.object(Path, 'write_bytes', short_write),
                  self.assertRaisesRegex(ValueError, 'Incomplete replay copy: unrelated.py')):
                checker.materialize(root, target, config, paths, inputs)
            self.assertEqual((root / 'unrelated.py').read_bytes(), b'unchanged checker bytes\n')

    def test_copy_write_error_propagates_without_modifying_source(self):
        with tempfile.TemporaryDirectory() as td:
            root, inputs, config, paths = self.fixture(td)
            before = {name: (root / name).read_bytes() for name in paths}
            with (patch.object(Path, 'write_bytes', side_effect=OSError('disk full')),
                  self.assertRaisesRegex(OSError, 'disk full')):
                checker.materialize(root, Path(td) / 'copy', config, paths, inputs)
            self.assertEqual({name: (root / name).read_bytes() for name in paths}, before)

    def test_missing_changed_and_nonbyte_pins_reject(self):
        with tempfile.TemporaryDirectory() as td:
            root, inputs, config, _paths = self.fixture(td)
            for entry in [None, '0'*64, {'representation': 'gzip-payload', 'sha256': config['sha256']}]:
                (root/'manifest.json').write_text(json.dumps({'files': {'input.txt': entry}}))
                with self.subTest(entry=entry), self.assertRaises(ValueError):
                    checker.authenticated_input(root, config, inputs)

    def test_nested_coverage_pin_rejects_missing_duplicate_and_changed_records(self):
        with tempfile.TemporaryDirectory() as td:
            root, inputs, config, paths = self.fixture(td)
            config['field'] = ['pull_requests', '681', 'files']
            record = {'integrated_path': 'input.txt', 'integrated_sha256': config['sha256']}
            manifest = root / 'manifest.json'
            def write(records):
                manifest.write_text(json.dumps({'pull_requests': {'681': {'files': records}}}))
            write([record])
            self.assertEqual(checker.authenticated_input(root, config, inputs), b'historical input\n')
            for records in ([], [record, record], [{**record, 'integrated_sha256': '0'*64}]):
                write(records)
                with self.subTest(records=records), self.assertRaises(ValueError):
                    checker.authenticated_input(root, config, inputs)

    def test_ci_document_successor_preserves_historical_context_and_guards(self):
        # 54bbb81c appended timeout guidance to the already accepted live doc.
        # The PR695 evidence and every historical checker remain unchanged.
        config = next(entry for entry in checker.CONFIG['tooling-ledger']['additional_inputs']
                      if entry['path'] == 'docs/ci-verification.md')
        live = (ROOT / config['path']).read_bytes()
        historical = (checker.INPUTS / config['input']).read_bytes()
        previous = live.split(b'\n### Bound an isolated test module\n', 1)[0]
        self.assertEqual(hashlib.sha256(previous).hexdigest(),
                         'ae5bcac684ce2188632f38dee8ed46ebdc9588f490401505aa1cac33c55d84db')
        self.assertEqual(hashlib.sha256(live).hexdigest(),
                         'a3711fe12d560fac7726c530b9c8c622182f3d4f231a876c163616e49bd911bc')
        self.assertEqual(hashlib.sha256(historical).hexdigest(), config['sha256'])
        with tempfile.TemporaryDirectory() as td:
            root, inputs = Path(td) / 'source', Path(td) / 'inputs'
            root.mkdir()
            inputs.mkdir()
            document = root / config['path']
            document.parent.mkdir(parents=True)
            baseline = inputs / config['input']
            baseline.write_bytes(historical)
            manifest = root / config['manifest']
            manifest.parent.mkdir(parents=True)
            manifest_bytes = (ROOT / config['manifest']).read_bytes()
            manifest.write_bytes(manifest_bytes)
            for label, value in [('current', live), ('previous', previous),
                                 ('historical', historical)]:
                with self.subTest(live_context=label):
                    document.write_bytes(value)
                    self.assertEqual(checker.authenticated_input(root, config, inputs), historical)
            document.write_bytes(live + b' ')
            with self.assertRaisesRegex(ValueError, 'Unrecognized live source update'):
                checker.authenticated_input(root, config, inputs)
            document.write_bytes(live)
            baseline.write_bytes(historical + b' ')
            with self.assertRaisesRegex(ValueError, 'Changed historical input'):
                checker.authenticated_input(root, config, inputs)
            baseline.write_bytes(historical)
            for mutation in ('changed', 'duplicate'):
                coverage = json.loads(manifest_bytes)
                records = coverage['pull_requests']['695']['files']
                record = next(row for row in records if row['integrated_path'] == config['path'])
                if mutation == 'changed':
                    record['integrated_sha256'] = '0' * 64
                else:
                    records.append(dict(record))
                manifest.write_text(json.dumps(coverage), encoding='utf-8')
                with self.subTest(pin_mutation=mutation), self.assertRaises(ValueError):
                    checker.authenticated_input(root, config, inputs)
            manifest.write_bytes(manifest_bytes)
            (root / 'unrelated.txt').write_bytes(b'unchanged current input\n')
            paths = [config['path'], config['manifest'], 'unrelated.txt']
            before = {name: (root / name).read_bytes() for name in paths}
            target = Path(td) / 'copy'
            expected = checker.materialize(root, target, config, paths, inputs)
            self.assertEqual((target / config['path']).read_bytes(), historical)
            self.assertEqual({name: (root / name).read_bytes() for name in paths}, before)
            checker.verify_unchanged(target, expected)
            for name in (config['path'], 'unrelated.txt'):
                path = target / name
                original = path.read_bytes()
                path.write_bytes(original + b' ')
                with self.subTest(replay_mutation=name), self.assertRaisesRegex(
                        ValueError, 'Replay changed tracked artifact'):
                    checker.verify_unchanged(target, expected)
                path.write_bytes(original)
            checker.verify_unchanged(target, expected)
            self.assertEqual({name: (root / name).read_bytes() for name in paths}, before)

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
            with (patch.object(Path, 'is_symlink', return_value=True),
                  self.assertRaisesRegex(ValueError, 'Non-file tracked')):
                checker.materialize(root, Path(td)/'copy', config, paths, inputs)

    def test_makefile_append_is_allowed_but_original_prefix_mutation_rejects(self):
        with tempfile.TemporaryDirectory() as td:
            root, inputs, config, _paths = self.fixture(td)
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
            root, inputs, config, _paths = self.fixture(td)
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
        config['additional_inputs'] = [{
            'manifest': 'manifest.json', 'field': 'files', 'path': 'second.py',
            'input': 'second.txt', 'sha256': digest}]
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
            'scripts/shared_point_circuit.py', 'scripts/partial_swap/shared.py',
            'scripts/audit_sparse_fusion.py'})
        for entry in entries:
            with self.subTest(path=entry['path']):
                checker.authenticated_input(ROOT, entry)

    def test_scheduler_and_hpe_overlays_bind_frozen_and_live_bytes(self):
        cases = [*checker.CONFIG['reconciliation92']['additional_inputs'],
                 checker.CONFIG['tooling-exact']]
        for config in cases:
            with self.subTest(path=config['path']):
                original = (checker.INPUTS / config['input']).read_bytes()
                self.assertEqual(hashlib.sha256(original).hexdigest(), config['sha256'])
                self.assertEqual(checker.authenticated_input(ROOT, config), original)
                live = hashlib.sha256((ROOT / config['path']).read_bytes()).hexdigest()
                self.assertIn(live, config['accepted_live_sha256'])
                self.assertNotEqual(live, config['sha256'])
        self.assertEqual(len(checker.CONFIG['tooling-exact']['commands']), 7)

    def test_new_context_overlays_reject_real_pin_and_live_drift(self):
        for real in [*checker.CONFIG['reconciliation92']['additional_inputs'],
                     checker.CONFIG['tooling-exact']]:
            with self.subTest(path=real['path']), tempfile.TemporaryDirectory() as td:
                root, inputs = Path(td)/'repo', Path(td)/'inputs'
                root.mkdir()
                inputs.mkdir()
                manifest = root / real['manifest']
                manifest.parent.mkdir(parents=True,exist_ok=True)
                manifest.write_text(json.dumps({real['field']:{real['path']:real['sha256']}}))
                live = root / real['path']
                live.parent.mkdir(parents=True,exist_ok=True)
                live.write_bytes((ROOT/real['path']).read_bytes())
                original = (checker.INPUTS/real['input']).read_bytes()
                (inputs/real['input']).write_bytes(original)
                self.assertEqual(checker.authenticated_input(root,real,inputs),original)
                live.write_bytes(b'unreviewed live successor')
                with self.assertRaisesRegex(ValueError,'Unrecognized live source update'):
                    checker.authenticated_input(root,real,inputs)
                live.write_bytes((ROOT/real['path']).read_bytes())
                (inputs/real['input']).write_bytes(b'corrupted immutable historical blob')
                with self.assertRaisesRegex(ValueError,'Changed historical input'):
                    checker.authenticated_input(root,real,inputs)
                (inputs/real['input']).write_bytes(original)
                manifest.write_text(json.dumps({real['field']:{real['path']:'0'*64}}))
                with self.assertRaisesRegex(ValueError,'Missing or changed predecessor source pin'):
                    checker.authenticated_input(root,real,inputs)

    def test_git_free_catalog_rejects_corruption_and_missing_inputs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'input.txt').write_bytes(b'input')
            catalog = root / '.historical-ci-tracked.json'
            raw = json.dumps(['input.txt']).encode()
            catalog.write_bytes(raw)
            with patch.dict(os.environ, {'HISTORICAL_CI_CATALOG_SHA256': hashlib.sha256(raw).hexdigest()}):
                self.assertEqual(checker.tracked_paths(root), ['input.txt'])
                catalog.write_bytes(raw + b' ')
                with self.assertRaisesRegex(ValueError, 'Changed historical tracked-input catalog'):
                    checker.tracked_paths(root)
                catalog.write_bytes(raw)
                (root / 'input.txt').unlink()
                with self.assertRaisesRegex(ValueError, 'Missing historical tracked input'):
                    checker.tracked_paths(root)

    def test_live_guards_also_admit_the_actual_committed_source_bytes(self):
        # Windows Git attributes can normalize bytes at commit time. A local
        # working-copy hash alone is not a published source admission check.
        for name, config in checker.CONFIG.items():
            for entry in [config, *config.get('additional_inputs', [])]:
                if 'accepted_live_sha256' not in entry:
                    continue
                with self.subTest(package=name, path=entry['path']):
                    raw = subprocess.check_output(['git', 'show', 'HEAD:' + entry['path']], cwd=ROOT)
                    digest = hashlib.sha256(raw).hexdigest()
                    self.assertIn(digest, [entry['sha256'], *entry['accepted_live_sha256']])

    def test_real_snapshots_match_unchanged_predecessor_pins(self):
        for name, config in checker.CONFIG.items():
            with self.subTest(package=name):
                for entry in [config, *config.get('additional_inputs', [])]:
                    checker.authenticated_input(ROOT, entry)

    def test_legacy_graph_and_certificate_context_match_original_provenance(self):
        baseline = (ROOT / 'research/partial-swap-digest/baseline.py').read_bytes()
        entry = checker.LEGACY_SHARED
        self.assertEqual(checker.authenticated_input(ROOT, entry), baseline)
        config = checker.CONFIG['legacy-producers']['additional_inputs'][0]
        original = checker.authenticated_input(ROOT, config)
        verifier = (ROOT / 'research/partial-swap-digest/verify.py').read_text()
        self.assertIn('BASE_CERT_SHA256 = "' + hashlib.sha256(original).hexdigest() + '"', verifier)
        self.assertEqual(json.loads(original)['source_sha256']['scripts/partial_swap/shared.py'], entry['sha256'])
        for family in ('community', 'producers', 'strips', 'pair'):
            self.assertEqual(checker.CONFIG['legacy-' + family]['make_target'], 'verify-' + family)


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

    def test_nested_replay_retains_full_inventory_without_git_metadata(self):
        body = "import os, pathlib, subprocess, sys\nif not os.environ.get('NESTED_REPLAY'):\n    root = pathlib.Path(__file__).resolve().parents[2]\n    subprocess.run([sys.executable, '-B', str(root / 'scripts/replay_historical_check.py'), 'r420'],\n                   env=dict(os.environ, NESTED_REPLAY='1'), check=True)\nelse:\n    print('PASS_NESTED_GIT_FREE_REPLAY')\n"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.sandbox(root, body)
            result = self.run_cli(root, '2')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('PASS_NESTED_GIT_FREE_REPLAY', result.stdout)
            self.assertEqual(result.stdout.count('PASS_HISTORICAL_CHECK r420'), 2)

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
