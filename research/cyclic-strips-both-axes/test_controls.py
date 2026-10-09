"""Adversarial controls: old rows, unpaid cleanup and omitted loss cannot certify the new bound."""
import copy, unittest
import verify as v

class Controls(unittest.TestCase):
    def setUp(self):
        self.bit=v.read(v.HERE/'bit-row.json');self.row=v.read(v.HERE/'producer.json')
    def test_selected_rows_pass_without_certificate(self):
        v.exact(self.bit,self.row,compare=False)
    def test_old_bit_row_rejected(self):
        with self.assertRaises(Exception):v.exact(v.read(v.ROOT/'certificates/stopped-product-bit-axis.json'),self.row,compare=False)
    def test_pr108_complex_row_rejected(self):
        with self.assertRaises(Exception):v.exact(self.bit,v.read(v.ROOT/'research/dual-suffix-centers/producer.json'),compare=False)
    def test_unpaid_complex_cleanup_rejected(self):
        r=copy.deepcopy(self.row);r['histogram'][24]-=1
        with self.assertRaises(Exception):v.exact(self.bit,r,compare=False)
    def test_omitted_bit_loss_rejected(self):
        b=copy.deepcopy(self.bit);b['loss']=0
        with self.assertRaises(Exception):v.exact(b,self.row,compare=False)
    def test_unpaid_bit_role_rejected(self):
        b=copy.deepcopy(self.bit);b['R']-=1
        with self.assertRaises(Exception):v.exact(b,self.row,compare=False)

if __name__=='__main__':unittest.main()
