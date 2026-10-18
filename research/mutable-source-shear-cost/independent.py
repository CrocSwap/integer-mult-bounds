#!/usr/bin/env python3
"""Separate matching, column and dense-matrix checks. No primary-checker import.

Arham Tahir, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent


def check(ok, label):
    if not ok:
        raise ValueError(label)


def hash_json(value):
    return hashlib.sha256((json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()).hexdigest()


def matchings(left, pairs=()):
    if not left:
        yield pairs
        return
    first = left[0]
    for other in left[1:]:
        yield from matchings(tuple(v for v in left if v not in (first, other)), pairs + ((first, other),))


def walsh(values):
    result = list(values)
    stride = 1
    while stride < len(result):
        for start in range(0, len(result), 2 * stride):
            for i in range(start, start + stride):
                a, b = result[i], result[i + stride]
                result[i], result[i + stride] = a + b, a - b
        stride *= 2
    return result


def census():
    histogram, records = Counter(), []
    for pairs in matchings(tuple(range(10))):
        word = [None] * 10
        for label, (s, t) in enumerate(sorted(pairs)):
            word[s] = word[t] = label
        point, seen = 0, {0}
        for label in word:
            point ^= 1 << label
            seen.add(point)
        spectrum = walsh([int(q in seen) for q in range(32)])
        correlation = walsh([n * n for n in spectrum])
        check(all(n >= 0 and n % 32 == 0 for n in correlation), "integer autocorrelation")
        covered = [q for q, n in enumerate(correlation) if n]
        histogram[len(covered)] += 1
        records.append([word, covered])
    return {str(k): n for k, n in sorted(histogram.items())}, hash_json(sorted(records))


def column_identities():
    gates = [(s, t) for s in range(5) for t in range(5) if s != t]
    result = []
    for length in range(4):
        count = 0
        for word in product(gates, repeat=length):
            columns = [1 << j for j in range(5)]
            for s, t in word:
                columns = [v ^ (((v >> s) & 1) << t) for v in columns]
            if columns == [1, 2, 4, 8, 16]:
                check(not word or (length == 2 and word[0] == word[1]), "short identity shape")
                count += 1
        result.append(count)
    return result


def emit(points):
    pairs = []
    for mask in range(1, 32):
        valid = [(s, t) for s, t in combinations(range(len(points)), 2) if points[s] ^ points[t] == mask]
        check(bool(valid), "independent difference cover")
        pairs.append(min(valid))
    word = []
    for i, q in enumerate(points):
        for mask, pair in enumerate(pairs, 1):
            if i in pair:
                word.append(("A" + str(mask), 36, mask + 4))
        if i + 1 == len(points):
            break
        edge = q ^ points[i + 1]
        pivot = (edge & -edge).bit_length() - 1
        donors = [j for j in range(pivot + 1, 5) if edge & (1 << j)]
        word += [("X", donor, pivot) for donor in donors]
        word.append(("B", pivot, 36))
        word += [("X", donor, pivot) for donor in donors[::-1]]
    return word, [list(pair) for pair in pairs]


def tree(op, source, target, start=0, stop=5, depth=0):
    if stop - start == 1:
        return [(op + ":" + str(start), source, target)], 0
    mid, temp = start + (stop - start) // 2, 37 + depth
    right, nr = tree(op, source, temp, start, mid, depth + 1)
    left, nl = tree(op, temp, target, mid, stop, depth + 1)
    return right + left + right[::-1] + left[::-1], 1 + 2 * nr + 2 * nl


def flatten(word):
    expanded, nodes = [], 0
    for op, source, target in word:
        if op == "X":
            expanded.append((op, source, target))
        else:
            child, n = tree(op, source, target)
            expanded += child
            nodes += n
    return expanded, nodes


def map_value(matrix, value):
    return sum(((row & value).bit_count() % 2) << i for i, row in enumerate(matrix))


def tables(width):
    rng = random.Random(0x5A17 + width)
    result = {"X": list(range(1 << width))}
    for op in ["B"] + ["A" + str(m) for m in range(1, 32)]:
        matrices = [[rng.randrange(1 << width) for _ in range(width)] for _ in range(5)]
        for j, matrix in enumerate(matrices):
            result[op + ":" + str(j)] = [map_value(matrix, x) for x in range(1 << width)]
        image = []
        for x in range(1 << width):
            for matrix in matrices:
                x = map_value(matrix, x)
            image.append(x)
        result[op] = image
    return result


def run(word, incoming, lookup):
    rows = list(incoming)
    for op, source, target in word:
        rows[target] ^= lookup[op][rows[source]]
    return rows


def oracle(incoming, lookup):
    expected = list(incoming)
    for mask in range(1, 32):
        combined = 0
        for j in range(5):
            if mask & (1 << j):
                combined ^= incoming[j]
        expected[4 + mask] ^= lookup["A" + str(mask)][lookup["B"][combined]]
    return expected


def dense(candidate, predecessor):
    executions = 0
    for width in range(1, 5):
        lookup = tables(width)
        rng = random.Random(width)
        incoming_states = []
        for j in range(40):
            for bit in range(width):
                incoming = [0] * 40
                incoming[j] = 1 << bit
                incoming_states.append(incoming)
        incoming_states += [[rng.randrange(1 << width) for _ in range(40)] for _ in range(8)]
        for word in (candidate, predecessor):
            expanded, _ = flatten(word)
            for incoming in incoming_states:
                expected = oracle(incoming, lookup)
                for gates in (word, word[::-1], expanded, expanded[::-1]):
                    check(run(gates, incoming, lookup) == expected, "dense dirty-state map")
                    executions += 1
        # A genuine omitted-restoration failure, detected on a basis input.
        first_x = next(i for i, gate in enumerate(candidate) if gate[0] == "X")
        broken = candidate[:first_x] + candidate[first_x + 1:]
        check(any(run(broken, state, lookup) != oracle(state, lookup) for state in incoming_states), "dense restoration control")
    return executions


def main():
    cert = json.loads((HERE / "CERTIFICATE.json").read_text())
    points = [0, 4, 5, 1, 3, 7, 6, 14, 28, 16, 0]
    check(cert["points"] == points, "literal candidate path")
    histogram, pairing_hash = census()
    check(histogram == cert["pairing_histogram"] and pairing_hash == cert["pairing_records_sha256"], "independent pairing records")
    check(column_identities() == cert["short_shear_exclusion"]["restored_words_by_length"], "independent short identities")
    word, pairs = emit(points)
    expanded, nodes = flatten(word)
    check(pairs == cert["readout_pairs"], "literal readouts")
    check(hash_json(word) == cert["word_sha256"] and hash_json(expanded) == cert["expanded_sha256"], "literal emitted words")
    leaf_count = sum(op != "X" for op, _, _ in expanded)
    x_count = len(expanded) - leaf_count
    check((leaf_count, x_count, nodes, len(word)) == (2016, 4, 648, 76), "independent completed invoice")
    check(leaf_count + x_count + nodes + len(word) == cert["unit_tariff"]["candidate"], "paid X and dispatch")
    old = json.loads((HERE / "sources/CERTIFICATE.json").read_text())
    predecessor, _ = emit(old["points"])
    old_expanded, old_nodes = flatten(predecessor)
    check(len(old_expanded) + old_nodes + len(predecessor) == cert["unit_tariff"]["predecessor"], "predecessor complete tariff")
    executions = dense(word, predecessor)
    print("PASS_INDEPENDENT_SOURCE_SHEAR_COST dense_executions=" + str(executions) + " identities=8421 pairings=945")


if __name__ == "__main__":
    main()
