"""Obligation tests beyond the frozen successful construction; Apache-2.0."""
import copy
import unittest

import verify as v


class TargetBasisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word = v.read_sources()
        cls.recipe = v.nominate(cls.word)

    def test_all_pair_scores_by_column_census(self):
        # Independently count removed and introduced helper incidences.
        matrix = v.rows(self.word)
        for a in range(120, 240):
            for b in range(120, 240):
                if a != b:
                    gain = sum((1 if h in matrix[b] else -1)
                               for h in range(240, 660) if h in matrix[a]) - 2
                    self.assertEqual(gain, len(matrix[b]) - len(matrix[a] ^ matrix[b]) - 2)

    def test_overlapping_pairs_rejected(self):
        recipe = copy.deepcopy(self.recipe)
        recipe['pairs'].append(recipe['pairs'][0])
        with self.assertRaisesRegex(v.Reject, 'disjoint'):
            v.build(self.word, recipe)

    def test_underpriced_restoration_rejected(self):
        recipe = copy.deepcopy(self.recipe)
        recipe['pairs'][0][2] += 2
        with self.assertRaisesRegex(v.Reject, 'charged gain'):
            v.build(self.word, recipe)

    def test_target_dirt_is_essential(self):
        changed = v.build(self.word, self.recipe)
        changed['D'].pop(0)
        correct, wrong = v.set_prefix(self.word), v.set_prefix(changed)
        targets = set(range(120, 240))
        self.assertEqual([s - targets for s in correct], [s - targets for s in wrong])
        self.assertNotEqual(correct, wrong)
        with self.assertRaisesRegex(v.Reject, 'arbitrary inputs'):
            v.prefix_contract(self.word, changed)


if __name__ == '__main__':
    unittest.main()
