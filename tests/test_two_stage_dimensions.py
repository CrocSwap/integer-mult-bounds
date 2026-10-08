"""Reject corrupted dimension-specialized mathematical witnesses."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'research/two-stage-dimensions/corners'
spec = importlib.util.spec_from_file_location('dimension_corner_audit', SOURCE / 'independent_param.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
RUNS = [1, 43, 1, 1, 1, 1, 1, 1, 37, 1, 1, 1, 1]


class DimensionCornerFailures(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((SOURCE / 'corner-47-45.json').read_text())

    def test_wrong_last_corner_offset(self):
        self.record['gamma_offset'] -= 1
        with self.assertRaises(AssertionError):
            audit.run(self.record, RUNS)

    def test_unnormalized_projector(self):
        self.record['witness']['left_weights'][0] = '1'
        with self.assertRaises(AssertionError):
            audit.run(self.record, RUNS)

    def test_forged_rational_pivot(self):
        self.record['witness']['pivots'][0][2] = '0'
        with self.assertRaises(AssertionError):
            audit.run(self.record, RUNS)


if __name__ == '__main__':
    unittest.main()
