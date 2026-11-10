# SPDX-License-Identifier: Apache-2.0
"""Bounded independent cofactor oracle and generated hash-bound evidence."""
import hashlib
import itertools
import json
from dataclasses import replace
from fractions import Fraction
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from cache import exact_div, initialize, require  # noqa: E402


def literal_determinant(matrix):
    """Leibniz formula, independent of both initialization and slide algorithms."""
    size = len(matrix)
    require(size <= 5, "bounded permutation oracle")
    result = 0
    for order in itertools.permutations(range(size)):
        inversions = sum(order[i] > order[j] for i in range(size) for j in range(i + 1, size))
        term = (-1) ** inversions
        for i in range(size):
            term *= matrix[i][order[i]]
        result += term
    return result


def literal_adjugate(matrix):
    size = len(matrix)
    return tuple(tuple((-1) ** (i + j) * literal_determinant(
        [[matrix[r][c] for c in range(size) if c != i]
         for r in range(size) if r != j]) for j in range(size)) for i in range(size))


def check_state(state, original):
    labels = state.labels
    matrix = tuple(tuple(state.source[i][j] for j in labels) for i in labels)
    require(state.determinant == literal_determinant(matrix), "oracle determinant")
    require(state.adjugate == literal_adjugate(matrix), "oracle adjugate")
    require(type(state.determinant) is int
            and all(type(x) is int for row in state.adjugate for x in row), "integer state")
    actual = state.materialize()
    principal = tuple(tuple(Fraction(original[i][j]) for j in labels) for i in labels)
    determinant = literal_determinant(principal)
    adjugate = literal_adjugate(principal)
    expected = tuple(tuple(x / determinant for x in row) for row in adjugate)
    require(actual == expected, "rational-source inverse orientation")


def initialization_census():
    nonsingular = singular = 0
    for entries in itertools.product(range(-2, 3), repeat=4):
        matrix = (entries[:2], entries[2:])
        if literal_determinant(matrix):
            check_state(initialize(matrix, (0, 1)), matrix)
            nonsingular += 1
        else:
            expect_rejection(lambda: initialize(matrix, (0, 1)))
            singular += 1
    return {"nonsingular": nonsingular, "singular_rejected": singular}


def exhaustive_integer():
    initial_states = slides = 0
    positions = tuple((i, j) for i in range(3) for j in range(3) if i != j)
    for values in itertools.product((-1, 0, 1), repeat=6):
        source = [[0] * 3 for _ in range(3)]
        for i in range(3):
            source[i][i] = 4 + i
        for (i, j), value in zip(positions, values):
            source[i][j] = value
        for width in range(1, 4):
            for labels in itertools.permutations(range(3), width):
                state = initialize(source, labels)
                check_state(state, source)
                initial_states += 1
                for incoming in range(3):
                    if incoming not in labels[1:]:
                        following = state.slide(incoming)
                        check_state(following, source)
                        require(following.source is state.source, "fixed global integer source")
                        require(state.labels == labels, "immutable predecessor state")
                        slides += 1
    return {"sources": 3 ** 6, "initial_states": initial_states, "slides": slides}


def rational_streams():
    slides = 0
    for sign_pattern in range(2):
        source = [[Fraction(20 + i) if i == j else Fraction((3*i + 5*j) % 7 - 3, i+j+2)
                   for j in range(5)] for i in range(5)]
        if sign_pattern:
            source = [[(-1) ** i * x for x in row] for i, row in enumerate(source)]
        for width in range(1, 6):
            state = initialize(source, tuple(range(width)))
            check_state(state, source)
            for step in range(48):
                available = tuple(i for i in range(5) if i not in state.labels[1:])
                state = state.slide(available[(7 * step + width) % len(available)])
                check_state(state, source)
                slides += 1
    return {"sources": 2, "initial_states": 10, "slides": slides,
            "maximum_stream_length": 48}


