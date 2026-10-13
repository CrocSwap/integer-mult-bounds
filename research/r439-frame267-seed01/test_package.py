"""Defect-sensitive package checks; no theorem claim from unit tests.

Ross Richardson, substantial OpenAI Codex assistance; Apache-2.0.
"""
import copy
import gzip
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Package(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verify = load('verify')
        cls.optimality = load('optimality')
        cls.recipe = json.loads((HERE / 'WITNESS.json').read_text())
        cls.word = json.loads(gzip.decompress((ROOT / cls.verify.WORD).read_bytes()))

    def test_boolean_gate_index_rejected(self):
        recipe = copy.deepcopy(self.recipe)
        recipe['replacement'][0][0] = True
        with self.assertRaisesRegex(self.verify.Reject, 'invalid circuit gate'):
            self.verify.build(self.word, recipe)

    def test_self_add_rejected(self):
        recipe = copy.deepcopy(self.recipe)
        recipe['replacement'][0] = [0, 0]
        with self.assertRaisesRegex(self.verify.Reject, 'invalid circuit gate'):
            self.verify.build(self.word, recipe)

    def test_wrong_wire_binding_rejected(self):
        recipe = copy.deepcopy(self.recipe)
        recipe['registers'][0] += 1
        with self.assertRaisesRegex(self.verify.Reject, 'unexpected circuit registers'):
            self.verify.build(self.word, recipe)

    def test_missing_literal_cleanup_fails_h4(self):
        new = self.verify.build(self.word, self.recipe)
        spec = importlib.util.spec_from_file_location('owning_checker', ROOT / self.verify.AUDITOR)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        new['C'] = copy.deepcopy(self.word['C'])
        checker = module.Word(new)
        checker.full()  # Identical scalar map: the stale inverse still restores.
        hypotheses, _, _ = checker.interface()
        self.assertFalse(hypotheses['H4_C_literal_reverse_at_full'])

    def test_independent_minimum_controls(self):
        identity = [[int(i == j) for j in range(6)] for i in range(6)]
        one = copy.deepcopy(identity)
        one[0][1] = 1
        self.assertEqual(self.optimality.check_minimum(identity, 0)['minimum'], 0)
        self.assertEqual(self.optimality.check_minimum(one, 1)['minimum'], 1)
        with self.assertRaisesRegex(ValueError, 'below independent distance'):
            self.optimality.check_minimum(one, 0)
        with self.assertRaisesRegex(ValueError, 'exceeds independent distance'):
            self.optimality.check_minimum(one, 2)

    def test_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            mark = Path(folder) / 'marker'
            mark.write_text('keep')
            run = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'verify.py'), '--output', folder],
                                 text=True, capture_output=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertEqual(mark.read_text(), 'keep')

    def test_minimal_relocation_and_tampering(self):
        with tempfile.TemporaryDirectory(prefix='frame267 path with spaces ') as folder:
            root = Path(folder)
            package = root / HERE.relative_to(ROOT)
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            pins = json.loads((HERE / 'SOURCES.json').read_text())
            for relative in pins['execution_inputs']:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, path)
            command = [sys.executable, '-I', '-O', '-B', str(package / 'verify.py')]
            passed = subprocess.run(command, text=True, capture_output=True)
            self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)
            expected = package / 'CERTIFICATE.json'
            data = json.loads(expected.read_text())
            data['independent_optimality']['layers'][1] -= 1
            expected.write_text(json.dumps(data))
            failed = subprocess.run(command, text=True, capture_output=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('certificate mismatch', failed.stderr)
            path = root / pins['execution_inputs'][0]
            path.write_bytes(path.read_bytes() + b'corruption')
            failed = subprocess.run(command, text=True, capture_output=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('source hash mismatch', failed.stderr)


if __name__ == '__main__':
    unittest.main()
