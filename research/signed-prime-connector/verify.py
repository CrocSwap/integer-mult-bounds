#!/usr/bin/env python3
"""Exact signed two-source full-coefficient connector checks.

Produced by Nick Petalas. Apache-2.0.
"""

import hashlib
import itertools
import json
from pathlib import Path
import random
import sys


PRIMES = (3, 5, 7, 11, 13)
MAX_PRIME = 31
PACKAGE_FILES = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_prime(p):
    require(isinstance(p, int) and 3 <= p <= MAX_PRIME and p % 2 == 1,
            "prime outside executable odd-prime domain")
    require(all(p % d for d in range(2, p)), "composite modulus")


def source_path(p):
    check_prime(p)
    h = (p - 1) // 2
    return [("B", 0, 1)] * h + [("B", 1, 1)] * h + [
        ("B", 0, -1)] * h + [("B", 1, -1)] * h


def vertices(path):
    require(len(path) <= 2 * MAX_PRIME, "source path too long")
    result = [(0, 0)]
    q = [0, 0]
    for kind, j, sign in path:
        require(kind == "B" and j in (0, 1) and sign in (-1, 1), "bad source event")
        q[j] += sign
        result.append(tuple(q))
    return result


def rows(p):
    check_prime(p)
    return [v for v in itertools.product(range(p), repeat=2) if v != (0, 0)]


def readout_pair(v, p):
    """Return perimeter points P,Q with P-Q congruent to v, without a search."""
    h = (p - 1) // 2
    a, b = (x if x <= h else x - p for x in v)
    reverse = a < 0
    if reverse:
        a, b = -a, -b
    if b >= 0:
        positive, negative = (a, h), (0, h - b)
    else:
        positive, negative = (a, 0), (0, -b)
    if reverse:
        positive, negative = negative, positive
    require(tuple((x - y) % p for x, y in zip(positive, negative)) == v,
            "closed-form pair has wrong coefficient")
    return positive, negative


def compile_word(p):
    path = source_path(p)
    palette = vertices(path)
    first = {}
    for t, point in enumerate(palette):
        if point not in first:
            first[point] = t
    slots = [[] for _ in palette]
    targets = rows(p)
    for index, v in enumerate(targets):
        positive, negative = readout_pair(v, p)
        require(positive in first and negative in first, "readout point off perimeter")
        slots[first[positive]].append(("A", index, 1))
        slots[first[negative]].append(("A", index, -1))
    word = []
    for t, calls in enumerate(slots):
        word.extend(calls)
        if t < len(path):
            word.append(path[t])
    require(palette[-1] == (0, 0), "connector not restored as an integer path")
    require(len(word) == 2 * p * p + 2 * p - 4, "incorrect full call count")
    return targets, word


def symbolic_replay(p, targets, word):
    """Track dirt, B0*x0 and B1*x1, with the distinct A_v always on the left."""
    check_prime(p)
    require(0 < len(targets) < MAX_PRIME ** 2, "target capacity exceeded")
    require(len(word) <= 2 * MAX_PRIME ** 2 + 2 * MAX_PRIME,
            "word capacity exceeded")
    q = [1, 0, 0]
    out = [[0, 0, 0] for _ in targets]
    for kind, j, sign in word:
        require(sign in (-1, 1), "invalid sign")
        if kind == "B":
            require(j in (0, 1), "invalid source")
            q[j + 1] = (q[j + 1] + sign) % p
        else:
            require(kind == "A" and 0 <= j < len(targets), "invalid readout")
            out[j] = [(x + sign * y) % p for x, y in zip(out[j], q)]
    require(q == [1, 0, 0], "connector restoration failed")
    require(out == [[0, *v] for v in targets], "dirty target action failed")


def difference_set(points, p):
    return {((x[0] - y[0]) % p, (x[1] - y[1]) % p)
            for x in points for y in points}


def check_constructions():
    report = []
    for p in PRIMES:
        targets, word = compile_word(p)
        symbolic_replay(p, targets, word)
        points = vertices(source_path(p))
        require(len(difference_set(points, p)) == p * p, "incomplete difference set")
        source_counts = [sum(kind == "B" and j == k for kind, j, _ in word)
                         for k in (0, 1)]
        require(source_counts == [p - 1, p - 1], "wrong source counts")
        report.append({"p": p, "targets": len(targets), "calls": len(word),
                       "source_calls": sum(source_counts)})
    return report


