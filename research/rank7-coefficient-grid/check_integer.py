# SPDX-License-Identifier: Apache-2.0
"""Independent fixed-denominator replay; no Fraction or production row imports."""

import argparse
import gzip
import hashlib
import json
from math import gcd
from pathlib import Path

MAX_EVENTS = 30_000
MAX_SUPPORT = 4096
MAX_WORD = 256
MAX_REGISTERS = 1024
INPUTS = 632
PORTS = 112


def require(condition, message):
    if not condition:
        raise ValueError(message)


def register(value):
    require(isinstance(value, (list, tuple)) and len(value) == 2, "register shape")
    kind, index = value
    require(kind in ("L", "C", "Z"), "register kind")
    require(type(index) is int and 0 <= index < MAX_REGISTERS, "register index")
    return kind, index


def quotient(numerator, denominator):
    require(type(numerator) is type(denominator) is int, "integer quotient")
    require(denominator != 0, "nonzero denominator")
    value, remainder = divmod(numerator, denominator)
    require(remainder == 0, "exact fixed-grid divisibility")
    return value


def encode(row, denominator):
    result = []
    for (variable, word), numerator in sorted(row.items()):
        common = gcd(abs(numerator), denominator)
        result.append(
            [variable, list(word), numerator // common, denominator // common]
        )
    return result


def ratio(numerator, denominator):
    common = gcd(abs(numerator), denominator)
    numerator, denominator = numerator // common, denominator // common
    return str(numerator) if denominator == 1 else f"{numerator}/{denominator}"


def scalar(state, gate):
    require(isinstance(gate, list) and 2 <= len(gate) <= 5, "scalar shape")
    kind, target = gate[0], register(gate[1])
    increment = {}
    if kind == "clear":
        require(len(gate) == 2, "clear arity")
        row = {}
    elif kind == "copy":
        require(len(gate) == 3, "copy arity")
        row = dict(state[register(gate[2])])
    elif kind == "scale":
        require(len(gate) == 4, "scale arity")
        row = {}
        for atom, value in state[target].items():
            changed = quotient(value * gate[2], gate[3])
            if changed:
                row[atom] = changed
    else:
        require(kind == "add" and len(gate) == 5, "ADD shape")
        source = register(gate[2])
        require(target != source, "distinct ADD ports")
        row = dict(state[target])
        for atom, value in state[source].items():
            delta = quotient(value * gate[3], gate[4])
            if delta:
                increment[atom] = delta
            changed = row.get(atom, 0) + delta
            if changed:
                row[atom] = changed
            else:
                row.pop(atom, None)
    require(len(row) <= MAX_SUPPORT, "bounded integer support")
    state[target] = row
    require(len(state) <= MAX_REGISTERS, "bounded register count")
    return target, row, increment


def step(state, event):
    require(isinstance(event, list) and event, "native event shape")
    kind = event[0]
    if kind == "scalar":
        require(len(event) == 3, "scalar event arity")
        return scalar(state, event[1])
    if kind == "zero_buffer":
        require(len(event) == 3, "zero-buffer arity")
        target = register(["Z", event[2]])
        if event[1] == "alloc":
            require(target not in state, "fresh zero buffer")
            state[target] = {}
            require(len(state) <= MAX_REGISTERS, "bounded zero-buffer inventory")
        else:
            require(event[1] == "free" and target in state, "zero-buffer lifetime")
            require(not state[target], "private zero return")
            del state[target]
        return None
    if kind == "warp":
        require(len(event) == 5, "warp arity")
        target, operation = register(event[1]), event[2]
        require(type(operation) is int and operation != 0, "warp symbol")
        row = {}
        for (variable, word), value in state[target].items():
            moved = word[1:] if word and word[0] == -operation else (operation,) + word
            require(len(moved) <= MAX_WORD, "bounded free word")
            row[variable, moved] = value
        require(len(row) == len(state[target]), "injective free-word action")
        state[target] = row
        return target, row, {}
    require(
        kind in ("phase", "adapter", "residual_adapter", "climb", "center"),
        "known omitted native event",
    )
    return None


def statistics(row, fractional_bits, precision):
    require(len(row) <= MAX_SUPPORT, "bounded row")
    positive = sum(value for value in row.values() if value > 0)
    negative = -sum(value for value in row.values() if value < 0)
    limit = 1 << (precision - 1)
    low = -limit * positive - (limit - 1) * negative
    high = (limit - 1) * positive + limit * negative
    depth = 0
    for value in row.values():
        require(type(value) is int and value != 0, "nonzero integer coefficient")
        require(abs(value).bit_length() <= 512, "bounded integer coefficient")
        valuation = (abs(value) & -abs(value)).bit_length() - 1
        depth = max(depth, max(0, fractional_bits - valuation))
    return positive + negative, low, high, depth


def endpoints(state, scale, backward):
    require(sum(key[0] == "L" for key in state) == INPUTS, "all dirty inputs retained")
    require(not any(key[0] == "Z" for key in state), "all zero buffers freed")
    for key, row in state.items():
        if key[0] == "L":
            index = key[1]
            require(index < INPUTS, "original dirty index")
            expected = {(index, ()): scale}
            if backward and index < PORTS:
                expected[index + PORTS, ()] = -scale
            elif not backward and PORTS <= index < 2 * PORTS:
                expected[index - PORTS, ()] = scale
        else:
            expected = {}
        require(row == expected, "complete dirty/private endpoint")


def check(events, fractional_bits, backward=False, precision=64):
    require(isinstance(events, list) and len(events) <= MAX_EVENTS, "bounded stream")
    require(type(fractional_bits) is int and 0 <= fractional_bits <= 128, "grid depth")
    require(type(precision) is int and 2 <= precision <= 128, "input precision")
    require(type(backward) is bool, "orientation")
    scale = 1 << fractional_bits
    state = {("L", index): {(index, ()): scale} for index in range(INPUTS)}
    limit = 1 << (precision - 1)
    peak, low, high, depth = scale, -limit * scale, (limit - 1) * scale, 0
    rows, adds, maximum_support = 0, 0, 1
    digest = hashlib.sha256()
    for index, event in enumerate(events):
        changed = step(state, event)
        if changed is None:
            continue
        target, row, increment = changed
        norm, lower, upper, current_depth = statistics(row, fractional_bits, precision)
        peak, low, high = max(peak, norm), min(low, lower), max(high, upper)
        depth, rows = max(depth, current_depth), rows + 1
        adds += event[0] == "scalar" and event[1][0] == "add"
        maximum_support = max(maximum_support, len(row))
        entry = [index, list(target), encode(row, scale), encode(increment, scale)]
        digest.update(json.dumps(entry, sort_keys=True, separators=(",", ":")).encode())
        digest.update(b"\n")
    endpoints(state, scale, backward)
    extent = max(high + 1, -low, 1)
    return {
        "fractional_bits": depth,
        "max_norm": ratio(peak, scale),
        "low": ratio(low, scale),
        "high": ratio(high, scale),
        "signed_width": 1 + (extent - 1).bit_length(),
        "ADDs": adds,
        "rows": rows,
        "max_support": maximum_support,
        "ledger_sha256": digest.hexdigest(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("programs", type=Path, help="LOCAL-PROGRAMS.json[.gz]")
    parser.add_argument("--precision", type=int, default=64)
    args = parser.parse_args()
    require(args.programs.stat().st_size <= 8_000_000, "bounded input file")
    opener = gzip.open if args.programs.suffix == ".gz" else open
    with opener(args.programs, "rt") as stream:
        raw = stream.read(8_000_001)
    require(len(raw) <= 8_000_000, "bounded decoded input")
    programs = json.loads(raw)
    result = {
        direction: check(programs[direction], depth, backward, args.precision)
        for direction, depth, backward in (("forward", 4, False), ("backward", 5, True))
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
