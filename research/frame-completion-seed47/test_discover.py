#!/usr/bin/env python3
"""Exercise the producer against independently enumerated tiny-space optima."""
import unittest

import check
import discover


class CompletionProducerTest(unittest.TestCase):
    def test_every_orthogonal_pair_through_dimension_four(self):
        pairs = 0
        for h in range(5):
            spaces = check.all_subspaces(h)
            perps = {space: check.perpendicular(space, h) for space in spaces}
            nondegenerate = [space for space in spaces if check.radical(space) == frozenset({0})]
            for A in spaces:
                for B in spaces:
                    if not A <= perps[B]:
                        continue
                    pairs += 1
                    with self.subTest(h=h, A=sorted(A), B=sorted(B)):
                        R, U, common = discover.complete(check.spanning_vectors(A),
                                                         check.spanning_vectors(B), h)
                        self.assertEqual(check.span(R, h, 'radical'), check.radical(A))
                        candidates = [frame for frame in nondegenerate if A <= frame <= perps[B]]
                        if not candidates:
                            self.assertIsNone(U)
                            self.assertNotEqual(common, 0)
                            self.assertIn(common, A & B)
                        else:
                            self.assertIsNone(common)
                            frame = check.span(U, h, 'produced frame')
                            self.assertIn(frame, candidates)
                            self.assertEqual(check.dimension(frame), min(map(check.dimension, candidates)))
        self.assertEqual(pairs, 595)

    def test_disjoint_nonorthogonal_spans_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'not orthogonal'):
            discover.complete([1], [3], 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
