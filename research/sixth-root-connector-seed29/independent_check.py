#!/usr/bin/env python3
"""Second census: ordered local phases, interleavings and explicit coordinates.

No imports from verify.py or predecessor code. Dense rational block matrices
provide a second semantics for the attaining words. This is algorithmic
independence, not independent human or proof-assistant review.
Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import itertools
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[1]
PHASES = ((1, 0), (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1))
TARGET = ((1, 1, 1), (1, 1, -1), (1, -1, 0))


def check(ok, message):
    if not ok:
        raise ValueError(message)


def local_sequences(n):
    return [word for word in itertools.product(PHASES, repeat=n)
            if sum(x[0] for x in word) == 0 and sum(x[1] for x in word) == 0]


def interleavings(counts):
    def visit(left, prefix):
        if not any(left):
            yield prefix
            return
        for j, n in enumerate(left):
            if n:
                next_left = list(left)
                next_left[j] -= 1
                yield from visit(next_left, prefix + (j,))
    return tuple(visit(counts, ()))


def count_case(extra):
    counts = tuple(3 if j == extra else 2 for j in range(3))
    orders = interleavings(counts)
    check(len(orders) == (90 if extra is None else 210), "interleaving count")
    matches = {}
    for i, row in enumerate(TARGET):
        for a, b in PHASES:
            key = tuple(component for c in row for component in (c * a, c * b))
            matches[key] = matches.get(key, 0) | (1 << i)
    hist = [0] * 8
    for schedules in itertools.product(*(local_sequences(n) for n in counts)):
        for labels in orders:
            indices = [0, 0, 0]
            current = [0] * 6
            points = {tuple(current)}
            for j in labels:
                a, b = schedules[j][indices[j]]
                indices[j] += 1
                current[2 * j] += a
                current[2 * j + 1] += b
                points.add(tuple(current))
            check(current == [0] * 6, "source restoration")
            mask = 0
            # Each target orbit includes its negative, so either orientation
            # of an unordered boundary pair suffices. No packed integers.
            for p, q in itertools.combinations(points, 2):
                difference = tuple(a - b for a, b in zip(p, q))
                mask |= matches.get(difference, 0)
            hist[mask] += 1
    return {"paths": sum(hist), "row_coverage_histogram": hist, "feasible": hist[7]}


def matrix_product(x, y):
    return [[sum(x[i][k] * y[k][j] for k in range(2)) for j in range(2)]
            for i in range(2)]


def rational_phase(a, b):
    # Multiplication by a+b*omega on the rational basis (1,omega).
    return [[a, -b], [b, a - b]]


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


OPERATORS = {
    "B0": [[1, 2], [0, 1]], "B1": [[0, 1], [-1, 1]],
    "B2": [[1, -1], [2, 1]], "A0": [[1, 0], [3, 1]],
    "A1": [[2, 1], [1, 1]], "A2": [[1, 2], [1, 3]],
}


def dense_word(word, initial=None):
    # Seven length-two arrays over Q(omega) = 28 independent rational inputs.
    out = identity(28) if initial is None else [row[:] for row in initial]
    for kind, j, phase in word:
        source, target = (j, 6) if kind == "B" else (6, j + 3)
        scalar = rational_phase(*phase)
        operator = OPERATORS[kind + str(j)]
        for r in range(2):
            for a in range(2):
                destination = 4 * target + 2 * r + a
                for s in range(2):
                    for b in range(2):
                        coefficient = operator[r][s] * scalar[a][b]
                        origin = 4 * source + 2 * s + b
                        for col in range(28):
                            out[destination][col] += coefficient * out[origin][col]
    return out


def dense_expected(reverse_factors=False):
    result = identity(28)
    for i in range(3):
        for j in range(3):
            a, b = OPERATORS["A" + str(i)], OPERATORS["B" + str(j)]
            product = matrix_product(b, a) if reverse_factors else matrix_product(a, b)
            for r in range(2):
                for s in range(2):
                    for component in range(2):
                        result[4 * (3 + i) + 2 * r + component][4 * j + 2 * s + component] += (
                            TARGET[i][j] * product[r][s])
    return result


def check_words():
    pins = json.loads((PACKAGE / "SOURCES.json").read_text())
    name = "research/weighted-signed-connector-seed58/CERTIFICATE.json"
    record = next(x for x in pins["files"] if x["path"] == name)
    raw = (REPO / name).read_bytes()
    check(hashlib.sha256(raw).hexdigest() == record["sha256"], "predecessor source drift")
    source = json.loads(raw)
    expected = dense_expected()
    check(expected != dense_expected(True), "fixture must distinguish factor order")
    maps = 0
    for original in source["witnesses"].values():
        # First signed; second B phases omega and A phases omega^2.
        for gauge in (False, True):
            word = []
            for kind, j, sign in original:
                phase = ((0, sign) if kind == "B" else (-sign, -sign)) if gauge else (sign, 0)
                word.append((kind, j, phase))
            out = dense_word(word)
            check(out == expected, "dense target or dirty row failure")
            undo = [(kind, j, (-a, -b)) for kind, j, (a, b) in reversed(word)]
            check(dense_word(undo, out) == identity(28), "dense inverse failure")
            maps += 2
    # An Eisenstein zero triangle is nonzero if silently read as three +1s.
    omega = rational_phase(0, 1)
    omega2 = matrix_product(omega, omega)
    check([[int(i == j) + omega[i][j] + omega2[i][j] for j in range(2)]
           for i in range(2)] == [[0, 0], [0, 0]], "phase triangle")
    check([[3, 0], [0, 3]] != [[0, 0], [0, 0]], "finite-characteristic confusion")
    return maps


def main():
    expected = json.loads((PACKAGE / "CERTIFICATE.json").read_text())
    check(len(local_sequences(2)) == 6 and len(local_sequences(3)) == 12,
          "ordered zero-sum phase coverage")
    cases = {"12": count_case(None)}
    for extra in range(3):
        cases["13_B" + str(extra)] = count_case(extra)
    check(cases == expected["census"], "independent histogram mismatch")
    check(sum(x["paths"] for x in cases.values()) == 291600, "coverage total")
    check(all(x["feasible"] == 0 for x in cases.values()), "short phase word exists")
    maps = check_words()
    print("PASS_INDEPENDENT_SIXTH_ROOT_CONNECTOR source_paths=291600 "
          f"histograms=4 rational_basis_inputs=28 dense_maps={maps}")


if __name__ == "__main__":
    main()
