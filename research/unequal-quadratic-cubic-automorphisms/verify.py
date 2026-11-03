#!/usr/bin/env python3
"""Construct all normal-form automorphisms of F_q[x,y]/(x^2,y^3)."""
import argparse
from collections import Counter
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
SOURCE_HASH = 'e9e770f3a98ed8366e254ad33c3970e95a77e255c95d6128ff6897e14b13cc41'
CASE_HASH = '0449dbb927e385e63a14d5c5366f65bd91a99a341c05e2a6373ea0de1e05bd0c'
BASIS = [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)]
PRODUCT = [[BASIS.index((a + c, b + d)) if a + c < 2 and b + d < 3 else -1
            for c, d in BASIS] for a, b in BASIS]
ZERO = [0] * 6
ONE = [1, 0, 0, 0, 0, 0]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def unique(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, 'duplicate JSON key: ' + key)
        value[key] = item
    return value


def reject_number(value):
    raise ValueError('nonfinite JSON number: ' + value)


def parse(raw):
    return json.loads(raw, object_pairs_hook=unique, parse_constant=reject_number)


def same_typed(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(same_typed(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(same_typed(x, y) for x, y in zip(a, b))
    return a == b


def authenticate():
    require(sha((ROOT / 'SOURCE-PINS.json').read_bytes()) == SOURCE_HASH, 'source manifest hash')
    require(sha((ROOT / 'CASES.json').read_bytes()) == CASE_HASH, 'case manifest hash')
    source = parse((ROOT / 'SOURCE-PINS.json').read_bytes())
    require(type(source) is dict and len(source['files']) == 6, 'six inert sources')
    for row in source['files']:
        path = (ROOT / row['local_path']).resolve()
        require(path.parent == (ROOT / 'inputs').resolve(), 'source containment')
        raw = path.read_bytes()
        require(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'source bytes/SHA256')
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        require(blob == row['git_blob'], 'source Git blob')
    return parse((ROOT / 'CASES.json').read_bytes())


class Field:
    def __init__(self, q, p, modulus=None):
        self.q, self.p = q, p
        require((q == p and modulus is None) or (q, p, modulus) == (4, 2, 7), 'declared field')
        self.add = [[a ^ b if q == 4 else (a + b) % p for b in range(q)] for a in range(q)]
        self.mul = [[self.raw_product(a, b) for b in range(q)] for a in range(q)]
        self.neg = [next(b for b in range(q) if self.add[a][b] == 0) for a in range(q)]
        self.inv = [0] + [next(b for b in range(1, q) if self.mul[a][b] == 1) for a in range(1, q)]
        for a, b, c in itertools.product(range(q), repeat=3):
            require(self.mul[a][self.add[b][c]] == self.add[self.mul[a][b]][self.mul[a][c]], 'field distributivity')

    def raw_product(self, a, b):
        if self.q != 4:
            return a * b % self.p
        value = 0
        for _ in range(2):
            if b & 1:
                value ^= a
            b >>= 1
            a <<= 1
            if a & 4:
                a ^= 7
        return value

    def power(self, a, exponent):
        value = 1
        for _ in range(exponent):
            value = self.mul[value][a]
        return value


def multiply(left, right, field):
    value = [0] * 6
    for i, a in enumerate(left):
        if a == 0:
            continue
        for j, b in enumerate(right):
            k = PRODUCT[i][j]
            if b and k >= 0:
                value[k] = field.add[value[k]][field.mul[a][b]]
    return value


def columns(x, y, field):
    yy = multiply(y, y, field)
    return [ONE, x, y, multiply(x, y, field), yy, multiply(x, yy, field)]


def determinant(cols, field):
    matrix = [list(row) for row in zip(*cols)]
    value = 1
    for k in range(6):
        pivot = next((r for r in range(k, 6) if matrix[r][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            matrix[k], matrix[pivot] = matrix[pivot], matrix[k]
            value = field.neg[value]
        scale = matrix[k][k]
        value = field.mul[value][scale]
        inverse = field.inv[scale]
        for row in range(k + 1, 6):
            factor = field.mul[matrix[row][k]][inverse]
            for col in range(k + 1, 6):
                term = field.mul[factor][matrix[k][col]]
                matrix[row][col] = field.add[matrix[row][col]][field.neg[term]]
            matrix[row][k] = 0
    return value


def valid_relations(x, y, field):
    return multiply(x, x, field) == ZERO and multiply(multiply(y, y, field), y, field) == ZERO


def normal_forms(field):
    for a, d in itertools.product(range(1, field.q), repeat=2):
        extra = int(field.p in (2, 3))
        for values in itertools.product(range(field.q), repeat=5 + extra):
            alpha, gamma, delta, epsilon, zeta = values[:5]
            beta = values[5] if field.p == 2 else 0
            c = values[5] if field.p == 3 else 0
            yield [0, a, 0, alpha, beta, gamma], [0, c, d, delta, epsilon, zeta]


def census(field):
    rows = []
    histogram = Counter()
    for x, y in normal_forms(field):
        require(valid_relations(x, y, field), 'normal form preserves defining relations')
        actual = determinant(columns(x, y, field), field)
        expected = field.mul[field.power(x[1], 3)][field.power(y[2], 6)]
        require(actual != 0 and actual == expected, 'literal determinant character')
        rows.append(x[1:] + y[1:])
        histogram[str(actual)] += 1
    rows.sort()
    require(len(rows) == len({tuple(row) for row in rows}), 'normal form uniqueness')
    count = (field.q - 1) ** 2 * field.q ** (6 if field.p in (2, 3) else 5)
    require(len(rows) == count, 'normal form count')
    cubes = {field.power(a, 3) for a in range(1, field.q)}
    require({int(k) for k in histogram} == cubes, 'complete determinant image')
    profile = {'q': field.q, 'p': field.p, 'accepted_count': len(rows),
               'accepted_map_sha256': sha(canonical(rows)),
               'determinant_counts': dict(sorted(histogram.items(), key=lambda item: int(item[0])))}
    return profile, rows


def apply(cols, value, field):
    out = [0] * 6
    for i, scalar in enumerate(value):
        for j in range(6):
            out[j] = field.add[out[j]][field.mul[scalar][cols[i][j]]]
    return out


def product_controls(field):
    beta, c = int(field.p == 2), int(field.p == 3)
    x, y = [0, 1, 0, 1, beta, 1], [0, c, 1, 1, 1, 1]
    cols = columns(x, y, field)
    require(valid_relations(x, y, field) and determinant(cols, field) != 0, 'nonlinear control')
    for i, j in itertools.product(range(6), repeat=2):
        expected = ZERO if PRODUCT[i][j] < 0 else cols[PRODUCT[i][j]]
        require(multiply(cols[i], cols[j], field) == expected, 'all 36 basis products')
    composed = [apply(cols, col, field) for col in cols]
    expected = field.mul[determinant(cols, field)][determinant(cols, field)]
    require(determinant(composed, field) == expected, 'composition determinant')
    swap_x, swap_y = [0, 0, 1, 0, 0, 0], [0, 1, 0, 0, 0, 0]
    require(not valid_relations(swap_x, swap_y, field), 'unequal variable swap rejected')
    shear_x, pure_y = [0, 1, 0, 0, 1, 0], [0, 0, 1, 0, 0, 0]
    require(valid_relations(shear_x, pure_y, field) == (field.p == 2), 'nonlinear characteristic-two exception')
    pure_x, shear_y = [0, 1, 0, 0, 0, 0], [0, 1, 1, 0, 0, 0]
    require(valid_relations(pure_x, shear_y, field) == (field.p == 3), 'triangular characteristic-three exception')


def witnesses(fields):
    rows = []
    for q in fields:
        field = Field(q, q)
        for a, d in itertools.product(range(1, q), repeat=2):
            x, y = [0, a, 0, 1, 0, 2], [0, 0, d, 1, 1, 1]
            require(valid_relations(x, y, field), 'prime nonlinear witness relation')
            actual = determinant(columns(x, y, field), field)
            require(actual == field.mul[field.power(a, 3)][field.power(d, 6)], 'witness determinant')
            rows.append([q, a, d, actual])
        require({row[3] for row in rows if row[0] == q} == {field.power(t, 3) for t in range(1, q)}, 'witness cube image')
    return rows


def admit(value):
    keys = {'schema_version', 'source_manifest_sha256', 'case_manifest_sha256', 'census', 'witnesses'}
    require(type(value) is dict and set(value) == keys, 'receipt exact keyset')
    require(type(value['schema_version']) is int and value['schema_version'] == 1, 'receipt version')
    for key in ['source_manifest_sha256', 'case_manifest_sha256']:
        require(type(value[key]) is str and re.fullmatch('[0-9a-f]{64}', value[key]), 'receipt digest')
    require(type(value['census']) is list and len(value['census']) == 4, 'census four fields')
    for row in value['census']:
        require(type(row) is dict and set(row) == {'q', 'p', 'accepted_count', 'accepted_map_sha256', 'determinant_counts'}, 'census keyset')
        require(all(type(row[k]) is int and row[k] > 0 for k in ['q', 'p', 'accepted_count']), 'census integer types')
        require(type(row['accepted_map_sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['accepted_map_sha256']), 'map digest')
        hist = row['determinant_counts']
        require(type(hist) is dict and hist, 'determinant histogram')
        for key, count in hist.items():
            require(type(key) is str and key.isdecimal() and str(int(key)) == key
                    and 0 < int(key) < row['q'] and type(count) is int and count > 0, 'histogram entry types')
    require(type(value['witnesses']) is list, 'witness list')
    for row in value['witnesses']:
        require(type(row) is list and len(row) == 4 and all(type(v) is int for v in row), 'witness integer row')
    return value


def compute():
    cases = authenticate()
    profiles, maps = [], {}
    for spec in cases['full_census_fields']:
        field = Field(spec['q'], spec['p'], spec['modulus'])
        profile, rows = census(field)
        profiles.append(profile); maps[str(field.q)] = rows
        product_controls(field)
    require(sum(row['accepted_count'] for row in profiles) == 89844, 'frozen census total')
    return {'schema_version': 1, 'source_manifest_sha256': SOURCE_HASH,
            'case_manifest_sha256': CASE_HASH, 'census': profiles,
            'witnesses': witnesses(cases['witness_prime_fields'])}, maps


def read_maps(path):
    with gzip.open(path, 'rb') as stream:
        raw = stream.read(16000001)
    require(len(raw) <= 16000000, 'decompressed map certificate byte bound')
    return parse(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', type=Path)
    parser.add_argument('--write-maps', type=Path)
    parser.add_argument('--artifact', type=Path, default=ROOT / 'RESULT.json')
    parser.add_argument('--maps', type=Path, default=ROOT / 'ACCEPTED-MAPS.json.gz')
    args = parser.parse_args()
    result, maps = compute(); admit(result)
    if args.write_maps:
        args.write_maps.write_bytes(gzip.compress(canonical(maps), mtime=0))
    maps_path = args.write_maps if args.write_maps else args.maps
    require(same_typed(read_maps(maps_path), maps), 'all actual accepted-map certificate rows/types')
    if args.emit:
        args.emit.write_bytes(canonical(result))
    else:
        retained = admit(parse(args.artifact.read_bytes()))
        require(same_typed(retained, result), 'whole retained math profile mismatch')
    print(json.dumps({'status': 'pass', 'accepted_maps': 89844, 'fields': [2, 3, 4, 5],
                      'witnesses': len(result['witnesses'])}, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, TypeError, KeyError, StopIteration) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        raise SystemExit(1) from error
