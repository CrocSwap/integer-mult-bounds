#!/usr/bin/env python3
"""Exact signed dirty-row pilot and bounded rational adapter census.

Cinna Davis, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
B0 = ((1, -1, 1), (1, 0, -1), (1, -1, 0))
B1 = ((1, 0, 1), (1, 1, -1), (1, 0, 0))
C = ((0, 0, 1), (0, 0, 0), (0, 0, 0))
A0 = ((0, 1, 0), (0, 0, 1), (1, 0, 0))
A1 = ((1, -1, 0), (0, 1, 0), (0, 0, 1))


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def subtract(a, b):
    return [[x - y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def rank(a):
    a = [[Fraction(x) for x in row] for row in a]
    pivot = 0
    for col in range(len(a[0])):
        found = next((i for i in range(pivot, len(a)) if a[i][col]), None)
        if found is None:
            continue
        a[pivot], a[found] = a[found], a[pivot]
        factor = a[pivot][col]
        a[pivot] = [x / factor for x in a[pivot]]
        for i in range(len(a)):
            if i != pivot:
                factor = a[i][col]
                a[i] = [x - factor * y for x, y in zip(a[i], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def append_map(gates, matrix, source, target, sign=1):
    n = len(matrix)
    for i, row in enumerate(matrix):
        for j, coefficient in enumerate(row):
            # Literal repeated signed ADDs, never a free scalar multiply.
            for _ in range(abs(coefficient)):
                gates.append([source * n + j, target * n + i,
                              sign * (1 if coefficient > 0 else -1)])


def programs():
    baseline = []
    for a, b, target in ((A0, B0, 3), (A1, B1, 4)):
        if target == 4:
            append_map(baseline, C, 1, 0)
        append_map(baseline, a, 2, target, -1)
        append_map(baseline, b, 0, 2)
        append_map(baseline, a, 2, target)
        append_map(baseline, b, 0, 2, -1)
    carried = []
    append_map(carried, A0, 2, 3, -1)
    append_map(carried, B0, 0, 2)
    append_map(carried, A0, 2, 3)
    append_map(carried, C, 1, 0)
    repair_start = len(carried)
    # x[1] is borrowed, then returned exactly. u[2] is index 5.
    carried.append([5, 1, 1])
    for z in range(6, 9):
        carried.append([1, z, 1])
    carried.append([5, 1, -1])
    repair_end = len(carried)
    append_map(carried, A1, 2, 4)
    append_map(carried, B1, 0, 2, -1)
    append_map(carried, A1, 2, 4, -1)
    return baseline, carried, [repair_start, repair_end]


def symbolic(gates, width=15):
    state = eye(width)
    for source, target, sign in gates:
        require(source != target and sign in (-1, 1), "invalid elementary gate")
        require(0 <= source < width and 0 <= target < width, "gate outside data tape")
        state[target] = [x + sign * y for x, y in zip(state[target], state[source])]
    return state


def expected_map():
    state = eye(15)
    for target, matrix, source in ((0, C, 1), (3, multiply(A0, B0), 0),
                                   (4, multiply(A1, B1), 0),
                                   (4, multiply(multiply(A1, B1), C), 1)):
        for i in range(3):
            for j in range(3):
                state[3 * target + i][3 * source + j] += matrix[i][j]
    return state


def cost(gates):
    # Rows x,u,z,y0,y1 occupy data cells 0..14. Both heads return to 0.
    data_moves = sum(2 * max(source, target) for source, target, _ in gates)
    count = len(gates)
    record_bits = 2 * (15 - 1).bit_length() + 1
    result = {"signed_adds": count, "data_head_steps": data_moves,
              "data_reads": 2 * count, "data_writes": count,
              "instruction_bits_per_record": record_bits,
              "instruction_reads": record_bits * count,
              "instruction_head_steps": 2 * record_bits * count,
              "decode_dispatch": count}
    result["unit_steps"] = sum(result[k] for k in (
        "signed_adds", "data_head_steps", "data_reads", "data_writes",
        "instruction_reads", "instruction_head_steps", "decode_dispatch"))
    return result


def apply_block(state, matrix, source, target, sign=1):
    n = len(matrix)
    old = [row[:] for row in state[source * n:(source + 1) * n]]
    for i in range(n):
        for j in range(n):
            value = sign * matrix[i][j]
            state[target * n + i] = [a + value * b for a, b in
                                         zip(state[target * n + i], old[j])]


def census():
    domain = [tuple(tuple(bits[2 * i + j] for j in range(2)) for i in range(2))
              for bits in itertools.product((0, 1), repeat=4)]
    joint, separate = Counter(), Counter()
    omit_reader = omit_source = wrong_order = 0
    for b0, b1, c in itertools.product(domain, repeat=3):
        delta, bc = subtract(b1, b0), multiply(b0, c)
        adapter = [ar + br for ar, br in zip(delta, bc)]
        joint[rank(adapter)] += 1
        separate[rank(delta) + rank(bc) - rank(adapter)] += 1
        omit_reader += int(any(any(row) for row in delta))
        omit_source += int(any(any(row) for row in bc))
        wrong_order += int(multiply(c, b0) != bc)
        # Independent arbitrary dirt is represented by ten input columns.
        state, ident = eye(10), eye(2)
        for matrix, source, target, sign in (
                (ident, 2, 3, -1), (b0, 0, 2, 1), (ident, 2, 3, 1),
                (c, 1, 0, 1), (delta, 0, 2, 1), (bc, 1, 2, 1),
                (ident, 2, 4, 1), (b1, 0, 2, -1), (ident, 2, 4, -1)):
            apply_block(state, matrix, source, target, sign)
        desired = eye(10)
        for matrix, source, target in ((c, 1, 0), (b0, 0, 3),
                                        (b1, 0, 4), (multiply(b1, c), 1, 4)):
            for i in range(2):
                for j in range(2):
                    desired[2 * target + i][2 * source + j] += matrix[i][j]
        require(state == desired, "rational moving-reader census failed")
    return {"domain": "all ordered B0,B1,C in {0,1}^{2x2}, interpreted over Q",
            "completed_triples": len(domain) ** 3,
            "joint_adapter_rank": dict(sorted(joint.items())),
            "separate_rank_overcharge": dict(sorted(separate.items())),
            "wrong_adapter_counterexamples": {"omit_reader_change": omit_reader,
                "omit_source_change": omit_source, "replace_B0C_by_CB0": wrong_order}}


def adapter_short_words():
    """Exhaust all signed-ADD words of length <=4 by meeting at two gates."""
    alphabet = [(s, t, sign) for s in range(5) for t in range(5) if s != t
                for sign in (-1, 1)]

    def ball(center):
        center = tuple(tuple(row) for row in center)
        seen, frontier = {center}, {center}
        for _ in range(2):
            following = set()
            for state in frontier:
                for source, target, sign in alphabet:
                    child = list(state)
                    child[target] = tuple(x + sign * y for x, y in
                                           zip(state[target], state[source]))
                    following.add(tuple(child))
            seen.update(following)
            frontier = following
        return seen

    target = eye(5)
    for i in (2, 3, 4):
        target[i][0] = target[i][1] = 1
    before, after = ball(eye(5)), ball(target)
    require(not before.intersection(after), "four-gate adapter unexpectedly exists")
    word = [[1, 0, 1], [0, 2, 1], [0, 3, 1], [0, 4, 1], [1, 0, -1]]
    require(symbolic(word, 5) == target, "five-gate adapter witness failed")
    return {"alphabet": "signed ADD between distinct cells in five arbitrary-dirty rows",
            "alphabet_size": len(alphabet), "radius": 2,
            "words_per_ball_before_deduplication": 1 + 40 + 40 ** 2,
            "forward_states": len(before), "reverse_states": len(after),
            "intersection": 0, "maximum_excluded_length": 4, "attaining_length": 5}


def controls(baseline, carried, bounds):
    correct = expected_map()
    start, end = bounds
    faulty = {
        "drop_repair": carried[:start] + carried[end:],
        "drop_borrowed_source_restore": carried[:end - 1] + carried[end:],
        "wrong_borrow_sign": carried[:start] + [[5, 1, -1]] + carried[start + 1:],
        "characteristic_two_readout": [[s, t, 1] for s, t, sign in carried],
        "drop_dirty_prewrites": carried[3:],
        "drop_baseline_cleanup": baseline[:-6],
    }
    closing_start = end + 4
    wrong_close = carried[:closing_start]
    append_map(wrong_close, B0, 0, 2, -1)
    faulty["use_old_reader_to_close"] = wrong_close + carried[closing_start + 6:]
    for name, gates in faulty.items():
        require(symbolic(gates) != correct, "faulty gate word accepted: " + name)
    # General coefficient order and version controls, independent of the pilot.
    b0, b1, c = [[1, 0], [1, 1]], [[2, 0], [1, 1]], [[1, 1], [0, 0]]
    require(multiply(b0, c) != multiply(b1, c), "version control is vacuous")
    require(multiply(b0, c) != multiply(c, b0), "order control is vacuous")
    return sorted([*faulty, "post_update_wrong_reader_version", "reverse_product_order"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write two derived local receipts")
    args = parser.parse_args()
    baseline, carried, bounds = programs()
    require(symbolic(baseline) == expected_map(), "baseline target mismatch")
    require(symbolic(carried) == expected_map(), "carried target mismatch")
    for name, gates in (("baseline", baseline), ("carried", carried)):
        inverse = [[s, t, -sign] for s, t, sign in reversed(gates)]
        require(symbolic(gates + inverse) == eye(15), name + " inverse failed")
    delta, bc = subtract(B1, B0), multiply(B0, C)
    receipt = {"status": "PASS_COMPLEX_MOVING_READER", "assignment_seed": 28,
               "baseline": cost(baseline), "carried": cost(carried),
               "pilot_ranks": {"B0": rank(B0), "B1": rank(B1), "C": rank(C),
                               "delta": rank(delta), "B0C": rank(bc),
                               "joint_adapter": rank([a + b for a, b in zip(delta, bc)])},
               "controls": controls(baseline, carried, bounds), "census": census(),
               "five_add_minimum": adapter_short_words()}
    gates = {"row_order": ["x", "u", "z", "y0", "y1"], "row_width": 3,
             "gate_format": ["source_cell", "target_cell", "sign"],
             "B0": B0, "B1": B1, "C": C, "A0": A0, "A1": A1,
             "baseline": baseline, "carried": carried, "repair_range": bounds}
    for name, value in (("EXPECTED.json", receipt), ("GATES.json", gates)):
        canonical = json.dumps(value, indent=2, sort_keys=True) + "\n"
        if args.write:
            (HERE / name).write_text(canonical)
        else:
            require((HERE / name).read_text() == canonical, "receipt mismatch: " + name)
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
