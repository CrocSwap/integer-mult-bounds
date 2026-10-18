#!/usr/bin/env python3
"""Exact support certificates for the physical C5 Gram cost floor.

thakrarsagar with substantial OpenAI Codex assistance. Apache-2.0.
Geometry and complete-plane tariff: Tekalign/PR2782 and its predecessors.
Principal-block method: Arham Tahir/PR2879; overlapping cover checked here.
"""
from fractions import Fraction
import gzip
import hashlib
from itertools import combinations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = "research/c5-dyadic-decoder-gate/inputs/"
CORE = (13, 23, 35, 16, 34)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def dot(left, right):
    return (left & right).bit_count() % 2


def pairing(left, right):
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
    raw = {}
    for pin in json.loads((HERE / "SOURCES.json").read_bytes())["files"]:
        if pin["usage"] == "input":
            value = (Path(root) / pin["path"]).read_bytes()
            need(hashlib.sha256(value).hexdigest() == pin["sha256"],
                 "source bytes changed: " + pin["path"])
            raw[pin["path"]] = value
    need(set(raw) == {INPUT + "DATA-PHASES.json.gz", INPUT + "MATCHING.json"},
         "two pinned geometry inputs")
    recipes = json.loads(gzip.decompress(raw[INPUT + "DATA-PHASES.json.gz"]))["recipes"]
    labels = {row["port"]: row["q"] for row in recipes}
    need(len(recipes) == len(labels) == 112 and sorted(labels) == list(range(112)),
         "complete distinct port domain")
    need(all(type(q) is int and 0 < q < 512 for q in labels.values()), "binary labels")
    matching = json.loads(raw[INPUT + "MATCHING.json"])["matching"]
    need(len(matching) == 56 and all(len(pair) == 2 for pair in matching)
         and sorted(port for pair in matching for port in pair) == list(range(112)),
         "complete plane partition")
    planes = [[labels[port] for port in pair] for pair in matching]
    need(all([[dot(a, b) for b in plane] for a in plane] == [[1, 0], [0, 1]]
             for plane in planes), "each full plane has Gram I2")
    return matching, planes


def orthogonal(left, right):
    return all(dot(a, b) == 0 for a in left for b in right)


def induced_cycles(planes):
    neighbors = [sum(1 << j for j, other in enumerate(planes)
                     if i != j and orthogonal(plane, other))
                 for i, plane in enumerate(planes)]
    cycles = []
    for group in combinations(range(len(planes)), 5):
        mask = sum(1 << i for i in group)
        # A simple two-regular graph on five vertices must be a C5.
        if all((neighbors[i] & mask).bit_count() == 2 for i in group):
            cycles.append(group)
    return cycles


def costs_for(planes):
    need(len(planes) == 5, "five full planes")
    result = []
    for mask in range(32):
        basis = [q for i, plane in enumerate(planes) if mask >> i & 1 for q in plane]
        result.append(pairing(basis, basis))
    return result


def check_gram(planes, terms):
    """Check rational fixtures; the written rank argument is coefficient-free."""
    matrix = [[Fraction(0) for _ in range(10)] for _ in range(10)]
    prices, cost = costs_for(planes), 0
    for weight, vector in terms:
        need(len(vector) == 10, "ten scalar coordinates")
        weight, vector = Fraction(weight), [Fraction(x) for x in vector]
        if not weight:
            continue
        mask = sum(1 << i for i in range(5) if vector[2*i] or vector[2*i+1])
        cost += prices[mask]
        for i in range(10):
            for j in range(10):
                matrix[i][j] += weight * vector[i] * vector[j]
    for i in range(10):
        for j in range(10):
            if i == j or not orthogonal(planes[i//2], planes[j//2]):
                need(matrix[i][j] == int(i == j), f"strict scalar mask at ({i}, {j})")
    return cost


def certificate(cycle, planes):
    local = [planes[i] for i in cycle]
    edges = [(i, j) for i, j in combinations(range(5), 2)
             if orthogonal(local[i], local[j])]
    need(len(edges) == 5 and all(sum(i in edge for edge in edges) == 2
                                for i in range(5)), "induced C5")
    blocks = [pair for pair in combinations(range(5), 2) if pair not in edges]
    prices = costs_for(local)
    touches = [sum(bool(mask & ((1 << i) | (1 << j))) for i, j in blocks)
               for mask in range(32)]
    need(all(price >= count for price, count in zip(prices, touches)),
         "tariff covers every charged identity block")

    # One axis per free edge, assigning each plane's two ports to distinct edges.
    terms = []
    for edge in edges:
        vector = [0] * 10
        for plane in edge:
            incident = [e for e in edges if plane in e]
            vector[2*plane + incident.index(edge)] = 1
        terms.append((1, vector))
    cost = check_gram(local, terms)
    need(cost == 20, "sharp five-edge baseline")
    return {"planes": list(cycle), "forced_identity_blocks": [list(p) for p in blocks],
            "tariffs": prices, "block_touches": touches,
            "lower_bound": 4 * len(blocks), "baseline_cost": cost,
            "baseline_vectors": [v for _, v in terms]}


def build():
    matching, planes = load_geometry()
    cycles = induced_cycles(planes)
    need(len(cycles) == 23 and tuple(sorted(CORE)) in cycles, "complete 23-cycle census")
    certificates = [certificate(cycle, planes) for cycle in cycles]
    core = [planes[i] for i in CORE]
    blocks = [(i, j) for i, j in combinations(range(5), 2)
              if not orthogonal(core[i], core[j])]
    left, right = 1 << 2, (1 << 0) | (1 << 4)
    asymmetric_cost = pairing(core[2], core[0] + core[4])
    touches = sum(bool(left & ((1 << i) | (1 << j)))
                  and bool(right & ((1 << i) | (1 << j))) for i, j in blocks)
    need(asymmetric_cost == 1 and touches == 2, "unequal-span scope control")
    return {"schema_version": 1, "status": "SHARP_GRAM_COST_20_ON_23_C5S",
            "cycle_count": len(cycles), "support_inequalities": 32 * len(cycles),
            "core_planes": list(CORE), "core_ports": [p for i in CORE for p in matching[i]],
            "certificates": certificates,
            "asymmetric_scope_control": {"left_plane_mask": left, "right_plane_mask": right,
                                         "tariff": asymmetric_cost, "block_touches": touches},
            "scope": "Finite Gram sums on these 23 strict scalar masks with additive full-plane "
                     "binary tariffs; arbitrary coefficients and supports. No arbitrary "
                     "unequal-span decoder, native supplier or new kappa claim."}


if __name__ == "__main__":
    actual = build()
    need(actual == json.loads((HERE / "RESULT.json").read_bytes()), "complete receipt differs")
    print("PASS_C5_GRAM_RANK_COVER", actual["cycle_count"], "cycles,",
          actual["support_inequalities"], "support inequalities; sharp cost 20")
