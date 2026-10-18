#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 thakrarsagar. Developed with substantial OpenAI Codex assistance.
"""Exact encoded setup invoices for authenticated, unchanged PR2915 execution.

The formulas follow PROOF.md; observations run the retained source. Data-call
tolls are charged whole, with nested native intervals reported separately.
"""

import argparse
import json
from pathlib import Path
import runtime

HERE = Path(__file__).resolve().parent
require = runtime.require


def close_cost(value):
    require(type(value) is int and value >= 0, "nonnegative Count value")
    return 5 * max(1, value.bit_length()) + 12


def product_cost(left, right):
    require(type(left) is type(right) is int and min(left, right) > 0,
            "positive Count product")
    a, b = left.bit_length(), right.bit_length()
    total, value = 19 * a + 21 * b + 151, 0
    for bit in bin(right)[2:]:
        digit = int(bit)
        total += 3 + (1 - digit) + (11 if value == 0 else 6 * value.bit_length() + 9)
        value *= 2
        if digit:
            total += 23 * a + 2 * max(1, value.bit_length()) + 9 * (value + left).bit_length() + 50
            value += left
    return total


def power_cost(modulus, exponent):
    require(type(modulus) is type(exponent) is int and modulus > 0 and exponent >= 0,
            "positive modulus and nonnegative exponent")
    result, factor, remaining = 1, modulus, exponent
    total = 87 + 14 * modulus.bit_length()
    while remaining:
        if remaining & 1:
            total += product_cost(result, factor) + close_cost(result)
            result *= factor
        remaining >>= 1
        if remaining:
            total += product_cost(factor, factor) + close_cost(factor)
            factor *= factor
    return total + close_cost(factor)


def extent_cost(modulus, fibre, dimension, first, second=None):
    """Complete lifetime including all returned Counts' final closures."""
    require(all(type(x) is int for x in (modulus, fibre, dimension, first)) and
            modulus > 0 and fibre > 0 and dimension > 0, "extent parameters")
    fields = dimension * dimension
    require(0 <= first < fields, "first field index")
    if second is None:
        exponents = [first, fields - first - 1]
    else:
        require(type(second) is int and 0 <= second < fields and second != first,
                "distinct second field index")
        low, high = sorted((first, second))
        exponents = [low, high - low - 1, fields - high - 1]
    powers = [modulus ** exponent for exponent in exponents]
    return (sum(power_cost(modulus, exponent) for exponent in exponents) +
            product_cost(powers[-1], fibre) + close_cost(powers[-1]) +
            sum(close_cost(value) for value in powers[:-1]) +
            close_cost(powers[-1] * fibre))


def countdown_cost(value):
    require(type(value) is int and value > 0, "positive canonical countdown")
    return 15 * value + 14 * value.bit_length() - 5 * value.bit_count() + 36


def copy_rows_cost(highs, fibre):
    require(type(highs) is type(fibre) is int and min(highs, fibre) > 0,
            "positive row counts")
    probe = 4 if fibre % 2 == 0 else 15 if fibre > 1 and fibre % 4 == 1 else 12
    return (countdown_cost(highs) + 1 +
            highs * (probe + 5 * fibre + (countdown_cost(fibre) + 1 if fibre > 1 else 0)))


