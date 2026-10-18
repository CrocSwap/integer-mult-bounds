#!/usr/bin/env python3
"""Exact old-prefix lifting of complete reached high-route traffic."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from invoice import predict, wrapper
from runtime import PACKAGE, load, require, run_case

PREFIXES = (1, 2, 3, 4, 7, 8, 9, 16, 17)
CONFIGURATIONS = (
    dict(q=3, width=1, fibre_value=3),
    dict(q=3, width=2, fibre_value=1),
    dict(q=3, width=2, fibre_value=3, inverse=True),
    dict(q=5, width=2, fibre_value=1, inverse=True),
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def check_receipt(actual, expected):
    require(canonical(actual) == canonical(expected), "complete typed receipt")


def check_wrapper(row):
    highs = row["q"] ** (4 * (row["width"] - 1))
    expected = wrapper(row["prefixes"], highs, row["fibre"])
    require(row["wrapper_traffic"] == expected, "exact wrapper invoice")
    volume = row["prefixes"] * row["cube_bits"]
    require(expected <= 265 * volume, "uniform wrapper bound")
    closed = row["disposed_traffic"] - row["cube_traffic"]
    require(
        closed == wrapper(row["prefixes"], highs, row["fibre"], True),
        "closed wrapper invoice",
    )
    require(closed <= 277 * volume, "uniform closed wrapper bound")


def check_lift(single, row):
    check_wrapper(row)
    require(
        row["traffic"] == predict(single["traffic"], row["prefixes"]), "prefix lift"
    )
    require(
        row["disposed_traffic"]
        == predict(single["traffic"], row["prefixes"], True, row["cube_bits"]),
        "disposed prefix lift",
    )
    require(
        row["native_calls"] == row["prefixes"] * single["native_calls"],
        "native call multiplicity",
    )
    require(
        row["native_traffic"] == row["prefixes"] * single["native_traffic"],
        "native traffic multiplicity",
    )


def group(runtime, parameters, prefixes):
    rows = [run_case(runtime, count, **parameters) for count in prefixes]
    require(rows[0]["prefixes"] == 1, "single-prefix reference first")
    for row in rows:
        check_lift(rows[0], row)
    complementary = run_case(runtime, 3, **parameters, pattern=1)
    check_lift(rows[0], complementary)
    return dict(parameters=parameters, rows=rows, complementary=complementary)


def result():
    runtime = load()
    groups = [group(runtime, parameters, PREFIXES) for parameters in CONFIGURATIONS]
    groups.append(group(runtime, dict(q=3, width=3, fibre_value=1), (1, 2, 3)))
    rows = [row for item in groups for row in (*item["rows"], item["complementary"])]
    return dict(
        status="PASS_HIGH_ROUTE_PREFIX_COST",
        cases=len(rows),
        bits=sum(row["prefixes"] * row["cube_bits"] for row in rows),
        native_calls=sum(row["native_calls"] for row in rows),
        groups=groups,
        rows_sha256=hashlib.sha256(canonical(rows).encode()).hexdigest(),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--emit", action="store_true", help="print, never replace, a new receipt"
    )
    args = parser.parse_args()
    actual = result()
    if args.emit:
        print(json.dumps(actual, indent=2, sort_keys=True))
        return
    path = PACKAGE / "RESULT.json"
    require(path.stat().st_size <= 1024 * 1024, "bounded receipt")
    check_receipt(actual, json.loads(path.read_bytes()))
    print(
        actual["status"],
        "cases=" + str(actual["cases"]),
        "bits=" + str(actual["bits"]),
        "native_calls=" + str(actual["native_calls"]),
    )


if __name__ == "__main__":
    main()
