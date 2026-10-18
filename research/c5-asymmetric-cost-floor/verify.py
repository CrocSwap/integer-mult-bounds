#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 thakrarsagar. Developed with substantial OpenAI Codex assistance.
"""Exact asymmetric support certificate on the attributed physical C5 core.

Geometry and full-plane tariff: PR2782 and its retained predecessors.
Rank-cover starting point: PR3232. This checker does not use a five-term bound.
The written rank and trace lemmas are in README.md; this file checks their
finite premises. All scalar coefficient arguments are over characteristic zero.
"""

import argparse
from collections import deque
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
from typing import NamedTuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = "research/c5-dyadic-decoder-gate/inputs/"
CORE = (13, 23, 35, 16, 34)
Q = ((0, 2), (0, 3), (1, 3), (1, 4))
TIGHT_TARGET = (4, 4, 4, 4, 2, 2, 0)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def dot(left, right):
    return (left & right).bit_count() % 2


def pairing(left, right):
    """Rank of the inherited binary dot pairing, including complete planes."""
    pivots = {}
    for label in left:
        row = sum(dot(label, other) << j for j, other in enumerate(right))
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def load_geometry(root=ROOT):
    """Authenticate exactly two geometry inputs; return matching and 56 planes."""
    raw = {}
    for pin in json.loads((HERE / "SOURCES.json").read_bytes())["files"]:
        if pin["usage"] == "input":
            value = (Path(root) / pin["path"]).read_bytes()
            need(hashlib.sha256(value).hexdigest() == pin["sha256"],
                 "source bytes changed: " + pin["path"])
            raw[pin["path"]] = value
    need(set(raw) == {INPUT + "DATA-PHASES.json.gz", INPUT + "MATCHING.json"},
         "exactly two geometry inputs")
    recipes = json.loads(gzip.decompress(raw[INPUT + "DATA-PHASES.json.gz"]))["recipes"]
    labels = {row["port"]: row["q"] for row in recipes}
    need(len(recipes) == len(labels) == 112 and sorted(labels) == list(range(112)),
         "complete scalar-port domain")
    need(all(type(q) is int and 0 < q < 512 for q in labels.values()), "binary labels")
    matching = json.loads(raw[INPUT + "MATCHING.json"])["matching"]
    need(len(matching) == 56 and all(len(pair) == 2 for pair in matching)
         and sorted(port for pair in matching for port in pair) == list(range(112)),
         "complete paired-plane partition")
    planes = [[labels[port] for port in pair] for pair in matching]
    need(all([[dot(a, b) for b in plane] for a in plane] == [[1, 0], [0, 1]]
             for plane in planes), "each complete plane has Gram I2")
    return matching, planes


def core(planes):
    """Select the named C5 in its inherited cycle order."""
    local = [planes[i] for i in CORE]
    for i in range(5):
        for j in range(i + 1, 5):
            need((pairing(local[i], local[j]) == 0) == ((j - i) in (1, 4)),
                 "named core has exactly the C5 orthogonality edges")
    return local


class Support(NamedTuple):
    left: int
    right: int
    cost: int
    hits: tuple  # Four Q blocks, then the single planes 2 and 4.
    defect: int
    missing: int  # The fifth forced I4 block, on planes 2 and 4.


def support_records(planes):
    """All 1024 ordered masks, with full source-versus-target tariffs."""
    need(len(planes) == 5, "five complete planes")
    bases = [[q for i, plane in enumerate(planes) if mask >> i & 1 for q in plane]
             for mask in range(32)]
    records = []
    for left in range(32):
        for right in range(32):
            cost = pairing(bases[left], bases[right])
            hits = tuple(int(bool(left & ((1 << i) | (1 << j)))
                             and bool(right & ((1 << i) | (1 << j)))) for i, j in Q)
            hits += (int(bool(left & right & 4)), int(bool(left & right & 16)))
            defect = 2 * cost - 2 * sum(hits[:4]) - sum(hits[4:])
            records.append(Support(left, right, cost, hits, defect,
                                   int(bool(left & 20) and bool(right & 20))))
    return tuple(records)


