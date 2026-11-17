"""Exact finite corroboration of the sharp relaxed native-fusion error law."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
from fractions import Fraction as F
from pathlib import Path

G = tuple[F, F]
Matrix = list[list[G]]
ZERO: G = (F(0), F(0))
ONE: G = (F(1), F(0))
A: G = (F(1, 2), F(1, 2))
B: G = (F(1, 2), F(-1, 2))
MAX_DIM = 128


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def add(x: G, y: G) -> G:
    return x[0] + y[0], x[1] + y[1]


def mul(x: G, y: G) -> G:
    return x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0]


def scale(x: G, q: F) -> G:
    return q * x[0], q * x[1]


def norm2(x: G) -> F:
    return x[0] ** 2 + x[1] ** 2


def power(x: G, n: int) -> G:
    require(0 <= n <= 6, "power exponent outside finite-check domain")
    out = ONE
    for _ in range(n):
        out = mul(out, x)
    return out


def zeros(rows: int, cols: int) -> Matrix:
    require(1 <= rows <= MAX_DIM and 1 <= cols <= MAX_DIM, "matrix capacity")
    return [[ZERO for _ in range(cols)] for _ in range(rows)]


def matmul(x: Matrix, y: Matrix) -> Matrix:
    require(bool(x) and bool(y) and len(x[0]) == len(y), "matrix dimensions")
    out = zeros(len(x), len(y[0]))
    for i, row in enumerate(x):
        for k, value in enumerate(row):
            if value == ZERO:
                continue
            for j, other in enumerate(y[k]):
                if other != ZERO:
                    out[i][j] = add(out[i][j], mul(value, other))
    return out


def tensor(n: int) -> Matrix:
    require(0 <= n <= 6, "tensor exponent outside finite-check domain")
    out = [[ONE]]
    for _ in range(n):
        size = len(out)
        new = zeros(2 * size, 2 * size)
        for i in range(2 * size):
            for j in range(2 * size):
                base = A if i // size == j // size else B
                new[i][j] = mul(base, out[i % size][j % size])
        out = new
    return out


def duplicate(x: Matrix) -> Matrix:
    size = len(x)
    out = zeros(2 * size, 2 * size)
    for lane in range(2):
        for i in range(size):
            for j in range(size):
                out[lane * size + i][lane * size + j] = x[i][j]
    return out


def column_errors(x: Matrix, target: Matrix) -> list[F]:
    require(len(x) == len(target) and len(x[0]) == len(target[0]), "error shapes")
    errors = [F(0) for _ in target[0]]
    for i, row in enumerate(target):
        for j, value in enumerate(row):
            errors[j] += norm2(add(x[i][j], scale(value, F(-1))))
    return errors


def bypass(target: Matrix, gain: F, h: int) -> Matrix:
    d = len(target) // 2
    require(0 <= h <= d, "bypass support")
    out = zeros(len(target), len(target))
    for j in range(len(target)):
        start = (j // d) * d
        for i in range(start, start + h):
            out[i][j] = scale(target[i][j], 1 - gain)
    return out


def plus(x: Matrix, y: Matrix) -> Matrix:
    require(len(x) == len(y) and len(x[0]) == len(y[0]), "sum shapes")
    return [[add(a, b) for a, b in zip(row, other, strict=True)]
            for row, other in zip(x, y, strict=True)]


def attainer(f: int, r: int, gain: F) -> tuple[Matrix, Matrix, Matrix, Matrix]:
    require(1 <= f <= 3 and 2 <= r <= 4 and r * f <= 6, "attainer domain")
    require(0 <= gain <= 1, "attainer gain")
    d, n = 2 ** f, 2 ** (r * f)
    child, target = duplicate(tensor(r * f)), duplicate(tensor(f))
    encode, read = zeros(2 * n, 2 * d), zeros(2 * d, 2 * n)
    factor = power(A, (r - 1) * f)
    reciprocal = scale((factor[0], -factor[1]), gain / norm2(factor))
    for lane in range(2):
        for j in range(d):
            encode[lane * n + j][lane * d + j] = ONE
            read[lane * d + j][lane * n + j] = reciprocal
    require(norm2(reciprocal) == gain ** 2 * n / d, "adapter norm product")
    return child, target, encode, read


def check_attainers() -> dict[str, int]:
    cases = columns = tensor_entries = 0
    shapes = ((1, 2), (1, 3), (1, 4), (2, 2), (2, 3), (3, 2))
    for f, r in shapes:
        child, target, encode, read = attainer(f, r, F(1))
        raw = matmul(child, encode)
        require(matmul(read, raw) == target, "exact projected identity")
        d, n = 2 ** f, 2 ** (r * f)
        for i in range(n):
            for j in range(n):
                weight = (i ^ j).bit_count()
                direct = mul(power(A, r * f - weight), power(B, weight))
                require(child[i][j] == direct, "independent tensor entry")
                require(norm2(direct) == F(1, n), "flat child modulus")
                tensor_entries += 1
        for gain in (F(0), F(1, 4), F(1, 2), F(3, 4), F(1)):
            scaled_read = [[scale(x, gain) for x in row] for row in read]
            projected = matmul(scaled_read, raw)
            for h in range(d + 1):
                output = plus(projected, bypass(target, gain, h))
                errors = column_errors(output, target)
                expected = F(d - h, d) * (1 - gain) ** 2
                require(all(e == expected for e in errors), "sharp error equality")
                cases += 1
                columns += len(errors)
    return {"attainers": cases, "attainer_columns": columns,
            "independent_tensor_entries": tensor_entries}


def axis_abs(x: G) -> F:
    require(x[0] == 0 or x[1] == 0, "axis-only random adapter coefficient")
    return abs(x[0]) + abs(x[1])


def random_adapter(rng: random.Random, rows: int, cols: int) -> Matrix:
    out = zeros(rows, cols)
    values = ((F(1, 4), F(0)), (F(-1, 4), F(0)),
              (F(0), F(1, 4)), (F(0), F(-1, 4)))
    for j in range(cols):
        for i in rng.sample(range(rows), min(2, rows)):
            out[i][j] = rng.choice(values)
    return out


def check_general_adapters() -> dict[str, int]:
    rng = random.Random(7166)
    cases = columns = 0
    for f, r in ((2, 2), (2, 3)):
        d, n = 2 ** f, 2 ** (r * f)
        child, target = duplicate(tensor(r * f)), duplicate(tensor(f))
        alpha = F(1, 2 ** ((r - 1) * f // 2))
        for _ in range(4):
            encode = random_adapter(rng, 2 * n, 2 * d)
            transposed = random_adapter(rng, 2 * n, 2 * d)
            read = [list(row) for row in zip(*transposed, strict=True)]
            a_norm = max(sum(axis_abs(row[j]) for row in encode)
                         for j in range(2 * d))
            b_norm = max(sum(axis_abs(value) for value in row) for row in read)
            product = a_norm * b_norm
            projected = matmul(read, matmul(child, encode))
            for h in range(d + 1):
                shortcut = zeros(2 * d, 2 * d)
                for j in range(2 * d):
                    for i in rng.sample(range(2 * d), h):
                        shortcut[i][j] = rng.choice((A, B, ONE))
                errors = column_errors(plus(projected, shortcut), target)
                bound = F(d - h, d) * max(F(0), 1 - product * alpha) ** 2
                require(all(e >= bound for e in errors), "general lower bound")
                cases += 1
                columns += len(errors)
    return {"general_adapters": cases, "general_columns": columns}


def check_controls() -> dict[str, int]:
    child, target, encode, read = attainer(2, 2, F(1, 2))
    projected = matmul(read, matmul(child, encode))
    expected = F(3, 16)
    require(all(e == expected for e in column_errors(
        plus(projected, bypass(target, F(1, 2), 1)), target)), "control baseline")
    wrong_phase = [[mul(x, (F(0), F(1))) for x in row] for row in projected]
    require(any(e != expected for e in column_errors(
        plus(wrong_phase, bypass(target, F(1, 2), 1)), target)), "phase rejection")
    require(any(e != expected for e in column_errors(projected, target)),
            "missing bypass rejection")
    require(expected < F(1, 4), "wrong support-count rejection")
    threshold = [h for h in range(257) if F(256 - h, 256) * F(15, 16) ** 2 <= F(1, 4)]
    require(min(threshold) == 184, "exact bypass threshold")
    rejected = 0
    for rows, cols in ((0, 1), (1, 0), (129, 1), (1, 129)):
        try:
            zeros(rows, cols)
        except ValueError:
            rejected += 1
    require(rejected == 4, "matrix-capacity rejections")
    return {"semantic_controls": 3, "capacity_rejections": rejected,
            "threshold_supports_enumerated": 257, "half_error_minimum_bypass": 184}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="create a hash-bound receipt; refuse overwrite")
    args = parser.parse_args()
    counts = check_attainers() | check_general_adapters() | check_controls()
    package = Path(__file__).resolve().parent
    names = ("verify.py", "README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json")
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest() for name in names}
    report = {"status": "PASS_SHARP_APPROXIMATE_NATIVE_FUSION", "counts": counts,
              "python": platform.python_version(), "sha256": hashes}
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.receipt is not None:
        with args.receipt.open("x", encoding="utf-8") as stream:
            written = stream.write(payload)
        require(written == len(payload), "complete receipt write")
    print(payload, end="")


if __name__ == "__main__":
    main()
