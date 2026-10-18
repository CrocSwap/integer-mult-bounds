# SPDX-License-Identifier: Apache-2.0
"""Uncancelled signed-path expansion, rather than a sparse matrix replay."""

from dataclasses import dataclass, replace

from source import BITS, MAX_GATES, Gate, require

MAX_PATHS = 4096
MAX_PHASE_TERMS = BITS * (BITS + 1) // 2


def parity_polynomial(axis: int) -> tuple[tuple[int, int], ...]:
    require(type(axis) is int and 0 <= axis < 1 << BITS, "parity axis bound")
    bits = [1 << i for i in range(BITS) if axis >> i & 1]
    terms = [(bit, 1) for bit in bits]
    terms.extend((left | right, 2) for i, left in enumerate(bits) for right in bits[i + 1:])
    return tuple(sorted(terms))


def combine(left: tuple, right: tuple, scalar: int = 1) -> tuple:
    result = dict(left)
    for monomial, coefficient in right:
        result[monomial] = (result.get(monomial, 0) + scalar * coefficient) % 4
    result = {key: value for key, value in result.items() if value}
    require(len(result) <= MAX_PHASE_TERMS, "quadratic phase capacity")
    return tuple(sorted(result.items()))


def gate_exponent(gate: Gate) -> tuple:
    result = ()
    for axis, coefficient in gate.phases:
        result = combine(result, parity_polynomial(axis), coefficient)
    return result


@dataclass(frozen=True)
class Path:
    origin: int
    sign: int = 1
    variables: int = 0
    exponent: tuple = ()


def expand(gates: list[Gate]) -> tuple[list, int, int]:
    require(len(gates) <= MAX_GATES, "primitive gate capacity")
    streams = [[Path(i)] for i in range(8)]
    peak = 8
    for gate in gates:
        row = gate.row
        require(0 <= row < 8, "primitive row")
        if gate.kind == "phase":
            exponent = gate_exponent(gate)
            bit = 0 if gate.site < 0 else 1 << gate.site
            changed = []
            for path in streams[row]:
                require(not path.variables & bit, "repeated variable along a path")
                changed.append(replace(path, variables=path.variables | bit,
                                       exponent=combine(path.exponent, exponent)))
            streams[row] = changed
        elif gate.kind == "add":
            require(0 <= gate.source < 8 and gate.source != row, "primitive add rows")
            require(gate.coefficient in (-1, 1), "primitive add sign")
            count = sum(map(len, streams)) + len(streams[gate.source])
            require(count <= MAX_PATHS, "uncancelled path capacity")
            streams[row] = streams[row] + [replace(path, sign=gate.coefficient * path.sign)
                                          for path in streams[gate.source]]
        elif gate.kind == "exchange":
            require(gate.source == row + 1 and row % 2 == 0, "signed exchange rows")
            x, y = streams[row], streams[gate.source]
            streams[row] = y
            streams[gate.source] = [replace(path, sign=-path.sign) for path in x]
        else:
            raise ValueError("unknown primitive gate")
        peak = max(peak, sum(map(len, streams)))
    return streams, peak, sum(map(len, streams))


def collect(streams: list, q: int) -> list[list[int]]:
    require(len(streams) == 8, "stream count")
    grouped = {}
    for row, paths in enumerate(streams):
        require(len(paths) <= MAX_PATHS, "output path bound")
        for path in paths:
            key = row, path.origin, path.variables, path.exponent
            grouped[key] = grouped.get(key, 0) + path.sign
    g = combine((), parity_polynomial(q), -1)
    rows = []
    for (row, column, mask, exponent), coefficient in grouped.items():
        if not coefficient:
            continue
        require(exponent in ((), g), "unexpected complete character polynomial")
        rows.append([row, column, mask, -1 if exponent == g else 0, coefficient])
    return sorted(rows)
