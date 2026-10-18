#!/usr/bin/env python3
"""Independent exact oracle: free GF(2) words, suffix routing, endpoint matchings.

No package verifier or predecessor code is imported.  Every initial register has
its own formal vector; a row is a set of (input, noncommutative operator word)
terms.  Symmetric difference performs addition over GF(2).
"""
from __future__ import annotations

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path


class Rejected(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise Rejected(message)


def require_rejection(fixture, message):
    try:
        check_fixture(fixture)
    except Rejected as error:
        require(str(error) == message, "wrong rejecting check")
        return
    raise Rejected("invalid fixture accepted")


def dimensions(fixture):
    s, n, r = (fixture[k] for k in
               ("source_count", "logical_outputs", "bank_size"))
    require(all(type(x) is int and x > 0 for x in (s, n, r)), "dimensions")
    require(n <= r and len(fixture["masks"]) == n, "output dimensions")
    require(all(type(m) is int and 0 <= m < 1 << s
                for m in fixture["masks"]), "masks")
    for op in fixture["word"]:
        require(isinstance(op, list) and op, "operation")
        tag, *args = op
        require(all(type(x) is int for x in args), "operation indices")
        legal = ((tag == "B" and len(args) == 1 and 0 <= args[0] < s)
                 or (tag == "A" and len(args) == 2
                     and 0 <= args[0] < n and 0 <= args[1] < r)
                 or (tag == "X" and len(args) == 2
                     and 0 <= args[0] < r and 0 <= args[1] < r
                     and args[0] != args[1]))
        require(legal, "operation domain")
    return s, n, r


def initial_rows(s, r):
    return [{(column, ())} for column in range(s + 1 + r)]


def apply_symbol(symbol, row):
    return {(column, (symbol,) + word) for column, word in row}


def execute(fixture):
    s, _, r = dimensions(fixture)
    rows = initial_rows(s, r)
    for op in fixture["word"]:
        if op[0] == "B":
            rows[s] ^= apply_symbol(("B", op[1]), rows[op[1]])
        elif op[0] == "A":
            rows[s + 1 + op[2]] ^= apply_symbol(("A", op[1]), rows[s])
        else:
            rows[s + 1 + op[2]] ^= rows[s + 1 + op[1]]
    return rows


def desired(fixture):
    s, _, r = dimensions(fixture)
    rows = initial_rows(s, r)
    for i, mask in enumerate(fixture["masks"]):
        rows[s + 1 + i] ^= {
            (j, (("A", i), ("B", j)))
            for j in range(s) if mask >> j & 1}
    return rows


def erase(fixture):
    """Trace final influences backward; no forward frame inverse is used."""
    _, _, r = dimensions(fixture)
    image = [1 << p for p in range(r)]
    kept = []
    for op in reversed(fixture["word"]):
        if op[0] == "X":
            image[op[1]] ^= image[op[2]]
        elif op[0] == "B":
            kept.append(op[:])
        elif image[op[2]] >> op[1] & 1:
            kept.append(["A", op[1], op[1]])
    return list(reversed(kept))


def query_counts(word):
    return Counter((op[0], op[1]) for op in word if op[0] != "X")


def check_fixture(fixture):
    s, _, r = dimensions(fixture)
    target = desired(fixture)
    require(execute(fixture) == target, "complete generic operator")
    projected = erase(fixture)
    require(execute(dict(fixture, word=projected)) == target,
            "projected complete generic operator")
    if "expected_erased" in fixture:
        require(projected == fixture["expected_erased"], "fixed erased word")
    before, after = query_counts(fixture["word"]), query_counts(projected)
    require(all(after[k] <= before[k] for k in after), "per-query domination")
    inverse = dict(fixture, word=list(reversed(fixture["word"])))
    require(execute(inverse) == target, "inverse complete generic operator")
    require(execute(dict(inverse, word=erase(inverse))) == target,
            "inverse projected operator")
    return {"name": fixture["name"], "input_vector_columns": s + 1 + r,
            "dirty_vector_columns": r + 1, "orientations": 2,
            "queries_before": sum(before.values()),
            "queries_after": sum(after.values()),
            "mixes": len(fixture["word"]) - sum(before.values())}


def pairings(points):
    """Pair the least unused endpoint, then recurse on the remaining endpoints."""
    if not points:
        yield ()
        return
    first, rest = points[0], points[1:]
    for offset, partner in enumerate(rest):
        for tail in pairings(rest[:offset] + rest[offset + 1:]):
            yield ((first, partner),) + tail


def census():
    histogram = Counter()
    for matching in pairings(tuple(range(10))):
        labels = [None] * 10
        for label, (a, b) in enumerate(sorted(matching)):
            labels[a] = labels[b] = label
        prefixes = [0]
        for label in labels:
            prefixes.append(prefixes[-1] ^ (1 << label))
        differences = {a ^ b for a in prefixes for b in prefixes}
        histogram[len(differences)] += 1
    require(histogram == {16: 42, 19: 120, 21: 180, 22: 56, 23: 45,
                          24: 220, 26: 110, 28: 150, 31: 22},
            "complete five-source matching histogram")
    return {"pairings": sum(histogram.values()), "maximum_coverage": max(histogram),
            "histogram": dict(sorted(histogram.items()))}


def short_word_census():
    """All <=6-gate words on one source, one reader and two dirty bank rows."""
    alphabet = (["B", 0], ["A", 0, 0], ["A", 0, 1], ["X", 0, 1], ["X", 1, 0])
    fixture = {"source_count": 1, "logical_outputs": 1, "bank_size": 2,
               "masks": [1], "word": []}
    target = desired(fixture)
    total = valid = valid_mixed = 0
    for length in range(7):
        for word in product(alphabet, repeat=length):
            total += 1
            trial = dict(fixture, word=list(word))
            if execute(trial) != target:
                continue
            valid += 1
            valid_mixed += any(op[0] == "X" for op in word)
            projected = erase(trial)
            require(execute(dict(trial, word=projected)) == target,
                    "short-word projection")
            before, after = query_counts(word), query_counts(projected)
            require(all(after[k] <= before[k] for k in after), "short-word price")
    require(total == 19531 and valid_mixed > 0, "short-word census coverage")
    return {"words": total, "maximum_length": 6,
            "valid": valid, "valid_with_mixing": valid_mixed}


def matrix_apply(matrix, vector):
    return tuple((vector[0] if row & 1 else 0)
                 ^ (vector[1] if row & 2 else 0) for row in matrix)


def numerical_rows(fixture, a_maps, b_maps, expected=False, reverse_products=False):
    """Independent 2x2 block-matrix simulation on every scalar input basis."""
    s, _, r = dimensions(fixture)
    rows = [(1 << (2*k), 1 << (2*k + 1)) for k in range(s + 1 + r)]

    def add(target, contribution):
        rows[target] = tuple(a ^ b for a, b in zip(rows[target], contribution))

    if expected:
        for i, mask in enumerate(fixture["masks"]):
            for j in range(s):
                if mask >> j & 1:
                    outer, inner = ((b_maps[j], a_maps[i]) if reverse_products
                                    else (a_maps[i], b_maps[j]))
                    add(s + 1 + i, matrix_apply(outer, matrix_apply(inner, rows[j])))
        return rows
    for op in fixture["word"]:
        if op[0] == "B":
            add(s, matrix_apply(b_maps[op[1]], rows[op[1]]))
        elif op[0] == "A":
            add(s + 1 + op[2], matrix_apply(a_maps[op[1]], rows[s]))
        else:
            add(s + 1 + op[2], rows[s + 1 + op[1]])
    return rows


def matrix_controls(common):
    matrices = list(product(range(4), repeat=2))
    mixed = {"source_count": 1, "logical_outputs": 1, "bank_size": 2,
             "masks": [1], "word": [
                 ["B", 0], ["X", 1, 0], ["A", 0, 1], ["X", 1, 0], ["A", 0, 1],
                 ["B", 0], ["X", 1, 0], ["A", 0, 1], ["X", 1, 0], ["A", 0, 1]]}
    for a, b in product(matrices, repeat=2):
        require(numerical_rows(mixed, [a], [b]) ==
                numerical_rows(mixed, [a], [b], expected=True), "2x2 mixed operator")
    common_passes = equal_cases = 0
    for a0, a1, b in product(matrices, repeat=3):
        actual = numerical_rows(common, [a0, a1], [b])
        wanted = numerical_rows(common, [a0, a1], [b], expected=True)
        passes = actual == wanted
        relation = matrix_apply((a0[0] ^ a1[0], a0[1] ^ a1[1]), b) == (0, 0)
        require(passes == relation, "common-reader exact specialization condition")
        common_passes += passes
        if a0 == a1:
            require(passes, "identical-reader positive control")
            equal_cases += 1
    # A=E12, B=E21: AB=diag(1,0), BA=diag(0,1).
    a, b = (2, 0), (0, 1)
    require(numerical_rows(mixed, [a], [b]) != numerical_rows(
        mixed, [a], [b], expected=True, reverse_products=True), "noncommuting control")
    require(numerical_rows(common, [a, b], [b]) != numerical_rows(
        common, [a, b], [b], expected=True), "independent-reader counterexample")
    return {"all_2x2_single_reader_pairs": 256, "common_reader_triples": 4096,
            "common_reader_triples_correct": common_passes,
            "identical_reader_cases": equal_cases,
            "reversed_product_rejected": True}


def fault_controls(fixtures, common):
    require(execute(common) != desired(common), "common-reader generic rejection")
    require_rejection(common, "complete generic operator")
    projected = dict(common, word=erase(common))
    require(execute(projected) != desired(common), "common-reader projection scope")
    mixed = next(f for f in fixtures if any(op[0] == "X" for op in f["word"]))
    cut = next(i for i, op in enumerate(mixed["word"]) if op[0] == "X")
    bad = dict(mixed, word=mixed["word"][:cut] + mixed["word"][cut + 1:])
    actual, target = execute(bad), desired(bad)
    s = mixed["source_count"]
    dirty_columns = lambda rows: [{term for term in row if term[0] >= s}
                                  for row in rows]
    require(dirty_columns(actual) != dirty_columns(target), "missing mix dirty fault")
    require_rejection(bad, "complete generic operator")
    fixture = fixtures[0]
    cut = next(i for i, op in enumerate(fixture["word"]) if op[0] == "A")
    bad = dict(fixture, word=fixture["word"][:cut] + fixture["word"][cut + 1:])
    require(any(column == fixture["source_count"] and word
                for row in execute(bad) for column, word in row),
            "missing read connector-dirt fault")
    require(execute(bad) != desired(bad), "missing read complete rejection")
    require_rejection(bad, "complete generic operator")
    return ["missing_mix_dirty_columns", "missing_read_connector_dirt",
            "common_reader_generic_scope", "noncommuting_product_order"]


def run(certificate):
    require(type(certificate["schema_version"]) is int
            and certificate["schema_version"] == 1, "schema")
    fixtures = certificate["fixtures"]
    names = [f["name"] for f in fixtures]
    require(len(names) == len(set(names)), "unique fixture names")
    require({"five_source_baseline", "five_source_dirty_output_helpers",
             "odd_reader_identity"} == set(names), "fixed certificate fixtures")
    common = certificate["common_reader_control"]
    reports = [check_fixture(f) for f in fixtures]
    baseline = next(f for f in fixtures if f["name"] == "five_source_baseline")
    require((baseline["source_count"], baseline["logical_outputs"],
             baseline["masks"]) == (5, 31, list(range(1, 32))), "all-mask instance")
    counts = query_counts(baseline["word"])
    prices = [1, 4, 10, 16, 28]
    bill = sum(count * (prices[index] if tag == "B" else 1)
               for (tag, index), count in counts.items())
    require(sum(counts.values()) == 74 and bill == 182, "attained pinned bills")
    # The written parity/path argument gives the two exhaustive source-count cases.
    lower_bills = [2 * sum(prices) + 64, 2 * sum(prices) + 2 * min(prices) + 62]
    require(lower_bills == [182, 182], "weighted lower-bound cases")
    return {"pass": "GENERIC_OUTPUT_MIXING_INDEPENDENT", "fixtures": reports,
            "matching_census": census(), "short_word_census": short_word_census(),
            "matrix_controls": matrix_controls(common),
            "pinned_bills": {"attained_queries": 74, "attained_weighted": bill,
                             "weighted_lower_cases": lower_bills},
            "rejecting_controls": fault_controls(fixtures, common)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path,
                        default=Path(__file__).with_name("CERTIFICATE.json"))
    args = parser.parse_args()
    # Missing evidence is an error; this oracle never generates a certificate.
    print(json.dumps(run(json.loads(args.certificate.read_text())), sort_keys=True))


if __name__ == "__main__":
    main()
