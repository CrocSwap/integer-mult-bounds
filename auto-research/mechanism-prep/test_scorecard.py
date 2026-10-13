"""Controls for the preparation pass's arithmetic and scoped specifications."""
from collections import Counter
from fractions import Fraction as Q
import unittest
from scorecard import design_envelope,envelope_residual,log_bounds,moment,profile_score


class MechanismControls(unittest.TestCase):
    def test_log_enclosures_and_rescaling(self):
        self.assertEqual(log_bounds(1),(Q(0),Q(0)))
        lo,hi=log_bounds(2)
        # A separate slower unscaled series gives an enclosing comparison.
        z=Q(1,3)
        ref=2*sum((z**(2*j+1)/Q(2*j+1) for j in range(40)),Q(0))
        tail=2*z**81/(81*(1-z*z))
        self.assertLessEqual(lo,ref)
        self.assertGreaterEqual(hi,ref+tail)
        a,b=log_bounds(8)
        self.assertLessEqual(a,3*hi)
        self.assertGreaterEqual(b,3*lo)

    def test_width_distribution_matters_at_equal_rank_mass(self):
        fine=profile_score({1:8},16,1)
        coarse=profile_score({8:1},16,1)
        self.assertEqual(fine['rank_deficit'],coarse['rank_deficit'])
        self.assertGreater(fine['log_width_penalty_coefficient_interval'][0],
                           coarse['log_width_penalty_coefficient_interval'][1])
        self.assertGreater(fine['target_moment_interval'][0],coarse['target_moment_interval'][1])

    def test_affine_budget_matches_direct_profile(self):
        e=design_envelope(12,16)
        rhos=[Q(3,2),Q(2)];losses=[Q(1,10),Q(1,5)]
        rows=Counter(e['data_profile_per_pair']);m=e['m'];W=2+sum(rhos)
        for d,r,l in zip(e['dimensions'],rhos,losses):
            rows[d]+=r+l/d;rows[m-d]+=r
        direct=moment(rows,m,W);gap=envelope_residual(e,rhos,losses)
        self.assertLessEqual(gap[0],W*(1-direct[0]))
        self.assertGreaterEqual(gap[1],W*(1-direct[1]))

    def test_current_geometry_fails_even_at_rank_storage_floor(self):
        e=design_envelope(23,25)
        self.assertLess(envelope_residual(e,[1,1],[0,0])[1],0)
        self.assertLess(e['equal_role_ratio_ceiling_with_zero_loss_interval'][1],1)
        self.assertLess(e['equal_loss_ratio_ceiling_with_one_role_per_label_interval'][1],0)

    def test_improved_optimistic_budget_is_not_a_construction_claim(self):
        e=design_envelope(12,12)
        self.assertGreater(envelope_residual(e,[1,1],[Q(1,10)]*2)[0],0)
        self.assertIn('Necessary optimistic',e['scope'])
        with self.assertRaises(ValueError): envelope_residual(e,[-1,1],[0,0])
        with self.assertRaises(ValueError): profile_score({144:1},144,2)


if __name__=='__main__':unittest.main()
