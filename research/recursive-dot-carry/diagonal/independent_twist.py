"""Replay the guarded first-payload-twist substitution on pinned #7834 code."""

import argparse
from hashlib import sha1
import importlib
import json
from math import isqrt, prod
from pathlib import Path
from random import Random
import sys
from unittest.mock import patch


SOURCE_BLOBS = {
    "fine_ring.py": "b18da6275e31ac0bcc4174ec86106532c0cb5958",
    "word_multiply.py": "b148a60eac955722520e193f8bde0687635407ee",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_source(directory):
    for name, expected in SOURCE_BLOBS.items():
        blob = (directory / name).read_bytes()
        actual = sha1(f"blob {len(blob)}\0".encode() + blob).hexdigest()
        require(actual == expected, name)
    sys.path.insert(0, str(directory))
    return importlib.import_module("fine_ring")


def root_checks(ring):
    count = 0
    for f in (16, 23, 128, 8192, 8193):
        expected = isqrt(1 << (2 * f - 1))
        for r in (4, 8, 16, 64, 256):
            for k, sign in ((r // 4, 1), (3 * r // 4, -1)):
                sampled = ring.root_word(k, 2 * r, f, ring.Trace())
                require(sampled == (sign * expected, expected) and expected.bit_length() == f,
                        (r, k, f, "root projection"))
                count += 1
    return count


def check_middle(ring, sources, radices, q, inverse):
    r, volume = radices[0], prod(radices)
    rng = Random(r * q + int(inverse))
    bound = 1 << (q - 1)
    values = [(bound, 0), (0, -bound)] + [
        (rng.randint(-bound // 2, bound // 2), rng.randint(-bound // 2, bound // 2))
        for _ in range(volume - 2)
    ]
    old, new = ring.Trace(), ring.Trace()
    want = ring.chirp_middle(values, sources, radices, q, inverse=inverse, trace=old)
    original = ring.scalar_diagonal
    diagonals = fused = 0

    def replace_second_diagonal(tape, diagonal, size, unit, conjugate=False):
        nonlocal diagonals
        diagonals += 1
        if diagonals != 2:
            return original(tape, diagonal, size, unit, conjugate)
        require(not conjugate and size == volume, "first twist ABI")
        diagonal.home()

        def substitute(i, record):
            nonlocal fused
            u, v = diagonal.read()
            if i % r not in (r // 4, 3 * r // 4):
                return ring.times(record, (u, v), unit, tape.trace)
            require(abs(u) == abs(v) > 0 and u.bit_length() == unit.bit_length() - 1, "root guard")
            x, y = record
            require(x * x + y * y <= unit * unit // 4, "payload radius")
            sign = 1 if u == v else -1
            a, b = x - sign * y, y + sign * x
            require(max(x.bit_length(), y.bit_length(), a.bit_length(), b.bit_length()) <= u.bit_length(),
                    "same-width operands")
            real = ring.mul(u, a, tape.trace)
            imag = ring.mul(u, b, tape.trace)
            require((real, imag) == (x * u - y * v, x * v + y * u), "exact raw complex return")
            fused += 1
            return ring.tz(real, unit), ring.tz(imag, unit)

        return ring.map_tape(tape, size, substitute)

    with patch.object(ring, "scalar_diagonal", replace_second_diagonal):
        result = ring.chirp_middle(values, sources, radices, q, inverse=inverse, trace=new)
    require(result == want and old.live == new.live == old.fast_words == new.fast_words == 0,
            "completed middle endpoint")
    require(diagonals == 5 and fused == 2 * volume // r, "guaranteed first twist count")
    require(old.scalar_products - new.scalar_products == 4 * volume // r, "guaranteed dispatch saving")
    return {
        "sources": sources, "radices": radices, "q": q, "inverse": inverse, "records_fused": fused,
        "original_scalar_dispatches": old.scalar_products, "new_scalar_dispatches": new.scalar_products,
        "live_numeric_bits_at_return": new.live,
    }


def kernel_width_control(ring):
    f, index = 16, 10
    trace = ring.Trace()
    phase, twist = ring.make_diagonals((5, 7), (8, 8), f + 5, f, trace)
    x, y = phase.cells[index]
    u, v = twist.cells[index]
    require(index % 8 == 2 and u == v > 0, "kernel control root")
    require(x * x + y * y <= 1 << (2 * f), "kernel disk")
    require(max(n.bit_length() for n in (x, y, u, v)) == f and (x - y).bit_length() == f + 1,
            "unguarded kernel mix widens")
    phase.release()
    twist.release()
    require(trace.live == 0, "kernel control cleanup")
    return {"index": index, "payload": [x, y], "phase": [u, v], "original_width": f, "mixed_width": f + 1}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    ring = load_source(parser.parse_args().source.resolve())
    print(json.dumps({
        "status": "PASS_GUARDED_FIRST_PAYLOAD_TWIST",
        "source_git_blobs": SOURCE_BLOBS,
        "root_projection_checks": root_checks(ring),
        "middle_controls": [
            check_middle(ring, sources, radices, q, inverse)
            for sources, radices, q in (((3, 1), (4, 2), 22), ((5, 7), (8, 8), 128), ((11, 5), (16, 8), 63))
            for inverse in (False, True)
        ],
        "kernel_width_control": kernel_width_control(ring),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
