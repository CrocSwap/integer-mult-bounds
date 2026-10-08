"""Adversarial controls for the pair-assembly producer (adapted from test_skip_strips.py, PR #53, and test_copied_fixed.py, PR #43/#48)."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import importlib.util
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'research/pair-assembly'
spec=importlib.util.spec_from_file_location('pair_assembly_verify',HERE/'verify.py')
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class PairAssemblyTests(unittest.TestCase):
    def test_frozen_certificate(self):
        self.assertEqual(v.js(v.run()),v.read(HERE/'certificate.json'))

    def test_all_strict_constraints_and_dyadic_bracket(self):
        result=v.run()
        a=result['assembly']
        self.assertEqual(len(a['constraints']),47)
        self.assertEqual(len(a['margins']),7)
        self.assertTrue(all(x>0 for x in a['constraints'].values()))
        self.assertGreater(v.KAPPA,Q(1,2**15))
        self.assertLess(v.KAPPA,Q(1,2**14))

    def test_independent_cost_rows(self):
        result=v.run();a=result['assembly'];p=a['parameters']
        e,c,r,delta=p['epsilon'],p['c'],p['alpha_squared_power'],p['delta']
        costs=[e,p['tau'],1-e*(1-p['lambda_prime']),p['tau'],
               max(e+delta,1-r+delta),e+delta,1-e]
        self.assertEqual([1-x for x in costs],list(a['margins'].values()))
        self.assertTrue(all(1-x>v.KAPPA for x in costs))
        self.assertEqual(p['q'],v.AB*(1-2*p['h']))
        self.assertEqual(a['margins']['g1']-a['minimum_margin'],p['h'])

    def test_real_lower_bound_exclusions(self):
        result=v.run()
        self.assertGreater(result['controls']['old_bit_at_new_lower'],1)
        self.assertGreater(result['controls']['PR40_bit_at_new_lower'],1)
        self.assertGreater(result['controls']['PR41_bit_at_new_lower'],1)
        self.assertGreater(result['controls']['PR42_bit_at_new_lower'],1)
        self.assertGreater(result['controls']['PR43_bit_at_new_lower'],1)
        self.assertGreater(result['controls']['PR44_bit_at_new_lower'],1)
        self.assertGreater(result['controls']['PR46_bit_at_new_lower'],1)
        self.assertGreater(result['controls']['PR47_bit_at_new_lower'],1)
        self.assertGreater(result['controls']['PR48_bit_at_new_lower'],1)
        self.assertGreater(result['controls']['PR53_bit_at_new_lower'],1)
        self.assertGreater(result['controls']['PR54_bit_at_new_lower'],1)
        self.assertGreater(result['controls']['PR57_bit_at_new_lower'],1)

    def test_recovery_and_every_pair_charged(self):
        c=v.data_corners()
        self.assertEqual((c['good'],c['fallback'],c['pairs']),(4073300,0,4073300))
        p=v.profile();data=p['parts']['data']
        self.assertEqual(data[1],2*(9*c['good']+47*c['fallback']))
        self.assertEqual(data[21],2*c['good'])
        self.assertEqual(data[17],2*c['good'])
        self.assertEqual(sum(t*n for t,n in data.items()),2*p['N']*528)

    def test_pair_assembly_reduces_physical_roles(self):
        p=v.profile()
        self.assertEqual([axis['original']['R'] for axis in p['axes']],[28719,37676])
        self.assertEqual([axis['original']['matched'] for axis in p['axes']],[38911,55844])
        # PR #53 had R=(32946,43409) and W=160799739.
        self.assertEqual(p['W'],160799739-(32946-28719)*2300-(43409-37676)*1771)
        self.assertEqual(p['deficit'],1846900)

    def test_interval_layout_is_exact_leave_one_out(self):
        import pair_graph
        class Adder:
            support={}
            def add(self,a,b):
                if not a: return b
                if not b: return a
                assert not a&b, 'cancellation'
                return a|b
        c=Adder()
        layouts=(pair_graph.interval_layout(pair_graph.skip_prefix),pair_graph.skip_prefix,pair_graph.prefix_suffix,
                 pair_graph.reversed_layout(pair_graph.interval_layout(pair_graph.skip_prefix)))
        for k in range(1,14):
            vals=[1<<i for i in range(k)]
            full=(1<<k)-1
            for layout in layouts:
                total,out=layout(c,vals)
                self.assertEqual(total,full)
                self.assertEqual(out,[full^(1<<j) for j in range(k)])

    def test_every_short_interval_has_a_containing_consumer(self):
        # I(a,m)=I(a,m-1)+v_(a+m-1); the next interval I(a-1,m+1) consumes the
        # same item v_(a+m-1) and contains I(a,m), for every m < k-1.
        import pair_graph
        for k in range(3,13):
            splits={S:(L,R) for S,L,R in pair_graph.interval_splits(k)}
            full=(1<<k)-1
            for S,(L,R) in splits.items():
                if S==full or S.bit_count()==k-1:
                    continue
                consumers=[T for T,(L2,R2) in splits.items() if T!=S and R in (L2,R2) and not S&~T]
                self.assertTrue(consumers, (k,S))

    def test_pair_assembly_outputs_and_nesting(self):
        # Symbolic check of the eight-addition assembly: exact outputs, and
        # each F+S node has a later consumer of its strip operand containing it.
        F,Sa,Sa2,Sb,Sb2=1,2,4,8,16
        e={('a2','b2'):32,('a2','b'):64,('a','b2'):128,('a','b'):256}
        FSa,FSa2,FSb,FSb2=F|Sa,F|Sa2,F|Sb,F|Sb2
        Y1,Y2,Y3,Y4=FSb|Sa,FSa|Sb2,FSa2|e['a','b2'],FSb2|e['a','b']
        outs={('a','b'):e['a2','b2']|Y1,('a','b2'):e['a2','b']|Y2,('a2','b'):Y3|Sb,('a2','b2'):Y4|Sa2}
        self.assertEqual(outs[('a','b')],F|Sa|Sb|e['a2','b2'])
        self.assertEqual(outs[('a','b2')],F|Sa|Sb2|e['a2','b'])
        self.assertEqual(outs[('a2','b')],F|Sa2|Sb|e['a','b2'])
        self.assertEqual(outs[('a2','b2')],F|Sa2|Sb2|e['a','b'])
        for donor,target in ((FSa,Y1),(FSb2,Y2),(FSb,outs[('a2','b')]),(FSa2,outs[('a2','b2')])):
            self.assertFalse(donor&~target)

    def test_pinned_links_use_distinct_donors_and_uses(self):
        import struct
        raw=(HERE/'links-23.uses').read_bytes()
        n,count=struct.unpack_from('<2I',raw)
        pairs=list(struct.iter_unpack('<2I',raw[8:]))
        self.assertEqual(count,len(pairs))
        self.assertEqual(len({d for d,_ in pairs}),count)
        self.assertEqual(len({u for _,u in pairs}),count)

    def test_exact_recovery_explains_primary_modular_failures(self):
        c=v.data_corners();prime=c['prime']
        self.assertEqual((c['primary_good'],c['primary_fallback']),(4073290,10))
        self.assertEqual(len(c['exact_recovery']),10)
        for row in c['exact_recovery']:
            self.assertEqual(len(row['pivots']),47)
            self.assertEqual(row['ordered_zero_checks'],346)
            for i,value in enumerate(row['pivots']):
                q=Q(value)
                self.assertNotEqual(q,0)
                if i<=row['primary_failed_row']:
                    self.assertNotEqual(q.denominator%prime,0)
                    self.assertEqual(q.numerator%prime==0,i==row['primary_failed_row'])

    def test_zero_recovered_pivot_rejected(self):
        import data_recovery
        bad=deepcopy(v.data_corners()['exact_recovery']);bad[0]['pivots'][0]='0'
        with patch.object(data_recovery,'recover',return_value=bad):
            with self.assertRaisesRegex(ValueError,'Incomplete rational pivot proof'):v.data_corners()

    def test_corrupted_pair_coverage_rejected(self):
        original_read=v.read
        def corrupt(path):
            result=deepcopy(original_read(path))
            if path.name=='data-corners.json':result['records'][0][3]-=1
            return result
        with patch.object(v,'read',side_effect=corrupt):
            with self.assertRaisesRegex(ValueError,'Pair coverage gap'):v.data_corners()

    def test_mass_corruption_rejected(self):
        original_read=v.read
        def corrupt(path):
            result=deepcopy(original_read(path))
            if path.name=='profiles-23.json':result['blocks'][1]+=1
            return result
        with patch.object(v,'read',side_effect=corrupt):
            with self.assertRaisesRegex(ValueError,'Fixed profile mass'):v.profile()

    def test_omitted_paid_copy_detected(self):
        p=v.profile();rows=p['child_multiplicities'].copy()
        rows[1]-=p['N']
        self.assertNotEqual(sum(t*n for t,n in rows.items()),p['total_rank'])
        self.assertEqual(sum(t*n for t,n in p['parts']['paid_endpoint_copy'].items()),4073300)

    def test_mismatched_source_hash_rejected(self):
        original_read=v.read
        def corrupt(path):
            result=deepcopy(original_read(path))
            if path.name=='SOURCE.json':result['files']['scripts/copied_centers_network.py']='0'*64
            return result
        with patch.object(v,'read',side_effect=corrupt):
            with self.assertRaisesRegex(ValueError,'Pinned source changed'):v.check_sources()

    def test_assembly_boundary_rejected(self):
        result=v.run()
        with self.assertRaises(AssertionError):
            v.assembly(result['finite_bridge'],v.AB,result['assembly']['minimum_margin'],a_complex=v.AC)

    def test_balanced_transfer_negative_controls(self):
        r=v.run()
        for kw in ({'original_prefix':True},{'old_guard':True},{'old_exposures':True}):
            with self.assertRaises(AssertionError):
                v.assembly(r['finite_bridge'],v.AB,v.KAPPA,a_complex=v.AC,**kw)

    def test_float_saving_rejected(self):
        with self.assertRaises(ValueError):v.moment(2,2,{1:1},0.01)

    def test_restriction_tree_mutation_rejected(self):
        g=v.geometry();edges=g['row_tree'][:];edges[-1]=edges[0]
        with self.assertRaises(ValueError):v.tree(edges,48)

    def test_stacked_frame_certificate(self):
        cert=v.read(HERE/'frame/frame-certificate.json')
        self.assertEqual(cert['kappa'],'5101691/100000000000')
        self.assertGreater(Q(cert['kappa']),v.KAPPA)
        self.assertEqual(cert['bit']['W'],137151806)
        self.assertEqual(len(cert['assembly']['constraints']),47)
        self.assertTrue(cert['comparison']['next_kappa_grid_fails'])

    def test_deterministic_prime_and_minor_gaps(self):
        for h in (23,25):
            e=v.exactness(h)
            self.assertTrue(all(x>0 for x in e['modulus_gaps'].values()))
            self.assertEqual(e['prime_product'],2596143476298333157846630848266239)


if __name__=='__main__':unittest.main()
