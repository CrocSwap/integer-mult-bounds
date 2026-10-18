"""Rounded Gaussian-dyadic tensor lines. Nick Petalas. Apache-2.0.

This is a bounded exact-rational reference implementation, not the recursive
rank-one child or its physical tape realization. See README.md for the all-size
proof and the extra block-scale, scan, and direct-work charges.
"""

import argparse
import hashlib
import itertools
import json
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ZERO = (Q(0), Q(0))
MAX_COORDINATES = 4096


def need(condition, message):
    if not condition:
        raise ValueError(message)


def power2(exponent):
    need(type(exponent) is int and abs(exponent) <= 4096, "power capacity")
    return Q(2**exponent) if exponent >= 0 else Q(1, 2 ** (-exponent))


def round_even(value, step):
    """Nearest multiple of a positive step, with exact ties to even."""
    need(step > 0, "positive rounding step")
    lower, remainder = divmod(value, step)
    if 2 * remainder > step or (2 * remainder == step and lower % 2):
        lower += 1
    return lower * step


def validate(values, width, directions, sign, step):
    need(type(width) is int and 1 <= width <= 12, "width capacity")
    need(1 <= len(directions) <= 12, "depth capacity")
    size = 1 << (width * len(directions))
    need(size <= MAX_COORDINATES and len(values) == size, "coordinate capacity")
    need(sign in (-1, 1) and type(sign) is int, "signed line")
    need(step > 0, "positive rounding step")
    need(all(type(q) is int and 0 < q < 1 << width for q in directions), "direction")
    need(
        all(len(z) == 2 and all(isinstance(t, Q) for t in z) for z in values),
        "Gaussian rationals",
    )
    return size


def rounded_pair(a, b, sign, step):
    """Eight real ADD/subtracts, four halvings, four component roundings."""
    sr, si = a[0] + b[0], a[1] + b[1]
    dr, di = a[0] - b[0], a[1] - b[1]
    left = tuple(round_even(t, step) for t in ((sr - di) / 2, (si + dr) / 2))
    right = tuple(round_even(t, step) for t in ((sr + di) / 2, (si - dr) / 2))
    return (left, right) if sign == 1 else (right, left)


def paired_line(values, width, directions, sign, step):
    size = validate(values, width, directions, sign, step)
    result = list(values)
    for factor, direction in enumerate(directions):
        shift = direction << (width * factor)
        for x in range(size):
            y = x ^ shift
            if x < y:
                result[x], result[y] = rounded_pair(result[x], result[y], sign, step)
    return result


def basis_permutation(size, width, directions):
    """Map the native first-bit direction to each physical q."""
    basis = []
    for factor, q in enumerate(directions):
        pivot = (q & -q).bit_length() - 1
        vectors = [q] + [1 << k for k in range(width) if k != pivot]
        basis.extend(v << (width * factor) for v in vectors)
    permutation = []
    for x in range(size):
        image = 0
        for k, vector in enumerate(basis):
            if (x >> k) & 1:
                image ^= vector
        permutation.append(image)
    need(len(set(permutation)) == size, "monomial bijection")
    return permutation


def wrapped_line(values, width, directions, sign, step):
    size = validate(values, width, directions, sign, step)
    permutation = basis_permutation(size, width, directions)
    native = [values[p] for p in permutation]
    positive = paired_line(native, width, [1] * len(directions), 1, step)
    flip = sum(1 << (width * j) for j in range(len(directions))) if sign == -1 else 0
    output = [ZERO] * size
    for x, physical in enumerate(permutation):
        output[physical] = positive[x ^ flip]
    return output


def dense_ideal(values, width, directions, sign):
    """Independent dense kernel, with Gaussian integer coefficient products."""
    size = len(values)
    depth = len(directions)
    output = []
    for x in range(size):
        real, imag = Q(0), Q(0)
        for choices in range(1 << depth):
            y, cr, ci = x, 1, 0
            for j, q in enumerate(directions):
                bit = (choices >> j) & 1
                y ^= (q << (width * j)) if bit else 0
                phase = -sign if bit else sign
                cr, ci = cr - phase * ci, ci + phase * cr
            vr, vi = values[y]
            real += cr * vr - ci * vi
            imag += cr * vi + ci * vr
        output.append((real / (1 << depth), imag / (1 << depth)))
    return output


