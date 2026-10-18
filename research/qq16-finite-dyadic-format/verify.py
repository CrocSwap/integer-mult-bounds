#!/usr/bin/env python3
"""Authenticate sources and check finite-integer rounded-line arithmetic."""

import argparse
import hashlib
import json
import sys
from fractions import Fraction as F
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import grid  # noqa: E402

MAX_BYTES = 400_000
MAX_BITS = 8192


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_json(path):
    need(path.stat().st_size <= MAX_BYTES, "JSON capacity")
    return json.loads(path.read_text(), object_pairs_hook=unique)


def sources():
    manifest = read_json(PACKAGE / "SOURCES.json")
    pins = manifest["snapshots"]
    need(len(pins) == 3, "three source snapshots")
    need(
        {p["path"] for p in pins}
        == {"source/WORD.json", "source/LINE-PROOF.md", "source/DEFECT-PROOF.md"},
        "complete source inventory",
    )
    for pin in pins:
        path = PACKAGE / pin["path"]
        need(path.stat().st_size <= MAX_BYTES, "source capacity")
        need(
            hashlib.sha256(path.read_bytes()).hexdigest() == pin["sha256"],
            "source hash mismatch: " + pin["path"],
        )
    return read_json(PACKAGE / "source/WORD.json")


def signed(value, bits):
    need(type(bits) is int and 2 <= bits <= MAX_BITS, "register capacity")
    need(
        type(value) is int and -(1 << (bits - 1)) <= value < 1 << (bits - 1),
        "signed register overflow",
    )
    return value


def rounded_integer(value, shift, bits):
    """Round value/2**shift to nearest integer, ties to even, for signed input."""
    signed(value, bits)
    need(type(shift) is int and 0 <= shift <= bits - 2, "rounding shift")
    divisor = signed(1 << shift, bits)
    lower, remainder = divmod(value, divisor)
    # Compare to half without constructing 2*remainder in a finite register.
    if remainder > divisor - remainder or (remainder == divisor - remainder and lower % 2):
        lower = signed(lower + 1, bits)
    return signed(lower, bits)


def integer_pair(left, right, sign, scale, bits):
    need(type(sign) is int and sign in (-1, 1), "signed pair")
    need(type(scale) is int and 0 <= scale <= bits - 3, "pair scale")
    ar, ai, br, bi = (signed(v, bits) for v in (*left, *right))
    sr, si = signed(ar + br, bits), signed(ai + bi, bits)
    dr, di = signed(ar - br, bits), signed(ai - bi, bits)
    raw = (
        signed(sr - sign * di, bits),
        signed(si + sign * dr, bits),
        signed(sr + sign * di, bits),
        signed(si - sign * dr, bits),
    )
    values = tuple(signed(rounded_integer(v, scale + 1, bits) << scale, bits) for v in raw)
    return values[:2], values[2:]


def integer_line(values, width, directions, sign, precision, bits):
    need(type(width) is int and 1 <= width <= 4, "fixture width capacity")
    need(1 <= len(directions) <= 4 and width * len(directions) <= 10, "fixture depth capacity")
    size = 1 << (width * len(directions))
    need(len(values) == size, "payload size")
    need(all(type(q) is int and 0 <= q < 1 << width for q in directions), "direction")
    need(type(sign) is int and sign in (-1, 1), "line sign")
    need(type(precision) is int and 1 <= precision <= 512, "precision capacity")
    need(all(len(z) == 2 for z in values), "complex components")
    result = [tuple(signed(v, bits) for v in z) for z in values]
    maximum = signed(max(abs(v) for z in result for v in z), bits)
    if maximum == 0 or not any(directions):
        return result
    padding = (len(directions) - 1).bit_length() + width * len(directions) // 2
    scale = maximum.bit_length() - 1 - precision - padding
    need(scale >= 0, "common grid too coarse for relative line")
    for factor, q in enumerate(directions):
        if q == 0:
            continue
        shift = q << (width * factor)
        for x in range(size):
            y = x ^ shift
            if x < y:
                result[x], result[y] = integer_pair(result[x], result[y], sign, scale, bits)
    return result


