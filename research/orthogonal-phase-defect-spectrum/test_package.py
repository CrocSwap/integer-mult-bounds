#!/usr/bin/env python3
"""Independent bounded controls for the phase-defect package."""
import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('phase_spectrum', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

class PhaseSpectrumTests(unittest.TestCase):
    def test_complete_binary_matrix_sets_through_four(self):
        # No group recurrence or transvections in the independent admission predicate.
        for n in range(1, 5):
            admitted = set()
            for cols in itertools.product(range(1 << n), repeat=n):
                rows = [[(cols[j] >> i) & 1 for j in range(n)] for i in range(n)]
                if all(sum(rows[k][i]*rows[k][j] for k in range(n)) % 2 == int(i == j)
                       for i in range(n) for j in range(n)):
                    admitted.add(cols)
            self.assertEqual(admitted, set(v.group(n)))

    def test_first_column_transversal_all_vectors_through_nine(self):
        for n in range(1, 10):
            count = 0
            for u in range(1 << n):
                if u.bit_count() % 2 != 1 or (n > 1 and u == (1 << n) - 1):
                    continue
                t = v.first_column_map(n, u)
                self.assertTrue(v.orthogonal(t))
                self.assertEqual(t[0], u)
                count += 1
            self.assertEqual(count, 1 if n == 1 else 2**(n-1) - (n % 2))

    def test_row_convention_is_material(self):
        s = v.compose((2, 1, 4, 8, 16), v.representative(5, 30))
        row_defect = v.defect(s)
        column_defect = sum((((c.bit_count()-1)//2) & 1) << i for i, c in enumerate(s))
        self.assertNotEqual(row_defect, column_defect)
        kernel = v.kernel(s, 1)
        base = v.kernel(v.identity(5), 1)
        wrong = 0
        for x, a in enumerate(kernel):
            sign = -1 if v.dot(row_defect, x) else 1
            self.assertEqual(a, tuple(sign*t for t in base[x]))
            wrong_sign = -1 if v.dot(column_defect, x) else 1
            wrong += a != tuple(wrong_sign*t for t in base[x])
        self.assertEqual(wrong, 16)

    def test_all_fiber_bijections_at_dimension_five(self):
        matrices = list(v.group(5))
        zero = {s for s in matrices if v.defect(s) == 0}
        for d in (0, 15, 23, 27, 29, 30):
            observed = {s for s in matrices if v.defect(s) == d}
            constructed = {v.compose(v.representative(5, d), h) for h in zero}
            self.assertEqual(observed, constructed)
            self.assertEqual(len(observed), 120)

    def test_semantic_controls(self):
        self.assertEqual(len(v.controls()), 9)

    def test_receipt_mutations_under_optimized_python(self):
        original = json.loads((HERE / 'CERTIFICATE.json').read_text())
        mutations = [
            lambda d: d['spectrum'][8].update(matrices_per_defect=348364801),
            lambda d: d['spectrum'][0].update(orthogonal_matrices=True),
            lambda d: d['complete_censuses'][3]['histogram'].pop('15'),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'bad.json'
            for mutate in mutations:
                data = json.loads(json.dumps(original)); mutate(data)
                target.write_text(json.dumps(data, indent=2, sort_keys=True)+'\n')
                result = subprocess.run([sys.executable, '-I', '-O', '-B', str(HERE/'verify.py'),
                                         '--receipt', str(target)], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('certificate mismatch', result.stderr)

    def test_relocated_source_corruptions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = root / 'research' / HERE.name
            shutil.copytree(HERE, package)
            sources = json.loads((HERE / 'SOURCES.json').read_text())
            inputs = [x['path'] for x in sources['files'] if x['usage'] == 'input']
            for name in inputs:
                p = root / name; p.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(v.ROOT / name, p)
            # Successful execution away from the checkout has no sys.path assumptions.
            command = [sys.executable, '-I', '-O', '-B', str(package/'verify.py')]
            good = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertEqual(good.returncode, 0, good.stderr)
            pin = package / 'sources' / 'PR1255-EXPECTED.json'
            saved = pin.read_bytes(); pin.write_bytes(saved+b'\n')
            bad = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn('predecessor receipt mismatch', bad.stderr)
            pin.write_bytes(saved)
            live = root / inputs[0]
            live.write_bytes(live.read_bytes()+b'\n# deliberate pin corruption\n')
            bad = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn('live input digest mismatch', bad.stderr)

if __name__ == '__main__':
    unittest.main(verbosity=2)
