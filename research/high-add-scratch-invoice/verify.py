#!/usr/bin/env python3
"""Source-bound high ADD capacity, endpoint and physical invoice audit."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from invoice import allocations, counter, limits, require, shell
from runtime import (PACKAGE, Traffic, dispose, encoded, endpoint, load,
                     physical_total, prepare)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def check_receipt(actual, expected):
    require(canonical(actual) == canonical(expected), "complete typed receipt")


def primitive_bounds(traffic, q, before):
    b = q.bit_length() + 1
    expected = {
        "fixed_coefficient": (2, 256 * b * b),
        "compare": (2, 18 * b), "zero": (2 * before, 13 * b),
        "multiply": (2 * before * q, 300 * b * b),
        "subtract_exact": (2 * before * q, 36 * b),
        "free_many": (2 * before * q, 20 * b),
        "increment_in_place": (2 * before * (q - 1), 10 * b),
        "free": (2 * before + 2, 10 * b),
    }
    require(set(traffic.intervals) == set(expected), "complete arithmetic partition")
    for name, (count, bound) in expected.items():
        row = traffic.intervals[name]
        require(row[0] == count and row[2] <= bound, "arithmetic count/bound: " + name)


def run_case(rt, q, before, middle, suffix, coefficient, *, occupied=0,
             pooled=False, basis=None, spare=None, numerical_capacity=8,
             numerical_occupied=0):
    bound = limits(q, before, middle, suffix)
    f = prepare(rt, q, before, middle, suffix, coefficient,
                bound["scratch"] if spare is None else spare, occupied, pooled,
                numerical_capacity, basis, numerical_occupied)
    original = dict(source=encoded(f.source), counts=[encoded(v.tape) for v in f.extents],
                    numerical={slot: encoded(f.bank.words[slot].tape) for slot in f.bank.live})
    held = [encoded(lease) for lease in f.held]
    residents = set(f.bank.live)
    start, acquisitions = physical_total(f.tapes), f.pool.allocations
    traffic, output = Traffic(rt), None
    try:
        with traffic.installed(), f.pool.install():
            output = rt.kernels.added(f.source, f.ring, *f.extents, coefficient)
        require(traffic.total == physical_total(f.tapes) - start, "unique physical meters")
        validate_boundary(f, output, original, held, residents, q, before, middle,
                          suffix, coefficient, occupied, bound)
        require(traffic.total - traffic.arithmetic == shell(q, before, middle, suffix),
                "exact non-arithmetic invoice")
        primitive_bounds(traffic, q, before)
        require(f.pool.allocations - acquisitions == allocations(q, before, middle, suffix),
                "exact lease acquisition count")
        require(traffic.arithmetic <= bound["arithmetic"] and
                traffic.total - traffic.arithmetic <= bound["shell"] and
                traffic.total <= bound["total"], "uniform complete local I/O bound")
        row = dict(q=q, before=before, middle=middle, suffix=suffix, coefficient=coefficient,
                   basis=basis, occupied=occupied, pooled_source=pooled, volume=bound["volume"],
                   scratch_peak=f.pool.peak - occupied, numerical_extra=f.bank.meter.peak_live - len(residents),
                   acquisitions=f.pool.allocations - acquisitions, traffic=traffic.total,
                   arithmetic=traffic.arithmetic, shell=traffic.total - traffic.arithmetic,
                   arithmetic_intervals=traffic.intervals)
        output.clear()
        output = None
        require(physical_total(f.tapes) - start == traffic.total + 5 * bound["volume"] + 7,
                "complete returned-output disposal invoice")
        require(set(f.pool.live.values()) == set(f.held), "only entry leases after disposal")
        return row
    finally:
        dispose(f, output)


def validate_boundary(f, output, original, held, residents, q, before, middle,
                      suffix, coefficient, occupied, bound):
    observed = dict(source=encoded(f.source), counts=[encoded(v.tape) for v in f.extents],
                    numerical={slot: encoded(f.bank.words[slot].tape) for slot in residents})
    require(original == observed, "borrowed payload/count/numerical bytes and heads preserved")
    require(held == [encoded(lease) for lease in f.held], "all occupied entry roles preserved")
    require(set(f.bank.live) == residents, "numerical residents restored")
    require(f.bank.meter.peak_live - len(residents) <= 6, "six additional numerical slots")
    require(f.pool.peak == occupied + bound["scratch"], "exact free scratch inventory")
    require(set(f.pool.live.values()) == {*f.held, output}, "only owned output remains")
    require(output not in f.held and output is not f.source, "distinct owned output")
    endpoint(f, output, q, before, middle, suffix, coefficient)


def counter_controls(rt):
    cases = 0
    for n in range(17):
        for extra in (0, 1, 3):
            width = max(2, n.bit_length()) + extra
            bank = rt.physical.PhysicalArena(2)
            maximum = rt.cardinal_counts.Count.literal(2 ** (width - 2))
            bank.prepare(maximum)
            value = bank.literal(n)
            pool = rt.pool.ScratchPool(1)
            tapes = [value.tape, *pool.tapes]
            start = physical_total(tapes)
            with pool.install():
                item = rt.stream.Counter(value)
                while not item.finished:
                    item.decrement()
                item.close()
            require(physical_total(tapes) - start == counter(n, width), "padded/zero counter invoice")
            require(counter(n, width) <= 16 * n + 16 * width + 64, "counter majorant")
            maximum.close()
            bank.free(value)
            bank.erase_owned()
            pool.empty()
            cases += 1
    return cases


def large_word_controls(rt):
    """Probe the width-dependent arithmetic tariff without materializing Q^2 bits."""
    checks = 0
    for q in (129, 65537, 2 ** 80 + 7):
        b = q.bit_length() + 1
        bank = rt.physical.PhysicalArena(8)
        encoded_q = rt.cardinal_counts.Count.literal(q)
        bank.prepare(encoded_q)
        modulus = bank.load(encoded_q)
        ring = rt.words.Ring(modulus)
        for coefficient in (-4, 1, 2):
            trace = Traffic(rt)
            with trace.installed():
                value = rt.kernels.fixed_coefficient(ring, coefficient)
            require(trace.total <= 256 * b * b, "large fixed-coefficient bill")
            require(word_value(value) == coefficient % q, "large fixed coefficient")
            checks += 1
            for x in (0, 1, q - 1):
                argument = bank.literal(x)
                trace = Traffic(rt)
                with trace.installed():
                    product = ring.multiply(value, argument)
                require(trace.total <= 300 * b * b, "large multiplication bill")
                require(word_value(product) == coefficient * x % q, "large product")
                bank.free_many(argument, product)
                checks += 1
            bank.free(value)
        require(bank.meter.peak_live <= 8, "large numerical capacity")
        ring.close()
        bank.free(modulus)
        bank.erase_owned()
        encoded_q.close()
    return checks


def word_value(word):
    # Checker-only decoding, outside every measured source interval.
    digits = word.tape.cells[1:]
    require(3 in digits, "word right delimiter")
    return sum(bit << index for index, bit in enumerate(digits[:digits.index(3)]))


def result(rt):
    cases = []
    for q in (3, 5, 9, 17):
        for before, middle, suffix in ((1, 1, 1), (1, 1, 2), (2, 3, 1), (2, 1, 3)):
            for coefficient in (-4, -2, -1, 1, 2, 4):
                cases.append(run_case(rt, q, before, middle, suffix, coefficient))
    for suffix in (1, 3):
        for pooled in (False, True):
            cases.append(run_case(rt, 5, 2, 2, suffix, -2, occupied=3, pooled=pooled))
    for column in range(9):
        cases.append(run_case(rt, 3, 1, 1, 1, -1, basis=column))
    return dict(status="PASS_HIGH_ADD_SCRATCH_INVOICE", cases=len(cases),
                payload_bits=sum(row["volume"] for row in cases), basis_columns=9,
                counter_cases=counter_controls(rt), large_word_checks=large_word_controls(rt),
                scratch_roles=[10, 11], numerical_extra=6,
                uniform_io_coefficient=4096, disposed_io_coefficient=4102,
                cases_sha256=hashlib.sha256(canonical(cases).encode()).hexdigest(), cases_detail=cases)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print a new receipt without replacing it")
    args = parser.parse_args()
    actual = result(load())
    if args.emit:
        print(json.dumps(actual, indent=2, sort_keys=True))
    else:
        check_receipt(actual, json.loads((PACKAGE / "RESULT.json").read_bytes()))
        print(actual["status"], "cases=" + str(actual["cases"]),
              "payload_bits=" + str(actual["payload_bits"]), "scratch=10,11 numerical_extra<=6 io<=4096V")


if __name__ == "__main__":
    main()
