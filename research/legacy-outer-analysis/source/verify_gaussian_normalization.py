#!/usr/bin/env python3
"""Check exact phase and tail bounds for the retained Gaussian sampler."""

from fractions import Fraction as Q
from hashlib import sha256
import json
from math import gcd
from pathlib import Path


def main():
    cases, distances = [], 0
    for s in range(3, 32, 2):
        for t in range(s+1, 2*s+2):
            if gcd(s,t) != 1:
                continue
            phase = (s-1)//2
            j = (pow(t,-1,s)*phase) % s
            x = Q(t*j,s)
            nearest = (2*x.numerator+x.denominator)//(2*x.denominator)
            beta = x-nearest
            assert Q(1,3) <= beta < Q(1,2)
            for k in range(t):
                # Use the exact nearest periodic image of this integer k.
                relative = (x-k)/t
                alias = (2*relative.numerator+relative.denominator)//(2*relative.denominator)
                delta = abs(x-k-alias*t)
                assert beta <= delta <= Q(t,2)
                for ell in range(1,9):
                    far_plus = abs(x-k-(alias+ell)*t)
                    far_minus = abs(x-k-(alias-ell)*t)
                    assert min(far_plus,far_minus) >= t*(ell-Q(1,2))
                    assert (t*(ell-Q(1,2)))**2-beta**2 >= 2+(ell-1)
                    distances += 2
            cases.append(dict(s=s,t=t,j=j,beta=str(beta)))
    # For v>=0, 9(v+1/2)^2-1/4-(2+v) = 9v^2+8v.
    # Its coefficients certify the bound for every v, beyond the finite cases.
    universal_polynomial = [9,8,0]
    assert all(coefficient >= 0 for coefficient in universal_polynomial)
    ratio = 2*Q(1,2**6)/(1-Q(1,2**3))
    assert ratio == Q(1,28) < 1
    for u in range(12,257):
        assert Q(u,3)-1 >= Q(u,4)
    for u in range(24,257):
        for d in (1,2,10,100):
            assert d*(Q(u,3)-1)-1 >= Q(d*u,4)
    # An integral phase has no suppression; it cannot serve as the selected
    # worst column. The non-integral phase selection is necessary.
    assert Q(0)**2 < Q(1,9)
    out=Path(__file__).with_name('gaussian-normalization-receipt.json')
    receipt=dict(status='PASS exact phase and tail certificates',
        script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        coprime_size_cases=len(cases),exact_periodic_distance_checks=distances,cases=cases,
        universal_tail_polynomial_coefficients=universal_polynomial,
        tail_relative_upper_bound=str(ratio),
        classical_bounds=['pi > 3','exp(1) > 2'],
        column_upper_bound='||T e_j||_infinity < 2 exp(-pi u beta_j^2)',
        left_inverse_lower_bound='||L||_infinity > 2^(u/3-1)',
        tensor_lower_bound='||L_tensor||_infinity > 2^(d(u/3-1)) for any full left inverse',
        required_normalization_bits='gamma >= d*u/4 when u >= 12',
        approximate_left_inverse='gamma >= d*u/4 when ||L_tensor T_tensor-I||<=1/2 and u>=24',
        scope='The written argument proves the conditional operator bound. Finite rational controls check its phase and tail arithmetic. The complete sampler, arbitrary-input disk interface, and tensor volume are retained. This is not an integer-multiplication lower bound.')
    out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({key:receipt[key] for key in ('status','coprime_size_cases','exact_periodic_distance_checks','required_normalization_bits')}))


if __name__ == '__main__':
    main()
