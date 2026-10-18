#!/usr/bin/env python3
"""Independent k=3,q=2 shortening audit; Python 3.10+, standard library only.

Copyright 2026 Sam Sung. Apache-2.0. Substantial OpenAI Codex assistance.
This verifies the finite shortening lemma, not all rank-three global subcodes.
"""
import argparse
from collections import Counter
import hashlib
from itertools import combinations, product
import json
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


def ports(p, k):
    return [sum(1 << (2 * i + sign) for i, sign in zip(indices, signs))
            for indices in combinations(range(p), k)
            for signs in product((0, 1), repeat=k)]


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


def nullspace(equations, dimension):
    pivots = basis(equations)
    vectors = []
    for free in range(dimension):
        if free in pivots:
            continue
        vector = 1 << free
        for pivot in sorted(pivots):
            if (pivots[pivot] & vector).bit_count() % 2:
                vector ^= 1 << pivot
        require(all((equation & vector).bit_count() % 2 == 0 for equation in equations),
                "invalid restriction-kernel vector")
        vectors.append(vector)
    require(len(basis(vectors)) == dimension - len(pivots), "incomplete restriction kernel")
    return vectors


def words_from_basis(pivots):
    words = [0]
    for row in pivots.values():
        words += [word ^ row for word in words]
    require(len(set(words)) == len(words), "dependent enumeration basis")
    return words


