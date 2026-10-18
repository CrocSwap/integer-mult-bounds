"""Semantic and package controls; Philipp / GPT-6 Astra, Apache-2.0."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Package(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v = load('verify')
        cls.lib = cls.v.engine()
        cls.word, cls.baseline, _, _ = cls.lib.load()
        cls.certificate, cls.candidate = cls.v.compute()
        cls.gauges = {int(h): k for h, k in json.loads((HERE / 'GAUGES.json').read_bytes())['forward'].items()}

    def test_complete_receipt(self):
        self.assertEqual(self.v.canonical(self.certificate), self.v.canonical(json.loads((HERE / 'CERTIFICATE.json').read_bytes())))
        self.assertEqual(load('independent').run()['status'], 'PASS_INDEPENDENT_MANY_DYADIC_PRIMITIVES')

    def test_boundary_and_coefficient_mutants(self):
        events = self.candidate['forward']
        n = len(self.gauges)
        mutants = [events[:1] + events[2:], events[:-(n + 1)] + events[-n:],
                   events[:-(n + 1)] + events[-1:]]
        wrong = copy.deepcopy(events)
        for i, e in enumerate(self.baseline['forward'][1:-1], 1):
            if e[0] == 'scalar' and e[1][0] == 'add' and e != events[i + n]:
                wrong[i + n] = e
                break
        mutants.append(wrong)
        # Reuse the forward entry scales only; keep the backward interior/exit.
        wrong = copy.deepcopy(self.candidate['backward'])
        wrong[1:n + 1] = copy.deepcopy(events[1:n + 1])
        for index, mutant in enumerate(mutants):
            with self.subTest(fault=index):
                with self.assertRaises(ValueError):
                    self.lib.replay(mutant, 'forward')
        with self.assertRaises(ValueError):
            self.lib.replay(wrong, 'backward')

    def test_shared_edges_and_local_optimum_controls(self):
        helpers = self.certificate['eligible_helpers']
        terms = self.v.terms_from(self.lib, self.baseline['forward'], helpers)
        joint = self.v.objective(terms, self.gauges)
        separated = sum(self.v.objective(terms, {h: k}) for h, k in self.gauges.items())
        self.assertEqual(joint, -6500)
        self.assertNotEqual(joint, separated)
        old = dict(self.v.coordinate_candidates(terms, {}, 427))[0]
        self.assertLess(min(v for _, v in self.v.coordinate_candidates(terms, {}, 427)), old)
        # The ±1 shortcut matters: two coefficients 1/2 choose exponent +1
        # despite the undiscounted |.| objective tying 0 and 1.
        toy = [(True, -1, 1, -1)] * 2
        self.assertEqual(self.v.objective(toy, {1: 1}), -2)

    def test_domain_rejections(self):
        for helper in (0, 703, self.word['centers'][0]):
            with self.subTest(helper=helper):
                with self.assertRaises(ValueError):
                    self.v.transform(self.lib, self.word, self.baseline['forward'], {helper: 1})

    def test_optimized_relocation_and_corruptions(self):
        with tempfile.TemporaryDirectory(prefix='k8 many dyadic ') as raw:
            root = Path(raw)
            package = root / 'research/k8-many-dyadic-seed29'
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            pins = json.loads((HERE / 'vendor/pr1161/SOURCES.json').read_bytes())
            for path in pins['files']:
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.symlink_to(self.v.ROOT / path)

            def run():
                return subprocess.run([sys.executable, '-I', '-O', '-B', str(package / 'verify.py')],
                                      cwd=root, capture_output=True, text=True, timeout=60)

            self.assertEqual(run().returncode, 0)
            p = package / 'CERTIFICATE.json'
            original = p.read_bytes()
            corrupted = json.loads(original)
            corrupted['orientations']['forward']['candidate']['real_primitives'] -= 1
            p.write_text(json.dumps(corrupted))
            self.assertNotEqual(run().returncode, 0)
            p.write_bytes(original)
            p = package / 'GAUGES.json'
            original = p.read_bytes()
            corrupted = json.loads(original)
            corrupted['forward'].pop('225')
            p.write_text(json.dumps(corrupted))
            self.assertNotEqual(run().returncode, 0)
            p.write_bytes(original)
            p = package / 'vendor/pr1161/SOURCES.json'
            original = p.read_bytes()
            corrupted = json.loads(original)
            corrupted['files'].pop('research/complex-dyadic-lowering/lower.py')
            p.write_text(json.dumps(corrupted))
            self.assertNotEqual(run().returncode, 0)
            p.write_bytes(original)
            p = root / 'research/complex-dyadic-lowering/lower.py'
            original = p.read_bytes()
            p.unlink()  # Remove only the temporary symlink, never the input.
            p.write_bytes(original + b'\n# corruption control\n')
            self.assertNotEqual(run().returncode, 0)
            p.write_bytes(original)
            # A falsified advertised saving is rejected by complete receipt binding.
            p = package / 'verify.py'
            p.write_text(p.read_text().replace("'saving_complex': before['complex_primitives'] - after['complex_primitives'],",
                                               "'saving_complex': 999999,"))
            self.assertNotEqual(run().returncode, 0)


if __name__ == '__main__':
    unittest.main()