def rational_round(value, step):
    lower, remainder = divmod(value, step)
    return (lower + int(remainder > step / 2 or (remainder == step / 2 and lower % 2))) * step


def rational_line(values, width, directions, sign, step):
    """Separate four-term Gaussian oracle with exact Fractions."""
    result = [(F(a), F(b)) for a, b in values]
    for factor, q in enumerate(directions):
        if q == 0:
            continue
        for x in range(len(result)):
            y = x ^ (q << (width * factor))
            if x < y:
                a, b = result[x], result[y]
                left = (
                    (a[0] + b[0] - sign * a[1] + sign * b[1]) / 2,
                    (a[1] + b[1] + sign * a[0] - sign * b[0]) / 2,
                )
                right = (
                    (a[0] + b[0] + sign * a[1] - sign * b[1]) / 2,
                    (a[1] + b[1] - sign * a[0] + sign * b[0]) / 2,
                )
                if step is not None:
                    left = tuple(rational_round(v, step) for v in left)
                    right = tuple(rational_round(v, step) for v in right)
                result[x], result[y] = left, right
    return result


def line_fixtures():
    cases, errors = 0, 0
    for width in range(1, 4):
        for depth in range(1, 4):
            size = 1 << (width * depth)
            for sign in (-1, 1):
                for precision in (2, 22, 25):
                    directions = [1 + (j % ((1 << width) - 1)) for j in range(depth)]
                    padding = (depth - 1).bit_length() + width * depth // 2
                    values = [(1 << (precision + padding + 4), -3)]
                    values += [((17 * j) % 31 - 15, (11 * j) % 29 - 14) for j in range(1, size)]
                    scale = (
                        max(abs(v) for z in values for v in z).bit_length()
                        - 1
                        - precision
                        - padding
                    )
                    actual = integer_line(values, width, directions, sign, precision, 128)
                    expected = rational_line(values, width, directions, sign, F(1 << scale))
                    need(actual == expected, "integer/rational rounded disagreement")
                    ideal = rational_line(values, width, directions, sign, None)
                    error = sum(
                        (F(a) - z) ** 2
                        for p, q in zip(actual, ideal, strict=True)
                        for a, z in zip(p, q, strict=True)
                    )
                    norm = sum(v * v for pair in values for v in pair)
                    need(error * (1 << (2 * precision)) <= norm, "relative defect")
                    errors += int(error != 0)
                    cases += 1
    return cases, errors


