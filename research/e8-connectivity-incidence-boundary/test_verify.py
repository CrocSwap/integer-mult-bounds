"""Reject invalid geometry, disconnected signs and altered result receipts."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


class CertificateTests(unittest.TestCase):
    def run_check(self, *args):
        return subprocess.run(
            [sys.executable, '-I', '-O', '-B', str(HERE / 'verify.py'), *args],
            text=True, encoding='utf-8', capture_output=True, timeout=120)

    def test_explicit_connected_rank_deficit_is_verified(self):
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS_E8_CONNECTIVITY_INCIDENCE_BOUNDARY', result.stdout)

    def test_invalid_geometry_disconnected_signs_and_false_rank_are_rejected(self):
        original = json.loads((HERE / 'CERTIFICATE.json').read_text(encoding='utf-8'))
        cases = [
            ('deleted-pivot', lambda d: d['deleted_lines'].__setitem__(0, 2), 'deleted pivot'),
            ('unknown-negative', lambda d: d['negative_lines'].append(119), 'unknown/duplicate negative line'),
            ('disconnected', lambda d: d.update(negative_lines=[]), 'disconnected graph'),
            ('false-rank', lambda d: d['result']['ranks'][0].update(selected_rank=44), 'certificate result mismatch'),
            ('missing-vertex', lambda d: d['result']['graphs'].pop(), 'certificate result mismatch'),
        ]
        with tempfile.TemporaryDirectory(prefix='.controls-', dir=HERE) as temp:
            for name, mutate, diagnostic in cases:
                with self.subTest(name=name):
                    data = json.loads(json.dumps(original))
                    mutate(data)
                    path = Path(temp) / (name + '.json')
                    path.write_text(json.dumps(data), encoding='utf-8')
                    result = self.run_check('--certificate', str(path))
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertNotIn('PASS_E8_CONNECTIVITY_INCIDENCE_BOUNDARY', result.stdout)
                    self.assertIn(diagnostic, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
