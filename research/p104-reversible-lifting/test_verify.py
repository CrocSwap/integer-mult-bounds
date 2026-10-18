"""Behavioral controls. Tekalign/Codex, Apache-2.0."""
import copy
import gzip
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import types
import unittest

HERE = Path(__file__).resolve().parent
v = types.ModuleType('checked_verifier')
v.__file__ = str(HERE / 'verify.py')
exec(compile((HERE / 'verify.py').read_bytes(), v.__file__, 'exec'), v.__dict__)


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lift, cls.old, cls.recipes = v.inputs()
        cls.plans = [(cls.lift.plan(r['left']), cls.lift.plan(r['right'])) for r in cls.recipes]

    def test_inverse_rotation_and_rounding_faults(self):
        raw = (HERE / 'lifting.py').read_text()
        bad = v.module(raw.replace('-1 if inverse else 1', '1'), 'bad_rotation')
        with self.assertRaisesRegex(ValueError, 'pair inverse'):
            v.pair_checks(bad)
        # A malformed non-bijective whole-output rounding cannot inherit the proof.
        bad = v.module(raw, 'bad_pair')
        bad.pair = lambda a, b, inverse=False: ((0, 0), (0, 0))
        with self.assertRaisesRegex(ValueError, 'pair inverse'):
            v.pair_checks(bad)

    def test_reverse_chronology_matters(self):
        lift = self.lift
        raw = (HERE / 'lifting.py').read_text()
        bad = v.module(raw.replace('reversed(range(rank)) if inverse else range(rank)',
                                   'range(rank)'), 'bad_order')
        rng = random.Random(53)
        source = [(rng.randrange(-19, 20), rng.randrange(-19, 20)) for _ in range(512)]
        left, right = self.plans[0]
        sent = lift.kernel(list(source), 7, left, right)
        self.assertEqual(lift.kernel(list(sent), 7, left, right, True), source)
        self.assertNotEqual(bad.kernel(list(sent), 7, left, right, True), source)
        # A separately nearest-rounded V is not this paired inverse, even
        # though it is the correct ideal native recipe.
        sparse = list(v.ZERO)
        sparse[0] = (257, 0)
        sparse = lift.permute(sparse, lift.inverse_plan(right))
        sent = lift.kernel(list(sparse), 7, left, right)
        old_back, old_grid, _ = self.old.execute(sent, 0, 0, self.recipes[1])
        self.assertNotEqual(old_back, lift.shift(sparse, old_grid))

    def test_all_actual_wrapper_cycles_and_scratch(self):
        lift = self.lift
        value = [(x, 3*x-19) for x in range(512)]
        for pair in self.plans:
            for p in pair:
                actual = list(value)
                lift.permute_inplace(actual, p)
                self.assertEqual(actual, lift.permute(value, p))
                lift.permute_inplace(actual, lift.inverse_plan(p))
                self.assertEqual(actual, value)
        bad = v.module((HERE / 'lifting.py').read_text().replace(
            'scratch, value[start] = value[start], (0, 0)',
            'scratch, value[start] = value[start], (1, 0)'), 'bad_scratch')
        with self.assertRaisesRegex(ValueError, 'scratch restored'):
            bad.permute_inplace(list(value), self.plans[0][0])

    def test_changed_recipe_binding_and_phase(self):
        root = v.ROOT / 'research/p104-rounded-collector/inputs'
        word = json.loads((root / 'WORD.json').read_bytes())
        native = json.loads(gzip.decompress((root / 'NATIVE.json.gz').read_bytes()))
        broken = copy.deepcopy(word)
        broken['program'][2031][4] = 6
        with self.assertRaisesRegex(ValueError, 'native binding'):
            v.bind(broken, native)
        recipes = copy.deepcopy(self.recipes)
        recipes[1]['left']['phase'] = (recipes[1]['left']['phase'] + 1) % 4
        plans = [(self.lift.plan(r['left']), self.lift.plan(r['right'])) for r in recipes]
        with self.assertRaisesRegex(ValueError, 'literal ideal inverse'):
            v.ideal_columns(self.lift, plans)

    def test_fixed_grid_relative_and_downcast_controls(self):
        lift = self.lift
        source = list(v.ZERO)
        source[53] = (1, 0)
        left, right = self.plans[0]
        # Deliberately keep the tiny input on grid f; requested relative b=8 fails.
        sent = lift.kernel(list(source), 7, left, right)
        error, common = v.defect(lift, sent, 0, source, 0, self.plans[0])
        self.assertGreater(error*(1 << 16), lift.norm2(source)*(1 << (2*common)))
        with self.assertRaisesRegex(ValueError, 'exact downshift'):
            lift.shift([(1, 0)], -1)
        # Adaptive execution restores exactly even with almost cancelled large dirt.
        opposite = [(-x, -y) for x, y in source]
        report = v.check_collector(lift, [source, opposite, source, list(v.ZERO), list(v.ZERO)],
                                   source, 19, 8, self.plans)
        self.assertEqual(report['fractional_bits_added'], 16)

    def test_cleaner_and_invoice_faults(self):
        raw = (HERE / 'lifting.py').read_text()
        bad = v.module(raw.replace("meter['field_adds'] += 1", "meter['field_adds'] += 2"), 'bad_invoice')
        with self.assertRaisesRegex(ValueError, 'literal invoice'):
            v.check_collector(bad, [list(v.ZERO) for _ in range(5)], list(v.ZERO), 0, 0, self.plans)
        bad = v.module(raw.replace('c[j] = (a-x, z-y)', 'c[j] = (a+x, z+y)'), 'bad_cleaner')
        source = list(v.ZERO)
        source[53] = (3, -1)
        with self.assertRaisesRegex(ValueError, 'private erasure'):
            bad.collector([source] + [list(v.ZERO) for _ in range(4)], list(v.ZERO), 0, 0, *self.plans[0])
        sources = [source] + [list(v.ZERO) for _ in range(4)]
        expected = self.lift.collector(sources, source, 19, 8, *self.plans[0])
        query = list(source)
        grid, meter = self.lift.execute_collector(sources, query, 19, 8, *self.plans[0])
        self.assertEqual((query, grid, meter), (expected['query'], expected['grid'], expected['meter']))

    def test_source_authentication(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for pin in v.loads((HERE / 'SOURCES.json').read_bytes())['files']:
                if pin['usage'] == 'input':
                    target = root / pin['path']
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(v.ROOT / pin['path'], target)
            path = root / 'research/p104-rounded-native-child/arithmetic.py'
            path.write_bytes(path.read_bytes() + b'\nraise RuntimeError("must not execute")\n')
            with self.assertRaisesRegex(ValueError, 'source SHA256'):
                v.inputs(root)

    def test_readonly_gitfree_and_receipt_controls(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = root / 'research/p104-reversible-lifting'
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            for pin in v.loads((HERE / 'SOURCES.json').read_bytes())['files']:
                if pin['usage'] == 'input':
                    target = root / pin['path']
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(v.ROOT / pin['path'], target)
            command = [sys.executable, '-Werror', '-I', '-O', '-B', str(package / 'verify.py')]
            paths = list(root.rglob('*'))
            for p in paths:
                p.chmod(0o555 if p.is_dir() else 0o444)
            before = {str(p.relative_to(root)): p.read_bytes() for p in paths if p.is_file()}
            try:
                result = subprocess.run(command, capture_output=True, text=True, timeout=60)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(before, {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()})
            finally:
                for p in paths:
                    p.chmod(0o755 if p.is_dir() else 0o644)
            receipt = package / 'RESULT.json'
            data = json.loads(receipt.read_bytes())
            data['pair']['exhaustive_pairs'] = True
            receipt.write_text(json.dumps(data))
            result = subprocess.run(command, capture_output=True, text=True, timeout=60)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('typed result mismatch', result.stderr)
            with self.assertRaisesRegex(ValueError, 'duplicate JSON'):
                v.loads('{"x":1,"x":2}')


if __name__ == '__main__':
    unittest.main()
