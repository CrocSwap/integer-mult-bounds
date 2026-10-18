#!/usr/bin/env python3
"""Independent finite geometry audit; no imports from primary/predecessor code.

Uses row sets for binary elimination and modular lower bounds plus exact
integer normal vectors for rational ranks. This is a finite audit, not a proof
assistant formalization of the all-k statement in README.md.

alephnan with substantial OpenAI Codex assistance. Apache-2.0.
"""

from collections import Counter
from itertools import combinations, product
from pathlib import Path
import argparse
import copy
import hashlib
import json


def need(value, reason):
    if not value:
        raise ValueError(reason)


def direct_geometry():
    """One positive-first vector from each antipodal doubled E8 root pair."""
    lines = set()
    for first, second in combinations(range(8), 2):
        for sign in (-1, 1):
            line = [0] * 8
            line[first], line[second] = 2, 2 * sign
            lines.add(tuple(line))
    for tail in product((-1, 1), repeat=7):
        line = (1,) + tail
        if sum(x < 0 for x in line) % 2 == 0:
            lines.add(line)
    frame = set()
    for first in (0, 2, 4, 6):
        for sign in (-1, 1):
            line = [0] * 8
            line[first], line[first + 1] = 2, sign * 2
            frame.add(tuple(line))
    need(len(lines) == 120 and len(frame) == 8, "root/frame enumeration")
    need(frame <= lines, "frame consists of roots")
    need(all(dot(x, x) == 8 for x in lines), "doubled root norm")
    need(all(dot(x, y) == 0 for x, y in combinations(frame, 2)),
         "frame orthogonality")
    return sorted(lines), sorted(frame), sorted(lines - frame)


def dot(left, right):
    return sum(x * y for x, y in zip(left, right))


def binary_basis(rows):
    """Gaussian elimination as symmetric differences of coordinate sets."""
    pivots = {}
    for source in rows:
        row = set(source)
        while row:
            lead = min(row)
            if lead in pivots:
                row.symmetric_difference_update(pivots[lead])
            else:
                pivots[lead] = row
                break
    return list(pivots.values())


def binary_rank(rows):
    return len(binary_basis(rows))


