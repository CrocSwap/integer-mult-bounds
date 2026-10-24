"""Exact finite corroboration of the signed three-source demand theorem.

New work produced by Nick Petalas. Apache-2.0.
No predecessor implementation is imported or replayed.
"""

import hashlib
import itertools
import json
from pathlib import Path


ROWS = tuple(v for v in itertools.product((-1, 0, 1), repeat=3) if any(v))
CUBE = tuple(itertools.product((0, 1), repeat=3))
SOURCE = ((0, 1), (1, 1), (0, -1), (2, 1),
          (0, 1), (1, -1), (0, -1), (2, -1))
FILES = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def prefixes(source: tuple) -> tuple:
    require(len(source) <= 8, "source path exceeds the fixed domain")
    points = [(0, 0, 0)]
    for j, sign in source:
        require(type(j) is int and 0 <= j < 3, "invalid source")
        require(type(sign) is int and sign in (-1, 1), "invalid sign")
        q = list(points[-1])
        q[j] += sign
        points.append(tuple(q))
    return tuple(points)


def compile_word() -> tuple:
    points = prefixes(SOURCE)
    require(points[-1] == points[0], "source path is not restored")
    require(set(points[:-1]) == set(CUBE), "path does not visit the cube")
    at = {q: i for i, q in enumerate(points[:-1])}
    reads = [[] for _ in range(8)]
    for i, v in enumerate(ROWS):
        positive = tuple(max(x, 0) for x in v)
        negative = tuple(max(-x, 0) for x in v)
        reads[at[positive]].append(("A", i, 1))
        reads[at[negative]].append(("A", i, -1))
    word = []
    for t, (j, sign) in enumerate(SOURCE):
        word.extend(reads[t])
        word.append(("B", j, sign))
    return tuple(word)


def serial_word() -> tuple:
    word = []
    for i, v in enumerate(ROWS):
        word.append(("A", i, -1))
        for j in range(3):
            if v[j]:
                word.append(("B", j, v[j]))
        word.append(("A", i, 1))
        for j in range(3):
            if v[j]:
                word.append(("B", j, -v[j]))
    return tuple(word)


def formal_action(word: tuple) -> tuple:
    """Track z dirt and the three independent formal A_i B_j x_j terms."""
    require(len(word) <= 160, "word exceeds the fixed control domain")
    z = [1, 0, 0, 0]
    out = [[0] * 4 for _ in ROWS]
    for kind, i, sign in word:
        require(type(sign) is int and sign in (-1, 1), "invalid sign")
        require(type(i) is int, "invalid index type")
        if kind == "B":
            require(0 <= i < 3, "invalid source index")
            z[i + 1] += sign
        else:
            require(kind == "A" and 0 <= i < 26, "invalid readout")
            for j in range(4):
                out[i][j] += sign * z[j]
    return tuple(z), tuple(tuple(row) for row in out)


def check_action(word: tuple) -> None:
    z, out = formal_action(word)
    require(z == (1, 0, 0, 0), "connector restoration failed")
    require(out == tuple((0,) + v for v in ROWS), "target action failed")


