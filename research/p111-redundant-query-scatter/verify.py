#!/usr/bin/env python3
"""Sharp direct-scatter support obstruction for one retained P111 query.

Produced by Nick Petalas. Apache-2.0.
"""
import gzip
import hashlib
import io
import json
import platform
import sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

from oracle import support_oracle

ROOT = Path(__file__).resolve().parent
CENTRES = (60, 61, 63, 224, 31, 240, 23, 256)
QUERY_CENTRES = (61, 63, 31, 256)
FILES = (
    "README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
    "verify.py", "oracle.py", "ORIGINS.json", "inputs/word.json.gz",
    "inputs/CENTRE-SEED.json", "inputs/PR1525-NOTICE.md",
    "inputs/PR1525-PREDECESSOR-NOTICE.md",
)


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def read_bytes(name):
    with (ROOT / name).open("rb") as handle:
        raw = handle.read(1_048_577)
    need(len(raw) <= 1_048_576, "file size bound: " + name)
    return raw


def read_inputs():
    origins = json.loads(read_bytes("ORIGINS.json"))["files"]
    need(len(origins) == 4, "four retained source files")
    for name, origin in origins.items():
        need(name in {Path(f).name for f in FILES if f.startswith("inputs/")},
             "unexpected source path")
        raw = read_bytes("inputs/" + name)
        need(hashlib.sha256(raw).hexdigest() == origin["sha256"], "source hash")
        blob = b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
        need(hashlib.sha1(blob).hexdigest() == origin["git_blob"], "source blob")
    raw = read_bytes("inputs/word.json.gz")
    need(hashlib.sha256(raw).hexdigest() ==
         "e8e6e78ff7422275c38324499e1f33fb2ecd30de9503aef2b8f1ee80d8c4df8e",
         "fixed PR1525 word")
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as handle:
        expanded = handle.read(2_097_153)
    need(len(expanded) <= 2_097_152, "decompressed word bound")
    word = json.loads(expanded)
    seed_raw = read_bytes("inputs/CENTRE-SEED.json")
    need(hashlib.sha256(seed_raw).hexdigest() ==
         "228e178662fc01895bbcd8472a52114d3a3d11ea8c7ae44d99cd1c8cf9e89147",
         "fixed PR1525 query seed")
    seed = json.loads(seed_raw)
    need(word["centers"] == list(CENTRES), "centre order")
    terms = seed["terms"]
    need(seed["puncture"] == 0 and len(terms) == 4, "query domain")
    need(tuple(t["center"] for t in terms) == QUERY_CENTRES, "query support")
    need(all(Q(t["weight"]) == Q(1, 2) for t in terms), "query weights")
    return word


def scatter(word):
    events = word["cut"]
    need(isinstance(events, list) and len(events) <= 1024, "cut bound")
    result = [[Q(0) for _ in range(8)] for _ in range(112)]
    for event in events:
        need(isinstance(event, list) and len(event) == 6, "cut event shape")
        op, target, source, numerator, denominator, frame = event
        need(op == "add" and frame is None, "cut event kind")
        need(type(target) is int and 112 <= target < 224, "output role")
        need(type(source) is int and source in CENTRES, "centre role")
        need(type(numerator) is int and numerator in (-1, 1), "numerator")
        need(type(denominator) is int and denominator == 4, "denominator")
        result[target - 112][CENTRES.index(source)] += Q(numerator, denominator)
    need(all(value in (Q(-1, 4), Q(0), Q(1, 4))
             for row in result for value in row), "quarter-grid scatter")
    return result


def corrected(row, coefficient, slots):
    return [value - coefficient / 2 if j in slots else value
            for j, value in enumerate(row)] + [coefficient]


def nnz(row):
    return sum(value != 0 for value in row)


def row_optimum(row, slots):
    # All exceptional cancellation points, plus zero and one generic point.
    candidates = {Q(0), Q(1)} | {2 * row[j] for j in slots if row[j]}
    need(len(candidates) <= 4, "bounded candidate set")
    costs = [(nnz(corrected(row, t, slots)), t) for t in sorted(candidates)]
    best = min(cost for cost, _ in costs)
    active = min((cost, t) for cost, t in costs if t)
    need([t for cost, t in costs if cost == best] == [Q(0)],
         "unique optimum must ignore query")
    return best, active


def check_identity(original, replacement, slots):
    need(len(original) == len(replacement) == 112, "matrix rows")
    for old, new in zip(original, replacement, strict=True):
        need(len(old) == 8 and len(new) == 9, "matrix columns")
        actual = [new[j] + new[8] / 2 if j in slots else new[j]
                  for j in range(8)]
        need(actual == old, "exact formal centre identity")


