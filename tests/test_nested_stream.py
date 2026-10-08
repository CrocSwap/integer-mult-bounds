"""Cross-interface regressions for the h30 nested-stream composition."""
from pathlib import Path
from fractions import Fraction as Q
from dataclasses import replace
import importlib.util, unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('nested_stream_verify',ROOT/'research/nested-stream/verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

class NestedStreamTests(unittest.TestCase):
    def test_block_profile_and_rank_conservation(self):
        n=v.bit.counts(v.H,v.ROLES);B=n['v']**2*v.ROLES;N=n['N']
        expected={26880:B,26940:B,25142:2*N,782:2*N,842:2*N,30:B}
        self.assertEqual({x['chunk_digits']:x['copies'] for x in n['recursive_blocks']},expected)
        self.assertEqual(n['singleton_calls']+sum(a*b for a,b in expected.items()),n['original_rank_sum'])
        self.assertEqual(n['W']*n['m']-n['original_rank_sum'],N-2*n['decreasing_dimension'])
    def test_geometric_savings_are_required(self):
        for change in (dict(nested=False),dict(roles=17515487)):
            args=dict(a=v.BIT_SAVING,h=v.H,roles=v.ROLES);args.update(change)
            with self.assertRaises(AssertionError):v.bit.certificate(**args)
    def test_claimed_moment_and_rounded_failure(self):
        b=v.bit.certificate(a=v.BIT_SAVING,h=v.H,roles=v.ROLES)
        self.assertGreater(b['strict_gap'],Q(19,10**15))
        with self.assertRaises(AssertionError):v.bit.certificate(a=v.BIT_SAVING+Q(1,10**12),h=v.H,roles=v.ROLES)
    def test_final_interface_and_failure(self):
        w=v.assembly();self.assertEqual(len(w['constraints']),29);self.assertEqual(len(w['margins']),7)
        self.assertGreater(w['absorption_gap'],0)
        self.assertGreater((1-v.parameters().beta)*v.COMPLEX_SAVING,v.BIT_SAVING)
        with self.assertRaises(AssertionError):v.assembly(replace(v.parameters(),kappa=Q(125,10**8)))
    def test_one_nested_basis_and_bad_shared_inner_basis(self):
        result=v.controls.run_one(4,191400)
        self.assertEqual(len(result['profiles']),8)
        self.assertEqual(v.controls.run_one(4,191400,same_inner=True)['rejected_condition'],'A1 corner loses required rank')

if __name__=='__main__':unittest.main()
