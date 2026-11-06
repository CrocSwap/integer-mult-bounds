#!/usr/bin/env python3
"""Exact replay of the fixed positive-half tape table; writes no files."""

import hashlib
import json
from pathlib import Path
import sys


PACKAGE = Path(__file__).resolve().parent
MAX_WIDTH = 4096
SYMBOLS = frozenset(("0", "1", "P0", "P1", "S0", "S1"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_table():
    document = json.loads((PACKAGE / "TABLE.json").read_text())
    require(document["schema_version"] == 1, "table schema")
    require(document["columns"] == [
        "state", "read", "coin", "next_state", "write", "move"
    ], "table columns")
    rows = document["rows"]
    require(len(rows) == 66, "table row count")
    table = {}
    for state, read, coin, target, write, move in rows:
        require(read in SYMBOLS and write in SYMBOLS, "table alphabet")
        require(type(coin) is int and coin in (0, 1), "table coin")
        require(type(move) is int and move in (-1, 0, 1), "table move")
        require(state[0] in "FI" and target[0] in "FIH", "table state")
        key = state, read, coin
        require(key not in table, "duplicate table key")
        table[key] = target, write, move
    return table


def check_local_injectivity(table):
    """Standard sufficient local criterion for a reversible partial TM."""
    for mode in ("F", "I"):
        outputs = set()
        directions = {}
        for (state, read, coin), (target, write, move) in table.items():
            if not state.startswith(mode):
                continue
            key = target, write, coin
            require(key not in outputs, "noninjective local table")
            outputs.add(key)
            require(target not in directions or directions[target] == move,
                    "ambiguous incoming head direction")
            directions[target] = move


def tape_for(width, value, residue=0, origin=0):
    require(type(width) is int and 2 <= width <= MAX_WIDTH, "width")
    require(-(1 << (width - 1)) <= value < 1 << (width - 1), "signed input")
    require(residue in (0, 1) and 0 <= origin <= 16, "layout")
    bits = [(value >> bit) & 1 for bit in range(width)]
    return (["outside-left"] * origin + ["P" + str(residue)]
            + [str(bit) for bit in bits[:-1]] + ["S" + str(bits[-1])]
            + ["outside-right", "spectator"])


def execute(table, tape, width, coin, mode, origin=0):
    require(type(width) is int and 2 <= width <= MAX_WIDTH, "width")
    require(type(coin) is int and coin in (0, 1), "coin")
    require(mode in ("F", "I") and 0 <= origin <= 16, "entry")
    require(len(tape) == origin + width + 3, "extent")
    require(tape[origin] in (("P0",) if mode == "F" else ("P0", "P1")),
            "parity marker")
    require(all(cell in ("0", "1") for cell in
                tape[origin + 1:origin + width]), "payload alphabet")
    require(tape[origin + width] in ("S0", "S1"), "sign marker")
    data = tape.copy()
    head, state = origin, mode + "0"
    left = right = head
    for steps in range(1, 4 * width + 2):
        require(origin <= head <= origin + width, "head escaped active interval")
        key = state, data[head], coin
        require(key in table, "undefined transition")
        state, data[head], move = table[key]
        head += move
        left, right = min(left, head), max(right, head)
        if state == "H":
            require(head == origin, "head did not return")
            require(left == origin and right == origin + width, "visited interval")
            return data, steps
    raise ValueError("transition budget exhausted")


def exact_steps(width, value, coin):
    quotient, residue = divmod(value, 2)
    if residue == 0 or coin == 1:
        return 2 * width + 1
    stop = width - 1
    for index in range(width):
        if not (quotient >> index) & 1:
            stop = index
            break
    return 2 * width + 2 * stop + 3


def check_case(table, width, value, coin, origin=0):
    before = tape_for(width, value, origin=origin)
    after, forward_steps = execute(table, before, width, coin, "F", origin)
    quotient, residue = divmod(value, 2)
    expected = quotient + residue * (1 - coin)
    require(after == tape_for(width, expected, residue, origin), "forward endpoint")
    restored, inverse_steps = execute(table, after, width, coin, "I", origin)
    require(restored == before, "inverse endpoint or spectator restoration")
    require(forward_steps == inverse_steps == exact_steps(width, value, coin),
            "exact transition count")
    return forward_steps + inverse_steps


def check_exhaustive(table):
    cases = transitions = 0
    for width in range(2, 13):
        for value in range(-(1 << (width - 1)), 1 << (width - 1)):
            for coin in (0, 1):
                transitions += check_case(table, width, value, coin)
                cases += 1
    return {"cases": cases, "transitions": transitions}


def check_large_and_translated(table):
    cases = transitions = 0
    for width in (13, 16, 31, 64, 127, 256, 1024, 4096):
        bound = 1 << (width - 1)
        values = (-bound, -bound + 1, -3, -2, -1, 0, 1, 2, bound - 2, bound - 1)
        for value in values:
            for coin in (0, 1):
                transitions += check_case(table, width, value, coin)
                cases += 1
    for width in range(2, 9):
        for origin in (1, 7, 16):
            for value in (-(1 << (width - 1)), -1, 0, (1 << (width - 1)) - 1):
                for coin in (0, 1):
                    transitions += check_case(table, width, value, coin, origin)
                    cases += 1
    return {"cases": cases, "transitions": transitions}


def check_inverse_domain(table):
    accepted = rejected = 0
    for width in range(2, 9):
        bound = 1 << (width - 1)
        for value in range(-bound, bound):
            for residue in (0, 1):
                for coin in (0, 1):
                    original = 2 * (value - residue * (1 - coin)) + residue
                    valid = -bound <= original < bound
                    try:
                        result, _ = execute(table, tape_for(width, value, residue),
                                            width, coin, "I")
                    except ValueError:
                        require(not valid, "valid inverse input rejected")
                        rejected += 1
                    else:
                        require(valid and result == tape_for(width, original),
                                "invalid inverse input accepted")
                        accepted += 1
    return {"accepted": accepted, "rejected": rejected}


def expect_rejection(action, name):
    try:
        action()
    except ValueError:
        return name
    raise ValueError("control did not reject: " + name)


def check_controls(table):
    controls = []
    faults = [
        ("coin complement", ("FD1", "P0", 0), ("H", "P1", 0), 4, 1, 0),
        ("negative carry overflow", ("FI", "S1", 0), ("FR", "S1", -1), 4, -1, 0),
        ("inverse sign consistency", ("IU0", "S0", 0), ("IB", "S1", -1), 4, 0, 0),
        ("head return", ("FR", "P1", 0), ("H", "P1", 1), 4, 1, 0),
    ]
    for name, key, row, width, value, coin in faults:
        changed = dict(table)
        changed[key] = row
        controls.append(expect_rejection(
            lambda: check_case(changed, width, value, coin), name))
    for width, coin in ((1, 0), (MAX_WIDTH + 1, 0), (4, 2)):
        controls.append(expect_rejection(
            lambda: execute(table, tape_for(4, 0), width, coin, "F"),
            "entry domain " + str((width, coin))))
    corrupted = tape_for(4, 0)
    corrupted[4] = "0"
    controls.append(expect_rejection(
        lambda: execute(table, corrupted, 4, 0, "F"), "missing sign marker"))
    return controls


def main():
    require(len(sys.argv) == 1, "no command-line arguments are supported")
    table = load_table()
    check_local_injectivity(table)
    result = {
        "schema_version": 1,
        "table_rows": len(table),
        "exhaustive": check_exhaustive(table),
        "large_and_translated": check_large_and_translated(table),
        "inverse_domain": check_inverse_domain(table),
        "rejected_controls": check_controls(table),
    }
    result["sha256"] = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(PACKAGE.iterdir()) if path.is_file()
    }
    print(json.dumps(result, sort_keys=True))
    print("PASS_LINEAR_POSITIVE_HALF_TAPE")


if __name__ == "__main__":
    main()
