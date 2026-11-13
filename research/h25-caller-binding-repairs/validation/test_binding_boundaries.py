"""Changed production boundaries only; no genuine owner or native launch."""
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import types
import unittest

D = Path(__file__).resolve().parents[1]
W = Path('/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453')
OLD = W / 'outputs/connected-caller-assembly-20261107T2053Z/repair-v3'
NEW = D / 'successor'
LOADER_NAME = '_s03_fixed_entry_private_loader'

def clear_fixture():
    for name in list(sys.modules):
        if name.startswith('_s03_'):
            del sys.modules[name]

def factory_fixture(root):
    clear_fixture()
    path = root / 'implementation/bindings/private_loader.py'
    spec = importlib.util.spec_from_file_location(LOADER_NAME, path)
    loader = importlib.util.module_from_spec(spec)
    sys.modules[LOADER_NAME] = loader
    spec.loader.exec_module(loader)
    b = object.__new__(loader.PrivateBundle)
    b._pid, b.role = os.getpid(), 'CONTROLLER'
    b.manifest = json.loads((root / 'implementation/bindings/SOURCE-MANIFEST-v2.json').read_bytes())
    b.modules, b._images, b._functions, b._classes, b._runtime_seen = {}, {}, {}, {}, {}
    b._environment_association, b.guardian = None, None
    b.contract = {}  # Genuine required selection is deliberately absent.
    loader.RETAINED.append(b)  # Source-transport fixture, never a genuine runtime enrolment.
    module = b.load('environment_association')
    return loader, b, module

def launch_projection(root):
    """Complete native_argv body and the actual Popen expression, with inert ports."""
    text = (root / 'implementation/source/candidate_entry.py').read_text()
    tree = ast.parse(text)
    read_root = next(n.value.args[0].value for n in tree.body if isinstance(n, ast.Assign)
                     and any(isinstance(t, ast.Name) and t.id == 'READ_ROOT' for t in n.targets))
    argv_fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'native_argv')
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name)
             and n.func.value.id == 'subprocess' and n.func.attr == 'Popen']
    if len(calls) != 1:
        raise AssertionError('one selected production launch')
    captures = []
    def popen(argv, **kwargs):
        captures.append((argv, kwargs))
        return None
    def need(ok, message):
        if ok is not True:
            raise AssertionError(message)
    class Artifact:
        def lstat(self):
            return types.SimpleNamespace(st_mode=stat.S_IFDIR | 0o700,
                                         st_uid=os.getuid(), st_dev=11, st_ino=12)
        def resolve(self, strict=True):
            return self
        def iterdir(self):
            return iter(())
        def __str__(self):
            return '/fixture/artifact'
    ns = dict(Path=Path, stat=stat, os=os, need=need, READ_ROOT=Path(read_root),
              read_stable=lambda *args, **kwargs: b'',
              subprocess=types.SimpleNamespace(Popen=popen))
    exec(compile(ast.Module(body=[argv_fn], type_ignores=[]), str(root / 'candidate_entry.py'), 'exec'), ns)
    profile = dict(entry_path='/fixture/native', entry_sha256='a'*64, entry_bytes=1,
                   time_path='/fixture/time', time_sha256='b'*64, time_bytes=1, source_sha256='c'*64)
    stage = Path('/fixture/distinct-stage')
    timed = ['/fixture/time', '-f', 'fixture-format', '-o', '/fixture/usage', '--', '/fixture/science']
    config = dict(native_source_path=str(root / 'implementation/native/science_view_entry.c'))
    native = ns['native_argv'](profile, timed, stage, Artifact(), (13, 14), config)
    ns.update(native=native, stage=stage, ENV={'fixture':'inert'}, stdin={'object':object()},
              out=object(), err=object(), limits=lambda: None)
    exec(compile(ast.Expression(body=calls[0]), str(root / 'candidate_entry.py'), 'eval'), ns)
    if len(captures) != 1:
        raise AssertionError('one inert production call')
    return captures[0], Path(read_root)

