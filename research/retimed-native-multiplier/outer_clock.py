"""Check the finite endpoints and the dyadic induction comparisons for the outer clock."""

from fractions import Fraction
from itertools import chain


def width_cap(s):
    if s < 512:
        return 128 * s * s
    return 1024 * s + 2560


def private_log(s):
    # X=2^64(t+2)(P+2), P<2^20 p, d<=p<2^s.
    return s + 1024 * (width_cap(s) + s + 88)


def controls_log(s):
    # Dense Beneš, inverse modulo the true side, restored left child, and all copies.
    return 60 + 16 * (s + 1) + 10 * (width_cap(s) + 1)


def exact_shape_check(package):
    from pathlib import Path
    import sys

    sys.path.insert(0, str(Path(package).resolve()))
    import band_product
    from linear_geometry import parameters, square_sides

    first = (18508 << 18493) + 1
    assert parameters(first - 1) is None
    shape = parameters(first)
    assert shape.count == 1
    side, = square_sides(shape)
    bits = next(shape.axes())
    assert side.bit_length() == bits
    actual_precision = band_product.precision(shape.public, shape.extent_bits, shape.count)
    # The production fourier_axis function calls [Fraction(1)] * r. This reproduces
    # its host list limit before any large allocation. It is not a Turing lower bound.
    try:
        [None] * side
    except OverflowError as exc:
        host = type(exc).__name__
    else:
        raise AssertionError("The first side unexpectedly fit a host list")

    # The two-endpoint assertions bind all advertised finite constants to the producer.
    return {"first_b": shape.public // 6, "first_L": bits, "first_P": actual_precision,
            "first_side_bit_length": side.bit_length(), "host_list": host}


def financial_checks():
    # At s>=32 the private setup fits in n. Compare one term with an exponential
    # and use (s+2)^2<2(s+1)^2 on the tail. The linear cap only decreases at s=512.
    assert max(private_log(s) for s in range(1, 32)) < (1 << 27) - 100_000
    assert 32 + 1024 * (128 * 32**2 + 32 + 88) < 1 << (32 - 4)
    assert max(controls_log(s) for s in range(1, 64)) < 1 << 23
    assert 128 * 63**2 == 508_032
    for s in chain(range(32, 1025), (4096, 8192)):
        assert private_log(s) < 1 << (s - 4)
        if s >= 64:
            # Use p>=2^(s-1)-1 and L>=p/12. The polynomial has its
            # maximum relative to the exponential at the first endpoint.
            p_min = (1 << (s - 1)) - 1
            L_min = p_min // 12
            G_max = 64 * (width_cap(s) + s)
            assert L_min >= 10100 * G_max
            assert L_min // (2 * width_cap(s)) >= 51_200
            H_min = L_min // 101
            assert controls_log(s) + 16 < H_min
            assert private_log(s) + 16 < H_min
    # Scalar fallback is impossible at b >= 2^15. On 2^j<=b<2^(j+1),
    # ceil(log2(p+2))<=j+4; L >= 2^j-j-1. Growth closes all later j.
    for j in range(15, 128):
        assert (1 << j) - j - 1 >= 64 * (j + 4)**2
        assert 2 * (j + 4)**2 >= (j + 5)**2
    for s in (512, 1023, 1024, 4096):
        ell = width_cap(s)
        h_mixing_class = 80_000 * (ell + 2)**6 + 2048 * s + 2
        pack_pass = 40_000 * (ell + 2)**6 + 4
        assert 3 * h_mixing_class * pack_pass < (1 << 168) * (s + 1)**12
        # Each switch has at most 20 whole swaps, and each tail has two.
        K = 64 * 64 * (ell + s)
        crt_dispatch = 3 * s * 2 * ell * (1 << 18) * (10 + 32 * K + 4 * K*K)
        assert crt_dispatch < (1 << 90) * (s + 1)**4
    g = Fraction(1, 10**17)
    assert (Fraction(128, 1) / g)**16 < 1 << 1024
    return {"private_prefix_log2": max(private_log(s) for s in range(1, 32)),
            "controls_prefix_log2": max(controls_log(s) for s in range(1, 64)),
            "early_log2_C_bound": 1 << 27,
            "tail_log2_fixed_factor_including_b_to_n": 1434,
            "tail_unit": "(1 + B + Z) * n * (1 + log2(n))^(1-kappa)"}


if __name__ == "__main__":
    from argparse import ArgumentParser
    import json

    command = ArgumentParser(description=__doc__)
    command.add_argument("package", nargs="?")
    args = command.parse_args()
    report = financial_checks()
    if args.package:
        report.update(exact_shape_check(args.package))
    print(json.dumps(report, sort_keys=True))
