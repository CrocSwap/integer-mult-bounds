#!/usr/bin/env python3
"""Literal finite corroboration of the extension-residue lift count.

Produced by Nick Petalas. Apache-2.0. No predecessor code is imported.
"""

from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digits(value: int, base: int, length: int) -> tuple[int, ...]:
    result = []
    for _ in range(length):
        result.append(value % base)
        value //= base
    require(value == 0, "coefficient encoding overflow")
    return tuple(result)


def encode(values: tuple[int, ...], base: int) -> int:
    return sum(value * base**i for i, value in enumerate(values))


class Field:
    def __init__(self, prime: int, modulus: tuple[int, ...]) -> None:
        require((prime, modulus) in (
            (2, (1, 1, 1)), (2, (1, 1, 0, 1)),
            (3, (1, 0, 1)), (2, (1, 1, 0, 0, 1))), "unsupported field")
        self.p = prime
        self.modulus = modulus
        self.degree = len(modulus) - 1
        self.size = prime**self.degree
        coefficients = [digits(a, prime, self.degree) for a in range(self.size)]
        self.add = [[encode(tuple((x + y) % prime for x, y in zip(a, b)), prime)
                     for b in coefficients] for a in coefficients]
        self.mul = [[self.multiply(a, b) for b in coefficients] for a in coefficients]
        self.neg = [next(b for b in range(self.size) if self.add[a][b] == 0)
                    for a in range(self.size)]
        require(all(sum(self.mul[a][b] == 1 for b in range(self.size)) == 1
                    for a in range(1, self.size)), "not a field")

    def multiply(self, a: tuple[int, ...], b: tuple[int, ...]) -> int:
        work = [0] * (2 * self.degree - 1)
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                work[i + j] = (work[i + j] + x * y) % self.p
        for i in range(len(work) - 1, self.degree - 1, -1):
            leading = work[i]
            for j in range(self.degree + 1):
                k = i - self.degree + j
                work[k] = (work[k] - leading * self.modulus[j]) % self.p
        return encode(tuple(work[:self.degree]), self.p)

    def power(self, value: int, exponent: int) -> int:
        require(0 <= exponent <= 16, "power bound")
        result = 1
        for _ in range(exponent):
            result = self.mul[result][value]
        return result


class Ring:
    def __init__(self, field: Field, length: int) -> None:
        require(1 <= length <= 3 and field.size**length <= 81, "ring bound")
        self.field = field
        self.length = length
        self.size = field.size**length
        coefficients = [digits(a, field.size, length) for a in range(self.size)]
        self.add = [[encode(tuple(field.add[x][y] for x, y in zip(a, b)), field.size)
                     for b in coefficients] for a in coefficients]
        self.mul = [[self.multiply(a, b) for b in coefficients] for a in coefficients]

    def multiply(self, a: tuple[int, ...], b: tuple[int, ...]) -> int:
        f = self.field
        work = [0] * self.length
        for i in range(self.length):
            for j in range(self.length - i):
                work[i + j] = f.add[work[i + j]][f.mul[a[i]][b[j]]]
        return encode(tuple(work), f.size)


def base_objects(field: Field, q: int) -> tuple[tuple[int, ...], list, list]:
    require(q in (2, 3, 4) and field.size % q == 0, "base-field bound")
    base = tuple(a for a in range(field.size) if field.power(a, q) == a)
    require(len(base) == q, "wrong subfield size")
    require(all(field.add[a][b] in base and field.mul[a][b] in base
                for a in base for b in base), "subfield closure")
    lines = [(1, a) for a in base] + [(0, 1)]
    gl = []
    for a, b, c, d in product(base, repeat=4):
        determinant = field.add[field.mul[a][d]][field.neg[field.mul[b][c]]]
        if determinant:
            gl.append((a, b, c, d))
    require(len(gl) == (q*q - 1)*(q*q - q), "GL cardinality")
    return base, lines, gl


def rank_one(field: Field, matrix: tuple[int, ...]) -> bool:
    a, b, c, d = matrix
    return any(matrix) and field.mul[a][d] == field.mul[b][c]


def eligible(field: Field, matrix: tuple[int, ...], base: tuple, lines: list) -> list:
    a, b, c, d = matrix
    accepted = []
    for x, y in lines:
        first = field.add[field.mul[a][x]][field.mul[b][y]]
        second = field.add[field.mul[c][x]][field.mul[d][y]]
        if (first or second) and first in base and second in base:
            accepted.append((x, y))
    require(len(accepted) in (0, 1, len(base)), "eligible-line trichotomy")
    return accepted


def literal_one_factor(ring: Ring, lines: list, gl: list) -> dict:
    """Enumerate P(u,y)G directly; do not use the lift-count criterion."""
    f = ring.field
    image = {}
    for a, b, c, d in gl:
        for x, y in lines:
            row0 = f.add[f.mul[x][a]][f.mul[y][c]]
            row1 = f.add[f.mul[x][b]][f.mul[y][d]]
            for u, v in product(range(ring.size), repeat=2):
                matrix = (ring.add[a][ring.mul[u][row0]],
                          ring.add[b][ring.mul[u][row1]],
                          ring.add[c][ring.mul[v][row0]],
                          ring.add[d][ring.mul[v][row1]])
                residue = tuple(entry % f.size for entry in matrix)
                if rank_one(f, residue):
                    image.setdefault(residue, set()).add(encode(matrix, ring.size))
    return image


