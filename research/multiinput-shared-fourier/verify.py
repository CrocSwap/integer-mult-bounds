#!/usr/bin/env python3
"""Exhaust the declared monomial coefficient census using integer turns."""
import argparse
import hashlib
import json
from itertools import permutations, product
from math import gcd, lcm, prod
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GROUPS = ((2,), (3,), (4,), (2, 2))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def geometry(moduli):
    need(isinstance(moduli, tuple) and 1 <= len(moduli) <= 3, "invalid factors")
    need(all(type(q) is int and 2 <= q <= 8 for q in moduli), "invalid modulus")
    need(prod(moduli) <= 64, "group too large")
    points = tuple(product(*(range(q) for q in moduli)))
    period = lcm(4, *moduli)
    pairing = tuple(tuple(sum(a * b * (period // q)
                             for a, b, q in zip(x, y, moduli)) % period
                          for y in points) for x in points)
    return points, period, pairing


def validate(arity, permutation, weights, size, period):
    need(type(arity) is int and 2 <= arity <= 64, "invalid arity")
    need(len(permutation) == size and all(type(x) is int for x in permutation),
         "invalid permutation shape")
    need(sorted(permutation) == list(range(size)), "not a permutation")
    need(len(weights) == size and all(type(x) is int and 0 <= x < period
                                    for x in weights), "invalid phases")


def coefficient_rule(arity, permutation, weights, pairing, period):
    size = len(pairing)
    validate(arity, permutation, weights, size, period)
    return all((arity * weights[y] - weights[x] + pairing[permutation[x]][y]
                - pairing[x][permutation[y]]) % period == 0
               for x in range(size) for y in range(size))


def normal_form(moduli, arity, permutation, weights, points, period, pairing):
    size = len(points)
    validate(arity, permutation, weights, size, period)
    offset = points[permutation[0]]
    lookup = {point: i for i, point in enumerate(points)}
    linear = tuple(lookup[tuple((a - b) % q for a, b, q
                              in zip(points[p], offset, moduli))]
                   for p in permutation)
    if any((arity - 1) * b % q for b, q in zip(offset, moduli)):
        return False
    if (arity - 1) * weights[0] % period:
        return False
    if any(weights[x] != (weights[0] - pairing[x][permutation[0]]) % period
           for x in range(size)):
        return False
    for x in range(size):
        for y in range(size):
            total = lookup[tuple((a + b) % q for a, b, q
                                 in zip(points[x], points[y], moduli))]
            image = tuple((a + b) % q for a, b, q
                          in zip(points[linear[x]], points[linear[y]], moduli))
            if points[linear[total]] != image:
                return False
            if pairing[linear[x]][y] != pairing[x][linear[y]]:
                return False
    return True


def census():
    rows = []
    digest = hashlib.sha256()
    for moduli in GROUPS:
        points, period, pairing = geometry(moduli)
        size = len(points)
        for arity in range(2, 6):
            candidates = accepted = symmetric = 0
            for permutation in permutations(range(size)):
                if permutation[0] == 0 and all(pairing[permutation[x]][y]
                        == pairing[x][permutation[y]]
                        for x in range(size) for y in range(size)):
                    symmetric += 1
                for weights in product(range(period), repeat=size):
                    actual = coefficient_rule(arity, permutation, weights, pairing, period)
                    predicted = normal_form(moduli, arity, permutation, weights,
                                            points, period, pairing)
                    need(actual == predicted, "normal-form disagreement")
                    candidates += 1
                    accepted += actual
                    digest.update(bytes((int(actual),)))
            torsion = prod(gcd(arity - 1, q) for q in moduli)
            expected = symmetric * torsion * gcd(arity - 1, period)
            need(accepted == expected, "closed count disagreement")
            rows.append(dict(group=moduli, arity=arity, period=period,
                             candidates=candidates, accepted=accepted,
                             self_adjoint_automorphisms=symmetric,
                             torsion=torsion))
    return dict(rows=rows, candidates=sum(r['candidates'] for r in rows),
                accepted=sum(r['accepted'] for r in rows),
                classification_sha256=digest.hexdigest())


def controls():
    points, period, pairing = geometry((2,))
    good = (3, (1, 0), (0, 2))
    need(coefficient_rule(*good, pairing, period), "ternary translated fixture")
    need(not coefficient_rule(2, good[1], good[2], pairing, period),
         "bilinear translation must fail")
    need(not coefficient_rule(3, (0, 1), (1, 1), pairing, period),
         "constant i must fail at arity three")
    need(coefficient_rule(5, (0, 1), (1, 1), pairing, period),
         "constant i must pass at arity five")
    cases = ((1, (0, 1), (0, 0)), (65, (0, 1), (0, 0)),
             (True, (0, 1), (0, 0)), (3, (0, 0), (0, 0)),
             (3, (0,), (0, 0)), (3, (0, 1), (4, 0)),
             (3, (0, 1), (0,)), (3, (False, 1), (0, 0)))
    for args in cases:
        try:
            coefficient_rule(*args, pairing, period)
        except ValueError:
            continue
        raise ValueError("invalid-input control accepted")
    for factors in ((), (1,), (2, 2, 2, 2), (8, 8, 8)):
        try:
            geometry(factors)
        except ValueError:
            continue
        raise ValueError("invalid-group control accepted")
    return dict(semantic=4, invalid_inputs=len(cases) + 4)


def source_binding():
    manifest = json.loads((ROOT / 'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage'] == 'input':
            data = (ROOT.parent.parent / row['path']).read_bytes()
            need(hashlib.sha256(data).hexdigest() == row['sha256'], "source drift")
    names = ('README.md', 'TASK.json', 'SOURCES.json', 'VERIFY.json',
             'verify.py', 'oracle.py')
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in names}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    result = dict(schema='multiinput-shared-fourier-primary/v1',
                  source_sha256=source_binding(), census=census(), controls=controls())
    result = json.loads(json.dumps(result))
    if args.write is None:
        expected = json.loads((ROOT / 'PRIMARY.json').read_text())
        need(result == expected, "primary receipt mismatch")
    else:
        with args.write.open('x') as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print('PASS_MULTIINPUT_SHARED_FOURIER', result['census']['candidates'],
          'candidates;', result['census']['accepted'], 'accepted')


if __name__ == '__main__':
    main()
