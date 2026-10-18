#!/usr/bin/env python3
"""Exact independent k=2 hierarchy verification; Python 3.10+, stdlib only.

Copyright 2026 Sam Sung. Apache-2.0. Substantial OpenAI Codex assistance.
No assertions or imports from the predecessor verifiers. The searches do not
use the proposed hierarchy formulas; formulas are compared only afterward.
"""
import argparse
from collections import Counter
import hashlib
from itertools import combinations
import json
from math import comb
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def basis(rows):
    pivots = {}
    for word in rows:
        while word:
            pivot = word.bit_length() - 1
            if pivot in pivots:
                word ^= pivots[pivot]
            else:
                pivots[pivot] = word
                break
    return pivots


def belongs(word, pivots):
    for pivot in sorted(pivots, reverse=True):
        if word >> pivot & 1:
            word ^= pivots[pivot]
    return word == 0


def combine(coefficients, rows):
    word = 0
    for i, row in enumerate(rows):
        if coefficients >> i & 1:
            word ^= row
    return word


def graph_model(p):
    edges = [(u, v) for u, v in combinations(range(2 * p), 2) if u // 2 != v // 2]
    rows = [sum(1 << e for e, edge in enumerate(edges) if v in edge) for v in range(2 * p)]
    return edges, rows


def code_basis(rows, empty):
    generators = rows + ([(1 << max(row.bit_length() for row in rows)) - 1] if empty else [])
    independent = []
    for row in generators:
        if not belongs(row, basis(independent)):
            independent.append(row)
    return independent


def formula(p, empty):
    n, size = 2 * p, 2 * p * (p - 1)
    cut = [size - comb(n - r, 2) + max(0, p - r) for r in range(1, n)]
    if not empty or p == 2:
        return cut
    return [cut[0]] + [min(cut[r - 1], size - (n - r + 1) ** 2 // 4)
                      for r in range(2, n)] + [size]


def graph_components(n, edges, edge_mask):
    adjacent = [[] for _ in range(n)]
    for e, (u, v) in enumerate(edges):
        if edge_mask >> e & 1:
            adjacent[u].append(v)
            adjacent[v].append(u)
    colors, components, bipartite = {}, 0, True
    for root in range(n):
        if root in colors:
            continue
        components += 1
        colors[root] = 0
        stack = [root]
        while stack:
            u = stack.pop()
            for v in adjacent[u]:
                if v not in colors:
                    colors[v] = 1 - colors[u]
                    stack.append(v)
                elif colors[v] == colors[u]:
                    bipartite = False
    return components, bipartite


def partition_tables(n, edges):
    """All labeled vertex partitions, via subset DP; all cuts in every block.

    A transition chooses the block containing the lowest remaining vertex.
    No block-size, convexity, symmetry or optimal-component assumption is used.
    Disconnected block realizations are permitted: their true component count
    can only be greater, so maximizing over at least the required blocks is valid.
    """
    order = 1 << n
    induced, cut = [0] * order, [0] * order
    block_visits, cut_visits, transitions = 0, 0, 0
    tables = [[[0]], [[0]]]
    choices = [[[0]], [[0]]]
    for mask in range(1, order):
        anchor = mask & -mask
        vertex = anchor.bit_length() - 1
        rest = mask ^ anchor
        induced[mask] = induced[rest]
        for e, (u, v) in enumerate(edges):
            if vertex == u and rest >> v & 1 or vertex == v and rest >> u & 1:
                induced[mask] |= 1 << e
        left = (mask - 1) & mask
        while left:
            if left & anchor:
                candidate = induced[mask] ^ induced[left] ^ induced[mask ^ left]
                cut_visits += 1
                if candidate.bit_count() > cut[mask].bit_count():
                    cut[mask] = candidate
            left = (left - 1) & mask
        for kind in range(2):
            tables[kind].append([-1] * (mask.bit_count() + 1))
            choices[kind].append([0] * (mask.bit_count() + 1))
        block = mask
        while block:
            if block & anchor:
                block_visits += 1
                remainder = mask ^ block
                for count in range(len(tables[0][remainder])):
                    if tables[0][remainder][count] < 0:
                        continue
                    transitions += 1
                    for kind, weights in enumerate((induced, cut)):
                        value = weights[block].bit_count() + tables[kind][remainder][count]
                        if value > tables[kind][mask][count + 1]:
                            tables[kind][mask][count + 1] = value
                            choices[kind][mask][count + 1] = block
            block = (block - 1) & mask
    require(block_visits == (3 ** n - 1) // 2, "complete anchored-block census")
    require(cut_visits == (3 ** n - 2 ** (n + 1) + 1) // 2, "complete nontrivial-cut census")
    return tables, choices, (induced, cut), dict(
        vertex_subsets=order, block_choices=block_visits,
        cut_assignments=cut_visits, partition_transitions=transitions)


def retained_witness(n, required, kind, tables, choices, weights):
    if required > n:
        return -1, 0
    mask = (1 << n) - 1
    count = max(range(required, n + 1), key=lambda count: tables[kind][mask][count])
    retained = tables[kind][mask][count]
    witness = 0
    while mask:
        block = choices[kind][mask][count]
        require(block and block & mask == block, "invalid partition reconstruction")
        witness |= weights[kind][block]
        mask ^= block
        count -= 1
    require(count == 0 and witness.bit_count() == retained, "partition edge count")
    return retained, witness


def kernel(rows, zero_edges, size):
    equations = [sum(((row >> e) & 1) << j for j, row in enumerate(rows))
                 for e in range(size) if zero_edges >> e & 1]
    pivots = basis(equations)
    vectors = []
    for free in range(len(rows)):
        if free in pivots:
            continue
        vector = 1 << free
        for pivot in sorted(pivots):
            if (pivots[pivot] & vector).bit_count() % 2:
                vector ^= 1 << pivot
        require(all((equation & vector).bit_count() % 2 == 0 for equation in equations),
                "restriction-kernel vector")
        vectors.append(vector)
    return vectors


def decoder_witness(rows, zero_edges, rank, size):
    coefficients = kernel(rows, zero_edges, size)[:rank]
    require(len(coefficients) == rank, "insufficient kernel dimension")
    words = [combine(vector, rows) for vector in coefficients]
    information = []
    for column in range(size):
        found = next((i for i in range(len(information), rank) if words[i] >> column & 1), None)
        if found is None:
            continue
        pivot = len(information)
        words[pivot], words[found] = words[found], words[pivot]
        coefficients[pivot], coefficients[found] = coefficients[found], coefficients[pivot]
        for i in range(rank):
            if i != pivot and words[i] >> column & 1:
                words[i] ^= words[pivot]
                coefficients[i] ^= coefficients[pivot]
        information.append(column)
    require(len(information) == rank, "dependent decoder rows")
    support = 0
    for word in words:
        support |= word
    require(support.bit_count() == size - zero_edges.bit_count(), "non-sharp witness support")
    selected = sum(1 << e for e in information)
    deleted = support ^ selected
    surviving = ((1 << size) - 1) ^ deleted
    for coefficient, word, target in zip(coefficients, words, information):
        require(combine(coefficient, rows) == word, "literal observation combination")
        require(word & surviving == 1 << target, "simultaneous target identity")
    for edge in range(size):
        if deleted >> edge & 1:
            restored = surviving | 1 << edge
            restricted = basis(row & restored for row in rows)
            require(not all(belongs(1 << target, restricted) for target in information),
                    "single-edge restoration still decodes every target")
    return dict(rank=rank, support_size=support.bit_count(), retained_edge_mask=zero_edges,
                information_edge_indices=information, coefficient_masks=coefficients,
                decoder_word_masks=words, deletions=deleted.bit_count())


def partition_case(p):
    n = 2 * p
    edges, stars = graph_model(p)
    size = len(edges)
    tables, choices, weights, counts = partition_tables(n, edges)
    cases = []
    for empty in (False, True):
        rows = code_basis(stars, empty)
        require(len(rows) == n - 1 + empty, "graph-code rank")
        witnesses = []
        for rank in range(1, len(rows) + 1):
            candidates = [retained_witness(n, rank + 1, 0, tables, choices, weights)]
            if empty:
                candidates.append(retained_witness(n, rank, 1, tables, choices, weights))
            _, retained = max(candidates, key=lambda pair: pair[0])
            witnesses.append(decoder_witness(rows, retained, rank, size))
        hierarchy = [witness["support_size"] for witness in witnesses]
        require(hierarchy == formula(p, empty), "formula versus exact partition hierarchy")
        cases.append(dict(empty_star=empty, dimension=len(rows), hierarchy=hierarchy,
                          observation_basis_rows=rows, witnesses=witnesses))
    return dict(p=p, ports=size, searches=counts,
                unrestricted_retained_by_block_count=tables[0][-1][1:],
                bipartite_retained_by_block_count=tables[1][-1][1:],
                edge_order=[list(edge) for edge in edges], codes=cases)


def exhaustive_edge_sets(p):
    edges, stars = graph_model(p)
    n, size = 2 * p, len(edges)
    output = []
    for empty in (False, True):
        rows = code_basis(stars, empty)
        hierarchy = [size + 1] * len(rows)
        for mask in range(1 << size):
            dimension = len(rows) - len(basis(row & mask for row in rows))
            components, bipartite = graph_components(n, edges, mask)
            predicted = components - 1 + (empty and p >= 3 and bipartite)
            require(dimension == predicted, "graph kernel formula versus literal restriction rank")
            for rank in range(dimension):
                hierarchy[rank] = min(hierarchy[rank], size - mask.bit_count())
        require(hierarchy == formula(p, empty), "all edge subsets versus hierarchy formula")
        output.append(dict(p=p, empty_star=empty, dimension=len(rows),
                           edge_sets=1 << size, hierarchy=hierarchy))
    return output


def exhaustive_subspaces(p, empty, ranks=None):
    edges, stars = graph_model(p)
    rows = code_basis(stars, empty)
    dimension, size = len(rows), len(edges)
    evaluations = [combine(vector, rows) for vector in range(1 << dimension)]
    hierarchy, counts, minimum_counts = [], [], []
    checked_ranks = list(ranks or range(1, dimension + 1))
    for rank in checked_ranks:
        minimum, count, attaining = size + 1, 0, 0
        for pivots in combinations(range(dimension), rank):
            slots = [(i, column) for i, pivot in enumerate(pivots)
                     for column in range(pivot + 1, dimension) if column not in pivots]
            for assignments in range(1 << len(slots)):
                vectors = [1 << pivot for pivot in pivots]
                for bit, (i, column) in enumerate(slots):
                    if assignments >> bit & 1:
                        vectors[i] |= 1 << column
                support = 0
                for vector in vectors:
                    support |= evaluations[vector]
                weight = support.bit_count()
                count += 1
                if weight < minimum:
                    minimum, attaining = weight, 1
                elif weight == minimum:
                    attaining += 1
        numerator, denominator = 1, 1
        for i in range(rank):
            numerator *= (1 << dimension) - (1 << i)
            denominator *= (1 << rank) - (1 << i)
        require(count == numerator // denominator, "Gaussian binomial subspace count")
        hierarchy.append(minimum)
        counts.append(count)
        minimum_counts.append(attaining)
    require(hierarchy == [formula(p, empty)[rank - 1] for rank in checked_ranks],
            "RREF full-code hierarchy")
    if p >= 5 and 3 in checked_ranks:
        require(minimum_counts[checked_ranks.index(3)] == 8 * comb(p, 3),
                "complete optimal rank-three census versus triangle classification")
    return dict(p=p, empty_star=empty, dimension=dimension, ranks=checked_ranks, hierarchy=hierarchy,
                subspaces_by_rank=counts, minimum_subspaces_by_rank=minimum_counts,
                nonzero_subspaces=sum(counts), generator_rows_sha256=digest(rows))


def spectrum_case(p, empty):
    _, stars = graph_model(p)
    rows = code_basis(stars, empty)
    words = [0]
    for row in rows:
        words += [word ^ row for word in words]
    require(len(set(words)) == 1 << len(rows), "complete distinct graph-word census")
    distribution = Counter(word.bit_count() for word in words)
    positive_weights = sorted(weight for weight in distribution if weight)
    require(positive_weights[:2] == [2 * p - 2, 4 * p - 6], "first two graph weights")
    return dict(p=p, empty_star=empty, dimension=len(rows), words=len(words),
                weight_distribution={str(weight): count for weight, count in sorted(distribution.items())})


def verify():
    partitions = [partition_case(p) for p in range(3, 7)]
    edges = [case for p in (2, 3) for case in exhaustive_edge_sets(p)]
    subspaces = [exhaustive_subspaces(p, empty) for p in (3, 4) for empty in (False, True)]
    triangles = [exhaustive_subspaces(5, empty, ranks=(3,)) for empty in (False, True)]
    spectra = [spectrum_case(p, empty) for p in range(5, 10) for empty in (False, True)]
    require(partitions[1]["codes"][0]["hierarchy"][4] == 21 and
            partitions[1]["codes"][1]["hierarchy"][4] == 20, "empty-star distinction control")
    require(partitions[0]["bipartite_retained_by_block_count"][0] == 8,
            "odd-p rank-one balanced-cut obstruction")
    require(edges[1]["dimension"] == 3, "p=2 redundant constant control")
    return dict(status="PASS", arithmetic="exact F2 integer bitsets",
                scope="Finite independent graph-code checks only. Partition DP exhausts all labeled vertex "
                      "partitions and all cuts within blocks for p=3,4,5,6. Literal edge-subset ranks "
                      "are exhaustive at p=2,3; literal code subspaces are exhaustive at p=3,4, and rank-three "
                      "subspaces at p=5. Full graph-code weight distributions are checked at p=5,...,9. "
                      "Uniform formulas require the separate mathematical proof; no supplier or kappa claim.",
                partition_cases=partitions, exhaustive_edge_sets=edges, exhaustive_subspaces=subspaces,
                optimal_triangle_census=triangles, full_graph_spectra=spectra,
                negative_controls=["every single deleted-edge restoration breaks its simultaneous decoder",
                                   "p=2 has redundant empty star and dimension three",
                                   "odd p=3 loses one edge against the naive balanced complete cut",
                                   "omitting the bipartite branch gives a false fifth weight at p=4"])


def self_test(result):
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        script = directory / "higher_verify.py"
        script.write_bytes(Path(__file__).read_bytes())
        receipt = directory / "HIGHER-RESULTS.json"
        receipt.write_text(json.dumps(result))
        command = [sys.executable, "-I", "-O", "-B", str(script)]
        run = subprocess.run(command, capture_output=True, text=True)
        require(run.returncode == 0, f"isolated optimized relocated replay: {run.stderr}")
        receipt.write_text(json.dumps(dict(result, status="CORRUPTED")))
        protected = directory / "protected.json"
        protected.write_text("preserve this output\n")
        run = subprocess.run(command + ["--check", str(receipt), "--write", str(protected)],
                             capture_output=True, text=True)
        require(run.returncode != 0, "corrupt receipt accepted")
        require(protected.read_text() == "preserve this output\n", "failed check overwrote output")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write receipt after checks pass")
    parser.add_argument("--check", type=Path, help="compare receipt before writing output")
    parser.add_argument("--self-test", action="store_true", help="check relocation and failure preservation")
    args = parser.parse_args()
    result = verify()
    if args.check or not args.write:
        receipt = args.check or HERE / "HIGHER-RESULTS.json"
        require(json.loads(receipt.read_text()) == result, f"receipt mismatch: {receipt}")
    if args.self_test:
        self_test(result)
    if args.write:
        args.write.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    witnesses = [witness for case in result['partition_cases']
                 for code in case['codes'] for witness in code['witnesses']]
    print("PASS_HIGHER_GRAPH: 4 exact partition DPs; "
          f"{sum(case['edge_sets'] for case in result['exhaustive_edge_sets'])} edge restrictions; "
          f"{sum(case['nonzero_subspaces'] for case in result['exhaustive_subspaces'])} code subspaces; "
          f"{sum(case['nonzero_subspaces'] for case in result['optimal_triangle_census'])} rank-three census subspaces; "
          f"{sum(case['words'] for case in result['full_graph_spectra'])} spectral words; "
          f"{len(witnesses)} optimal simultaneous decoder witnesses; "
          f"{sum(witness['deletions'] for witness in witnesses)} restoration controls")


if __name__ == "__main__":
    main()
