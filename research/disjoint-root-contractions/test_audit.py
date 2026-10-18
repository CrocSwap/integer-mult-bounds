"""Failure controls and independent dirty-column checks for the new recipe."""
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import audit
from circuit import RootContraction, recurrence_cost, feasible_channels
from experiments.disjoint_tensor import DisjointTensor, scalar_program
from complex_compression import invoke
sys.path.insert(0,str(audit.ROOT/'tests'))
from test_complex_compression import Linear

class RootContractionTests(unittest.TestCase):
    def test_complete_search_domain(self):
        self.assertEqual([len(feasible_channels(22,l)) for l in range(1,12)],
                         [3,6,10,13,15,16,16,16,16,16,16])
        self.assertEqual(11+sum(len(feasible_channels(22,l)) for l in range(1,12)),154)

    def test_infeasible_recipe_rejected(self):
        for args in [(22,0,None),(22,12,None),(22,1,(1,1)),(9,4,None),
                     (22,11,(4,4))]:
            with self.subTest(args=args),self.assertRaises(ValueError):RootContraction(*args)

    def test_adapter_reproduces_baseline(self):
        for h in (8,10,22):
            from experiments.disjoint_tensor import plan
            original=DisjointTensor(h); adapted=RootContraction(h,plan(h,3,3)[1])
            expected=audit.expected_map(h)
            self.assertEqual(audit.verify_dag(original,expected),audit.verify_dag(adapted,expected))

    def test_same_recurrence_different_paid_count(self):
        baseline=RootContraction(22,11);best=RootContraction(22,11,(1,1))
        self.assertEqual(recurrence_cost(22,11),39900)
        self.assertEqual(recurrence_cost(22,11,(1,1)),39900)
        self.assertEqual((baseline.additions,best.additions),(31929,30708))
        self.assertEqual(baseline.compile()['roles']-best.compile()['roles'],1221)

    def test_corrupt_coefficients_rejected(self):
        c=RootContraction(8,4,(1,1));t=next(iter(c.outputs));c.outputs[t]=1
        with self.assertRaisesRegex(ValueError,'wrong output'):audit.verify_dag(c,audit.expected_map(8))
        c=RootContraction(8,4,(1,1));node=next(n for n in sorted(c.active) if c.args[n])
        c.support[node]^=1
        with self.assertRaisesRegex(ValueError,'wrong node'):audit.verify_dag(c,audit.expected_map(8))

    def test_overlapping_and_cyclic_additions_rejected(self):
        for mutation in ('overlap','cycle'):
            c=RootContraction(8,4,(1,1));node=next(n for n in sorted(c.active) if c.args[n])
            a,b=c.args[node];c.args[node]=(a,a) if mutation=='overlap' else (a,node)
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):
                audit.verify_dag(c,audit.expected_map(8))

    def check_formal(self,h,mutate=None):
        code=scalar_program(RootContraction(h,h//2,(1,1)))
        if mutate=='omit_copy': code['sources']=code['sources'][1:]
        if mutate=='wrong_injection':
            i,s,w=code['outputs'][0];code['outputs'][0]=(i,s,-w)
        v=len(code['triples']);sizes=[v,v,code['roles'],h+1]
        for inverse in (False,True):
            values=[Linear({i:1}) for i in range(sum(sizes))]
            banks=[];offset=0
            for size in sizes:banks.append(values[offset:offset+size]);offset+=size
            old=[list(b) for b in banks]
            invoke(*banks,code,inverse=inverse)
            self.assertEqual(banks[0],old[0]);self.assertEqual(banks[2:],old[2:])
            sign=-1 if inverse else 1
            self.assertEqual(banks[1],[b+sign*a for a,b in zip(old[0],old[1])])
        return 2*sum(sizes)

    def test_all_independent_dirty_columns_small(self):
        for h in (8,10):self.check_formal(h)

    def test_omitted_source_access_and_wrong_injection_detected(self):
        for mutate in ('omit_copy','wrong_injection'):
            with self.subTest(mutate=mutate),self.assertRaises(AssertionError):self.check_formal(8,mutate)

    def test_cost_saving_includes_all_four_mixers(self):
        old=audit.invoice(RootContraction(22,11));new=audit.invoice(RootContraction(22,11,(1,1)))
        self.assertEqual(old['complete_signed_invocation_bound']-new['complete_signed_invocation_bound'],9768)
        self.assertEqual(old['three_stage_scalar_bound']-new['three_stage_scalar_bound'],69497366400)
        self.assertEqual(old['counts']['deficit'],new['counts']['deficit'])
        self.assertEqual(old['source_accesses'],new['source_accesses'])
        self.assertEqual(old['weighted_injections'],new['weighted_injections'])

if __name__=='__main__':unittest.main()
