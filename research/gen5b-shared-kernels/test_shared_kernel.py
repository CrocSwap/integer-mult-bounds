import unittest
from check_shared_kernel import run

class SharedKernelTests(unittest.TestCase):
    def test_three_individual_groups(self):
        for s in('line6','line16','line2'):
            with self.subTest(selection=s):self.assertTrue(run(selection=s)['formal_forward_and_inverse_equal'])
    def test_two_line_union(self):
        r=run();self.assertEqual(r['pivots'],34);self.assertEqual(r['distinct_donors'],43)
    def test_trimmed_three_line_union(self):
        r=run(selection='union72');self.assertEqual(r['setup_adds'],473);self.assertEqual(r['max_donor_multiplicity'],21)
    def test_missing_setup_rejected(self):
        with self.assertRaises(AssertionError):run('omit_setup')
    def test_missing_restore_rejected(self):
        with self.assertRaises(AssertionError):run('omit_restore')
    def test_bad_response_rejected(self):
        with self.assertRaises(AssertionError):run('bad_relation')
    def test_conservative_payload_cap(self):
        from check_scalar_bounds import run as bounds
        r=bounds();self.assertEqual(r['payload_bits'],102);self.assertTrue(r['retained_payload_cap_2_to104']);self.assertEqual(r['actual_sink_redirects'],14)
    def test_bad_entrance_rejected(self):
        with self.assertRaises(AssertionError):run('bad_entrance')

if __name__=='__main__':unittest.main()
