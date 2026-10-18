#!/usr/bin/env python3
"""Exact dirty-map, affine-prefix and invoice checks; no predecessor code imports."""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations, permutations, product
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import (build, check_identity, expected, interpret, invoice, minimum_word,
                   need, roles, root_ops, slots)

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent


def load(path):
    def unique(items):
        out = {}
        for key, value in items:
            need(key not in out, "duplicate JSON key")
            out[key] = value
        return out
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)


def check_pins():
    sources = load(HERE / "SOURCES.json")
    for row in sources["files"]:
        if row["usage"] == "input":
            need(sha256((REPO / row["path"]).read_bytes()).hexdigest() == row["sha256"], "source drift")


def check_expanded(item):
    word, ops = item["word"], item["leaf_word"]
    check_identity(word, 5)
    need(item["invoice"] == invoice(word), "complete invoice mismatch")
    actual = interpret(ops, roles(5))
    need(actual == expected(5, True), "factor order or private dirty restoration failed")
    need(interpret(ops[::-1], roles(5), actual) == {r: {(r,)} for r in roles(5)}, "expanded inverse failed")
    need(sum(bool(op[0]) for op in ops) == item["invoice"]["map_leaves"], "unpaid map leaf")
    need(sum(not op[0] for op in ops) == item["invoice"]["X"], "unpaid source XOR")


def prefix_subset_check(n, points):
    seen = {}
    for bits in product((0, 1), repeat=n + 1):
        if sum(bits) % 2:
            continue
        mask = 0
        for bit, point in zip(bits, points):
            if bit:
                mask ^= point
        need(mask not in seen, "even-subset representation is not unique")
        seen[mask] = sum(bits)
    need(set(seen) == set(range(1 << n)), "even-subset coverage incomplete")
    need(sum(seen.values()) == (n + 1) * (1 << (n - 1)), "readout bound mismatch")
    return Counter(seen.values())


def rank(vectors):
    basis = {}
    for value in vectors:
        while value:
            pivot = value.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = value
                break
            value ^= basis[pivot]
    return len(basis)


def checks(cert):
    need(cert["schema_version"] == 1 and type(cert["n"]) is int and cert["n"] == 5, "certificate header")
    old = load(REPO / "research/universal-connector-boundary/CERTIFICATE.json")
    need(cert == build(old), "certificate is not the complete deterministic construction")
    need(cert["complete_tariff"] == {"Q": 38, "R": 2, "X": 2}, "tariff mismatch")
    for item in cert["schedules"].values():
        check_expanded(item)
    histograms = {}
    for n in range(1, 10):
        points = [(1 << t) - 1 for t in range(n + 1)]
        histograms[str(n)] = {str(k): v for k, v in sorted(prefix_subset_check(n, points).items())}
        counts = check_identity(minimum_word(n), n)
        need(counts["Q"] == n + 1 and counts["R"] == (n + 1) * (1 << (n - 1))
             and counts["X"] == 2 * (n - 1), "general construction count")
        for m in range(1, 1 << n):
            selected = slots(n, m)
            mask = 0
            for t in selected:
                mask ^= points[t]
            need(mask == m and len(selected) % 2 == 0, "wrong prefix readout")
    # Complete small arbitrary-prefix control, independent of the triangular slots formula.
    gl3 = 0
    for basis in permutations(range(1, 8), 3):
        if rank(basis) == 3:
            prefix_subset_check(3, [0, *basis])
            gl3 += 1
    need(gl3 == 168, "GL3 domain incomplete")
    # Any at-most-n-query closed path has at most n-1 independent increments.
    # Check every ordered 3D full-span four-query circuit (generic theorem is written).
    circuits = 0
    for first in product(range(1, 8), repeat=3):
        if rank(first) == 3:
            last = first[0] ^ first[1] ^ first[2]
            points, value = [0], 0
            for step in (*first, last):
                value ^= step
                points.append(value)
            need(value == 0 and rank(points[:-1]) == 3, "circuit prefix rank")
            prefix_subset_check(3, points[:-1])
            circuits += 1
    need(circuits == 168, "four-query circuit domain incomplete")
    bills = {name: item["invoice"] for name, item in cert["schedules"].items()}
    need({name: bill["tariff"] for name, bill in bills.items()} == {
        "minimum_queries": 436, "four_X_ten_Q": 512,
        "five_extra_source": 580, "five_extra_output": 508}, "unequal complete bills")
    need(all(436 < bill["tariff"] for name, bill in bills.items() if name != "minimum_queries"), "tariff is not favorable")
    # Falsification of extrapolation to equal prices: this new word is worse there.
    need(38 * (6 + 96) + 2 * 8 == 3892 > 2744 == 38 * (10 + 62) + 2 * 4,
         "equal-price non-improvement control")
    return {"n_range": [1, 9], "GL3_prefix_bases": gl3, "full_span_four_query_circuits": circuits,
            "readout_histograms": histograms, "invoices": bills}


