import itertools
import unittest

from checks import (at_most, satisfied, audit_counter_bridge, build_instance,
                    normalize, word_assignment, covers)


class EncodingTests(unittest.TestCase):
    def test_constructive_counter_extension(self):
        for n in range(2, 9):
            for bound in range(1, n - 1):
                literals = list(range(1, n + 1))
                clauses, top, meaning = at_most(literals, bound, n)
                for bits in itertools.product((False, True), repeat=n):
                    assignment = dict(zip(literals, bits))
                    for var, prefix, threshold in meaning:
                        assignment[var] = sum(assignment[abs(x)] == (x > 0)
                                              for x in prefix) >= threshold
                    self.assertEqual(satisfied(clauses, assignment), sum(bits) <= bound)
                    self.assertEqual(len(assignment), top)

    def test_target_matches_predecessor(self):
        cnf, pool = build_instance()
        self.assertEqual((cnf.nv, len(cnf.clauses)), (4278, 52672))
        self.assertEqual(audit_counter_bridge(cnf, pool), 6)

    def test_bad_counter_clause_rejected(self):
        cnf, pool = build_instance()
        cnf.clauses[480][0] *= -1
        with self.assertRaises(ValueError):
            audit_counter_bridge(cnf, pool)

    def test_wrong_signed_extension_rejected(self):
        clauses, _, meaning = at_most([-1, -2, -3, -4], 2, 4)
        a = {1: False, 2: False, 3: True, 4: True}
        for var, prefix, threshold in meaning:
            a[var] = sum(a[abs(x)] == (x > 0) for x in prefix) >= threshold
        self.assertTrue(satisfied(clauses, a))
        a[meaning[0][0]] = not a[meaning[0][0]]
        self.assertFalse(satisfied(clauses, a))

    def test_exhaustive_small_floor_words(self):
        for k, c in [(2, 2), (2, 3), (3, 2)]:
            weights = frozenset(range(1, k + 1))
            cnf, pool = build_instance(k, c, weights)
            for word in itertools.product(range(k), repeat=k * c):
                if any(word.count(j) != c for j in range(k)):
                    continue
                word = normalize(word)
                a = word_assignment(word, k, c, pool)
                self.assertEqual(satisfied(cnf.clauses, a), covers(word, k, c, weights))

    def test_target_relaxation_has_constructive_sat_word(self):
        word = [j for j in range(6) for _ in range(5)]
        cnf, pool = build_instance(6, 5, {2})
        self.assertTrue(covers(word, 6, 5, {2}))
        self.assertTrue(satisfied(cnf.clauses, word_assignment(word, 6, 5, pool)))
        self.assertFalse(covers(word, 6, 5, {2, 6}))

    def test_invalid_word_rejected(self):
        _, pool = build_instance(2, 2, {1, 2})
        for word in [[0, 0, 0, 1], [1, 1, 0, 0]]:
            with self.assertRaises(ValueError):
                word_assignment(word, 2, 2, pool)

    def test_invalid_counter_domain_rejected(self):
        for bound in [0, 3, 4]:
            with self.assertRaises(ValueError):
                at_most([1, 2, 3, 4], bound, 4)

    def test_unexpected_variable_rejected(self):
        _, pool = build_instance(2, 2, {1, 2})
        pool.id(('unrecognized',))
        with self.assertRaises(ValueError):
            word_assignment([0, 0, 1, 1], 2, 2, pool)


if __name__ == '__main__':
    unittest.main()
