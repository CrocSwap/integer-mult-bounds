#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent dense-dyadic audit of the pinned all-target P104 relay word."""

import argparse
import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PORTS = 104
HELPERS = 1031
SIZE = 2 * PORTS + HELPERS
EVENTS = 17625
CORE_EVENTS = 4058
MAX_EXPONENT = 64
MAX_BITS = 256


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_inputs():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    for item in sources["files"]:
        if item["usage"] == "input":
            data = (ROOT / item["path"]).read_bytes()
            require(hashlib.sha256(data).hexdigest() == item["sha256"], "source pin")
    for item in sources["vendored_inputs"]:
        data = (PACKAGE / item["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == item["sha256"], "vendored pin")
    core = ROOT / "research/p104-native-channel/inputs"
    witness = json.loads((core / "LOWRANK-WITNESS.json").read_text())
    fixture = json.loads((core / "P104-FIXTURE.json").read_text())
    word = json.loads((PACKAGE / "inputs/WORD.json").read_text())
    return witness, fixture, word


def frame(vectors):
    require(isinstance(vectors, list) and len(vectors) <= 9, "frame size")
    pivots = [0] * 9
    for value in vectors:
        require(type(value) is int and 0 < value < 512, "binary label")
        for bit in range(8, -1, -1):
            if value & (1 << bit):
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    for bit in range(9):
        for higher in range(bit + 1, 9):
            if pivots[higher] & (1 << bit):
                pivots[higher] ^= pivots[bit]
    return tuple(value for value in reversed(pivots) if value)


def contained(smaller, larger):
    for value in smaller:
        for pivot in larger:
            value = min(value, value ^ pivot)
        if value:
            return False
    return True


def geometry(witness, fixture):
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.add(tuple(row))
    for signs in product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            roots.add((1, *signs))
    puncture = fixture["section4_explicit_P104"]
    removed = {tuple(row) for row in puncture["F0"] + puncture["C"]}
    roots = sorted(roots - removed)
    require(len(roots) == PORTS, "P104 geometry")
    correction = []
    for t, target in enumerate(roots):
        row = []
        for s, source in enumerate(roots):
            dot = sum(a * b for a, b in zip(target, source, strict=True))
            require(dot % 4 == 0, "integral Gram entry")
            row.append(2 * int(t == s) - dot // 4)
        correction.append(row)
    require(sum(bool(x) for row in correction for x in row) == 4992, "correction support")
    initial = {name: frame(basis) for name, basis in witness["initial_frames"].items()}
    current = dict(initial)
    require(len(witness["program"]) == CORE_EVENTS, "core event count")
    for event in witness["program"]:
        if event[0] == "transport":
            require(current[event[1]] == frame(event[2]), "core transport entry")
            current[event[1]] = frame(event[3])
        elif event[0] == "zero":
            current["C"] = frame(event[2])
    final = {name: frame(basis) for name, basis in witness["final_frames"].items()}
    require(all(current[name] == value for name, value in final.items()), "core final frames")
    return correction, initial, final


def coefficient(value):
    require(isinstance(value, str) and len(value) <= 5, "coefficient encoding")
    rational = Fraction(value)
    require(rational in {Fraction(s, d) for s in (-4, -2, -1, 1, 2, 4)
                         for d in (1, 2, 4)}, "coefficient alphabet")
    exponent = rational.denominator.bit_length() - 1
    return rational.numerator, exponent


def index(value, limit):
    require(type(value) is int and 0 <= value < limit, "register index")
    return value


def check_word(word, initial, final):
    require(set(word) == {"lifetimes", "ops"}, "word schema")
    require(word["lifetimes"] == HELPERS, "helper count")
    ops = word["ops"]
    require(isinstance(ops, list) and len(ops) <= EVENTS, "event bound")
    require(ops and ops[0] == ["move_zero_all", HELPERS], "initialization")
    frames = [()] * HELPERS
    histogram, counts, gates = Counter(), Counter(), []
    cut = 0
    for position, op in enumerate(ops[1:], 1):
        require(isinstance(op, list) and op, "event shape")
        kind = op[0]
        require(kind in {"move", "read", "write", "shear"}, "event kind")
        counts[kind] += 1
        if kind == "move":
            require(len(op) == 3, "move arity")
            helper = index(op[1], HELPERS)
            target = frame(op[2])
            source = frames[helper]
            require(contained(source, target) and len(source) < len(target), "nested move")
            histogram[len(target) - len(source)] += 1
            frames[helper] = target
            continue
        require(len(op) == (4 if kind == "shear" else 5), "scalar arity")
        numerator, exponent = coefficient(op[3])
        if kind == "shear":
            dst, src = index(op[1], HELPERS), index(op[2], HELPERS)
            require(dst != src and frames[dst] == frames[src], "common shear frame")
            dst, src = 2 * PORTS + dst, 2 * PORTS + src
        else:
            require(type(op[4]) is int and op[4] in (0, CORE_EVENTS), "allowed cut")
            require(op[4] >= cut, "cut order")
            cut = op[4]
            boundary = initial if cut == 0 else final
            if kind == "read":
                helper, source = index(op[1], HELPERS), index(op[2], PORTS)
                require(frames[helper] == boundary[f"X{source}"], "source frame")
                dst, src = 2 * PORTS + helper, source
            else:
                target, helper = index(op[1], PORTS), index(op[2], HELPERS)
                require(frames[helper] == boundary[f"Y{target}"], "target frame")
                dst, src = PORTS + target, 2 * PORTS + helper
        gates.append((position, dst, src, numerator, exponent))
    full = frame([1 << bit for bit in range(9)])
    require(all(value == full for value in frames), "helper final frames")
    require(sum(rank * count for rank, count in histogram.items()) == 9 * HELPERS, "rank mass")
    return gates, dict(sorted(histogram.items())), dict(sorted(counts.items()))


@dataclass
class Row:
    values: list[int]
    exponent: int


def add_row(dst, src, numerator, exponent):
    require(len(dst.values) == len(src.values) == SIZE, "row width")
    scale = max(dst.exponent, src.exponent + exponent)
    require(scale <= MAX_EXPONENT + 2, "dyadic exponent capacity")
    left = 1 << (scale - dst.exponent)
    right = numerator << (scale - src.exponent - exponent)
    values = [left * a + right * b for a, b in zip(dst.values, src.values, strict=True)]
    common = 0
    for value in values:
        common |= abs(value)
    shift = min(scale, (common & -common).bit_length() - 1) if common else scale
    values = [value >> shift for value in values]
    scale -= shift
    require(scale <= MAX_EXPONENT and common.bit_length() <= MAX_BITS, "row capacity")
    return Row(values, scale)


def expected_row(register, correction, dual):
    values = [0] * SIZE
    values[register] = 2
    if not dual and PORTS <= register < 2 * PORTS:
        values[:PORTS] = correction[register - PORTS]
    if dual and register < PORTS:
        for target in range(PORTS):
            values[PORTS + target] = -correction[target][register]
    return values


def replay(gates, correction, dual=False):
    rows = []
    for register in range(SIZE):
        values = [0] * SIZE
        values[register] = 1
        rows.append(Row(values, 0))
    maximum, denominator = Fraction(1), 0
    norm_witness = denominator_witness = {"event": 0, "register": 0}
    for position, dst, src, numerator, exponent in gates:
        if dual:
            dst, src, numerator = src, dst, -numerator
        row = add_row(rows[dst], rows[src], numerator, exponent)
        rows[dst] = row
        norm = Fraction(sum(abs(value) for value in row.values), 1 << row.exponent)
        if norm > maximum:
            maximum, norm_witness = norm, {"event": position, "register": dst}
        if row.exponent > denominator:
            denominator = row.exponent
            denominator_witness = {"event": position, "register": dst}
    for register, row in enumerate(rows):
        wanted = expected_row(register, correction, dual)
        require(all(2 * actual == expected * (1 << row.exponent)
                    for actual, expected in zip(row.values, wanted, strict=True)),
                "endpoint coefficient")
    return {"max_row_l1": str(maximum), "norm_witness": norm_witness,
            "max_denominator_exponent": denominator,
            "denominator_witness": denominator_witness,
            "endpoint_coefficients": SIZE * SIZE,
            "scalar_gates": len(gates)}


def audit(witness, fixture, word):
    correction, initial, final = geometry(witness, fixture)
    gates, profile, counts = check_word(word, initial, final)
    forward = replay(gates, correction)
    dual = replay(gates, correction, dual=True)
    mass = sum(rank * count for rank, count in profile.items())
    available = Fraction(72 * 832, 9) + 56
    channel_profile = Counter(abs(len(frame(op[3])) - len(frame(op[2])))
                              for op in witness["program"] if op[0] == "transport")
    channel_mass = sum(rank * count for rank, count in channel_profile.items())
    require(channel_mass == 2368, "channel transport recount")
    return {"status": "PASS_P104_RELAY_GROWTH", "lifetimes": HELPERS,
            "independent_inputs": SIZE, "correction_nonzeros": 4992,
            "profile": {str(rank): count for rank, count in profile.items()},
            "operation_counts": counts, "rank_mass": mass,
            "forward": forward, "logical_inverse_transpose": dual,
            "fixed_template": {"allowed_total_rank_mass": str(available),
                               "channel_rank_mass": channel_mass,
                               "remaining_idle_mass": str(available - channel_mass),
                               "overfill": str(channel_mass + mass - available),
                               "local_only_moment_at_zero": str(Fraction(
                                   9 * (channel_mass + mass), 73 * 832))}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="Create a new receipt; never overwrite")
    args = parser.parse_args()
    witness, fixture, word = load_inputs()
    result = audit(witness, fixture, word)
    expected = json.loads((PACKAGE / "EXPECTED.json").read_text())
    require(result == expected, "receipt drift")
    encoded = json.dumps(result, indent=2) + "\n"
    if args.out:
        with args.out.open("x", encoding="utf-8") as stream:
            require(stream.write(encoded) == len(encoded), "receipt write")
    print(encoded, end="")


if __name__ == "__main__":
    main()
