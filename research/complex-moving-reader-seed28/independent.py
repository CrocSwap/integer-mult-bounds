#!/usr/bin/env python3
"""Separate certificate interpreter: Gaussian integers and minor-based ranks.

Does not import the constructor or its algebra helpers.
Cinna Davis, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def mv(matrix, vector):
    return [tuple(sum(matrix[i][j] * vector[j][part] for j in range(len(vector)))
                  for part in (0, 1)) for i in range(len(matrix))]


def add(left, right):
    return [(a[0] + b[0], a[1] + b[1]) for a, b in zip(left, right)]


def execute(word, data, inverse=False):
    data = data[:]
    if inverse:
        word = [(source, target, -sign) for source, target, sign in reversed(word)]
    for source, target, sign in word:
        r, i = data[target]
        sr, si = data[source]
        data[target] = (r + sign * sr, i + sign * si)
    return data


def target(data, maps):
    x, u, z, y0, y1 = [data[i:i + 3] for i in range(0, 15, 3)]
    new_x = add(x, mv(maps["C"], u))
    new_y0 = add(y0, mv(maps["A0"], mv(maps["B0"], x)))
    new_y1 = add(y1, mv(maps["A1"], mv(maps["B1"], new_x)))
    return new_x + u + z + new_y0 + new_y1


def physical_cost(word):
    head = 0
    data_moves = 0
    for source, target, _ in word:
        # Follow the physical visits; do not use the constructor's max formula.
        for position in (source, target, 0):
            data_moves += abs(position - head)
            head = position
    n = len(word)
    check(head == 0, "data head not restored")
    code_head = code_moves = 0
    for _ in word:
        for _ in range(9):
            code_head += 1
            code_moves += 1
    code_moves += code_head
    return {"signed_adds": n, "data_head_steps": data_moves,
            "data_reads": 2 * n, "data_writes": n, "instruction_bits_per_record": 9,
            "instruction_reads": 9 * n, "instruction_head_steps": code_moves,
            "decode_dispatch": n, "unit_steps": data_moves + code_moves + 14 * n}


def two_row_rank(rows):
    if not any(any(row) for row in rows):
        return 0
    for j, k in itertools.combinations(range(len(rows[0])), 2):
        if rows[0][j] * rows[1][k] != rows[0][k] * rows[1][j]:
            return 2
    return 1


def matrices_product(a, b):
    return [[a[i][0] * b[0][j] + a[i][1] * b[1][j]
             for j in range(2)] for i in range(2)]


def census_check(expected):
    ranks, extra = Counter(), Counter()
    reader_fail = source_fail = order_fail = 0
    matrices = [list(map(list, (bits[:2], bits[2:])))
                for bits in itertools.product((0, 1), repeat=4)]
    for old in matrices:
        for new in matrices:
            for mutation in matrices:
                delta = [[new[i][j] - old[i][j] for j in range(2)] for i in range(2)]
                correction = matrices_product(old, mutation)
                joined = [delta[i] + correction[i] for i in range(2)]
                r = two_row_rank(joined)
                ranks[str(r)] += 1
                extra[str(two_row_rank(delta) + two_row_rank(correction) - r)] += 1
                reader_fail += int(any(any(row) for row in delta))
                source_fail += int(any(any(row) for row in correction))
                order_fail += int(correction != matrices_product(mutation, old))
    check(dict(ranks) == expected["joint_adapter_rank"], "minor rank census differs")
    check(dict(extra) == expected["separate_rank_overcharge"], "rank-overcharge census differs")
    check({"omit_reader_change": reader_fail, "omit_source_change": source_fail,
           "replace_B0C_by_CB0": order_fail} == expected["wrong_adapter_counterexamples"],
          "faulty-adapter census differs")
    return sum(ranks.values())


def short_word_check(expected):
    # Store column images rather than the constructor's row representation.
    identity = tuple(tuple(int(i == j) for i in range(5)) for j in range(5))
    target = tuple(tuple(int(i == j) + int(i >= 2 and j in (0, 1))
                         for i in range(5)) for j in range(5))
    letters = [(s, t, k) for k in (1, -1) for t in range(5) for s in range(5) if s != t]

    def radius_two(center):
        states, layer = {center}, {center}
        for _ in (1, 2):
            next_layer = set()
            for columns in layer:
                for s, t, k in letters:
                    transformed = tuple(tuple(value + k * column[s] if i == t else value
                                              for i, value in enumerate(column))
                                        for column in columns)
                    next_layer.add(transformed)
            states |= next_layer
            layer = next_layer
        return states

    forward, backward = radius_two(identity), radius_two(target)
    check(not (forward & backward), "independent four-ADD exclusion failed")
    check(len(forward) == expected["forward_states"] and
          len(backward) == expected["reverse_states"], "short-word coverage mismatch")
    check(expected["alphabet_size"] == len(letters) == 40 and
          expected["maximum_excluded_length"] == 4 and expected["attaining_length"] == 5,
          "short-word domain mismatch")
    # Easier two-target control has an explicit four-gate witness.
    fixture = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]
    witness = [(1, 0, 1), (0, 2, 1), (0, 3, 1), (1, 0, -1)]
    result = execute(witness, fixture)
    desired = fixture[:]
    for i in (2, 3):
        desired[i] = tuple(fixture[i][j] + fixture[0][j] + fixture[1][j] for j in (0, 1))
    check(result == desired, "two-target four-gate positive control failed")
    return len(forward) + len(backward)


def main():
    maps = json.loads((HERE / "GATES.json").read_text())
    receipt = json.loads((HERE / "EXPECTED.json").read_text())
    check(maps["row_order"] == ["x", "u", "z", "y0", "y1"] and maps["row_width"] == 3,
          "unexpected data layout")
    fixtures = []
    for column in range(15):
        for value in ((1, 0), (0, 1)):
            data = [(0, 0)] * 15
            data[column] = value
            fixtures.append(data)
    # Dense, dirty Gaussian integer inputs, deterministically selected by seed28.
    for seed in range(28, 92):
        fixtures.append([((seed * (j + 1) % 17) - 8,
                          (seed + 3 * j * j) % 19 - 9) for j in range(15)])
    evaluations = 0
    for name in ("baseline", "carried"):
        word = maps[name]
        check(physical_cost(word) == receipt[name], "cost discrepancy: " + name)
        for size in (1, 2, 3):
            # I_L extension, evaluated as independent complex input lanes.
            for start in range(len(fixtures)):
                lanes = [fixtures[(start + lane) % len(fixtures)] for lane in range(size)]
                for data in lanes:
                    actual = execute(word, data)
                    check(actual == target(data, maps), "Gaussian integer target failure")
                    check(execute(word, actual, inverse=True) == data, "literal inverse failure")
                    evaluations += 1
    count = census_check(receipt["census"])
    states = short_word_check(receipt["five_add_minimum"])
    # A one-cell sign corruption must fail on an independently supplied basis.
    corrupt = [gate[:] for gate in maps["carried"]]
    corrupt[maps["repair_range"][0]][2] *= -1
    check(any(execute(corrupt, data) != target(data, maps) for data in fixtures),
          "independent corruption control did not fail")
    print(json.dumps({"status": "PASS_INDEPENDENT_COMPLEX_MOVING_READER",
                      "gaussian_integer_lane_evaluations": evaluations,
                      "rank_triples": count, "lengths": [1, 2, 3],
                      "gaussian_integer_fixtures": len(fixtures),
                      "short_word_ball_states": states}, sort_keys=True))


if __name__ == "__main__":
    main()
