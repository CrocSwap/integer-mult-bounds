"""Behavioral, exact-array and integrity checks; standard library only."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import physical
import verify


class Checks(unittest.TestCase):
    def test_complete_certificate(self):
        result = verify.compute()
        expected = json.loads((verify.PACKAGE / 'RESULT.json').read_text())
        self.assertEqual(verify.canonical(result), verify.canonical(expected))
        self.assertEqual(result['physical_fixture']['fractional_witness_value'],
                         {'address': 0, 'real': '-1/128', 'imag': '1/128'})
        self.assertEqual(result['physical_fixture']['final_max_fractional_bits'], 6)

    def test_chart_unitarity_and_inverse(self):
        word = verify.authenticate()
        representatives = {}
        for e in word['program']:
            if e[0] == 'transport':
                for f in e[2:4]:
                    representatives.setdefault(len(f), tuple(f))
        self.assertEqual(set(representatives), set(range(10)))
        original = tuple(((17*x) % 7 - 3, (11*x) % 5 - 2) for x in range(512)), 0
        square_norm = sum(a*a+b*b for a, b in original[0])
        for frame in representatives.values():
            changed = physical.apply_chart(original, frame)
            values, d = changed
            self.assertEqual(sum(a*a+b*b for a, b in values), square_norm * (1 << (2*d)))
            self.assertEqual(physical.apply_chart(changed, frame, True), original)

    def test_reverse_lifetime_and_signed_cancellation(self):
        # A separate tiny model exercises a private erase and a reused name.
        p = [['zero', 'C', []], ['add', 'C', 'a', '1/4', []],
             ['add', 'b', 'C', '-2', []], ['add', 'C', 'a', '-1/4', []],
             ['erase', 'C', []], ['zero', 'C', []], ['erase', 'C', []],
             ['sign', 'b', '-1', []]]
        self.assertEqual(verify.reverse_row(p, len(p), 'b', {'a', 'b'}),
                         {'a': verify.Q(1, 2), 'b': verify.Q(-1)})
        self.assertEqual(verify.v2(verify.Q(12, 4)), 0)
        self.assertEqual(verify.v2(verify.Q(-8, 2)), 2)

    def test_relocated_export_and_real_corruptions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / 'research' / verify.PACKAGE.name
            shutil.copytree(verify.PACKAGE, package, ignore=shutil.ignore_patterns('__pycache__'))
            source = 'research/p104-native-channel/vendor/native_verify.py'
            (root / source).parent.mkdir(parents=True)
            shutil.copyfile(verify.ROOT / source, root / source)

            def run():
                return subprocess.run([sys.executable, '-I', '-O', '-B', str(package / 'verify.py')],
                                      cwd=root, text=True, capture_output=True, timeout=120)

            self.assertEqual(run().returncode, 0, 'Git-free optimized replay')
            for path, expected_message in [(package / 'WORD.json', 'dependency SHA256'),
                                           (root / source, 'chart-definition SHA256')]:
                raw = path.read_bytes()
                path.write_bytes(raw + b'\n')
                rejected = run()
                self.assertNotEqual(rejected.returncode, 0)
                self.assertIn(expected_message, rejected.stderr)
                path.write_bytes(raw)
            receipt = package / 'RESULT.json'
            raw = receipt.read_bytes()
            result = json.loads(raw)
            result['replay']['grid_forms']['0'] = True  # Python True == 1.
            receipt.write_text(json.dumps(result))
            rejected = run()
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn('typed receipt mismatch', rejected.stderr)
            receipt.write_bytes(raw)
            output = root / 'occupied.json'
            output.write_text('preserve me')
            rejected = subprocess.run([sys.executable, '-I', '-B', str(package / 'verify.py'),
                                       '--out', str(output)], capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual(output.read_text(), 'preserve me')


if __name__ == '__main__':
    unittest.main()