def prime_rank(rows, prime=101):
    """Rank over F_101, hence a rigorous lower bound for integer matrix rank/Q."""
    matrix = [[x % prime for x in row] for row in rows]
    if not matrix:
        return 0
    rank = 0
    for column in range(len(matrix[0])):
        pivot = next((i for i in range(rank, len(matrix))
                      if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        factor = pow(matrix[rank][column], -1, prime)
        matrix[rank] = [x * factor % prime for x in matrix[rank]]
        for i in range(rank + 1, len(matrix)):
            factor = matrix[i][column]
            matrix[i] = [(x - factor * y) % prime
                         for x, y in zip(matrix[i], matrix[rank])]
        rank += 1
        if rank == len(matrix[0]):
            break
    return rank


def pairing_rows(ports):
    """B(r,s) = (<r,s> + 1) mod 2 in undoubled coordinates."""
    rows = []
    for left in ports:
        row = set()
        for j, right in enumerate(ports):
            numerator = dot(left, right)
            need(numerator % 4 == 0, "integral root inner product")
            if (numerator // 4 + 1) % 2:
                row.add(j)
        rows.append(row)
    return rows


def all_nonzero_patterns(rows):
    basis = binary_basis(rows)
    need(len(basis) == 9, "full binary pairing rank must be nine")
    patterns = {frozenset()}
    for row in basis:
        patterns |= {pattern ^ frozenset(row) for pattern in patterns}
    need(len(patterns) == 512, "complete binary functional space")
    patterns.remove(frozenset())
    return sorted(patterns, key=lambda values: tuple(sorted(values)))


def audit_geometry():
    all_lines, frame, ports = direct_geometry()
    need(len(ports) == 112, "live port count")
    rows = pairing_rows(ports)
    patterns = all_nonzero_patterns(rows)
    rational_ranks = Counter()
    size_ranks = Counter()
    deficient = []
    canonical_patterns = []
    for pattern in patterns:
        vectors = [ports[i] for i in sorted(pattern)]
        lower = prime_rank(vectors)
        normals = [normal for normal in frame
                   if all(dot(vector, normal) == 0 for vector in vectors)]
        if normals:
            need(len(normals) == 1 and lower == 7,
                 "a unique exact normal and modular rank seven")
            rank = 7  # exact nonzero normal gives <=7; mod101 minor gives >=7.
            deficient.append({"support": sorted(pattern),
                              "normal_doubled": list(normals[0])})
        else:
            need(lower == 8, "full rational rank requires modular rank eight")
            rank = 8  # there are exactly eight columns.
        rational_ranks[rank] += 1
        size_ranks[(len(pattern), rank)] += 1
        canonical_patterns.append({"support": sorted(pattern), "rank": rank})
    need(rational_ranks == {7: 8, 8: 503}, "hyperplane rank census")
    need({tuple(row["normal_doubled"]) for row in deficient} == set(frame),
         "all deficient normals are exactly the omitted frame")
    supports = [{i for i, root in enumerate(ports) if dot(root, normal) != 0}
                for normal in frame]
    need(all(len(support) == 56 for support in supports), "frame support size")
    support_pair_ranks = [[binary_rank([rows[i] & right for i in left])
                           for right in supports] for left in supports]
    need(all(rank == 8 for row in support_pair_ranks for rank in row),
         "all 64 frame support-pair ranks must be eight")
    encoded = json.dumps(canonical_patterns, separators=(",", ":"),
                         sort_keys=True).encode("ascii")
    return {
        "root_lines": len(all_lines), "ports": len(ports),
        "pairing_rank": binary_rank(rows), "functionals": len(patterns),
        "rational_rank_histogram": {str(k): v for k, v in sorted(rational_ranks.items())},
        "size_rank_histogram": [[size, rank, count]
                                for (size, rank), count in sorted(size_ranks.items())],
        "frame_doubled": [list(row) for row in frame],
        "deficient": deficient, "support_pair_ranks": support_pair_ranks,
        "canonical_patterns_sha256": hashlib.sha256(encoded).hexdigest(),
    }


def mutation_controls():
    """Reject model changes which invalidate the finite premises."""
    _, frame, ports = direct_geometry()
    rows = pairing_rows(ports)
    changed = [set(row) for row in rows]
    changed[0].symmetric_difference_update({0})
    need(binary_rank(changed) != 9, "single corrupted pairing bit is detected")
    normal = frame[0]
    flat = [root for root in ports if dot(root, normal) == 0]
    outside = next(root for root in ports if dot(root, normal) != 0)
    need(prime_rank(flat) == 7 and prime_rank(flat + [outside]) == 8,
         "inserting an outside root destroys the deficient flat")
    wrong_normal = frame[1]
    need(any(dot(root, wrong_normal) != 0 for root in flat),
         "a substituted null normal is rejected")
    return ["corrupted pairing bit", "outside-root insertion", "wrong exact normal"]


def subset_determinant(matrix):
    """Exact determinant by subset dynamic programming, not Bareiss/pivots."""
    size = len(matrix)
    values = {0: 1}
    for row in matrix:
        following = {}
        for mask, coefficient in values.items():
            for column in range(size):
                if mask >> column & 1:
                    continue
                inversions = (mask >> (column + 1)).bit_count()
                value = coefficient * row[column] * (-1 if inversions % 2 else 1)
                following[mask | (1 << column)] = following.get(mask | (1 << column), 0) + value
        values = following
    return values[(1 << size) - 1]


def bind_receipt(receipt, independent):
    """Bind all finite hyperplanes/minors to RESULT, without primary imports.

    Cross-call fixtures and the prose theorem are deliberately outside this
    geometry auditor's coverage; the primary verifier checks its fixtures.
    """
    lines, expected_frame, ports = direct_geometry()
    geometry = receipt["geometry"]
    finite = receipt["finite_premises"]
    frame = [tuple(row) for row in geometry["standard_frame"]]
    need(len(frame) == 8 and set(frame) == set(expected_frame), "receipt frame")
    images = {}
    for line in lines:
        numerators = [dot(line, normal) for normal in frame]
        need(all(value % 4 == 0 for value in numerators), "frame-map integrality")
        image = tuple(value // 4 for value in numerators)
        first = next(value for value in image if value)
        if first < 0:
            image = tuple(-value for value in image)
        need(image not in images, "injective frame-coordinate map")
        images[image] = line
    hamming = [tuple(row) for row in geometry["hamming_roots"]]
    need(len(hamming) == 120 and set(hamming) == set(images), "receipt root geometry")
    source_lines = [images[row] for row in hamming]
    deleted = geometry["deleted_indices"]
    need(len(deleted) == 8 and len(set(deleted)) == 8
         and {source_lines[i] for i in deleted} == set(frame), "deleted frame indices")
    live = [i for i in range(120) if i not in deleted]
    port_index = {root: i for i, root in enumerate(ports)}
    source_to_port = {i: port_index[source_lines[i]] for i in live}
    labels = finite["labels_in_dual_coordinates"]
    need(len(labels) == 120 and all(type(label) is int and 0 < label < 512
                                  for label in labels), "nine-bit labels")
    expected_patterns = {tuple(sorted(pattern))
                         for pattern in all_nonzero_patterns(pairing_rows(ports))}
    deficient = {tuple(row["support"]): tuple(row["normal_doubled"])
                 for row in independent["deficient"]}
    records = finite["hyperplanes"]
    need(len(records) == 511 and {row["functional"] for row in records} == set(range(1, 512)),
         "all 511 functionals exactly once")
    seen_patterns = set()
    exceptional = []
    exceptional_supports = {}
    for row in records:
        functional = row["functional"]
        outside = [i for i in live if (labels[i] & functional).bit_count() % 2]
        pattern = tuple(sorted(source_to_port[i] for i in outside))
        need(pattern in expected_patterns and pattern not in seen_patterns,
             "receipt functional space equals full pairing row space")
        seen_patterns.add(pattern)
        rank = 7 if pattern in deficient else 8
        need(row["outside_count"] == len(outside) and row["rank"] == rank,
             "receipt hyperplane count/rank")
        minor_rows, columns = row["minor_rows"], row["minor_columns"]
        need(len(minor_rows) == rank and len(set(minor_rows)) == rank
             and set(minor_rows) <= set(outside), "minor rows in hyperplane complement")
        need(len(columns) == rank and len(set(columns)) == rank
             and set(columns) <= set(range(8)), "minor columns")
        determinant = subset_determinant([[hamming[i][j] for j in columns]
                                          for i in minor_rows])
        need(determinant != 0 and determinant == row["minor_determinant"],
             "exact minor determinant")
        if rank == 7:
            coordinate = row["normal_coordinate"]
            need(type(coordinate) is int and 0 <= coordinate < 8
                 and frame[coordinate] == deficient[pattern], "exceptional exact normal")
            support = [i for i in live if hamming[i][coordinate] != 0]
            need(row["support"] == support, "exceptional support")
            label_rank = binary_rank([{j for j in range(9) if labels[i] >> j & 1}
                                      for i in support])
            need(label_rank == row["support_label_rank"] == 8, "exceptional label rank")
            exceptional.append(functional)
            exceptional_supports[functional] = {source_to_port[i] for i in support}
    need(seen_patterns == expected_patterns, "complete receipt support coverage")
    need(finite["exceptional_functionals"] == exceptional, "exceptional functional order")
    rows = pairing_rows(ports)
    ranks = [[binary_rank([rows[i] & exceptional_supports[right]
                           for i in exceptional_supports[left]])
              for right in exceptional] for left in exceptional]
    need(ranks == finite["exceptional_pairing_ranks"]
         and all(rank == 8 for row in ranks for rank in row), "receipt exceptional pairings")
    need(finite["hyperplane_count"] == finite["checked_integer_minors"] == 511,
         "receipt finite coverage counts")
    need(finite["exceptional_pairings_checked"] == 64
         and finite["complement_rank_histogram"] == {"7": 8, "8": 503}, "receipt rank summary")
    return {"hyperplanes": 511, "exact_subset_determinants": 511, "pairings": 64}


def receipt_mutation_controls(receipt, independent):
    changes = [
        ("missing functional", lambda value: value["finite_premises"]["hyperplanes"].pop()),
        ("false rational rank", lambda value: value["finite_premises"]["hyperplanes"][0].__setitem__("rank", 8)),
        ("false minor determinant", lambda value: value["finite_premises"]["hyperplanes"][0].__setitem__("minor_determinant", 1)),
        ("false exceptional pairing", lambda value: value["finite_premises"]["exceptional_pairing_ranks"][0].__setitem__(0, 7)),
    ]
    for name, mutate in changes:
        changed = copy.deepcopy(receipt)
        mutate(changed)
        try:
            bind_receipt(changed, independent)
        except ValueError:
            continue
        raise ValueError("accepted receipt mutation: " + name)
    return [name for name, _ in changes]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print the independent receipt")
    parser.add_argument("--result", type=Path, default=Path(__file__).with_name("RESULT.json"),
                        help="primary finite receipt to independently bind")
    args = parser.parse_args()
    result = audit_geometry()
    result["mutation_controls"] = mutation_controls()
    receipt = json.loads(args.result.read_text(encoding="utf-8"))
    result["receipt_binding"] = bind_receipt(receipt, result)
    result["mutation_controls"] += receipt_mutation_controls(receipt, result)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PASS_P112_BATCH_CENTRE_FLOOR_INDEPENDENT "
              "functionals=511 rank7=8 rank8=503 support_pairs=64 "
              "exact_minors=511 method=mod101-plus-integer-normals controls=7")


if __name__ == "__main__":
    main()
