"""Independent coefficient oracle, full restoring word, and rejection controls."""

import ast
from collections import Counter
from fractions import Fraction as F
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from circuit import MAX_BITS, ZERO, decoder, execute, inverse, program, scaled


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def expected(state: tuple, sign: int = 1) -> tuple:
    """Schoolbook convolution; independent real/imaginary arithmetic."""
    output = [list(value) for value in state[6:11]]
    for j in range(3):
        for k in range(3):
            ar, ai = state[j]
            br, bi = state[3 + k]
            output[j + k][0] += sign * (ar * br - ai * bi)
            output[j + k][1] += sign * (ar * bi + ai * br)
    return state[:6] + tuple(tuple(value) for value in output) + state[11:]


def fixture(values: tuple) -> tuple:
    need(len(values) == 6, "six real input components")
    return tuple((v, 0) for v in values) + ((2, -3),) * 5 + (ZERO, ZERO)


def endpoint_cases(word: tuple) -> dict:
    backwards = tuple(inverse(op) for op in reversed(word))
    count = 0
    for values in product((-1, 0, 1), repeat=6):
        state = fixture(values)
        need(execute(state, word) == expected(state), "real cube endpoint")
        need(execute(state, backwards) == expected(state, -1), "inverse endpoint")
        count += 1
    for seed in range(257):
        values = tuple(((seed * (j + 3) + j * j) % 37 - 18,
                        (seed * (2 * j + 1) + 7) % 41 - 20) for j in range(11))
        state = values + (ZERO, ZERO)
        result = execute(state, word)
        need(result == expected(state), "complex dirty endpoint")
        need(execute(result, backwards) == state, "full restoration")
        count += 1
    huge = tuple(((-1) ** j * ((1 << 1024) + j), (1 << 1019) - j)
                 for j in range(11)) + (ZERO, ZERO)
    need(execute(huge, word) == expected(huge), "large signed endpoint")
    limit = ((1 << MAX_BITS) - 1, -(1 << (MAX_BITS - 1)))
    boundary = (limit,) * 11 + (ZERO, ZERO)
    need(execute(boundary, word) == expected(boundary), "maximum admitted entrance")
    return {"real_cube": 729, "complex_dirty": 257, "large_signed": 1,
            "maximum_bits": 1, "total": count + 2}


def qadd(a: tuple, b: tuple) -> tuple:
    return a[0] + b[0], a[1] + b[1]


def qmul(a: tuple, b: tuple) -> tuple:
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def qinv(a: tuple) -> tuple:
    norm = a[0] ** 2 + a[1] ** 2
    need(norm != 0, "invertible Gaussian rational")
    return a[0] / norm, -a[1] / norm


def evaluation_matrix() -> list:
    rows = []
    for z in ((F(0), F(0)), (F(1), F(0)), (F(0), F(1)), (F(1), F(1))):
        row = [(F(1), F(0))]
        for _ in range(4):
            row.append(qmul(row[-1], z))
        rows.append(row)
    rows.append([(F(int(j == 4)), F(0)) for j in range(5)])
    return rows


def invert_matrix(matrix: list) -> tuple:
    """Rational Gauss-Jordan oracle, unrelated to the literal decoder."""
    rows = [row[:] + [(F(int(i == j)), F(0)) for j in range(5)]
            for i, row in enumerate(matrix)]
    determinant = (F(1), F(0))
    for column in range(5):
        pivot = next(i for i in range(column, 5) if rows[i][column] != (0, 0))
        if pivot != column:
            rows[column], rows[pivot] = rows[pivot], rows[column]
            determinant = qmul(determinant, (F(-1), F(0)))
        value = rows[column][column]
        determinant = qmul(determinant, value)
        rows[column] = [qmul(x, qinv(value)) for x in rows[column]]
        for i in range(5):
            if i != column:
                value = rows[i][column]
                rows[i] = [qadd(x, qmul((-value[0], -value[1]), y))
                           for x, y in zip(rows[i], rows[column])]
    return [row[5:] for row in rows], determinant


