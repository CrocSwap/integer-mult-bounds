#!/usr/bin/env python3
"""Replay the independently derived high-scaling traffic invoice."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from observe import Observer
from source import authenticated
from traffic import allocations, countdown, invoice, require

PACKAGE = Path(__file__).resolve().parent


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def counter_checks(data):
    observer = Observer(data)
    rows = []
    values = (0, 1, 2, 3, 7, 8, 15, 16, 31, 32, 63, 64, 65, 127, 129)
    for value in values:
        for padding in (0, 1, 7):
            digits = max(2, value.bit_length()) + padding
            arena = observer.modules["words"].Arena(digits)
            source = arena.input(value)
            initial = bytes(source.cells)
            started = observer.measured(arena)
            counter = observer.modules["stream"].Counter(source)
            for _ in range(value):
                require(not counter.finished, "early countdown finish")
                counter.decrement()
            require(counter.finished, "complete countdown")
            counter.close()
            measured = observer.measured(arena) - started
            require(measured == countdown(value, digits), "retained countdown identity")
            require(
                bytes(source.cells) == initial and source.head == 1,
                "countdown source restoration",
            )
            arena.free(source)
            rows.append([value, digits, measured])
    return {"cases": len(rows), "sha256": digest(rows)}


def scaling_checks(data):
    observer = Observer(data)
    rows = []
    for modulus in (3, 5, 7, 9, 15, 17, 25, 31, 33, 63, 65, 127, 129):
        for before in (1, 2, 5):
            for suffix in (1, 2, 3, 5, 7):
                for inverse in (False, True):
                    row = observer.run(modulus, before, suffix, inverse)
                    require(
                        row["traffic"]
                        == sum(invoice(modulus, before, suffix).values()),
                        "exact scaling invoice",
                    )
                    require(
                        row["allocations"] == allocations(modulus, before, suffix),
                        "allocation census",
                    )
                    require(
                        row["traffic"] < 1024 * modulus * before * suffix,
                        "canonical linear bound",
                    )
                    rows.append(row)
    for first, second in zip(rows[::2], rows[1::2], strict=True):
        require(first["traffic"] == second["traffic"], "equal doubling/halving traffic")
    return {
        "cases": len(rows),
        "addresses": sum(r["q"] * r["b"] * r["s"] for r in rows),
        "sha256": digest(rows),
    }


def controls(data):
    observer = Observer(data)
    base = observer.run(65, 2, 1)
    inflated = observer.run(65, 2, 1, extra=True)
    expected_extra = 2 * 2 * 65 * countdown(0, 8)
    require(
        inflated["traffic"] - base["traffic"] == expected_extra,
        "endpoint-preserving cost control",
    )
    padded = observer.run(3, 1, 1, digits=4096)
    require(padded["traffic"] == sum(invoice(3, 1, 1, 4096).values()), "padded formula")
    require(padded["traffic"] > 1024 * 3, "canonical width is necessary")
    return {
        "baseline": base,
        "extra_work": inflated,
        "extra": expected_extra,
        "padded": padded,
    }


def result():
    data = authenticated()
    return {
        "status": "PASS_HIGH_SCALING_TOTAL_TRAFFIC",
        "counters": counter_checks(data),
        "scaling": scaling_checks(data),
        "controls": controls(data),
        "scope": "Successful literal local logical-tape invoice; no physical caller, supplier or new kappa.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--emit",
        action="store_true",
        help="print fresh results without writing a receipt",
    )
    args = parser.parse_args()
    actual = result()
    if args.emit:
        print(json.dumps(actual, indent=2, sort_keys=True))
        return
    expected = json.loads((PACKAGE / "RESULT.json").read_text())
    require(canonical(actual) == canonical(expected), "complete typed receipt mismatch")
    print(
        actual["status"],
        "cases=" + str(actual["scaling"]["cases"]),
        "addresses=" + str(actual["scaling"]["addresses"]),
    )


if __name__ == "__main__":
    main()
