#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline independent root/dependency check. Stdlib only; no predecessor code.

Normal use requires PACKAGE/RESULT.json and PACKAGE/INDEPENDENT.json and writes
nothing. --write-receipt EXTERNAL creates a new audit receipt outside the input
checkout instead of reading INDEPENDENT.json. It never skips RESULT comparison.
The arbitrary-count reduction is a written proof, NOT a finite circuit search.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations, combinations_with_replacement, product
import json
from pathlib import Path
from random import Random
import sys

PIN = "e733746ba3e5151c829b4e8728bfff5ae3ed24d8d203eb77c735d20758e8266a"
MAIN_INPUT = "research/universal-connector-boundary/CERTIFICATE.json"
FOUR = (0, 4, 5, 1, 3, 7, 6, 14, 28, 16, 0)  # Arham Tahir, PR1370
TWELVE = (0, 16, 8, 31, 5, 4, 6, 2, 3, 1, 0)  # Arham Tahir, PR1340
TWO = FOUR[:-2] + (24,) + FOUR[-2:]  # split compound edge 28->16 at 24
THEOREM = "min(72*c+4*x,74*c), c>0, x>0; equal complete Q/R prices only"


class Invalid(Exception):
    pass


def need(ok, message):
    if not ok:
        raise Invalid(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def bad_constant(text):
        raise Invalid(f"non-finite JSON constant: {text}")

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs,
                      parse_constant=bad_constant)


def same(actual, expected, where):
    """JSON equality that does not identify True, 1 and 1.0."""
    need(type(actual) is type(expected), f"{where}: wrong JSON type")
    if isinstance(expected, dict):
        need(actual.keys() == expected.keys(), f"{where}: wrong fields")
        for key in expected:
            same(actual[key], expected[key], f"{where}.{key}")
    elif isinstance(expected, list):
        need(len(actual) == len(expected), f"{where}: wrong list length")
        for index, value in enumerate(expected):
            same(actual[index], value, f"{where}[{index}]")
    else:
        need(actual == expected, f"{where}: value mismatch")


def walsh(values):
    values = list(values)
    width = 1
    while width < len(values):
        for start in range(0, len(values), 2 * width):
            for j in range(start, start + width):
                a, b = values[j], values[j + width]
                values[j], values[j + width] = a + b, a - b
        width *= 2
    return values