def execute(matrix, centres, targets, reverse=False):
    need(len(centres) == 9 and len(targets) == 112, "execution domain")
    output = targets[:]
    sign = -1 if reverse else 1
    for i, row in enumerate(matrix):
        for value, source in zip(row, centres, strict=True):
            if value:
                output[i] += sign * value * source
    return output


def expect_failure(action):
    try:
        action()
    except (AssertionError, ValueError):
        return
    raise AssertionError("control was accepted")


def controls(rows, witness, slots):
    bad = [row[:] for row in witness]
    chosen = next(i for i, row in enumerate(bad) if row[8])
    bad[chosen][8] = 0
    expect_failure(lambda: check_identity(rows, bad, slots))
    bad = [row[:] for row in witness]
    bad[chosen][slots[0]] += Q(1, 4)
    expect_failure(lambda: check_identity(rows, bad, slots))
    expect_failure(lambda: check_identity(rows, witness, slots[:-1]))
    expect_failure(lambda: need(sum(nnz(row) for row in witness) == 176,
                                "query use increases support cost"))
    # Without the two-zero premise a query really can save terms.
    dense = [Q(1, 4) if j in slots else Q(0) for j in range(8)]
    need(nnz(corrected(dense, Q(1, 2), slots)) == 1 < nnz(dense),
         "dense changed-contract positive control")
    expect_failure(lambda: scatter({"cut": [["add", 111, 61, 1, 4, None]]}))
    expect_failure(lambda: scatter({"cut": [["add", 112, 61, 1, 0, None]]}))
    return 6


def analyze(rows, slots):
    types, minima, active, witnesses = Counter(), [], [], []
    for i, row in enumerate(rows):
        values = [row[j] for j in slots if row[j]]
        need(len(values) <= 2, "at least two absent query centres in each row")
        kind = ("zero" if not values else "single" if len(values) == 1
                else "same" if values[0] == values[1] else "opposite")
        types[kind] += 1
        best, (cost, t) = row_optimum(row, slots)
        minima.append(best)
        active.append(cost)
        if cost - best == 1:
            witnesses.append((i, t))
    need(types == {"zero": 40, "single": 56, "same": 8, "opposite": 8},
         "complete row census")
    need(sum(minima) == 176 and len(witnesses) == 8, "exact optima")
    need(Counter(b - a for a, b in zip(minima, active, strict=True))
         == {1: 8, 2: 8, 3: 56, 5: 40}, "all row activation penalties")
    integers = [[int(4 * value) for value in row] for row in rows]
    answers, cases = support_oracle(integers, slots)
    need(answers == list(zip(minima, active, strict=True)), "support oracle")
    return types, witnesses, cases


def dirty_checks(rows, matrix, slots):
    for column in range(8):
        centres = [Q(int(j == column)) for j in range(8)]
        query = sum(centres[j] for j in slots) / 2
        dirty = [Q((7 * j) % 23 - 11, j % 5 + 1) for j in range(112)]
        readouts = centres + [query]
        saved = readouts[:]
        output = execute(matrix, readouts, dirty)
        expected = [dirty[j] + rows[j][column] for j in range(112)]
        need(output == expected and readouts == saved, "dirty endpoint")
        need(execute(matrix, readouts, output, reverse=True) == dirty,
             "literal reverse ADD restoration")
        need(readouts == saved, "reverse readout restoration")


def main():
    rows = scatter(read_inputs())
    slots = tuple(CENTRES.index(c) for c in QUERY_CENTRES)
    types, witnesses, cases = analyze(rows, slots)
    matrix = [row + [Q(0)] for row in rows]
    index, coefficient = witnesses[0]
    matrix[index] = corrected(rows[index], coefficient, slots)
    check_identity(rows, matrix, slots)
    need(sum(nnz(row) for row in matrix) == 177, "attaining forced-query matrix")
    dirty_checks(rows, matrix, slots)
    rejected = controls(rows, matrix, slots)
    receipt = {
        "status": "PASS_P111_REDUNDANT_QUERY_SCATTER", "claim_type": "scoped proof",
        "unrestricted_minimum": 176, "query_used_minimum": 177,
        "query_free_optimum_unique": True, "row_types": dict(types),
        "optimal_query_receivers": [112 + i for i, _ in witnesses],
        "witness_receiver": 112 + index,
        "witness_query_coefficient": str(coefficient),
        "support_subsets_checked": cases, "rejection_controls": rejected,
        "dirty_basis_cases": 8, "dense_scope_control": "4 terms to 1",
        "python": sys.version, "platform": platform.platform(), "no_new_kappa": True,
        "sha256": {name: hashlib.sha256(read_bytes(name)).hexdigest() for name in FILES},
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
