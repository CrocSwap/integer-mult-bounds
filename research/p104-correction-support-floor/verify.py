"""Exact support evidence for the first-final-ADD lower bound.

Produced by Nick Petalas. Apache-2.0.
The imported correction operator is Ali Romman's PR6537 construction.
"""

import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
DIMENSION = 799


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(raw, origin):
    require(len(raw) <= 1024 * 1024, "Source exceeds one MiB")
    require(hashlib.sha256(raw).hexdigest() == origin["sha256"], "Source hash")
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    require(blob == origin["git_blob"], "Source Git blob")


def load_program():
    origin = json.loads((PACKAGE / "ORIGIN.json").read_text(encoding="utf-8"))
    source = PACKAGE / "inputs/pr6537-RESULT.json"
    require(source.stat().st_size <= 1024 * 1024, "Source size")
    raw = source.read_bytes()
    authenticate(raw, origin)
    program = json.loads(raw)["correction"]
    require(isinstance(program, list) and len(program) == 74, "74 source gates")
    for gate in program:
        require(isinstance(gate, list) and len(gate) == 5, "Gate shape")
        op, dst, src, coefficient, frame = gate
        require(op == "ADD" and frame == 127, "Exact common-frame ADD")
        require(type(dst) is int and type(src) is int, "Integer register")
        require(0 <= dst < DIMENSION and 0 <= src < DIMENSION, "Register range")
        require(dst != src and isinstance(coefficient, str), "ADD operands")
        require(len(coefficient) <= 32 and Fraction(coefficient) != 0, "Coefficient")
    return program, raw, origin


def forward_rows(program):
    rows = [{i: Fraction(1)} for i in range(DIMENSION)]
    for _, dst, src, coefficient, _ in program:
        scale = Fraction(coefficient)
        for column, value in tuple(rows[src].items()):
            total = rows[dst].get(column, Fraction(0)) + scale * value
            if total:
                rows[dst][column] = total
            else:
                rows[dst].pop(column, None)
    return rows


def backward_row(program, output):
    row = {output: Fraction(1)}
    for _, dst, src, coefficient, _ in reversed(program):
        total = row.get(src, Fraction(0)) + row.get(dst, Fraction(0)) * Fraction(coefficient)
        if total:
            row[src] = total
        else:
            row.pop(src, None)
    return row


def support_floor(sizes):
    require(len(sizes) <= DIMENSION, "Output count bound")
    require(all(type(s) is int and 2 <= s <= DIMENSION for s in sizes), "Dense rows")
    return len(sizes) + min(sizes) - 2 if sizes else 0


def binary_controls():
    gates = tuple((dst, src) for dst in range(3) for src in range(3) if dst != src)
    checked = 0
    for length in range(6):
        for word in itertools.product(gates, repeat=length):
            rows = [1, 2, 4]
            for dst, src in word:
                rows[dst] ^= rows[src]
            dense = [row.bit_count() for row in rows if row.bit_count() >= 2]
            require(support_floor(dense) <= length, "Binary circuit violates bound")
            checked += 1
    require(checked == sum(6**length for length in range(6)), "Complete word count")
    return checked


def sharp_controls():
    checked = 0
    for count in range(1, 9):
        for size in range(2, 9):
            rows = [1 << i for i in range(size + count - 1)]
            for src in range(1, size):
                rows[0] ^= rows[src]
            for dst in range(size, size + count - 1):
                rows[dst] ^= rows[0]
            dense = [row.bit_count() for row in rows if row.bit_count() >= 2]
            require(len(dense) == count and min(dense) == size, "Attaining supports")
            require(support_floor(dense) == count + size - 2, "Sharp general bound")
            checked += 1
    return checked


def rejection_controls(raw, origin):
    rejected = 0
    for sizes in ([1], [0], [-1], [800], [True], [2] * 800):
        try:
            support_floor(sizes)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("Invalid support accepted")
    for changed in (raw + b"\n", raw[:-1], raw.replace(b"ADD", b"SUB", 1)):
        require(changed != raw, "Actual byte corruption")
        try:
            authenticate(changed, origin)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("Changed source accepted")
    return rejected


def main():
    program, raw, origin = load_program()
    rows = forward_rows(program)
    changed = [i for i in range(DIMENSION) if rows[i] != {i: Fraction(1)}]
    for output in range(DIMENSION):
        require(rows[output] == backward_row(program, output), "Independent row extraction")
    sizes = [len(rows[i]) for i in changed]
    histogram = dict(sorted(Counter(sizes).items()))
    require(histogram == {12: 3, 13: 19, 25: 6}, "Complete support histogram")
    floor = support_floor(sizes)
    require(floor == 38 and len(changed) == 28, "Source-specific lower bound")
    result = {
        "status": "PASS_P104_CORRECTION_SUPPORT_FLOOR",
        "claim_type": "scoped written circuit lower bound with exact finite support evidence",
        "source_sha256": origin["sha256"],
        "changed_rows": changed,
        "row_supports": {str(i): len(rows[i]) for i in changed},
        "support_histogram": histogram,
        "minimum_support": min(sizes),
        "add_lower_bound": floor,
        "credited_add_upper_bound": len(program),
        "independent_rows": DIMENSION,
        "binary_words": binary_controls(),
        "sharp_fixtures": sharp_controls(),
        "rejection_controls": rejection_controls(raw, origin),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
