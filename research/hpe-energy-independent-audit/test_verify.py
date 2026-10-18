"""Independent small dense oracle and failure-boundary controls. Apache-2.0."""
import copy
from fractions import Fraction as Q
import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('energy_audit', HERE/'verify.py')
v = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)
ZERO, ONE, I = (Q(0), Q(0)), (Q(1), Q(0)), (Q(0), Q(1))


def add(a, b):
    return a[0]+b[0], a[1]+b[1]


def mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def identity(n=4):
    return [[ONE if j == k else ZERO for k in range(n)] for j in range(n)]


def product(a, b):
    n = len(a)
    result = [[ZERO]*n for _ in range(n)]
    for j in range(n):
        for k in range(n):
            for l in range(n):
                result[j][k] = add(result[j][k], mul(a[j][l], b[l][k]))
    return result


def permutation(mapping):
    return [[ONE if row == mapping[column] else ZERO for column in range(4)]
            for row in range(4)]


def diagonal(entries):
    return [[entries[j] if j == k else ZERO for k in range(4)] for j in range(4)]


def c_gate(mapping, sign):
    a, b = (Q(1, 2), Q(sign, 2)), (Q(1, 2), Q(-sign, 2))
    return [[add(a if j == k else ZERO, b if j == mapping[k] else ZERO)
             for k in range(4)] for j in range(4)]


def alphabet():
    # Matrices are hard-coded from mathematical action on four addresses;
    # no production phase, parity, parser or realification helper is used.
    return [
        (['cg', 1, True], c_gate([1, 0, 3, 2], 1)),
        (['cg', 1, False], c_gate([1, 0, 3, 2], -1)),
        (['cg', 2, False], c_gate([2, 3, 0, 1], -1)),
        (['cg', 0, True], identity()),
        (['ph', 1], diagonal([I]*4)),
        (['dg', [2, 0], [1, 2]], diagonal([ONE, I, (-Q(1), Q(0)), I])),
        (['pm', [2, 3], [3, 1]], permutation([0, 2, 3, 1])),
        (['xg', 1], permutation([1, 0, 3, 2])),
    ]


def dense_of_result(result):
    rows, count = result
    return [[(Q(a, 1 << count), Q(b, 1 << count)) for a, b in row]
            for row in v.gaussian_rows(rows, 0)]


