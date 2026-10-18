#!/usr/bin/env python3
"""Mathematical adverse controls and portable package-boundary tests."""
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
spec = importlib.util.spec_from_file_location('first_rank_drop_primary', HERE / 'verify.py')
primary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(primary)
spec2 = importlib.util.spec_from_file_location('first_rank_drop_independent', HERE / 'independent_check.py')
independent = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(independent)


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads((HERE / 'CERTIFICATE.json').read_text())
        cls.roots, _ = primary.roots_and_simple()
        cls.rows, _ = primary.decoder(cls.roots)

    def test_scalar_delivery_and_basis_mutations(self):
        for orbit in self.receipt['orbit_classes']:
            case, available, needed, costs = primary.analyze_puncture(int(orbit['representative']), self.roots, self.rows)
            live = primary.FULL ^ int(case['deleted'])
            for label in ('available', 'required'):
                patterns = [int(w) for w in case[label]['basis']]
                # Independently emit the source payload coefficients and replay
                # all 64 literal source columns, not just their dimensions.
                coordinates = {0: 0}
                for i, pattern in enumerate(patterns):
                    coordinates.update({word ^ pattern: mask | (1 << i) for word, mask in list(coordinates.items())})
                for source in range(120):
                    if not (live >> source & 1):
                        continue
                    coefficients = coordinates[self.rows[source] & live]
                    delivered = 0
                    for j, pattern in enumerate(patterns):
                        if coefficients >> j & 1:
                            delivered ^= pattern
                    self.assertEqual(delivered, self.rows[source] & live)
                with self.assertRaisesRegex(ValueError, 'independent totals'):
                    primary.check_cover(set(available), needed, patterns + [patterns[0]], costs, case[label]['cost'])
            bad = next(1 << i for i in range(120) if live >> i & 1 and (1 << i) not in available)
            with self.assertRaisesRegex(ValueError, 'admitted nonzero totals'):
                primary.check_cover(set(available), needed, [bad], costs, 1)

    def test_root_parity_corruption(self):
        roots = list(self.roots)
        bad = list(roots[0])
        bad[0] += 1
        roots[0] = tuple(bad)
        with self.assertRaisesRegex(ValueError, 'integral Gram'):
            primary.decoder(roots)

    def test_independent_rejects_incomplete_census(self):
        receipt = copy.deepcopy(self.receipt)
        receipt['cases'].pop()
        with self.assertRaisesRegex(ValueError, 'all first-rank-drop punctures'):
            independent.run(receipt)

    def test_independent_rejects_dimension_and_cost_claims(self):
        for field, value, expected in [('dimension', 8, 'target/ambient dimension'),
                                       ('cost', 49, 'minimum basis invoice')]:
            receipt = copy.deepcopy(self.receipt)
            orbit = next(x for x in receipt['orbit_classes'] if x['required']['dimension'] == 7)
            orbit['required'][field] = value
            with self.assertRaisesRegex(ValueError, expected):
                independent.run(receipt)

    def test_relocated_replay_and_boundaries(self):
        with tempfile.TemporaryDirectory(prefix='e8 rank drop ') as tmp:
            package = Path(tmp) / 'package with spaces'
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            output = Path(tmp) / 'fresh certificate.json'
            def run(script, *args):
                return subprocess.run([sys.executable, '-I', '-O', '-B', str(package / script), *map(str, args)],
                                      cwd=tmp, capture_output=True, text=True, timeout=90)
            result = run('verify.py', '--write', output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(output.read_bytes(), (package / 'CERTIFICATE.json').read_bytes())
            result = run('independent_check.py', '--certificate', output)
            self.assertEqual(result.returncode, 0, result.stderr)
            before = output.read_bytes()
            result = run('verify.py', '--write', output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('output path already exists', result.stderr)
            self.assertEqual(output.read_bytes(), before)
            # Exact reconstruction must reject altered claims.
            receipt_path = package / 'CERTIFICATE.json'
            receipt = json.loads(receipt_path.read_text())
            receipt['rank_retained_lower_bound'] = 45
            receipt_path.write_text(json.dumps(receipt))
            result = run('verify.py')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('certificate mismatch', result.stderr)
            # A retained-source mutation must fail before producing evidence.
            with (package / 'reference/PR939-PROOF.md').open('a') as stream:
                stream.write('\nmutation\n')
            failed_output = Path(tmp) / 'must not exist.json'
            result = run('verify.py', '--write', failed_output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('source SHA256 mismatch', result.stderr)
            self.assertFalse(failed_output.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
