#!/usr/bin/env python3
"""Exact finite corroboration of the Gray-layout stable-lane theorem."""

import argparse
from bisect import bisect_left
from collections import deque
import hashlib
import json
from pathlib import Path
import sys


MAX_BITS = 16
PACKAGE_FILES = (
    "README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py"
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, lo, hi):
    require(type(value) is int and lo <= value <= hi, "integer outside domain")


def fibonacci(index):
    integer(index, 0, MAX_BITS + 2)
    a, b = 0, 1
    for _ in range(index):
        a, b = b, a + b
    return a


def gray_order(bits):
    integer(bits, 0, MAX_BITS)
    return tuple(x ^ (x >> 1) for x in range(1 << bits))


def permutation(order):
    require(type(order) is tuple, "permutation must be a tuple")
    integer(len(order), 1, 1 << MAX_BITS)
    require(all(type(x) is int for x in order), "record IDs must be integers")
    require(sorted(order) == list(range(len(order))), "invalid permutation")


def inverse_order(order):
    permutation(order)
    result = [0] * len(order)
    for position, record in enumerate(order):
        result[record] = position
    return tuple(result)


def patience_certificate(order):
    """Return lane of each record and a decreasing position witness."""
    permutation(order)
    tails, ends = [], []
    previous = [-1] * len(order)
    lane_of = [-1] * len(order)
    for position, record in enumerate(order):
        lane = bisect_left(tails, -record)
        lane_of[record] = lane
        if lane:
            previous[position] = ends[lane - 1]
        if lane == len(tails):
            tails.append(-record)
            ends.append(position)
        else:
            tails[lane] = -record
            ends[lane] = position
    witness, position = [], ends[-1]
    for _ in range(len(tails)):
        require(position >= 0, "short predecessor chain")
        witness.append(position)
        position = previous[position]
    require(position == -1, "long predecessor chain")
    return tuple(lane_of), tuple(reversed(witness)), len(tails)


def check_decreasing(order, witness, width):
    permutation(order)
    integer(width, 1, len(order))
    require(type(witness) is tuple and len(witness) == width, "wrong witness size")
    for position in witness:
        integer(position, 0, len(order) - 1)
    for left, right in zip(witness, witness[1:]):
        require(left < right and order[left] > order[right], "not decreasing")


def replay_lanes(order, lane_of, width):
    """Split in input order, then merge whole symbolic records literally."""
    permutation(order)
    integer(width, 1, len(order))
    require(type(lane_of) is tuple and len(lane_of) == len(order), "bad lane map")
    for lane in lane_of:
        integer(lane, 0, width - 1)
    queues = [deque() for _ in range(width)]
    for record, lane in enumerate(lane_of):
        queues[lane].append((record, (record * 37) ^ 0x5A5A))
    output = []
    for record in order:
        queue = queues[lane_of[record]]
        require(bool(queue), "read from empty lane")
        actual = queue.popleft()
        require(actual == (record, (record * 37) ^ 0x5A5A), "unstable lane")
        output.append(actual[0])
    require(tuple(output) == order, "wrong output")
    require(all(not queue for queue in queues), "unconsumed record")
    return len(output)


def quadratic_extrema(order):
    """Independent predecessor DP, without patience sorting or reflection."""
    permutation(order)
    require(len(order) <= 1024, "quadratic oracle capacity")
    increasing, decreasing = [1] * len(order), [1] * len(order)
    for right in range(len(order)):
        for left in range(right):
            if order[left] < order[right]:
                increasing[right] = max(increasing[right], increasing[left] + 1)
            else:
                decreasing[right] = max(decreasing[right], decreasing[left] + 1)
    return max(increasing), max(decreasing)


def exhaustive_lane_minimum(order):
    """Independent subset DP over every increasing chain and partition."""
    permutation(order)
    require(len(order) <= 8, "subset oracle capacity")
    size = 1 << len(order)
    chains = [False] * size
    chains[0] = True
    for mask in range(1, size):
        values = [value for i, value in enumerate(order) if mask & (1 << i)]
        chains[mask] = all(a < b for a, b in zip(values, values[1:]))
    costs = [len(order) + 1] * size
    costs[0] = 0
    for mask in range(1, size):
        for chain in range(1, size):
            if chain & mask == chain and chains[chain]:
                costs[mask] = min(costs[mask], costs[mask ^ chain] + 1)
    return costs[-1]


