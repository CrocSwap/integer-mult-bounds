"""Mathematical and fail-closed controls for the P112 completion certificate."""
from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
from itertools import permutations, product
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import unittest

HERE = Path(__file__).resolve().parent


def load(name, filename):
    spec = spec_from_file_location(name, HERE / filename)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V = load('p112_primary', 'verify.py')
I = load('p112_independent', 'independent.py')


class ArithmeticTests(unittest.TestCase):
    def test_all_small_determinants(self):
        perms = list(permutations(range(3)))
        signs = [(-1) ** sum(p[i] > p[j] for i in range(3) for j in range(i + 1, 3))
                 for p in perms]
        for values in product((-1, 0, 1), repeat=9):
            matrix = [values[:3], values[3:6], values[6:]]
            expected = sum(sign * matrix[0][p[0]] * matrix[1][p[1]] * matrix[2][p[2]]
                           for sign, p in zip(signs, perms))
            self.assertEqual(I.determinant(matrix), expected)
        for values in product((-1, 0, 1), repeat=4):
            matrix = [values[:2], values[2:]]
            expected = 2 if values[0] * values[3] != values[1] * values[2] else int(any(values))
            self.assertEqual(I.rational_rank(matrix), expected)

    def test_modular_rank_is_only_a_lower_bound(self):
        matrix = [[V.PRIME, 0], [0, 1]]
        self.assertEqual(V.rank(matrix), 1)
        self.assertEqual(I.rational_rank(matrix), 2)
        self.assertEqual(I.determinant(matrix), V.PRIME)


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = V.bind_sources()
        cls.roots, cls.gram = V.geometry(cls.source)
        cls.cert = json.loads((HERE / 'CENSUS.json').read_text())
        cls.result = json.loads((HERE / 'RESULT.json').read_text())

    def test_missing_pair_and_false_minor_reject(self):
        bad = deepcopy(self.cert); bad['pairs'].pop()
        with self.assertRaisesRegex(ValueError, 'cardinality'):
            I.audit_census(self.roots, self.gram, bad)
        bad = deepcopy(self.cert); bad['pairs'][0][4][1] = bad['pairs'][0][4][0]
        with self.assertRaisesRegex(ValueError, 'multiplicity'):
            I.audit_census(self.roots, self.gram, bad)

    def test_missing_projective_direction_rejects(self):
        bad = deepcopy(self.cert); bad['odd_pencils'][0][3].pop()
        with self.assertRaisesRegex(ValueError, 'projective exceptional'):
            I.audit_census(self.roots, self.gram, bad)

    def test_false_row_threshold_rejects(self):
        bad = deepcopy(self.result); bad['two_column_failure_row_floor'] = 54
        with self.assertRaisesRegex(ValueError, 'pencil summary'):
            I.audit_result(self.roots, self.gram, bad, self.cert)
        bad = deepcopy(self.cert); bad['odd_pencils'][0][3][0][2] += 1
        with self.assertRaisesRegex(ValueError, 'exact pencil support'):
            I.audit_census(self.roots, self.gram, bad)

    def test_source_change_and_missing_source_reject(self):
        with TemporaryDirectory(prefix='source-control-', dir=HERE) as tmp:
            root = Path(tmp)
            package = root / 'research' / 'p112-two-column-completion'
            package.mkdir(parents=True)
            manifest = json.loads((HERE / 'SOURCES.json').read_text())
            for entry in manifest['files']:
                if entry['usage'] == 'input':
                    target = root / entry['path']; target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes((V.ROOT / entry['path']).read_bytes())
            (package / 'SOURCES.json').write_text(json.dumps(manifest))
            with patch.object(V, 'ROOT', root), patch.object(V, 'HERE', package):
                V.bind_sources()
                source = root / V.SOURCE
                source.write_bytes(source.read_bytes() + b' ')
                with self.assertRaisesRegex(ValueError, 'source bytes changed'):
                    V.bind_sources()
                manifest['files'] = [e for e in manifest['files'] if e['path'] != V.SOURCE]
                (package / 'SOURCES.json').write_text(json.dumps(manifest))
                with self.assertRaisesRegex(ValueError, 'input inventory'):
                    V.bind_sources()

    def test_complex_completion_by_exact_realification(self):
        # G+(1+i)Q. This is an exact Gaussian-integer fixture; no floating point.
        q = V.low_witness(self.gram, 0, 1)
        a = [[self.gram[i][j] + q[i][j] for j in range(112)] for i in range(112)]
        realification = [a[i] + [-x for x in q[i]] for i in range(112)]
        realification += [q[i] + a[i] for i in range(112)]
        self.assertEqual(I.rational_rank(realification), 18)

    def test_mask_is_necessary_for_the_rank_one_claim(self):
        # An unmasked rank-one correction can decrease rank to seven.
        # For a root normal x_j, G-(G e_j)(G e_j)^T/4 removes one root-code direction.
        g = [row[0] for row in self.gram]
        scaled = [[4 * self.gram[i][j] - g[i] * g[j] for j in range(112)] for i in range(112)]
        self.assertEqual(I.rational_rank(scaled), 7)
        correction = [[-g[i] * g[j] for j in range(112)] for i in range(112)]
        with self.assertRaisesRegex(ValueError, 'not odd-only'):
            V.validate_mask(correction, self.gram)


if __name__ == '__main__':
    unittest.main()
