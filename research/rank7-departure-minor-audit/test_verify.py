#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fault controls for the independent departure audit (standard library only)."""
import copy
import json
import unittest
from fractions import Fraction as Q

import verify as v


def rational_det(matrix):
    """Separate Gaussian determinant, without Bareiss or row-basis selection."""
    a = [list(map(Q, row)) for row in matrix]
    answer = Q(1)
    for j in range(len(a)):
        p = next((i for i in range(j, len(a)) if a[i][j]), None)
        if p is None:
            return Q(0)
        if p != j:
            a[j], a[p] = a[p], a[j]
            answer = -answer
        pivot = a[j][j]
        answer *= pivot
        for i in range(j + 1, len(a)):
            factor = a[i][j] / pivot
            for k in range(j, len(a)):
                a[i][k] -= factor * a[j][k]
    return answer


class AuditControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sources = json.loads((v.HERE / 'SOURCES.json').read_bytes())['files']
        cls.source = next(s for s in sources if s['usage'] == 'input')
        cls.raw = (v.ROOT / cls.source['path']).read_bytes()
        cls.word = v.decode_word(cls.raw, cls.source['sha256'])
        cls.result = v.run()['result']

    def test_both_providers_and_all_minor_determinants(self):
        self.assertEqual(len(self.result['departure_witnesses']), 10)
        self.assertEqual(len(self.result['no_reader_cases']), 17)
        for w in self.result['departure_witnesses']:
            with self.subTest(register=w['register']):
                a = w['integer_minor']
                self.assertEqual(rational_det(a), w['integer_determinant'])
                self.assertNotEqual(rational_det(a), 0)
                bad = copy.deepcopy(a)
                bad[-1] = bad[0][:]
                self.assertEqual(rational_det(bad), 0)
                self.assertEqual(v.determinant(bad), 0)

    def test_corrupt_bytes_fail_before_parsing(self):
        with self.assertRaisesRegex(ValueError, 'source digest mismatch'):
            v.decode_word(self.raw[:-1] + bytes([self.raw[-1] ^ 1]), self.source['sha256'])

    def test_empty_restore_cannot_supply_its_own_coordinates(self):
        w = copy.deepcopy(self.word)
        w['restore'] = []
        with self.assertRaisesRegex(ValueError, 'forced coordinate fails prefix identity'):
            v.forced_coordinates(w)

    def test_wrong_restored_helper_coefficient(self):
        w = copy.deepcopy(self.word)
        gate = next(g for g in reversed(w['restore'])
                    if g[0] == 'scale' and str(g[1]) in w['helper_final'])
        gate[2] = -gate[2]
        with self.assertRaisesRegex(ValueError, 'forced coordinate fails prefix identity'):
            v.forced_coordinates(w)

    def test_changed_prefix_with_unchanged_restore(self):
        w = copy.deepcopy(self.word)
        helper = min(map(int, w['helper_final']))
        w['B'].append(['add', helper, 0, 1, 1, []])
        with self.assertRaisesRegex(ValueError, 'forced coordinate fails prefix identity'):
            v.forced_coordinates(w)

    def test_target_feedback_and_singular_gate(self):
        w = copy.deepcopy(self.word)
        w['B'].append(['add', 0, 112, 1, 1, []])
        with self.assertRaisesRegex(ValueError, 'illegal ADD operands'):
            v.forced_coordinates(w)
        for gate, message in ((['scale', 0, 0, 1], 'noninvertible SCALE'),
                              (['add', 0, 0, 1, 1], 'illegal ADD operands')):
            with self.subTest(gate=gate), self.assertRaisesRegex(ValueError, message):
                v.scalar(gate, {0: {0: Q(1)}})
        rows = {0: {0: Q(1)}}
        v.scalar(['scale', 0, 1, -4], rows)
        self.assertEqual(rows, {0: {0: Q(-1, 4)}})

    def test_inconsistent_cut_frame(self):
        w = copy.deepcopy(self.word)
        w['center_frames'][0] = []
        with self.assertRaisesRegex(ValueError, 'below its lower bound'):
            v.entry_bounds(w, v.forced_coordinates(w), v.ends(w))

    def test_missing_coordinate_destroys_departure_obstruction(self):
        m, end = v.forced_coordinates(self.word), v.ends(self.word)
        lower, _ = v.entry_bounds(self.word, m, end)
        frame = next(w['frame'] for w in self.result['departure_witnesses'] if w['register'] == 69)
        for row in m.values():
            row.pop(69, None)
        with self.assertRaisesRegex(ValueError, 'departure matrix not full rank'):
            v.rank_witness(m, lower, end, 69, v.space(frame))


if __name__ == '__main__':
    unittest.main()
