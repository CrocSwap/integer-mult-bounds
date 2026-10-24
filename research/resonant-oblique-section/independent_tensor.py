#!/usr/bin/env python3
"""Literal tensor oracle, using a separate packed monomial implementation."""
import argparse
from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent.parent / 'research/resonant-all-width-projector/TARGET.json'
PIN = 'e7df852b5c641f326ac67cd35cea8da6cfdd059fa12df1cf6fb758bb4206d684'
UNITS = ((1, 0), (0, 1), (-1, 0), (0, -1))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def compose(left, right):
    return tuple((left[v % 8] % 8) + 8 * ((v // 8 + left[v % 8] // 8) % 4) for v in right)


def invert(g):
    result = [0] * 8
    for j, v in enumerate(g):
        result[v % 8] = j + 8 * ((-(v // 8)) % 4)
    return tuple(result)


def signs(g):
    return tuple(v ^ 16 for v in g) if g[0] >= 16 else g


def word(record):
    return tuple(p + 8 * q for p, q in zip(record['permutation'], record['phase_i']))


def decoder(records, recipe):
    anchor = word(recipe['anchor'])
    c = defaultdict(int)
    for record in records:
        c[signs(compose(invert(anchor), word(record)))] += 1 if record['coefficient'] == '1/16' else -1
    require(set(c.values()) == {-2, 2}, 'source quotient coefficient')
    c = {g: v // 2 for g, v in c.items()}
    first = next(iter(c))
    stabs = []
    for left in (True, False):
        out = []
        candidates = {signs(compose(g, invert(first)) if left else compose(invert(first), g)) for g in c}
        for h in candidates:
            translated = {signs(compose(h, g) if left else compose(g, h)): v for g, v in c.items()}
            if translated == c:
                out.append((h, 1))
            elif translated == {g: -v for g, v in c.items()}:
                out.append((h, -1))
        stabs.append(out)
    require(tuple(map(len, stabs)) == (32, 16), 'independent signed stabilizers')
    out = defaultdict(int)
    for record in recipe['corners']:
        g = word(record)
        orbit = defaultdict(int)
        for r, x in stabs[1]:
            for l, y in stabs[0]:
                orbit[signs(compose(compose(r, g), l))] += x * y
        scale = abs(next(iter(orbit.values())))
        require(scale and all(abs(v) == scale for v in orbit.values()), 'signed orbit multiplicity')
        for h, value in orbit.items():
            out[signs(compose(h, invert(anchor)))] += record['numerator'] * value // scale
    return {g: v for g, v in out.items() if v}


def plus(a, b):
    return a[0] + b[0], a[1] + b[1]


def product(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def literal_matrix(terms, width):
    matrix = {}
    for j in range(8 ** width):
        digits = [(j >> (3 * h)) & 7 for h in range(width)]
        column = defaultdict(lambda: (0, 0))
        for g, value in terms.items():
            k = sum((g[d] % 8) << (3 * h) for h, d in enumerate(digits))
            phase = sum(g[d] // 8 for d in digits) % 4
            u = UNITS[phase]
            column[k] = plus(column[k], (value * u[0], value * u[1]))
        for k, value in column.items():
            if value != (0, 0):
                matrix[k, j] = value
    return matrix


def matrix_product(a, b):
    columns = defaultdict(list)
    for (i, j), value in a.items():
        columns[j].append((i, value))
    out = defaultdict(lambda: (0, 0))
    for (k, j), value in b.items():
        for i, coefficient in columns[k]:
            out[i, j] = plus(out[i, j], product(coefficient, value))
    return {k: v for k, v in out.items() if v != (0, 0)}


def scale(matrix, value):
    return {k: (a * value, b * value) for k, (a, b) in matrix.items()}


def apply_literal(terms, width, data):
    out = [(0, 0)] * len(data)
    for j, value in enumerate(data):
        digits = [(j >> (3 * h)) & 7 for h in range(width)]
        for g, coefficient in terms.items():
            k = sum((g[d] % 8) << (3 * h) for h, d in enumerate(digits))
            phase = sum(g[d] // 8 for d in digits) % 4
            term = product(UNITS[phase], value)
            out[k] = plus(out[k], (coefficient * term[0], coefficient * term[1]))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    raw = SOURCE.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == PIN, 'independent source hash')
    records = json.loads(raw)
    recipe = json.loads((HERE / 'SECTION.json').read_text())
    require(recipe['D_denominator'] == 16384, 'independent denominator')
    a = {word(r): 1 if r['coefficient'] == '1/16' else -1 for r in records}
    b = decoder(records, recipe)
    require(len(b) == 1920, 'independent decoder term count')
    m = literal_matrix(a, 2)
    n = literal_matrix(b, 2)
    mn = matrix_product(m, n)
    nm = matrix_product(n, m)
    require(matrix_product(mn, m) == scale(m, 32768), 'all 64 columns of A2 B2 A2')
    require(matrix_product(nm, nm) == scale(nm, 32768), 'all 64 columns of E2 squared')
    nonhermitian = [(i, j) for (i, j), (x, y) in nm.items()
                    if nm.get((j, i), (0, 0)) != (x, -y)]
    require(bool(nonhermitian), 'the section must be genuinely oblique')
    i, j = min(nonhermitian)
    witness = {'row': i, 'column': j,
               'E_entry': [str(Fraction(v, 32768)) for v in nm.get((i, j), (0, 0))],
               'E_transposed_entry': [str(Fraction(v, 32768)) for v in nm.get((j, i), (0, 0))]}
    require(not literal_matrix(a, 1) and not literal_matrix(a, 3), 'literal odd-width cancellation')
    collapsed = {}
    for g, value in a.items():
        h = tuple((v % 8) + 8 * ((v // 8 - g[0] // 8) % 4) for v in g)
        collapsed[h] = collapsed.get(h, 0) + value
    require(literal_matrix(collapsed, 2) != m, 'quarter-phase loss must alter actual tensor action')
    dirty = [(j % 11 - 5, (7 * j) % 13 - 6) for j in range(4096)]
    z = apply_literal(a, 4, dirty)
    y = apply_literal(b, 4, z)
    returned = apply_literal(a, 4, y)
    require(returned == [(32768 * x, 32768 * y) for x, y in z], 'actual width-four dirty ABA')
    result = {'status': 'PASS_INDEPENDENT_OBLIQUE_TENSORS', 'full_width_two_columns': 64,
              'odd_literal_widths': [1, 3], 'width_four_dirty_coordinates': 4096,
              'decoder_terms': len(b), 'quarter_phase_mutation_rejected': True, 'nonhermitian_witness': witness,
              'independent_representation': 'packed column action; literal Gaussian integer tensors'}
    expected = HERE / 'INDEPENDENT.json'
    if not args.write:
        require(json.dumps(json.loads(expected.read_text()), sort_keys=True) == json.dumps(result, sort_keys=True), 'typed independent receipt')
    else:
        expected.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(result['status'])


if __name__ == '__main__':
    main()
