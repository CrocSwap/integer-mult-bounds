import importlib.util, pathlib, unittest
from fractions import Fraction as Q

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('certificate_round3', ROOT / 'scripts' / 'certificate_round3.py')
r3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(r3)

A_B = Q(22157, 5 * 10**9)
A_C = Q(1048009, 25 * 10**10)   # fully batched PR #7 complex network, independent/complex-network
KAPPA = Q(13086957581, 3125 * 10**12)


class Round3(unittest.TestCase):
    def test_headline_both_guards(self):
        for guard in ('pathwise', 'crude'):
            r = r3.evaluate(A_B, A_C, Q(1, 1000), guard)
            self.assertTrue(r['ok'], r['bad'])
            self.assertEqual(r['kappa'], KAPPA)
            self.assertEqual(r['binding'], 'simultaneous butterflies')
            self.assertGreater(r['kappa'], Q(1, 2**18))

    def test_complex_side_binds(self):
        # raising a_c must raise kappa; raising a_b must not
        k = r3.evaluate(A_B, A_C, Q(1, 1000), 'crude')['kappa']
        self.assertGreater(r3.evaluate(A_B, A_C * 2, Q(1, 1000), 'crude')['kappa'], k)
        self.assertEqual(r3.evaluate(A_B * 2, A_C, Q(1, 1000), 'crude')['kappa'], k)


if __name__ == '__main__':
    unittest.main()
