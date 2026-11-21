"""Check the exact geometry, physical reservations and both dyadic controller boundaries."""

from fractions import Fraction
from itertools import combinations, islice, product
from math import comb, gcd, isqrt, prod

from linear_geometry import (
    ceil_log2,
    connected_exponent,
    entrance_geometry,
    minimum_window,
    parameters,
    public_shape,
    square_sides,
)
from outer_schedule import Shape, parameters as predecessor_parameters, square_axes


def integer_guards(precision):
    count = 0
    for s in (*range(512, 770), 1023, 1024, 1025, 8191, 8192, 8193, 12000):
        # Include both ends of the public controller bucket, with actual multiples of six.
        for p in (6 * (((1 << (s - 1)) + 4) // 6), 6 * (((1 << s) - 2) // 6)):
            assert ceil_log2(p + 2) == s
            for length in (p // 12, p // 6 + 3):
                shape = public_shape(p, length)
                width = (length + shape.count - 1) // shape.count
                h0 = shape.count // (1024 * s)
                p_work = precision(p, length, shape.count)
                sp = ceil_log2(p_work + 2)
                g = 4 * sp + 6
                rows = 448 * (4 * s + 1)
                assert minimum_window(s) <= width <= 2 * minimum_window(s)
                assert 50 * p_work < 51 * p and sp <= s + 1
                assert width - (length % shape.count != 0) >= 128 * g
                assert p_work > 32768 * (width + 6)
                assert minimum_window(s) // 2 - s - 6 >= 192 * s + 2
                amp = 4096 * h0 * (width + 6)
                assert 8 * amp * s < 33 * length
                if s >= 8192:
                    assert 1000 * p_work < 1001 * p
                guaranteed = min(h0, shape.count // (80_000 * (width + 2) ** 6))
                assert guaranteed * s**7 >= 1 << (s - 100)
                guard, rmax, crt = shape.crt_control()
                assert 10100 * guard <= length and crt * 101 >= length >= 100 * crt
                assert rmax * 51200 >= shape.count and shape.count // 2 > (1 << 46) * width**3
                body = h0 * width
                required = body + rows + 3 * h0 * g + sp**2
                assert 4 * required < length and (length - s // 2 - body) // 2 >= required
                clock_log = s + 1024 * (width + s + 67)
                assert clock_log < (1 << 21) * (s + 1) < 1 << (s - 9)
                count += 1
    return count


def band_checks():
    bands = ((2, 3, 5, 7), (11, 13, 17, 19), (23, 29, 31))
    orders = (2, 2, 0)
    # Check the lower sieve as an integer identity for every possible divisibility pattern.
    patterns = 0
    for counts in product(*(range(len(band) + 1) for band in bands)):
        upper = [sum((-1) ** i * comb(m, i) for i in range(k + 1)) for m, k in zip(counts, orders)]
        omitted = [comb(m, k + 1) for m, k in zip(counts, orders)]
        lower = prod(upper) - sum(
            x * prod(upper[:j] + upper[j + 1 :]) for j, x in enumerate(omitted)
        )
        assert lower <= int(not any(counts)) <= prod(upper)
        patterns += 1

    # Expand a deliberately coarse case. Period averaging and arbitrary translated intervals
    # must agree with the same signed divisor polynomial, including the interval-end errors.
    def terms(band, ranks):
        return {prod(t): (-1) ** k for k in ranks for t in combinations(band, k)}

    def tensor(parts):
        return {
            prod(v[0] for v in row): prod(v[1] for v in row)
            for row in product(*(piece.items() for piece in parts))
        }

    upper = [terms(band, range(k + 1)) for band, k in zip(bands, orders)]
    lower = tensor(upper)
    for j, (band, k) in enumerate(zip(bands, orders)):
        # k is even. Its next signed term has sign -1.
        extra = tensor(upper[:j] + [terms(band, [k + 1])] + upper[j + 1 :])
        for divisor, weight in extra.items():
            lower[divisor] = lower.get(divisor, 0) + weight
    expected = sum(Fraction(w, d) for d, w in lower.items())
    modulus = prod(prod(b) for b in bands)
    for start in (0, 19, 131, 104729):
        for size in (61, 334, 997):
            count = sum(w * ((start + size) // d - start // d) for d, w in lower.items())
            survivors = sum(gcd(i, modulus) == 1 for i in range(start + 1, start + size + 1))
            assert count <= survivors and abs(count - size * expected) <= sum(
                map(abs, lower.values())
            )
    return patterns


def positive_guards():
    from positive_dispatch import native_h
    from spool import Field

    ranks_read = []

    class AtFactory(Exception):
        pass

    def factory():
        ranks_read.append(1)
        raise AtFactory

    class Empty:
        ambient_bits = 0

    precision = 127
    required = 128 * (4 * (precision + 1).bit_length() + 6)
    for h, window in ((4, required), (5, required - 1), (5, required), (9, required + 1)):
        try:
            native_h(Empty(), 0, h, window, 0, precision, None, 2, factory)
        except AtFactory:
            assert h > 4 and window >= required
        except ValueError as err:
            assert "windows do not fit" in str(err) and (h == 4 or window < required)
        else:
            raise AssertionError("The incomplete test field produced a numerical result")
    assert len(ranks_read) == 2
    field = Field(4, 4)
    data = [(i - 5, (5 * i) % 13 - 3) for i in range(16)]
    field.write(data)
    native_h(field, 0, 4, 1, 0, precision, None, 2, factory)
    expected = []
    for j in range(16):
        signs = [(-1) ** ((i & j).bit_count()) for i in range(16)]
        expected.append(
            tuple(sum(sign * value[c] for sign, value in zip(signs, data)) for c in range(2))
        )
    assert list(field.values()) == expected and len(ranks_read) == 2
    field.retire()
    return 4


def run(precision):
    for n in (0, 1, 2, 5, 8, 741503, 1 << 8192, (1 << 16384) + 11):
        assert parameters(n) == predecessor_parameters(n)
    for width in (20, 21, 24, 28, 31, 38, 51, 66, 96):
        shape = Shape(10000, 8 * width + 3, 8)
        try:
            before = tuple(square_axes(shape.axes()))
        except ValueError:
            try:
                tuple(square_sides(shape))
            except ArithmeticError:
                continue
            raise AssertionError("The predecessor rejected a square that the new scan accepted")
        ours = tuple(square_sides(shape))
        assert ours == before
        assert all(gcd(r, prod(ours[:i])) == 1 for i, r in enumerate(ours))
        assert 4 * prod(ours) >= 3 * (1 << shape.extent_bits)
    # Compute the first actual new prime-avoiding square choices at the production switch.
    p = 6 * (((1 << 511) + 4) // 6)
    b = p // 6
    # These are the exact controller arguments for the binary input length n = 2**b.
    shape = public_shape(p, b + 2 - (b.bit_length() - 1))
    sides = tuple(islice(square_sides(shape), 4))
    assert all(gcd(r, prod(sides[:i])) == 1 and isqrt(r) ** 2 == r for i, r in enumerate(sides))
    for i, (r, width) in enumerate(zip(sides, shape.axes())):
        m = (16 if i % 2 else 4) * shape.count
        assert (m - 1) * (1 << width) <= m * r and 2 * m * r <= (2 * m - 1) * (1 << width)
    for a in (512, 513, 517, 729, 1024, 4095, 4096):
        p = 6 * (((1 << a) + 5) // 6)
        b = p // 6
        for quadratic in (False, True):
            actual = entrance_geometry(a, quadratic=quadratic)
            assert p == (1 << a) + actual["public_offset_above_2_to_A"]
            for correction in (1, 2):
                length = b + correction - (b.bit_length() - 1)
                cap = length // actual["minimum_width"]
                d = 1 << (cap.bit_length() - 1)
                assert actual["log2_axis_count"] == d.bit_length() - 1
                assert actual["largest_axis_width"] == (length + d - 1) // d
    for top, carrier in ((1, 1), (800, 52), (6179, 471), (10**7, 2**21), (2**38, 3300000000)):
        s = connected_exponent(top, carrier) + 1
        assert s - 100 - 7 * ceil_log2(s) >= top + carrier + 2
        for k in range(ceil_log2(s), ceil_log2(s) + 5):
            after_jump = (1 << k) + 1
            assert after_jump - 100 - 7 * ceil_log2(after_jump) >= top + carrier + 2
    # The local inequality first holds at 1024, then fails at 1025 through 1030.
    assert connected_exponent(800, 52) == 1030
    return {
        "public_and_physical_guard_cases": integer_guards(precision),
        "positive_dispatch_boundaries": positive_guards(),
        "band_divisibility_patterns": band_checks(),
        "actual_new_side_widths": [r.bit_length() for r in sides],
    }
