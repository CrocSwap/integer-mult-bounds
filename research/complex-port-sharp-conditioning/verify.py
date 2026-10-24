#!/usr/bin/env python3
"""Exact new Gram-spectrum certificates for the full-input complex port.

No predecessor verifier is imported or replayed. Matrices have Gaussian-integer
entries. Fixed widths 1, 2, 3 give at most 1,024 rows.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ZERO = (0, 0)
ONE = (1, 0)
PHASES = (ONE, (0, 1), (-1, 0), (0, -1))
MAX_ROWS = 1024


def require(ok, message):
    if not ok:
        raise ValueError(message)


def plus(a, b):
    return (a[0] + b[0], a[1] + b[1])


def times(a, b):
    return (a[0] * b[0] - a[1] * b[1],
            a[0] * b[1] + a[1] * b[0])


def put(row, column, value):
    value = plus(row.get(column, ZERO), value)
    if value == ZERO:
        row.pop(column, None)
    else:
        row[column] = value


def eye(n):
    require(1 <= n <= MAX_ROWS, "matrix capacity")
    return [{j: ONE} for j in range(n)]


def add(a, b, coefficient=1):
    require(len(a) == len(b), "addition dimensions")
    out = [dict(row) for row in a]
    for row, source in zip(out, b):
        for column, z in source.items():
            put(row, column, (coefficient * z[0], coefficient * z[1]))
    return out


def product(a, b):
    n = len(a)
    require(n == len(b) and n <= MAX_ROWS, "product dimensions")
    out = [{} for _ in range(n)]
    for r, row in enumerate(a):
        for k, x in row.items():
            for c, y in b[k].items():
                put(out[r], c, times(x, y))
    return out


def adjoint(a):
    out = [{} for _ in a]
    for r, row in enumerate(a):
        for c, z in row.items():
            out[c][r] = (z[0], -z[1])
    return out


def monomial(width, branch):
    """Build S U S or S V S, tensorizing each actual base letter."""
    require(width in (1, 2, 3), "width domain")
    require(branch in (0, 1), "branch domain")
    n = 8 ** width
    out = [{} for _ in range(n)]
    for column in range(n):
        remaining, address, exponent = column, 0, 0
        for digit_index in range(width):
            digit = remaining % 8
            remaining //= 8
            if branch == 0:
                image = digit ^ ((digit & 1) << 2)
            else:
                image = (digit & 4) | ((digit & 1) << 1) | ((digit & 2) >> 1)
            address += image * 8 ** digit_index
            exponent += digit.bit_count() + image.bit_count()
        out[address][column] = PHASES[exponent % 4]
    require(all(len(row) == 1 for row in out), "monomial bijection")
    return out


def shear(coupling):
    n = len(coupling)
    out = eye(2 * n)
    for r, row in enumerate(coupling):
        for c, z in row.items():
            put(out[n + r], c, z)
    return out


def spectrum_check(coupling, expected):
    """Verify exact squared singular values and projector multiplicities."""
    n = len(coupling)
    ident = eye(n)
    gram = product(adjoint(coupling), coupling)
    annihilator = ident
    counts = {}
    for d in (1, 5, 9):
        annihilator = product(annihilator, add(gram, ident, -d))
        numerator, denominator = ident, 1
        for other in (1, 5, 9):
            if other != d:
                numerator = product(numerator, add(gram, ident, -other))
                denominator *= d - other
        trace = ZERO
        for j in range(n):
            trace = plus(trace, numerator[j].get(j, ZERO))
        require(trace[1] == 0 and trace[0] % denominator == 0,
                "spectral projector trace")
        counts[d] = trace[0] // denominator
    require(all(not row for row in annihilator), "squared-spectrum polynomial")
    require(counts == expected and sum(counts.values()) == n,
            "squared-spectrum multiplicities")
    return counts


def port_check(coupling):
    """Check the new Gram polynomial and both inverse orders."""
    n = len(coupling)
    port, ident = shear(coupling), eye(2 * n)
    gram = product(adjoint(port), port)
    annihilator = ident
    for d in (1, 5, 9):
        factor = add(add(product(gram, gram), gram, -(d + 2)), ident)
        annihilator = product(annihilator, factor)
    require(all(not row for row in annihilator), "port Gram polynomial")
    inverse = add(eye(2 * n), add(port, eye(2 * n), -1), -1)
    require(product(port, inverse) == ident, "shear inverse")
    require(product(inverse, port) == ident, "reverse shear inverse")
    return gram


def apply(a, vector):
    out = []
    for row in a:
        value = ZERO
        for c, z in row.items():
            value = plus(value, times(z, vector[c]))
        out.append(value)
    return out


def sharp_sector(width, p, gram):
    n = 8 ** width
    v = []
    for address in range(n):
        exponent, remaining = 0, address
        for _ in range(width):
            exponent += (remaining % 8).bit_count()
            remaining //= 8
        v.append(PHASES[-exponent % 4])
    left = v + [ZERO] * n
    right = [ZERO] * n + apply(p, v)
    image_left, image_right = apply(gram, left), apply(gram, right)
    for j in range(2 * n):
        require(image_left[j] == plus(times((10, 0), left[j]),
                                     times((3, 0), right[j])), "sharp first column")
        require(image_right[j] == plus(times((3, 0), left[j]), right[j]),
                "sharp second column")


def rejects(operation):
    try:
        operation()
    except ValueError:
        return
    raise ValueError("negative control was accepted")


def verify():
    records = []
    for width in (1, 2, 3):
        p, q = monomial(width, 0), monomial(width, 1)
        coupling = add(p, q, 2)
        positive = (8 ** width + 4 ** width + 2 * 2 ** width) // 4
        negative = (8 ** width + 4 ** width - 2 * 2 ** width) // 4
        imaginary = (8 ** width - 4 ** width) // 2
        counts = spectrum_check(coupling, {1: negative, 5: imaginary, 9: positive})
        sharp_sector(width, p, port_check(coupling))
        records.append({"width": width, "port_rows": 2 * 8 ** width,
                        "squared_coupling_multiplicities": counts})
    p, q = monomial(1, 0), monomial(1, 1)
    rejects(lambda: spectrum_check(add(p, q), {1: 2, 5: 2, 9: 4}))
    rejects(lambda: spectrum_check(add(p, q, 2), {1: 4, 5: 2, 9: 2}))
    wrong = shear(add(p, q, 2))
    rejects(lambda: require(product(wrong, shear(add(p, q, 2))) == eye(16),
                            "wrong inverse"))
    rejects(lambda: monomial(4, 0))
    rejects(lambda: monomial(1, 2))
    # The larger root of t^2-11t+1 lies strictly between 10 and 11.
    require(10 * 10 - 11 * 10 + 1 < 0 < 11 * 11 - 11 * 11 + 1,
            "sharp condition interval")
    rejects(lambda: require(10 * 10 - 11 * 10 + 1 >= 0, "false cap ten"))
    return {"status": "PASS_COMPLEX_PORT_SHARP_CONDITIONING",
            "condition_number": "(11+3*sqrt(13))/2", "domains": records,
            "controls": 6}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    result = verify()
    package = Path(__file__).resolve().parent
    names = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    result["sha256"] = {
        name: hashlib.sha256((package / name).read_bytes()).hexdigest()
        for name in names
    }
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.receipt is not None:
        args.receipt.write_text(output)
    print(output, end="")


if __name__ == "__main__":
    main()
