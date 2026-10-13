"""Exact operator and budget controls; no construction search."""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import importlib.util
import json
import unittest
from audit import (ROOT, atom, moment, operator_controls, packet_budget,
                   reframe, single_shear_budget, transparent_word_control, xor)

spec = importlib.util.spec_from_file_location('architecture_rank',
    ROOT/'research/architecture-nine/audit.py')
matrix = importlib.util.module_from_spec(spec)
spec.loader.exec_module(matrix)


class FusionControls(unittest.TestCase):
    def test_dirty_basis_and_missing_cleanup(self):
        result = transparent_word_control()
        for name in ('x','y','z'):
            self.assertEqual(result[name],result['expected_'+name])
        broken = transparent_word_control(True)
        self.assertEqual(broken['y'],result['y'])
        self.assertNotEqual(broken['z'],result['z'])

    def test_replacement_readouts_as_operator_identities(self):
        operator_controls()
        # A different tensor-coordinate placement, with nontrivial R and A.
        U,E,F = 1<<5,(1<<1)|(1<<5)|(1<<9),(1<<12)-1
        x,y = atom('independent x'),atom('independent y')
        first_y = reframe(xor(reframe(x,U),y),E^U)
        B = reframe(first_y,F^E)
        self.assertEqual(xor(B,reframe(y,F^U)),reframe(x,F))
        self.assertNotEqual(B,reframe(x,F))

    def test_full_width_grant_does_not_certify_contraction(self):
        self.assertEqual(moment({575:2},575,2),(Q(1),Q(1)))
        self.assertGreater(moment({575:2,1:1},575,2)[0],1)
        for bad in ({576:1},{0:1},{23:-1}):
            with self.assertRaises(ValueError): moment(bad,575,2)

    def test_complete_single_shear_count_and_free_source_relaxation(self):
        baseline=json.loads((ROOT/'research/kappa-nine/baseline/certificate.json').read_text())
        result=single_shear_budget(baseline)
        N,m,W=result['N'],result['m'],result['W']
        self.assertEqual(result['rank_excess'],22*N)
        self.assertEqual(sum(t*n for t,n in result['optimistic_child_profile'].items()),W*m+22*N)
        self.assertEqual(result['source_growth_free_rank_mass'],W*m)
        self.assertGreater(result['source_growth_free_moment_interval'][0],1)

    def test_packet_bound_for_nonsymmetric_rational_matrices(self):
        u,v = [Q(1),Q(2),Q(-1)],[Q(1,2)]*3
        P=[[x*y for y in v] for x in u]
        I=matrix.identity(3)
        self.assertEqual(matrix.multiply(P,P),P)
        R=matrix.subtract(I,[[2*x for x in row] for row in P])
        self.assertEqual(matrix.multiply(R,R),I)
        # Includes noncommuting/nonprojector K: validates the stronger
        # matrix inequality, not availability of its address implementation.
        cases=[[[Q(0)]*3 for _ in range(3)],P,I,
               [[Q(1),Q(2),Q(0)],[Q(0),Q(1,3),Q(-1)],[Q(2),Q(0),Q(1)]]]
        for K in cases:
            ranks=[matrix.rank(matrix.subtract(K,P)),matrix.rank(K),
                   matrix.rank(matrix.subtract(I,K)),
                   matrix.rank(matrix.subtract(matrix.subtract(I,P),K))]
            self.assertGreaterEqual(sum(ranks),6)
        result=packet_budget(575)
        self.assertGreater(result['moment_lower_interval'][0],1)
        self.assertGreaterEqual(result['K_zero_moment_interval'][1],
                                result['moment_lower_interval'][0])


if __name__ == '__main__': unittest.main()