class BindingBoundaries(unittest.TestCase):
    def tearDown(self):
        clear_fixture()

    def test_frozen_predecessor_rejects_actual_factory(self):
        loader, b, module = factory_fixture(OLD)
        with self.assertRaisesRegex(module.AssociationError, 'actual fixed private loader module'):
            b.associate_environment()
        self.assertIsNone(b._environment_association)
        self.assertEqual(module._LIVE, [])

    def test_successor_factory_reaches_required_input_boundary(self):
        loader, b, module = factory_fixture(NEW)
        self.assertEqual(module.LOADER_PATH, loader.__file__)
        with self.assertRaises(KeyError) as caught:
            b.associate_environment()
        self.assertEqual(caught.exception.args, ('environment_association',))
        self.assertIsNone(b._environment_association)
        self.assertEqual(module._LIVE, [])

    def test_strict_factory_negatives_remain(self):
        for variant in ('wrong_path', 'wrong_name', 'unenrolled', 'wrong_role',
                        'wrong_pid', 'missing_module', 'replaced_function', 'direct_call'):
            with self.subTest(variant=variant):
                loader, b, module = factory_fixture(NEW)
                if variant == 'wrong_path': loader.__file__ = '/fixture/wrong/private_loader.py'
                if variant == 'wrong_name': del sys.modules[LOADER_NAME]
                if variant == 'unenrolled': loader.RETAINED.remove(b)
                if variant == 'wrong_role': b.role = 'CAPTURE'
                if variant == 'wrong_pid': b._pid = -1
                if variant == 'missing_module': del sys.modules[module.__name__]
                if variant == 'replaced_function': module.open_parent = lambda bundle: object()
                with self.assertRaises((module.AssociationError, loader.BootstrapStop)):
                    if variant == 'direct_call': module.open_parent(b)
                    else: b.associate_environment()
                self.assertIsNone(b._environment_association)
                self.assertEqual(module._LIVE, [])

    def test_actual_native_command_and_launch_projection(self):
        (before, old_kwargs), old_read_root = launch_projection(OLD)
        (after, new_kwargs), new_read_root = launch_projection(NEW)
        self.assertNotEqual(str(old_kwargs['cwd']), before[10])
        self.assertEqual(str(new_kwargs['cwd']), after[10])
        self.assertEqual(new_kwargs['cwd'], new_read_root)
        self.assertEqual(new_read_root, old_read_root)
        self.assertEqual(before, after)
        self.assertTrue(new_kwargs['close_fds'])
        self.assertFalse(new_kwargs['start_new_session'])  # Its separate proof obligation is not changed.
        native = NEW / 'implementation/native/science_view_entry.c'
        self.assertEqual(native.read_bytes(), (OLD / 'implementation/native/science_view_entry.c').read_bytes())
        self.assertIn('original-cwd-is-preserved', native.read_text())

    def test_changed_frozen_stage_and_source_joins(self):
        m = json.loads((NEW / 'implementation/bindings/SOURCE-MANIFEST-v2.json').read_bytes())
        old = json.loads((OLD / 'implementation/bindings/SOURCE-MANIFEST-v2.json').read_bytes())
        self.assertEqual(m['control_pins'], old['control_pins'])
        self.assertEqual(m['source_pins']['runner'], m['source_pins']['common_runner'])
        for role in ('environment_association', 'waiting_entry', 'private_loader', 'supervisor'):
            row = m['source_pins'][role]
            self.assertEqual(hashlib.sha256(Path(row['path']).read_bytes()).hexdigest(), row['sha256'])
        queue = json.loads((NEW / 'implementation/bindings/control/IndependentPrefixDATAComposedV1-QUEUE.json').read_bytes())
        for mode, leaf in [('normal','joined-full-candidate-v1'), ('optimized','joined-full-candidate-refusal-v1')]:
            base = NEW / 'implementation/bindings/stages' / leaf
            stage = json.loads((base / 'STAGE.json').read_bytes())
            prior = json.loads((OLD / 'implementation/bindings/stages' / leaf / 'STAGE.json').read_bytes())
            self.assertEqual(set(stage['files']), set(prior['files']))
            for rel, row in stage['files'].items():
                data = (base / rel).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), row['sha256'])
                if rel != 'integration/candidate_entry.py':
                    self.assertEqual(row, prior['files'][rel])
                    self.assertEqual(data, (OLD / 'implementation/bindings/stages' / leaf / rel).read_bytes())
            self.assertEqual(stage['files']['integration/candidate_entry.py']['sha256'], m['source_pins']['waiting_entry']['sha256'])
            self.assertEqual(next(c for c in queue['cases'] if c['job']==mode)['stage_sha256'], hashlib.sha256((base/'STAGE.json').read_bytes()).hexdigest())

if __name__ == '__main__':
    unittest.main(verbosity=2)
