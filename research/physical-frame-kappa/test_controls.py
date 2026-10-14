#!/usr/bin/env python3
"""Independent small-space and adversarial ledger controls."""
import copy
import json
import unittest
from fractions import Fraction as Q
from pathlib import Path
from lift115 import basis, nondeg, perp
from optimize_frames import minimum, intersection, inside
from verify import validate
import certificate

HERE=Path(__file__).resolve().parent

class Controls(unittest.TestCase):
    def test_radical_completion_all_subspaces_through_dimension_four(self):
        for h in range(1,5):
            spaces={()};front=[()]
            while front:
                A=front.pop()
                for v in range(1,1<<h):
                    B=basis(A+(v,))
                    if B not in spaces:spaces.add(B);front.append(B)
            for C in spaces:
                if not nondeg(C):continue
                for L in spaces:
                    if not inside(L,C):continue
                    A=minimum(L,C,h)
                    self.assertTrue(nondeg(A) and inside(L,A) and inside(A,C))
                    self.assertEqual(len(A),len(L)+len(intersection(L,perp(L,h),h)))

    def test_previous_profile_does_not_contract_at_new_saving(self):
        old=json.loads((HERE/'references/pr118/complex-profile.json').read_text())
        old['child_multiplicities']={int(t):c for t,c in old['child_multiplicities'].items()}
        self.assertFalse(certificate.contracts(old,certificate.COMPLEX))

    def test_missing_endpoint_and_retained_copy_charges_rejected(self):
        original=json.loads((HERE/'complex-profile.json').read_text())
        for rank,amount in ((1,original['N']),(23,2*original['v']*24)):
            changed=copy.deepcopy(original)
            changed['child_multiplicities'][str(rank)]-=amount
            with self.assertRaisesRegex(AssertionError,'rank mass'):validate(changed)

    def test_nonshrinking_child_rejected(self):
        changed=json.loads((HERE/'complex-profile.json').read_text())
        changed['child_multiplicities'][str(changed['m'])]=1
        with self.assertRaisesRegex(AssertionError,'child range'):validate(changed)

    def test_next_moment_grid_points_rejected(self):
        for name,a,step in [('bit-profile.json',certificate.COARSE,Q(1,10**10)),
                            ('complex-profile.json',certificate.COMPLEX,Q(1,10**12))]:
            self.assertFalse(certificate.contracts(certificate.profile(name),a+step))

if __name__=='__main__':unittest.main(verbosity=2)
