"""Exercise the complete relocated Gaussian packet on both sides of a dirty field."""

from complex_stage import entrance, native_h, place_and_apply
from compact_crt import binary_swap
from positive import Positive
from spool import Field


def run(positions, L, h, window, offset, low, stock, digit, suffix):
    field = Field(L, 4)
    data = [(i % 31 - 12, (i * i + 3 * i) % 73 - 19) for i in range(1 << L)]
    field.write(iter(data))
    expected = data.copy()
    for pos in positions:
        bit = 1 << pos
        for addr in range(1 << L):
            if addr & bit:
                continue
            a, b = expected[addr]
            c, d = expected[addr + bit]
            expected[addr], expected[addr + bit] = (a + c, b + d), (a - c, b - d)
    provider = Positive(None, None, h)
    if digit:
        issued = []

        def observed(s, d, bits, p, g, last):
            issued.append(bits)
            binary_swap(s, d, bits, p, g, last)

        place_and_apply(field, low, h, window, offset, stock, digit, suffix, observed, provider)
        assert issued == [h * window, h * window]
    else:
        native_h(field, low, h, window, offset, 64, binary_swap)
    assert list(field.values()) == expected
    field.retire()


if __name__ == "__main__":
    for L, h, window, offset, low, stock, digit, suffix in (
        (8, 1, 2, 1, 0, 0, 1, 1),
        (8, 1, 2, 1, 6, 0, 1, 1),
        (14, 2, 1, 0, 2, 1, 1, 1),
        (13, 2, 2, 1, 3, 0, 0, 0),
    ):
        run(
            [low + i * window + offset for i in range(h)],
            L,
            h,
            window,
            offset,
            low,
            stock,
            digit,
            suffix,
        )
    try:
        entrance(10, 4, 2, 2, 3, 2, 2)
    except ValueError:
        pass
    else:
        raise AssertionError("A colliding complete packet was admitted")
    print(
        "PASS_PLACEMENT 4 dirty Gaussian fields, both exterior directions, 6 whole-window shuttles"
    )