def check_short_paths(p):
    """Census every signed source word shorter than the proposed source optimum."""
    require(p in (3, 5), "census domain is p=3,5")
    letters = (("B", 0, 1), ("B", 0, -1), ("B", 1, 1), ("B", 1, -1))
    visited, closed, smallest_missing = 0, 0, p * p
    for length in range(2 * (p - 1)):
        for path in itertools.product(letters, repeat=length):
            visited += 1
            points = vertices(path)
            if any(x % p for x in points[-1]):
                continue
            closed += 1
            counts = [sum(event[1] == j for event in path) for j in (0, 1)]
            j = 0 if counts[0] <= counts[1] else 1
            require(counts[j] <= p - 2 and counts[j] % 2 == 0,
                    "short coordinate count lemma failed")
            values = [q[j] for q in points]
            require(2 * (max(values) - min(values)) <= counts[j],
                    "closed integer walk range lemma failed")
            missing = p * p - len(difference_set(points, p))
            require(missing >= 2 * p, "paired-readout deficit lemma failed")
            require(length + missing > 2 * (p - 1), "all-word excess bound failed")
            smallest_missing = min(smallest_missing, missing)
    expected_visited = sum(4 ** k for k in range(2 * (p - 1)))
    require(visited == expected_visited, "census incomplete")
    return {"p": p, "visited": visited, "closed": closed,
            "smallest_missing": smallest_missing}


def matvec(matrix, vector, p):
    return [sum(a * b for a, b in zip(row, vector)) % p for row in matrix]


def matmul(a, b, p):
    return [[sum(x * y for x, y in zip(row, column)) % p
             for column in zip(*b)] for row in a]


def dense_case(p, dimension):
    require(p in PRIMES and dimension in (2, 3), "dense fixture outside bounds")
    targets, word = compile_word(p)
    rng = random.Random(100 * p + dimension)
    b = [[[int(r == 0 and c == 1) for c in range(dimension)]
          for r in range(dimension)],
         [[int(r == 1 and c == 0) for c in range(dimension)]
          for r in range(dimension)]]
    a = [[[rng.randrange(p) for _ in range(dimension)]
          for _ in range(dimension)] for _ in targets]
    require(any(matmul(matrix, b[0], p) != matmul(b[0], matrix, p) for matrix in a),
            "fixture lacks noncommuting maps")
    x = [[rng.randrange(p) for _ in range(dimension)] for _ in (0, 1)]
    z0 = [1] + [rng.randrange(p) for _ in range(dimension - 1)]
    incoming = [[rng.randrange(p) for _ in range(dimension)] for _ in targets]
    bx = [matvec(matrix, value, p) for matrix, value in zip(b, x)]
    z, out = list(z0), [list(value) for value in incoming]
    for kind, j, sign in word:
        if kind == "B":
            z = [(old + sign * value) % p for old, value in zip(z, bx[j])]
        else:
            out[j] = [(old + sign * value) % p
                      for old, value in zip(out[j], matvec(a[j], z, p))]
    require(z == z0, "dense dirty connector not restored")
    for index, v in enumerate(targets):
        required = [(v[0] * u + v[1] * w) % p for u, w in zip(*bx)]
        expected = [(old + value) % p for old, value in
                    zip(incoming[index], matvec(a[index], required, p))]
        require(out[index] == expected, "dense noncommuting target mismatch")


def check_controls():
    targets, word = compile_word(5)
    first_a = next(i for i, event in enumerate(word) if event[0] == "A")
    first_b = next(i for i, event in enumerate(word) if event[0] == "B")
    mutants = []
    for position in (first_a, first_b):
        mutants.append((5, word[:position] + word[position + 1:]))
        changed = list(word)
        kind, j, sign = changed[position]
        changed[position] = kind, j, -sign
        mutants.append((5, changed))
    changed = list(word)
    kind, j, sign = changed[first_a]
    changed[first_a] = kind, (j + 1) % len(targets), sign
    mutants.append((5, changed))
    mutants.append((5, [event for event in word if event[:2] != ("A", 0)]))
    mutants.append((7, word))
    rejected = 0
    for modulus, mutant in mutants:
        try:
            symbolic_replay(modulus, targets, mutant)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("semantic mutant accepted")
    for invalid in (2, 9, 33):
        try:
            source_path(invalid)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid modulus accepted")
    require(rejected == 10, "control inventory changed")
    return rejected


def file_hashes():
    package = Path(__file__).resolve().parent
    result = {}
    for name in PACKAGE_FILES:
        path = package / name
        require(path.is_file() and path.stat().st_size <= 1024 * 1024,
                "missing or oversized package file")
        result[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def main():
    constructions = check_constructions()
    census = [check_short_paths(p) for p in (3, 5)]
    for p in PRIMES:
        for dimension in (2, 3):
            dense_case(p, dimension)
    controls = check_controls()
    receipt = {"claim_type": "scoped proof with finite corroboration",
               "constructions": constructions, "short_path_census": census,
               "dense_cases": 2 * len(PRIMES), "rejected_controls": controls,
               "python": sys.version.split()[0], "sha256": file_hashes()}
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_SIGNED_PRIME_CONNECTOR p5_calls=56 primes=5 dense_cases=10 controls=10")


if __name__ == "__main__":
    main()
