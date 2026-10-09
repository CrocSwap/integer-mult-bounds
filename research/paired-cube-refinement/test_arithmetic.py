"""Fail-closed controls for supplied frame plans and paid fallback accounting."""
import copy
from fractions import Fraction as Q
import json
import importlib.util
from pathlib import Path
import tempfile
import unittest

from paid_moment import ROOT,envelope,validate_envelope,profile
from plan_validation import validate_plan
from arithmetic import baseline_complex_profile,bridge,validate_bridge,assembly,AC


class AccountingControls(unittest.TestCase):
    def test_prime_factor_proof_not_determinant_size(self):
        source=ROOT/'research/paired-cube-bit-descent/prime_check.py'
        spec=importlib.util.spec_from_file_location('prime_factor_control',source)
        checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
        with tempfile.TemporaryDirectory(prefix='paired-prime-controls-') as temporary:
            path=Path(temporary)/'plan.json'
            def check(vector):
                path.write_text(json.dumps(dict(p=12,frames=[[0,[vector]]])))
                return checker.certificate(path)
            good=check([2**50]+[0]*23)
            self.assertGreater(good['maximum_determinant_bits'],80)
            self.assertEqual(good['frame_witnesses'][0]['residual'],1)
            with self.assertRaises(AssertionError):check([1]*9+[0]*15)
            with self.assertRaises(AssertionError):check([2**89-1]+[0]*23)

    def test_derived_envelope_rejects_underbilling(self):
        bill=envelope(72)
        self.assertEqual(bill["fallback_children_per_edge"],124842)
        self.assertEqual(bill["bad_fraction"],Q(729,1180591620717411303424))
        cases={"missing reversals":("fallback_children_per_edge",124841),
               "understated rare class":("bad_fraction",bill["bad_fraction"]-Q(1,10**30)),
               "changed prime range":("prime_lower_bound_exclusive",2**81),
               "same-valued float":("fallback_children_per_edge",124842.0),
               "stale theorem":("source_sha256","0"*64)}
        for name,(key,value) in cases.items():
            bad=copy.deepcopy(bill);bad[key]=value
            with self.subTest(name=name),self.assertRaises(ValueError):validate_envelope(bad,72)

    def test_omitted_ideal_child_rejected(self):
        row=json.loads((ROOT/"research/paired-cube-bit/out/profile_p12.json").read_text())
        profile(row);row["child_histogram"]["1"]-=1
        with self.assertRaises(ValueError):profile(row)

    def test_plan_shapes_rejected_before_indexing(self):
        valid=dict(p=12,frames=[[0,[[1]+[0]*23]],[2,[[0,1]+[0]*22]]])
        validate_plan(valid,4)
        cases={"duplicate":lambda x:x["frames"].insert(0,copy.deepcopy(x["frames"][0])),
               "negative":lambda x:x["frames"][0].__setitem__(0,-1),
               "boolean index":lambda x:x["frames"][0].__setitem__(0,False),
               "out of range":lambda x:x["frames"][1].__setitem__(0,4),
               "empty basis":lambda x:x["frames"][0].__setitem__(1,[]),
               "noninteger coordinate":lambda x:x["frames"][0][1][0].__setitem__(0,1.0)}
        for name,mutate in cases.items():
            bad=copy.deepcopy(valid);mutate(bad)
            with self.subTest(name=name),self.assertRaises(ValueError):validate_plan(bad,4)

    def test_transfer_rejects_unsupported_supplier(self):
        row=baseline_complex_profile();coarse=Q(6105820,10**10);atom=Q(1,1000)
        finite=bridge(row,coarse,atom)
        validate_bridge(finite,row)
        bad=copy.deepcopy(finite);bad["bit_uniform"]["ordinary_saving"]+=Q(1,10**24)
        with self.assertRaises(ValueError):validate_bridge(bad,row)
        with self.assertRaises(ValueError):assembly(finite,row,finite["bit_uniform"]["ordinary_saving"]+Q(1,10**24),Q(609,10**6))

    def test_full_finite_bridge_reproduces_published_numbers(self):
        old=json.loads((ROOT/"certificates/paired-cube-network.json").read_text())["finite_bridge"]
        row=baseline_complex_profile()
        actual=bridge(row,Q(6105820,10**10),Q(1,1000))
        for section in ("bit_uniform","complex","semantic","rows"):
            for key,value in actual[section].items():
                if key in old[section]:
                    with self.subTest(section=section,key=key):self.assertEqual(value,Q(old[section][key]))


if __name__=="__main__":unittest.main()
