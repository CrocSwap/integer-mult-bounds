#!/usr/bin/env python3
"""Independent truth-table census and dense integer positive lifts.

No imports from verify.py. Uses a 3 | 4 split, versus its 4 | 3 split.
Hanson Sun, substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path


def check(condition, message):
    if not condition:
        raise ValueError(message)


OPS = [(to, source) for to in range(6) for source in range(6) if to != source]
INPUT = tuple(sum(((assignment >> bit) & 1) << assignment for assignment in range(64))
              for bit in range(6))
OUTPUT = INPUT[:3] + tuple(INPUT[j] ^ INPUT[0] ^ INPUT[1] ^ INPUT[2] for j in range(3, 6))


def apply(state, index):
    to, source = OPS[index]
    new = list(state)
    new[to] ^= new[source]
    return tuple(new)


def walk(state, count, record=()):
    if not count:
        yield state, record
    else:
        for index in range(len(OPS)):
            yield from walk(apply(state, index), count - 1, record + (index,))


def dense_lift(word):
    # Literal nonnegative matrix multiplication, not a scalar bound vector.
    matrix = [[int(i == j) for j in range(6)] for i in range(6)]
    for index in word:
        to, source = OPS[index]
        elementary = [[int(i == j) for j in range(6)] for i in range(6)]
        elementary[to][source] = 1
        matrix = [[sum(elementary[i][k] * matrix[k][j] for k in range(6))
                   for j in range(6)] for i in range(6)]
    return matrix


def read_word(gates):
    answer = []
    for pair in gates:
        check(isinstance(pair, list) and len(pair) == 2, "malformed paid gate")
        to, source = pair
        check(type(to) is int and type(source) is int and to != source
              and to in range(6) and source in range(6), "illegal paid gate")
        answer.append(OPS.index((to, source)))
    return tuple(answer)


def check_fixture(receipt):
    word = read_word(receipt["gates"])
    check(receipt["cost"] == len(word), "unpaid gate")
    for orientation, stream in (("forward", word), ("reverse", word[::-1])):
        state = INPUT
        for op in stream:
            state = apply(state, op)
        check(state == OUTPUT, "64-input dirty truth table")
        matrix = dense_lift(stream)
        check(matrix == receipt["positive_" + orientation], "incorrect positive matrix")
        check(max(map(sum, matrix)) == receipt[orientation], "incorrect positive peak")
    return word


def census():
    front = {}
    endpoint_counts, path_counts = [], []
    found = [0] * 8
    for length in range(4):
        unique, total = set(), 0
        for state, word in walk(INPUT, length):
            unique.add(state)
            total += 1
            front.setdefault(state, []).append(word)
            if state == OUTPUT:
                found[length] += 1
        endpoint_counts.append(len(unique))
        path_counts.append(total)
    shortest, histogram, feedback = [], Counter(), 0
    leaves = 0
    for state, tail in walk(OUTPUT, 4):
        leaves += 1
        for head in front.get(state, ()):
            word = head + tail[::-1]
            found[len(word)] += 1
            if len(word) == 7:
                shortest.append(word)
                f = max(map(sum, dense_lift(word)))
                b = max(map(sum, dense_lift(word[::-1])))
                histogram[(f, b)] += 1
                feedback += any(OPS[g][0] < 3 <= OPS[g][1] for g in word)
    shortest.sort()
    check(len(shortest) == len(set(shortest)), "nonunique paths")
    return {
        "words_by_length_0_through_7": found,
        # Left/right translation is bijective, so either root has these counts.
        "backward_paths_by_length": path_counts,
        "backward_distinct_endpoints_by_length": endpoint_counts,
        "backward_distinct_endpoints_total": len(front),
        "forward_length_four_paths": leaves,
        "shortest_word_sha256": hashlib.sha256(b"".join(bytes(w) for w in shortest)).hexdigest(),
        "shortest_positive_histogram": [
            {"forward": f, "reverse": b, "words": count}
            for (f, b), count in sorted(histogram.items())],
        "shortest_words_with_target_to_helper_feedback": feedback,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path,
                        default=Path(__file__).with_name("CERTIFICATE.json"))
    args = parser.parse_args()
    receipt = json.loads(args.certificate.read_text())
    check(receipt["schema_version"] == 1, "schema")
    check(receipt["model"] == "six-dirty-register-zero-frame-J3-unit-XOR", "model")
    seven = check_fixture(receipt["seven_gate_witness"])
    eight = check_fixture(receipt["eight_gate_witness"])
    check(len(seven) == 7 and len(eight) == 8, "witness costs")
    data = census()
    check(data == receipt["census"], "independent complete census mismatch")
    check(data["words_by_length_0_through_7"][:7] == [0] * 7, "shorter word exists")
    peaks = data["shortest_positive_histogram"]
    check(min(max(row["forward"], row["reverse"]) for row in peaks) == 5, "seven-gate optimum")
    # Test each input basis as a truth-table bit; this constructs the endpoint
    # support independently from the packed-row encoding in verify.py.
    support_floor = max(sum((table >> (1 << j)) & 1 for j in range(6)) for table in OUTPUT)
    check(support_floor == receipt["positive_support_lower_bound"] == 4, "support lower bound")
    improvements = {}
    for direction, stream7, stream8 in (("forward", seven, eight), ("reverse", seven[::-1], eight[::-1])):
        a, b = dense_lift(stream7), dense_lift(stream8)
        check(max(map(sum, b)) == support_floor, "attainment")
        check(all(b[i][j] <= a[i][j] for i, j in product(range(6), repeat=2)), "matrix domination")
        improvements[direction] = [[i, j, a[i][j], b[i][j]] for i, j in product(range(6), repeat=2)
                                   if b[i][j] < a[i][j]]
    check(improvements == receipt["strict_componentwise_improvements"], "domination entries")
    check(receipt["pareto_gate_count_bidirectional_peak"] == [[7, 5], [8, 4]], "Pareto frontier")

    # Distinguish an exact GF2 map from its nonnegative lift and check that
    # omitting restoration is detected even though clean-helper tests pass.
    broken = eight[:4] + eight[5:]
    state = INPUT
    for op in broken:
        state = apply(state, op)
    check(state != OUTPUT, "missing restoration was not detected")
    clean_mask = sum(1 << a for a in range(64) if a & 7 == 0)
    check(all((a & clean_mask) == (b & clean_mask) for a, b in zip(state, OUTPUT)), "clean control")
    check(max(map(sum, dense_lift(seven))) > support_floor, "endpoint-only growth control")
    print("PASS_INDEPENDENT_J3_PRECISION truth_tables=64 shortest_words=216 dense_lifts=432 frontier=(7,5),(8,4)")


if __name__ == "__main__":
    main()
