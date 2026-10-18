#!/usr/bin/env python3
"""Derive inverse rows from the ordered equations, without replaying WORD.json.

Paths are reduced words in free involutions. A left action prepends its token;
equal adjacent tokens cancel. Stage zero is the identity chart. The arena owns
all intermediate rows and clears them at their last use. Its entry cap bounds
live sparse storage even under Python's allocating arithmetic. It does not bound
Python's allocator overhead or the interpreter itself.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

PORTS = 112
QUERIES = 8
MAX_PATH = 4
MAX_ROW_TERMS = 50_000
MAX_LIVE_TERMS = 600_000
MAX_ROWS = 2_048
SOURCE_SHA256 = "a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7"
Key = tuple[int, tuple[int, ...]]
Polynomial = dict[Key, Fraction]
Vector = list[Polynomial]


class Arena:
    """Own all derivation dictionaries and reject capacity exhaustion."""

    def __init__(self) -> None:
        self.rows: list[Polynomial] = []
        self.terms = 0
        self.peak_terms = 0

    def new(self) -> Polynomial:
        if len(self.rows) >= MAX_ROWS:
            raise ValueError("independent polynomial-row capacity exhausted")
        row: Polynomial = {}
        self.rows.append(row)
        return row

    def add(self, row: Polynomial, key: Key, value: Fraction) -> None:
        previous = row.get(key, Fraction(0))
        updated = previous + value
        if updated:
            if not previous:
                if len(row) >= MAX_ROW_TERMS or self.terms >= MAX_LIVE_TERMS:
                    raise ValueError("independent sparse-term capacity exhausted")
                self.terms += 1
                self.peak_terms = max(self.peak_terms, self.terms)
            row[key] = updated
        elif previous:
            del row[key]
            self.terms -= 1

    def release(self, row: Polynomial) -> None:
        self.terms -= len(row)
        row.clear()
        assert self.terms >= 0


def _add(
    arena: Arena, target: Polynomial, source: Polynomial, scale: Fraction,
    stage: int = 0, port: int = 0,
) -> None:
    assert target is not source
    assert 0 <= stage <= 2 and 0 <= port < PORTS
    token = (stage - 1) * PORTS + port
    for (index, path), coefficient in source.items():
        if stage:
            path = path[1:] if path and path[0] == token else (token,) + path
        if len(path) > MAX_PATH:
            raise ValueError("independent route-path capacity exhausted")
        arena.add(target, (index, path), coefficient * scale)


def _combine(arena: Arena, terms: list[tuple[int, Polynomial]]) -> Polynomial:
    assert len(terms) <= 3
    result = arena.new()
    for scale, row in terms:
        _add(arena, result, row, Fraction(scale))
    return result


def _geometry(packet: dict[str, Any]) -> dict[str, Any]:
    groups = []
    for name, size in (("A_ports", 8), ("T_ports", 8), ("U_ports", 96)):
        values = packet.get(name)
        if (type(values) is not list or len(values) != size
                or any(type(port) is not int or not 0 <= port < PORTS
                       for port in values) or len(set(values)) != size):
            raise ValueError("invalid independent port partition")
        groups.append(tuple(values))
    if len(set(groups[0] + groups[1] + groups[2])) != PORTS:
        raise ValueError("independent port groups do not partition all ports")
    matrices = []
    for name, height, width, allowed in (
        ("R_rows", QUERIES, PORTS, {"-1", "1"}),
        ("K_rows", PORTS, QUERIES, {"-1/4", "1/4"}),
    ):
        source = packet.get(name)
        if type(source) is not list or len(source) != height:
            raise ValueError("invalid independent matrix height")
        rows = []
        for entries in source:
            if type(entries) is not dict or len(entries) > width:
                raise ValueError("invalid independent matrix row")
            row = {}
            for column, value in entries.items():
                if (type(column) is not str or not column.isdecimal()
                        or str(int(column)) != column or int(column) >= width
                        or type(value) is not str or value not in allowed):
                    raise ValueError("invalid independent matrix entry")
                row[int(column)] = Fraction(value)
            rows.append(row)
        matrices.append(rows)
    r_rows, k_rows = matrices
    for port in range(PORTS):
        for query in range(QUERIES):
            if k_rows[port].get(query, 0) != r_rows[query].get(port, Fraction(0)) / 4:
                raise ValueError("independent K is not R transpose divided by four")
    return {"A": groups[0], "T": groups[1], "U": groups[2], "R": r_rows, "K": k_rows}


def _query(
    arena: Arena, vector: Vector, stage: int, ports: tuple[int, ...],
    geometry: dict[str, Any],
) -> Vector:
    assert len(vector) == PORTS and len(ports) <= PORTS
    selected = set(ports)
    result = []
    for coefficients in geometry["R"]:
        row = arena.new()
        for port, scale in coefficients.items():
            if port in selected:
                _add(arena, row, vector[port], scale, stage, port)
        result.append(row)
    return result


def _section(
    arena: Arena, query: Vector, stage: int, port: int,
    geometry: dict[str, Any],
) -> Polynomial:
    assert len(query) == QUERIES
    result = arena.new()
    for component, scale in geometry["K"][port].items():
        _add(arena, result, query[component], scale, stage, port)
    return result


def _discard(arena: Arena, vectors: list[Vector]) -> None:
    assert len(vectors) <= 4
    for vector in vectors:
        assert len(vector) <= 2 * PORTS
        for row in vector:
            arena.release(row)


def _inverse_f0(
    arena: Arena, x: Vector, y: Vector, geometry: dict[str, Any],
) -> Vector:
    assert len(x) == len(y) == PORTS
    f = _query(arena, x, 0, geometry["T"], geometry)
    c = _query(arena, x, 0, geometry["A"], geometry)
    rw = _query(arena, x, 0, geometry["U"], geometry)
    a = [_combine(arena, [(-11, f[k]), (-1, rw[k]), (-1, c[k])])
         for k in range(QUERIES)]
    _discard(arena, [rw])
    original_x = []
    for port in range(PORTS):
        if port in geometry["U"]:
            section = _section(arena, f, 0, port, geometry)
            row = _combine(arena, [(1, x[port]), (1, section)])
            arena.release(section)
        else:
            selected = a if port in geometry["A"] else c
            row = _section(arena, selected, 0, port, geometry)
        original_x.append(row)
    _discard(arena, [f, c, a])
    original_y = []
    for port in range(PORTS):
        terms = [(1, y[port]), (-1, x[port])]
        if port not in geometry["U"]:
            terms = [(1, y[port]), (1, x[port]), (-1, original_x[port])]
        original_y.append(_combine(arena, terms))
    return original_x + original_y


def _inverse_b1(
    arena: Arena, x: Vector, y: Vector, geometry: dict[str, Any],
) -> tuple[Vector, Vector]:
    assert len(x) == len(y) == PORTS
    a = _query(arena, y, 1, tuple(range(PORTS)), geometry)
    u = []
    for port in range(PORTS):
        if port in geometry["A"]:
            row = _combine(arena, [(1, y[port])])
        else:
            ka = _section(arena, a, 1, port, geometry)
            terms = [(1, y[port]), (-1, ka)]
            if port in geometry["T"]:
                terms.append((1, x[port]))
            row = _combine(arena, terms)
            arena.release(ka)
        u.append(row)
    _discard(arena, [a])
    off_a = tuple(port for port in range(PORTS) if port not in geometry["A"])
    future_query = _query(arena, u, 2, off_a, geometry)
    previous_y = []
    for port in range(PORTS):
        terms = [(1, u[port])]
        if port in geometry["A"]:
            correction = _section(arena, future_query, 2, port, geometry)
            terms.append((-1, correction))
        previous_y.append(_combine(arena, terms))
        if port in geometry["A"]:
            arena.release(correction)
    _discard(arena, [u, future_query])
    previous_x = []
    for port in range(PORTS):
        terms = [(1, x[port]), (1, previous_y[port])]
        if port not in geometry["U"]:
            terms = [(1, x[port]), (1, y[port]), (-1, previous_y[port])]
        previous_x.append(_combine(arena, terms))
    return previous_x, previous_y


def derive(packet: dict[str, Any]) -> dict[str, Vector]:
    """Return F0 inverse and F0 inverse after B1 inverse on 224 inputs."""
    if type(packet) is not dict:
        raise ValueError("independent certificate root must be an object")
    geometry = _geometry(packet)
    arena = Arena()
    basis = []
    for index in range(2 * PORTS):
        row = arena.new()
        arena.add(row, (index, ()), Fraction(1))
        basis.append(row)
    x, y = basis[:PORTS], basis[PORTS:]
    f0 = _inverse_f0(arena, x, y, geometry)
    previous_x, previous_y = _inverse_b1(arena, x, y, geometry)
    decoder = _inverse_f0(arena, previous_x, previous_y, geometry)
    assert len(f0) == len(decoder) == 2 * PORTS
    return {"F0": f0, "D": decoder}


def _read(path: Path, limit: int) -> bytes:
    with path.open("rb") as stream:
        contents = stream.read(limit + 1)
    if len(contents) > limit:
        raise ValueError("independent input byte capacity exhausted")
    return contents


def _certificate(path: Path) -> dict[str, Any]:
    compressed = _read(path, 1 << 20)
    if hashlib.sha256(compressed).hexdigest() != SOURCE_SHA256:
        raise ValueError("independent certificate SHA256 mismatch")
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:
        decoded = stream.read((12 << 20) + 1)
    if len(decoded) > 12 << 20:
        raise ValueError("independent decompression capacity exhausted")
    result = json.loads(decoded)
    if type(result) is not dict:
        raise ValueError("independent certificate root must be an object")
    return result


def _summaries(rows: Vector) -> list[dict[str, Any]]:
    assert len(rows) == 2 * PORTS
    summaries = []
    for index, row in enumerate(rows):
        encoded = [[column, list(path), str(value)]
                   for (column, path), value in sorted(row.items())]
        digest = hashlib.sha256(
            json.dumps(encoded, separators=(",", ":")).encode()
        ).hexdigest()
        summaries.append({"row": index, "l1": str(sum(map(abs, row.values()))),
                          "terms": len(row), "sha256": digest})
    return summaries


def main() -> int:
    package = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path,
                        default=package.parent / "joint-query/certificate.json.gz")
    parser.add_argument("--result", type=Path, default=package / "RESULT.json")
    args = parser.parse_args()
    try:
        packet = _certificate(args.certificate)
        operators = derive(packet)
        expected = {name: _summaries(rows) for name, rows in operators.items()}
        result = json.loads(_read(args.result, 1 << 20))
        if type(result) is not dict:
            raise ValueError("independent result root must be an object")
        actual_json = json.dumps(result.get("operators"), sort_keys=True,
                                 separators=(",", ":"))
        expected_json = json.dumps(expected, sort_keys=True, separators=(",", ":"))
        if actual_json != expected_json:
            raise ValueError("independent operator summaries disagree")
    except (OSError, ValueError, TypeError, OverflowError) as error:
        print(f"FAIL_INDEPENDENT_QQ16_DEFECT_TRANSFER: {error}", file=sys.stderr)
        return 1
    print("PASS_INDEPENDENT_QQ16_DEFECT_TRANSFER")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
