"""Independent separate-bank trace followed by the exact bank-sharing change."""
from collections import Counter
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from paired_complex import PairedComplex
from complex_circuit import Checks,compile_roles,verify_role_frames
from experiments import assembly_breakthrough_guard as old
from experiments.complex_all_residuals import counts


def independent_histogram(h,shared=True):
    """Use the older three-separate-bank schedule, then join only endpoints."""
    captured=[]
    class Traced(old.PathAudit):
        def __init__(self,dimensions):
            super().__init__(dimensions)
            self.histogram=Counter()
            captured.append(self)
        def gate(self,name,roles,dimension):
            roles=tuple(set(roles))
            self.histogram.update(abs(dimension-self.dim[r]) for r in roles
                                  if dimension!=self.dim[r])
            return super().gate(name,roles,dimension)
    c=PairedComplex(h);checks=Checks(c);code=compile_roles(c)
    dimensions={node:checks.label(node).dim for node in c.active}
    with patch.object(old,'PathAudit',Traced):
        for stage,inverse in ((1,False),(2,True),(3,False)):
            old.invocation(c,code,dimensions,stage,inverse)
    histogram=sum((trace.histogram for trace in captured),Counter())
    r=code['roles']+h+1;m=h**3;v=len(c.triples)
    if shared:
        # Old stage1 exit h->m and stage3 entry 0->m-h become h->m-h.
        # The complete bank includes every central role exactly once.
        histogram[m-h]-=2*r
        assert histogram[m-h]>=0
        histogram[m-2*h]+=r
    return ({rank:copies*v*v for rank,copies in sorted(histogram.items()) if copies},
            c,checks,code)


class IndependentComplexHistogram(unittest.TestCase):
    def test_all_small_physical_residual_ranks_match(self):
        for h in (8,10):
            histogram,c,checks,code=independent_histogram(h)
            self.assertEqual(histogram,counts(h)['residual_histogram'])
            self.assertTrue(checks.verify_labels()['all_residuals_have_odd_vectors'])
            self.assertTrue(verify_role_frames(c,checks,code)['reverse_complement_frames_nested'])

    def test_unshared_bank_has_exactly_one_extra_full_bank_rank_mass(self):
        h=8
        unshared,c,checks,code=independent_histogram(h,shared=False)
        shared=counts(h)
        extra=sum(rank*copies for rank,copies in unshared.items())-shared['s']
        self.assertEqual(extra,len(c.triples)**2*(code['roles']+h+1)*h**3)
        self.assertNotEqual(unshared,shared['residual_histogram'])


if __name__=='__main__': unittest.main()
