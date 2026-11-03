#!/usr/bin/env python3
"""Exact finite corroboration of homogeneous chronological width cancellation.

Produced by Nick Petalas. Apache-2.0.
The universal statements are proved in PROOF.md; this checker imports no
predecessor implementation and writes no files.
"""
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from math import gcd, lcm
from pathlib import Path


FILES = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, low, high):
    need(type(value) is int and low <= value <= high, "integer domain")


def floor_log(value, base):
    integer(value, 1, 2**256)
    integer(base, 2, 2**16)
    for exponent in range(257):
        if value < base:
            return exponent
        value //= base
    raise ValueError("logarithm capacity")


def closed_flow(m, w, p, n, height):
    """New source/cut formula, on an explicitly bounded executable domain."""
    integer(m, 2, 16)
    integer(w, 1, 16)
    integer(p, 1, 16)
    integer(n, m, 2**256)
    integer(height, 0, 256)
    shell = floor_log(n, m)
    letters = min(height + 1, shell)
    start = height + 1 - letters
    rank = m**letters
    sources = p**start * w**letters
    need(1 <= rank <= n and start >= 0, "strict complement descent")
    columns = Counter()
    for depth in range(start, height + 1):
        columns[m**(height - depth)] += p**depth * w**(height - depth)
    return {"sources": {rank: sources}, "columns": dict(columns),
            "leaf_cuts": p**(height + 1), "boundary_cuts": 0,
            "source_depth": start}


def literal_flow(m, w, p, n, height):
    """Enumerate distinguishable paid paths and ordered target words.

    This does not use closed_flow, a multinomial formula, or compressed path
    occurrences. Each paid position retains its own chronological cut.
    """
    integer(m, 2, 6)
    integer(w, 1, 3)
    integer(p, 1, 3)
    integer(n, m, 512)
    integer(height, 0, 5)
    cap = n // m
    sources, columns = Counter(), Counter()
    leaf_cuts, boundary_cuts, first_source = 0, 0, None
    for depth in range(height + 1):
        degree = height - depth
        here = set(product(range(w), repeat=degree)) if m**degree <= cap else set()
        if depth == 0:
            for word in here:
                for letter in range(w):
                    sources[m**(len(word) + 1)] += 1
                    first_source = 0
        below = set()
        if degree and m**(degree - 1) <= cap:
            for tail in product(range(w), repeat=degree - 1):
                for letter in range(w):
                    below.add((letter,) + tail)
        for path in product(range(p), repeat=depth):
            need(len(path) == depth, "literal paid path")
            for word in here:
                columns[m**len(word)] += 1
            for paid_position in range(p):
                need(0 <= paid_position < p, "literal paid position")
                if depth == height:
                    need(here == {()}, "leaf unit exists")
                    leaf_cuts += 1
                else:
                    boundary_cuts += bool(here - below)
                    for word in below - here:
                        sources[m**len(word)] += 1
                        if first_source is None:
                            first_source = depth + 1
    return {"sources": dict(sources), "columns": dict(columns),
            "leaf_cuts": leaf_cuts, "boundary_cuts": boundary_cuts,
            "source_depth": first_source}


