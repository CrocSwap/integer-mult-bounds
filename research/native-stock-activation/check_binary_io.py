"""Check signed binary tapes, retained input heads, growing carries and the Fourier product."""

from argparse import ArgumentParser
from io import BytesIO
from random import Random

from binary_io import carry_to_tape, magnitude_bits, magnitude_limbs


def encoded(value):
    return value.to_bytes(max(1, (value.bit_length() + 7) // 8), "little")


def check_primitive():
    rng = Random(170621)
    cases = 0
    for radix in (1, 2, 5, 7, 8, 9, 15, 16, 17, 31, 65, 267):
        for length in (0, 1, 3, 8, 16, 64, 339, 1031):
            value = rng.getrandbits(length)
            data = encoded(value) + bytes(17)
            bank = BytesIO(b"input" + data + b"/dirty")
            bank.seek(5)
            assert magnitude_bits(bank, len(data)) == value.bit_length() and bank.tell() == 5
            limbs = list(magnitude_limbs(bank, value.bit_length(), radix))
            assert bank.tell() == 5
            assert sum(x << (i * radix) for i, x in enumerate(limbs)) == value
            # Each coefficient exceeds one digit when both source digits have high bits.
            coefficients = (
                [
                    sum(
                        a * b
                        for j, a in enumerate(limbs)
                        for k, b in enumerate(limbs)
                        if j + k == i
                    )
                    for i in range(max(0, 2 * len(limbs) - 1))
                ]
                if len(limbs) <= 20
                else [v * 8841 for v in limbs]
            )
            expected = encoded(value**2 if len(limbs) <= 20 else value * 8841)
            target = BytesIO(b"guard" + bytes(len(expected)) + b"/dirty")
            target.seek(5)
            written = carry_to_tape(target, iter(coefficients), radix)
            assert written == len(expected) and target.tell() == 5 + written
            assert target.getvalue() == b"guard" + expected + b"/dirty"
            cases += 1
    # Interior zero runs need to be emitted. Canonical trailing zero runs must be dropped.
    run = [0] * 5000
    data = BytesIO()
    assert carry_to_tape(data, iter([9, *run, 19, *run]), 8) == 5002
    assert data.getvalue() == b"\x09" + bytes(5000) + b"\x13"
    source = BytesIO(b"prefix")
    source.seek(4)
    try:
        magnitude_bits(source, 20)
    except EOFError:
        assert source.tell() == 4
    else:
        raise AssertionError("The truncated input was accepted")
    print("signed-magnitude input, output guard and carry cases", cases + 2, flush=True)


def checked(run, left, right, pad=0):
    a, b = (encoded(abs(x)) + bytes(pad) for x in (left, right))
    x, y = (BytesIO(b"PRE" + data + b"POST") for data in (a, b))
    x.seek(3)
    y.seek(3)
    expected = encoded(abs(left * right))
    out = BytesIO(b"guard" + bytes(len(expected)) + b"after")
    out.seek(5)
    result = run(
        x, len(a), y, len(b), out, left_negative=left < 0 or not left, right_negative=right < 0
    )
    assert (
        x.tell() == 3
        and y.tell() == 3
        and x.getvalue() == b"PRE" + a + b"POST"
        and y.getvalue() == b"PRE" + b + b"POST"
    )
    assert result[:2] == (left * right < 0, len(expected))
    assert out.tell() == 5 + len(expected) and out.getvalue() == b"guard" + expected + b"after"
    return result[2] if len(result) > 2 else None


if __name__ == "__main__":
    p = ArgumentParser(description=__doc__)
    p.add_argument(
        "--fourier", action="store_true", help="also run the signed 3-by-5 Fourier product"
    )
    args = p.parse_args()
    check_primitive()
    from product_path import Product, multiply_tapes

    for left, right in (
        (0, 0),
        (0, -3441),
        (-655377, 0),
        (1, 64),
        (-51, 73),
        (-74493, -2011),
        (2**311 + 1, 2**131 - 1),
    ):
        checked(multiply_tapes, left, right, pad=17)
    print("uniform stopped binary tape products", 7, flush=True)
    if args.fourier:
        machine = Product((3, 5), 8, 136)

        def collect(*params, **kw):
            return machine.multiply_tapes(*params, **kw, coefficients=True)

        coefficients = checked(collect, -741503, 466013, pad=11)
        assert coefficients == [11811, 10996, 4152, 868, 77] + [0] * 10
        print(
            "signed file Fourier product",
            -345550037539,
            coefficients[:5],
            machine.h_calls,
            flush=True,
        )
        small = Product((3,), 5, 96)
        for left, right in ((0, -751), (-1023, -1023), (1, -1)):
            checked(small.multiply_tapes, left, right, pad=3)
        print(
            "extra full Fourier zero, negative-unit and saturated-carry file products",
            3,
            flush=True,
        )
