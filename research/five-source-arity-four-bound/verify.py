#!/usr/bin/env python3
"""Exact finite check for the five-source arity-four connector boundary."""

from hashlib import sha256
from itertools import product


def require(condition, message):
    if not condition:
        raise ValueError(message)


def matvec(matrix, vector):
    return tuple(sum(a * b for a, b in zip(row, vector)) % 2 for row in matrix)


def matmul(left, right):
    return tuple(
        tuple(sum(left[i][k] * right[k][j] for k in range(2)) % 2 for j in range(2))
        for i in range(2)
    )


def fused_four(z, matrices, sources):
    out = list(z)
    for matrix, source in zip(matrices, sources):
        term = matvec(matrix, source)
        out = [a ^ b for a, b in zip(out, term)]
    return tuple(out)


def prefix_differences(events):
    prefixes = [0]
    current = 0
    for event in events:
        current ^= event
        prefixes.append(current)
    if current != 0:
        raise ValueError("source event word is not restored")
    differences = {0}
    for i, left in enumerate(prefixes):
        for right in prefixes[:i]:
            differences.add(left ^ right)
    return differences


def tiny_dirty_control():
    # B0 and B1 do not commute; all four inputs and z are dirty.
    matrices = (
        ((1, 1), (0, 1)),
        ((1, 0), (1, 1)),
        ((0, 1), (1, 0)),
        ((1, 0), (0, 1)),
    )
    sources = ((1, 0), (0, 1), (1, 1), (1, 0))
    z_in = (1, 1)
    require(
        matmul(matrices[0], matrices[1]) != matmul(matrices[1], matrices[0]),
        "noncommuting-map control failed",
    )
    z_out = fused_four(z_in, matrices, sources)
    require(z_out == (0, 1), "dirty four-source output mismatch")
    require(fused_four(z_out, matrices, sources) == z_in, "two calls did not restore dirty z")
    require(sources == ((1, 0), (0, 1), (1, 1), (1, 0)), "source rows changed")
    return z_out


def normalized_census():
    # By source permutation fix the four-toggle as 01111. By cyclic rotation
    # of a closed event word, put that toggle last. The 8 singleton labels
    # before it must XOR to 01111. This enumerates every normalized word.
    quad = 0b01111
    valid = 0
    histogram = {}
    records = []
    maximum = 0
    maximum_word = None
    maximum_differences = None

    for word in product(range(5), repeat=8):
        end = 0
        prefixes = [0]
        for label in word:
            end ^= 1 << label
            prefixes.append(end)
        if end != quad:
            continue

        valid += 1
        differences = {0}
        for i, left in enumerate(prefixes):
            for right in prefixes[:i]:
                differences.add(left ^ right)

        size = len(differences)
        histogram[size] = histogram.get(size, 0) + 1
        encoded_differences = bytes(sorted(differences))
        records.append(bytes(word) + b":" + encoded_differences + b"\n")
        if size > maximum:
            maximum = size
            maximum_word = word
            maximum_differences = differences

    digest = sha256(b"".join(records)).hexdigest()
    return valid, histogram, maximum, maximum_word, maximum_differences, digest


def symmetry_control(word, canonical_differences):
    # Check all 5 choices of omitted source and all 9 cyclic rotations of the
    # complete closed event cycle on a maximizing word. Label permutations
    # and cycle rotations preserve the difference-set cardinality.
    for omitted in range(5):
        labels = [j for j in range(5) if j != omitted]
        permutation = {j: labels[j] for j in range(4)}
        permutation[4] = omitted
        events = [1 << permutation[j] for j in word]
        events.append(0b11111 ^ (1 << omitted))
        for shift in range(9):
            rotated = events[shift:] + events[:shift]
            differences = prefix_differences(rotated)
            require(
                len(differences) == len(canonical_differences),
                "cyclic or label symmetry changed coverage cardinality",
            )


def singleton_positive_control():
    # Twelve-event all-singleton repair from the pinned predecessor.
    word = (2, 0, 2, 1, 2, 0, 3, 1, 4, 2, 3, 4)
    differences = prefix_differences(tuple(1 << label for label in word))
    require(len(differences) == 32, "twelve-event positive control lost masks")
    return len(differences)


def main():
    dirty_out = tiny_dirty_control()
    valid, histogram, maximum, max_word, max_differences, digest = normalized_census()
    require(valid == 23184, "normalized branch size changed")
    require(histogram == {
        11: 312,
        13: 2160,
        14: 2976,
        15: 576,
        16: 2832,
        19: 4464,
        21: 3984,
        22: 408,
        23: 3168,
        24: 1728,
        26: 576,
    }, "coverage histogram changed")
    require(maximum == 26, "maximum difference-set size changed")
    require(max_word == (0, 1, 0, 2, 0, 4, 3, 4), "maximizing word changed")
    require(len(max_differences) == 26, "maximum witness has wrong coverage")
    symmetry_control(max_word, max_differences)
    baseline_masks = singleton_positive_control()
    missing = tuple(mask for mask in range(1, 32) if mask not in max_differences)
    print(
        "PASS_FIVE_SOURCE_ARITY4_BOUND "
        f"dirty_out={dirty_out} normalized_words={valid} "
        f"max_D={maximum}/32 max_word={''.join(map(str, max_word))} "
        f"missing={','.join(f'{mask:05b}' for mask in missing)} "
        f"baseline_D={baseline_masks}/32 sha256={digest}"
    )


if __name__ == "__main__":
    main()
