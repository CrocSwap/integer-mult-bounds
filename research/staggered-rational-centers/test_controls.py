"""Adversarial cost and strict-endpoint controls for the staggered rational-center witness."""
import unittest
from fractions import Fraction as Q
import verify as v


class Controls(unittest.TestCase):
    def setUp(self):
        self.crow = v.read(v.HERE / 'producer.json')
        self.brow = v.read(v.HERE / 'bit-axis.json')

    def test_unpaid_complex_cleanup_rejected(self):
        self.crow['histogram'][24] -= 1
        with self.assertRaises(ValueError):
            v.exact(self.crow, self.brow)

    def test_omitted_retained_complex_loss_rejected(self):
        self.crow['loss'] = 0
        with self.assertRaises(ValueError):
            v.exact(self.crow, self.brow)

    def test_unpaid_bit_cleanup_rejected(self):
        self.brow['histogram'][23] -= 1
        with self.assertRaises(ValueError):
            v.exact(self.crow, self.brow)

    def test_omitted_retained_bit_loss_rejected(self):
        self.brow['loss'] = 0
        with self.assertRaises(ValueError):
            v.exact(self.crow, self.brow)

    def test_parent_complex_histograms_cannot_claim_new_bound(self):
        for path in (
            v.ROOT / 'certificates/stopped-product-complex-input.json',
            v.ROOT / 'research/reversed-rational-centers/producer.json',
        ):
            with self.assertRaises((AssertionError, ValueError)):
                v.exact(v.read(path), self.brow)

    def test_parent_bit_histogram_cannot_claim_new_coarse_bound(self):
        old_brow = v.read(v.ROOT / 'certificates/stopped-product-bit-axis.json')
        with self.assertRaises((AssertionError, ValueError)):
            v.exact(self.crow, old_brow)

    def test_next_complex_grid_rejected(self):
        p = v.parent.profile(self.crow)
        with self.assertRaises(ValueError):
            v.parent.moment(p['m'], p['W'], p['child_multiplicities'], Q(8801801148, 10**14), True)

    def test_next_coarse_bit_grid_rejected(self):
        p = v.parent.profile(self.brow)
        with self.assertRaises(ValueError):
            v.check_coarse(p, Q(8926632363, 10**14))

    def test_next_complex_only_kappa_grid_rejected(self):
        c = v.read(v.HERE / 'certificate.json')
        b = Q(c['complex_saving'])
        a = Q(c['bit_parameter'])
        bit = v.parent.profile(v.read(v.ROOT / 'certificates/stopped-product-bit-axis.json'))
        bridge = v.parent.finite_bridge(
            bit, v.parent.profile(self.crow), self.crow,
            v.read(v.ROOT / 'certificates/copied-centers-network.json'),
        )
        with self.assertRaises(AssertionError):
            v.assembly(a, b, bridge, Q(80325171150016, 10**18), beta=v.parent.PHASE_STOP)

    def test_next_joint_kappa_grid_rejected(self):
        c = v.read(v.HERE / 'certificate.json')['joint']
        b = Q(c['complex_saving'])
        a = Q(c['bit_parameter'])
        bit = v.parent.profile(self.brow)
        bridge = v.parent.finite_bridge(
            bit, v.parent.profile(self.crow), self.crow,
            v.read(v.ROOT / 'certificates/copied-centers-network.json'),
        )
        with self.assertRaises(AssertionError):
            v.assembly(a, b, bridge, Q(88002329264726, 10**18), beta=v.parent.PHASE_STOP)


if __name__ == '__main__':
    unittest.main()
