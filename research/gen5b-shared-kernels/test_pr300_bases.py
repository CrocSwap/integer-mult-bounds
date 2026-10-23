import unittest
import copy
import source_data as sd
import check_pr300_bases as bases

class BasisTests(unittest.TestCase):
    def test_pinned_bases(self):
        r=bases.run()
        self.assertEqual(r['unique_selected_bases'],65)
        self.assertTrue(r['nondegenerate_over_every_field_of_characteristic_above5'])
    def test_singular_basis_rejected(self):
        x=sd.read_json('pr300/descent2-selection.json')
        x['entries'][0]['new_basis'][0]=[0]*24
        with self.assertRaises(AssertionError): bases.basis_receipt(x)
    def test_bareiss_row_swap(self):
        self.assertEqual(bases.det([[0,2],[3,4]]),-6)

if __name__=='__main__': unittest.main()