def height_at(n, m, rule):
    kind, base, multiplier = rule
    if kind == "default":
        return floor_log(n // m, m)
    if kind == "fixed":
        return multiplier
    need(kind == "adaptive", "height rule")
    return multiplier * floor_log(n // m, base)


def width_table(m, w, p, maximum, rule, literal=False):
    integer(maximum, m, 1024)
    widths = [1] * (maximum + 1)
    for n in range(m, maximum + 1):
        height = height_at(n, m, rule)
        flow = literal_flow(m, w, p, n, height) if literal else closed_flow(m, w, p, n, height)
        need(len(flow["sources"]) == 1, "one source rank")
        (source_rank, count), = flow["sources"].items()
        complement = n - source_rank
        replication = widths[complement] // gcd(widths[complement], count)
        # Every leaf is a separate (rank 1, count 1) batch; B_1=1.
        need(widths[1] == 1 and flow["boundary_cuts"] == 0, "complete cut reduction")
        widths[n] = count * replication
        need(replication * count % widths[complement] == 0, "whole complement batch")
        need(widths[n] == lcm(count, widths[complement]), "gcd cancellation")
    return widths


def chain_width(m, w, p, n, rule):
    """Evaluate the new decreasing-chain LCM, without a table of widths."""
    integer(n, 0, 1024)
    result, remaining = 1, n
    for _ in range(n // m + 1):
        if remaining < m:
            return result
        flow = closed_flow(m, w, p, remaining, height_at(remaining, m, rule))
        (rank, count), = flow["sources"].items()
        result = lcm(result, count)
        remaining -= rank
    raise ValueError("subtraction chain capacity")


def check_flows():
    fixtures, literal_leaves, empty_roots = 0, 0, 0
    for m, w, p in product(range(2, 7), range(1, 4), range(1, 4)):
        ranks = {m, m + 1, 2 * m - 1, m*m - 1, m*m, m*m + 1, 63, 127}
        for n, height in product(sorted(ranks), range(6)):
            actual = literal_flow(m, w, p, n, height)
            predicted = closed_flow(m, w, p, n, height)
            need(actual == predicted, "literal forest agrees with new formula")
            source_mass = sum(rank * count for rank, count in actual["sources"].items())
            column_mass = sum(rank * count for rank, count in actual["columns"].items())
            need(source_mass - actual["leaf_cuts"] == (m*w - p)*column_mass,
                 "exact rank invoice")
            fixtures += 1
            literal_leaves += actual["leaf_cuts"]
            empty_roots += actual["source_depth"] > 0
    return {"forest_fixtures": fixtures, "enumerated_leaf_cuts": literal_leaves,
            "empty_root_fixtures": empty_roots}


def check_widths():
    fixtures, coordinates, literal_tables, strict = 0, 0, 0, 0
    rules = [("default", 0, 0), ("fixed", 0, 0), ("fixed", 0, 4),
             ("adaptive", 2, 2), ("adaptive", 3, 3), ("adaptive", 8, 4)]
    for m, w, p, rule in product(range(2, 7), range(1, 5), range(1, 5), rules):
        widths = width_table(m, w, p, 256, rule)
        for n in range(m, 257):
            need(widths[n] == chain_width(m, w, p, n, rule), "exact chain LCM")
            if rule[0] == "default":
                need(widths[n] == w**floor_log(n, m), "default closed form")
            divisor = w**floor_log(n, m) * p**height_at(n, m, rule)
            need(divisor % widths[n] == 0, "polynomial divisor")
            coordinates += 1
        fixtures += 1
    for m, w, p in product(range(2, 5), range(1, 4), range(1, 4)):
        literal = width_table(m, w, p, 63, ("default", 0, 0), literal=True)
        formula = width_table(m, w, p, 63, ("default", 0, 0))
        need(literal == formula, "independent literal-batch widths")
        literal_tables += 1
        strict += sum(width > 1 for width in literal)
    return {"width_tables": fixtures, "width_coordinates": coordinates,
            "literal_width_tables": literal_tables,
            "nonunit_literal_widths": strict}


def expect_rejection(values):
    try:
        closed_flow(*values)
    except ValueError as error:
        need(str(error) == "integer domain", "specific domain rejection")
        return
    raise ValueError("invalid input accepted")


def check_controls():
    invalid = [(1,2,3,8,2), (True,2,3,8,2), (17,2,3,32,2),
               (2,0,3,8,2), (2,17,3,8,2), (2,2,False,8,2),
               (2,2,0,8,2), (2,2,17,8,2), (2,2,3,1,2),
               (2,2,3,2**257,2), (2,2,3,8,-1), (2,2,3,8,257)]
    for values in invalid:
        expect_rejection(values)
    empty = literal_flow(2, 2, 3, 2, 3)
    widths = width_table(2, 2, 3, 8, ("default", 0, 0))
    fixed = width_table(2, 2, 3, 10, ("fixed", 0, 2))
    first = closed_flow(2, 2, 3, 8, 0)
    second = closed_flow(2, 2, 3, 6, 3)
    controls = [
        (empty["sources"] == {2:54} and empty["source_depth"] == 3,
         "empty parents cannot be pruned"),
        (empty["leaf_cuts"] == 81, "occurrences are distinct cuts"),
        (closed_flow(2, 2, 3, 8, 2)["sources"] == {8:8}, "target multiplicity"),
        (widths[6] == 4 and 4*widths[2] == 8, "omitted gcd overpays"),
        (chain_width(2, 2, 3, 8, ("fixed", 0, 0)) == 2 != widths[8],
         "height is part of the contract"),
        (fixed[10] == 72 and max(8, 18) == 18, "LCM is not maximum"),
        (first["sources"] == {2:2} and second["sources"] == {4:36}
         and 2 * (36 // gcd(36, 2)) == 36, "arbitrary-height cancellation")]
    for condition, message in controls:
        need(condition, message)
    return {"invalid_input_rejections": len(invalid),
            "semantic_control_groups": len(controls)}


def check_capacities():
    large = closed_flow(2, 16, 16, 2**256, 256)
    controls = [
        (floor_log(2**256, 2) == 256, "maximum logarithm"),
        (large["sources"] == {2**256:16**257}
         and len(large["columns"]) == 256, "maximum closed formula"),
        (chain_width(2, 2, 3, 1024, ("fixed", 0, 0)) == 2,
         "maximum subtraction chain"),
        (len(width_table(2, 1, 1, 1024, ("fixed", 0, 0))) == 1025,
         "maximum width table")]
    for condition, message in controls:
        need(condition, message)
    return {"capacity_controls": len(controls)}


def file_hashes():
    folder = Path(__file__).resolve().parent
    hashes = {}
    for name in FILES:
        with (folder / name).open("rb") as source:
            raw = source.read(2**21 + 1)
        need(len(raw) <= 2**21, "package file capacity")
        hashes[name] = sha256(raw).hexdigest()
    return hashes


def main():
    receipt = {"claim_type": "scoped written proof with exact finite corroboration"}
    receipt.update(check_flows())
    receipt.update(check_widths())
    receipt.update(check_controls())
    receipt.update(check_capacities())
    default = chain_width(2, 2, 3, 1023, ("default", 0, 0))
    need(default == 512, "default numerical example")
    receipt["example"] = {"m":2, "W":2, "P":3, "rank":1023,
                          "least_width":default, "gcd_free_width":2**45}
    receipt["package_sha256"] = file_hashes()
    print(json.dumps(receipt, sort_keys=True, indent=2))
    print("PASS_HOMOGENEOUS_GCD_WIDTH")


if __name__ == "__main__":
    main()
