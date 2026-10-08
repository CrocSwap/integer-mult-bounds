"""Failure modes of the concrete finite certificate and its literal interface."""
from copy import deepcopy
from hashlib import sha256
from fractions import Fraction as Q
import gzip
import json
import subprocess
import sys
import unittest
from support import HERE, SELECTED
import arithmetic
import verify


class WitnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word = json.loads(gzip.decompress((SELECTED/'word-23.json.gz').read_bytes()))
        cls.cert = json.loads((SELECTED/'certificate.json').read_text())

    def test_selected_literal_ports(self):
        verify.validate_word(self.word)

    def test_negative_role_alias(self):
        bad = deepcopy(self.word)
        bad['ops'][0][0] = -1
        with self.assertRaises(ValueError):
            verify.validate_word(bad)

    def test_negative_frame_alias(self):
        bad = deepcopy(self.word)
        bad['ops'][0][2] = -1
        with self.assertRaises(ValueError):
            verify.validate_word(bad)

    def test_aliased_source(self):
        bad = deepcopy(self.word)
        bad['sources']['0'] = bad['sources']['1']
        with self.assertRaises(ValueError):
            verify.validate_word(bad)

    def test_unpaid_canceling_scatter(self):
        bad = deepcopy(self.word)
        bad['scatter'].extend([bad['scatter'][0], bad['scatter'][0]])
        with self.assertRaises(ValueError):
            verify.validate_word(bad)

    def test_wrong_scatter_destination(self):
        bad = deepcopy(self.word)
        bad['scatter'][0][0] += 1
        with self.assertRaises(ValueError):
            verify.validate_word(bad)

    def test_understated_width(self):
        bad = deepcopy(self.word)
        bad['R'] -= 1
        with self.assertRaises(ValueError):
            verify.validate_word(bad)

    def test_omitted_paid_child(self):
        bad = deepcopy(self.cert['bit'])
        bad['child_multiplicities']['1'] -= 1
        with self.assertRaises(AssertionError):
            arithmetic.moment(bad, Q(self.cert['bit_saving']))

    def test_exact_accepted_and_rejected_grid(self):
        accepted = arithmetic.independent_moment(self.cert['bit'], Q(self.cert['bit_saving']))
        rejected = arithmetic.independent_moment(self.cert['bit'], Q(self.cert['next_bit_saving']))
        self.assertLess(accepted[1], 1)
        self.assertGreater(rejected[0], 1)

    def test_complete_predecessor_is_excluded(self):
        old = json.loads((HERE/'vendor/pr82-certificate.json').read_text())['bit']
        self.assertGreater(arithmetic.independent_moment(old, Q(self.cert['bit_saving']))[0], 1)

    def test_float_saving_rejected(self):
        with self.assertRaises(AssertionError):
            arithmetic.moment(self.cert['bit'], float(Q(self.cert['bit_saving'])))

    def test_optimized_python_rejected(self):
        result = subprocess.run([sys.executable, '-O', str(HERE/'verify.py')], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Assertions must remain enabled', result.stderr)

    def test_commuting_scatter_order(self):
        changed = deepcopy(self.word)
        changed['scatter'].reverse()
        verify.validate_word(changed)

    def reject_stale_bridge(self, section, key, value):
        bridge = arithmetic.bridge_for(self.cert['bit'])
        bridge[section][key] = value
        with self.assertRaises(arithmetic.balanced.InvalidAssembly):
            arithmetic.balanced.assembly(bridge, Q(self.cert['bit_saving']), Q(self.cert['kappa']), h=arithmetic.BACKOFF)

    def test_stale_wire_bits(self):
        self.reject_stale_bridge('bit', 'wire_bits', 28)

    def test_stale_row_coefficient(self):
        self.reject_stale_bridge('rows', 'coefficient', 852)

    def test_stale_degree_gap(self):
        self.reject_stale_bridge('rows', 'degree_gap', Q(6548, 25))

    def test_pin_help_does_not_refresh_sources(self):
        before = sha256((HERE/'SOURCE.json').read_bytes()).hexdigest()
        result = subprocess.run([sys.executable, str(HERE/'pin.py'), '--help'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(before, sha256((HERE/'SOURCE.json').read_bytes()).hexdigest())


if __name__ == '__main__':
    unittest.main()
