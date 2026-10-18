#!/usr/bin/env python3
"""Package rejection/portability controls. Ross Richardson / Codex, Apache-2.0."""
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import model
import oracle
import verify


class Tests(unittest.TestCase):
    def test_invalid_inputs(self):
        for args in ((0, 1, 1), (-1, 2, 2), (True, 1, 1), (2, 0, 1), (2, 1, -1)):
            with self.assertRaises(ValueError):
                model.plan(*args)
        for r in ([], [[1]], [[1, 0, 0]]*2, [[1, 2, 3], [1], [1, 2, 3]], [[True]*3]*3):
            with self.assertRaises(ValueError):
                model.dimensions(r)
        with self.assertRaises(ValueError):
            model.matrix_of({'children': []})
        with self.assertRaises(ValueError):
            model.matrix_of({'children': [{'matrix': [[1, 0, 0], [0, 1, 0], [0, 0, 1]]}, {'matrix': [[0]*6 for _ in range(3)]}]})
        with self.assertRaises(ValueError):
            model.rotate(0, 1, 3)

    def test_every_emitted_phase_path(self):
        # Independently vary readers with distinct symbolic responses, including
        # lengths beyond the full nine-choice census; inspect returned path.
        for k in range(1, 41):
            for a, b in ((1, 1), (1, 7), (7, 1), (2, 5), (5, 2)):
                price, gaps = model.plan(k, a, b)
                w = o = 0
                terms = []
                paid = 0
                for i, (u, v) in enumerate(gaps):
                    paid += a*(u != 0)+b*(v != 0)
                    w = (w+u) % 3
                    o = (o+v) % 3
                    terms = [(t+v) % 3 for t in terms]
                    if i < k:
                        terms.append(w)
                        w = (w+1) % 3
                self.assertEqual((w, o, terms, paid), (0, 0, [0]*k, price))

    def test_cycle_every_dirty_column(self):
        for p in (0, 1, 2):
            macro = model.rotate(0, 2, p)
            self.assertEqual(oracle.replay(macro, 6)[0], oracle.replay(model.expand(macro), 6)[0])
            raw = model.expand(macro)
            self.assertEqual(oracle.replay(raw+model.inverse(raw), 6)[0], oracle.identity(6))

    def test_noninvolution(self):
        node = verify.make_tree(random.Random(7), 1, 1, 1, 0)
        w, size = model.compile_word(node, 'reader')
        self.assertNotEqual(oracle.replay(w+w, size)[0], oracle.identity(size))
        self.assertEqual(oracle.replay(w+model.inverse(w), size)[0], oracle.identity(size))

    def test_checkpoint_observer(self):
        # A phase-one frame changes an arbitrary original output even with zero readers.
        child = {'matrix': [[0]*3 for _ in range(3)]}
        prefix = model.reader(child, 3, 0, 6, 1, 1)+model.rotate(0, 1, 1)
        self.assertNotEqual(oracle.replay(prefix, 6)[0], oracle.identity(6))

    def test_special_tuple_not_uniform_optimum(self):
        children = [{'matrix': [[0]*3 for _ in range(3)]} for _ in range(3)]
        # Three zero-reader child drifts cancel with no boundaries. This does not
        # contradict the strictly positive uniform class optimum.
        word = sum((model.reader(c, 3, 0, 6, 1, 1) for c in children), [])
        self.assertEqual(oracle.replay(word, 6)[0], oracle.identity(6))
        self.assertGreater(model.plan(3, 2, 2)[0], 0)

    def test_archive_relocation_and_corruptions(self):
        with tempfile.TemporaryDirectory(prefix='cyclic-output-package-') as td:
            target = Path(td)/'renamed'
            shutil.copytree(HERE, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            def run():
                return subprocess.run([sys.executable, '-I', '-O', '-B', str(target/'verify.py')], cwd=td, capture_output=True, text=True, timeout=120)
            clean = run()
            self.assertEqual(clean.returncode, 0, clean.stderr)
            self.assertIn('PASS_CYCLIC_OUTPUT_RESTORATION', clean.stdout)
            for name in ('CERTIFICATE.json', 'FIXTURE.json', 'PREDECESSORS.json', 'sources/PR1227-README.md'):
                path = target/name
                old = path.read_bytes()
                if name == 'CERTIFICATE.json':
                    x = json.loads(old); x['fixture']['optimized']['invoice']['dispatch'] -= 1
                    data = json.dumps(x).encode()
                elif name == 'FIXTURE.json':
                    x = json.loads(old); x['children'][0]['matrix'][0][0] += 1
                    data = json.dumps(x).encode()
                elif name == 'PREDECESSORS.json':
                    x = json.loads(old); x[0]['sha256'] = '0'*64
                    data = json.dumps(x).encode()
                else:
                    data = old+b'\nCORRUPTION CONTROL\n'
                path.write_bytes(data)
                bad = run()
                self.assertNotEqual(bad.returncode, 0, name+' corruption was accepted')
                path.write_bytes(old)
            # Mathematical failure, with unchanged expected certificate.
            path = target/'model.py'; old = path.read_bytes()
            bad_code = old.replace(b'(s-t-1) % 3', b'(s-t+1) % 3')
            self.assertNotEqual(bad_code, old)
            path.write_bytes(bad_code)
            self.assertNotEqual(run().returncode, 0, 'wrong cyclic drift accepted')
            path.write_bytes(old)
            # Export is canonical and does not rely on the tracked certificate.
            emitted = subprocess.run([sys.executable, '-I', '-O', '-B', str(target/'verify.py'), '--emit'], cwd=td, capture_output=True, check=True, timeout=120)
            self.assertEqual(emitted.stdout, (target/'CERTIFICATE.json').read_bytes())


if __name__ == '__main__':
    result = unittest.main(exit=False)
    if not result.result.wasSuccessful():
        raise SystemExit(1)
    print('PASS_CYCLIC_OUTPUT_PACKAGE tests=7 relocation=1 corruptions=5')
