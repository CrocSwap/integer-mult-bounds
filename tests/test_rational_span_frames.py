"""Exact dual-Gram decisions checked against independent Fraction elimination."""
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import rational_span_frames as frames


def fraction_rank(matrix):
    rows = [list(map(Fraction, row)) for row in matrix]
    rank = 0
    for col in range(len(rows[0]) if rows else 0):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][col]
        rows[rank] = [x/scale for x in rows[rank]]
        for i in range(rank+1, len(rows)):
            scale = rows[i][col]
            rows[i] = [x-scale*y for x, y in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def dense_nondegenerate(rows):
    gram = [[9*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b)
             for b in rows] for a in rows]
    return fraction_rank(gram) == len(rows)


class RationalSpanFrames(unittest.TestCase):
    def check_rows(self, rows):
        rows = tuple(tuple(row) for row in rows)
        self.assertEqual(frames.nondegenerate(rows), dense_nondegenerate(rows), rows)

    def test_coordinate_subspaces(self):
        for h in range(1, 11):
            for d in range(h+1):
                for chosen in combinations(range(h), d):
                    self.check_rows(tuple(tuple(int(i == j) for i in range(h)) for j in chosen))

    def test_integer_frames_and_dependent_presentations(self):
        rng = random.Random(90724)
        for h in range(1, 13):
            for _ in range(32):
                d = rng.randrange(h+3)
                self.check_rows(tuple(tuple(rng.randrange(-3,4) for _ in range(h))
                                      for _ in range(d)))
        self.check_rows(((1,0,0,0), (2,0,0,0), (0,1,0,0)))
        self.check_rows(((0,)*10,))

    def test_ambient_dimension_nine_and_negative_gap(self):
        self.assertFalse(frames.nondegenerate(tuple(tuple(int(i == j) for i in range(9))
                                                   for j in range(9))))
        self.assertTrue(frames.nondegenerate(tuple(tuple(int(i == j) for i in range(9))
                                                  for j in range(8))))
        self.assertTrue(frames.nondegenerate(tuple(tuple(int(i == j) for i in range(10))
                                                  for j in range(10))))
        self.assertFalse(frames.nondegenerate(((1,)*9+(0,),)))

    def test_orthogonal_complement_contract(self):
        rng = random.Random(243)
        for h in (4, 8, 10, 12):
            for d in range(h+1):
                U = frames.basis(tuple(tuple(rng.randrange(-2,3) for _ in range(h))
                                       for _ in range(d)))
                V = frames.orthogonal(U,h)
                self.assertEqual(len(V),h-len(U))
                self.assertEqual(fraction_rank(V),len(V))
                self.assertTrue(all(frames.dot(a,b) == 0 for a in U for b in V))
        with self.assertRaises(ValueError):
            frames.orthogonal(((1,)+(0,)*8,),9)


if __name__ == '__main__':
    unittest.main()
