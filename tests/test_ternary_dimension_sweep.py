"""Dimension-specific logarithms, matching, and isolated 32-column controls."""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts/experiments'))
from ternary_dimension_sweep import log_upper, moment, rank, matching, build_sweep_binaries


class DimensionSweep(unittest.TestCase):
    def test_explicit_matching_covers_even_dimensions_missing_euler_route(self):
        for h in (8, 10, 26, 28, 30, 32):
            result = matching(h)
            self.assertEqual(result['distinct_images'], comb(h, 5))
            self.assertTrue(result['every_intersection_two'])

    def test_generic_logarithms_and_mass_identity_change_with_dimension(self):
        for h, roles in ((26, 5_000_000), (28, 8_791_733), (30, 14_000_000)):
            result = moment(h, roles, Q(1, 10**7))
            counts = result['counts']
            self.assertEqual(sum(result['rank_mass_weights']), 1-counts['eta'])
            self.assertEqual(result['normalized_widths'][-1], Q(1, h))
            self.assertEqual(result['logarithm_upper_bounds'][-1], log_upper(h))
            self.assertEqual(sum(row['copies']*row['chunk_digits']
                                 for row in counts['recursive_blocks'])+counts['singleton_calls'],
                             counts['original_rank_sum'])
        self.assertEqual(log_upper(1), 0)
        self.assertGreater(log_upper(30), log_upper(28))
        with self.assertRaises(ValueError):
            log_upper(Q(1, 2))

    def test_retained_dimension_reproduces_or_improves_conservative_exponent(self):
        result = rank(28, 8_791_733)
        a = result['bit']['bit_saving']
        self.assertGreaterEqual(a, Q(329033, 10**12))
        self.assertGreater(result['bit']['strict_gap'], 0)
        self.assertLessEqual(moment(28, 8_791_733, result['first_rejected_bit_saving'])['strict_gap'], 0)
        self.assertGreaterEqual(result['assembly']['kappa'], Q(164516, 10**12))
        self.assertGreater(result['assembly']['absorption_gap'], 0)

    def test_isolated_span_has_full_rank_through_bit31(self):
        with tempfile.TemporaryDirectory(prefix='ternary-dimension-span-') as folder:
            folder = Path(folder)
            build_sweep_binaries(folder)
            source = folder/'span-control.cpp'
            source.write_text('''
#define main old_main
#include "ternary_target_span_classes.cpp"
#undef main
int main() {
  Span span(32, 28);
  // A fixed four-point star has 28 independent generators and includes bit31.
  for (U j=4; j<32; j++) span.add(15U | (U(1)<<j));
  if(span.rows.size()!=28 || span.key().size()!=28*32) return 1;
  if(span.rows.back()[31]==0) return 2;
}
''')
            binary = folder/'span-control'
            subprocess.run(['c++', '-std=c++17', '-O1',
                            str(source), '-o', str(binary)], check=True, capture_output=True)
            subprocess.run([str(binary)], check=True, capture_output=True, timeout=30)


if __name__ == '__main__':
    unittest.main()
