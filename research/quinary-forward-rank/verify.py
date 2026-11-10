"""Finite conformance for an implementation change, not a new repair theorem."""

import hashlib
import itertools
import json

from adapter import (
    INPUTS,
    PACKAGE,
    SOURCE,
    authenticate,
    check_digest,
    forward_rank,
    primary_text,
    require,
    run_complete,
)


def rank_two_rows(matrix):
    if not any(x % 5 for row in matrix for x in row):
        return 0
    for j, k in itertools.combinations(range(3), 2):
        if (matrix[0][j] * matrix[1][k] - matrix[0][k] * matrix[1][j]) % 5:
            return 2
    return 1


def exhaustive_small():
    histogram = [0, 0, 0]
    for entries in itertools.product(range(5), repeat=6):
        matrix = [list(entries[:3]), list(entries[3:])]
        before = [row[:] for row in matrix]
        expected = rank_two_rows(matrix)
        require(forward_rank(matrix) == expected, "minor oracle disagreement")
        require(matrix == before, "small input changed")
        histogram[expected] += 1
    require(sum(histogram) == 5**6, "exhaustive domain")
    return histogram


def edge_cases(payloads):
    namespace = {"__name__": "source_fixture", "__file__": str(PACKAGE / "unused")}
    exec(compile(primary_text(payloads, "original"), "frozen-primary", "exec"), namespace)
    matrices = [[], [[]], [[], []], [[0]], [[-5]], [[-1]], [[0, 1], [1, 0]]]
    for rows in range(1, 10):
        for cols in range(1, 10):
            matrices.append([[(i * j + i + 3 * j) % 7 - 3 for j in range(cols)]
                             for i in range(rows)])
    for matrix in matrices:
        require(forward_rank(matrix) == namespace["rank"](matrix), "boundary rank")
    require(forward_rank([[int(i == j) for j in range(256)] for i in range(256)])
            == 256, "dimension limit")
    return len(matrices) + 1


def controls(payloads):
    rejected = []
    bad_inputs = (
        ("field", [[1]], 3),
        ("field type", [[1]], True),
        ("matrix type", None, 5),
        ("row type", [1], 5),
        ("ragged", [[1], []], 5),
        ("entry type", [[True]], 5),
        ("entry size", [[2**65]], 5),
        ("row limit", [[0]] * 257, 5),
        ("column limit", [[0] * 257], 5),
    )
    for name, matrix, p in bad_inputs:
        try:
            forward_rank(matrix, p)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("invalid matrix accepted: " + name)
    try:
        check_digest(payloads[INPUTS[0]] + b"\n", hashlib.sha256(payloads[INPUTS[0]]).hexdigest())
    except ValueError:
        rejected.append("source mutation")
    else:
        raise ValueError("changed source accepted")
    changed = dict(payloads)
    changed[SOURCE + "verify.py"] = b"def other(): pass\n"
    try:
        primary_text(changed, "adapted")
    except ValueError:
        rejected.append("definition anchor")
    else:
        raise ValueError("missing definition accepted")
    require(forward_rank([[0, 1], [1, 0]]) == 2, "row swap required")
    require(forward_rank([[1, 1], [2, 2]]) == 1, "dependent row required")
    return rejected


def main():
    payloads = authenticate()
    original, empty = run_complete("original")
    adapted, records = run_complete("adapted", observe=True)
    require(not empty and len(records) == 28, "complete reached rank inventory")
    require(original == adapted, "complete scientific output changed")
    require(original.splitlines() == ["PASS_QUINARY_RESONANT_DISJOINTNESS_REPAIR",
            "PASS_INDEPENDENT_QUINARY_TENSOR_AND_KERNEL"], "complete markers")
    histogram = exhaustive_small()
    boundaries = edge_cases(payloads)
    rejected = controls(payloads)
    files = sorted(p for p in PACKAGE.iterdir() if p.is_file())
    require(len(files) == 7, "package inventory")
    receipt = {
        "claim_type": "implementation equivalence and measured runtime improvement",
        "reached_rank_calls": records,
        "small_matrix_rank_histogram": histogram,
        "boundary_cases": boundaries,
        "rejected_controls": rejected,
        "complete_output_sha256": hashlib.sha256(original.encode()).hexdigest(),
        "source_sha256": {p: hashlib.sha256(b).hexdigest() for p, b in payloads.items()},
        "package_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
    }
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_QUINARY_FORWARD_RANK")


if __name__ == "__main__":
    main()
