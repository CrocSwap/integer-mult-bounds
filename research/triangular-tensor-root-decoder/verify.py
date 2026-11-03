#!/usr/bin/env python3
"""Exact support-aware tensor-root factorization. Nick Petalas, Apache-2.0."""

from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import platform
import sys


FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def size(s):
    require(type(s) is int and 1 <= s <= 6, "tensor exponent outside 1..6")
    return 1 << s


def rank2(rows):
    """Gaussian elimination of bounded binary row masks."""
    require(len(rows) <= 64, "too many binary rows")
    pivots = [0] * 64
    result = 0
    for original in rows:
        require(type(original) is int and 0 <= original < (1 << 64), "bad row")
        value = original
        for bit in range(63, -1, -1):
            if (value >> bit) & 1:
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    result += 1
                    break
    return result


def factor(s):
    n = size(s)
    frame = tuple(tuple(Fraction(1 << (s - x.bit_count())) if z & x == z
                        else Fraction(0) for z in range(n)) for x in range(n))
    weights = tuple(Fraction(2, n) * 3 ** z.bit_count() for z in range(n))
    return frame, weights


def kron(a, b):
    require(1 <= len(a) <= 32 and 1 <= len(b) <= 2, "Kronecker capacity")
    return tuple(tuple(av * bv for av in ar for bv in br)
                 for ar in a for br in b)


def tensor(base, s):
    size(s)
    result = ((Fraction(1),),)
    for _ in range(s):
        result = kron(result, base)
    return result


def target(s):
    return tensor(((2, 1), (1, 2)), s)


def pairing(gram):
    n = len(gram)
    require(2 <= n <= 64, "pairing capacity")
    return tuple(tuple((int(value) + 1) % 2 for value in row) for row in gram)


def support_cost(binary, left, right):
    rows = [sum(binary[x][y] << j for j, y in enumerate(right)) for x in left]
    return rank2(rows)


def check_identity(frame, weights, gram):
    n = len(gram)
    for x in range(n):
        for y in range(n):
            value = sum((weights[z] * frame[x][z] * frame[y][z]
                         for z in range(n)), Fraction(0))
            require(value == 2 * gram[x][y], "full Gram identity failed")
    return n * n


def check_inverse(frame, s):
    inverse = tensor(((Fraction(1, 2), 0), (Fraction(-1, 2), 1)), s)
    n = len(frame)
    for x in range(n):
        for y in range(n):
            left = sum((frame[x][z] * inverse[z][y] for z in range(n)), Fraction(0))
            right = sum((inverse[x][z] * frame[z][y] for z in range(n)), Fraction(0))
            require(left == right == int(x == y), "two-sided frame inverse failed")
    return 2 * n * n


def check_level(s):
    n = size(s)
    frame, weights = factor(s)
    literal = tensor(((2, 0), (1, 1)), s)
    require(frame == literal, "closed and literal tensor frames differ")
    gram = target(s)
    identities = check_identity(frame, weights, gram)
    inverses = check_inverse(frame, s)
    binary = pairing(gram)
    require(all(binary[x][y] == int(y != (x ^ (n - 1)))
                for x in range(n) for y in range(n)), "complement pairing failed")
    supports = [tuple(x for x in range(n) if frame[x][z]) for z in range(n)]
    costs = [support_cost(binary, support, support) for support in supports]
    require(costs == [n] + [1] * (n - 1), "COPY profile failed")
    require(sum(bool(v) for row in frame for v in row) == 3 ** s, "frame sparsity")
    require(sum(costs) == 2 * n - 1 < n * n, "rank mass improvement failed")
    return {"s": s, "n": n, "profile": {"1": n - 1, str(n): 1},
            "copy_mass": sum(costs), "dense_mass_cited": n * n,
            "frame_nonzeros": 3 ** s, "identity_entries": identities,
            "inverse_entries": inverses}


def check_actual_roots():
    entries = 0
    base = ((1, 1, 0, 0, 0, 0, 0, 0), (1, 0, 1, 0, 0, 0, 0, 0))
    for s in range(1, 4):
        n = size(s)
        roots = []
        for word in product(range(2), repeat=s):
            vector = (1,)
            for digit in word:
                vector = tuple(a * b for a in vector for b in base[digit])
            roots.append(vector)
        gram = target(s)
        for x in range(n):
            for y in range(n):
                dot = sum(a * b for a, b in zip(roots[x], roots[y], strict=True))
                require(dot == gram[x][y], "literal product-root Gram failed")
                entries += 1
    return entries


def expect_failure(operation):
    try:
        operation()
    except ValueError:
        return 1
    raise ValueError("rejection control unexpectedly passed")


def check_controls():
    count = 0
    for invalid in (0, -1, 7, True, Fraction(2), "2"):
        count += expect_failure(lambda: size(invalid))
    frame, weights = factor(2)
    gram = target(2)
    count += expect_failure(lambda: check_identity(frame, (weights[0] + 1,) + weights[1:], gram))
    count += expect_failure(lambda: check_identity(frame, weights[:-1] + (0,), gram))
    wrong = tuple(tuple(row[3 - z] for z in range(4)) for row in frame)
    count += expect_failure(lambda: check_identity(wrong, weights, gram))
    binary = pairing(gram)
    require(support_cost(binary, (0, 3), (0, 3)) == 2, "antipodal support control")
    require(support_cost(binary, (1, 3), (1, 3)) == 1, "proper subcube control")
    count += 2
    count += expect_failure(lambda: require(support_cost(binary, range(4), range(4)) == 1,
                                            "false full-support tariff"))
    count += expect_failure(lambda: require(sum(row[0] != 0 for row in frame) == 1,
                                            "false all-singleton profile"))
    return count


def receipt_hashes():
    directory = Path(__file__).resolve().parent
    result = {}
    for name in FILES:
        path = directory / name
        require(path.stat().st_size <= 256 * 1024, "source file capacity")
        data = path.read_bytes()
        result[name] = sha256(data).hexdigest()
    return result


def main():
    levels = [check_level(s) for s in range(1, 7)]
    roots = check_actual_roots()
    controls = check_controls()
    result = {"status": "PASS_TRIANGULAR_TENSOR_ROOT_DECODER", "levels": levels,
              "literal_root_gram_entries": roots,
              "controls": controls, "python": platform.python_version(),
              "source_sha256": receipt_hashes()}
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
