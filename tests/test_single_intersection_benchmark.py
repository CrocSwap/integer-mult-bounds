"""Ensure the comparison harness fails closed on changed sources or evidence."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location(
    'packing_benchmark', ROOT / 'research/single-intersection-packing/benchmark.py')
benchmark = importlib.util.module_from_spec(spec)
spec.loader.exec_module(benchmark)
import audit_single_intersection as audit


class PackingBenchmark(unittest.TestCase):
    def test_changed_baseline_source_is_rejected(self):
        with patch.object(Path, 'read_bytes', return_value=b'corrupt source'):
            with self.assertRaisesRegex(ValueError, 'Pinned source changed'):
                benchmark.load_baseline()

    def test_complete_certificate_and_mutations(self):
        value = json.loads((ROOT / 'certificates/single-intersection.json').read_text())
        with patch.object(audit, 'certificate', return_value=copy.deepcopy(value)):
            sample = benchmark.sample('packed')
        self.assertEqual(sample['certificate_sha256_with_original_source_binding'],
                         benchmark.CERTIFICATE_SHA256)
        for field in ('rows', 'source_sha256', 'exact_feature_orbit_certificates'):
            corrupt = copy.deepcopy(value)
            if field == 'rows':
                corrupt[field][0]['rank_lower'] += 1
            elif field == 'source_sha256':
                corrupt[field]['docs/research/single-intersection.md'] = '0' * 64
            else:
                corrupt[field][0]['exact_full_binary_rank'] += 1
            with self.subTest(field=field), patch.object(audit, 'certificate', return_value=corrupt):
                with self.assertRaisesRegex(ValueError, 'Full predecessor certificate changed'):
                    benchmark.sample('packed')

    def test_wrong_matrix_entry_is_rejected(self):
        fixture = {'feature_orbits': [{'h': 4, 'k': 2, 'j': 1, 'labels': [3, 5]}]}
        # The correct matrix is [3, 3]; [3, 1] changes one off-diagonal entry.
        with patch.object(Path, 'read_text', return_value=json.dumps(fixture)):
            with patch('experiments.single_intersection.minor_rows', return_value=[3, 1]):
                with self.assertRaisesRegex(ValueError, 'Complete packed Gram matrix differs'):
                    benchmark.compare_rows()


if __name__ == '__main__':
    unittest.main()
