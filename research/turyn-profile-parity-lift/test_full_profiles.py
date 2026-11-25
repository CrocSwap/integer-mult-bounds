#!/usr/bin/env python3
"""Complete-profile checker regression controls; no predecessor imports."""
from pathlib import Path
from unittest.mock import patch
import copy
import importlib.util
import json
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('full_profile_checker', HERE/'verify_full_profiles.py')
F = importlib.util.module_from_spec(spec)
spec.loader.exec_module(F)
V = F.V


class FullProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code = V.turyn_code()
        cls.ports, cls.digest = F.enumerate_ports(cls.code)
        cls.certificate = V.load('FULL-PROFILE-UPPER.json')

    def test_complete_independent_replay(self):
        self.assertEqual(F.run(), V.load('FULL-PROFILE-EXPECTED.json'))

    def test_independent_enumerator_matches_producer_array(self):
        producer_spec = importlib.util.spec_from_file_location('new_baseline_producer', HERE.parent/'turyn-profile-cnf/build.py')
        producer = importlib.util.module_from_spec(producer_spec)
        producer_spec.loader.exec_module(producer)
        ports, digest = producer.construct_ports()
        self.assertEqual((ports, digest), (self.ports, self.digest))

    def test_dropped_port_invalidates_complete_fiber_partition(self):
        with self.assertRaisesRegex(ValueError, '120-by-64 fiber partition'):
            F.upper_bound(self.ports[1:], self.certificate, self.code)

    def test_root_or_label_corruption(self):
        for kind in ('duplicate_root', 'wrong_label', 'even_label', 'wrong_root_norm'):
            changed = copy.deepcopy(self.certificate)
            if kind == 'duplicate_root':
                changed['roots'][0] = changed['roots'][1]
            elif kind == 'wrong_label':
                changed['nine_bit_labels'][0] = changed['nine_bit_labels'][1]
            elif kind == 'even_label':
                changed['nine_bit_labels'][0] = 0
            else:
                changed['roots'][0][0] += 1
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                F.upper_bound(self.ports, changed, self.code)

    def test_changed_literal_port_index_is_rejected(self):
        original = V.load
        def altered(name):
            data = original(name)
            if name == 'CERTIFICATE.json':
                data['profiles'][0]['selected_ports'][0] += 1
            return data
        with patch.object(V, 'load', altered), self.assertRaisesRegex(ValueError, 'source indices'):
            F.run()

    def test_source_class_and_replacement_index_are_bound(self):
        lower = V.load('CERTIFICATE.json')
        control = V.load('SAME-CLASS-CONTROL.json')
        changed = copy.deepcopy(lower)
        changed['profiles'][0]['classes'][0] += 1
        with self.assertRaisesRegex(ValueError, 'declared quotient source class'):
            F.bind_source_classes(self.ports, changed, control)
        changed_control = copy.deepcopy(control)
        changed_control['replacement_port'] += 1
        with self.assertRaisesRegex(ValueError, 'exact replacement coordinates'):
            F.bind_source_classes(self.ports, lower, changed_control)

    def test_a_same_fiber_active_edge_cannot_be_ignored(self):
        # This directly exercises the exhaustive same-fiber obligation:
        # one injected active answer must invalidate the upper proof.
        with patch.object(V, 'active', return_value=True), self.assertRaisesRegex(ValueError, 'same-root ports are inactive'):
            F.upper_bound(self.ports, self.certificate, self.code)


if __name__ == '__main__':
    unittest.main(verbosity=2)
