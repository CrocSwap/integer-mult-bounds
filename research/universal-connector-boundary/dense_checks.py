#!/usr/bin/env python3
"""Independent finite replay with dense F2 maps and arbitrary dirty registers.

For each supplied schedule, the map banks at dimensions 1, 2, and 3 are fixed
by seed 52.  Every initial basis bit and 25 mixed dirty states are replayed.
The expected answer is evaluated from explicit matrix products A_i B_j,
independently of the schedule's intermediate connector states.  Exhaustion
of basis inputs checks each sampled linear transformation exactly; it does
not exhaust every possible matrix bank or prove the full multiplication
theorem.  No construction/generator module is imported.

SPDX-License-Identifier: Apache-2.0
Contributor: Ross, with substantial OpenAI Codex assistance.
"""

from copy import deepcopy
import json
from pathlib import Path
import random
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def matvec(matrix, vector):
    return sum(((row & vector).bit_count() & 1) << i
               for i, row in enumerate(matrix))


def matmul(left, right):
    """Explicit row-by-column product; deliberately separate from matvec."""
    size = len(left)
    result = []
    for i in range(size):
        row = 0
        for j in range(size):
            value = 0
            for k in range(size):
                value ^= ((left[i] >> k) & 1) & ((right[k] >> j) & 1)
            row |= value << j
        result.append(row)
    return tuple(result)


def symmetric(matrix):
    return all(((matrix[i] >> j) & 1) == ((matrix[j] >> i) & 1)
               for i in range(len(matrix)) for j in range(len(matrix)))


def map_bank(source_count, output_count, size):
    rng = random.Random(52 + 1000 * size + 100 * source_count + output_count)
    matrices = [tuple(rng.randrange(1, 1 << size) for _ in range(size))
                for _ in range(source_count + output_count)]
    sources = matrices[:source_count]
    outputs = matrices[source_count:]
    if size > 1:
        require(any(not symmetric(matrix) for matrix in matrices),
                "map bank needs a nonsymmetric matrix witness")
        require(any(matmul(a, b) != matmul(b, a)
                    for a in outputs for b in sources),
                "map bank needs a noncommuting pair witness")
    return sources, outputs


def validate_schedule(schedule):
    sources = schedule["sources"]
    rows = schedule["rows"]
    if not isinstance(sources, int) or sources < 1:
        raise ValueError("sources must be a positive integer")
    if not rows or any(not isinstance(row, int) or not 0 < row < 1 << sources
                       for row in rows):
        raise ValueError("target rows must be nonzero source masks")
    for operation in schedule["word"]:
        if not isinstance(operation, (tuple, list)) or len(operation) != 2:
            raise ValueError("each operation must be a [kind, index] pair")
        kind, index = operation
        bound = sources if kind == "B" else len(rows) if kind == "A" else 0
        if not isinstance(index, int) or not 0 <= index < bound:
            raise ValueError("invalid operation kind or index")


def apply_word(initial, word, source_maps, output_maps):
    source_count = len(source_maps)
    state = list(initial)
    for kind, index in word:
        if kind == "B":
            state[-1] ^= matvec(source_maps[index], state[index])
        else:
            state[source_count + index] ^= matvec(output_maps[index], state[-1])
    return tuple(state)


def target_state(initial, rows, compositions):
    source_count = len(compositions[0])
    state = list(initial)
    for output, row in enumerate(rows):
        for source in range(source_count):
            if row >> source & 1:
                state[source_count + output] ^= matvec(
                    compositions[output][source], initial[source])
    return tuple(state)


def input_states(register_count, size):
    # These vectors form a basis of all source, output, and dirty-connector bits.
    for register in range(register_count):
        for bit in range(size):
            state = [0] * register_count
            state[register] = 1 << bit
            yield tuple(state)
    # One all-one and 24 distinct sampled states.  Source 0, the final output,
    # and the connector are nonzero; remaining registers may be zero.  This
    # avoids repeating the all-one state 25 times at scalar dimension 1.
    all_one = ((1 << size) - 1,) * register_count
    yield all_one
    seen = {all_one}
    rng = random.Random(52 + 1000 * size + register_count)
    count = min(25, ((1 << size) - 1) ** 3 * (1 << size) ** (register_count - 3))
    while len(seen) < count:
        state = [rng.randrange(1 << size) for _ in range(register_count)]
        for register in (0, register_count - 2, register_count - 1):
            state[register] = rng.randrange(1, 1 << size)
        state = tuple(state)
        if state not in seen:
            seen.add(state)
            yield state


def check_schedule(schedule):
    validate_schedule(schedule)
    source_count = schedule["sources"]
    rows = schedule["rows"]
    registers = source_count + len(rows) + 1
    counts = {"map_banks": 0, "basis_states": 0, "mixed_dirty_states": 0,
              "forward_cases": 0, "inverse_cases": 0, "nonsymmetric_banks": 0,
              "noncommuting_banks": 0}
    for size in (1, 2, 3):
        sources, outputs = map_bank(source_count, len(rows), size)
        compositions = [[matmul(a, b) for b in sources] for a in outputs]
        bank_cases = 0
        for initial in input_states(registers, size):
            actual = apply_word(initial, schedule["word"], sources, outputs)
            expected = target_state(initial, rows, compositions)
            require(actual == expected, ("forward", size, initial, actual, expected))
            restored = apply_word(actual, reversed(schedule["word"]), sources, outputs)
            require(restored == initial, ("inverse", size, initial, restored))
            counts["forward_cases"] += 1
            counts["inverse_cases"] += 1
            bank_cases += 1
        counts["basis_states"] += registers * size
        counts["mixed_dirty_states"] += bank_cases - registers * size
        counts["map_banks"] += 1
        if size > 1:
            counts["nonsymmetric_banks"] += 1
            counts["noncommuting_banks"] += 1
    return counts


def check_dense(certificate):
    results = {name: check_schedule(schedule)
               for name, schedule in certificate["schedules"].items()}
    if not results:
        raise ValueError("certificate must contain schedules")

    # Controls start with the four-source schedule and alter distinct contracts.
    original = certificate["schedules"]["four_all"]
    controls = []
    missing_restoration = deepcopy(original)
    final_source = max(i for i, (kind, _) in enumerate(missing_restoration["word"])
                       if kind == "B")
    del missing_restoration["word"][final_source]
    controls.append(("omitted_final_source", missing_restoration))

    wrong_destination = deepcopy(original)
    first_output = next(i for i, (kind, _) in enumerate(wrong_destination["word"])
                        if kind == "A")
    kind, index = wrong_destination["word"][first_output]
    wrong_destination["word"][first_output] = [kind, (index + 1) % len(original["rows"])]
    controls.append(("wrong_output_destination", wrong_destination))

    wrong_target = deepcopy(original)
    wrong_target["rows"][0] ^= 1 << (original["sources"] - 1)
    controls.append(("wrong_target_row", wrong_target))

    detected = []
    for name, broken in controls:
        try:
            check_schedule(broken)
        except ValueError:
            detected.append(name)
        else:
            raise ValueError("negative control was accepted: " + name)
    return {"schedules": results, "negative_controls_detected": detected,
            "seed": 52, "dimensions": [1, 2, 3]}


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("CERTIFICATE.json")
    print(json.dumps(check_dense(json.loads(path.read_text())), indent=2, sort_keys=True))
