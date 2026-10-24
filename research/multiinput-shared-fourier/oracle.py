#!/usr/bin/env python3
"""Literal exact Fourier passes and cyclic convolution; no primary import."""
import argparse
import hashlib
import json
from itertools import permutations, product
from math import lcm
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def roots(period):
    need(period in (4, 12), 'unsupported exact root ring')
    degree = 2 if period == 4 else 4
    result = []
    for exponent in range(period):
        poly = [0] * (period + 1)
        poly[exponent] = 1
        for power in range(period, degree - 1, -1):
            coefficient = poly[power]
            poly[power] = 0
            poly[power - degree] -= coefficient
            if period == 12:
                poly[power - 2] += coefficient
        result.append(tuple(poly[:degree]))
    return tuple(result)


def add(left, right):
    return tuple(a + b for a, b in zip(left, right))


def multiply(left, right):
    degree = len(left)
    poly = [0] * (2 * degree - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            poly[i + j] += a * b
    for power in range(2 * degree - 2, degree - 1, -1):
        coefficient = poly[power]
        poly[power] = 0
        poly[power - degree] -= coefficient
        if degree == 4:
            poly[power - 2] += coefficient
    return tuple(poly[:degree])


def pairing(left, right, moduli, period):
    return sum(a * b * (period // q)
               for a, b, q in zip(left, right, moduli)) % period


def transform(vector, moduli, points, permutation, phases, sign, table):
    period = len(table)
    zero = (0,) * len(table[0])
    output = []
    for x, address in enumerate(permutation):
        total = zero
        for y, value in enumerate(vector):
            exponent = sign * pairing(points[address], points[y], moduli, period)
            total = add(total, multiply(table[exponent % period], value))
        output.append(multiply(table[phases[x] % period], total))
    return tuple(output)


def literal(inputs, moduli, points, permutation, phases, table):
    values = [table[0]] * len(points)
    for vector in inputs:
        forward = transform(vector, moduli, points, permutation, phases, -1, table)
        values = [multiply(a, b) for a, b in zip(values, forward)]
    return transform(values, moduli, points, permutation,
                     tuple(-w for w in phases), 1, table)


def convolution(inputs, moduli, points):
    lookup = {point: i for i, point in enumerate(points)}
    values = list(inputs[0])
    for vector in inputs[1:]:
        output = [0] * len(points)
        for x, a in enumerate(values):
            for y, b in enumerate(vector):
                address = tuple((i + j) % q for i, j, q
                                in zip(points[x], points[y], moduli))
                output[lookup[address]] += a * b
        values = output
    return tuple(values)


def descriptions(moduli, arity, points, period):
    lookup = {point: i for i, point in enumerate(points)}
    for permutation in permutations(range(len(points))):
        offset = points[permutation[0]]
        linear = tuple(tuple((a - b) % q for a, b, q
                             in zip(points[p], offset, moduli)) for p in permutation)
        symmetric = all(pairing(linear[x], points[y], moduli, period)
                        == pairing(points[x], linear[y], moduli, period)
                        for x in range(len(points)) for y in range(len(points)))
        additive = all(linear[lookup[tuple((a + b) % q for a, b, q
                                          in zip(x, y, moduli))]]
                       == tuple((a + b) % q for a, b, q
                                in zip(linear[i], linear[j], moduli))
                       for i, x in enumerate(points) for j, y in enumerate(points))
        if not symmetric or not additive:
            continue
        if any((arity - 1) * b % q for b, q in zip(offset, moduli)):
            continue
        for constant in range(period):
            if (arity - 1) * constant % period == 0:
                phases = tuple((constant - pairing(x, offset, moduli, period)) % period
                               for x in points)
                yield permutation, phases


def basis_replay():
    maps = tuples = dense = 0
    digest = hashlib.sha256()
    for moduli in ((2,), (3,), (4,), (2, 2)):
        points = tuple(product(*(range(q) for q in moduli)))
        size, period = len(points), lcm(4, *moduli)
        table = roots(period)
        zero = (0,) * len(table[0])
        basis = tuple(tuple(table[0] if x == y else zero for x in range(size))
                      for y in range(size))
        for arity in range(2, 6):
            for permutation, phases in descriptions(moduli, arity, points, period):
                maps += 1
                forward = tuple(transform(v, moduli, points, permutation,
                                          phases, -1, table) for v in basis)
                for addresses in product(range(size), repeat=arity):
                    values = [table[0]] * size
                    for address in addresses:
                        values = [multiply(a, b) for a, b in zip(values, forward[address])]
                    actual = transform(values, moduli, points, permutation,
                                       tuple(-w for w in phases), 1, table)
                    total = tuple(sum(points[a][i] for a in addresses) % q
                                  for i, q in enumerate(moduli))
                    expected = tuple(tuple(size * c for c in table[0])
                                     if point == total else zero for point in points)
                    need(actual == expected, 'literal basis mismatch')
                    digest.update(json.dumps(actual, separators=(',', ':')).encode())
                    tuples += 1
                inputs = tuple(tuple((j + 1) * (x + 1) - 2 for x in range(size))
                               for j in range(arity))
                embedded = tuple(tuple(tuple(a * c for c in table[0]) for a in v)
                                 for v in inputs)
                actual = literal(embedded, moduli, points, permutation, phases, table)
                expected = tuple(tuple(size * a * c for c in table[0])
                                 for a in convolution(inputs, moduli, points))
                need(actual == expected, 'dense convolution mismatch')
                dense += 1
    return dict(maps=maps, basis_tuples=tuples, dense_tuples=dense,
                output_sha256=digest.hexdigest())


def semantic_controls():
    cases = (
        ((2,), 2, (1, 0), (0, 2), False),
        ((2,), 3, (1, 0), (0, 2), True),
        ((2,), 3, (0, 1), (1, 1), False),
        ((2,), 5, (0, 1), (1, 1), True),
        ((3,), 3, (1, 2, 0), (0, 8, 4), False),
        ((4,), 5, (1, 2, 3, 0), (0, 1, 2, 3), False),
        ((2, 2), 3, (0, 1, 3, 2), (0, 0, 0, 0), False),
    )
    observations = []
    for moduli, arity, permutation, phases, expected in cases:
        points = tuple(product(*(range(q) for q in moduli)))
        period, size = lcm(4, *moduli), len(points)
        table = roots(period)
        zero = (0,) * len(table[0])
        failures = 0
        for addresses in product(range(size), repeat=arity):
            inputs = tuple(tuple(table[0] if i == a else zero for i in range(size))
                           for a in addresses)
            actual = literal(inputs, moduli, points, permutation, phases, table)
            total = tuple(sum(points[a][i] for a in addresses) % q
                          for i, q in enumerate(moduli))
            wanted = tuple(tuple(size * c for c in table[0])
                           if point == total else zero for point in points)
            failures += actual != wanted
        need((failures == 0) == expected, 'semantic control failed')
        observations.append(dict(group=moduli, arity=arity, failures=failures,
                                 permutation=permutation, phases=phases))
    return observations


def binding():
    sources = json.loads((ROOT / 'SOURCES.json').read_text())
    for row in sources['files']:
        if row['usage'] == 'input':
            data = (ROOT.parent.parent / row['path']).read_bytes()
            need(hashlib.sha256(data).hexdigest() == row['sha256'], 'source drift')
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in ('README.md', 'TASK.json', 'SOURCES.json', 'VERIFY.json',
                         'verify.py', 'oracle.py')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    result = dict(schema='multiinput-shared-fourier-oracle/v1', source_sha256=binding(),
                  replay=basis_replay(), controls=semantic_controls())
    result = json.loads(json.dumps(result))
    if args.write is None:
        need(result == json.loads((ROOT / 'ORACLE.json').read_text()), 'oracle receipt mismatch')
    else:
        with args.write.open('x') as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print('PASS_MULTIINPUT_FOURIER_ORACLE', json.dumps(result['replay'], sort_keys=True))


if __name__ == '__main__':
    main()