def norm_squared(values):
    return sum((r * r + i * i for r, i in values), Q(0))


def error_squared(actual, ideal):
    return sum(
        (
            (a - b) ** 2
            for x, y in zip(actual, ideal, strict=True)
            for a, b in zip(x, y, strict=True)
        ),
        Q(0),
    )


def floor_log2(value):
    need(value > 0, "positive block maximum")
    exponent = value.numerator.bit_length() - value.denominator.bit_length()
    if value < power2(exponent):
        exponent -= 1
    need(power2(exponent) <= value < power2(exponent + 1), "block exponent bracket")
    return exponent


def relative_step(values, width, depth, bits):
    need(type(bits) is int and 0 <= bits <= 512, "precision capacity")
    maximum = max(abs(t) for z in values for t in z)
    if maximum == 0:
        return Q(1)
    padding = (depth - 1).bit_length() + (width * depth) // 2
    return power2(floor_log2(maximum) - bits - padding)


def authenticate():
    metadata = json.loads((HERE / "SOURCES.json").read_text())
    records = metadata["predecessors"]
    expected = {"source/WORD.json", "source/LINE-PROOF.md", "source/DEFECT-PROOF.md"}
    need(
        {r["local_path"] for r in records} == expected and len(records) == 3,
        "source inventory",
    )
    payloads = {}
    for row in records:
        raw = (HERE / row["local_path"]).read_bytes()
        need(len(raw) <= 150000, "source capacity")
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "source SHA256")
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        need(hashlib.sha1(blob).hexdigest() == row["git_blob"], "source Git blob")
        payloads[row["local_path"]] = raw
    return payloads


def source_contract(payloads):
    word = json.loads(payloads["source/WORD.json"])
    need(isinstance(word, list) and len(word) == 3823, "literal source word")
    lines = [e for e in word if e[0] == "line"]
    need(len(lines) == 336, "line occurrence count")
    need(
        all(
            len(e) == 4 and 0 <= e[2] < 112 and type(e[3]) is int and e[3] in (-1, 1)
            for e in lines
        ),
        "line occurrence binding",
    )
    need(
        not any(
            e[0] in ("stage", "line", "map", "add", "clear") and e[1][0] in ("X", "Y")
            for e in word
        ),
        "read-only borrowed fields",
    )
    proof = payloads["source/DEFECT-PROOF.md"].decode()
    need(
        "2^(-b-22)" in proof and "2919388" in proof and "199144" in proof,
        "consumed guard contract",
    )
    need(2919388 + 199144 < 1 << 22, "strict uniform feedback margin")
    return {
        "events": len(word),
        "signed_lines": len(lines),
        "positive": sum(e[3] == 1 for e in lines),
        "negative": sum(e[3] == -1 for e in lines),
    }


