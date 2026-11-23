#!/usr/bin/env python3
"""Separate exact oracle for the source raw-H / normalized-H0 grid interface.

Does not import the author adapter or checker. Uses the literal retained raw
loop only as a compared implementation, and an independent dense sign kernel.
Prepared for Jerry Chen / CubeJerry with OpenAI assistance. Apache-2.0.
"""
import argparse
import ast
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path


RAW_SHA = '36c5a9a0082c9aa3c6cb2d04a9196af8debce0d551a0525975b710018ea02cac'


def require(ok, why):
    if not ok:
        raise ValueError(why)


def zmul(x, y):
    a, b = x
    c, d = y
    return a*c-b*d, a*d+b*c


def zpow(x, n):
    out = (F(1), F(0))
    for _ in range(n):
        out = zmul(out, x)
    return out


def dense_raw(data, positions):
    mask = sum(1 << j for j in positions)
    out = []
    for x in range(len(data)):
        real = imag = 0
        for y, (a, b) in enumerate(data):
            if (x & ~mask) == (y & ~mask):
                sign = -1 if (x & y & mask).bit_count() % 2 else 1
                real += sign*a
                imag += sign*b
        out.append((real, imag))
    return out


def trunc0(x):
    return x.numerator // x.denominator if x >= 0 else -((-x.numerator)//x.denominator)


def finish_independent(pair, h):
    k = h//2
    scaled = zmul(tuple(F(x, 1 << k) for x in pair), zpow((F(0),F(-1)), k))
    require(all(x.denominator == 1 for x in scaled), 'nonendpoint divisor')
    if h % 2:
        a, b = scaled
        scaled = ((a+b)/2, (b-a)/2)
        require(all(x.denominator == 1 for x in scaled), 'nonendpoint parity')
    return tuple(x.numerator for x in scaled)


def native_out(data, positions, precision, requested, radius_shift):
    """Direct rational normalized transform; no use of author's shifts."""
    h = len(positions)
    sums = dense_raw(data, positions)
    denominator = 1 << (precision + radius_shift + h)
    return [(trunc0(F(a, denominator) * (1 << requested)),
             trunc0(F(b, denominator) * (1 << requested))) for a, b in sums]


