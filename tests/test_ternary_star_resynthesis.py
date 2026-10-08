"""Independent full-output and rejection controls for four-point-star rewrites."""
from itertools import combinations
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts/experiments'))
from ternary_star_resynthesis import check_template, resynthesize
from ternary_target_certify import build_checkers, exact_run
from ternary_target_circuit import gram


def read_dag(path):
    data = Path(path).read_bytes()
    h, v, n, q = struct.unpack_from('<4I', data)
    parents = list(struct.iter_unpack('<2I', data[16:16+8*n]))
    offset = 16+8*n
    roots = struct.unpack_from(f'<{q}I', data, offset)
    offset += 4*q
    active = data[offset:offset+n]
    cores = struct.unpack_from(f'<{n}I', data, offset+n)
    if len(data) != offset+5*n:
        raise AssertionError('Unexpected DAG length')
    supports = [0]+[1 << i for i in range(v)]
    for node in range(v+1, n):
        a, b = parents[node]
        if not 0 < a < node or not 0 < b < node:
            raise AssertionError('Non-topological rewritten gate')
        if supports[a] & supports[b]:
            raise AssertionError('Rewritten gate has overlapping input supports')
        supports.append(supports[a] | supports[b])
    return dict(h=h, v=v, n=n, roots=roots, parents=parents, active=active,
                cores=cores, supports=supports)


class StarResynthesis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='ternary-star-tests-')
        cls.workdir = Path(cls.temporary.name)
        cls.checkers = build_checkers(cls.workdir)
        cls.original = exact_run(10, cls.workdir, cls.checkers)
        cls.dag = cls.workdir/'dag-10.bin'
        cls.binary = cls.workdir/'star-demands'
        subprocess.run(['c++', '-std=c++17', '-O2',
                        str(ROOT/'scripts/experiments/ternary_star_demands.cpp'),
                        '-o', str(cls.binary)], check=True, capture_output=True)
        cls.demands = cls.workdir/'demands.txt'
        cls.extract = json.loads(subprocess.check_output(
            [str(cls.binary), str(cls.dag), str(cls.demands)], text=True))
        cls.templates = cls.workdir/'templates.bin'
        cls.result = resynthesize(cls.demands, 10, cls.templates)
        cls.rewritten = cls.workdir/'rewritten.bin'
        cls.rewrite = json.loads(subprocess.check_output(
            [str(cls.binary), str(cls.dag), str(cls.workdir/'demands-again.txt'),
             str(cls.templates), str(cls.rewritten)], text=True))

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_real_saving_preserves_every_side_and_center_coefficient(self):
        before, after = read_dag(self.dag), read_dag(self.rewritten)
        self.assertEqual(self.result['saved_additions'], 10)
        self.assertEqual(self.rewrite['rewritten_additions'], 7335)
        self.assertEqual(self.extract['additions']-self.rewrite['rewritten_additions'],
                         self.result['saved_additions'])
        inputs = list(combinations(range(10), 5))
        targets = inputs+list(combinations(range(10), 2))
        self.assertEqual(len(targets), len(after['roots']))
        for target, old, new in zip(targets, before['roots'], after['roots']):
            expected = sum(1 << i for i, source in enumerate(inputs)
                           if len(set(source) & set(target)) == 2)
            self.assertEqual(before['supports'][old], expected)
            self.assertEqual(after['supports'][new], expected)
        self.assertTrue(all(after['active'][1:after['v']+1]))

    def test_rewritten_full_frame_audit_remains_valid(self):
        frames = json.loads(subprocess.check_output(
            [str(self.checkers['dual']), str(self.rewritten),
             str(self.workdir/'rewritten-unresolved')], text=True,
            stderr=subprocess.DEVNULL))
        self.assertTrue(frames['every_final_frame_nondegenerate'])
        self.assertTrue(frames['source_region_ancestor_closed'])
        self.assertTrue(frames['all_centers_in_source_region'])
        self.assertEqual(frames['unresolved_source_nodes'], 0)

    def test_four_point_star_full_span_has_positive_gram_matrix(self):
        # Each full-star generator has Gram diagonal 3 and off-diagonal 2:
        # I+2J is positive definite, so every new source subspace is too.
        for h in (8, 10, 28):
            rows = tuple(tuple(int(j < 4 or j == fifth) for j in range(h))
                         for fifth in range(4, h))
            actual = gram(rows)
            self.assertEqual(actual, tuple(tuple(2+int(i == j) for j in range(h-4))
                                           for i in range(h-4)))

    def reject_templates(self, words, expected):
        path = self.workdir/'corrupted-templates.bin'
        path.write_bytes(struct.pack(f'<{len(words)}I', *words))
        result = subprocess.run(
            [str(self.binary), str(self.dag), str(self.workdir/'reject-demands.txt'),
             str(path), str(self.workdir/'should-not-exist.bin')],
            capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(expected, result.stderr)

    def template_words(self):
        data = self.templates.read_bytes()
        return list(struct.unpack(f'<{len(data)//4}I', data))

    def test_wrong_boundary_is_rejected(self):
        words = self.template_words()
        self.assertGreater(words[1], 0)
        words[5] ^= 1
        self.reject_templates(words, 'Replacement boundary or saving mismatch')

    def test_overlapping_replacement_gate_is_rejected(self):
        words = self.template_words()
        first_gate = 5+words[3]
        words[first_gate+1] = words[first_gate]
        self.reject_templates(words, 'Invalid disjoint replacement')

    def test_unavailable_gate_input_is_rejected(self):
        words = self.template_words()
        first_gate = 5+words[3]
        words[first_gate] = 1 << 30
        self.reject_templates(words, 'Invalid disjoint replacement')

    def test_python_template_checker_rejects_missing_boundary_and_overlap(self):
        with self.assertRaisesRegex(ValueError, 'Missing replacement boundary'):
            check_template([3], [])
        with self.assertRaisesRegex(ValueError, 'Invalid disjoint replacement gate'):
            check_template([3], [(1, 1)])


if __name__ == '__main__':
    unittest.main()
