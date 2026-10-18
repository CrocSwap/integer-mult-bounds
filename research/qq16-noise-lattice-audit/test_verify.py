#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import copy
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f'{name}.py')
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


V = module('verify')
I = module('independent')


class NoiseLatticeControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = V.load_packet()
        cls.receipt = json.loads((HERE / 'RESULT.json').read_text())

    def test_intermediate_guard_survives_endpoint_cancellation(self):
        events = [
            ['climb', 'B', 0, 0, 1, 1],
            ['scalar', ['add', ['L', 1], ['L', 0], 1, 2], 1],
            ['scalar', ['add', ['L', 1], ['L', 0], -1, 2], 1],
            ['scalar', ['scale', ['L', 0], 1, 8], 1],
            ['scalar', ['scale', ['L', 0], 8, 1], 1],
        ]
        report = V.analyze(events)
        self.assertEqual(report['child_guard_bits'], 3)
        self.assertEqual(report['child_attainment']['attainment']['event'], 3)
        self.assertEqual(I.reverse_coefficient(events, {'event': 0, 'wire': 0},
                                               {'event': 4, 'wire': 0}), 1)

    def test_clear_erases_a_fault_but_does_not_erase_earlier_obligation(self):
        events = [
            ['climb', 'B', 0, 0, 1, 1],
            ['scalar', ['add', ['L', 1], ['L', 0], 1, 2], 1],
            ['scalar', ['clear', ['L', 1]], 1],
        ]
        report = V.analyze(events)
        self.assertEqual(report['child_guard_bits'], 1)
        self.assertEqual(I.reverse_coefficient(events, {'event': 0, 'wire': 0},
                                               {'event': 2, 'wire': 1}), 0)

    def test_adjacent_witness_cannot_skip_an_adapter(self):
        events = [
            ['climb', 'B', 0, 0, 1, 1],
            ['adapter', 'not a scalar'],
            ['scalar', ['add', ['L', 1], ['L', 0], 1, 2], 1],
        ]
        self.assertEqual(V.direct_sites(events), [])

    def test_same_grid_and_nearest_rounding_are_not_exact(self):
        for p in [0, 4, 17, 29, 61, 256]:
            q = Q(1, 1 << p)
            for sign in [-1, 1]:
                exact = sign * 3 * q / 2
                lower = (exact // q) * q
                self.assertEqual(abs(exact - lower), q / 2)
                self.assertEqual(abs(exact - (lower + q)), q / 2)

    def test_mutated_attainment_rejected_by_independent_dual(self):
        report = copy.deepcopy(self.receipt)
        report['cases']['B_1_2']['child_attainment']['attainment']['coefficient'] = '-81920/262144'
        with self.assertRaisesRegex(ValueError, 'forward coefficient'):
            I.verify(report, self.packet)

    def test_weaker_guard_rejected(self):
        report = copy.deepcopy(self.receipt)
        report['cases']['B_1_2']['child_attainment']['attainment']['bits'] = 17
        with self.assertRaisesRegex(ValueError, 'guard maximum'):
            I.verify(report, self.packet)

    def test_swapped_child_register_rejected(self):
        report = copy.deepcopy(self.receipt)
        report['cases']['B_1_2']['seed_selected_local_witness']['child'][2] += 1
        with self.assertRaisesRegex(ValueError, 'child bytes'):
            I.verify(report, self.packet)

    def test_changed_live_source_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / V.SOURCE
            source.parent.mkdir(parents=True)
            source.write_bytes(b'not the pinned certificate')
            with patch.object(V, 'ROOT', root):
                with self.assertRaisesRegex(ValueError, 'SHA256 mismatch'):
                    V.load_packet()

    def test_unknown_event_rejected(self):
        packet = {'programs': {'bad': [['unknown_map']]}}
        with self.assertRaisesRegex(ValueError, 'unknown event'):
            V.expand(packet, 'bad')

    def test_non_dyadic_and_invalid_register_rejected(self):
        with self.assertRaisesRegex(ValueError, 'non-dyadic'):
            V.denominator_bits(Q(1, 3))
        for invalid in [['L', 704], ['C', 8], ['Q', 0], ['L', -1]]:
            with self.assertRaises(ValueError):
                V.register(invalid)

    def test_complete_child_histograms(self):
        self.assertEqual(sum(c['child_defect_columns'] for c in self.receipt['cases'].values()), 7004)
        for record in self.receipt['cases'].values():
            self.assertEqual(sum(record['child_guard_histogram'].values()), record['child_defect_columns'])
            self.assertEqual(max(map(int, record['child_guard_histogram'])), record['child_guard_bits'])
        self.assertEqual(self.receipt['cases']['B_1_2']['child_guard_histogram']['18'], 12)


if __name__ == '__main__':
    unittest.main()
