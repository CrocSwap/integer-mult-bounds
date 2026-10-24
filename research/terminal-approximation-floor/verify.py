#!/usr/bin/env python3
"""Exact corroboration of a terminal approximation floor. Apache-2.0."""

from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SEED = ((1, 0), (0, -1), (0, 1), (1, 0))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def bounded_integer(value, lower, upper, name):
    need(type(value) is int and lower <= value <= upper, name)


def error_squared(width, adds, inverse_count):
    """Universal squared operator-error lower bound, not an optimum."""
    bounded_integer(width, 1, 1000, 'width outside executable budget')
    bounded_integer(adds, 0, 2000, 'ADD count outside executable budget')
    bounded_integer(inverse_count, 0, 2, 'invalid inverse count')
    support = 4 ** (width - 1)
    missed = max(0, support - 2 ** adds)
    return Fraction(missed, support * (8 * 13 ** inverse_count) ** 2)


def multiply(left, right):
    a, b = left
    c, d = right
    return a * c - b * d, a * d + b * c


def tensor_row(degree):
    bounded_integer(degree, 0, 5, 'tensor fixture exceeds capacity')
    row = [(1, 0)]
    for _ in range(degree):
        row = [multiply(x, y) for x in row for y in SEED]
    need(len(row) == 4 ** degree, 'tensor support length')
    need(all(a * a + b * b == 1 for a, b in row), 'flat Gaussian phases')
    return row, 2 ** degree


def distance_squared(target, approximation, denominator):
    need(len(target) == len(approximation) <= 1024, 'row dimensions')
    need(type(denominator) is int and denominator > 0, 'denominator')
    numerator = sum((a - c) ** 2 + (b - d) ** 2
                    for (a, b), (c, d) in zip(target, approximation))
    return Fraction(numerator, denominator ** 2)


def support_census():
    """Literal best truncations on every support through sixteen columns."""
    counts = []
    for degree in range(3):
        row, denominator = tensor_row(degree)
        size = len(row)
        for mask in range(1 << size):
            approximation = [value if mask >> i & 1 else (0, 0)
                             for i, value in enumerate(row)]
            actual = distance_squared(row, approximation, denominator)
            expected = Fraction(size - mask.bit_count(), size)
            need(actual == expected, 'nearest-support distance')
        counts.append(1 << size)
    return counts


def coefficient_census():
    """All 9^4 rows in a Gaussian-integer coefficient box, with cancellations."""
    row, denominator = tensor_row(1)
    alphabet = tuple(product(range(-1, 2), repeat=2))
    count = 0
    for approximation in product(alphabet, repeat=len(row)):
        used = sum(value != (0, 0) for value in approximation)
        actual = distance_squared(row, approximation, denominator)
        need(actual >= Fraction(4 - used, 4), 'arbitrary-coefficient floor')
        count += 1
    return count


