#!/usr/bin/env python3
"""Semantic and artifact controls for the fourth-moment certificate.

Prepared for commdata2338, with substantial OpenAI Codex assistance.
Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction as Q
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
    spec = importlib.util.spec_from_file_location('qq16_test_'+name, HERE/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


v, oracle = load('verify'), load('oracle')
src = v.src


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = src.load_packet(ROOT)
        cls.R, cls.routes = src.packet_data(cls.packet)
        cls.receipt = json.loads((HERE/'RESULT.json').read_text())

    def test_gram_and_chart_mutants(self):
        bad = deepcopy(self.R)
        bad[0][src.U[0]] += 1
        with self.assertRaisesRegex(ValueError, 'query Gram'):
            src.check_grams(bad)
        routes = deepcopy(self.routes)
        for stage in (1, 2):
            routes[stage][src.U[1]] = routes[stage][src.U[0]]
        with self.assertRaisesRegex(ValueError, 'distinct ordinary charts'):
            src.check_swap_charts(routes)

    def test_product_hypotheses(self):
        with self.assertRaises(ValueError):
            v.pair_census([self.routes[0], self.routes[1], self.routes[1]])
        # Distinct involutions alone do not imply singleton product fibres.
        ident = src.IDENTITY
        a, b = list(ident), list(ident)
        a[1] ^= 1
        b[3] ^= 4
        a, b = tuple(a), tuple(b)
        four = [ident, a, b, src.compose(a, b)]
        with self.assertRaisesRegex(ValueError, 'nonidentity pair collision'):
            v.pair_census([[ident]*4, four, four], ports=tuple(range(4)))

    def test_source_semantic_binding(self):
        wrong = deepcopy(self.packet)
        wrong['A_ports'][0] = wrong['U_ports'][0]
        with self.assertRaisesRegex(ValueError, 'selected partition'):
            src.packet_data(wrong)
        wrong = deepcopy(self.packet)
        event = wrong['programs']['F_1'][1]
        wrong['map_registry'][event[2]]['owner_right_matrix_columns'][72] ^= 1
        with self.assertRaisesRegex(ValueError, 'spectator axes'):
            src.packet_data(wrong)
        wrong = deepcopy(self.packet)
        word = wrong['programs']['B_1_2']
        cut = next(i for i,e in enumerate(word) if e[:2] == ['cover_sweep','future_E_t'])
        # Keep event shape and port, change its chart to the other stage.
        word[cut-112][2] = wrong['programs']['F_1'][1][2]
        with self.assertRaisesRegex(ValueError, 'forward/backward route binding'):
            src.packet_data(wrong)

    def test_noncommuting_multiplication_orientations(self):
        a, b = self.routes[1][src.U[0]], self.routes[2][src.U[1]]
        self.assertNotEqual(src.compose(a, b), src.compose(b, a))
        self.assertEqual(oracle.rows(src.compose(a, b)),
                         oracle.row_product(oracle.rows(a), oracle.rows(b)))
        self.assertEqual(src.compose(a, a), src.IDENTITY)
        # A third direct basis-action implementation checks the operator order.
        for axis in range(25):
            x = b[axis]
            expected = 0
            for k in range(25):
                if (x >> k) & 1:
                    expected ^= a[k]
            self.assertEqual(src.compose(a, b)[axis], expected)

    def test_polynomial_and_capacity(self):
        data = self.receipt['spectral_bound']
        p, q = [Q(x) for x in data['rank_polynomial']], [Q(x) for x in data['residual_polynomial']]
        v.check_polynomial(p, q)
        for index in (0, 2, 4):
            bad = p.copy()
            bad[index] += Q(1, 100)
            with self.assertRaisesRegex(ValueError, 'polynomial square identity'):
                v.check_polynomial(bad, q)
        # The exact polynomial controls a small diagonal positive operator,
        # including zero eigenvalues; counting ambient dimension is insufficient.
        values = [Q(0), Q(0), Q(1, 2), Q(1), Q(3)]
        evaluation = sum(sum(c*t**k for k,c in enumerate(p)) for t in values)
        self.assertLessEqual(evaluation, 3)
        moments = [Q(x) for x in self.receipt['moments_per_owner']]
        self.assertEqual(sum(c*m for c,m in zip(p[1:], moments)), Q(117, 5))
        self.assertEqual(Q(data['selected_defect_lower_per_owner'])-15, Q(2, 5))
        self.assertGreaterEqual(16, Q(data['selected_defect_lower_per_owner']))
        altered = moments.copy()
        altered[-1] -= Q(1, 36)
        with self.assertRaisesRegex(ValueError, 'quartic rank bound'):
            v.spectral_bound(altered)

    def test_direct_oracle_reordered_accumulation(self):
        moments, blocks = oracle.calculate(self.R, self.routes, stage_order=(2, 1, 0))
        self.assertEqual(moments, [Q(24), Q(28), Q(109, 3), Q(1823, 36)])
        self.assertEqual(blocks, {f'{s}{t}': str(Q(1187, 108) if s == t else Q(53, 18))
                                 for s in range(3) for t in range(3)})

    def test_receipt_type_and_duplicate_rejection(self):
        with tempfile.TemporaryDirectory(prefix='qq16-fourth-') as directory:
            path = Path(directory)/'receipt.json'
            wrong = deepcopy(self.receipt)
            wrong['cross_stage_intersections']['0'] = True
            path.write_text(json.dumps(wrong))
            # Python's ordinary equality would accept this proof-field type change.
            self.assertEqual(wrong, self.receipt)
            self.assertNotEqual(v.canonical(v.read_receipt(path)), v.canonical(self.receipt))
            proc = subprocess.run([sys.executable, '-I', '-B', str(HERE/'verify.py'),
                                   '--receipt', str(path)], capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn('receipt mismatch', proc.stderr)
            path.write_text('{"x":1,"x":2}')
            with self.assertRaisesRegex(ValueError, 'duplicate receipt key'):
                v.read_receipt(path)

    def test_source_and_numeric_receipt_corruption(self):
        with tempfile.TemporaryDirectory(prefix='qq16-fourth-') as directory:
            root = Path(directory)
            for name in src.PINS:
                target = root/name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/name, target)
            src.load_packet(root)
            packet = root/src.PACKET
            content = bytearray(packet.read_bytes())
            content[-1] ^= 1
            packet.write_bytes(content)
            proc = subprocess.run([sys.executable, '-I', '-B', str(HERE/'verify.py'),
                                   '--repo', str(root)], capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn('source pin', proc.stderr)
            wrong = deepcopy(self.receipt)
            wrong['moments_per_owner'][-1] = '1822/36'
            path = root/'receipt.json'
            path.write_text(json.dumps(wrong))
            proc = subprocess.run([sys.executable, '-I', '-B', str(HERE/'verify.py'),
                                   '--receipt', str(path)], capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn('receipt mismatch', proc.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