def exact_add(destination, source, coefficient, bits):
    """Component ADD on the common grid; a quarter division must be exact."""
    signed(destination, bits)
    signed(source, bits)
    need(coefficient in (F(1), F(-1), F(1, 4), F(-1, 4)), "ADD coefficient")
    need(source % coefficient.denominator == 0, "inexact quarter source")
    return signed(destination + coefficient.numerator * (source // coefficient.denominator), bits)


def controls():
    tests = [
        lambda: signed(128, 8),
        lambda: integer_pair((64, 64), (64, -64), 1, 0, 8),
        lambda: integer_line([(1, 0), (0, 0)], 1, [1], 1, 22, 64),
        lambda: exact_add(0, 1, F(1, 4), 8),
    ]
    for test in tests:
        try:
            test()
        except ValueError:
            continue
        raise ValueError("negative arithmetic control accepted")
    need(rounded_integer(-3, 1, 8) == -2 and rounded_integer(-1, 1, 8) == 0, "negative even ties")
    need(exact_add(-3, 8, F(1, 4), 8) == -1, "exact quarter")
    need(integer_line([(0, 0), (0, 0)], 1, [0], 1, 22, 64) == [(0, 0), (0, 0)], "zero exact")
    return len(tests)


def word_fixture(word, depth, q0, b):
    """All cuts of one noncommuting small-payload isometry model, not source semantics."""
    size, width, exponent = 1 << depth, 1, 5
    padding = (depth - 1).bit_length() + depth // 2
    qmax = q0 + 3 * (b + 22 + padding) + 6
    bits = qmax + exponent + 20
    actual, ideal = {}, {}
    for prefix in "XY":
        for port in range(112):
            name = f"{prefix}{port}"
            values = [((1 << q0) + (port + x) % 7, (port - 2 * x) % 5 - 2) for x in range(size)]
            actual[name] = [tuple(v << (qmax - q0) for v in pair) for pair in values]
            ideal[name] = [(F(a), F(c)) for a, c in actual[name]]
    changed = 0
    for index, event in enumerate(word):
        op, name = event[:2]
        if op == "clear":
            actual[name], ideal[name] = [(0, 0)] * size, [(F(0), F(0))] * size
        elif op == "add":
            c, source = F(event[3]), event[2]
            actual[name] = [
                tuple(exact_add(a, z, c, bits) for a, z in zip(p, r, strict=True))
                for p, r in zip(actual[name], actual[source], strict=True)
            ]
            ideal[name] = [
                tuple(a + c * z for a, z in zip(p, r, strict=True))
                for p, r in zip(ideal[name], ideal[source], strict=True)
            ]
        elif op == "line":
            directions = [1] * depth
            actual[name] = integer_line(actual[name], width, directions, event[3], b + 22, bits)
            ideal[name] = rational_line(ideal[name], width, directions, event[3], None)
        elif op == "map":
            # Rotation and XOR permutations need not commute with the line or each other.
            shift = index % depth
            perm = [
                (((x << shift) | (x >> (depth - shift))) & (size - 1)) ^ (index % size)
                for x in range(size)
            ]
            actual[name] = [actual[name][x] for x in perm]
            ideal[name] = [ideal[name][x] for x in perm]
        else:
            continue
        difference = sum(
            (F(a) - z) ** 2
            for p, r in zip(actual[name], ideal[name], strict=True)
            for a, z in zip(p, r, strict=True)
        )
        need(difference < 1 << (2 * (exponent + qmax - b)), "whole-word all-cut error")
        norm = sum(v * v for pair in actual[name] for v in pair)
        need(norm < 32369**2 * (1 << (2 * (exponent + qmax))), "whole-word magnitude")
        changed += int(difference != 0)
    return changed


def result():
    word = sources()
    certificate = grid.run_checks(word)
    cases, errors = line_fixtures()
    need(errors == cases, "rounding fixtures must exercise nonzero error")
    nonzero = [
        word_fixture(word, depth, q0, b) for depth in (1, 2, 3) for q0 in (0, 40) for b in (0, 3)
    ]
    need(sum(v != 0 for v in nonzero) == 6, "fine-entry word fixtures must round")
    return {
        "grid_certificate": certificate,
        "grid_bound": "Q0 + 3*(b+22+ceil_log2(depth)+floor(width*depth/2)) + 6",
        "signed_bits": "Qmax + E + 20",
        "line_cases": cases,
        "nonzero_error_cases": errors,
        "arithmetic_controls": controls(),
        "word_cases": len(nonzero),
        "word_cases_with_nonzero_errors": sum(v != 0 for v in nonzero),
        "scope": "finite direct integer implementation; no recursive tariff or supplier admission",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-result", type=Path)
    args = parser.parse_args()
    actual = result()
    if args.emit_result is not None:
        with args.emit_result.open("x") as stream:
            stream.write(json.dumps(actual, indent=2, sort_keys=True) + "\n")
    else:
        expected = read_json(PACKAGE / "RESULT.json")
        need(
            json.dumps(expected, sort_keys=True) == json.dumps(actual, sort_keys=True),
            "typed receipt mismatch",
        )
    print("PASS_QQ16_FINITE_DYADIC_FORMAT cuts=3816 grid=Q0+3k+6 no_new_kappa")


if __name__ == "__main__":
    main()
