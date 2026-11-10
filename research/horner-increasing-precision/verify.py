"""Exact finite corroboration of the increasing-precision Horner theorem."""

from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json
import platform


def require(condition, message):
    if not condition:
        raise ValueError(message)


def precisions(p):
    require(type(p) is int and 102 <= p <= 2048, "precision domain")
    return tuple(max(101, j + 3) for j in range(p))


def trunc(value):
    if value >= 0:
        return value.numerator // value.denominator
    return -((-value).numerator // value.denominator)


def rescale(n, old, new):
    if new >= old:
        return n << (new - old)
    return (abs(n) >> (old - new)) * (1 if n >= 0 else -1)


def complex_norm_ok(values, bound):
    return all(values[i] ** 2 + values[i + 1] ** 2 <= bound ** 2
               for i in range(0, len(values), 2))


def block_matrix(rows):
    d = len(rows)
    require(1 <= d <= 3 and all(len(row) == d for row in rows), "matrix shape")
    require(all(sum(abs(a) + abs(b) for a, b in row) <= F(21, 50)
                for row in rows), "operator bound")
    result = [[F(0) for _ in range(2 * d)] for _ in range(2 * d)]
    for i, row in enumerate(rows):
        for j, (a, b) in enumerate(row):
            result[2 * i][2 * j] = a
            result[2 * i][2 * j + 1] = -b
            result[2 * i + 1][2 * j] = b
            result[2 * i + 1][2 * j + 1] = a
    return result


def inverse_shift(matrix):
    n = len(matrix)
    rows = [[matrix[i][j] + (i == j) for j in range(n)]
            + [F(i == j) for j in range(n)] for i in range(n)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        require(pivot is not None, "singular inverse")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        divisor = rows[j][j]
        rows[j] = [x / divisor for x in rows[j]]
        for i in range(n):
            if i != j:
                multiplier = rows[i][j]
                rows[i] = [a - multiplier * b for a, b in zip(rows[i], rows[j])]
    require(all(rows[i][j] == (i == j) for i in range(n) for j in range(n)),
            "inverse left block")
    result = [row[n:] for row in rows]
    require(all(sum((matrix[i][k] + (i == k)) * result[k][j] for k in range(n))
                == (i == j) for i in range(n) for j in range(n)), "inverse product")
    return result


def apply(matrix, vector):
    return [sum(a * b for a, b in zip(row, vector)) for row in matrix]


def integer_oracle(rows, values, q, mode):
    exact = []
    for row in rows:
        real = sum(a * values[2 * j] - b * values[2 * j + 1]
                   for j, (a, b) in enumerate(row))
        imag = sum(b * values[2 * j] + a * values[2 * j + 1]
                   for j, (a, b) in enumerate(row))
        exact.extend((real, imag))
    result = [trunc(x) for x in exact]
    for i in range(0, len(values), 2):
        sign = (values[i] > 0) - (values[i] < 0)
        result[i] += mode * (q // 4 - 2) * sign
    errors = [a - b for a, b in zip(result, exact)]
    require(all(errors[i] ** 2 + errors[i + 1] ** 2 < F(q, 3) ** 2
                for i in range(0, len(values), 2)), "oracle local error")
    return result


def run_case(rows, u, p, mode, levels=None, update_sign=-1, halve=True):
    levels = precisions(p) if levels is None else levels
    require(len(levels) == p and all(101 <= q <= p + 2 for q in levels),
            "precision schedule range")
    require(all(a <= b for a, b in zip(levels, levels[1:])), "grid nesting")
    matrix = block_matrix(rows)
    reference = [F(x, 1 << (p + int(halve))) for x in u]
    state = [rescale(x, p + int(halve), levels[0]) for x in u]
    reference = [F(trunc(x * (1 << levels[0])), 1 << levels[0]) for x in reference]
    require(complex_norm_ok(u, 1 << p), "input disk")
    require(complex_norm_ok(state, 1 << levels[0]), "initial disk")
    for j in range(1, p):
        q = levels[j]
        embedded = [rescale(x, levels[j - 1], q) for x in state]
        require(complex_norm_ok(embedded, 1 << q), "oracle input disk")
        image = integer_oracle(rows, embedded, q, mode)
        source = [rescale(x, p + int(halve), q) for x in u]
        state = [a + update_sign * b for a, b in zip(source, image)]
        exact_image = apply(matrix, reference)
        rounded = [F(trunc(x * (1 << q)), 1 << q) for x in exact_image]
        for i in range(0, len(u), 2):
            sign = (reference[i] > 0) - (reference[i] < 0)
            rounded[i] += F(mode * (q // 4 - 2) * sign, 1 << q)
        source_ref = [F(trunc(F(x, 1 << (p + int(halve))) * (1 << q)), 1 << q)
                      for x in u]
        reference = [a + update_sign * b for a, b in zip(source_ref, rounded)]
        require(reference == [F(x, 1 << q) for x in state], "prefix disagreement")
        require(complex_norm_ok(state, 1 << q), "output disk")
        require(complex_norm_ok(image, 1 << q), "oracle output disk")
    final = [rescale(x, levels[-1], p) for x in state]
    reference = [F(trunc(x * (1 << p)), 1 << p) for x in reference]
    require(reference == [F(x, 1 << p) for x in final], "final projection")
    require(complex_norm_ok(final, 1 << p), "final disk")
    expected = apply(inverse_shift(matrix), [F(x, 1 << (p + 1)) for x in u])
    error = [a - b for a, b in zip(reference, expected)]
    allowance = (F(25 * (2 * p + 13), 96) + F(137, 58)) / (1 << p)
    require(allowance < F(p, 1 << p), "claimed allowance")
    require(all(error[i] ** 2 + error[i + 1] ** 2 < allowance ** 2
                for i in range(0, len(u), 2)), "final inverse error")
    return p - 1


def fixtures():
    z = (F(0), F(0))
    return (
        (((F(21, 50), F(0)),),),
        (((F(-21, 50), F(0)),),),
        ((z, (F(1, 4), F(0))), ((F(1, 4), F(0)), z)),
        ((z, (F(1, 5), F(1, 10))), ((F(-1, 10), F(1, 10)), z)),
        (((F(1, 10), F(0)), (F(0), F(1, 5)), z),
         (z, (F(-1, 10), F(0)), (F(3, 10), F(0))),
         (z, z, (F(1, 5), F(0)))),
    )


def input_vectors(d, p):
    scale = 1 << p
    values = [[0] * (2 * d)]
    for j in range(2 * d):
        unit = [0] * (2 * d)
        unit[j] = scale if j % 2 == 0 else -scale
        values.append(unit)
    values.append([n for _ in range(d) for n in (3 * scale // 5, 4 * scale // 5)])
    values.append([n for i in range(d) for n in ((-1) ** i * 112, 14)])
    values.append([n for i in range(d) for n in ((-1) ** i * (scale // 2 + 1), scale // 4)])
    return values


def proof_arithmetic():
    for p in range(102, 2049):
        levels = precisions(p)
        actual = sum(levels[1:])
        closed = (p * p + 5 * p) // 2 + 4750
        require(actual == closed < p * (p - 1), "precision volume")
        require(F(25 * (2 * p + 13), 96) + F(137, 58) < p, "error allowance")
        require(all(q >= p + 2 - (p - 1 - j) for j, q in enumerate(levels)),
                "precision damping")
    require(F(1, 2) + F(21, 50) + F(101, 3 * (1 << 101)) < 1,
            "global disk slack")
    require(F(21, 50) < F(1, 2) and 2 * F(21, 50) < 1, "tail and damping")
    return 1947


def controls():
    rejected = 0
    for bad in (101, 2049, True, F(102), "102"):
        try:
            precisions(bad)
        except ValueError as error:
            require(str(error) == "precision domain", "precision control reason")
            rejected += 1
        else:
            raise ValueError("bad precision accepted")
    row = (((F(1, 4), F(0)),),)
    u = [1 << 256, 0]
    attempts = (
        ({"levels": (101,) * 256}, "final inverse error"),
        ({"update_sign": 1}, "final inverse error"),
        ({"halve": False}, "final inverse error"),
        ({"levels": (102, 101) + precisions(256)[2:]}, "grid nesting"),
        ({"mode": 1000}, "oracle local error"),
    )
    for change, reason in attempts:
        options = {"mode": 1, **change}
        try:
            run_case(row, u, 256, **options)
        except ValueError as error:
            require(str(error) == reason, "semantic control reason")
            rejected += 1
        else:
            raise ValueError("semantic control accepted")
    try:
        block_matrix((((F(1, 2), F(0)),),))
    except ValueError as error:
        require(str(error) == "operator bound", "operator control reason")
        rejected += 1
    else:
        raise ValueError("expansive matrix accepted")
    return rejected


def main():
    cases = calls = 0
    for rows in fixtures():
        for p in (102, 103, 128, 192, 256, 512):
            for u in input_vectors(len(rows), p):
                for mode in (-1, 0, 1):
                    calls += run_case(rows, u, p, mode)
                    cases += 1
    result = {"cases": cases, "oracle_calls": calls,
              "precision_arithmetic_cases": proof_arithmetic(), "rejections": controls()}
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        path = package / name
        require(path.stat().st_size <= 256 * 1024, "package file capacity")
        hashes[name] = sha256(path.read_bytes()).hexdigest()
    receipt = {"result": result, "python": platform.python_version(), "sha256": hashes}
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_HORNER_INCREASING_PRECISION", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