def diagonal_boundaries():
    source = [[(i + 1) * (-1) ** i if i == j else 0 for j in range(17)] for i in range(17)]
    state = initialize(source, tuple(range(16)))
    for step in range(65):
        if step:
            incoming = next(i for i in range(17) if i not in state.labels)
            state = state.slide(incoming)
        determinant = 1
        for label in state.labels:
            determinant *= source[label][label]
        require(state.determinant == determinant, "width-sixteen diagonal determinant")
        require(state.materialize() == tuple(tuple(
            Fraction(1, source[label][label]) if i == j else Fraction(0)
            for j in range(16)) for i, label in enumerate(state.labels)), "wide diagonal inverse")
    max_source = [[int(i == j) for j in range(32)] for i in range(32)]
    require(initialize(max_source, (31,)).slide(0).materialize() == ((Fraction(1),),),
            "maximum source dimension")
    return {"width": 16, "slides": 64, "source_limit": 32}


def expect_rejection(action):
    try:
        action()
    except ValueError:
        return
    raise ValueError("expected rejection did not occur")


def controls():
    invalid = [([], (0,)), ([[1, 0], [0]], (0,)), ([[True]], (0,)),
               ([[1.0]], (0,)), ([[1 << 257]], (0,)), ([[1]], (True,)),
               ([[1]], (1,)), ([[1, 0], [0, 1]], (0, 0)),
               ([[1, 1], [1, 1]], (0, 1)),
               ([[int(i == j) for j in range(33)] for i in range(33)], (0,)),
               ([[int(i == j) for j in range(17)] for i in range(17)], tuple(range(17)))]
    for matrix, labels in invalid:
        expect_rejection(lambda: initialize(matrix, labels))
    source = [[4, -1, 2], [1, 5, -2], [0, 1, 3]]
    state = initialize(source, (0, 1))
    for incoming in (True, -1, 3, 1):
        expect_rejection(lambda: state.slide(incoming))
    expect_rejection(lambda: exact_div(1, 2))
    expect_rejection(lambda: exact_div(1, 0))
    expect_rejection(lambda: initialize([[0, 1], [1, 0]], (0, 1)).slide(0))
    bad = [[1, 0, 0], [0, 1, 1], [0, 1, 1]]
    expect_rejection(lambda: initialize(bad, (0, 1)).slide(2))
    following = state.slide(2)
    for corrupted in (replace(following, determinant=-following.determinant),
                      replace(following, adjugate=((3, -2), (-1, 5))),
                      replace(following, row_scales=(1, 2, 1)),
                      replace(following, labels=(2, 1))):
        expect_rejection(lambda: check_state(corrupted, source))
    require(state.labels == (0, 1) and state.determinant == 21, "failure leaves state intact")
    # A singular first scalar pivot is legal when the retained block is invertible.
    pivoted = [[0, 1], [1, 1]]
    check_state(initialize(pivoted, (0, 1)).slide(0), pivoted)
    return {"invalid_inputs": len(invalid) + 4, "division_or_singular_controls": 4,
            "corrupted_state_controls": 4, "row_pivot_positive_control": 1}


def source_hashes():
    names = ("cache.py", "verify.py", "README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json")
    hashes = {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest() for name in names}
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    root = PACKAGE.parents[1]
    require(len(manifest["files"]) <= 8, "bounded source manifest")
    inputs = {}
    for entry in manifest["files"]:
        if entry["usage"] == "input":
            actual = hashlib.sha256((root / entry["path"]).read_bytes()).hexdigest()
            require(actual == entry["sha256"], "changed predecessor contract bytes")
            inputs[entry["path"]] = actual
    return {"package": hashes, "contract_inputs": inputs}


def main():
    hashes_before = source_hashes()
    report = {"status": "PASS_SHARED_DENOMINATOR_WINDOW_CACHE",
              "claim_type": "scoped written construction with finite exact corroboration",
              "initialization_census": initialization_census(),
              "integer_census": exhaustive_integer(), "rational_streams": rational_streams(),
              "boundary_cases": diagonal_boundaries(), "controls": controls()}
    require(source_hashes() == hashes_before, "source stability during verification")
    report["sha256"] = hashes_before
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