def verify():
    full_ports, residual_ports = ports(5, 3), ports(4, 2)
    generators = [sum(1 << j for j, port in enumerate(full_ports) if port & face == face)
                  for degree in range(3) for face in ports(5, degree)]
    full_rows = list(basis(generators).values())
    require(len(full_ports) == 80 and len(full_rows) == 40, "full global code")
    require(belongs(generators[0], basis(generators[1:])), "empty-star redundancy at odd k=3")

    graph_rows = [(1 << len(residual_ports)) - 1]
    graph_rows += [sum(1 << j for j, port in enumerate(residual_ports) if port >> vertex & 1)
                   for vertex in range(8)]
    graph_basis = basis(graph_rows)
    blocks = [sum(1 << j for j, port in enumerate(residual_ports)
                  if {vertex // 2 for vertex in range(8) if port >> vertex & 1} == set(indices))
              for indices in combinations(range(4), 2)]
    block_basis, extended_basis = basis(blocks), basis(graph_rows + blocks)
    require(len(graph_basis) == 8 and len(block_basis) == 6 and len(extended_basis) == 10,
            "residual graph, block, and extended-space dimensions")
    intersection_dimension = len(graph_basis) + len(block_basis) - len(extended_basis)
    require(intersection_dimension == 4, "unsigned intersection dimension")
    graph_words, extended_words = words_from_basis(graph_basis), words_from_basis(extended_basis)
    require(min(word.bit_count() for word in graph_words if word) == 6, "graph minimum distance")
    require(min(word.bit_count() for word in extended_words if word) == 4, "extended minimum distance")
    minimum_words = {word for word in extended_words if word.bit_count() == 4}
    require(minimum_words == set(blocks), "extended minimum words are precisely unsigned blocks")
    require(all(not (left & right) for left, right in combinations(blocks, 2)), "block disjointness")

    residual_index = {port: j for j, port in enumerate(residual_ports)}
    cases = []
    for selected_pair in range(5):
        pair_mask = 3 << (2 * selected_pair)
        zero_columns = [j for j, port in enumerate(full_ports) if not port & pair_mask]
        equations = [sum(((row >> column) & 1) << i for i, row in enumerate(full_rows))
                     for column in zero_columns]
        coefficients = nullspace(equations, len(full_rows))
        shortened_rows = [combine(vector, full_rows) for vector in coefficients]
        require(len(basis(shortened_rows)) == 18, "shortened-space dimension")
        remaining_pairs = [pair for pair in range(5) if pair != selected_pair]
        slices = []
        for word in shortened_rows:
            plus, minus = 0, 0
            for column, port in enumerate(full_ports):
                if not (word >> column & 1):
                    continue
                require(port & pair_mask, "shortened word survives outside selected pair")
                residual = sum(((port >> (2 * pair)) & 3) << (2 * j)
                               for j, pair in enumerate(remaining_pairs))
                bit = 1 << residual_index[residual]
                if port >> (2 * selected_pair) & 1:
                    plus |= bit
                else:
                    minus |= bit
            require(belongs(plus, extended_basis) and belongs(minus, extended_basis),
                    "slice does not belong to extended residual space")
            require(belongs(plus ^ minus, graph_basis), "two slices have different quotient classes")
            slices.append((plus, minus))
        projection_ranks = [len(basis(pair[sign] for pair in slices)) for sign in (0, 1)]
        require(projection_ranks == [10, 10], "slice projection dimensions")
        require(any(not belongs(word, graph_basis) for pair in slices for word in pair),
                "unsigned extension is necessary, not just a redundant presentation")
        cases.append(dict(selected_pair=selected_pair, avoided_port_count=len(zero_columns),
                          avoidance_rank=len(basis(equations)), shortening_rank=len(shortened_rows),
                          slice_projection_ranks=projection_ranks,
                          shortening_basis_sha256=digest(shortened_rows), slice_basis_sha256=digest(slices)))

    return dict(status="PASS", arithmetic="exact F2 integer bitsets",
                scope="Complete finite linear-space audit of the k=3,p=5 shortening at all five original pairs. "
                      "Every shortening basis vector is checked; linearity extends containment and quotient "
                      "agreement to its full span. All residual E words are enumerated. This is not an "
                      "enumeration of every global codeword or rank-three subcode; the proof in "
                      "HIGHER-WEIGHTS.md supplies the third-weight conclusion.",
                global_ports=len(full_ports), global_degree_at_most_two_generators=len(generators),
                global_rank=len(full_rows), global_nonempty_rank=len(basis(generators[1:])),
                residual_ports=len(residual_ports), residual_graph_rank=len(graph_basis),
                unsigned_block_rank=len(block_basis), extended_rank=len(extended_basis),
                unsigned_graph_intersection_rank=intersection_dimension,
                extended_quotient_rank=len(extended_basis) - len(graph_basis),
                residual_graph_words=len(graph_words), extended_words=len(extended_words),
                extended_weight_distribution={str(weight): count for weight, count in
                                              sorted(Counter(word.bit_count() for word in extended_words).items())},
                extended_minimum_word_masks=sorted(minimum_words), shortening_cases=cases,
                negative_controls=["the graph-only slice space rejects valid shortened words",
                                   "every weight-four E word is a single unsigned block",
                                   "distinct weight-four E words have disjoint supports",
                                   "the k=3 global empty star is already in the nonempty span"])


def self_test(result):
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        script, receipt = directory / "boundary_verify.py", directory / "BOUNDARY-RESULTS.json"
        script.write_bytes(Path(__file__).read_bytes())
        receipt.write_text(json.dumps(result))
        command = [sys.executable, "-I", "-O", "-B", str(script)]
        replay = subprocess.run(command, capture_output=True, text=True)
        require(replay.returncode == 0, f"isolated optimized replay failed: {replay.stderr}")
        receipt.write_text(json.dumps(dict(result, status="CORRUPTED")))
        protected = directory / "protected.json"
        protected.write_text("preserve existing output\n")
        replay = subprocess.run(command + ["--check", str(receipt), "--write", str(protected)],
                                capture_output=True, text=True)
        require(replay.returncode != 0, "corrupted receipt was accepted")
        require(protected.read_text() == "preserve existing output\n", "failed check overwrote output")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a deterministic receipt after checks pass")
    parser.add_argument("--check", type=Path, help="compare with this receipt before writing output")
    parser.add_argument("--self-test", action="store_true", help="check optimized relocation and failure preservation")
    args = parser.parse_args()
    result = verify()
    if args.check or not args.write:
        receipt = args.check or HERE / "BOUNDARY-RESULTS.json"
        require(json.loads(receipt.read_text()) == result, f"receipt mismatch: {receipt}")
    if args.self_test:
        self_test(result)
    if args.write:
        args.write.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS_K3_BOUNDARY: 5 complete shortening spaces; 90 basis vectors; "
          "1024 residual E words; 6 literal weight-four blocks; 4 control categories")


if __name__ == "__main__":
    main()