class AuditTests(unittest.TestCase):
    def test_complete_short_word_oracle(self):
        letters = alphabet()
        cases = 0
        for length in range(4):
            for word in itertools.product(letters, repeat=length):
                expected = identity()
                for _, gate_matrix in word:
                    expected = product(gate_matrix, expected)
                actual = v.matrix([gate for gate, _ in word], n=2)
                self.assertEqual(dense_of_result(actual), expected)
                v.row_record(actual, actual[1])
                cases += 1
        self.assertEqual(cases, 585)

    def test_semantic_controls_and_detector_sensitivity(self):
        unit = v.matrix([], n=2)
        wrong_phase = v.matrix([['ph', 1]], n=2)
        wrong_character = v.matrix([['dg', [0, 0], [2, 0]]], n=2)
        equivalent = v.matrix([['cg', 1, True], ['cg', 1, False]], n=2)
        self.assertTrue(v.normalized_equal(unit, equivalent))
        self.assertTrue(v.normalized_equal(equivalent, unit))
        for bad in (wrong_phase, wrong_character, (equivalent[0], 0)):
            v.must_reject(lambda: v.require(v.normalized_equal(unit, bad), 'operator mismatch'),
                          'operator mismatch')
            # If the detector is removed, the rejection harness must fail.
            with patch.object(v, 'normalized_equal', return_value=True):
                with self.assertRaisesRegex(ValueError, 'unexpected acceptance'):
                    v.must_reject(lambda: v.require(v.normalized_equal(unit, bad), 'operator mismatch'),
                                  'operator mismatch')
        forward = v.matrix([['pm', [2, 3], [3, 1]]], n=2)
        backward = v.matrix([['pm', [3, 1], [2, 3]]], n=2)
        self.assertFalse(v.normalized_equal(forward, backward))
        c, d = ['cg', 1, True], ['dg', [0, 0], [1, 0]]
        self.assertFalse(v.normalized_equal(v.matrix([c, d], n=2), v.matrix([d, c], n=2)))
        self.assertTrue(v.normalized_equal(v.matrix([d], n=2),
                        v.matrix([['dg', [0, 0], [5, 4]]], n=2)))
        for sign in (True, False):
            self.assertTrue(v.normalized_equal(unit, v.matrix([['cg', 0, sign]], n=2)))

    def test_guard_energy_and_realification_obligations(self):
        malformed = [([['pm', [0, 0], [0, 0]]], 'permutation inverse'),
                     ([['xg', 4]], 'XOR domain'),
                     ([['cg', 1, 1]], 'Boolean C sign')]
        for gates, message in malformed:
            v.must_reject(lambda: v.validate(gates, 2), message)
            with patch.object(v, 'validate', return_value=None):
                with self.assertRaisesRegex(ValueError, 'unexpected acceptance'):
                    v.must_reject(lambda: v.validate(gates, 2), message)
        # This actual invalid literal program has energy 8 at row zero,
        # despite k=1 predicting 4. It isolates the unitarity premise.
        invalid = [['pm', [0], [0]], ['dg', [0], [1]], ['cg', 1, True]]
        with patch.object(v, 'validate', return_value=None):
            result = v.matrix(invalid, n=1)
        row = next(v.gaussian_rows(result[0], 0))
        self.assertEqual(row, [[2, 2], [0, 0]])
        v.must_reject(lambda: v.row_record(result, 1), 'scaled row energy')
        with patch.object(v, 'row_record', return_value={}):
            with self.assertRaisesRegex(ValueError, 'unexpected acceptance'):
                v.must_reject(lambda: v.row_record(result, 1), 'scaled row energy')
        damaged = copy.deepcopy(v.matrix([], n=1))
        damaged[0][1][0] = 1
        v.must_reject(lambda: list(v.gaussian_rows(damaged[0], 0)), 'realification')

    def test_parser_closed_inventory(self):
        source = (v.ROOT/v.EXACT).read_text(encoding='utf-8')
        circuits = v.literals(source)
        self.assertEqual(len(circuits), 6)
        # Explicit tokens, gate order and both directions of a non-self-inverse map.
        self.assertEqual(circuits['lhsLit1'][2], ['cg', 1, False])
        for change in [source.replace('.cg 1 false', '.cg 1 0'),
                       source.replace('def lhsLit1 :', 'def missingLit1 :'),
                       source.replace('.ph 1,', '.ph (1+0),'),
                       source + '\ndef lhsLit1 : List Gate :=\n [.ph 0]\n\n']:
            with self.assertRaises(ValueError):
                v.literals(change)
        # Layout changes inside a pinned closed literal grammar are harmless.
        self.assertEqual(v.literals(source.replace('   .cg', '     .cg')), circuits)

    def test_energy_boundary_witnesses(self):
        # Independent exact arithmetic corroboration, not proof by sampling.
        for radius in (1, 2, 3, 16, 512):
            for base in (1, 2*radius-1):
                upper, lower = (base+1)//2, base//2
                self.assertEqual(upper, -lower+base)
                self.assertLessEqual(upper*upper, radius*radius)
                self.assertLessEqual(lower*lower+1, radius*radius)
            base = 2*radius
            self.assertGreater(base*base+1, 4*radius*radius)
        # Column energies <=1 do not provide the row premise.
        a, b = [[1, 0], [0, 0]], [[-1, 1], [0, 0]]
        self.assertEqual([r[0]+2*r[1] for r in a], [r[0]+2*r[1] for r in b])
        self.assertTrue(all(sum(r[j]**2 for r in m) <= 1 for m in (a, b) for j in (0, 1)))
        self.assertEqual(sum(x*x for x in b[0]), 2)

    def test_predecessor_scientific_receipt_controls(self):
        expected = v.read_json(HERE/'PR1906-RESULT.json')['source']['pairs'][0]
        record = {'scaled_row_sha256': expected['scaled_row_sha256'],
                  'row_squared_energy': 4**9}
        v.bind_record([record, record], 9, 7, 9, expected)
        for field, value, message in (
                ('scaled_row_sha256', '0'*64, 'row digest'),
                ('row_squared_energy', 4**8, 'energy'),
                ('C_left', 8, 'C counts'), ('C_right', 6, 'C counts'),
                ('radix_bits', 9, 'radix binding'), ('radius', 256, 'radix binding'),
                ('largest_input_bits', 5110, 'packed input length')):
            bad = dict(expected, **{field: value})
            # Bypass checksum guards to test the mathematical receipt binding.
            v.must_reject(lambda: v.bind_record([record, record], 9, 7, 9, bad), message)
            with patch.object(v, 'bind_record', return_value=None):
                with self.assertRaisesRegex(ValueError, 'unexpected acceptance'):
                    v.must_reject(lambda: v.bind_record([record, record], 9, 7, 9, bad), message)

    def test_export_source_receipt_and_read_only_replay(self):
        with tempfile.TemporaryDirectory(prefix='hpe-energy-audit-') as directory:
            root = Path(directory)
            package = root/'research'/HERE.name
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            for name in (v.EXACT, v.CLIFFORD):
                target = root/name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(v.ROOT/name, target)

            def invoke(*args):
                return subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'verify.py'), *args],
                                      cwd=root, text=True, capture_output=True, timeout=120)

            receipt = package/'RESULT.json'
            original = receipt.read_bytes()
            receipt.unlink()
            result = invoke()
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(receipt.exists())
            receipt.write_bytes(original)
            data = json.loads(original)
            data['pairs'][0]['radix_bits'] += 1
            receipt.write_text(json.dumps(data), encoding='utf-8')
            result = invoke()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('audit receipt mismatch', result.stderr)
            receipt.write_bytes(original)
            source = root/v.EXACT
            source.write_bytes(source.read_bytes()+b'\n')
            result = invoke()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('source drift', result.stderr)
            shutil.copy2(v.ROOT/v.EXACT, source)
            predecessor = package/'PR1906-RESULT.json'
            pred_bytes = predecessor.read_bytes()
            predecessor.write_bytes(pred_bytes+b'\n')
            result = invoke()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('predecessor receipt drift', result.stderr)
            predecessor.write_bytes(pred_bytes)
            receipt.write_text('{"x":1,"x":2}', encoding='utf-8')
            result = invoke()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('duplicate JSON key', result.stderr)
            receipt.write_bytes(original)
            generated = root/'regenerated.json'
            result = invoke('--write', str(generated))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(generated.read_bytes(), original)
            files = [p for p in root.rglob('*') if p.is_file()]
            directories = [p for p in root.rglob('*') if p.is_dir()]
            before = {str(p.relative_to(root)): p.read_bytes() for p in files}
            try:
                for path in files:
                    path.chmod(0o444)
                for path in reversed(directories):
                    path.chmod(0o555)
                root.chmod(0o555)
                result = invoke()
                self.assertEqual(result.returncode, 0, result.stderr)
                after = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
                self.assertEqual(before, after)
            finally:
                root.chmod(0o755)
                for path in directories:
                    path.chmod(0o755)
                for path in files:
                    path.chmod(0o644)


if __name__ == '__main__':
    unittest.main()
