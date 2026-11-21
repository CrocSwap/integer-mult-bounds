"""Compute the fixed machine bills without expanding its production-size integers."""

from fractions import Fraction
from math import prod

OLD_BIT_H = 1_285_200_000_000_000
BIT_H = 240_000_000_000_000
OLD_COMPLEX_H = 15_171_300_000_000_000_000
COMPLEX_H = 3_300_000_000
KAPPA = Fraction(387992803556, 10**14)


def ceil_ratio(a, b):
    return (a+b-1)//b


def first_square_branch():
    """Work with the length exponent b, even when n itself will not fit in memory."""
    s = 1
    while True:
        w = 65536*s**3
        # s is the bit length of 6b+1.
        first = max(1, ceil_ratio((1 << (s-1))-1,6))
        last = ((1 << s)-2)//6

        def admitted(b):
            # At n=2**b the condition is 2**(b-w+3)>b.
            return b-w+3 >= b.bit_length()

        if first <= last and admitted(last):
            lo, hi = first, last
            while lo < hi:
                middle = (lo+hi)//2
                if admitted(middle):
                    hi = middle
                else:
                    lo = middle+1
            b = lo
            # n_min = max(2**(b-1), b*2**(w-3)) + 1.
            if b-w+2 >= b.bit_length():
                return dict(s=s, width=w, b=b, multiplier=1, shift=b-1)
            return dict(s=s, width=w, b=b, multiplier=b, shift=w-3)
        s += 1


def group_size(n,q):
    return prod(q**n - q**i for i in range(n))


def exact_stock(n,batch,q,e):
    """One stage in the exact units of the binary-to-radix wrapper."""
    lo, hi = 1, e
    while lo < hi:
        mid = (lo+hi)//2
        if mid**250 >= e:
            hi = mid
        else:
            lo = mid+1
    w = lo
    d = ceil_ratio(e,w)
    depth, capacity = 2, 1
    while capacity < d:
        capacity *= n
        depth += 1
    return dict(width=w, depth=depth, stock=(batch * group_size(n,q)*q**(n*n*(w-1)))**depth)


def bill():
    h, h0 = BIT_H, OLD_BIT_H
    threshold = ceil_ratio(250*(2*h+12),249)
    # At e=2**threshold the survival ratio dominates the six simultaneous reserves.
    if not (3*250 < h and 249*threshold >= 250*(2*h+12)
            and threshold < 3*h and 48*6+2 < 2**12):
        raise ArithmeticError("The simultaneous stock guard is insufficient")
    return dict(
        bit_log2_N=[h0,h], complex_log2_N=[OLD_COMPLEX_H,COMPLEX_H],
        N_reduction_log2=[h0-h, OLD_COMPLEX_H-COMPLEX_H],
        old_prime_strict_log2_lower=45+5*h0, new_prime=3,
        old_bucket_strict_log2_lower=2*(45+5*h0), new_buckets=9,
        old_low_count_strict_log2_lower="2^(2*old_H)-1",
        new_low_count_strict_log2_upper="log2(3)*2^(2*new_H)",
        new_bit_log2_batch_upper=105*h, new_complex_log2_batch_upper=448*COMPLEX_H,
        new_bit_log2_records_upper=2+285*h, new_complex_log2_records_upper=2+1216*COMPLEX_H,
        old_necessary_qdigit_log2_floor=(250*(2*h0+1))//249,
        new_sufficient_qdigit_log2_ceiling=threshold,
        new_eager_setup_log2log2_upper=2*h+5,
        new_streamed_setup_log2_upper=20000*h,
        old_low_output_log2log2_floor=2*h0-1,
        square_first=first_square_branch(), cold_kappa=str(KAPPA))


if __name__ == "__main__":
    import json
    print(json.dumps(bill(), indent=2))