def controls(cert):
    passed = []
    def reject(name, action):
        try:
            action()
        except ValueError:
            passed.append(name)
        else:
            raise ValueError("negative control accepted: " + name)
    def copy(value):
        return json.loads(json.dumps(value))
    item = cert["schedules"]["minimum_queries"]
    bad = copy(item["word"])
    del bad[next(i for i in reversed(range(len(bad))) if bad[i][0] == "Q")]
    reject("missing_final_query", lambda: check_identity(bad, 5))
    bad = copy(item["word"])
    bad.pop()
    # Outputs remain right, but a source is dirty; the check must compare every role.
    result = interpret(root_ops(bad, 5), roles(5))
    need(all(result[f"y{m}"] == expected(5)[f"y{m}"] for m in range(1, 32)), "source-only control shape")
    reject("outputs_correct_source_not_restored", lambda: check_identity(bad, 5))
    bad = copy(item["word"])
    del bad[next(i for i, e in enumerate(bad) if e[0] == "R")]
    reject("connector_dirt_readout", lambda: check_identity(bad, 5))
    bad = copy(item["word"])
    bad[0][1] ^= 2
    reject("wrong_output_mask", lambda: check_identity(bad, 5))
    bad = copy(item)
    for event in bad["leaf_word"]:
        if event[0].startswith("B"):
            event[0] = "B" + str(4 - int(event[0][1:]))
    reject("noncommuting_factor_order", lambda: check_expanded(bad))
    bad = copy(item)
    bad["leaf_word"].pop(next(i for i, op in enumerate(bad["leaf_word"]) if op[2].startswith("w")))
    reject("missing_private_uncompute", lambda: check_expanded(bad))
    bad = copy(item)
    bad["leaf_word"][0][2] = bad["leaf_word"][0][1]
    reject("aliased_port", lambda: check_expanded(bad))
    bad = copy(item)
    bad["invoice"]["echo_nodes"] -= 1
    reject("unpaid_internal_node", lambda: check_expanded(bad))
    bad = copy(item)
    bad["invoice"]["root_dispatches"] -= 1
    reject("unpaid_root_dispatch", lambda: check_expanded(bad))
    ops = root_ops(item["word"], 5)
    ops = [[coefficient + source if coefficient == "B" else coefficient, source, target]
           for coefficient, source, target in ops]
    reject("heterogeneous_B_does_not_inherit", lambda: need(interpret(ops, roles(5)) == expected(5), "common B required"))
    reject("dependent_prefixes", lambda: prefix_subset_check(3, [0, 1, 2, 3]))
    bad = copy(cert)
    bad["readout_slots"]["21"].pop()
    reject("incomplete_six_readout_certificate", lambda: checks(bad))
    return passed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate", action="store_true", help="explicitly write the deterministic certificate")
    args = parser.parse_args()
    check_pins()
    if args.generate:
        old = load(REPO / "research/universal-connector-boundary/CERTIFICATE.json")
        cert = build(old)
        checks(cert)
        (HERE / "CERTIFICATE.json").write_text(json.dumps(cert, indent=2) + "\n", encoding="utf-8", newline="\n")
    cert = load(HERE / "CERTIFICATE.json")
    result = checks(cert)
    result["controls"] = controls(cert)
    if args.generate:
        (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    need(result == load(HERE / "RESULT.json"), "stored result drift")
    print("PASS_MINIMUM_QUERY_SLICE n=1..9 Q=6 R=96 X=8 tariff=436_vs_508 controls=12 no_new_kappa")


if __name__ == "__main__":
    main()
