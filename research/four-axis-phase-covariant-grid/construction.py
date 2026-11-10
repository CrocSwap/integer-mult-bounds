"""Exact finite certificate for a sharp phase-covariant Walsh-16 map.

@CubeJerry with substantial AI assistance. Apache-2.0.
Candidate offsets and native conventions follow Nick Petalas, #6574;
this package changes the period quotient and enforces negation orbits.
"""
from itertools import product
import json
from pathlib import Path

SIZE = 16
MODULI = (8, 4, 4, 4, 4)
HIGH = (7, 11, 13, 14, 15)
KEYS = tuple(product(*(range(m) for m in MODULI)))
WALSH = tuple(tuple(1 if (r & s).bit_count() % 2 == 0 else -1
                    for s in range(SIZE)) for r in range(SIZE))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def walsh(values):
    return tuple(sum(a * b for a, b in zip(row, values)) for row in WALSH)


def negate_key(key):
    return tuple(-a % m for a, m in zip(key, MODULI))


def source_key(values):
    return ((4 * values[7] - sum(values)) % 8,) + tuple(
        (2 * values[HIGH[j + 1]] - sum(values[s] for s in range(SIZE)
                                      if s >> j & 1)) % 4 for j in range(4))


def target_key(values):
    numerator = walsh(values)
    return ((numerator[7] - 4 * values[0]) % 8,) + tuple(
        ((numerator[HIGH[j + 1]] - numerator[7]) // 2
         + 2 * values[1 << j]) % 4 for j in range(4))


def source_representative(key):
    values = [0] * SIZE
    values[0] = sum(key[1:]) - key[0]
    for j in range(4):
        values[1 << j] = -key[j + 1]
    return tuple(values)


def target_representative(key):
    a, b, c, d = key[1:]
    low = ((2 * a + c + 3 * d) % 4, (3 * b + 3 * d) % 4,
           (a + 2 * c + 3 * d) % 4, d)
    values = [0] * SIZE
    values[0] = (5 * (key[0] + sum(low[:3]) - low[3])) % 8
    for j in range(4):
        values[1 << j] = low[j]
    return tuple(values)


def build_tables():
    """Expand and validate 1008 signed-orbit witnesses plus 32 fixed classes."""
    certificate = json.loads(Path(__file__).with_name('CERTIFICATE.json').read_text())
    need(certificate.get('schema_version') == 1 and
         tuple(certificate.get('moduli', ())) == MODULI, 'Certificate schema')
    rows = certificate.get('rows', [])
    need(type(rows) is list and len(rows) == 1008, '1008 free negation orbits')
    forward, backward = {}, {}
    for key, offset in rows:
        key, offset = tuple(key), tuple(offset)
        need(key in KEYS and key < negate_key(key), 'Canonical free orbit')
        need(len(offset) == SIZE and all(type(x) is int for x in offset),
             'Sixteen integer correction coordinates')
        numerator = tuple(a + b for a, b in zip(walsh(source_representative(key)), offset))
        need(all(x % 4 == 0 for x in numerator), 'Integral corrected output')
        target = target_key(tuple(x // 4 for x in numerator))
        image = walsh(offset)
        need(all(x % 4 == 0 for x in image), 'Integral inverse correction')
        inverse = tuple(-x // 4 for x in image)
        for source, destination, e, f in (
                (key, target, offset, inverse),
                (negate_key(key), negate_key(target),
                 tuple(-x for x in offset), tuple(-x for x in inverse))):
            need(source not in forward and destination not in backward,
                 'Distinct source and target classes')
            forward[source], backward[destination] = e, f
    for key in KEYS:
        if key == negate_key(key):
            numerator = walsh(source_representative(key))
            need(all(x % 4 == 0 for x in numerator), 'Integral fixed class')
            target = target_key(tuple(x // 4 for x in numerator))
            need(key not in forward and target not in backward, 'Distinct fixed class')
            forward[key] = backward[target] = (0,) * SIZE
    need(set(forward) == set(backward) == set(KEYS), 'Complete class bijection')
    for table, coordinate_bound in ((forward, 3), (backward, 5)):
        for e in table.values():
            need(sum(x * x for x in e) <= 64, 'Sharp real energy')
            need(max(abs(x) for x in e) <= coordinate_bound,
                 'Certified forward/inverse coordinate bound')
            need(sum((1, 0, -1, 0)[j.bit_count() % 4] * e[j]
                     for j in range(SIZE)) == 0 and
                 sum((0, -1, 0, 1)[j.bit_count() % 4] * e[j]
                     for j in range(SIZE)) == 0, 'Exact weighted sum')
    return forward, backward
