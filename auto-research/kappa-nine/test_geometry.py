"""Independent finite controls for the two block-label experiments."""
from fractions import Fraction as Q
import unittest
from block_fano_obstruction import audit as fano_audit, determinant_mod, fano_planes, clique_incidence
from covariant_block_test import audit as covariant_audit, pieces, mul, rank, quotient_commutant
from geometry_screen import subset_axis, optimistic_pair, signed_rank


class GeometryControls(unittest.TestCase):
    def test_fano_certificate_and_destroyed_rank(self):
        d=fano_audit()
        self.assertEqual(d['rows_available'],1080)
        self.assertEqual(d['columns'],84)
        self.assertNotEqual(d['determinant_mod_prime'],0)
        triples,rows,_=clique_incidence()
        A=[rows[i].copy() for i in d['selected_row_indices']]
        A[-1]=A[0].copy()
        self.assertEqual(determinant_mod(A,101),0)

    def test_rank_two_headroom_does_not_imply_geometry(self):
        d=fano_audit()
        first=d['optimistic_budget_table'][0]
        self.assertLess(first['moment_interval'][1],1)
        self.assertNotEqual(d['idempotent_residual'],0)

    def test_covariance_rejection_and_nonadjacent_control(self):
        d=covariant_audit()
        self.assertEqual(d['cross_product_rank'],1)
        for h in (7,9,16):
            self.assertEqual(rank(quotient_commutant(h)),3)
            A=pieces(h,(0,1,2))[0];B=pieces(h,(3,4,5))[0]
            self.assertEqual(rank(mul(A,B)),0)
            C=pieces(h,(0,3,4))[0]
            self.assertEqual(rank(mul(A,C)),1)

    def test_subset_best_relaxation_still_rejected(self):
        row=optimistic_pair(subset_axis(24,4),subset_axis(24,4))
        self.assertTrue(row['target_excluded'])
        self.assertGreater(row['free_role_constant'][0],1)

    def test_signed_rank_small_exact_controls(self):
        for h,q,n,r in ((4,4,8,2),(5,4,40,10),(8,8,128,16)):
            result=signed_rank(h,q)
            self.assertEqual((result['n'],result['exact_binary_rank']),(n,r))


if __name__=='__main__':unittest.main()
