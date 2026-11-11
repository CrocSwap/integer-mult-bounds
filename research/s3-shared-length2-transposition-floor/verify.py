#!/usr/bin/env python3
"""Exact check for the shared length-2 S3 transposition floor.

Model: a paid call is a pair (g, mask), where g is an S3 element written to
every register selected by the nonempty mask, and the cost is the reduced
generator length of g with respect to s = (1 2) and t = (2 3).  A register's
induced element is the ordered product over the calls whose mask contains it.

The script enumerates every shared word of total cost at most two on two and
three registers, checks that no register receives the transposition (1 3),
and supplies cost-3 and cost-4 attaining controls.  Standard library only.
"""

import hashlib
import itertools
import os

S = (1, 0, 2)
T = (0, 2, 1)
E = (0, 1, 2)
TARGET = (2, 1, 0)
REGISTER_COUNTS = (2, 3)
PACKAGE_FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
                 "VERIFY.json", "verify.py")


def compose(a, b):
    """Return a after b, acting on positions 0,1,2."""
    return tuple(a[b[i]] for i in range(3))


def inverse(a):
    out = [0, 0, 0]
    for i, value in enumerate(a):
        out[value] = i
    return tuple(out)


def all_elements():
    return [perm for perm in itertools.permutations(range(3))]


def word_lengths():
    """Breadth-first reduced lengths for the generating set {S, T}."""
    distance = {E: 0}
    frontier = [E]
    while frontier:
        nxt = []
        for word in frontier:
            for letter in (S, T):
                image = compose(letter, word)
                if image not in distance:
                    distance[image] = distance[word] + 1
                    nxt.append(image)
        frontier = nxt
    return distance


def products(letters):
    out = E
    for letter in letters:
        out = compose(letter, out)
    return out


def masks(count):
    return [mask for mask in range(1, 1 << count)]


def selected(mask, register):
    return (mask >> register) & 1


def induce(calls, count):
    """Induced element on each register for a shared word."""
    out = []
    for register in range(count):
        letters = [g for g, mask in calls if selected(mask, register)]
        out.append(products(letters))
    return out


def enumerate_cost_at_most_two(count, distance):
    """Every nonempty shared word of total paid cost at most two."""
    one_cost = [g for g in all_elements() if distance.get(g) == 1]
    two_cost = [g for g in all_elements() if distance.get(g) == 2]
    words = []
    for mask in masks(count):
        for g in one_cost:
            words.append([(g, mask)])
        for g in two_cost:
            words.append([(g, mask)])
    for first in masks(count):
        for second in masks(count):
            for g in one_cost:
                for h in one_cost:
                    words.append([(g, first), (h, second)])
    return words


def check_group(distance):
    """Multiplication, inverse, length table and subadditivity."""
    elements = all_elements()
    assert len(elements) == 6
    for a in elements:
        assert compose(a, inverse(a)) == E
        assert compose(inverse(a), a) == E
    for a in elements:
        for b in elements:
            c = compose(a, b)
            assert distance[c] <= distance[a] + distance[b]
    expected = {E: 0, S: 1, T: 1,
                compose(S, T): 2, compose(T, S): 2, TARGET: 3}
    assert distance == expected, (distance, expected)
    assert compose(S, compose(T, S)) == TARGET
    assert compose(T, compose(S, T)) == TARGET
    return len(elements) ** 2


def check_cost_two(count, distance):
    """No cost-at-most-two shared word writes TARGET on any register."""
    words = enumerate_cost_at_most_two(count, distance)
    evaluations = 0
    for calls in words:
        induced = induce(calls, count)
        for register, value in enumerate(induced):
            assert value != TARGET, (count, calls, register)
            evaluations += 1
    return len(words), evaluations


def check_controls(count, distance):
    """Cost 3 attains; cost 4 attains and restores one scratch register."""
    assert induce([(S, 1), (T, 1), (S, 1)], count)[0] == TARGET
    full = (1 << count) - 1
    restored = [(S, full), (T, 1), (S, 1), (S, 2)]
    induced = induce(restored, count)
    assert induced[0] == TARGET, induced
    if count >= 2:
        assert induced[1] == E, induced
    # Sharing the same three letters across both registers writes TARGET twice.
    shared = [(S, full), (T, full), (S, full)]
    assert induce(shared, count)[0] == TARGET
    if count >= 2:
        assert induce(shared, count)[1] == TARGET
    # A cost-2 product is a 3-cycle, never the transposition.
    assert compose(S, T) != TARGET and compose(T, S) != TARGET
    return 3 + len(restored) + len(shared) + 2


def check_mutation_rejected(count):
    """A length-2 product is a 3-cycle, not the transposition."""
    calls = [(S, 1), (T, 1)]
    assert induce(calls, count)[0] != TARGET
    calls = [(T, 1), (S, 1)]
    assert induce(calls, count)[0] != TARGET
    return 2


def receipt():
    root = os.path.dirname(os.path.abspath(__file__))
    digest = hashlib.sha256()
    present = 0
    for name in PACKAGE_FILES:
        path = os.path.join(root, name)
        if not os.path.isfile(path):
            continue
        with open(path, "rb") as handle:
            digest.update(name.encode("ascii") + b"\0" + handle.read() + b"\0")
        present += 1
    return digest.hexdigest(), present


def main():
    distance = word_lengths()
    pairs = check_group(distance)
    total_words = 0
    total_evaluations = 0
    for count in REGISTER_COUNTS:
        words, evaluations = check_cost_two(count, distance)
        total_words += words
        total_evaluations += evaluations
        controls = check_controls(count, distance)
        mutation = check_mutation_rejected(count)
        print("registers=%d words=%d evaluations=%d controls=%d mutation=%d"
              % (count, words, evaluations, controls, mutation))
    digest, present = receipt()
    print("PASS_S3_SHARED_LENGTH2_TRANSPOSITION_FLOOR "
          "pairs=%d words=%d evaluations=%d target_length=3 "
          "shared_cost=4 receipt=%s files=%d"
          % (pairs, total_words, total_evaluations, digest[:16], present))


if __name__ == "__main__":
    main()