def counts(q: int, extension_size: int) -> dict[int, int]:
    scalar = (q*q - 1)**2 // (q - 1)
    single = (q + 1)*(q*q - 1)*(extension_size - q)
    total = (extension_size**2 - 1)**2 // (extension_size - 1)
    return {0: total - scalar - single, 1: single, q: scalar}


def predicted(t: int, z: int) -> int:
    return 0 if t == 0 else 1 + t*(z*z - 1)


def census(ring: Ring, q: int) -> tuple[dict, dict]:
    f = ring.field
    base, lines, gl = base_objects(f, q)
    image = literal_one_factor(ring, lines, gl)
    z = ring.size // f.size
    histogram = Counter()
    one = two = residues = 0
    for matrix in product(range(f.size), repeat=4):
        if not rank_one(f, matrix):
            continue
        residues += 1
        allowed = eligible(f, matrix, base, lines)
        histogram[len(allowed)] += 1
        targets = image.get(matrix, set())
        observed = 0
        for noise in product(range(z), repeat=4):
            lift = tuple(a + f.size*b for a, b in zip(matrix, noise))
            observed += encode(lift, ring.size) in targets
        require(observed == len(targets), "literal image outside lift fiber")
        require(observed == predicted(len(allowed), z), "per-residue count")
        one += observed
        two += z**4 - observed
    expected = counts(q, f.size)
    require(all(histogram[t] == count for t, count in expected.items()), "residue counts")
    require(one + two == residues*z**4, "complete lift partition")
    require(one == sum(count*predicted(t, z) for t, count in expected.items()),
            "aggregate count")
    require(one == (q + 1)*(q*q - 1)*(f.size*z*z - q + 1), "closed total")
    result = {"q": q, "Q": f.size, "length": ring.length, "z": z,
              "residues": residues, "by_t": expected, "cost1": one, "cost2": two}
    return result, image


def controls(field: Field, image: dict, result: dict) -> int:
    alpha = 2
    base, lines, _ = base_objects(field, 2)
    require(len(eligible(field, (1, 0, 0, 0), base, lines)) == 2, "q-line fixture")
    require(len(eligible(field, (1, alpha, 0, 0), base, lines)) == 1, "one-line fixture")
    require(not eligible(field, (alpha, 0, 0, 0), base, lines), "zero-line fixture")
    require(predicted(0, 1) == 0 and 1 + 0*(1 - 1) != predicted(0, 1),
            "empty union must not count the zero noise")
    ring_size = 16
    bad = (1 + 4, 0, 0, 0)
    require(encode(bad, ring_size) not in image[(1, 0, 0, 0)],
            "scalar kernel with zero image is ineligible")
    bad = (1 + 4, 0, 0, 4)
    require(encode(bad, ring_size) not in image[(1, 0, 0, 0)], "radical kill required")
    require(result["cost1"] == 567 and result["cost2"] == 18633, "first example")
    require(sum(counts(4, 4)[t]*predicted(t, 4) for t in (0, 1, 4)) == 4575
            and result["cost1"] != 4575, "changing the base field changes cost")
    require(counts(2, 8) != counts(2, 4), "extension degree must affect residue counts")
    return 9


def receipt() -> dict[str, str]:
    directory = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        path = directory / name
        require(path.is_file() and not path.is_symlink(), "receipt input missing")
        require(path.stat().st_size <= 1024*1024, "receipt input too large")
        hashes[name] = sha256(path.read_bytes()).hexdigest()
    return hashes


def main() -> None:
    cases = ((2, (1, 1, 1), 2, 1), (2, (1, 1, 1), 2, 2),
             (2, (1, 1, 1), 2, 3), (2, (1, 1, 0, 1), 2, 1),
             (2, (1, 1, 0, 1), 2, 2), (3, (1, 0, 1), 3, 1),
             (3, (1, 0, 1), 3, 2), (2, (1, 1, 0, 0, 1), 4, 1))
    results = []
    control_count = 0
    for prime, modulus, q, length in cases:
        field = Field(prime, modulus)
        result, image = census(Ring(field, length), q)
        results.append(result)
        if field.size == 4 and length == 2:
            control_count = controls(field, image, result)
        del image
    require(control_count == 9, "controls were not run")
    total = sum(row["cost1"] + row["cost2"] for row in results)
    print(json.dumps({"cases": results, "controls": control_count,
                      "sha256": receipt()}, indent=2, sort_keys=True))
    print(f"PASS_RIGHT_VECTOR_EXTENSION_RESIDUE lifts={total} controls={control_count}")


if __name__ == "__main__":
    main()
