#!/usr/bin/env python3
"""Fixed-grid Gaussian engine and Walsh target, sharing source dispatch and bound."""

import json
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
V = types.ModuleType("scoped_helper_certificate")
V.__file__ = str(HERE / "verify.py")
exec(compile((HERE / "verify.py").read_bytes(), V.__file__, "exec"), V.__dict__)
DIM, HELPER = V.DIM, V.HELPER
need = V.need


def canonical(real, imag, exponent):
    nonzero = [abs(x) for x in real + imag if x]
    if not nonzero:
        return (0,) * DIM, (0,) * DIM, 0
    shift = min(exponent, min((x & -x).bit_length() - 1 for x in nonzero))
    return (
        tuple(x >> shift for x in real),
        tuple(x >> shift for x in imag),
        exponent - shift,
    )


def butterfly(values):
    result = list(values)
    for axis in range(9):
        step = 1 << axis
        for base in range(0, DIM, step * 2):
            for j in range(base, base + step):
                x, y = result[j], result[j + step]
                result[j], result[j + step] = x + y, x - y
    return result


def walsh_expected(entry):
    """W^-1 diag(i^weight) W, without the native line implementation."""
    transformed = butterfly(entry)
    real, imag = [0] * DIM, [0] * DIM
    for j, value in enumerate(transformed):
        phase = j.bit_count() % 4
        if phase % 2:
            imag[j] = value if phase == 1 else -value
        else:
            real[j] = value if phase == 0 else -value
    return canonical(tuple(butterfly(real)), tuple(butterfly(imag)), 9)


class FixedGrid:
    def __init__(self, entry, quantum):
        self.quantum = quantum
        self.zero = ((0,) * DIM, (0,) * DIM)
        self.entry = (tuple(x << quantum for x in entry), (0,) * DIM)
        self.calls = 0
        self.event = None

    def constant(self, _value):
        self.calls += 1
        need(self.calls <= 2, "Fixed-grid initialization bound")
        return self.zero if self.calls == 1 else self.entry

    def canonical(self, value):
        return canonical(*value, self.quantum)

    def scalar(self, value, numerator, denominator, _stage):
        rows = []
        for row in value:
            need(
                all((numerator * x) % denominator == 0 for x in row),
                "Exact fixed-grid scalar division",
            )
            rows.append(tuple(numerator * x // denominator for x in row))
        return tuple(rows)

    def add(self, left, right):
        return tuple(
            tuple(a + b for a, b in zip(x, y, strict=True))
            for x, y in zip(left, right, strict=True)
        )

    def mono(self, value, key, adjoint=False):
        matrix, quadratic, linear, offset, phase = key
        real, imag = [0] * DIM, [0] * DIM
        for x in range(DIM):
            dest = offset
            angle = phase
            for j in range(9):
                dest ^= ((matrix[j] & x).bit_count() % 2) << j
                if (x >> j) & 1:
                    angle += linear[j]
                    angle += 2 * (quadratic[j] & x & ~((1 << (j + 1)) - 1)).bit_count()
            src, dst = (dest, x) if adjoint else (x, dest)
            angle = (-angle if adjoint else angle) % 4
            a, b = value[0][src], value[1][src]
            real[dst], imag[dst] = ((a, b), (-b, a), (-a, -b), (b, -a))[angle]
        return tuple(real), tuple(imag)

    def line(self, value, axis):
        real, imag = [0] * DIM, [0] * DIM
        for x in range(DIM):
            y = x ^ axis
            a, b = value[0][x], value[1][x]
            c, d = value[0][y], value[1][y]
            r, i = a - b + c + d, b + a + d - c
            need(r % 2 == 0 and i % 2 == 0, "Exact fixed-grid line division")
            real[x], imag[x] = r // 2, i // 2
        return tuple(real), tuple(imag)

    def recipe(self, value, record, axes=9):
        def key(part):
            data = record[part]
            need(len(data["matrix_rows"]) == axes, "Recipe factor width")
            need(
                data["matrix_rows"][9:] == [1 << j for j in range(9, axes)],
                "Identity spectators",
            )
            return (
                tuple(data["matrix_rows"][:9]),
                tuple(data["quadratic_rows"][:9]),
                tuple(data["linear_Z4"][:9]),
                data["offset"],
                data["phase"],
            )

        if record["rank"]:
            value = self.mono(value, key("right"))
            for j in range(record["rank"]):
                value = self.line(value, 1 << j)
        return self.mono(value, key("left"))

    def report(self):
        return []


def audit():
    v = V.authenticated_source()
    data = v.load()
    _peak, guard, bits = V.coefficient_bound(v, data)
    entry = [1 << (bits * j) for j in range(DIM)]
    engine = FixedGrid(entry, guard + 9)
    state, faults, _cuts = v.run(data, engine=engine)
    need(engine.calls == 2 and not faults, "Fixed-grid execution completes")
    zero = ((0,) * DIM, (0,) * DIM, 0)
    need(
        all(value == zero for j, value in enumerate(state) if j != HELPER),
        "Independent no-leakage check",
    )
    expected = walsh_expected(entry)
    need(state[HELPER] == expected, "Literal native execution equals Walsh operator")
    receipt = json.loads((HERE / "RESULT.json").read_text())
    need(
        V.vector_hash(expected) == receipt["packed_endpoint_sha256"],
        "Packed endpoint hash",
    )
    need(
        [sum(x.bit_count() % 4 == k for x in range(DIM)) for k in range(4)]
        == receipt["eigenvalue_multiplicities_1_i_minus1_minusi"],
        "Eigenspace receipt",
    )
    print("PASS_QQ16_HELPER_FIXED_GRID_WALSH all_512_columns other_711_outputs_zero")


if __name__ == "__main__":
    audit()
