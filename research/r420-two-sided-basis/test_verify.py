"""Exact obligations specific to two-sided composition; Apache-2.0."""
import copy
import unittest

import verify as v


class TwoSidedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word = v.read_sources()
        cls.recipe = v.nominate(cls.word)

    def test_four_term_matrix_formula(self):
        original = v.original_rows(self.word)
        _, helper_gates = v.helper_transform(self.word)
        target_parent = {b: a for a, b, _ in self.recipe['target_pairs']}
        helper_parent = {g[2][0]: g[1] for g in helper_gates}
        # Direct four-entry formula, without sequential basis transformation.
        expected = {}
        for t in range(120, 240):
            expected[t] = set()
            for h in range(240, 660):
                ts = [t] + ([target_parent[t]] if t in target_parent else [])
                hs = [h] + ([helper_parent[h]] if h in helper_parent else [])
                if sum(s in original[r] for r in ts for s in hs) % 2:
                    expected[t].add(h)
        word = v.build(self.word, self.recipe)
        boundary = len(helper_gates) + len(self.recipe['target_pairs'])
        middle = {dst: set(srcs) for _, dst, srcs in word['D'][boundary:-boundary]}
        self.assertEqual(expected, middle)

    def test_all_target_scores_by_column_incidence(self):
        matrix, _ = v.helper_transform(self.word)
        for a in range(120, 240):
            for b in range(120, 240):
                if a != b:
                    cost = sum(1 if s in matrix[b] else -1 for s in range(240, 660) if s in matrix[a]) - 2
                    self.assertEqual(cost, len(matrix[b]) - len(matrix[a] ^ matrix[b]) - 2)

    def test_overlapping_target_pairs_rejected(self):
        recipe = copy.deepcopy(self.recipe)
        recipe['target_pairs'].append(recipe['target_pairs'][0])
        with self.assertRaisesRegex(v.Reject, 'overlap'):
            v.build(self.word, recipe)

    def test_no_uncharged_basis_operations(self):
        recipe = copy.deepcopy(self.recipe)
        recipe['target_pairs'][0][2] += 2
        with self.assertRaisesRegex(v.Reject, 'priced on KQ'):
            v.build(self.word, recipe)


if __name__ == '__main__':
    unittest.main()
