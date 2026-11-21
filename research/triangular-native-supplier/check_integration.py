"""Compare complete opaque banks and signed Fourier products with independent endpoints."""

from collections import Counter
from hashlib import sha256
from io import BytesIO
import json
from math import prod
from time import perf_counter
from unittest.mock import patch

from check_module_atoms import expected_packet, payload
from growing_binary import Weighted
from module_atoms import balanced_widths
from ordinary import rectangle
from streaming_routes import cold_swap_tape, work_tapes

from multiplier import Product, RetainedProduct, multiply_tapes
from receiver import Receiver
from tape_meter import Motion
from triangular_ordinary import root_body


def movement():
    dims = (48, 2, 3, 3, 3, 2, 3, 3, 3)
    data = payload(prod(dims))
    expected = expected_packet(
        data, dims, lambda row, old, a, b, c, g, x, y, z: (row, old, x, y, z, g, a, b, c)
    )
    observations = {}
    for name in ("previous", "direct"):
        prior = Counter()

        def charged(src, dst, width, prefix, gap, suffix):
            prior[width] += 1
            cold_swap_tape(src, dst, width, prefix, gap, suffix)

        layout = balanced_widths(1)
        core = (
            Weighted(2, layout, charged)
            if name == "previous"
            else Receiver(2, layout, charged, direct=True)
        )
        meter = Motion()
        with meter.tape(data) as source, meter.tape(b"") as target:
            with (
                patch("stack_tapes.TemporaryFile", meter.tape),
                patch("streaming_routes.TemporaryFile", meter.tape),
            ):
                core.body_ordinary(source, target, 3, 48, 2, 2, 4)
            assert meter.live == 2 * len(data)
            target.stream.seek(0)
            got = target.stream.read()
            assert got == expected
        assert meter.live == 0
        observations[name] = {
            "records": len(data) // 4,
            "input_bytes": len(data),
            "peak_tape_bytes": meter.peak,
            "earlier_swaps": dict(prior),
            "movement": dict(meter.bytes),
            "sha256": sha256(got).hexdigest(),
        }
    print(json.dumps(observations, sort_keys=True), flush=True)


def native_product():
    layout = balanced_widths(1)
    core = Receiver(2, layout, direct=True)
    calls = Counter()

    def two_trits(src, dst, bits, prefix, gap, suffix):
        # The diagnostic CRT requests exactly one bit. Pad both axes to the actual rank-two body.
        if bits != 1:
            raise ValueError("The finite control expects a one-bit CRT request")
        calls["physical_swaps"] += 1
        calls["padded_bytes"] += prefix * 81 * gap * suffix
        with work_tapes(2) as (prepared, result):
            rectangle(src, prepared, 2, 9, prefix, gap, suffix)
            prepared.seek(0)
            root_body(prepared, result, 2, prefix, gap, suffix, core)
            result.seek(0)
            rectangle(result, dst, 2, 9, prefix, gap, suffix, restrict=True)

    results = {}
    for label, factory in (
        ("previous", lambda: RetainedProduct((3, 5), 8, 136)),
        ("completed-packs", lambda: Product((3, 5), 8, 136)),
        ("physical-rank-two", lambda: Product((3, 5), 8, 136, two_trits)),
    ):
        start = perf_counter()
        machine = factory()
        built = perf_counter()

        def operand(value):
            return BytesIO(b"input" + value.to_bytes(3, "little") + b"/keep")

        a, b = operand(741503), operand(466013)
        a.seek(5)
        b.seek(5)
        out = BytesIO(b"out:" + bytes(5) + b"/keep")
        out.seek(4)
        sign, count, coefficients = machine.multiply_tapes(
            a, 3, b, 3, out, coefficients=True, left_negative=True
        )
        elapsed = perf_counter() - built
        assert (sign, count, a.tell(), b.tell(), out.tell()) == (True, 5, 5, 5, 9)
        assert coefficients == [11811, 10996, 4152, 868, 77] + [0] * 10
        assert out.getvalue() == b"out:" + (345550037539).to_bytes(5, "little") + b"/keep"
        results[label] = {
            "per_geometry_setup_seconds": round(built - start, 3),
            "product_seconds": round(elapsed, 3),
            "H_calls": machine.h_calls,
        }
    assert calls["physical_swaps"] > 0
    print(
        "signed product", -345550037539, "coefficients", coefficients[:5], dict(calls), flush=True
    )
    print(json.dumps(results, sort_keys=True), flush=True)


def public_files():
    cases = (
        (0, -99),
        (-71, 1),
        (-19, -37),
        (2**311 + 1, 2**139 - 1),
        (2**4333 - 65, -(2**4211 + 7)),
    )
    for x, y in cases:
        a, b = [abs(v).to_bytes((abs(v).bit_length() + 7) // 8, "little") for v in (x, y)]
        out = BytesIO()
        neg, count = multiply_tapes(
            BytesIO(a), len(a), BytesIO(b), len(b), out, left_negative=x < 0, right_negative=y < 0
        )
        assert count == len(out.getvalue())
        assert (-1 if neg else 1) * int.from_bytes(out.getvalue(), "little") == x * y
    print("public signed tapes", len(cases), "maximum bits", 4333, flush=True)
