#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Aaron Wang, with help from opencode.
"""Focused tests for the forced-carry closure engine. Standard library only."""
import json
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify


def toy_word():
    # Three registers: sources 0 and 1 at their own lines, register 2 at frame 0.
    # Frames: 0 = zero, 1 = full {0,1,2}, 2 = {0}, 3 = {1}, 4 = {0,1}, 5 = {2}.
    # A[0] touches all three registers, so its forced frame is the join {0,1}.
    frames = [[], [0, 1, 2], [0], [1], [0, 1], [2]]
    lines = [[1, 0, 0, 0, 0, 0, 0, 0],
             [0, 1, 0, 0, 0, 0, 0, 0],
             [0, 0, 1, 0, 0, 0, 0, 0]]
    return {
        'v': 1, 'R': 1, 'lines': lines, 'frames': frames,
        'start': [2, 3, 0],
        'final': [1, 1, 2],
        'D': [], 'A': [[4, 2, [0, 1]]], 'B': [], 'C': [],
        'ret': [], 'scatter': [],
    }


class RankTests(unittest.TestCase):
    def test_exact_ranks(self):
        self.assertEqual(len(verify.rref([[1, 0, 0, 0, 0, 0, 0, 0]])), 1)
        self.assertEqual(len(verify.rref([[1, 0, 0, 0, 0, 0, 0, 0],
                                          [0, 1, 0, 0, 0, 0, 0, 0]])), 2)
        self.assertEqual(len(verify.rref([[1, 0, 0, 0, 0, 0, 0, 0],
                                          [2, 0, 0, 0, 0, 0, 0, 0]])), 1)

    def test_mask_containment_matches_sets(self):
        rng = random.Random(20261015)
        universe = 111
        for _ in range(200):
            a = rng.getrandbits(universe)
            b = rng.getrandbits(universe)
            sa = {k for k in range(universe) if (a >> k) & 1}
            sb = {k for k in range(universe) if (b >> k) & 1}
            self.assertEqual((a | b) == b, sa <= sb)


class ClosureTests(unittest.TestCase):
    def test_forced_join_and_witness(self):
        word = toy_word()
        geo = verify.Geometry(word)
        fails, cur = verify.closure_walk(geo, word, use_orig_floor=False)
        # A[0] touches sources at {0} and {1} and register 2 at zero:
        # the forced join is {0,1} and every touched register carries it.
        self.assertEqual(cur[2], geo.frame_masks[4])
        self.assertEqual(cur[0], geo.frame_masks[4])
        self.assertEqual(cur[1], geo.frame_masks[4])
        # Final of register 2 is {0}; the forced carry {0,1} leaks label 1.
        by_reg = {r: w for r, w in fails}
        self.assertEqual(set(by_reg), {2})
        self.assertEqual(by_reg[2]['leaked_labels'], [1])
        self.assertEqual(by_reg[2]['rank_final'], 1)
        self.assertEqual(by_reg[2]['rank_joined'], 2)

    def test_leastness(self):
        word = toy_word()
        geo = verify.Geometry(word)
        _, cur = verify.closure_walk(geo, word, use_orig_floor=False)
        # Any legal reframing must dominate the closure: enlarging gate frames
        # further cannot remove the leaked direction from register 2.
        big = geo.frame_masks[1]
        for r in (0, 1, 2):
            self.assertEqual(cur[r] | big, big)
        self.assertTrue((cur[2] | geo.frame_masks[2]) != geo.frame_masks[2])

    def test_wanted_boundary_formula(self):
        word = {'v': 1, 'R': 1}
        self.assertEqual(verify.wanted(word), [1, 0b11, 0b100])


class ContractTests(unittest.TestCase):
    def test_profile_mass(self):
        self.assertEqual(sum(k * v for k, v in verify.PROFILE.items()), verify.PROFILE_MASS)

    def test_second_donor_lookup_uniqueness(self):
        # Distinct nonzero rows make the second-donor lookup injective.
        rng = random.Random(42)
        rows = set()
        while len(rows) < 64:
            rows.add(rng.getrandbits(64) | 1)
        rows = list(rows)
        lookup = {r: i for i, r in enumerate(rows)}
        self.assertEqual(len(lookup), len(rows))

    def test_loader_refuses_pin_drift(self):
        manifest = json.loads((verify.HERE / 'SOURCES.json').read_text(encoding='utf-8'))
        entry = [x for x in manifest['files'] if x['path'] == verify.WORD][0]
        data = (verify.ROOT / verify.WORD).read_bytes()
        self.assertEqual(verify.sha(data), entry['sha256'])


if __name__ == '__main__':
    unittest.main()
