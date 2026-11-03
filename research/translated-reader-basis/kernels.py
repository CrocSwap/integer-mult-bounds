"""Reconstruct supplied reader factors, following Ali Romman PR5646. Apache-2.0.

The factor formulas and published basis are predecessor inputs. This module
constructs their kernels for a translated dyadic basis; it does not audit the source.
Adapted from Nick Petalas PR5919, retaining the PR5646 factor reconstruction.
"""
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/centre-code-services/frozen/'
RESPONSE = SOURCE + ('lanes/new-core-transfer-20261017/low-displacement-20261020/'
                     'run-normal/RESPONSE-PROGRAM.json')
DIRECTIONS = SOURCE + ('lanes/history-encoding/independent-skeleton-20261018/'
                       'fresh-three-child/FRESH-THREE-CHILD-PROGRAMS.json.gz')
BLOCKS = SOURCE + 'root/RANK30-PHASE-SECTION-BLOCKS-20261020.json.gz'
BASIS = 'research/actual-gaussian-reader-tariff/BASIS.json'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_json(path):
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    matches = [x for x in manifest['files'] if x['path'] == path]
    require(len(matches) == 1, 'unique source pin')
    raw = (ROOT / path).read_bytes()
    require(len(raw) <= 16 * 1024 * 1024, 'source byte bound')
    require(sha256(raw).hexdigest() == matches[0]['sha256'], 'source hash: ' + path)
    if path.endswith('.gz'):
        raw = gzip.decompress(raw)
    require(len(raw) <= 16 * 1024 * 1024, 'decoded source byte bound')
    return json.loads(raw)


def sparse_add(left, right, coefficient):
    require(len(left) <= 57344 and len(right) <= 57344, 'kernel support bound')
    result = {}
    for key in left.keys() | right.keys():
        value = left.get(key, 0) + coefficient * right.get(key, 0)
        if value:
            result[key] = value
    require(len(result) <= 57344, 'result support bound')
    return result


def walsh(values):
    require(len(values) == 512, 'nine-axis character table')
    result = values[:]
    for width in (1, 2, 4, 8, 16, 32, 64, 128, 256):
        for first in range(0, 512, 2 * width):
            for index in range(first, first + width):
                left, right = result[index], result[index + width]
                result[index], result[index + width] = left + right, left - right
    return result


def inverse_times_reader(records, reader):
    require(len(records) == 512 and len(reader) == 30, 'source matrix dimensions')
    result = []
    for record in records:
        inverse = [[Fraction(0)] * 30 for _ in range(30)]
        for row in range(16):
            for column in range(16):
                inverse[row][column] = 60 * Fraction(record['large_inverse'][row][column])
        for row in range(16, 30):
            inverse[row][row] = 60 / Fraction(record['small_diagonal'][row - 16])
        values = [[0] * 112 for _ in range(30)]
        for row in range(30):
            for column, coefficient in enumerate(inverse[row]):
                if coefficient:
                    for port, value in reader[column].items():
                        scaled = coefficient * value
                        require(scaled.denominator == 1, 'supplied inverse scale')
                        values[row][port] += int(scaled)
        result.append(values)
    return result


def supplied_factors():
    response = source_json(RESPONSE)
    raw_u, raw_v = response['correction_U'], response['correction_V']
    require(len(raw_u) == 112 and len(raw_v) == 30, 'response dimensions')
    source = [{int(k): Fraction(c) for k, c in row.items()} for row in raw_u]
    reader = [{int(k): Fraction(c) for k, c in row.items()} for row in raw_v]
    directions = [row['q'] for row in source_json(DIRECTIONS)['transfers']]
    require(len(directions) == 112, 'port directions')
    require(all(type(q) is int and 0 <= q < 512 for q in directions), 'direction range')
    values = inverse_times_reader(source_json(BLOCKS)['characters'], reader)
    kernels = []
    for row in range(30):
        kernel = {}
        for port in range(112):
            spectrum = [values[0][row][port] * (1 - 2 * ((chi & directions[port]).bit_count() % 2))
                        - values[chi][row][port] for chi in range(512)]
            transformed = walsh(spectrum)
            kernel.update({512 * port + shift: Fraction(c, 30720)
                           for shift, c in enumerate(transformed) if c})
        kernels.append(kernel)
    columns = [{port: row[column] for port, row in enumerate(source) if column in row}
               for column in range(30)]
    operations = source_json(BASIS)['operations']
    require(len(operations) == 10, 'published basis length')
    for left, right, coefficient in operations:
        change_basis(columns, kernels, left, right, Fraction(coefficient))
    return columns, kernels, directions


def change_basis(source, reader, left, right, coefficient):
    require(len(source) == len(reader) == 30, 'basis dimension')
    require(type(left) is int and type(right) is int, 'basis index types')
    require(0 <= left < 30 and 0 <= right < 30 and left != right, 'basis indices')
    require(isinstance(coefficient, Fraction), 'exact basis coefficient')
    reader[right] = sparse_add(reader[right], reader[left], coefficient)
    source[left] = sparse_add(source[left], source[right], -coefficient)