def trace_compatible(record, target):
    """Necessary per-term traces for blocks whose term counts are tight.

    target holds four Q term counts, the counts at planes 2 and 4, and total
    tariff defect. A tight I4 block gives z_i+z_j=its hit; a tight I2 block
    gives z_i=its hit. Off the common support z_i=0. Q is a path, so affine
    propagation and anchor consistency solve this system exactly. Oversized
    blocks supply no individual trace equation.
    """
    graph = [[] for _ in range(5)]
    for k, (i, j) in enumerate(Q):
        if target[k] == 4:
            graph[i].append((j, record.hits[k]))
            graph[j].append((i, record.hits[k]))
    anchors = {i: 0 for i in range(5) if not (record.left & record.right) >> i & 1}
    if target[4] == 2:
        anchors[2] = record.hits[4]
    if target[5] == 2:
        anchors[4] = record.hits[5]
    unseen = set(range(5))
    while unseen:
        start = min(unseen)
        affine = {start: (1, 0)}
        todo = [start]
        fixed = None
        while todo:
            i = todo.pop()
            unseen.discard(i)
            sign, offset = affine[i]
            if i in anchors:
                value = (anchors[i] - offset) * sign
                if fixed is not None and value != fixed:
                    return False
                fixed = value
            for j, total in graph[i]:
                if j not in affine:
                    affine[j] = (-sign, total - offset)
                    todo.append(j)
    return True


def increments(record):
    return record.hits + (record.defect, record.missing)


def search_case(records, target, *, use_trace=True):
    """Unbounded profile addition, capped only by necessary block counts.

    The first seven coordinates must equal target. The eighth records whether
    at least four terms touch the missing I4 block, and is saturated at four.
    Reusing a profile arbitrarily often is allowed. Zero-tariff records are
    skipped only after checking all eight increments, including the missing
    block, are zero. No coefficient menu or fixed term limit is imposed.
    """
    target = tuple(target)
    need(len(target) == 7 and all(type(n) is int and n >= 0 for n in target),
         "seven nonnegative target counts")
    profiles = set()
    for record in records:
        profile = increments(record)
        need(record.defect >= 0, "weighted tariff inequality")
        if record.cost == 0:
            need(profile == (0,) * 8, "zero-price record must have zero increments")
            continue
        need(any(profile[:7]), "positive-price profile must advance a bounded count")
        if record.defect <= target[6] and (not use_trace or trace_compatible(record, target)):
            profiles.add(profile)
    profiles = sorted(profiles)
    zero = (0,) * 8
    seen = {zero}
    todo = deque([zero])
    while todo:
        state = todo.popleft()
        for profile in profiles:
            new = tuple(state[i] + profile[i] for i in range(7))
            if any(new[i] > target[i] for i in range(7)):
                continue
            new += (min(4, state[7] + profile[7]),)
            if new not in seen:
                seen.add(new)
                todo.append(new)
    return {"target": list(target), "profiles": len(profiles), "states": len(seen),
            "reachable": target + (4,) in seen}


def cost19_targets():
    """All nonnegative allocations of the two-unit defect budget."""
    targets = [(4, 4, 4, 4, 2, 2, 2)]
    for i in range(4):
        target = [4, 4, 4, 4, 2, 2, 0]
        target[i] = 5
        targets.append(tuple(target))
    for n2, n4 in ((3, 2), (2, 3), (4, 2), (2, 4), (3, 3)):
        targets.append((4, 4, 4, 4, n2, n4, 6 - n2 - n4))
    return tuple(targets)


def baseline_terms():
    terms = []
    for i in range(5):
        vector = [0] * 10
        vector[2 * i + 1] = vector[2 * ((i + 1) % 5)] = 1
        terms.append((Fraction(1), tuple(vector), tuple(vector)))
    return tuple(terms)


