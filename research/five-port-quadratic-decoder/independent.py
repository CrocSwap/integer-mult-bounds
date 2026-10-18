#!/usr/bin/env python3
"""Separately implemented check: set features and fraction-free elimination.

Imports neither the primary verifier nor discovery code. Uses a second prime
and recomputes the pricing from the literal minor dimensions.
Copyright 2026 Ross Richardson. Apache-2.0. Substantial OpenAI Codex assistance.
This is a second implementation by the same AI-assisted contributor, not
independent human peer review.
"""
from fractions import Fraction
from itertools import combinations, product
from math import comb, isqrt
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parent
MODULUS = 65519


def check(condition, text):
    if not condition:
        raise ValueError(text)


def decode(mask, p):
    check(type(mask) is int and 0 <= mask < 4**p, 'encoded port')
    coordinates = frozenset(i for i in range(2 * p) if mask // (2**i) % 2)
    check(len(coordinates) == 5 and len({i // 2 for i in coordinates}) == 5, 'five distinct pairs')
    return coordinates


def feature_entry(left, right):
    # Evaluate the bilinear form on explicit constant, singleton and pair
    # features, independently of the primary overlap-polynomial routine.
    common_singles = len(left.intersection(right))
    left_pairs = {frozenset(pair) for pair in combinations(left, 2)}
    right_pairs = {frozenset(pair) for pair in combinations(right, 2)}
    return 6 - 6 * common_singles + 4 * len(left_pairs.intersection(right_pairs))


def bareiss(matrix, modulus=None):
    """Fraction-free elimination over Z, or its second-prime field image."""
    array = [list(row) for row in matrix]
    size = len(array)
    check(size > 0 and all(len(row) == size for row in array), 'square matrix')
    previous, sign = 1, 1
    for k in range(size - 1):
        pivot_row = next((i for i in range(k, size)
                          if (array[i][k] % modulus if modulus else array[i][k])), None)
        if pivot_row is None:
            return 0
        if pivot_row != k:
            array[k], array[pivot_row] = array[pivot_row], array[k]
            sign = -sign
        pivot = array[k][k]
        if modulus:
            inverse = pow(previous, -1, modulus)
        for i in range(k + 1, size):
            for j in range(k + 1, size):
                numerator = pivot * array[i][j] - array[i][k] * array[k][j]
                if modulus:
                    array[i][j] = numerator * inverse % modulus
                else:
                    check(numerator % previous == 0, 'exact Bareiss division')
                    array[i][j] = numerator // previous
            array[i][k] = 0
        previous = pivot % modulus if modulus else pivot
    result = sign * array[-1][-1]
    return result % modulus if modulus else result


def verify():
    check(all(MODULUS % i for i in range(2, isqrt(MODULUS) + 1)), 'second prime')
    raw = (ROOT / 'WITNESSES.json').read_bytes()
    evidence = json.loads(raw)
    check(evidence['seed'] == 40, 'assignment seed')
    expected = {(p, 'corrector') for p in range(5, 14)} | {(p, 'star') for p in range(5, 13)}
    actual = {(row['p'], row['kind']) for row in evidence['witnesses']}
    check(actual == expected and len(evidence['witnesses']) == 17, 'complete minor coverage')
    dimensions, residues, exact_small = {}, [], []
    canonical = frozenset((0, 2, 4, 6, 8))
    for witness in evidence['witnesses']:
        p, kind = witness['p'], witness['kind']
        left = [decode(mask, p) for mask in witness['rows']]
        right = [decode(mask, p) for mask in witness['columns']]
        check(len(left) == len(set(left)) == len(right) == len(set(right)), 'minor dimensions and uniqueness')
        for label in left + right:
            check((len(label & canonical) in (1, 3)) if kind == 'corrector' else 0 in label,
                  'neighborhood/reader membership')
        matrix = [[feature_entry(x, y) for y in right] for x in left]
        determinant = bareiss(matrix, MODULUS)
        check(determinant != 0, 'second-prime nonsingularity')
        check(len(left) == witness['rank_lower'], 'claimed dimension')
        dimensions[p, kind] = len(left)
        residues.append(dict(p=p, kind=kind, dimension=len(left), determinant_mod_second_prime=determinant))
        if p == 5:
            integer_det = bareiss(matrix)
            check(integer_det != 0 and integer_det % MODULUS == determinant, 'integer determinant')
            check(integer_det % evidence['prime'] == witness['determinant_mod_prime'], 'primary residue cross-check')
            exact_small.append(dict(kind=kind, determinant=str(integer_det)))
    # Independently construct the parity-class labels and their diagonal Gram.
    even_words = [word for word in product((0, 1), repeat=5) if sum(word) % 2 == 0]
    clique = [frozenset(2 * i + bit for i, bit in enumerate(word)) for word in even_words]
    check(len(clique) == 16, 'clique cardinality')
    check(all(feature_entry(x, y) == (16 if x == y else 0) for x in clique for y in clique),
          'quadratic parity clique')
    log_lower = Fraction(549, 500)
    series = sum((Fraction(1, 4**j * (2*j + 1)) for j in range(6)), Fraction())
    check(series > log_lower, 'logarithm certificate')
    bounds = []
    for p in range(5, 13):
        volume = 2**5 * comb(p, 5)
        copies = 2 * p * dimensions[p, 'star']
        if copies < volume:
            bound = Fraction(volume - copies, volume) / (2 * dimensions[p, 'corrector'] * log_lower)
            bounds.append(dict(p=p, upper=str(bound)))
        else:
            check(p in (5, 6, 7), 'nonpositive-deficit cases')
    ceiling = max(Fraction(row['upper']) for row in bounds)
    tail = Fraction(1, 2 * dimensions[13, 'corrector']) / log_lower
    frozen = json.loads((ROOT / 'sources/selected-result-base.json').read_text())
    check(tail < ceiling < Fraction(frozen['kappa']), 'strict comparison to frozen selection')
    return dict(schema='five-port-second-implementation-v1', witness_sha256=hashlib.sha256(raw).hexdigest(),
                second_prime=MODULUS, minors=residues, integer_determinants_p5=exact_small,
                finite_bounds=bounds, ceiling=str(ceiling), tail=str(tail),
                selected_kappa=frozen['kappa'], human_independent_review=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate', type=Path)
    args = parser.parse_args()
    report = verify()
    if args.write_certificate:
        with args.write_certificate.open('x') as handle:
            handle.write(json.dumps(report, indent=2) + '\n')
    else:
        check(json.loads((ROOT / 'INDEPENDENT.json').read_text()) == report, 'second receipt equality')
    print('PASS_FIVE_PORT_SECOND_IMPLEMENTATION minors=17 prime=65519 exact_integer_determinants=2 '
          'ceiling=125/76433 no_new_kappa')


if __name__ == '__main__':
    main()