def autocorrelation(points):
    """Integer inverse Walsh of squared Walsh indicator; no difference pairs."""
    indicator = [0] * 32
    for point in points:
        need(type(point) is int and 0 <= point < 32, "bad coefficient point")
        indicator[point] = 1
    transformed = walsh(indicator)
    numerator = walsh([x * x for x in transformed])
    need(all(x >= 0 and x % 32 == 0 for x in numerator), "bad Walsh divisibility")
    correlation = [x // 32 for x in numerator]
    size = sum(indicator)
    need(correlation[0] == size and sum(correlation) == size * size,
         "bad autocorrelation mass")
    need(all(x % 2 == 0 for x in correlation[1:]), "bad nonzero correlation parity")
    return correlation


def endpoint_matchings(unmatched):
    """Choose a partner for the lowest unmatched endpoint, not growth strings."""
    if not unmatched:
        yield ()
    else:
        first = unmatched[0]
        for index in range(1, len(unmatched)):
            partner = unmatched[index]
            rest = unmatched[1:index] + unmatched[index + 1:]
            for tail in endpoint_matchings(rest):
                yield ((first, partner),) + tail


def census(point_lists):
    histogram = Counter()
    records = []
    for points in point_lists:
        correlation = autocorrelation(points)
        histogram[sum(value > 0 for value in correlation)] += 1
        records.append(correlation)
    return {"count": len(records), "histogram": {str(k): histogram[k] for k in sorted(histogram)},
            "max_coverage": max(histogram), "walsh_records_sha256": digest(records)}


def finite_dependencies():
    base = (0, 1, 2, 4, 8, 16)
    nine = census(base + extra for extra in combinations([v for v in range(32) if v not in base], 3))

    def walks():
        for matching in endpoint_matchings(tuple(range(10))):
            events = [0] * 10
            for label, endpoints in enumerate(matching):
                for endpoint in endpoints:
                    events[endpoint] = 1 << label
            points = [0]
            for event in events:
                points.append(points[-1] ^ event)
            need(points[-1] == 0, "matching does not close")
            yield points

    paired = census(walks())
    need(nine["count"] == 2600 and nine["max_coverage"] == 29, "nine-point exclusion")
    need(paired["count"] == 945 and paired["max_coverage"] == 31, "paired-word exclusion")
    ops = tuple((s, t) for s in range(5) for t in range(5) if s != t)
    identity = tuple(1 << j for j in range(5))
    identity_counts, total, repeated = [], 0, []
    for length in range(4):
        found = 0
        for sequence in product(ops, repeat=length):
            total += 1
            columns = identity
            for donor, target in sequence:
                columns = tuple(v ^ (((v >> donor) & 1) << target) for v in columns)
            if columns == identity:
                found += 1
                if length == 2:
                    need(sequence[0] == sequence[1], "non-identical two-X identity")
                    repeated.append(sequence[0])
        identity_counts.append(found)
    need(total == 8421 and identity_counts == [1, 0, 20, 0], "source projection census")
    need(sorted(repeated) == sorted(ops), "missing repeated two-X identity")
    return nine, paired, {"count": total, "identity_by_length": identity_counts}


def multiplicities():
    # Six effective directions: e0,e1,e0+e1,e2,e3,e4. Enumerate multisets,
    # rather than query/readout/X interleavings or five-label row images.
    directions = (1, 2, 3, 4, 8, 16)
    survivors, checked = [], 0
    for multiset in combinations_with_replacement(range(6), 10):
        checked += 1
        counts = Counter(multiset)
        parity, span = 0, {0}
        for index, amount in counts.items():
            direction = directions[index]
            if amount % 2:
                parity ^= direction
            span |= {v ^ direction for v in tuple(span)}
        if parity or len(span) != 32:
            continue
        need(len(counts) == 5 and all(v == 2 for v in counts.values()),
             "two-X directions are not an independent twice-used basis")
        label_counts = [counts[0], counts[1] + counts[2], counts[3], counts[4], counts[5]]
        survivors.append([label_counts, counts[2], sorted(directions[j] for j in counts)])
    need(checked == 3003 and len(survivors) == 3, "two-X multiplicity classification")
    return {"necessary_cases_checked": checked, "survivors": sorted(survivors)}


def arithmetic(nine, paired, projection):
    table = [[t, 124 - 2 * min(31, t * (t - 1) // 2)] for t in range(9)]
    table = [[t, r, t + r] for t, r in table]
    need(min(row[2] for row in table) == 76, "small-query capacity")
    survivors = []
    for t in range(11):
        for r in range(62, 73, 2):
            if t + r > 72 or r < 124 - 2 * min(31, t * (t - 1) // 2):
                continue
            if t == 9 and r == 62 and nine["max_coverage"] < 32:
                continue
            survivors.append([t, r])
    need(survivors == [[10, 62]], "at-most-72 reduction")
    need(projection["identity_by_length"] == [1, 0, 20, 0] and paired["max_coverage"] < 32,
         "missing fixed-count exclusion")
    # At n=73, r even makes t odd. Without X, restoring queries have even
    # total length; one X cannot restore. These implications are written proof.
    need(all(t % 2 == 1 for t in range(74) if (73 - t) % 2 == 0), "73 parity")
    faces = [[72, 4], [73, 2], [74, 0]]
    doubled = [faces[0][j] + faces[2][j] for j in range(2)]
    need(doubled == [2 * v for v in faces[1]], "midpoint identity")
    switch = Fraction(faces[2][0] - faces[0][0], faces[0][1])
    return {"t_at_most_eight": table, "at_most_72_survivors": survivors,
            "lower_faces": faces, "midpoint_doubled_coefficients": doubled,
            "switch_x_over_c": [switch.numerator, switch.denominator]}


def path_word(points):
    need(points[0] == points[-1] == 0, "unclosed witness path")
    need(all(autocorrelation(points)), "witness does not cover every difference")
    reads = [[] for _ in points]
    for mask in range(1, 32):
        pair = next(((i, j) for i in range(len(points)) for j in range(i + 1, len(points))
                     if points[i] ^ points[j] == mask), None)
        need(pair is not None, "missing witness readout")
        for boundary in pair:
            reads[boundary].append(["R", mask])
    word = []
    for boundary, point in enumerate(points):
        word.extend(reads[boundary])
        if boundary == len(points) - 1:
            break
        active = [j for j in range(5) if (point ^ points[boundary + 1]) >> j & 1]
        need(active, "zero witness edge")
        pivot, *donors = active
        word.extend(["X", j, pivot] for j in donors)
        word.append(["Q", pivot])
        word.extend(["X", j, pivot] for j in reversed(donors))
    return word


def root_repairs(certificate):
    repairs = {}
    for name in ("extra_source", "extra_output"):
        entry = certificate["schedules"]["five_" + name]
        same(entry["sources"], 5, "main.sources")
        same(entry["rows"], list(range(1, 32)), "main.rows")
        word = []
        for instruction in entry["word"]:
            need(type(instruction) is list and len(instruction) == 2, "bad main instruction")
            kind, index = instruction
            need(type(index) is int and type(kind) is str, "bad main instruction type")
            need((kind == "A" and 0 <= index < 31) or (kind == "B" and 0 <= index < 5),
                 "bad main instruction index")
            word.append(["R", entry["rows"][index]] if kind == "A" else ["Q", index])
        need(len(word) == 74, "main repair length")
        repairs[name] = word
    return repairs


def validate_word(word):
    need(type(word) is list, "word is not a list")
    for instruction in word:
        need(type(instruction) is list and len(instruction) in (2, 3), "bad instruction shape")
        op, *args = instruction
        need(type(op) is str and all(type(j) is int for j in args), "bad instruction types")
        need((op == "Q" and len(args) == 1 and 0 <= args[0] < 5) or
             (op == "R" and len(args) == 1 and 1 <= args[0] < 32) or
             (op == "X" and len(args) == 2 and all(0 <= j < 5 for j in args) and args[0] != args[1]),
             "instruction outside Q/R/X alphabet")


def apply(matrix, vector):
    return sum(((row & vector).bit_count() & 1) << i for i, row in enumerate(matrix))


def execute(word, initial, queries, readouts):
    state = list(initial)  # sources 0..4, connector 5, outputs 6..36
    for op, *args in word:
        if op == "X":
            state[args[1]] ^= state[args[0]]
        elif op == "Q":
            state[5] ^= apply(queries[args[0]], state[args[0]])
        else:
            state[5 + args[0]] ^= apply(readouts[args[0] - 1], state[5])
    return state


def target(initial, queries, readouts):
    state = list(initial)
    source_images = [apply(queries[j], initial[j]) for j in range(5)]
    for mask in range(1, 32):
        image = 0
        for j in range(5):
            if mask >> j & 1:
                image ^= source_images[j]
        state[5 + mask] ^= apply(readouts[mask - 1], image)
    return state


def first_failure(word, width, queries, readouts):
    for row in range(37):
        for bit in range(width):
            initial = [0] * 37
            initial[row] = 1 << bit
            actual, expected = execute(word, initial, queries, readouts), target(initial, queries, readouts)
            for output in range(37):
                if actual[output] != expected[output]:
                    return [row, bit, output, actual[output], expected[output]]
    return None


def map_banks():
    yield "scalar_identity", 1, (1,), [(1,)] * 31
    yield "scalar_zero_B", 1, (0,), [(i % 2,) for i in range(31)]
    for width, seeds in ((2, (1103, 1109)), (3, (2203, 2207)), (4, (3301, 3307))):
        for seed in seeds:
            rng = Random(seed)
            while True:
                b = tuple(rng.getrandbits(width) for _ in range(width))
                a = [tuple(rng.getrandbits(width) for _ in range(width)) for _ in range(31)]
                if any(apply(m, apply(b, 1 << j)) != apply(b, apply(m, 1 << j))
                       for m in a for j in range(width)):
                    break
            yield f"binary_{width}_{seed}", width, b, a


def root_checks(words):
    banks = []
    for name, width, b, a in map_banks():
        for word in words.values():
            for candidate in (word, list(reversed(word))):
                need(first_failure(candidate, width, [b] * 5, a) is None,
                     f"root dirty-basis map failed: {name}")
                # Additional dense dirty fixtures; full basis already proves this
                # particular instantiated linear map on every possible input.
                for salt in range(3):
                    initial = [((j + 1) * (salt + 3) ^ (j >> 1)) & ((1 << width) - 1) for j in range(37)]
                    need(execute(candidate, initial, [b] * 5, a) == target(initial, [b] * 5, a),
                         "dense dirty fixture failed")
        banks.append({"name": name, "width": width, "maps_sha256": digest([b, a]),
                      "basis_inputs_per_word_per_direction": 37 * width})
    good = words["four_x"]
    odd = list(good)
    del odd[next(i for i, op in enumerate(odd) if op[0] == "R")]
    dirty_connector = [0] * 37
    dirty_connector[5] = 1
    need(execute(odd, dirty_connector, [(1,)] * 5, [(1,)] * 31) != dirty_connector,
         "odd-readout control was not detected")
    missing = list(good)
    last = max(i for i, op in enumerate(missing) if op[0] == "X")
    _, donor, target_row = missing.pop(last)
    initial = [0] * 37
    initial[donor] = 1
    actual = execute(missing, initial, [(1,)] * 5, [(1,)] * 31)
    expected = target(initial, [(1,)] * 5, [(1,)] * 31)
    need(actual[target_row] != expected[target_row] and actual[5:] == expected[5:],
         "missing-source-return control must fail restoration despite correct outputs")
    heterogeneous = [(2, 1)] * 4 + [(1, 0)]
    a = [(3, 2)] + [(1, 2)] * 30
    counterexample = first_failure(good, 2, heterogeneous, a)
    need(counterexample is not None, "heterogeneous-B control was not detected")
    for name in ("extra_source", "extra_output"):
        need(first_failure(words[name], 2, heterogeneous, a) is None,
             "heterogeneous-B control also broke the read-only repair")
    return {"banks": banks, "forward_and_reverse": True, "dirty_rows": 37,
            "controls": {"odd_readout_rejected": True, "missing_source_return_rejected": True,
                         "heterogeneous_B_counterexample": counterexample,
                         "heterogeneous_B_readonly_repairs_passed": 2}}


def lowering_counts(factors):
    if factors == 1:
        return 1, 0, 0
    left, right = lowering_counts(factors // 2), lowering_counts(factors - factors // 2)
    return 2 * (left[0] + right[0]), 1 + 2 * (left[1] + right[1]), 1 + max(left[2], right[2])


def witness_record(word):
    validate_word(word)
    counts = [sum(op[0] == kind for op in word) for kind in ("Q", "R", "X")]
    leaves, nodes, depth = lowering_counts(5)
    need((leaves, nodes, depth) == (28, 9, 3), "five-factor recurrence")
    calls, xors = counts[0] + counts[1], counts[2]
    invoice = leaves * calls + nodes * calls + len(word) + xors
    need(invoice == 38 * calls + 2 * xors, "complete-price invoice")
    return {"counts": counts, "root_word": word, "map_leaves": leaves * calls,
            "internal_nodes": nodes * calls, "root_instructions": len(word),
            "source_xors": xors, "borrowed_dirty_rows": 1 + depth, "unit_tariff": invoice}


def compare_parent(parent, semantic):
    need(type(parent) is dict and parent.keys() == semantic.keys(), "RESULT: wrong fields")
    for key, expected in semantic.items():
        actual = parent[key]
        if key in ("nine_points", "pairings"):
            need(type(actual) is dict and actual.keys() == expected.keys() | {"records_sha256"},
                 f"RESULT.{key}: wrong fields")
            old_digest = actual["records_sha256"]
            need(type(old_digest) is str and len(old_digest) == 64 and
                 all(c in "0123456789abcdef" for c in old_digest), "bad parent record digest type")
            actual = {k: actual[k] for k in expected}
        same(actual, expected, f"RESULT.{key}")


def verify(package):
    package = package.resolve(strict=True)
    need(package.is_dir() and package.parent.name == "research", "package must be CHECKOUT/research/NAME")
    source = package.parent.parent / MAIN_INPUT
    need(hashlib.sha256(source.read_bytes()).hexdigest() == PIN, "main input SHA256 mismatch")
    certificate = read_json(source)
    nine, paired, projection = finite_dependencies()
    words = {"four_x": path_word(FOUR), "twelve_x": path_word(TWELVE),
             **root_repairs(certificate), "two_x": path_word(TWO)}
    witnesses = {name: witness_record(word) for name, word in words.items()}
    need([witnesses[n]["counts"] for n in words] == [[10, 62, 4], [10, 62, 12], [12, 62, 0], [10, 64, 0], [11, 62, 2]],
         "witness count vectors")
    need([witnesses[n]["unit_tariff"] for n in words] == [2744, 2760, 2812, 2812, 2778], "witness tariffs")
    semantics = {"schema_version": 1, "input_sha256": PIN, "theorem": THEOREM,
                 "nine_points": {k: nine[k] for k in ("count", "histogram", "max_coverage")},
                 "pairings": {k: paired[k] for k in ("count", "histogram", "max_coverage")},
                 "source_projections": projection, "two_x_multiplicities": multiplicities(),
                 "arithmetic": arithmetic(nine, paired, projection), "witnesses": witnesses}
    compare_parent(read_json(package / "RESULT.json"), semantics)
    checks = root_checks(words)
    receipt = {**semantics, "schema": "uniform-tariff-independent-v1",
               "scope": "bounded proof dependencies and root maps; arbitrary-count conclusion is written proof; no expanded-leaf or physical/native supplier validation",
               "methods": ["integer Walsh autocorrelation", "endpoint matchings", "source column images",
                           "six-direction multiplicity multisets", "all-basis exact binary matrices"],
               "nine_points": nine, "pairings": paired, "root_checks": checks}
    receipt["witnesses"] = {name: {**{k: v for k, v in record.items() if k != "root_word"},
                                   "root_word_sha256": digest(record["root_word"])}
                            for name, record in witnesses.items()}
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--write-receipt", type=Path, metavar="EXTERNAL")
    args = parser.parse_args()
    try:
        package = args.package.resolve(strict=True)
        need(package.is_dir() and package.parent.name == "research", "package must be CHECKOUT/research/NAME")
        if args.write_receipt is not None:
            output = args.write_receipt.expanduser().resolve()
            checkout = package.parent.parent
            need(not output.is_relative_to(checkout), "receipt export must be outside the input checkout")
            need(not output.exists(), "receipt export refuses an existing path")
        receipt = verify(package)
        if args.write_receipt is None:
            same(read_json(package / "INDEPENDENT.json"), receipt, "INDEPENDENT")
        else:
            with output.open("x", encoding="utf-8") as stream:
                stream.write(json.dumps(receipt, sort_keys=True, indent=2, allow_nan=False) + "\n")
        print("independent: PASS (2600 sets; 945 matchings; 8421 X words; five root witnesses; tariffs 2744,2760,2812,2812,2778)")
        return 0
    except (Invalid, OSError, ValueError, KeyError, TypeError) as error:
        print(f"independent: FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
