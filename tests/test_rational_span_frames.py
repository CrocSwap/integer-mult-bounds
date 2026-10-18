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

    def test_primitive_against_scalar_gcd_reference(self):
        from math import gcd
        rng = random.Random(239619)
        rows = [(), (0,0), (True,False), (False,True),
                (-(2**127),2**129,0), (2**521-1,2**127-1,0)]
        rows += [tuple(rng.randrange(-100,101) for _ in range(h))
                 for h in range(15) for _ in range(32)]
        for row in rows:
            g = 0
            for value in row:
                g = gcd(g,value)
            if g and next(value for value in row if value) < 0:
                g = -g
            expected = tuple(value//g for value in row) if g else None
            self.assertEqual(frames.primitive(row), expected)
        for row in ((1,2.0), (1,"2"), (1,Fraction(2,1))):
            with self.assertRaises(TypeError):
                frames.primitive(row)

    def test_complements_against_explicit_ambient_form(self):
        from unittest.mock import patch
        rng = random.Random(6194534)
        for h in (1,2,4,6,8,10,12,14):
            for d in range(h+1):
                for _ in range(3):
                    U = tuple(tuple(rng.randrange(-3,4) for _ in range(h))
                              for _ in range(d))
                    if fraction_rank(U) != d:
                        continue
                    V = frames.orthogonal(U,h)
                    self.assertEqual(len(V),h-d)
                    self.assertEqual(fraction_rank(V),h-d)
                    for a in U:
                        for b in V:
                            self.assertEqual(9*sum(x*y for x,y in zip(a,b))
                                             -sum(a)*sum(b),0)
        U = ((1,)*9+(0,),)
        V = frames.orthogonal(U,10)
        self.assertEqual(len(V),9)
        self.assertTrue(all(9*sum(x*y for x,y in zip(U[0],b))
                            -sum(U[0])*sum(b) == 0 for b in V))
        with self.assertRaises(ValueError):
            frames.orthogonal(((1,0),(2,0)),2)
        with self.assertRaises(ValueError):
            frames.orthogonal(((1,0),),3)
        U = ((1,0,0,0),(0,1,0,0),(0,0,1,0))
        for forged in ((), ((1,0,0,0),)):
            frames.orthogonal.cache_clear()
            with patch.object(frames, '_kernel_basis', return_value=forged):
                with self.assertRaises(ValueError):
                    frames.orthogonal(U,4)
        frames.orthogonal.cache_clear()

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
