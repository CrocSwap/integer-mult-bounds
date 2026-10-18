#!/usr/bin/env python3
"""Replay the row wrapper and compare a stored, fully typed receipt."""

import argparse
import json
import sys
from hashlib import sha256
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from source import PACKAGE, installed, require


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def inspect(count):
    require(count.tape.head == 1, "count head restored")
    cells = count.tape.cells[1:]
    end = cells.index(3)
    require(all(bit in (0, 1) for bit in cells[:end]), "binary count fixture")
    return sum(bit << i for i, bit in enumerate(cells[:end]))


def payload(tape):
    require(tape.head == 1, "payload head restored")
    return bytes(tape.cells[1:]).rstrip(bytes([4]))


def meters(tapes):
    return {
        key: sum(getattr(tape.meter, key) for tape in tapes)
        for key in ("reads", "writes", "moves")
    }


def rejected(action, message):
    try:
        action()
    except ValueError as error:
        require(message in str(error), "expected rejection reason: " + str(error))
        return
    raise ValueError("invalid fixture accepted: " + message)


def plans(padding, Count):
    digest = sha256()
    cases = 0
    for rows in range(1, 130):
        for stock in range(1, rows + 1):
            r, s = Count.literal(rows), Count.literal(stock)
            saved = bytes(r.tape.cells), bytes(s.tape.cells)
            padded, added = padding.plan_rows(r, s)
            actual = inspect(padded), inspect(added)
            expected = ((rows + stock - 1) // stock * stock, (-rows) % stock)
            require(
                actual == expected and rows <= actual[0] < 2 * rows,
                "independent division/ceiling oracle",
            )
            require(
                saved == (bytes(r.tape.cells), bytes(s.tape.cells)),
                "borrowed plan inputs",
            )
            digest.update(canonical([rows, stock, actual]).encode())
            for count in (r, s, padded, added):
                count.close()
            cases += 1
    return {"cases": cases, "sha256": digest.hexdigest()}


def row_permutation(data, prefixes, rows, body):
    # Independent fixture endpoint: rotate a whole row, depending on prefix.
    return bytes(
        data[(prefix * rows + row) * body + (column + prefix + 1) % body]
        for prefix in range(prefixes)
        for row in range(rows)
        for column in range(body)
    )


def wrapper_case(padding, Count, Tape, c, r, s, b, data):
    tapes = []

    class Observed(Tape):
        def __init__(self):
            super().__init__()
            tapes.append(self)

    original_type = padding.Tape
    padding.Tape = Observed
    source = Observed()
    for bit in data:
        source.append(bit)
    source.rewind()
    saved = bytes(source.cells)
    counts = tuple(Count.literal(v) for v in (c, r, s, b))
    before = meters(tapes)
    child_cost = {}

    def callee(padded, row_count):
        start = meters(tapes)
        rp = inspect(row_count)
        require(rp % s == 0, "callee receives exact stock divisor")
        out = Observed()
        for bit in row_permutation(payload(padded), c, rp, b):
            out.append(bit)
        out.rewind()
        child_cost.update({key: meters(tapes)[key] - start[key] for key in start})
        return out

    try:
        out = padding.complete(source, *counts[:3], counts[3], callee)
        expected = row_permutation(data, c, r, b)
        require(
            payload(out) == expected and bytes(source.cells) == saved,
            "complete genuine-row endpoint and preserved input",
        )
        v, vp = c * r * b, c * ((r + s - 1) // s * s) * b
        expected_cost = {
            "reads": 4 * v + 8 * vp + 12,
            "writes": v + 3 * vp,
            "moves": 4 * v + 8 * vp + 16,
        }
        # payload() inspects fixture cells without invoking the metered API.
        actual_cost = {
            key: meters(tapes)[key] - before[key] - child_cost[key] for key in before
        }
        require(actual_cost == expected_cost, "exact wrapper payload traffic")
        require(
            all(not payload(tape) for tape in tapes if tape not in (source, out)),
            "owned padded input and child output erased",
        )
        record = [c, r, s, b, sha256(payload(out)).hexdigest(), actual_cost]
        out.clear()
        return record
    finally:
        source.clear()
        for count in counts:
            count.close()
        padding.Tape = original_type


def wrappers(padding, Count, Tape):
    digest = sha256()
    cases = columns = 0
    for c in (1, 2, 3):
        for r in range(1, 13):
            for s in range(1, r + 1):
                for b in (1, 2, 5):
                    data = bytes(((j * 13) ^ (j >> 2)) & 1 for j in range(c * r * b))
                    digest.update(
                        canonical(
                            wrapper_case(padding, Count, Tape, c, r, s, b, data)
                        ).encode()
                    )
                    cases += 1
    for bit in range(40):
        data = bytes(int(j == bit) for j in range(40))
        digest.update(
            canonical(wrapper_case(padding, Count, Tape, 2, 5, 3, 4, data)).encode()
        )
        columns += 1
    return {
        "pattern_cases": cases,
        "basis_columns": columns,
        "sha256": digest.hexdigest(),
    }


def swapped_row_control(padding, counts, source, Tape):
    # A shape-correct genuine-row swap passes structural zero checks.
    # The endpoint oracle must detect it; runtime checks are not a proof
    # of the source-bound callee's pointwise-row contract.
    def bad_rows(padded, rows):
        data = bytearray(payload(padded))
        data[0], data[1] = data[1], data[0]
        out = Tape()
        for bit in data:
            out.append(bit)
        out.rewind()
        return out

    out = padding.complete(source, *counts, bad_rows)
    require(payload(out) != payload(source), "pointwise-row premise is indispensable")
    out.clear()


def controls(padding, Count, Tape):
    source = Tape()
    for bit in (1, 0, 1, 1, 0):
        source.append(bit)
    source.rewind()
    c, r, s, b = (Count.literal(v) for v in (1, 5, 3, 1))
    saved = bytes(source.cells)

    def fixture(kind):
        def child(padded, rows):
            if kind == "alias":
                return padded
            if kind == "abort":
                raise ValueError("aborted completed callee")
            out = Tape()
            data = bytearray(payload(padded))
            if kind == "nonzero":
                data[-1] = 1
            if kind == "short":
                data.pop()
            if kind == "long":
                data.append(0)
            for bit in data:
                out.append(bit)
            out.rewind()
            if kind == "head":
                out.step(1)
            return out

        return lambda: padding.complete(source, c, r, s, b, child)

    try:
        for kind, message in (
            ("alias", "distinct owned"),
            ("abort", "aborted"),
            ("nonzero", "added rows zero"),
            ("short", "binary row"),
            ("long", "exact complete"),
            ("head", "restores"),
        ):
            rejected(fixture(kind), message)
            require(
                bytes(source.cells) == saved and source.head == 1,
                "source survives rejected callee",
            )
        rejected(lambda: padding.plan_rows(s, r), "capacity")
        zero = Count.literal(0)
        try:
            rejected(lambda: padding.plan_rows(zero, s), "positive")
        finally:
            zero.close()

        swapped_row_control(padding, (c, r, s, b), source, Tape)
        return {"runtime_rejections": 8, "semantic_endpoint_control": 1}
    finally:
        source.clear()
        for count in (c, r, s, b):
            count.close()


def core():
    with installed() as (manifest, _root):
        import padding
        from cardinal_counts import Count
        from records import Tape

        record = {
            "predecessor_head": manifest["head"],
            "source_files": len(manifest["files"]),
            "plans": plans(padding, Count),
            "wrappers": wrappers(padding, Count, Tape),
            "controls": controls(padding, Count, Tape),
        }
    return record


def integration():
    with installed() as (_manifest, _root):
        import bootstrap

        require(_root == bootstrap.ROOT, "authenticated source import root")
        from integration_check import run_node

        return run_node()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", choices=("core", "integration"), default="core")
    parser.add_argument("--emit-to", type=Path)
    args = parser.parse_args()
    result = (core if args.suite == "core" else integration)()
    if args.emit_to is not None:
        target = args.emit_to.resolve()
        require(
            not target.is_relative_to(PACKAGE), "emit outside the immutable package"
        )
        with target.open("x") as output:
            output.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((PACKAGE / (args.suite.upper() + ".json")).read_text())
        require(
            canonical(result) == canonical(expected),
            "complete typed receipt comparison",
        )
    print(
        "PASS_COMPATIBLE_ROW_PADDING "
        + args.suite
        + " "
        + sha256(canonical(result).encode()).hexdigest()
    )


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError) as error:
        print("FAIL_COMPATIBLE_ROW_PADDING: " + str(error), file=sys.stderr)
        raise SystemExit(1) from None
