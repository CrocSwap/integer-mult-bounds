#!/usr/bin/env python3
"""Unit tests for the KB3b f(7) package (fast; no long censuses)."""
import hashlib
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from engine import (
    census_words,
    cyclic_census,
    gray_word,
    hamiltonian_cycle,
    lemma_a_table,
    prefixes,
    rg_prefixes,
    word_is_restored,
    word_is_universal,
)
from search import (
    climb_set,
    cov_pts,
    induced_degrees,
    missing_masks,
    patterns,
    word_pts,
)

ENGINE_SHA256 = "82e4c407b58864c74ffd14d47f00b6b1675005ee0e0173909b7bd092491175e4"


class TestVendoredEngine(unittest.TestCase):
    def test_engine_byte_pin(self):
        data = (HERE / "engine.py").read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), ENGINE_SHA256)

    def test_pinned_n5_l10(self):
        hist, digest, words = census_words(5, 10)
        self.assertEqual(words, 945)
        self.assertEqual(max(hist), 31)
        self.assertEqual(digest,
                         "3dcc5689a4a34baec6424389a07dd917c0b681d6a894cba3e909f5a81efdc86e")

    def test_leaf_counts_match_canonical_words(self):
        r = cyclic_census(5, 10)
        self.assertEqual(r["leaves"], 945)


class TestParityLemma(unittest.TestCase):
    def test_odd_lengths_have_no_restored_pattern(self):
        for L in (19, 21, 23):
            self.assertEqual(patterns(7, L), [])

    def test_even_patterns(self):
        self.assertEqual(len(patterns(7, 20)), 3)
        self.assertEqual(len(patterns(7, 22)), 5)
        self.assertEqual(sorted(patterns(7, 14)[0]), [2] * 7)

    def test_restored_requires_even_length(self):
        w = [0] * 19
        self.assertFalse(word_is_restored(w, 7))


class TestCoverageForms(unittest.TestCase):
    def test_prefix_xor_equals_pair_positions(self):
        w = list(gray_word(7))
        pts = prefixes(w)
        m = cov_pts(pts)
        self.assertEqual(m.bit_count(), 128)
        self.assertEqual(missing_masks(pts), [])

    def test_gray_universal(self):
        for n in (4, 5, 6, 7):
            self.assertTrue(word_is_universal(gray_word(n), n))

    def test_cov_pts_matches_engine_on_words(self):
        w = [0, 1, 0, 2, 0, 1, 0, 2, 3, 4, 3, 5, 3, 4, 3, 5]
        self.assertEqual(cov_pts(word_pts(w)).bit_count(),
                         __import__("engine").word_coverage(w))


class TestTransversalLemma(unittest.TestCase):
    """G[R] for R = {t + g(t)} has edges only within level sets of g."""

    def test_level_set_components(self):
        import itertools
        for bits in range(0, 1 << 8, 7):  # deterministic sample of g
            g = [((bits >> (2 * t)) & 3) for t in range(16)]
            R = []
            for t in range(16):
                q1, q2 = g[t] & 1, (g[t] >> 1) & 1
                v = t << 2 | q1 | (q2 << 1)
                R.append(v)
            S = set(R)
            # components: BFS in the induced graph
            seen = set()
            comps = 0
            for v in R:
                if v in seen:
                    continue
                comps += 1
                stack = [v]
                seen.add(v)
                while stack:
                    x = stack.pop()
                    for b in range(6):
                        y = x ^ (1 << b)
                        if y in S and y not in seen:
                            seen.add(y)
                            stack.append(y)
            levels = len(set(g))
            self.assertGreaterEqual(comps, levels)
            if comps == 1:
                self.assertEqual(levels, 1)
                # g constant: R+R is a 16-point plane, far from a cover
                sums = {a ^ b for a in R for b in R}
                self.assertEqual(len(sums), 16)


class TestCoverArtifacts(unittest.TestCase):
    def test_cover20(self):
        expected = json.loads((HERE / "EXPECTED.json").read_text(encoding="utf-8"))
        raw = expected["cover20"]["points"]
        P = sorted(v ^ raw[0] for v in raw)  # normalize 0 into P (translation)
        self.assertEqual(cov_pts(P).bit_count(), 128)
        self.assertEqual(induced_degrees(P), expected["cover20"]["degrees"])
        self.assertIsNone(hamiltonian_cycle(P, 7))
        self.assertLess(min(induced_degrees(P)), 2)

    def test_set_ils_finds_covers_deterministically(self):
        r = climb_set([0, 2, 4, 6, 39, 49, 50, 55, 76, 77,
                       92, 93, 98, 101, 106, 111, 113, 118, 120, 125], 20, [0])
        self.assertEqual(r, 128)


class TestSharding(unittest.TestCase):
    def test_shards_partition(self):
        shards = rg_prefixes(7, 4)
        self.assertEqual(len(shards), 15)  # Bell(4) restricted-growth strings
        self.assertEqual(len(set(shards)), 15)

    def test_lemma_rows_survive_at_L20(self):
        self.assertTrue(any(r["feasible"] for r in lemma_a_table(7, 10, 10)))
        self.assertTrue(any(r["feasible"] for r in lemma_a_table(7, 10, 7)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
