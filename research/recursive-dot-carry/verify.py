"""Replay the exact residue construction, independent row oracle and finite circuit."""

from itertools import product
from pathlib import Path
import json
import random
import runpy


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def fused(left, right, a, b, carry, m):
    mask = (1 << m) - 1
    x, u = left
    y, v = right
    left_mean = ((x + u) & mask) >> 1
    right_mean = ((y + v) & mask) >> 1
    base = 2 * left_mean * right_mean
    width = max(0, m + 1 - a - b)
    if width:
        left_diff = (u >> a) - (x >> a)
        right_diff = (v >> b) - (y >> b)
        correction = left_diff * right_diff & ((1 << width) - 1)
        base += correction << (a + b - 1)
    return (base + carry) & mask


def valid_pairs(m, shared_bits):
    size = 1 << m
    return [(x, (x + offset) % size)
            for x in range(size) for offset in range(0, size, 1 << shared_bits)]


def check_congruences():
    total = 0
    for m in range(2, 6):
        size = 1 << m
        for a, b in product(range(1, m + 1), repeat=2):
            without_residual = True
            for left, right in product(valid_pairs(m, a), valid_pairs(m, b)):
                x, u = left
                y, v = right
                want = (x*y + u*v) % size
                got = fused(left, right, a, b, 0, m)
                require(got == want, (m, a, b, left, right, got, want))
                mean_only = 2 * ((x+u) // 2) * ((y+v) // 2)
                if (mean_only - want) % size:
                    without_residual = False
                total += 1
            require(without_residual == (a+b >= m+1), (m, a, b, 'threshold'))
    rng = random.Random(891605)
    for m in (6, 8, 16, 31, 64, 255, 1024):
        for _ in range(120):
            a, b = rng.randint(1, m), rng.randint(1, m)
            x, y, c = [rng.randrange(-(1 << m), 1 << m) for _ in range(3)]
            u = x + (rng.getrandbits(m-a) << a)
            v = y + (rng.getrandbits(m-b) << b)
            require(fused((x, u), (y, v), a, b, c, m) == (x*y + u*v + c) % (1 << m),
                    ('signed lifts', m, a, b, c))
    return {'exhaustive_congruent_inputs': total, 'signed_large_inputs': 840}


def literal_rows(m):
    size = 1 << m
    odds = list(product(range(1, size, 2), repeat=2))
    classes = {}
    for x, u in odds:
        row = bytes(((x*y+u*v) >> (m-1)) & 1 for y, v in odds)
        require(0 in row and 1 in row, 'constant row')
        classes.setdefault(row, set()).add((x, u))
    half = size >> 1
    for group in classes.values():
        x, u = next(iter(group))
        require(group == {(x, u), (x ^ half, u ^ half)}, ('row class', m, x, u))
    require(len(classes) == 1 << (2*m-3), 'row count')
    return {'m': m, 'rows': len(odds), 'different': len(classes),
            'minimum_total_coordinates_per_side': len(classes).bit_length()}


def run():
    result = {'congruence': check_congruences(),
              'odd_dot_rows': [literal_rows(m) for m in range(3, 7)]}
    result['circuits'] = runpy.run_path(str(Path(__file__).with_name('circuits.py')))['check']()
    return result


if __name__ == '__main__':
    result = run()
    frozen = json.loads(Path(__file__).with_name('RESULT.json').read_text())
    require(result == frozen, 'replay differs from RESULT.json')
    review = Path(__file__).with_name('independent.py')
    if review.is_file():
        runpy.run_path(str(review), run_name='__main__')
    print(json.dumps(result, sort_keys=True))
    print('PASS_RECURSIVE_DOT_CARRY')
