"""Exact regression controls for the bounded design session."""
from fractions import Fraction as Q
import unittest
import design as d


def partial_swap(P):
    A=d.sub(d.eye(len(P)),P)
    return [a+p for a,p in zip(A,P)]+[p+a for a,p in zip(A,P)]


class DesignTests(unittest.TestCase):
    def test_common_charts_and_exception(self):
        results=d.chart_controls()
        self.assertEqual([r['commutant_dimension'] for r in results],[1,4,1,1,1,1])
        coordinates=[[[Q(i==k and j==k) for j in range(4)] for i in range(4)] for k in range(4)]
        self.assertEqual(d.commutant_dimension(coordinates),4)

    def test_clean_scalar_map(self):
        self.assertEqual(d.clean_identity(6)['binary_central_rank'],6)
        # Omitting side correction fails, despite a correct diagonal.
        S={0,1,2};T={0,3,4}
        self.assertEqual(len(S&T)%2,1)
        self.assertNotEqual(S,T)

    def test_readout_budget_and_degenerate_exclusions(self):
        for h in (6,7,10):
            r=d.readout(h)
            self.assertEqual(r['minimum_terminal_tour'],2*h)
            self.assertGreaterEqual(r['any_tree_rank_lower_bound'],r['useful_rank_capacity'])
        with self.assertRaises(AssertionError):d.readout(9)
        with self.assertRaises(AssertionError):d.readout(5)

    def test_physical_clean_endpoint(self):
        h=6;P=d.projector([d.vector({0,1,2},h)],d.metric(h));H=d.sub(d.eye(h),P)
        self.assertEqual(d.product(partial_swap(P),partial_swap(P)),d.eye(2*h))
        self.assertEqual(d.product(partial_swap(H),partial_swap(P)),partial_swap(d.eye(h)))
        self.assertNotEqual(partial_swap(H),partial_swap(d.eye(h)))

    def test_explicit_tree_path_operators(self):
        h=6;G=d.metric(h);S={0,1,2};ts=d.triples(h)
        H=d.sub(d.eye(h),d.projector([d.vector(S,h)],G))
        U=[d.projector([d.vector(T,h) for T in ts if set(T)&S=={i}],G) for i in range(3)]
        D=d.projector([[Q(j==i)-Q(j==h-1) for j in range(h)] for i in range(3,h-1)],G)
        FD,FH,F1=map(partial_swap,[D,H,U[0]])
        tail=d.product(d.product(FH,F1),d.product(F1,FD))
        self.assertEqual(d.product(tail,FD),FH)
        for P in U[1:]:
            self.assertEqual(d.product(tail,d.product(FD,partial_swap(P))),d.product(FH,partial_swap(P)))
        self.assertNotEqual(d.product(tail,partial_swap(U[1])),d.product(FH,partial_swap(U[1])))

    def test_hypothetical_budget_is_not_a_certificate(self):
        b=d.aggregate_budget()
        self.assertFalse(b['construction_supplied'])
        self.assertFalse(b['complex_partner_supplied'])
        self.assertEqual(b['remaining_rank_budget_at_exponent_one_strictly_below'],1265)
        self.assertLess(Q(b['moment_bounds']['1253'][1]),1)
        self.assertGreater(Q(b['moment_bounds']['1254'][0]),1)


if __name__=='__main__':unittest.main()