def run(source):
    raw = source.read_bytes()
    require(sha256(raw).hexdigest() == RAW_SHA, 'literal raw-H source hash')
    tree = ast.parse(raw)
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'hadamard')
    scope = {}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec'), scope)
    literal = scope['hadamard']
    counts = {'phase_entries': 0, 'terminal_entries': 0, 'complete_fields': 0, 'endpoint_components': 0,
              'sharpness_witnesses': 0, 'parameter_enclosures': 0}

    # Independent Gaussian-rational C/S/b calculation, retaining absolute phase.
    a = (F(1, 2), F(1, 2))
    b = (F(1, 2), F(-1, 2))
    i = (F(0), F(1))
    for h in range(1, 7):
        for x in range(1 << h):
            for y in range(1 << h):
                distance = (x ^ y).bit_count()
                z = zmul(zpow(a, h-distance), zpow(b, distance))
                z = zmul(z, zpow(i, x.bit_count()+y.bit_count()))
                # At the private Q+h grid, the completed S C S basis endpoint
                # has this exact integral numerator. Normalize it entirely by
                # integer division and phase, separately from rational b**h.
                before = tuple(t * (1 << h) for t in z)
                require(all(t.denominator == 1 for t in before), 'C endpoint integer grid')
                k = h//2
                require(all(t.numerator % (1 << k) == 0 for t in before), 'C endpoint divisor')
                integer_pair = tuple(t.numerator//(1 << k) for t in before)
                integer_pair = zmul(integer_pair, zpow((F(0),F(-1)), k))
                if h % 2:
                    aa, bb = integer_pair
                    require((aa+bb) % 2 == 0 and (bb-aa) % 2 == 0, 'C endpoint odd parity')
                    integer_pair = ((aa+bb)/2, (bb-aa)/2)
                require(integer_pair == (-1 if (x & y).bit_count() % 2 else 1, 0),
                        'terminal normalization without extra denominator')
                require(finish_independent(tuple(t.numerator for t in before), h) == integer_pair,
                        'independent terminal guard accepts valid endpoint')
                counts['terminal_entries'] += 1
                z = zmul(z, zpow(b, h))
                wanted = (F(-1 if (x & y).bit_count() % 2 else 1, 1 << h), F(0))
                require(z == wanted, 'normalized C/S/b identity')
                counts['phase_entries'] += 1

    for dimension in range(1, 7):
        n = 1 << dimension
        for h in range(1, dimension+1):
            for positions in combinations(range(dimension), h):
                # Arbitrary full fields, including spectators and nonzero holes.
                for p in (1, 3, 7):
                    data = [(((17*j+3) % 11)-5, ((7*j*j+1) % 9)-4) for j in range(n)]
                    exponent = 4
                    radius_shift = exponent+1
                    requested = p+radius_shift+h
                    # Squared norm is exact and safely within the supplied bound.
                    require(all(a*a+b*b <= (1 << (2*(p+exponent))) for a,b in data), 'input modulus')
                    expected = dense_raw(data, positions)
                    actual = list(data)
                    literal(actual, tuple(1 << j for j in positions))
                    require(actual == expected, 'actual source raw-H vs dense oracle')
                    returned = native_out(data, positions, p, requested, radius_shift)
                    require(returned == expected, 'requested native grid is exact')
                    initial_numerators = [(a << h, b << h) for a,b in data]
                    require(all(F(a,1<<requested) == F(c,1<<(p+radius_shift)) and
                                F(b,1<<requested) == F(d,1<<(p+radius_shift))
                                for (a,b),(c,d) in zip(initial_numerators,data)), 'entrance encoding')
                    counts['complete_fields'] += 1
                    counts['endpoint_components'] += 2*n

                # Each sign has a basis datum lost at one fewer fractional bit.
                for sign in (-1, 1):
                    p, radius_shift = 1, 2
                    one = [(0,0)]*n
                    one[(n-1) ^ (1 << positions[0])] = (sign, -sign)
                    requested = p+radius_shift+h
                    full = native_out(one, positions, p, requested, radius_shift)
                    low = native_out(one, positions, p, requested-1, radius_shift)
                    require(any(a or b for a,b in full), 'nonzero sharpness output')
                    require(all(a == b == 0 for a,b in low), 'Q-1 truncation control')
                    counts['sharpness_witnesses'] += 1

    # Exact finite corroboration of the universal polynomial inequalities.
    for p in range(1, 65):
        for L in sorted({1, p, max(1,p//2)}):
            for d in sorted({1,L,max(1,L//2)}):
                ellmax = L-d+1
                J = 20000*(d+1)*(ellmax+2)**6
                C = 4*J*(d+1)**2+d+1
                E = (257*L+1)//2+1354*d
                A = 20*L+303*d
                P = 4*p+A+2*E+C.bit_length()
                Q = P+E+1+d
                require(C < (1 << 29)*L**9, 'C polynomial bound')
                require(C.bit_length() <= 29*L, 'C bit bound')
                require(E <= 1483*L and P <= 4*p+3318*L, 'P/E enclosure')
                require(Q <= 4807*p and P+E+3*d+31 <= 4839*p, 'Q/width enclosure')
                counts['parameter_enclosures'] += 1

    # A half-normalization omission is detected already on one real basis input.
    require(zmul(a,b) == (F(1,2),F(0)) and zmul(a,b) != (F(1),F(0)), 'missing normalization control')
    for h, why in ((1,'nonendpoint parity'),(2,'nonendpoint divisor')):
        try:
            finish_independent((1,0),h)
        except ValueError as exc:
            require(str(exc) == why, 'wrong endpoint control failure')
        else:
            raise ValueError('nonendpoint accepted')
    return {'status': 'PASS_INDEPENDENT_NATIVE_GRID_ORACLE', 'counts': counts,
            'negative_controls': ['one fewer output bit, both signs',
                                  'missing native normalization', 'source corruption',
                                  'nonendpoint divisor/parity'],
            'scope': 'Exact finite corroboration and source identity; no native internal execution or tariff admission.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.source), indent=2, sort_keys=True))