def check_fit(planes, terms):
    """Check exact asymmetric fixtures against every strict scalar entry."""
    matrix = [[Fraction(0) for _ in range(10)] for _ in range(10)]
    total = 0
    for weight, left, right in terms:
        need(len(left) == len(right) == 10, "ten scalar coordinates per factor")
        weight = Fraction(weight)
        left, right = [Fraction(x) for x in left], [Fraction(x) for x in right]
        if not weight:
            continue
        source = [q for i, plane in enumerate(planes) if any(left[2*i:2*i+2]) for q in plane]
        target = [q for i, plane in enumerate(planes) if any(right[2*i:2*i+2]) for q in plane]
        total += pairing(source, target)
        for i in range(10):
            for j in range(10):
                matrix[i][j] += weight * left[i] * right[j]
    for i in range(10):
        for j in range(10):
            if i == j or pairing(planes[i // 2], planes[j // 2]) != 0:
                need(matrix[i][j] == int(i == j), f"strict scalar mask at ({i}, {j})")
    return total


def build():
    matching, planes = load_geometry()
    local = core(planes)
    records = support_records(local)
    need(all(record.defect >= 0 for record in records), "weighted cost-18 premise")
    zero = [r for r in records if r.cost == 0]
    need(all(increments(r) == (0,) * 8 for r in zero), "free terms affect no forced block")

    tight = [r for r in records if r.defect == 0]
    compatible = [r for r in tight if trace_compatible(r, TIGHT_TARGET)]
    positive = [r for r in compatible if r.cost]
    need(all(r.missing == r.hits[4] == r.hits[5] for r in compatible),
         "cost-18 equality forces missing-pair count to be two")
    missing = [[r.left, r.right] for r in positive if r.missing]
    need(missing == [[20, 20], [20, 28], [28, 20], [28, 28]],
         "complete cost-18 missing-pair support census")

    cases = [search_case(records, target) for target in cost19_targets()]
    need(all(not case["reachable"] for case in cases), "cost-19 support exclusion")
    baseline = baseline_terms()
    need(check_fit(local, baseline) == 20, "sharp complete strict-mask baseline")
    by_masks = {(r.left, r.right): r for r in records}
    edge_masks = [(1 << i) | (1 << ((i + 1) % 5)) for i in range(5)]
    baseline_supports = [by_masks[mask, mask] for mask in edge_masks]
    baseline_counts = tuple(sum(increments(r)[i] for r in baseline_supports) for i in range(8))
    need(baseline_counts == (4, 4, 4, 4, 2, 2, 4, 4), "baseline profile counts")
    positive_case = search_case(baseline_supports, baseline_counts[:7])
    need(positive_case["reachable"], "cost-20 baseline must remain reachable")

    # All ten principal identity-block rank counts pass, but traces do not.
    masks = ((28, 28), (19, 19), (7, 7), (14, 24), (1, 4))
    relaxed = [by_masks[pair] for pair in masks]
    need(sum(r.cost for r in relaxed) == 19, "rank-count relaxation cost")
    pair_counts = [sum(r.hits[i] for r in relaxed) for i in range(4)]
    pair_counts.append(sum(r.missing for r in relaxed))
    singleton_counts = [sum(bool((r.left & r.right) >> i & 1) for r in relaxed)
                        for i in range(5)]
    need(pair_counts == [4] * 5 and singleton_counts == [2] * 5,
         "all ten principal identity-block rank counts")
    relaxed_target = TIGHT_TARGET[:6] + (2,)
    need(sum(r.defect for r in relaxed) == relaxed_target[6], "relaxation defect budget")
    rejected = [[r.left, r.right] for r in relaxed if not trace_compatible(r, relaxed_target)]
    need(bool(rejected), "rank counts alone must not be accepted as a fitting decoder")

    prices = [record.cost for record in records]
    return {
        "schema_version": 1,
        "claim": "minimum_asymmetric_cost_20_on_named_core",
        "coefficient_fields": ["Q", "R", "C"],
        "core": list(CORE),
        "ports": [port for i in CORE for port in matching[i]],
        "binary_labels": local,
        "support_certificate": {
            "ordered_pairs": len(records),
            "zero_tariff_pairs": len(zero),
            "nonempty_zero_tariff_pairs": sum(bool(r.left and r.right) for r in zero),
            "tariff_sha256": hashlib.sha256(json.dumps(prices, separators=(",", ":")).encode()).hexdigest(),
            "weighted_lower_bound": 18,
            "tight_pairs": len(tight),
            "tight_positive_pairs": sum(bool(r.cost) for r in tight),
        },
        "cost18": {
            "trace_compatible_pairs": len(compatible),
            "positive_trace_compatible_pairs": len(positive),
            "missing_pair_positive_supports": missing,
            "excluded": True,
        },
        "cost19_cases": cases,
        "baseline": {"term_count": len(baseline), "cost": 20,
                     "reachability": positive_case},
        "controls": {
            "all_principal_rank_only_cost19": {
                "supports": [list(pair) for pair in masks],
                "cost": 19,
                "pair_counts": pair_counts,
                "singleton_counts": singleton_counts,
                "trace_rejected_supports": rejected,
                "scope": "five forced I4 principal blocks and five I2 plane blocks",
            },
        },
        "no_new_kappa": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print the deterministic receipt")
    args = parser.parse_args()
    result = build()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        need(result == json.loads((HERE / "RESULT.json").read_bytes()), "receipt mismatch")
        print("PASS_C5_ASYMMETRIC_COST_FLOOR minimum=20 core=13,23,35,16,34 no_new_kappa")


if __name__ == "__main__":
    main()