def check_case(row):
    """Reject mismatched source observations; return their symbolic invoice."""
    q, width = row["parameters"]["q"], row["parameters"]["width"]
    fibre, capacity = row["parameters"]["fibre"], row["parameters"]["capacity"]
    modulus, dimension = row["high_modulus"], row["dimension"]
    digits, volume = row["input_digits"], row["volume"]
    require(modulus == q ** (width - 1) and digits == (q ** width).bit_length() + 1,
            "source context modulus/width")
    highs = modulus ** (dimension * dimension)
    require(volume == highs * fibre, "complete cube volume")
    length = modulus.bit_length()
    skeleton = copy_rows_cost(highs, fibre) + 4 * volume + 27 * digits + length + 61
    bank = 10 * capacity + 65 * length + 159 if modulus > 1 else 0
    operations = row["operations"] if modulus > 1 else []
    expected_tolls, expected_extents = [], []
    reversed_adds = 0
    for operation in operations:
        kind, target, *arguments = operation
        require(kind in ("swap", "add", "double", "half", "negate", "translate"),
                "compiled vocabulary")
        second = arguments[0] if kind in ("swap", "add") else None
        expected_extents.append(extent_cost(modulus, fibre, dimension, target, second))
        if kind == "swap":
            expected_tolls.append("swap")
        elif kind == "add":
            reverse = second > target
            reversed_adds += reverse
            expected_tolls.extend((["swap"] if reverse else []) + ["added"] +
                                  (["swap"] if reverse else []))
        else:
            expected_tolls.append({"double": "doubled", "half": "doubled",
                                   "negate": "negated", "translate": "translated"}[kind])
    require([x["kind"] for x in row["tolls"]] == expected_tolls, "complete data-call sequence")
    require(len(row["extents"]) == len(expected_extents), "one extent lifetime per factor")
    for operation, observed, expected in zip(operations, row["extents"], expected_extents):
        second = operation[2] if operation[0] in ("swap", "add") else None
        require((observed["first"], observed["second"]) == (operation[1], second),
                "extent field binding")
        require(observed["create"] + observed["close"] == expected, "exact extent lifetime")
    clear_cost = 5 * volume + 7
    clear_count = len(operations) + 2 * reversed_adds
    require(row["intermediate_clears"] == [clear_cost] * clear_count,
            "every owned intermediate disposal")
    setup = skeleton + bank + sum(expected_extents) + clear_count * clear_cost
    require(row["setup_traffic"] == setup, "exact encoded setup invoice")
    toll_total = sum(x["traffic"] for x in row["tolls"])
    require(all(type(x["traffic"]) is int and x["traffic"] > 0 for x in row["tolls"]),
            "positive charged data tolls")
    require(row["traffic"] == setup + toll_total, "disjoint whole-cube invoice")
    swap_tolls = [x["traffic"] for x in row["tolls"] if x["kind"] == "swap"]
    native_tolls = [x["traffic"] for x in row["native_intervals"]]
    require(len(swap_tolls) == len(native_tolls) and
            all(0 < native < whole for native, whole in zip(native_tolls, swap_tolls)),
            "one charged native interval inside each adapter swap")
    expected_peak = 3 if reversed_adds else 2 if operations else 1
    require(row["output_payload_peak"] == expected_peak, "owned payload cut peak")
    require(row["disposal"] == clear_cost, "returned output disposal")
    fields = dimension * dimension
    extent_bound = 716 + 933 * (2 * fields.bit_length())
    setup_bound = 27 * digits + 10 * capacity + (373 + len(operations) * (3 * extent_bound + 36)) * volume
    require(setup <= setup_bound, "uniform proved-part bound")
    return dict(skeleton=skeleton, bank=bank, extent_lifetimes=expected_extents,
                intermediate_disposal=clear_count * clear_cost,
                encoded_setup=setup, whole_data_tolls=toll_total,
                native_subset=sum(native_tolls),
                adapter_overhead=sum(swap_tolls) - sum(native_tolls),
                returned_output_disposal=clear_cost, executed_factors=len(operations),
                reversed_add_factors=reversed_adds, uniform_setup_bound=setup_bound)


def build():
    loaded = runtime.load()
    cases = []
    fixtures = [dict(kind="ordered"), dict(kind="reversed"), dict(kind="mixed"),
                dict(kind="mixed", fibre=2, pattern=1), dict(kind="ordered", fibre=3),
                dict(kind="identity"), dict(kind="identity", capacity=65),
                dict(kind="identity", q=5), dict(kind="identity", width=1),
                dict(kind="identity", q=5, width=1)]
    try:
        for parameters in fixtures:
            row = runtime.run_case(loaded, **parameters)
            row["invoice"] = check_case(row)
            cases.append(row)
    finally:
        runtime.close(loaded)
    require(cases[6]["setup_traffic"] - cases[5]["setup_traffic"] == 10,
            "one additional high-bank role costs ten")
    require(cases[9]["setup_traffic"] - cases[8]["setup_traffic"] == 27,
            "legal Q=1 contexts expose input-width cost twenty-seven")
    kinds = sorted({operation[0] for row in cases if row["high_modulus"] > 1
                    for operation in row["operations"]})
    require(kinds == ["add", "double", "half", "negate", "swap", "translate"],
            "all reached source operation kinds covered")
    return dict(schema=1, claim="successful unchanged high-route encoded setup and ownership invoice",
                currency="physical Tape reads, writes, unit moves and charged native controller operations",
                source_binding="SOURCES.json input hashes checked before source activation",
                cases=cases, compiled_kinds=kinds,
                controls=dict(extra_bank_role=10, legal_Q1_context_digit=27),
                limitations=["data-call tolls remain charged, not given new all-width bounds",
                             "finite d=2 executions corroborate the source proof",
                             "payload cut counts exclude borrowed source and callee internal workspace",
                             "successful calls only; no exception recovery or global stock claim"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    receipt = build()
    if args.emit:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        require(receipt == json.loads((HERE / "RESULT.json").read_bytes()), "retained result mismatch")
        print("PASS: exact high-route setup, whole data-call tolls and ownership boundary")


if __name__ == "__main__":
    main()
