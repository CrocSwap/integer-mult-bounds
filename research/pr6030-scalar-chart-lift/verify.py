#!/usr/bin/env python3
"""Bind the scalar half of native_all_columns to the selected PR6030 word.

The all-width identities are proved in PROOF.md. This program checks the
common-chart and empty-COPY hypotheses on that word, and checks the tensor
arithmetic on explicit charts. Finite widths are controls, not a substitute
for the induction.
"""

from fractions import Fraction
from hashlib import sha256
import gzip
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORD = ROOT / "research/p104-helper470-twin-rung-removal/WORD.json.gz"
WORD_SHA256 = "7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f"
# Published #5599 census in research/native-scalar-chart-lift/PROOF.md.
# A swap back to that word must not satisfy this package.
OLDER_SELECTED_COUNTS = {"ADD": 21247, "SCALE": 757, "COPY": 8, "MOVE": 3447}
Q = Fraction


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load_word(path):
    payload = path.read_bytes()
    need(sha256(payload).hexdigest() == WORD_SHA256, "Selected word SHA256")
    word = json.loads(gzip.decompress(payload).decode("utf-8"))
    need(word.get("schema") == "p104-accumulated-block-composition/2", "Word schema")
    public = word.get("public")
    owned = word.get("owned_fields")
    need(isinstance(public, int) and isinstance(owned, int) and owned > 0, "Inventory")
    need(len(word["initial"]) == public == len(word["final"]), "Boundary length")
    need(isinstance(word.get("frames"), list) and word["frames"], "Frames")
    need(isinstance(word.get("program"), list), "Program")
    return word


def frame_index(value, frame_count, why):
    need(isinstance(value, int) and 0 <= value < frame_count, why)
    return value


def walk(program, initial, frame_count, owned_slots=0):
    """Accept scalar events only on one common current frame.

    COPY is accepted only into an owned register whose logical row is empty.
    Public rows start nonempty. An owned row is empty after INIT or CLEAR
    and becomes nonempty when a nonempty source is copied or added into it.
    """
    current = list(initial) + [None] * owned_slots
    empty = [False] * len(initial) + [False] * owned_slots
    owned = set()
    counts = {op: 0 for op in ("ADD", "SCALE", "COPY", "MOVE", "INIT", "CLEAR")}
    peak = 0
    initialized = set()
    for event in program:
        need(isinstance(event, list) and event, "Event shape")
        op = event[0]
        need(op in counts, "Unexpected opcode " + str(op))
        role = event[1]
        need(isinstance(role, int) and 0 <= role < len(current), "Role index")
        if op == "MOVE":
            need(len(event) == 5 and isinstance(event[4], bool), "MOVE shape")
            source = frame_index(event[2], frame_count, "MOVE source chart")
            destination = frame_index(event[3], frame_count, "MOVE destination chart")
            need(current[role] == source, "MOVE leaves the recorded chart")
            need((role in owned) == event[4], "MOVE ownership flag")
            current[role] = destination
        elif op == "INIT":
            need(len(event) == 3, "INIT shape")
            need(role >= len(initial) and role not in owned, "Owned init")
            owned.add(role)
            initialized.add(role)
            peak = max(peak, len(owned))
            empty[role] = True
            current[role] = frame_index(event[2], frame_count, "INIT chart")
        elif op == "CLEAR":
            need(len(event) == 3, "CLEAR shape")
            need(role in owned, "CLEAR of an unowned register")
            need(current[role] == frame_index(event[2], frame_count, "CLEAR chart"),
                 "CLEAR leaves the recorded chart")
            owned.discard(role)
            empty[role] = True
            current[role] = None
        else:
            need(len(event) == (4 if op == "SCALE" else 5), op + " shape")
            coefficient = Q(event[-2])
            frame = frame_index(event[-1], frame_count, "Scalar frame")
            need(coefficient != 0, "Zero scalar coefficient")
            need(current[role] == frame, "Scalar destination chart")
            if op == "SCALE":
                pass
            else:
                source = event[2]
                need(isinstance(source, int) and source != role, "Scalar source role")
                need(0 <= source < len(current), "Scalar source index")
                need(current[source] == frame, "Common scalar chart")
                if op == "COPY":
                    need(role in owned and empty[role], "COPY into a nonempty row")
                    empty[role] = empty[source]
                else:
                    need(op == "ADD", "Opcode")
                    empty[role] = empty[role] and empty[source]
        counts[op] += 1
    need(not owned, "Owned register left open")
    return counts, peak, initialized, current


