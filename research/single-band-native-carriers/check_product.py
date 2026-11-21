"""Compare signed integer tapes and all recovered digits at the same Fourier geometry."""

from collections import Counter
from io import BytesIO
from time import perf_counter

from band_product import PackProduct, Product, multiply
from ordinary_carrier import ordinary_swap, stage_body


def limbs(value, b):
    v = abs(value)
    return [(v >> q) % (1 << b) for q in range(0, v.bit_length(), b)]


def one(machine, a, b):
    field_bits = machine.b
    left, right = (abs(v).to_bytes((abs(v).bit_length() + 7) // 8, "little") for v in (a, b))
    inputs = [BytesIO(b"keep" + v + b"tail") for v in (left, right)]
    for src in inputs:
        src.seek(4)
    target = BytesIO(b"head" + bytes(80) + b"guard")
    target.seek(4)
    before = machine.h_calls
    start = perf_counter()
    sign, size, coeff = machine.multiply_tapes(
        inputs[0],
        len(left),
        inputs[1],
        len(right),
        target,
        coefficients=True,
        left_negative=a < 0,
        right_negative=b < 0,
    )
    seconds = perf_counter() - start
    expected = [0] * machine.size
    for i, x in enumerate(limbs(a, field_bits)):
        for j, y in enumerate(limbs(b, field_bits)):
            expected[i + j] += x * y
    raw = abs(a * b).to_bytes(max(1, (abs(a * b).bit_length() + 7) // 8), "little")
    assert list(coeff) == expected and sign == (a * b < 0) and size == len(raw)
    assert target.getvalue() == b"head" + raw + bytes(80 - size) + b"guard"
    assert all(
        t.tell() == 4 and t.getvalue() == b"keep" + v + b"tail"
        for t, v in zip(inputs, (left, right), strict=True)
    )
    assert machine.h_calls > before
    return {
        "product": str(a * b),
        "bits": [abs(a).bit_length(), abs(b).bit_length()],
        "H_calls": machine.h_calls - before,
        "coefficients_prefix": expected[:5],
        "seconds": round(seconds, 4),
    }


def stock_and_public():
    from dataclasses import replace
    from calibration import COMPACT

    assert multiply(-741503, 466013) == -345550037539
    for x in (0, -1, 1, 37, -69, 2**16383 + 5):
        assert multiply(x, -997) == x * -997
    # Exercise the production stage body with a feasible rank and all 81 by 81 addresses.
    profile = replace(COMPACT, rank_logs=(1,))
    side = 3**4
    records = bytes((i * 97 + (i >> 4)) % 256 for i in range(side * side))
    result = BytesIO()
    stage_body(BytesIO(records), result, 4, 1, 1, 1, 1, profile)
    assert result.getvalue() == bytes(
        records[j * side + i] for i in range(side) for j in range(side)
    )


def physical_product():
    from binary_receiver import Receiver
    from module_atoms import balanced_widths
    from ordinary import rectangle
    from streaming_routes import work_tapes
    from triangular_ordinary import root_body

    stock_and_public()
    core = Receiver(2, balanced_widths(1), direct=True)
    calls = Counter()

    def exchange(src, dst, bits, prefix, gap, suffix):
        assert bits == 1
        calls["shuttles"] += 1
        calls["padded_bytes"] += prefix * 81 * gap * suffix
        with work_tapes(2) as (opened, restored):
            rectangle(src, opened, 2, 9, prefix, gap, suffix)
            opened.seek(0)
            root_body(opened, restored, 2, prefix, gap, suffix, core)
            restored.seek(0)
            rectangle(restored, dst, 2, 9, prefix, gap, suffix, restrict=True)

    machine = Product((3, 5), 8, 136, exchange)
    row = one(machine, -741503, 466013)
    assert calls["shuttles"] == 138 and row["H_calls"] == 157248
    return {**row, **calls, "rank": core.n, "stage_body_records": 81**2}


def matched(*, wide=False):
    cases = [
        ((9,), 24, 224, [-((1 << 120) - 1), (1 << 119) + (1 << 96) + (1 << 49) + 1]),
        ((3, 5), 8, 136, [-741503, 466013]),
    ]
    if wide:
        cases.append(((9, 25), 8, 136, [-741503, 466013]))
    for sides, b, P, values in cases:
        for constructor in (PackProduct, Product):
            counts = Counter()

            def charged(src, dst, bits, prefix, gap, suffix):
                counts[bits] += 1
                ordinary_swap(src, dst, bits, prefix, gap, suffix)

            start = perf_counter()
            machine = (
                constructor(sides, b, P, charged)
                if constructor is Product
                else constructor(sides, b, P)
            )
            wall = perf_counter() - start
            yield {
                "path": constructor.__module__,
                "true_sides": sides,
                "padded_sites": machine.total,
                "setup_seconds": round(wall, 4),
                **one(machine, *values),
                "physical_shuttles_by_width": dict(counts),
            }


if __name__ == "__main__":
    import json, sys

    for row in matched(wide="--wide" in sys.argv):
        print(json.dumps(row), flush=True)
