#!/usr/bin/env python3
"""Tests for the f(7) singleton universal-path engine.

Positive controls reproduce the pinned package numbers byte-for-byte;
negative controls are mutated words/configurations that must be rejected;
the set-level census reproduces the community nine-point five-bit result.
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine import (
    coverage_mask,
    coverage_size,
    cyclic_census,
    prefixes,
    rg_prefixes,
    restricted_growth_words,
    word_is_restored,
    word_is_universal,
    gray_word,
    census_words,
    counting_least_even_L,
    split_identity_feasible,
    admissible_splits,
    normalized_set_census,
    hamiltonian_cycle,
    closed_walk_word,
    joint_covers,
    lemma_a_table,
    set_level_splits,
)

ROOT = Path(__file__).resolve().parents[2]
PINNED = json.loads(
    (ROOT / "research" / "universal-connector-six-source" / "EXPECTED.json").read_text(
        encoding="utf-8"
    )
)
PINNED_CENSUSES = {(c["sources"], c["length"]): c for c in PINNED["censuses"]}


class TestCoverage(unittest.TestCase):
    def test_tiny_words(self):
        self.assertEqual(coverage_size([0, 0]), 2)          # D = {0, 1}
        self.assertEqual(coverage_size([0, 1, 0, 1]), 4)     # full F2^2
        self.assertEqual(coverage_size([0, 1, 0, 1, 2, 2]), 8)  # full F2^3

    def test_coverage_mask_matches_pairwise(self):
        w = [0, 1, 0, 2, 0, 1, 0, 2, 3, 4, 3, 4]
        ps = prefixes(w)
        brute = 0
        for a in ps:
            for b in ps:
                brute |= 1 << (a ^ b)
        self.assertEqual(coverage_mask(ps), brute)

    def test_gray_constructions_universal(self):
        for n in range(1, 9):
            rec = PINNED["constructions"][str(n)]
            w = gray_word(n)
            self.assertTrue(word_is_universal(w, n), f"n={n}")
            self.assertEqual(len(w), rec["length"])
            self.assertTrue(word_is_restored(w, n))

    def test_mutations_rejected(self):
        w = gray_word(6)
        self.assertTrue(word_is_universal(w, 6))
        bad = w[:-1]  # omitted final source call
        self.assertFalse(word_is_restored(bad, 6))
        self.assertFalse(word_is_universal(bad, 6))
        self.assertFalse(word_is_universal([0, 1, 0, 1], 3))  # label 2 unused


class TestReproduction(unittest.TestCase):
    """Smallest falsifying instance first: the pinned censuses must reproduce
    byte-for-byte (word counts, histograms, maxima, records SHA-256)."""

    def _run(self, n, length):
        hist, records_sha, words = census_words(n, length)
        pinned = PINNED_CENSUSES[(n, length)]
        self.assertEqual(words, pinned["words"])
        self.assertEqual(max(hist), pinned["max_coverage"])
        self.assertEqual(
            {str(k): v for k, v in sorted(hist.items())}, pinned["histogram"]
        )
        self.assertEqual(records_sha, pinned["records_sha256"])

    def test_n5_len10(self):
        self._run(5, 10)

    def test_n6_len12(self):
        self._run(6, 12)

    def test_n6_len14(self):
        self._run(6, 14)


class TestCountingBound(unittest.TestCase):
    def test_least_even_L(self):
        # Pinned EXPECTED.json constructions record lower_bound 10/14/18.
        self.assertEqual(counting_least_even_L(5), 10)
        self.assertEqual(counting_least_even_L(6), 14)
        self.assertEqual(counting_least_even_L(7), 18)

    def test_admissible_splits_L18_n7(self):
        splits = admissible_splits(7, 18)
        self.assertEqual(splits, [(9, 9)])

    def test_split_identity_kills_small_odd_side(self):
        # (9,8) at n=7: the pair-representation identity is contradictory.
        self.assertFalse(split_identity_feasible(7, 9, 8))
        self.assertFalse(split_identity_feasible(7, 8, 9))
        self.assertFalse(split_identity_feasible(7, 8, 8))
        self.assertTrue(split_identity_feasible(7, 9, 9))
        # n=5 nine-point splits die the same way (community census: max 29).
        self.assertFalse(split_identity_feasible(5, 5, 4))
        self.assertFalse(split_identity_feasible(5, 4, 5))
        self.assertTrue(split_identity_feasible(5, 5, 5))

    def test_lemma_a_table(self):
        table = lemma_a_table(7, 9, 8)
        for row in table:
            self.assertFalse(row["feasible"])
        table = lemma_a_table(7, 9, 9)
        self.assertTrue(any(row["feasible"] for row in table))


class TestSetCensusControl(unittest.TestCase):
    def test_n5_nine_point_sets(self):
        # Independent reproduction of the community five-bit result:
        # all 7,888,725 normalized nine-point sets, zero full covers, max 29.
        stats = normalized_set_census(5, 9)
        self.assertEqual(stats["sets"], 7_888_725)
        self.assertEqual(stats["max_coverage"], 29)
        self.assertEqual(stats["covers"], 0)


class TestCycleRealization(unittest.TestCase):
    def test_known_cycle(self):
        # The 6-cycle of Q_3: 000, 001, 011, 010, 110, 100.
        P = [0b000, 0b001, 0b011, 0b010, 0b110, 0b100]
        w = hamiltonian_cycle(P, 3)
        self.assertIsNotNone(w)
        self.assertEqual(len(w), 6)
        self.assertEqual(set(closed_walk_word(P, w)), set(P))

    def test_star_not_hamiltonian(self):
        # 000 plus its three neighbours: no cycle through all four points.
        P = [0b000, 0b001, 0b010, 0b100]
        self.assertIsNone(hamiltonian_cycle(P, 3))

    def test_f5_ten_point_covers_not_realisable_at_10(self):
        # f(5) = 12 pins that no 10-point cover of F2^5 is a closed 10-walk.
        covers = joint_covers(5, set_level_splits(5, 10))
        self.assertTrue(covers, "the joint search must actually find covers")
        for E, O in covers:
            P = sorted(set(E) | set(O))
            self.assertEqual(len(P), 10)
            self.assertIsNone(
                hamiltonian_cycle(P, 5), "f(5)=12 forbids a 10-cycle cover"
            )


class TestJointCovers(unittest.TestCase):
    def test_agrees_with_brute_force_n5(self):
        # Cross-validation of the joint search against the brute-force
        # ten-point set census (planted-hit non-vacuity: covers must be found).
        brute = normalized_set_census(5, 10)
        joint = joint_covers(5, set_level_splits(5, 10))
        self.assertGreater(brute["covers"], 0)
        self.assertEqual(len(joint), brute["covers"])


class TestCyclicCensus(unittest.TestCase):
    """The decisive engine, validated at the pinned small values."""

    def test_leaf_counts_match_canonical_words(self):
        # Every canonical word with even multiplicities is closed, so with no
        # prune the leaf count and leaf set must match restricted_growth_words.
        for n, L in ((5, 10), (6, 12)):
            want = set(restricted_growth_words(n, L))
            r = cyclic_census(n, L, collect_all=True)
            self.assertEqual(r["leaves"], len(want), (n, L))
            self.assertEqual(set(r["all_words"]), want, (n, L))

    def test_shards_partition_the_tree(self):
        full = cyclic_census(5, 10)
        parts = sum(
            cyclic_census(5, 10, prefix=p)["leaves"] for p in rg_prefixes(5, 3)
        )
        self.assertEqual(parts, full["leaves"])

    def test_n5_len10_no_hit(self):
        r = cyclic_census(5, 10)
        self.assertEqual(r["hits"], 0, "f(5)=12 forbids universal 10-cycles")
        self.assertEqual(r["leaves"], 945)

    def test_n5_len12_planted_hit(self):
        r = cyclic_census(5, 12, stop_on_first=True)
        self.assertGreaterEqual(r["hits"], 1, "f(5)=12 must be attained")
        self.assertTrue(word_is_universal(r["words"][0], 5))

    def test_n6_len14_no_hit(self):
        r = cyclic_census(6, 14)
        self.assertEqual(r["hits"], 0, "f(6)=16 forbids universal 14-cycles")
        self.assertEqual(r["leaves"], 945_945)

    def test_n6_len16_planted_hit(self):
        r = cyclic_census(6, 16, stop_on_first=True)
        self.assertGreaterEqual(r["hits"], 1, "f(6)=16 must be attained")
        self.assertTrue(word_is_universal(r["words"][0], 6))


if __name__ == "__main__":
    unittest.main(verbosity=2)