def kernel_fixtures():
    checks = 0
    for width in range(1, 5):
        size = 1 << width
        for q in range(1, size):
            for sign in (-1, 1):
                for basis in range(2 * size):
                    values = [ZERO] * size
                    values[basis // 2] = (Q(basis % 2 == 0), Q(basis % 2 == 1))
                    expected = dense_ideal(values, width, [q], sign)
                    actual = wrapped_line(values, width, [q], sign, Q(1, 2))
                    need(actual == expected, "signed wrapped basis column")
                    need(norm_squared(actual) == 1, "unitary basis norm")
                    checks += 1
    return checks


def rounded_fixtures():
    checks, relative_checks = 0, 0
    for width, depth, sign in itertools.product(range(1, 4), range(1, 4), (-1, 1)):
        size = 1 << (width * depth)
        directions = [1 + (j % ((1 << width) - 1)) for j in range(depth)]
        values = [
            (Q((7 * k) % 17 - 8, 16), Q((11 * k) % 19 - 9, 32)) for k in range(size)
        ]
        ideal = dense_ideal(values, width, directions, sign)
        need(norm_squared(ideal) == norm_squared(values), "tensor unitarity")
        for exponent in (-1, 0, 2, 5):
            step = power2(-exponent)
            actual = paired_line(values, width, directions, sign, step)
            need(
                actual == wrapped_line(values, width, directions, sign, step),
                "rounded wrapper equivalence",
            )
            bound_squared = Q(depth * depth * size, 2) * step * step
            need(
                error_squared(actual, ideal) <= bound_squared,
                "absolute tensor rounding bound",
            )
            checks += 1
        for bits in (0, 3, 22, 25):
            # Keep input dust below the chosen output grid, even at 22 bits.
            padding = (depth - 1).bit_length() + (width * depth) // 2
            fine = list(values)
            fine[0] = (fine[0][0] + power2(-bits - padding - 9), fine[0][1])
            fine_ideal = dense_ideal(fine, width, directions, sign)
            step = relative_step(fine, width, depth, bits)
            actual = paired_line(fine, width, directions, sign, step)
            error = error_squared(actual, fine_ideal)
            need(error > 0, "relative fixture must exercise actual rounding")
            need(
                error <= power2(-2 * bits) * norm_squared(fine),
                "state-relative line bound",
            )
            relative_checks += 1
    return checks, relative_checks


def controls():
    values = [(Q(1), Q(0)), ZERO]
    ideal = dense_ideal(values, 1, [1], 1)
    need(paired_line(values, 1, [1], -1, Q(1, 2)) != ideal, "wrong-sign control")
    need(values != ideal, "omitted-factor control")
    error = error_squared(paired_line(values, 1, [1], 1, Q(1)), ideal)
    need(
        error == norm_squared(values),
        "fixed absolute grid loses its smallest grid input",
    )
    need(
        error > Q(1, 4) * norm_squared(values), "fixed-grid relative inference rejects"
    )
    need(
        [round_even(Q(n, 2), Q(1)) for n in (-5, -3, -1, 1, 3, 5)]
        == [-2, -2, 0, 0, 2, 2],
        "signed ties-to-even",
    )
    need(
        [floor_log2(x) for x in (Q(1, 8), Q(3, 8), Q(1), Q(3), Q(7), Q(1, 3))]
        == [-3, -2, 0, 1, 2, -2],
        "block exponent boundary controls",
    )
    zeros = [ZERO] * 4
    need(
        paired_line(zeros, 1, [1, 1], 1, relative_step(zeros, 1, 2, 22)) == zeros,
        "zero block",
    )
    need(relative_step([(Q(1), Q(0)), ZERO], 1, 1, 22) == power2(-22), "guard scale")
    # Rounding 3/4 down to zero violates the nearest-grid delta/2 bound.
    need((Q(3, 4) - Q(0)) ** 2 > Q(1, 4), "floor-instead-of-nearest rounding rejects")
    rejected = 0
    for width, directions, sign in (
        (0, [1], 1),
        (1, [0], 1),
        (1, [1], 0),
        (12, [1, 1], 1),
    ):
        try:
            paired_line(values, width, directions, sign, Q(1))
        except ValueError:
            rejected += 1
    need(rejected == 4, "capacity and parameter controls")
    return 9 + rejected


def result():
    source = source_contract(authenticate())
    basis = kernel_fixtures()
    absolute, relative = rounded_fixtures()
    negative = controls()
    return {
        "source": source,
        "basis_columns": basis,
        "rounded_tensor_cases": absolute,
        "relative_tensor_cases": relative,
        "relative_cases_with_nonzero_error": relative,
        "controls": negative,
        "absolute_bound_squared": "depth^2 * D * step^2 / 2",
        "relative_padding": "ceil(log2(depth)) + floor(log2(D)/2)",
        "guard_bits": 22,
        "scope": "direct local line implementation; no recursive cost or supplier admission",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-result", action="store_true", help="create RESULT.json exclusively"
    )
    args = parser.parse_args()
    actual = result()
    rendered = json.dumps(actual, indent=2, sort_keys=True) + "\n"
    target = HERE / "RESULT.json"
    if args.write_result:
        with target.open("x", encoding="utf-8") as handle:
            need(handle.write(rendered) == len(rendered), "complete receipt write")
    else:
        expected = json.loads(target.read_text())
        need(
            json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "complete typed receipt",
        )
    print("PASS_QQ16_ROUNDED_NATIVE_LINE " + json.dumps(actual, sort_keys=True))


if __name__ == "__main__":
    main()