def finish_walk(word):
    counts, peak, initialized, current = walk(
        word["program"], word["initial"], len(word["frames"]), word["owned_fields"])
    public = word["public"]
    need(current[:public] == word["final"], "Public charts miss the published final boundary")
    need(initialized == set(range(public, public + word["owned_fields"])),
         "Owned inventory is not exactly the initialized registers")
    return counts, peak


def mat_id(size):
    return [[Q(i == j) for j in range(size)] for i in range(size)]


def mat_mul(left, right):
    rows, mid, cols = len(left), len(right), len(right[0])
    out = [[Q(0) for _ in range(cols)] for _ in range(rows)]
    for i in range(rows):
        for k in range(mid):
            if left[i][k] == 0:
                continue
            for j in range(cols):
                out[i][j] += left[i][k] * right[k][j]
    return out


def mat_vec(matrix, vector):
    return [sum(matrix[i][j] * vector[j] for j in range(len(vector))) for i in range(len(matrix))]


def kron(left, right):
    n, m = len(left), len(left[0])
    p, q = len(right), len(right[0])
    out = [[Q(0) for _ in range(m * q)] for _ in range(n * p)]
    for i in range(n):
        for j in range(m):
            for k in range(p):
                for ell in range(q):
                    out[i * p + k][j * q + ell] = left[i][j] * right[k][ell]
    return out


def tensor_pow(matrix, width):
    out = [[Q(1)]]
    for _ in range(width):
        out = kron(out, matrix)
    return out


def inv2(matrix):
    determinant = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    need(determinant != 0, "Singular specimen chart")
    return [[matrix[1][1] / determinant, -matrix[0][1] / determinant],
            [-matrix[1][0] / determinant, matrix[0][0] / determinant]]


def add_vec(left, right):
    return [a + b for a, b in zip(left, right)]


def scale_vec(coefficient, vector):
    return [coefficient * entry for entry in vector]


def common_pullback(base, width, coefficient):
    chart = tensor_pow(base, width)
    inverse = tensor_pow(inv2(base), width)
    size = len(chart)
    vector_u = [Q(index + 1) for index in range(size)]
    vector_v = [Q(1 if index % 2 == 0 else -3) for index in range(size)]
    physical = add_vec(mat_vec(chart, vector_u), scale_vec(coefficient, mat_vec(chart, vector_v)))
    logical = mat_vec(inverse, physical)
    replay = add_vec(vector_u, scale_vec(coefficient, vector_v))
    scaled = mat_vec(chart, scale_vec(coefficient, vector_u))
    return (logical == replay
            and scaled == scale_vec(coefficient, mat_vec(chart, vector_u))
            and mat_mul(inverse, chart) == mat_id(size))


def mixed_product_step(base):
    inverse = inv2(base)
    left = kron(mat_mul(inverse, base), mat_mul(inverse, base))
    right = mat_mul(kron(inverse, inverse), kron(base, base))
    return mat_mul(inverse, base) == mat_id(2) and left == right == mat_id(4)


def cross_matches_replay(source_base, width, coefficient):
    size = 2 ** width
    destination = mat_id(size)
    source = tensor_pow(source_base, width)
    vector_u = [Q(2) for _ in range(size)]
    vector_v = [Q(1)] + [Q(0)] * (size - 1)
    physical = add_vec(mat_vec(destination, vector_u),
                       scale_vec(coefficient, mat_vec(source, vector_v)))
    replay = add_vec(vector_u, scale_vec(coefficient, vector_v))
    return physical == replay


