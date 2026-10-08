"""Boundary controls for batching and the corrected Gaussian input budget."""
from dataclasses import replace
from fractions import Fraction as Q
from math import isqrt
from pathlib import Path
import re
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from batched_network import assembly, complex_certificate, parameters
from controlled_bit_rank_moment import certificate as bit_certificate
from make_batched_patch import patched_files


class BatchedNetworkTests(unittest.TestCase):
    def test_exponent_boundaries(self):
        self.assertLess(bit_certificate()['moment_upper'], 1)
        self.assertLess(complex_certificate()['moment_upper'], 1)
        with self.assertRaises(AssertionError):
            bit_certificate(a=Q(246, 10**8))
        with self.assertRaises(ValueError):
            complex_certificate(a=Q(7, 10**6))
        result = assembly()
        self.assertGreater(result['parameters']['kappa'], Q(1, 2**23))
        self.assertGreater(result['absorption_gap'], 0)
        with self.assertRaises(ValueError):
            assembly(replace(parameters(), kappa=result['minimum_margin']))

    def test_shifted_chirp_budget_and_old_enclosure_failure(self):
        # pi < 355/113 and log(2) > 693/1000 give a rational witness
        # that the old exact-magnitude enclosure cannot absorb shift error.
        alpha = 100
        B = 11400
        log2_ratio_lower = B - Q(355, 113)*alpha**2/(4*Q(693, 1000))
        self.assertGreater(log2_ratio_lower, 60)
        # Check both near-cutoff and larger legal integer inputs, including
        # ceil(sqrt(p)/(2 alpha)) and power-of-two length boundaries.
        for p in list(range(101, 401)) + [1024, 10000, 20000]:
            for alpha in range(2, isqrt(p-1)+1):
                B = (114*alpha**2+99)//100
                width = isqrt(p-1)//(2*alpha)+1
                length = 3*width+1
                ceil_log = (length-1).bit_length()
                self.assertLessEqual(length, p)
                self.assertLess(p+29*p+B+ceil_log+11, 34*p)

    def test_active_manuscript_interfaces_and_correction(self):
        root = Path(__file__).resolve().parents[1]
        sources = {str(p.relative_to(root/'upstream')): p.read_text()
                   for p in (root/'upstream').rglob('*.tex')}
        sources.update({name:new for name, old, new in patched_files()})
        text = '\n'.join(sources.values())
        labels = re.findall(r'\\label\{([^}]+)\}', text)
        self.assertEqual(len(labels), len(set(labels)))
        self.assertFalse(set(re.findall(r'\\(?:ref|eqref)\{([^}]+)\}', text))-set(labels))
        for section in ['06-transforms.tex', '08-assembly.tex']:
            self.assertIn('prop:batched-simultaneous-layer', sources['build/sections/'+section])
        gaussian = sources['build/sections/07-resampling.tex']
        self.assertIn(r'$F=2^{\lceil1.14\alpha^2\rceil}', gaussian)
        self.assertIn(r'\le 32.14p+11<34p', gaussian)
        self.assertNotIn(r'Then $F=e^{\pi\alpha^2/4}', gaussian)


if __name__ == '__main__':
    unittest.main()
