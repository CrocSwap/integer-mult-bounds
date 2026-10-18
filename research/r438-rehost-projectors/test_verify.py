#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Focused exact checks independent of the sparse projector application."""
from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('r438_projectors',HERE/'verify.py')
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class ProjectorTests(unittest.TestCase):
    def test_dense_rational_operator(self):
        # An independently assembled 16 by 16 block matrix checks every basis
        # column for coordinate and noncoordinate roots, including half entries.
        for q in ([2,0,0,0,0,0,0,0],[1,1,1,1,0,0,0,0],[0,0,1,-1,0,1,-1,0]):
            k=[[Q(i==j)-Q(q[i]*q[j],4) for j in range(8)] for i in range(8)]
            d=[[((Q(i%8==j%8)-k[i%8][j%8]) if i//8==j//8 else k[i%8][j%8])
                for j in range(16)] for i in range(16)]
            for col in range(16):
                e=tuple(Q(j==col) for j in range(16))
                self.assertEqual(v.low_apply(e,q,True),tuple(row[col] for row in d))
                self.assertEqual(v.low_apply(v.low_apply(e,q,True),q,True),e)

    def test_equal_rank_is_not_operator_equality(self):
        q=[1,1,1,1,0,0,0,0]
        p=[1,1,-1,-1,0,0,0,0]
        e=tuple(Q(i==0) for i in range(16))
        self.assertNotEqual(v.low_apply(e,q,True),v.low_apply(e,p,True))

    def test_rank34_partition_and_corruption(self):
        whole=v.pending(2,8)
        head=sum(1<<i for i in range(22,30))
        rest=sum(1<<i for i in range(30,64))
        self.assertEqual((head.bit_count(),rest.bit_count()),(8,34))
        v.factorization([head,rest],whole)
        with self.assertRaisesRegex(v.Rejected,'wrong pending operator'):
            v.factorization([head,rest^(1<<30)^(1<<8)],whole)

    def test_overlap_cancellation_is_not_partition(self):
        whole=v.pending(-1,0)
        with self.assertRaisesRegex(v.Rejected,'overlapping factors'):
            v.factorization([whole,whole],whole)
        # Direct matrix action makes the cancellation explicit on a dirty vector.
        q=[2,0,0,0,0,0,0,0]
        e=tuple(Q(i==1) for i in range(16))
        once=v.low_apply(e,q,True)
        self.assertNotEqual(e,once)
        self.assertEqual(v.low_apply(once,q,True),e)

    def test_source_chronology(self):
        v.source_check()
        _,children,windows=v.chronology()
        self.assertEqual([(c['source_level'],c['target_level']) for c in children],
                         [(-1,1),(1,2),(-1,3),(3,4),(-1,5),(5,6),(2,8),(4,8),(6,8),(8,8)])
        self.assertEqual(windows[6][2],frozenset(range(3,9)))
        self.assertEqual(children[-1]['mask'],0)


if __name__=='__main__':
    unittest.main()
