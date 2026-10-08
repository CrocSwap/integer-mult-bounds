"""Exact small controls for alternating and signed binary phase residuals.

All complex values below are Gaussian dyadics exactly representable in binary.
These finite controls supplement the general written proof.
"""
import unittest
from itertools import product


def parity(x):
    return x.bit_count() % 2


def linear(columns, x):
    out=0
    for j,col in enumerate(columns):
        if x>>j&1: out ^= col
    return out


class BinaryPhaseTests(unittest.TestCase):
    def test_general_signed_gauss_normal_form(self):
        # Odd line, alternating plane, mixed and nonorthogonal odd bases.
        for columns in ([1], [3,6], [1,6,12], [1,3,7]):
            r=len(columns); n=max(columns).bit_length()
            gram=[sum(parity(v&w)<<i for i,v in enumerate(columns)) for w in columns]
            inverse={linear(gram,z):z for z in range(1<<r)}
            self.assertEqual(len(inverse),1<<r)
            for signs in product((-1,1),repeat=n):
                def q(z):
                    ambient=linear(columns,inverse[z])
                    return sum(s for j,s in enumerate(signs) if ambient>>j&1)%4
                gauss=sum(1j**q(z) for z in range(1<<r))
                self.assertIn(gauss*((1-1j)/2)**r, (1,-1,1j,-1j))
                for x in range(1<<r):
                    for y in range(1<<r):
                        kernel=sum(1j**q(z)*(-1)**parity(z&(x^y)) for z in range(1<<r))/(1<<r)
                        normal=gauss/(1<<r)*1j**(-q(linear(gram,x)))*(-1)**parity(x&linear(gram,y))*1j**(-q(linear(gram,y)))
                        self.assertEqual(kernel,normal)

    def test_walsh_and_endpoint_phase_normalization(self):
        a,b=(1+1j)/2,(1-1j)/2
        C=((a,b),(b,a)); Z=(1,-1); S=(1,1j)
        for x in range(2):
            for y in range(2):
                self.assertEqual(b*S[x]*C[x][y]*S[y],(-1)**(x*y)/2)
                # C X = C^{-1}; the gauged endpoint is corrected by i Z on
                # the left and Z on the right, without another child call.
                self.assertEqual(1j*Z[x]*C[x][1-y]*Z[y],C[x][y])

if __name__=='__main__': unittest.main()
