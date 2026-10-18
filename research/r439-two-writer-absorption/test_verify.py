#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Adam Gall, with substantial OpenAI Codex assistance.
"""Focused tests; no whole-repository replay."""
import copy
import importlib.util
import itertools
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('two_writer', Path(__file__).with_name('verify.py'))
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word = v.load_word()
        cls.count, cls.edges, cls.first, cls.writers, cls.snapshots = v.star_domain(cls.word)

    def test_two_writer_boolean_identity(self):
        # Three arbitrary dirty values; the middle gate changes the later donor.
        # Independent scalar Boolean interpreter, all eight input assignments.
        for x, a, b in itertools.product((0, 1), repeat=3):
            pending = a ^ b
            pending ^= x
            later_leaf = b ^ x
            pending ^= later_leaf
            self.assertEqual(pending, a)
            # Assuming the second donor is still the original b is false.
            if x:
                self.assertNotEqual((a ^ b ^ x) ^ b, a)

    def test_source_pair_and_rows(self):
        self.assertIn((231, 459), self.edges)
        self.assertEqual(self.writers[231], [9, 527])
        self.assertEqual(self.first[231], 528)
        self.assertEqual(self.snapshots[9][109], 1 << 109)
        self.assertEqual(self.snapshots[527][459], (1 << 109) ^ (1 << 459))

    def test_rational_frame_failure(self):
        candidate = v.candidate(self.word, (-1, 231, 459, 9, 527, 109, 459), self.count)
        paths, error = v.Geometry(self.word).paths(candidate)
        self.assertIsNone(paths)
        self.assertEqual(error, {'section': 'A', 'gate': 9, 'register': 109,
                                'old_frame': 111, 'new_frame': 6, 'outside_label': 109,
                                'receiving_rank': 1, 'extended_rank': 2})
        self.assertEqual(v.literal(candidate), v.wanted(candidate))

    def test_clean_only_false_acceptance(self):
        candidate = v.omit_restoration(self.word, 231, 459, self.count)
        actual, target = v.literal(candidate), v.wanted(candidate)
        self.assertNotEqual(actual, target)
        # Projecting away every dirty-helper input hides the missing restoration.
        clean_mask = (1 << (2 * self.word['v'])) - 1
        self.assertEqual([r & clean_mask for r in actual], [r & clean_mask for r in target])

    def test_second_donor_uniqueness(self):
        rows = self.snapshots[527]
        required = self.snapshots[9][109] ^ (1 << 459)
        self.assertEqual([r for r, row in enumerate(rows) if row == required], [459])

    def test_source_pin_corruption(self):
        v.check_pin(b'unchanged', v.sha(b'unchanged'))
        with self.assertRaisesRegex(ValueError, 'source pin mismatch'):
            v.check_pin(b'changed', v.sha(b'unchanged'))

    def test_domain_rejects_overlapping_stars(self):
        candidate = copy.deepcopy(self.word)
        candidate['D'][0][2] = [candidate['D'][0][1]]
        candidate['D'][-1][2] = [candidate['D'][-1][1]]
        with self.assertRaisesRegex(ValueError, 'disjoint star leaves'):
            v.star_domain(candidate)


if __name__ == '__main__':
    unittest.main()
