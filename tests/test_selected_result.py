"""Reject publication metadata that is detached from its reviewed certificate."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('selected_result_check', ROOT / 'scripts/verify_selected_result.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class SelectedResult(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((ROOT / 'certificates/selected-result.json').read_text())

    def test_current_selection(self):
        checker.check(self.record)

    def test_reject_detached_claim_or_proof(self):
        mutations = [
            ('kappa', '1/1000'), ('decimal', '0.001'),
            ('certificate_sha256', '0' * 64), ('proof_supplements', {}),
        ]
        for key, value in mutations:
            with self.subTest(field=key):
                record = deepcopy(self.record)
                record[key] = value
                with self.assertRaises(ValueError):
                    checker.check(record)

    def test_reject_changed_supplement(self):
        record = deepcopy(self.record)
        name = next(iter(record['proof_supplements']))
        record['proof_supplements'][name] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'proof supplement changed'):
            checker.check(record)

    def test_optimized_interpreter_fails_closed(self):
        result = subprocess.run([sys.executable, '-O', str(ROOT / 'scripts/verify_selected_result.py')],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Assertions must remain enabled', result.stderr)


if __name__ == '__main__':
    unittest.main()
