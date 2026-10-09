"""Corruption and fail-closed controls for the composed finite certificate."""
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research/bit-reuse-147'))
import price147

class RecycledBitControls(unittest.TestCase):
    def test_uncharged_child_is_rejected(self):
        row = json.loads((ROOT / 'research/recycled-bit-integration/row.json').read_text())
        row['child_histogram']['1'] -= 1
        with self.assertRaises((AssertionError, ValueError)):
            price147.bit_profile(row)

    def test_fictitious_extra_role_is_rejected(self):
        row = json.loads((ROOT / 'research/recycled-bit-integration/row.json').read_text())
        row['R'] += 1
        row['W_per_vertex'] += 1
        with self.assertRaises((AssertionError, ValueError)):
            price147.bit_profile(row)

    def test_optimized_entry_points_reject_before_verification(self):
        for path in ('research/recycled-bit-integration/verify.py',
                     'research/bit-reuse-147/verify.py', 'research/bit-elim-144/verify.py'):
            for flags, opt in ((['-O'], ''), (['-OO'], ''), ([], '1')):
                with self.subTest(path=path, flags=flags, opt=opt):
                    env = dict(os.environ, PYTHONOPTIMIZE=opt)
                    p = subprocess.run([sys.executable, *flags, str(ROOT / path)],
                        capture_output=True, text=True, env=env, timeout=10)
                    self.assertNotEqual(p.returncode, 0)
                    self.assertIn('Assertions must remain enabled', p.stderr)
                    self.assertNotIn('PASS', p.stdout)

if __name__ == '__main__':
    unittest.main()
