#!/usr/bin/env python3
"""Exact bounded corroboration of the heavy tensor dimension theorem."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
MAX_BYTES = 2 * 1024 * 1024
MAX_P = 2**20
SERIES_TERMS = 32
LOCAL_SOURCES = ('README.md', 'TASK.json', 'SOURCES.json', 'VERIFY.json', 'verify.py')


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def integer(value: int, low: int, high: int) -> None:
    require(type(value) is int and low <= value <= high, 'integer outside bounds')


def read_bytes(path: Path) -> bytes:
    require(path.stat().st_size <= MAX_BYTES, 'file exceeds resource bound')
    data = path.read_bytes()
    require(len(data) <= MAX_BYTES, 'file grew beyond resource bound')
    return data


def ln_unit(x: Q, terms: int = SERIES_TERMS) -> tuple[Q, Q]:
    require(type(x) is Q and 1 <= x <= 2, 'logarithm range reduction failed')
    integer(terms, 1, 64)
    z = (x - 1) / (x + 1)
    power = z
    total = Q(0)
    for j in range(terms):
        total += 2 * power / (2 * j + 1)
        power *= z * z
    tail = 2 * power / ((2 * terms + 1) * (1 - z * z))
    require(0 <= tail, 'negative logarithm tail')
    return total, total + tail


def ln_integer(n: int, terms: int = SERIES_TERMS) -> tuple[Q, Q]:
    integer(n, 1, 2**41)
    k = n.bit_length() - 1
    low, high = ln_unit(Q(n, 2**k), terms)
    two_low, two_high = ln_unit(Q(2), terms)
    return low + k * two_low, high + k * two_high


def log_budget(p: int, g: int, k: int, c: int) -> tuple[Q, Q]:
    integer(p, 2, MAX_P)
    integer(g, 1, p * p + 1)
    integer(k, 0, MAX_P)
    integer(c, 0, MAX_P)
    gl, gu = ln_integer(g)
    pl, pu = ln_integer(p)
    tl, tu = ln_unit(1 + Q(1, p**4))
    bl, bu = ln_integer(2)
    constant = k * p - p * p
    low = gl + 10 * g * pl + tl + c * p * bl + constant
    high = gu + 10 * g * pu + tu + c * p * bu + constant
    require(low <= high, 'inverted logarithm interval')
    return low, high


def budget_sign(p: int, g: int, k: int, c: int) -> int:
    low, high = log_budget(p, g, k, c)
    if high < 0:
        return -1
    if low > 0:
        return 1
    raise ValueError('logarithm interval does not decide strict sign')


def last_dimension(p: int, k: int, c: int) -> int:
    integer(p, 2, MAX_P)
    integer(k, 0, MAX_P)
    integer(c, 0, MAX_P)
    low, high = 0, p * p + 1
    require(budget_sign(p, high, k, c) == 1, 'upper bracket failed')
    for _ in range(42):
        if high - low == 1:
            return low
        mid = (low + high) // 2
        if budget_sign(p, mid, k, c) < 0:
            low = mid
        else:
            high = mid
    raise ValueError('bounded dimension search exhausted')


def gate_dimension(p: int, k: int, c: int) -> int:
    integer(p, 2, MAX_P)
    integer(k, 0, MAX_P)
    integer(c, 0, MAX_P)
    level = (p - 1).bit_length()
    numerator = p * p - 2 * level - 1 - (2 * k + c) * p
    return max(0, numerator // (10 * level))


def exp_one_bounds() -> tuple[Q, Q]:
    total = Q(1)
    term = Q(1)
    for n in range(1, 13):
        term /= n
        total += term
    first_omitted = term / 13
    return total, total + first_omitted * Q(14, 13)


def direct_power_sign(p: int, g: int) -> int:
    integer(p, 2, 64)
    integer(g, 1, p * p + 1)
    low, high = exp_one_bounds()
    envelope = g * p ** (10 * g) * (1 + Q(1, p**4))
    if envelope < low ** (p * p):
        return -1
    if envelope > high ** (p * p):
        return 1
    raise ValueError('independent e-power interval undecided')


def rounded_interval(p: int, g: int, k: int, c: int) -> list[str]:
    low, high = log_budget(p, g, k, c)
    return [str(Q((1000 * low).__floor__(), 1000)),
            str(Q((1000 * high).__ceil__(), 1000))]


def boundary_cases() -> tuple[list[dict], int]:
    rows = []
    gate_checks = 0
    dimensions = tuple(range(2, 65)) + (84, 128, 256, 1024, 4096, 65536)
    for p in dimensions:
        for k, c in ((0, 0), (1, 2), (7, 3)):
            last = last_dimension(p, k, c)
            success = rounded_interval(p, last, k, c) if last else None
            failure = rounded_interval(p, last + 1, k, c)
            require(Q(failure[0]) > 0, 'failure not certified')
            if success is not None:
                require(Q(success[1]) < 0, 'success not certified')
            gate = gate_dimension(p, k, c)
            require(gate <= last, 'integer gate exceeded exact boundary')
            if gate:
                require(budget_sign(p, gate, k, c) < 0, 'integer gate fails')
                gate_checks += 1
            rows.append(dict(p=p, K=k, C=c, maximum=last,
                             success_log=success, next_log=failure, gate=gate))
    return rows, gate_checks


def semantic_controls() -> int:
    rejected = 0
    cases = ((1, 1, 0, 0), (True, 1, 0, 0), (2, 0, 0, 0),
             (2, 6, 0, 0), (2, 1, -1, 0), (2, 1, 0, -1),
             (MAX_P + 1, 1, 0, 0), (2, 1, 0, MAX_P + 1))
    for args in cases:
        try:
            log_budget(*args)
        except ValueError:
            rejected += 1
    require(rejected == len(cases), 'invalid input accepted')
    for x, terms in ((Q(3), 32), (Q(0), 32), (Q(2), 0), (Q(2), 65)):
        try:
            ln_unit(x, terms)
        except ValueError:
            rejected += 1
    require(rejected == 12, 'invalid series contract accepted')
    low, high = ln_integer(2)
    require(Q(69, 100) < low <= high < Q(7, 10), 'log base control failed')
    require(ln_integer(1) == (0, 0), 'log identity failed')
    require(gate_dimension(64, 0, 0) == 68, 'integer gate transcription')
    require(log_budget(64, 98, 0, 0)[1] < -15, 'success margin failed')
    require(log_budget(64, 99, 0, 0)[0] > 25, 'failure margin failed')
    return rejected + 5


def source_hashes() -> dict[str, str]:
    hashes = {name: hashlib.sha256(read_bytes(PACKAGE / name)).hexdigest()
              for name in LOCAL_SOURCES}
    manifest = json.loads(read_bytes(PACKAGE / 'SOURCES.json'))
    require(len(manifest['files']) <= 100, 'source row bound exceeded')
    for row in manifest['files']:
        if row['usage'] == 'input':
            data = read_bytes(ROOT / row['path'])
            digest = hashlib.sha256(data).hexdigest()
            require(digest == row['sha256'], 'live predecessor source changed')
            hashes[row['path']] = digest
    return hashes


def result() -> dict:
    hashes = source_hashes()
    controls = semantic_controls()
    rows, gates = boundary_cases()
    powers = 0
    for p in (2, 4, 8, 16, 32, 64):
        last = last_dimension(p, 0, 0)
        if last:
            require(direct_power_sign(p, last) == -1, 'direct success mismatch')
            powers += 1
        require(direct_power_sign(p, last + 1) == 1, 'direct failure mismatch')
        powers += 1
    selected = next(row for row in rows if (row['p'], row['K'], row['C']) == (64, 0, 0))
    require(selected['maximum'] == 98, 'first fixture maximum changed')
    return dict(schema_version=1, status='PASS_HEAVY_TENSOR_DIMENSION',
                source_sha256=hashes, series_terms=SERIES_TERMS,
                boundary_cases=len(rows), integer_gate_checks=gates,
                independent_power_comparisons=powers, semantic_controls=controls,
                boundaries=rows)


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-receipt', type=Path)
    args = parser.parse_args()
    actual = result()
    if args.write_receipt is not None:
        with args.write_receipt.open('x', encoding='utf-8') as out:
            out.write(json.dumps(actual, indent=2) + '\n')
    else:
        expected = json.loads(read_bytes(PACKAGE / 'RESULT.json'))
        require(canonical(expected) == canonical(actual), 'source-bound receipt mismatch')
    print('PASS_HEAVY_TENSOR_DIMENSION',
          f"boundaries={actual['boundary_cases']}",
          f"gates={actual['integer_gate_checks']}",
          f"power_comparisons={actual['independent_power_comparisons']}",
          f"controls={actual['semantic_controls']}")


if __name__ == '__main__':
    main()
