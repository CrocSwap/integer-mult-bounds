#!/usr/bin/env python3
"""Exact finite corroboration of the two-bank support bound. Apache-2.0."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAX_STATES = 200_000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def fibonacci(index):
    require(type(index) is int and 0 <= index <= 4096, "Fibonacci index")
    left, right = 0, 1
    for _ in range(index):
        left, right = right, left + right
    return left


def scan_floor(density, exponent=0):
    require(type(density) is int and 1 <= density <= 2**1024, "density")
    require(type(exponent) is int and 0 <= exponent <= 1024, "exponent")
    for scans in range(2049):
        if 2**exponent * fibonacci(scans + 1) >= density:
            return scans
    raise ValueError("bounded Fibonacci search exhausted")


def check_profile(profile, scans, exponent):
    scale = 2**exponent
    require(profile[0] <= scale * fibonacci(scans + 2), "largest bank")
    require(profile[1] <= scale * fibonacci(scans + 1), "second bank")


def successors(profile, scans, exponent):
    """Overapproximate row-support unions, including every bank choice."""
    for target, source in itertools.permutations(range(len(profile)), 2):
        sizes = list(profile)
        sizes[target] += sizes[source]
        yield tuple(sorted(sizes, reverse=True)), scans + 1, exponent
    for rank in (1, 2):
        if exponent + rank <= 4:
            for target in range(len(profile)):
                sizes = list(profile)
                sizes[target] *= 2**rank
                yield tuple(sorted(sizes, reverse=True)), scans, exponent + rank


def abstract_profiles():
    layers = []
    for banks in range(2, 6):
        states = {((1,) * banks, 0, 0)}
        for depth in range(8):
            for profile, scans, exponent in states:
                check_profile(profile, scans, exponent)
            layers.append([banks, depth, len(states)])
            if depth < 7:
                following = set()
                for profile, scans, exponent in states:
                    following.update(successors(profile, scans, exponent))
                    require(len(following) <= MAX_STATES, "profile capacity")
                states = following
    return layers


def support(matrix, width):
    sizes = []
    for start in range(0, len(matrix), width):
        sizes.append(max(sum(value != 0 for value in row)
                         for row in matrix[start:start + width]))
    return tuple(sorted(sizes, reverse=True))


def shear(matrix, width, target, source, shift, scalar):
    require(target != source, "distinct shear banks")
    for row in range(width):
        old = matrix[target * width + row]
        incoming = matrix[source * width + (row + shift) % width]
        matrix[target * width + row] = [
            (a + scalar * b) % 5 for a, b in zip(old, incoming, strict=True)
        ]


def unary(matrix, width, bank, axis):
    """Invertible I+2X_axis over F5, with row support two."""
    saved = [row[:] for row in matrix[bank * width:(bank + 1) * width]]
    for row in range(width):
        matrix[bank * width + row] = [
            (a + 2 * b) % 5
            for a, b in zip(saved[row], saved[row ^ (1 << axis)], strict=True)
        ]


def identity(dimension):
    return [[int(row == column) for column in range(dimension)]
            for row in range(dimension)]


def literal_traces():
    checked = 0
    for banks, bits, seed in itertools.product(range(2, 6), range(1, 5), range(6)):
        width = 2**bits
        matrix = identity(banks * width)
        scans, exponent = 0, 0
        for step in range(24):
            target = (seed + step) % banks
            if step % 5 == 2:
                unary(matrix, width, target, (seed + step) % bits)
                exponent += 1
            else:
                source = (target + 1 + step % (banks - 1)) % banks
                shear(matrix, width, target, source, step % width, 1 + step % 4)
                scans += 1
            # A per-bank address permutation does not change support.
            start = target * width
            matrix[start:start + width] = matrix[start:start + width][::-1]
            check_profile(support(matrix, width), scans, exponent)
            checked += 1
    return checked


def chirp_densities():
    """Direct tensor entries of C=[[alpha,beta],[beta,alpha]], modulo five."""
    rows = []
    for bits in range(1, 8):
        width = 2**bits
        for output in range(width):
            entries = []
            for incoming in range(width):
                entry = 1
                for axis in range(bits):
                    entry = entry * (2 if (output ^ incoming) >> axis & 1 else 4) % 5
                entries.append(entry)
            require(all(entries), "dense chirp tensor row")
        rows.append([bits, width, scan_floor(width)])
    return rows


def boundary_controls():
    rejected = 0
    for density, exponent in ((2, 0), (8, 0), (16, 0), (8, 1), (128, 2)):
        floor = scan_floor(density, exponent)
        require(floor > 0, "positive control floor")
        require(2**exponent * fibonacci(floor) < density, "one fewer scan rejects")
        rejected += 1
    for args in ((0, 0), (True, 0), (8, -1), (8, True)):
        try:
            scan_floor(*args)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid argument accepted")
    # Permitting buffered same-bank additions invalidates this alphabet.
    matrix = identity(16)
    for axis in range(3):
        unary(matrix, 8, 0, axis)
    shear(matrix, 8, 1, 0, 0, 1)
    require(support(matrix, 8)[1] == 8 > fibonacci(5), "same-bank boundary")
    try:
        check_profile(support(matrix, 8), 4, 0)
    except ValueError:
        rejected += 1
    else:
        raise ValueError("same-bank mutant accepted")
    return rejected


def build_receipt():
    layers = abstract_profiles()
    result = {
        "schema": "two-bank-fibonacci-support/v1",
        "abstract_layers": layers,
        "abstract_states": sum(row[2] for row in layers),
        "literal_prefixes": literal_traces(),
        "chirp_rows": chirp_densities(),
        "rejection_controls": boundary_controls(),
        "larger_floors": [[bits, scan_floor(2**bits)] for bits in (8, 16, 32, 64)],
    }
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    result["source_sha256"] = {
        name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in names
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="author a new, source-bound receipt")
    args = parser.parse_args()
    result = build_receipt()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write is not None:
        with args.write.open("x", encoding="utf-8") as stream:
            require(stream.write(encoded) == len(encoded), "complete receipt write")
    else:
        expected = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
        require(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
                "complete source-bound receipt mismatch")
    print("PASS_FIBONACCI_SCAN_FLOOR " + json.dumps({
        key: value for key, value in result.items() if key not in ("source_sha256", "abstract_layers")
    }, sort_keys=True))


if __name__ == "__main__":
    main()