def check_specimens():
    coefficient = Q(-1, 2)
    pauli_x = [[Q(0), Q(1)], [Q(1), Q(0)]]
    shear = [[Q(1), Q(1)], [Q(0), Q(1)]]
    generic = [[Q(2), Q(3)], [Q(5), Q(7)]]
    phase = [[Q(-1), Q(0)], [Q(0), Q(-1)]]
    for base in (pauli_x, shear, generic):
        need(mixed_product_step(base), "Tensor induction step failed")
        for width in (1, 2, 3):
            need(common_pullback(base, width, coefficient),
                 "Common-chart pullback failed at width " + str(width))
    phase_vs_replay = {width: cross_matches_replay(phase, width, coefficient) for width in (1, 2, 3)}
    need(phase_vs_replay == {1: False, 2: True, 3: False}, "Phase-chart trap did not separate widths")
    pauli_vs_replay = {width: cross_matches_replay(pauli_x, width, coefficient) for width in (1, 2, 3)}
    need(pauli_vs_replay == {1: False, 2: False, 3: False}, "Pauli cross-chart should miss the replay")
    need(kron(pauli_x, mat_id(2)) != kron(pauli_x, pauli_x), "Width-2 Pauli power collapsed")
    return phase_vs_replay


def expect_error(program, initial, frames, owned_slots, message):
    try:
        walk(program, initial, frames, owned_slots)
    except ValueError as exc:
        need(str(exc) == message, "Unexpected rejection: " + str(exc))
    else:
        raise ValueError("Accepted an event that must fail: " + message)


def check_walker_controls():
    expect_error([["ADD", 0, 1, "1", 4]], [4, 5], 6, 0, "Common scalar chart")
    expect_error([["MOVE", 0, 4, 5, False], ["ADD", 0, 1, "1", 4]], [4, 5], 6, 0,
                 "Scalar destination chart")
    expect_error([["SCALE", 0, "0", 4]], [4], 6, 0, "Zero scalar coefficient")
    owned_copy = [
        ["INIT", 1, 4],
        ["ADD", 1, 0, "1", 4],
        ["COPY", 1, 0, "1", 4],
    ]
    expect_error(owned_copy, [4], 6, 1, "COPY into a nonempty row")
    empty_copy = [["INIT", 1, 4], ["COPY", 1, 0, "1/2", 4], ["CLEAR", 1, 4]]
    counts, peak = walk(empty_copy, [4], 6, 1)[:2]
    need(counts["COPY"] == 1 and peak == 1, "Empty owned COPY")
    return True


def check_word_mutation(word):
    mutated = json.loads(json.dumps(word["program"]))
    index = next(i for i, event in enumerate(mutated) if event[0] == "ADD")
    mutated[index][-1] = mutated[index][-1] + 1
    try:
        walk(mutated, word["initial"], len(word["frames"]), word["owned_fields"])
    except ValueError:
        return True
    raise ValueError("Retagging the first ADD was accepted")


def main():
    word = load_word(WORD)
    counts, peak = finish_walk(word)
    need(counts["ADD"] == 18404 and counts["SCALE"] == 861 and counts["COPY"] == 23, "Scalar census")
    need(counts["MOVE"] == 3453 and counts["INIT"] == 31 and counts["CLEAR"] == 31, "State-machine census")
    need(sum(counts.values()) == 22803, "Event total")
    need(peak == 13 and word["owned_fields"] == 29 and word["public"] == 770, "Owned peak")
    need(any(counts[op] != OLDER_SELECTED_COUNTS[op] for op in OLDER_SELECTED_COUNTS),
         "Census collapsed to the older #5599 word")
    phase = check_specimens()
    need(phase == {1: False, 2: True, 3: False}, "Specimen phase trap")
    need(check_walker_controls(), "Walker controls")
    need(check_word_mutation(word), "Word mutation control")
    print(
        "PASS_PR6030_SCALAR_CHART_LIFT"
        " adds=%d scales=%d copies=%d moves=%d inits=%d clears=%d"
        " common_chart_violations=0 copy_into_empty=%d peak_owned=%d"
        " owned_fields=%d public=%d events=%d"
        " phase_width2_only=true no_new_kappa=true"
        % (counts["ADD"], counts["SCALE"], counts["COPY"], counts["MOVE"],
           counts["INIT"], counts["CLEAR"], counts["COPY"], peak,
           word["owned_fields"], word["public"], sum(counts.values()))
    )


if __name__ == "__main__":
    main()
