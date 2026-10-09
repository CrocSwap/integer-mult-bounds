import unittest
from fractions import Fraction as Q
from unit_readouts import split_numerator, validate_pieces
class Controls(unittest.TestCase):
    def test_actual_larger_coefficient(self): self.assertEqual(split_numerator(55),(42,13))
    def test_negative_coefficient(self): self.assertEqual(split_numerator(-55),(-42,-13))
    def test_zero(self): self.assertEqual(split_numerator(0),())
    def test_unpaid_third_piece_rejected(self):
        with self.assertRaises(AssertionError): split_numerator(85)
    def test_dropped_piece_rejected(self):
        with self.assertRaises(AssertionError): validate_pieces(55,(42,))
    def test_oversized_single_shear_rejected(self):
        with self.assertRaises(AssertionError): validate_pieces(55,(55,))
    def test_wrong_inverse_sign_rejected(self):
        with self.assertRaises(AssertionError): validate_pieces(55,(42,-13))
    def test_exact_shear_and_inverse_on_dirty_values(self):
        for numerator in range(-84,85):
            x,y=Q(17,13),Q(-29,11)
            pieces=split_numerator(numerator)
            z=y
            for a in pieces:z+=Q(a,42)*x
            self.assertEqual(z,y+Q(numerator,42)*x)
            for a in reversed(pieces):z-=Q(a,42)*x
            self.assertEqual(z,y)
if __name__=='__main__':unittest.main()
