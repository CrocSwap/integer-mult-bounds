"""Measure full scalar and split chart routes on the same eight-trit body."""

import argparse
from array import array
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from io import BufferedIOBase, BytesIO, RawIOBase
from itertools import product
import json
from pathlib import Path
import sys
from tempfile import TemporaryFile
from time import perf_counter


BODY = 3**8
BYTES = 4
FORWARD = (("add", 1, 0, Fraction(1, 2)), ("swap", 0, 1))
BACK = (("swap", 0, 1), ("add", 1, 0, Fraction(-1, 2)))


class TapeCount:
    """Observe the route's file objects, including its internal temporary tapes."""

    operations = {"read", "write", "truncate", "seek", "close"}

    def __init__(self, source, target, size):
        self.sizes = {source: size, target: 0}
        self.live = self.peak = size
        self.bytes = Counter()
        self.calls = Counter()
        self.pending = []

    def observe(self, frame, event, instruction):
        if event not in ("c_call", "c_return", "c_exception"):
            return
        name = getattr(instruction, "__name__", None)
        tape = getattr(instruction, "__self__", None)
        if name not in self.operations or not isinstance(
            tape, (BufferedIOBase, RawIOBase, BytesIO)
        ):
            return
        if event == "c_call":
            self.pending.append((tape, name, tape.tell() if not tape.closed else 0))
            return
        start_tape, start_name, before = self.pending.pop()
        assert tape is start_tape and name == start_name
        if event == "c_exception":
            return
        self.calls[name] += 1
        old = self.sizes.get(tape, 0)
        new = old
        if name == "close":
            new = 0
        elif name == "truncate":
            # The pinned erase routine truncates at the current zero position.
            new = tape.tell()
        elif name == "seek":
            self.bytes["absolute_seek"] += abs(tape.tell() - before)
        else:
            position = tape.tell()
            self.bytes[name] += position - before
            if name == "write":
                new = max(old, position)
        self.sizes[tape] = new
        self.live += new - old
        self.peak = max(self.live, self.peak)


def token_block(row):
    result = array("I", range(row * BODY, (row + 1) * BODY))
    if result.itemsize != BYTES:
        raise ValueError("The host unsigned integer width must be four bytes")
    if sys.byteorder != "little":
        result.byteswap()
    return result.tobytes()


def row_action(row, modulus, inverse):
    x, y, z, t = row
    half = pow(2, -1, modulus)
    if inverse:
        return y, (x - half * y) % modulus, t, (z - half * t) % modulus
    return (y + half * x) % modulus, x, (t + half * z) % modulus, z


def check(predecessor, mode):
    sys.path.insert(0, str(predecessor))
    from streaming_routes import cold_swap_tape, erase, regular, right_route

    exponent = 2 if mode == "scalar" else 1
    labels = 81 if mode == "split-matched" else 1
    low_values = [row for row in product(range(3), repeat=4) if regular(row, 2)]
    lows = {row: i for i, row in enumerate(low_values)}
    high_values = list(product(range(3 ** (exponent - 1)), repeat=4))
    highs = {row: i for i, row in enumerate(high_values)}
    rows = len(lows) * len(highs)
    size = rows * labels * BODY * BYTES
    flips = [bytes(x ^ (i + 1) for x in range(256)) for i in range(len(lows))]

    def route(source, target, word):
        tally = TapeCount(source, target, size)
        source.seek(0)
        sys.setprofile(tally.observe)
        try:
            right_route(
                source,
                target,
                2,
                exponent,
                1,
                labels * BODY * BYTES,
                word,
                previous_swap=cold_swap_tape,
            )
        finally:
            sys.setprofile(None)
        assert not tally.pending and target.tell() == size and tally.live == 2 * size
        return {
            "bytes": dict(tally.bytes),
            "peak_live_file_bytes": tally.peak,
            "file_operations": dict(tally.calls),
        }

    started = perf_counter()
    with (
        TemporaryFile() as source,
        TemporaryFile() as placed,
        TemporaryFile() as changed,
        TemporaryFile() as result,
    ):
        for r in range(rows * labels):
            source.write(token_block(r))
        forward = route(source, placed, FORWARD)
        erase(source)
        placed.seek(0)
        carry_low_rows = 0
        for j, low in enumerate(low_values):
            for high in high_values:
                actual = [v + 3 * w for v, w in zip(low, high, strict=True)]
                g = row_action(actual, 3**exponent, True)
                old_low = tuple(v % 3 for v in g)
                old_high = tuple(v // 3 for v in g)
                old = lows[old_low] * len(highs) + highs[old_high]
                if exponent > 1 and not any(high) and any(old_high):
                    carry_low_rows += 1
                for label in range(labels):
                    buf = placed.read(BODY * BYTES)
                    assert buf == token_block(old * labels + label)
                    changed.write(buf.translate(flips[j]))
        assert not placed.read(1)
        erase(placed)
        backward = route(changed, result, BACK)
        erase(changed)
        output = sha256()
        result.seek(0)
        for i, low in enumerate(low_values):
            mask = flips[lows[row_action(low, 3, False)]]
            for high_i in range(len(highs)):
                for label in range(labels):
                    row = (i * len(highs) + high_i) * labels + label
                    restored = result.read(BODY * BYTES)
                    assert restored == token_block(row).translate(mask)
                    output.update(restored)
        assert not result.read(1) and (exponent == 1 or carry_low_rows > 0)
        erase(result)
    return {
        "mode": mode,
        "genuine_matrices": rows,
        "body_records": BODY,
        "independent_suffix_labels": labels,
        "records": rows * labels * BODY,
        "payload_bytes": size,
        "destination_zero_high_with_nonzero_source_high": carry_low_rows,
        "forward": forward,
        "inverse": backward,
        "mutated_payload_sha256": output.hexdigest(),
        "seconds_including_checks": round(perf_counter() - started, 3),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("predecessor", type=Path)
    parser.add_argument("mode", choices=("scalar", "split", "split-matched"))
    args = parser.parse_args()
    print(json.dumps(check(args.predecessor.resolve(), args.mode), sort_keys=True))