def antipodal_check() -> dict:
    checked = 0
    max_full = 0
    full = set(itertools.product((-1, 1), repeat=3))
    for mask in range(256):
        if mask.bit_count() > 6:
            continue
        points = [CUBE[i] for i in range(8) if mask & (1 << i)]
        differences = {tuple(p[j] - q[j] for j in range(3))
                       for p in points for q in points}
        covered = len(full & differences)
        require(covered <= 6, "antipodal subset bound failed")
        require(covered <= 2 * (len(points) // 2), "pair bound failed")
        max_full = max(max_full, covered)
        checked += 1
    require(checked == 247 and max_full == 6, "subset coverage changed")
    return {"subsets_at_most_six": checked, "max_full_support_rows": max_full}


def matvec(matrix: tuple, vector: list) -> list:
    return [sum(a * b for a, b in zip(row, vector, strict=True))
            for row in matrix]


def make_matrix(seed: int, width: int) -> tuple:
    require(2 <= width <= 4, "invalid dense width")
    return tuple(tuple(((seed + 3 * i + 5 * j + i * j) % 7) - 3
                       if i else 0 for j in range(width))
                 for i in range(width))


def dense_execute(word: tuple, state: list, source: tuple, target: tuple) -> list:
    value = [row[:] for row in state]
    for kind, i, sign in word:
        if kind == "B":
            dst, src, matrix = 3, i, source[i]
        else:
            dst, src, matrix = 4 + i, 3, target[i]
        increment = matvec(matrix, value[src])
        value[dst] = [a + sign * b for a, b in
                      zip(value[dst], increment, strict=True)]
    return value


def dense_checks(word: tuple) -> dict:
    cases = 0
    noncommuting = 0
    inverse = tuple((kind, i, -sign) for kind, i, sign in reversed(word))
    for width in range(2, 5):
        for seed in range(1, 9):
            source = tuple(make_matrix(seed + j, width) for j in range(3))
            target = tuple(make_matrix(seed + 2 * i + 7, width)
                           for i in range(26))
            state = [[((seed + i * 7 + j * 3) % 17) - 8
                      for j in range(width)] for i in range(30)]
            expected = [row[:] for row in state]
            for i, v in enumerate(ROWS):
                combined = [0] * width
                for j in range(3):
                    bx = matvec(source[j], state[j])
                    combined = [a + v[j] * b for a, b in
                                zip(combined, bx, strict=True)]
                delta = matvec(target[i], combined)
                expected[4 + i] = [a + b for a, b in
                                  zip(state[4 + i], delta, strict=True)]
            actual = dense_execute(word, state, source, target)
            require(actual == expected, "dense dirty action failed")
            require(dense_execute(inverse, actual, source, target) == state,
                    "dense inverse failed")
            for j in range(3):
                ab = matvec(target[0], matvec(source[j], state[j]))
                ba = matvec(source[j], matvec(target[0], state[j]))
                noncommuting += int(ab != ba)
            cases += 1
    require(noncommuting > 0, "dense fixtures accidentally commute")
    return {"dirty_dense_cases": cases, "noncommuting_vector_tests": noncommuting}


def mutation_checks(word: tuple) -> int:
    controls = []
    for k in range(60):
        controls.append(word[:k] + word[k + 1:])
        kind, i, sign = word[k]
        controls.append(word[:k] + ((kind, i, -sign),) + word[k + 1:])
    for bad in (("B", 3, 1), ("A", 26, 1), ("X", 0, 1),
                ("A", 0, True), ("B", False, 1)):
        controls.append(word + (bad,))
    rejected = 0
    for control in controls:
        try:
            check_action(control)
        except ValueError:
            rejected += 1
    require(rejected == len(controls), "a faulty word was accepted")
    return rejected


def main() -> None:
    word = compile_word()
    check_action(word)
    serial = serial_word()
    check_action(serial)
    require(len(serial) == 160, "serial comparison count failed")
    require(len(word) == 60, "wrong complete-call count")
    require(sum(kind == "A" for kind, _, _ in word) == 52, "wrong reads")
    subsets = antipodal_check()
    dense = dense_checks(word)
    controls = mutation_checks(word)
    directory = Path(__file__).resolve().parent
    hashes = {}
    for name in FILES:
        data = (directory / name).read_bytes()
        require(len(data) <= 1_000_000, "package file exceeds hash bound")
        hashes[name] = hashlib.sha256(data).hexdigest()
    receipt = {"status": "PASS_FULL_SIGNED_TERNARY_THREE", "claim_type":
               "scoped written proof with finite exact corroboration",
               "source_calls": 8, "readouts": 52, "optimum": 60,
               "serial_comparison": len(serial),
               "source_word": SOURCE, "literal_word": word,
               "subset_check": subsets, "dense": dense,
               "rejected_controls": controls, "sha256": hashes}
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_FULL_SIGNED_TERNARY_THREE optimum=60 source=8 readouts=52")


if __name__ == "__main__":
    main()
