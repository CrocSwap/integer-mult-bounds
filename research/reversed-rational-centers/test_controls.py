"""Adversarial cost and strict-endpoint controls for the selected finite witness."""
import copy, unittest
from fractions import Fraction as Q
import verify as v

class Controls(unittest.TestCase):
    def setUp(self): self.row=v.read(v.HERE/'producer.json')
    def test_unpaid_cleanup_rejected(self):
        self.row['histogram'][24]-=1
        with self.assertRaises(ValueError):v.exact(self.row)
    def test_omitted_retained_loss_rejected(self):
        self.row['loss']=0
        with self.assertRaises(ValueError):v.exact(self.row)
    def test_parent_histogram_cannot_claim_new_bound(self):
        row=v.read(v.ROOT/'certificates/stopped-product-complex-input.json')
        with self.assertRaises((AssertionError,ValueError)):v.exact(row)
    def test_next_complex_grid_rejected(self):
        p=v.parent.profile(self.row)
        with self.assertRaises(ValueError):
            v.parent.moment(p['m'],p['W'],p['child_multiplicities'],Q(7799647192,10**14),True)
    def test_next_kappa_grid_rejected(self):
        c=v.read(v.HERE/'certificate.json');b=Q(c['complex_saving']);a=Q(c['bit_parameter'])
        bit=v.parent.profile(v.read(v.ROOT/'certificates/stopped-product-bit-axis.json'))
        bridge=v.parent.finite_bridge(bit,v.parent.profile(self.row),self.row,
            v.read(v.ROOT/'certificates/copied-centers-network.json'))
        with self.assertRaises(AssertionError):
            v.assembly(a,b,bridge,Q(7798412662810,10**17),beta=v.parent.PHASE_STOP)

if __name__=='__main__':unittest.main()