def composition_bound(order, passes):
    """Check tuple coloring of a literal sequence of stable passes."""
    permutation(order)
    require(1 <= len(passes) <= 8, "bad pass list")
    incoming = tuple(range(len(order)))
    histories = [()] * len(order)
    product = 1
    for outgoing, lane_of, width in passes:
        permutation(outgoing)
        require(len(outgoing) == len(order), "pass changes record set")
        integer(width, 1, len(order))
        require(len(lane_of) == len(order), "bad intermediate lane map")
        queues = [deque() for _ in range(width)]
        for record in incoming:
            integer(lane_of[record], 0, width - 1)
            queues[lane_of[record]].append(record)
            histories[record] += (lane_of[record],)
        for record in outgoing:
            queue = queues[lane_of[record]]
            require(bool(queue) and queue.popleft() == record, "unstable pass")
        require(all(not queue for queue in queues), "pass loses records")
        incoming = outgoing
        product *= width
    require(incoming == order, "wrong final order")
    last = {}
    for record in incoming:
        history = histories[record]
        require(last.get(history, -1) < record, "tuple class reverses input")
        last[history] = record
    require(len(last) <= product, "too many tuple classes")
    return product


def shear_passes(bits):
    """Low-to-high adjacent address shears give a two-lane factorization."""
    integer(bits, 1, 8)
    positions = list(range(1 << bits))
    incoming = tuple(positions)
    passes = []
    for bit in range(bits - 1):
        positions = [x ^ (((x >> (bit + 1)) & 1) << bit) for x in positions]
        outgoing = tuple(sorted(range(len(positions)), key=positions.__getitem__))
        relative_position = [0] * len(positions)
        for index, record in enumerate(incoming):
            relative_position[record] = index
        relative = tuple(relative_position[record] for record in outgoing)
        lane_relative, _, width = patience_certificate(relative)
        require(width == 2, "shear does not use two lanes")
        lane_of = tuple(lane_relative[relative_position[x]] for x in range(len(positions)))
        passes.append((outgoing, lane_of, width))
        incoming = outgoing
    require(tuple(positions) == gray_order(bits), "wrong shear product")
    return tuple(passes), incoming


def theorem_checks():
    counts = {"orders": 0, "routed_records": 0, "quadratic_oracles": 0,
              "subset_oracles": 0, "shear_compositions": 0}
    for bits in range(MAX_BITS + 1):
        order = gray_order(bits)
        if bits:
            lower = gray_order(bits - 1)
            reflected = lower + tuple((1 << (bits - 1)) + x for x in reversed(lower))
            require(order == reflected, "reflection identity fails")
        for candidate in (order, inverse_order(order)):
            lanes, witness, width = patience_certificate(candidate)
            require(width == fibonacci(bits + 1), "wrong Fibonacci lane count")
            check_decreasing(candidate, witness, width)
            counts["routed_records"] += replay_lanes(candidate, lanes, width)
            counts["orders"] += 1
            if bits <= 10:
                require(quadratic_extrema(candidate) ==
                        (fibonacci(bits + 2), fibonacci(bits + 1)), "DP disagrees")
                counts["quadratic_oracles"] += 1
            if bits <= 3:
                require(exhaustive_lane_minimum(candidate) == width, "partition disagrees")
                counts["subset_oracles"] += 1
        if 2 <= bits <= 8:
            passes, final = shear_passes(bits)
            product = composition_bound(final, passes)
            require(product >= fibonacci(bits + 1), "composition violates lower bound")
            counts["shear_compositions"] += 1
    return counts


def rejection_checks():
    bad_cases = (
        ("bits", -1), ("bits", True), ("bits", MAX_BITS + 1),
        ("order", (0, 0)), ("order", (False, 1)), ("order", (0, 2)),
        ("lanes", (0, 0, 0, 0)), ("lanes", (0, 1, 0, 2)),
        ("lanes", (0, 1, 0)), ("witness", (0, 1)),
        ("witness", (2, 1)), ("witness", (2, 4)),
    )
    order = gray_order(2)
    for kind, value in bad_cases:
        rejected = False
        try:
            if kind == "bits":
                gray_order(value)
            elif kind == "order":
                permutation(value)
            elif kind == "lanes":
                replay_lanes(order, value, 2)
            else:
                check_decreasing(order, value, 2)
        except ValueError:
            rejected = True
        require(rejected, "invalid fixture accepted")
    require(quadratic_extrema(gray_order(1)) == (2, 1), "LIS/LDS distinction lost")
    xor_order = tuple(x ^ 7 for x in range(8))
    require(quadratic_extrema(xor_order)[1] == 8, "XOR control incorrect")
    require(quadratic_extrema(gray_order(3))[1] == 3, "Gray control incorrect")
    return len(bad_cases) + 2


def receipt(counts):
    package = Path(__file__).resolve().parent
    hashes = {}
    for name in PACKAGE_FILES:
        with (package / name).open("rb") as source:
            payload = source.read(1024 * 1024 + 1)
        require(len(payload) <= 1024 * 1024, "package file capacity")
        hashes[name] = hashlib.sha256(payload).hexdigest()
    return {"status": "PASS_GRAY_LAYOUT_LANE_NUMBER", "counts": counts,
            "python": sys.version.split()[0], "file_sha256": hashes,
            "claim_type": "scoped written proof with finite corroboration"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    counts = theorem_checks()
    counts["controls"] = rejection_checks()
    print(json.dumps(receipt(counts), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
