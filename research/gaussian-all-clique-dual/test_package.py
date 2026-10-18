"""Scope, arithmetic, enumeration and portable failure-detection controls."""
from itertools import combinations
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import independent
import verify

HERE = Path(__file__).resolve().parent


class MathematicalControls(unittest.TestCase):
    def test_primary_clique_domain_all_small_graphs(self):
        checked = 0
        for n in range(1, 6):
            edges = list(combinations(range(n), 2))
            for encoding in range(1 << len(edges)):
                adjacency = [0] * n
                for k, (i, j) in enumerate(edges):
                    if encoding >> k & 1:
                        adjacency[i] |= 1 << j
                        adjacency[j] |= 1 << i
                expected = set()
                for mask in range(1, 1 << n):
                    members = [i for i in range(n) if mask >> i & 1]
                    if all(adjacency[i] >> j & 1 for i, j in combinations(members, 2)):
                        expected.add(mask)
                actual = list(verify.all_cliques(adjacency))
                self.assertEqual(len(actual), len(set(actual)))
                self.assertEqual(set(actual), expected)
                checked += 1
        self.assertEqual(checked, 1099)

    def test_two_rank_implementations(self):
        # Complex dependence differs from dependence of real coordinate rows.
        matrix = [[(1, 0), (0, 1)], [(0, 1), (-1, 0)]]
        self.assertEqual(independent.gaussian_rank(matrix), 1)
        realified = []
        for row in matrix:
            realified.append([x for a, b in row for x in (a, -b)])
            realified.append([x for a, b in row for x in (b, a)])
        self.assertEqual(len(verify.reduced_basis(realified)), 2)

    def test_wrong_original_and_stronger_duals_rejected(self):
        with self.assertRaisesRegex(ValueError, 'does not dominate'):
            verify.check_dual_hit(1, 42, 45)
        with self.assertRaisesRegex(ValueError, 'does not dominate'):
            verify.check_dual_hit(12, 108, 10)
        verify.check_dual_hit(12, 108, 9)

    def test_false_frame_partition_rejected(self):
        _, lines = verify.roots_and_lines()
        _, orthogonal, dual, _ = verify.graph_data(lines)
        wrong = list(dual)
        wrong[0] ^= 1 << next(verify.bits(wrong[0]))
        with self.assertRaises(ValueError):
            verify.frames_from_dual(wrong)
        wrong = list(orthogonal)
        wrong[0] |= 1
        with self.assertRaises(ValueError):
            verify.check_orthogonal_graph(wrong)

    def test_nonorthogonal_normals_have_different_charge(self):
        _, lines = verify.roots_and_lines()
        adjacency, orthogonal, _, _ = verify.graph_data(lines)
        j = next(verify.bits(adjacency[0]))
        with self.assertRaisesRegex(ValueError, 'wrong rational pairing rank'):
            verify.check_geometry(lines, orthogonal, ((0, j),))

    def test_claim_fields_are_checked_independently(self):
        certificate = json.loads((HERE / 'CERTIFICATE.json').read_text())
        result = {key: certificate[key] for key in independent.MATHEMATICAL_FIELDS}
        for field, value in [('ceiling', '39'), ('dual_multiplier', '1/10'),
                             ('all_cliques_sha256', '0' * 64), ('dual_pairs', [])]:
            damaged = dict(certificate, **{field: value})
            with self.assertRaisesRegex(ValueError, field):
                independent.compare_certificate(result, damaged)


class PortableControls(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.folder = Path(self.temporary.name)
        self.package = self.folder / 'relocated'
        shutil.copytree(HERE, self.package, ignore=shutil.ignore_patterns('__pycache__'))

    def tearDown(self):
        self.temporary.cleanup()

    def run_script(self, script, *arguments):
        return subprocess.run([sys.executable, '-I', '-O', '-B',
                               str(self.package / script), *map(str, arguments)],
                              cwd=self.folder, capture_output=True, text=True, timeout=120)

    def test_relocated_optimized_independent_replay(self):
        result = self.run_script('independent.py')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('PASS_INDEPENDENT_GAUSSIAN_ALL_CLIQUE_DUAL', result.stdout)

    def test_changed_retained_source_rejected(self):
        source = self.package / 'vendor/pr738-PROOF.md'
        source.write_bytes(source.read_bytes() + b'corruption\n')
        result = self.run_script('verify.py')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('retained source mismatch', result.stderr)

    def test_escaping_source_path_rejected(self):
        path = self.package / 'SOURCES.json'
        sources = json.loads(path.read_text())
        sources['retained_files']['../outside'] = next(iter(sources['retained_files'].values()))
        path.write_text(json.dumps(sources))
        result = self.run_script('verify.py')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('invalid retained source path', result.stderr)

    def test_existing_output_preserved(self):
        existing = self.folder / 'existing.json'
        existing.write_bytes(b'preserve this exact content')
        result = self.run_script('verify.py', '--output', existing)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('output file already exists', result.stderr)
        self.assertEqual(existing.read_bytes(), b'preserve this exact content')


if __name__ == '__main__':
    unittest.main()