def matrix_cases() -> dict:
    matrix = evaluation_matrix()
    inv, determinant = invert_matrix(matrix)
    need(determinant == (2, 0), "determinant two")
    nonintegral = 0
    for row in inv:
        for value in row:
            integral = all(x.denominator == 1 for x in value)
            nonintegral += not integral
            times_pi = qmul(value, (F(1), F(1)))
            need(all(x.denominator == 1 for x in times_pi), "one pi denominator")
    need(nonintegral > 0, "division cannot disappear")
    for j in range(5):
        encoded = tuple((int(matrix[i][j][0]), int(matrix[i][j][1])) for i in range(5))
        state = (ZERO,) * 6 + encoded + (ZERO, ZERO)
        target = (ZERO,) * 6 + tuple((int(i == j), 0) for i in range(5)) + (ZERO, ZERO)
        need(execute(state, decoder()) == target, "literal decoder column")
        encode = tuple(inverse(op) for op in reversed(decoder()))
        need(execute(target, encode) == state, "literal encoder column")
    return {"entries": 25, "nonintegral_inverse_entries": nonintegral,
            "determinant": [2, 0], "decoder_columns": 5, "encoder_columns": 5}


def tensor_cases(word: tuple) -> int:
    count = 0
    for left, right, phase_a, phase_b in product(range(3), range(3), (0, 1), (0, 1)):
        state = [ZERO] * 13
        state[left] = (int(phase_a == 0), int(phase_a == 1))
        state[3 + right] = (int(phase_b == 0), int(phase_b == 1))
        need(execute(tuple(state), word) == expected(tuple(state)), "tensor coefficient")
        count += 1
    for target, phase in product(range(6, 11), (0, 1)):
        state = [ZERO] * 13
        state[target] = (int(phase == 0), int(phase == 1))
        need(execute(tuple(state), word) == tuple(state), "arbitrary dirty output column")
        count += 1
    return count


def binary_obstruction() -> dict:
    rows = set()
    for u, v in product(range(2), repeat=2):
        if u or v:
            rows.add(tuple(u ** j * v ** (4 - j) % 2 for j in range(5)))
    need(len(rows) == 3, "three projective rows over F2")
    spans = {tuple(0 for _ in range(5))}
    for row in sorted(rows):
        spans |= {tuple(a ^ b for a, b in zip(x, row)) for x in tuple(spans)}
    need(len(spans) == 8, "evaluation rank three, not five")
    return {"projective_rows": 3, "span_size": 8}


def controls(word: tuple) -> dict:
    killed = 0
    states = []
    for j in range(9):
        state = [ZERO] * 13
        state[j // 3] = (1, 1)
        state[3 + j % 3] = (2, -1)
        state[6:11] = [(2, -3)] * 5
        states.append(tuple(state))
    for omitted in range(len(word)):
        mutant = word[:omitted] + word[omitted + 1:]
        detected = False
        for state in states:
            try:
                detected |= execute(state, mutant) != expected(state)
            except ValueError:
                detected = True
        need(detected, f"undetected instruction omission {omitted}")
        killed += 1
    invalid = [(), fixture((0,) * 6)[:12],
               fixture((0,) * 6)[:11] + ((1, 0), ZERO),
               ((True, 0),) + fixture((0,) * 6)[1:],
               ((1 << (MAX_BITS + 1), 0),) + fixture((0,) * 6)[1:]]
    for state in invalid:
        try:
            execute(state, word)
        except ValueError:
            continue
        raise ValueError("accepted invalid entrance")
    try:
        scaled((1, 0), (-1, 1, 2))
    except ValueError:
        return {"instruction_omissions": killed, "invalid_entrances": len(invalid),
                "inexact_division": 1}
    raise ValueError("accepted inexact pi division")


def diagnostics() -> dict:
    lengths = {}
    for name in ("circuit.py", "verify.py"):
        path = Path(__file__).resolve().parent / name
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                length = node.end_lineno - node.lineno + 1
                need(length <= 60, "one-page function bound")
                lengths[f"{name}:{node.name}"] = length
    return {"functions": len(lengths), "maximum_function_lines": max(lengths.values())}


def main() -> None:
    need(len(sys.argv) == 1, "no command-line arguments")
    word = program()
    counts = dict(Counter(op[0] for op in word))
    need(counts == {"ADD": 60, "SCALE": 4, "PRODUCT": 5}, "full word invoice")
    result = {"status": "PASS_GAUSSIAN_DYADIC_TOOM3", "claim_type": "scoped construction",
              "invoice": counts, "tensor_cases": tensor_cases(word),
              "matrix": matrix_cases(), "endpoints": endpoint_cases(word),
              "binary_obstruction": binary_obstruction(), "controls": controls(word),
              "diagnostics": diagnostics()}
    hashes = {}
    for path in sorted(Path(__file__).resolve().parent.iterdir()):
        if path.is_file():
            need(path.stat().st_size <= 128 * 1024, "package file-size bound")
            hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    result["package_sha256"] = hashes
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
