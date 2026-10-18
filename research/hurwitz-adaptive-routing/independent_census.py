#!/usr/bin/env python3
"""Separate conflict-graph check of every attaining four-port header.

Does not import verify.py or use its fibre-width lower-bound calculation.
Builds receiver ambiguity graphs and exhausts their independent sets instead.
"""

from itertools import combinations
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def ambiguity_graph(source_pair: tuple[int, int]) -> list[int]:
    neighbors = [0] * 16
    source_mask = sum(1 << bit for bit in source_pair)
    for x in range(16):
        for y in range(x + 1, 16):
            difference = x ^ y
            if difference & source_mask:
                continue
            ambiguous = any(
                difference & (1 << receiver) and not difference & (1 << (receiver ^ 1))
                for receiver in range(4)
            )
            if ambiguous:
                neighbors[x] |= 1 << y
                neighbors[y] |= 1 << x
    return neighbors


def independent_sets(neighbors: list[int]) -> bytearray:
    valid = bytearray(65536)
    valid[0] = 1
    for subset in range(1, 65536):
        low = subset & -subset
        vertex = low.bit_length() - 1
        rest = subset ^ low
        valid[subset] = int(bool(valid[rest]) and not (neighbors[vertex] & rest))
    return valid


def calculate() -> dict:
    source_pairs = list(combinations(range(4), 2))
    valid = [independent_sets(ambiguity_graph(pair)) for pair in source_pairs]
    accepted = []
    witness_pairs = {}
    for function in range(1, 65535):
        # Branch supports may differ: independently choose a pair on each fibre.
        options = [[pair for pair, table in zip(source_pairs, valid) if table[subset]]
                   for subset in (65535 ^ function, function)]
        if all(options):
            accepted.append(function)
            witness_pairs[function] = options
    if len(accepted) != 30:
        raise ValueError("conflict graph census did not produce 30 headers")
    # A compact closed form for the recovered family, independently expanded.
    families = []
    for known_pair, other_pair in [((0, 1), (2, 3)), ((2, 3), (0, 1))]:
        family = set()
        for g in range(16):
            table = 0
            for x in range(16):
                known = ((x >> known_pair[0]) & 1) + 2 * ((x >> known_pair[1]) & 1)
                parity = ((x >> other_pair[0]) ^ (x >> other_pair[1])) & 1
                value = parity ^ ((g >> known) & 1)
                table |= value << x
            family.add(table)
        families.append(family)
    if families[0] | families[1] != set(accepted) or len(families[0] & families[1]) != 2:
        raise ValueError("closed-form optimum-header family differs")
    certificate = json.loads((ROOT / "CERTIFICATE.json").read_text())
    expected = certificate["four_port_census"]["optimal_nonconstant_headers"]
    if [row["truth_table"] for row in expected] != accepted:
        raise ValueError("certificate's complete optimal-header list differs")
    decodes = 0
    for row in expected:
        function = row["truth_table"]
        if row["raw_source_pairs_by_header"] != [list(map(list, choices)) for choices in witness_pairs[function]]:
            raise ValueError("certificate's source-pair witnesses differ")
        # Literal independent inversion, not just the independent-set recurrence.
        for x in range(16):
            header = function >> x & 1
            pair = witness_pairs[function][header][0]
            for receiver in range(4):
                candidates = [y for y in range(16)
                              if function >> y & 1 == header
                              and all((y >> p & 1) == (x >> p & 1) for p in pair)
                              and (y >> (receiver ^ 1) & 1) == (x >> (receiver ^ 1) & 1)]
                if not candidates or {y >> receiver & 1 for y in candidates} != {x >> receiver & 1}:
                    raise ValueError("literal receiver inversion failed")
                decodes += 1
    # A demanded bit changed while all declared inputs remain fixed must be
    # an edge. Forgetting the side-information restriction adds false edges.
    graph = ambiguity_graph((0, 1))
    if not (graph[0] & (1 << 4)):
        raise ValueError("missing demand ambiguity")
    if graph[0] & (1 << 12):
        raise ValueError("incorrectly ignored changed mate side information")
    if independent_sets(graph)[(1 << 0) | (1 << 4)]:
        raise ValueError("an ambiguous fibre was admitted")
    return {"source_pair_graphs": 6, "fibres_per_graph": 65536,
            "nonconstant_headers_checked": 65534, "attaining_headers": len(accepted),
            "closed_form_family_sizes": [len(f) for f in families], "family_intersection": 2,
            "literal_receiver_decodes": decodes, "graph_controls": 3}


if __name__ == "__main__":
    print(json.dumps(calculate(), sort_keys=True))
    print("PASS_HURWITZ_ADAPTIVE_CENSUS independent_conflict_graphs=6 optimal_headers=30")
