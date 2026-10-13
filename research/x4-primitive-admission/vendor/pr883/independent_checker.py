#!/usr/bin/env python3
"""Independent, standard-library-only exact check of the isolated X4 pair map.

No imports from the integration verifier, no scratch register, no permutation,
and no weighted-cost or whole-circuit optimality claim. Every alphabet letter
costs one. Run from any directory; stdout is deterministic JSON.
"""

from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from pathlib import Path
import argparse
import gzip
import json
import tarfile

IDENTITY = (Q(1), Q(0), Q(0), Q(1))
FORWARD = (Q(-1, 2), Q(1, 2), Q(1, 2), Q(1, 2))
BACKWARD = (Q(-1), Q(1), Q(1), Q(1))

# (kind, destination, source-or-None, exact multiplier)
ALPHABET = tuple(
    [("ADD", i, 1 - i, Q(s)) for i in (0, 1) for s in (-1, 1)]
    + [(name, i, None, scalar)
       for name, scalar in (("NEG", Q(-1)), ("HALF", Q(1, 2)), ("DOUBLE", Q(2)))
       for i in (0, 1)]
)
FORWARD_WORD = (
    ("ADD", 0, 1, Q(-1)), ("NEG", 0, None, Q(-1)),
    ("HALF", 0, None, Q(1, 2)), ("ADD", 1, 0, Q(-1)),
)
# This word is the letterwise inverse transpose of FORWARD_WORD. The
# chronological order stays the same under the inverse-transpose operation.
BACKWARD_WORD = (
    ("ADD", 1, 0, Q(1)), ("NEG", 0, None, Q(-1)),
    ("DOUBLE", 0, None, Q(2)), ("ADD", 0, 1, Q(1)),
)
ORIGINAL_FORWARD = (
    ("SCALE", 0, None, Q(-1, 2)), ("ADD", 0, 1, Q(1, 2)),
    ("ADD", 1, 0, Q(-1)),
)
ORIGINAL_BACKWARD = (
    ("SCALE", 0, None, Q(-2)), ("ADD", 1, 0, Q(-1, 2)),
    ("ADD", 0, 1, Q(1)),
)
ARCHIVE_SHA256 = "70dfdfcf2ff95352c6020ee9dfca6dca9032b33c10daed3f3dc574c014f4e2cb"
MEMBER_HASHES = {
    "native/local/CANONICAL-WORD.json.gz":
        "f1c2ede9276d4447c5857d0e9d32adb52f987b8adb643b45bde2c172d88c6ee9",
    "native/local/LOCAL-PROGRAMS.json.gz":
        "ce194f8465079db575a9ce17ccee1396fa4de0210e2817da2525f95f4f93ebde",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def step(matrix, instruction):
    kind, destination, source, scalar = instruction
    result = list(matrix)
    for column in range(2):
        at = 2 * destination + column
        result[at] = (matrix[at] + scalar * matrix[2 * source + column]
                      if kind == "ADD" else scalar * matrix[at])
    return tuple(result)


def trace(word):
    matrices = [IDENTITY]
    for instruction in word:
        matrices.append(step(matrices[-1], instruction))
    return matrices


def inverse_transpose(matrix):
    a, b, c, d = matrix
    determinant = a * d - b * c
    require(determinant != 0, "singular target")
    return (d / determinant, -c / determinant,
            -b / determinant, a / determinant)


def metrics(matrices):
    return {
        "peak_row_l1": str(max(max(abs(m[0]) + abs(m[1]),
                                   abs(m[2]) + abs(m[3])) for m in matrices)),
        "maximum_reduced_denominator": max(q.denominator for m in matrices for q in m),
        "maximum_absolute_reduced_numerator": max(abs(q.numerator) for m in matrices for q in m),
        "prefix_matrices": [[str(q) for q in m] for m in matrices],
    }


def breadth_first():
    # Deduplication is sound because every continuation depends only on the
    # current 2x2 matrix. Retain first-seen distance, not a coefficient cutoff.
    distances = {IDENTITY: 0}
    frontier = {IDENTITY}
    sizes = [1]
    for depth in range(1, 5):
        following = set()
        for matrix in frontier:
            for letter in ALPHABET:
                candidate = step(matrix, letter)
                if candidate not in distances:
                    following.add(candidate)
        distances.update({matrix: depth for matrix in following})
        sizes.append(len(following))
        frontier = following
    require(sizes == [1, 10, 69, 370, 1646], "BFS frontier changed")
    require(distances[FORWARD] == distances[BACKWARD] == 4, "minimum changed")
    gatewise = {}
    for name, word in (("forward", ORIGINAL_FORWARD), ("backward", ORIGINAL_BACKWARD)):
        lengths = [distances[step(IDENTITY, letter)] for letter in word]
        require(lengths == [2, 3, 1], "gatewise primitive minima changed")
        gatewise[name] = lengths
    return {"frontier_sizes": sizes, "original_gatewise_minimum_lengths": gatewise}


def exhaustive_words():
    # A separate full-word enumeration cross-checks the state-based BFS and
    # examines *every* shortest realization's intermediate guard.
    counts = {"forward": 0, "backward": 0}
    targets = {FORWARD: "forward", BACKWARD: "backward"}
    examined = []
    for depth in range(5):
        total = 0
        for word in product(ALPHABET, repeat=depth):
            total += 1
            matrices = trace(word)
            name = targets.get(matrices[-1])
            if name:
                require(depth == 4, "a circuit shorter than four exists")
                counts[name] += 1
                measured = metrics(matrices)
                require(measured["peak_row_l1"] == "2", "optimal guard changed")
                require(measured["maximum_reduced_denominator"] ==
                        (2 if name == "forward" else 1), "optimal fraction guard changed")
        examined.append(total)
    require(counts == {"forward": 8, "backward": 8}, "shortest word count changed")
    return {"words_examined_by_length": examined, "shortest_word_counts": counts}


def check_archive(path):
    require(sha256(path.read_bytes()).hexdigest() == ARCHIVE_SHA256,
            "archive differs from pinned PR799 input")
    objects = {}
    with tarfile.open(path, "r:gz") as archive:
        for name, expected_hash in MEMBER_HASHES.items():
            member = archive.extractfile(name)
            require(member is not None, "missing archive member")
            raw = member.read()
            require(sha256(raw).hexdigest() == expected_hash, "archive member hash mismatch")
            objects[name] = json.loads(gzip.decompress(raw))
    canonical = objects["native/local/CANONICAL-WORD.json.gz"]
    programs = objects["native/local/LOCAL-PROGRAMS.json.gz"]
    precondition = canonical["precondition"]
    require(len(precondition) == 168, "precondition is not 56 triples")
    pairs = []
    expected_forward = [["phase", "zero_frame_precondition"]]
    expected_backward = [["phase", "zero_frame_precondition"]]
    for offset in range(0, len(precondition), 3):
        block = precondition[offset:offset + 3]
        x, y = block[0][1], block[1][2]
        require(block == [["scale", x, -1, 2, 0],
                          ["add", x, y, 1, 2, 0],
                          ["add", y, x, -1, 1, 0]], "unexpected pair shape")
        pairs.append([x, y])
        expected_forward.extend([
            ["scalar", ["scale", ["L", x], -1, 2], 0],
            ["scalar", ["add", ["L", x], ["L", y], 1, 2], 0],
            ["scalar", ["add", ["L", y], ["L", x], -1, 1], 0],
        ])
        expected_backward.extend([
            ["scalar", ["scale", ["L", x], 2, -1], 0],
            ["scalar", ["add", ["L", y], ["L", x], -1, 2], 0],
            ["scalar", ["add", ["L", x], ["L", y], 1, 1], 0],
        ])
    require(len({register for pair in pairs for register in pair}) == 112,
            "pairs overlap")
    for direction, expected in (("forward", expected_forward), ("backward", expected_backward)):
        require(programs[direction][:169] == expected, direction + " archived prefix differs")
    return {"archive_sha256": ARCHIVE_SHA256, "member_sha256": MEMBER_HASHES,
            "pair_count": len(pairs), "distinct_registers": 112, "pairs": pairs}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=Path(__file__).resolve().parents[1]
                        / "community-frontier799-audit" / "integrated799-replay.tar.gz")
    args = parser.parse_args()
    require(trace(ORIGINAL_FORWARD)[-1] == FORWARD, "original forward algebra fails")
    require(trace(FORWARD_WORD)[-1] == FORWARD, "candidate forward algebra fails")
    require(trace(ORIGINAL_BACKWARD)[-1] == BACKWARD, "original backward algebra fails")
    require(trace(BACKWARD_WORD)[-1] == BACKWARD, "candidate backward algebra fails")
    require(inverse_transpose(FORWARD) == BACKWARD, "duality identity fails")
    for f, b in zip(FORWARD_WORD, BACKWARD_WORD):
        require(inverse_transpose(step(IDENTITY, f)) == step(IDENTITY, b),
                "letterwise inverse-transpose mismatch")
    # Negative controls: deletion and a sign mutation must be detected by the
    # matrix oracle. A false prefix bound of one must also be detected.
    no_neg = FORWARD_WORD[:1] + FORWARD_WORD[2:]
    wrong_sign = (("ADD", 0, 1, Q(1)),) + FORWARD_WORD[1:]
    require(trace(no_neg)[-1] != FORWARD, "negative control: omitted NEG accepted")
    require(trace(wrong_sign)[-1] != FORWARD, "negative control: wrong sign accepted")
    require(metrics(trace(FORWARD_WORD))["peak_row_l1"] != "1",
            "negative control: false norm guard accepted")
    result = {
        "status": "PASS",
        "scope": "isolated two-register pair; ADD(+/-1), NEG, HALF, DOUBLE; unit cost; no scratch or swap",
        "archive": check_archive(args.archive),
        "minimum_primitive_counts": {"forward": 4, "inverse_transpose_backward": 4},
        "bfs": breadth_first(),
        "exhaustive": exhaustive_words(),
        "original_rational_forward": metrics(trace(ORIGINAL_FORWARD)),
        "candidate_forward": metrics(trace(FORWARD_WORD)),
        "original_rational_backward": metrics(trace(ORIGINAL_BACKWARD)),
        "candidate_backward": metrics(trace(BACKWARD_WORD)),
        "negative_controls_rejected": ["omitted NEG", "wrong first ADD sign", "false forward row-l1 guard <= 1"],
        "limitation": "No assertion of global-circuit optimality, global guard acceptance, or a new kappa bound.",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
