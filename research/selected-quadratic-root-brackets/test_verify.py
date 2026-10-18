"""Positive replay and explicit rejection controls for the screening certificate."""
import subprocess
import sys
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent

class ScreeningTests(unittest.TestCase):
    def test_three_fully_charged_screening_brackets(self):
        result = subprocess.run([sys.executable, '-I', '-O', '-B', str(HERE / 'verify.py')],
            capture_output=True, text=True, encoding='utf-8', timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS_SELECTED_QUADRATIC_ROOT_BRACKETS ledgers=3', result.stdout)

    def test_false_root_missing_surcharge_and_changed_source_receipts_reject(self):
        original = json.loads((HERE / 'RESULT.json').read_text(encoding='utf-8'))
        mutations = [
            lambda d: d['ledgers'][0].update(root_lower='1/100'),
            lambda d: d['ledgers'][2].update(surcharge_coefficient='0'),
            lambda d: d['sources'].update({'research/community-frontier1094-audit/ASSEMBLY.json': '0'*64}),
        ]
        with tempfile.TemporaryDirectory(prefix='.controls-', dir=HERE) as temp:
            for index, mutate in enumerate(mutations):
                with self.subTest(index=index):
                    data = json.loads(json.dumps(original))
                    mutate(data)
                    path = Path(temp) / f'bad-{index}.json'
                    path.write_text(json.dumps(data), encoding='utf-8')
                    result = subprocess.run([sys.executable, '-I', '-O', '-B', str(HERE/'verify.py'), '--result', str(path)],
                        capture_output=True, text=True, encoding='utf-8', timeout=120)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('result receipt mismatch', result.stdout + result.stderr)
                    self.assertNotIn('PASS_SELECTED_QUADRATIC_ROOT_BRACKETS', result.stdout)

if __name__ == '__main__':
    unittest.main()
