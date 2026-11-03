"""Regression checks for explicit payload-bound and bounded-candidate arithmetic."""
from fractions import Fraction as F
from collections import Counter
import unittest
import reproduce_pr275 as base
import review_payload_cap as cap
from integrate_bounded_candidate import invoice

class BoundedCandidateTests(unittest.TestCase):
    def test_old_cap_failure_is_explicit(self):
        r=cap.run()
        self.assertFalse(r['original_cap_satisfied'])
        self.assertTrue(r['explicit_candidate_cap_satisfied'])
        self.assertEqual(r['payload_bits'],110)
        self.assertEqual(r['explicit_candidate_cap_bits'],112)
        self.assertEqual(len(r['proof_source_bindings']),8)

    def test_too_large_payload_rejected(self):
        with self.assertRaises(AssertionError):cap.run(10**20,10**20,112)

    def test_no_silent_legacy_cap_relaxation(self):
        with self.assertRaises(AssertionError):cap.run(new_bits=104)

    def test_every_declared_delta_conserves_deficit(self):
        for size,h in [(136,{1:170,2:236,3:-236,4:70,5:-70}),
                       (176,{1:229,2:335,3:-335,4:70,5:-70}),
                       (164,{1:223,2:324,3:-324,4:63,5:-63}),
                       (166,{1:210,2:306,3:-306,4:70,5:-70})]:
            self.assertEqual(base.mass(h),-size)
            self.assertEqual(F(120*(-5*size//2),60),5*base.mass(h))

    def test_line136_displayed_invoice_charges_all_shears(self):
        r=invoice(1229395,482950,2*2477)
        self.assertEqual(r['gross_added_scalar_events_per_stage'],4954)
        self.assertEqual(r['unit_additions_upper'],219601200)
        self.assertEqual(r['selector_calls_bound'],905876636400)
        self.assertLess(r['displayed_finite_coefficient'],2**80)

    def test_exact_candidate_comparison_exponent(self):
        gap=F('0.000751091445301206')-F('0.000751090249287618')
        self.assertEqual(gap,F(299003397,250000000000000000))
        self.assertGreater(gap,F(1,10**9))
        self.assertLess(gap,F(2,10**9))

    def test_best_bounded_candidate_endpoint_signs(self):
        h,_=base.final_profile();h.update({r:5*n for r,n in {1:210,2:306,3:-306,4:70,5:-70}.items()})
        W=F(1229320,60);a=F(751662295432463,10**18)
        self.assertLess(base.moment(h,120,W,a)[1],1)
        self.assertGreater(base.moment(h,120,W,a+F(1,10**18))[0],1)
        self.assertEqual(base.assembly(a)['kappa'],F('0.000751097723288767'))

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions required')
    unittest.main()