def tensor_fixtures():
    count, witnesses = 0, []
    for degree in range(6):
        row, denominator = tensor_row(degree)
        size = len(row)
        need(distance_squared(row, [(0, 0)] * size, denominator) == 1,
             'normalized row energy')
        for used in sorted({0, 1, size // 2, size - 1, size}):
            approximation = row[:used] + [(0, 0)] * (size - used)
            actual = distance_squared(row, approximation, denominator)
            need(actual == Fraction(size - used, size), 'sharp row truncation')
            if used:
                a, b = approximation[0]
                approximation[0] = (a + 3, b - 2)
                perturbed = distance_squared(row, approximation, denominator)
                need(perturbed == actual + Fraction(13, denominator ** 2),
                     'retained-coordinate orthogonality')
            count += 1
        if degree:
            approximation = row[:size // 2] + [(0, 0)] * (size // 2)
            need(distance_squared(row, approximation, denominator) == Fraction(1, 2),
                 'one-fewer-ADD row boundary')
            witnesses.append({'width': degree + 1, 'support': size,
                              'half_support_error_squared_relative': '1/2'})
    return count, witnesses


def corollary_census():
    count = 0
    for width in range(2, 201):
        for inverses in range(3):
            scale_squared = Fraction(1, (8 * 13 ** inverses) ** 2)
            for adds in range(2 * (width - 1)):
                lower = error_squared(width, adds, inverses)
                need(lower >= scale_squared / 2 > scale_squared / 4,
                     'half-scale tolerance preserves ADD floor')
                count += 1
            need(error_squared(width, 2 * (width - 1), inverses) == 0,
                 'lower bound vanishes at exact support threshold')
    need(error_squared(1, 0, 1) == 0, 'width-one vacuous bound')
    need(error_squared(1000, 2000, 2) == 0, 'executable upper endpoint')
    return count


def controls():
    invalid = [(0, 0, 1), (1001, 0, 1), (True, 0, 1), (2, -1, 1),
               (2, 2001, 1), (2, False, 1), (2, 0, -1), (2, 0, 3)]
    for values in invalid:
        try:
            error_squared(*values)
        except ValueError:
            continue
        raise ValueError('invalid argument accepted')
    row, denominator = tensor_row(1)
    half = row[:2] + [(0, 0)] * 2
    half_error = distance_squared(row, half, denominator)
    need(half_error != 1, 'reject omitted support allowance')
    need(half_error != 0, 'reject a dimension-free zero-error claim')
    need(error_squared(3, 0, 0) != error_squared(3, 0, 1),
         'reject omitted inverse scaling')
    need(error_squared(3, 0, 1) != error_squared(3, 0, 2),
         'reject a squared inverse-count substitution')
    need(error_squared(3, 2, 1) != error_squared(2, 2, 1),
         'reject omission of the marker-column loss')
    need(distance_squared([(2, 0), (0, 0), (0, 0), (0, 0)],
                          [(2, 0), (0, 0), (0, 0), (0, 0)], 2) == 0,
         'nonflat negative fixture')
    return {'invalid_arguments': len(invalid), 'false_strengthenings': 6}


def input_hashes():
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_text())
    hashes = {}
    for entry in manifest['files']:
        if entry['usage'] == 'input':
            path = entry['path']
            digest = sha256((ROOT / path).read_bytes()).hexdigest()
            need(digest == entry['sha256'], 'cited premise changed: ' + path)
            hashes[path] = digest
    need(len(hashes) == 2, 'exactly two cited premise inputs')
    return hashes


def result():
    inputs = input_hashes()
    tensor_count, witnesses = tensor_fixtures()
    output = {
        'schema_version': 1,
        'claim_type': 'scoped proof with exact finite corroboration',
        'premise_inputs': inputs,
        'support_subsets': support_census(),
        'coefficient_rows': coefficient_census(),
        'tensor_truncation_fixtures': tensor_count,
        'tensor_boundary_witnesses': witnesses,
        'corollary_comparisons': corollary_census(),
        'controls': controls(),
        'actual_bank_inverse_count': 1,
        'actual_bank_scale': '1/104',
        'actual_bank_sufficient_error_tolerance': '1/208',
        'selected_kappa_unchanged': '60403/20000000',
    }
    need(input_hashes() == inputs, 'premise inputs changed during replay')
    own_files = ('PROOF.md', 'README.md', 'TASK.json', 'SOURCES.json',
                 'VERIFY.json', 'verify.py')
    output['package_sha256'] = {
        name: sha256((PACKAGE / name).read_bytes()).hexdigest() for name in own_files
    }
    return output


def main():
    arguments = sys.argv[1:]
    need(arguments == [] or len(arguments) == 2 and arguments[0] == '--emit',
         'usage: verify.py [--emit NEW_SCRATCH_FILE]')
    output = result()
    if arguments:
        destination = Path(arguments[1])
        need(destination.is_absolute() and not destination.exists(),
             'receipt destination must be a new absolute scratch path')
        with destination.open('x') as stream:
            stream.write(json.dumps(output, indent=2, sort_keys=True) + '\n')
    else:
        expected = json.loads((PACKAGE / 'RESULT.json').read_text())
        need(output == expected, 'receipt mismatch')
    print('PASS_TERMINAL_APPROXIMATION_FLOOR actual_bank_tolerance=1/208 '
          'minimum_ADDs=2(f-1) no_new_kappa')


if __name__ == '__main__':
    main()
