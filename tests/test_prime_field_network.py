"""Mathematical identities and negative controls for the F3 construction."""
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from paired_triple_circuit import PairedTriple
from prime_field_circuit import optimize
from prime_field_checks import SmallProducer,scalar_control,frame_control,matching
from prime_field_network import witness,parameters,bit_counts,complex_counts
from paired_complex import PairedComplex
from complex_circuit import Checks,verify_role_frames

class PrimeFieldTests(unittest.TestCase):
    def test_all_weighted_triple_coefficients(self):
        for n in (6,8,10):
            self.assertTrue(PairedTriple(n).verify()['all_disjoint_output_coefficients_exact'])

    def test_all_dirty_scalar_basis_and_both_frame_directions(self):
        c=SmallProducer(8)
        self.assertTrue(c.verify_map()['retained_coefficients_exact'])
        self.assertTrue(scalar_control(c)['corrected_three_stage_exchange'])
        for row in frame_control(c)['frames']:
            self.assertEqual(row['loss'],168)
            self.assertEqual(row['total_rank'],9472)

    def test_all_matching_cases(self):
        self.assertEqual(matching()['distinct_images'],98280)

    def test_star_replacement_preserves_each_coefficient(self):
        masks=[0b111100,0b111001,0b110011,0b001111]
        nodes={1<<i:1<<i for i in range(6)}
        for a,b in optimize(masks):
            self.assertFalse(nodes[a]&nodes[b]);nodes[a|b]=nodes[a]|nodes[b]
        for m in masks:self.assertEqual(nodes[m],m)

    def test_complex_coordinate_labels_after_new_producer(self):
        c=PairedComplex(10);checks=Checks(c)
        self.assertTrue(checks.verify_map()['side_map_exact'])
        self.assertTrue(checks.verify_labels()['all_residuals_have_odd_vectors'])
        self.assertTrue(verify_role_frames(c,checks)['reverse_complement_frames_nested'])

    def test_improvements_are_needed_by_the_consumer(self):
        p=parameters();self.assertGreater(witness()['absorption_gap'],0)
        for bad in (bit_counts(roles=12224156),bit_counts(center_dimension=28)):
            with self.assertRaisesRegex(ValueError,'Unsupported bit exponent'):witness(bn=bad)
        for bad in (replace(p,kappa=Q(1,2**27)),replace(p,epsilon=Q(1,2)),
                    replace(p,sigma=1-Q(14,10**9)),replace(p,C1=Q(2))):
            with self.assertRaises(ValueError):witness(p=bad)

if __name__=='__main__':unittest.main()
