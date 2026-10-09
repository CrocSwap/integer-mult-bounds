"""Independent base-two rational enclosures of the new complex moment.

These check the recurrence arithmetic, not the all-size realization. The
production certificate uses a different base-four-thirds interval engine.
"""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / 'research/coordinated-frames-and-entrance-banks'
sys.dont_write_bytecode = True  # The predecessor inventory forbids extra files.
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)


def read(path):
    return json.loads(path.read_text())


class FrameClosureMomentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = PARENT / 'bit/base_two_moment.py'
        spec = importlib.util.spec_from_file_location('frame_closure_base_two', path)
        cls.engine = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.engine)
        cls.certificate = read(ROOT / 'research/frame-closure-refinement/certificate.json')

    def enclose(self, profile, saving):
        self.assertEqual(sum(int(r)*n for r, n in profile['child_histogram'].items()),
                         profile['rank_per_vertex'])
        self.assertEqual(profile['m']*profile['W_per_vertex']-profile['rank_per_vertex'],
                         profile['deficit_per_vertex'])
        return self.engine.moment(profile['m'], profile['W_per_vertex'],
                                  profile['child_histogram'].items(), saving)

    def test_adjacent_complex_savings_with_independent_enclosures(self):
        profile = self.certificate['profile']
        saving = Q(self.certificate['complex_saving'])
        lo, hi = self.enclose(profile, saving)
        self.assertLessEqual(lo, hi)
        self.assertLess(hi, 1)
        next_lo, next_hi = self.enclose(profile, saving + Q(1, 10**18))
        self.assertLessEqual(next_lo, next_hi)
        self.assertGreater(next_lo, 1)

    def test_original_frames_cannot_certify_the_new_saving(self):
        profile = read(PARENT / 'certificate.json')['complex']['profile']
        lo, _ = self.enclose(profile, Q(self.certificate['complex_saving']))
        self.assertGreater(lo, 1)


if __name__ == '__main__':
    unittest.main()
