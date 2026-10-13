"""Exact basis-vector and recurrence controls; no numerical tolerances."""
from fractions import Fraction as Q
import unittest
import audit as a


class DirectTests(unittest.TestCase):
    def test_complete_basis_selected_xor_with_spectators(self):
        width=6;pairs=[(4,0),(5,2)]
        for j in range(1<<width):
            values=[(int(i==j),0) for i in range(1<<width)]
            self.assertEqual(a.direct_selected_xor(values,pairs),a.address_selected_xor(values,pairs))

    def test_complete_basis_later_source(self):
        pairs=[(0,4),(2,5)]
        for j in range(64):
            values=[(0,int(i==j)) for i in range(64)]
            self.assertEqual(a.direct_selected_xor(values,pairs),a.address_selected_xor(values,pairs))

    def test_walsh_against_character_sum_and_normalization(self):
        bits=[0,2];mask=sum(1<<b for b in bits)
        values=[(j-8,2*j+1) for j in range(16)]
        want=[]
        for i in range(16):
            terms=[((-1)**((i&j&mask).bit_count()),values[j]) for j in range(16) if (i^j)&~mask==0]
            want.append(tuple(sum(sign*v[k] for sign,v in terms) for k in range(2)))
        self.assertEqual(a.walsh(values,bits),want)
        self.assertEqual(a.divide(a.walsh(a.walsh(values,bits),bits),2),values)
        with self.assertRaises(AssertionError):a.divide([(1,0)],1)

    def test_fused_direction_on_complete_basis(self):
        bits=[0,2,4];mask=sum(1<<b for b in bits)
        for j in range(32):
            values=[(int(i==j),0) for i in range(32)]
            self.assertEqual(a.fused_direction(values,bits),a.twice_c(values,mask))

    def test_mobility_witness_requires_each_direction_coordinate(self):
        # The nonzero off-diagonal entry connects 0 to a mask containing all
        # three coordinates. Diagonal operations and kernels omitting any
        # one of them preserve that bit, so their products cannot supply it.
        mask=0b10101
        values=[(int(i==0),0) for i in range(32)]
        output=a.twice_c(values,mask)
        self.assertEqual(output[mask],(1,-1))
        for bit in [0,2,4]:
            touched=mask^(1<<bit)
            self.assertTrue(mask&~touched)

    def test_exact_pinned_cost_screen(self):
        b=a.budget()
        self.assertEqual(b['rank_slack'],5778864)
        self.assertEqual(b['extra_unit_child_allowance_per_endpoint'],Q(7,13))
        for result in b['screens'].values():
            self.assertGreater(result['linear_exponent_moment'],1)
        self.assertEqual(b['screens']['coordinate_mobility_lower_bound']['added_rank_mass'],8*b['N'])
        self.assertEqual(b['screens']['fused_hadamard_schedule']['added_rank_mass'],16*b['N'])


if __name__=='__main__':unittest.main()
