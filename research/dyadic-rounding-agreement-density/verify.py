#!/usr/bin/env python3
"""Exact bounded corroboration of PROOF.md; standard library only."""

import argparse
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
MODULI = (2, 3, 4, 6, 8)
GAPS = (1, 2, 3, 4)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rounded_numerator(numerator, denominator, bits):
    """Numerator of half-up rounding on the grid 2**(-bits)."""
    require(denominator > 0 and 0 <= bits <= 12, 'rounding domain')
    return ((numerator << (bits + 1)) + denominator) // (2 * denominator)


def agrees(numerator, denominator, gap):
    coarse = rounded_numerator(numerator, denominator, 0)
    fine = rounded_numerator(numerator, denominator, gap)
    return (coarse << gap) == fine


def generated_group(modulus, first, second):
    return frozenset(
        ((a * first[0] + b * second[0]) % modulus,
         (a * first[1] + b * second[1]) % modulus)
        for a in range(modulus) for b in range(modulus)
    )


def subgroup_catalogue(modulus):
    vectors = tuple(product(range(modulus), repeat=2))
    groups = {generated_group(modulus, a, b) for a in vectors for b in vectors}
    return sorted(groups, key=lambda group: (len(group), sorted(group)))


def subgroup_census():
    """Enumerate literal roundings, without using the safe-cell criterion."""
    stats = {'subgroups': 0, 'offset_gap_cases': 0, 'point_probes': 0,
             'tight_cases': 0, 'strict_cases': 0}
    sizes = {}
    for modulus in MODULI:
        groups = subgroup_catalogue(modulus)
        sizes[str(modulus)] = len(groups)
        stats['subgroups'] += len(groups)
        for gap in GAPS:
            tests = tuple(tuple(agrees(2 * x + offset, 2 * modulus, gap)
                                for x in range(modulus))
                          for offset in range(2 * modulus))
            for group in groups:
                torsion = sum(all(((1 << gap) * x) % modulus == 0 for x in h)
                              for h in group)
                require(torsion >= 1 and len(group) % torsion == 0,
                        'torsion subgroup cardinality')
                for first, second in product(range(2 * modulus), repeat=2):
                    count = sum(tests[first][x] and tests[second][y]
                                for x, y in group)
                    require(count * torsion <= len(group), 'density bound failed')
                    stats['offset_gap_cases'] += 1
                    stats['point_probes'] += len(group)
                    key = 'tight_cases' if count * torsion == len(group) else 'strict_cases'
                    stats[key] += 1
    stats['subgroups_by_modulus'] = sizes
    return stats


def rounding_oracle():
    count = 0
    for denominator in range(1, 33):
        for numerator in range(-3 * denominator, 3 * denominator + 1):
            value = Fraction(numerator, denominator)
            for bits in range(5):
                scaled = value * (1 << bits) + Fraction(1, 2)
                oracle = scaled.numerator // scaled.denominator
                require(rounded_numerator(numerator, denominator, bits) == oracle,
                        'independent Fraction rounding oracle')
                count += 1
    return count


def sharp_examples():
    cases = probes = 0
    for dimension in range(1, 4):
        for exponents in product(range(1, 5), repeat=dimension):
            for gap in GAPS:
                denominator = 1 << sum(exponents)
                actual = 1
                for exponent in exponents:
                    modulus = 1 << exponent
                    successes = sum(agrees(x, modulus, gap) for x in range(modulus))
                    actual *= successes
                    probes += modulus
                expected = Fraction(1, 1 << sum(min(gap, e) for e in exponents))
                require(Fraction(actual, denominator) == expected, 'sharpness formula')
                cases += 1
    return {'cases': cases, 'scalar_probes': probes}


def period_and_dirty_checks():
    period_cases = dirty_cases = 0
    for modulus in (2, 4, 8):
        for a, b in product(range(modulus), repeat=2):
            image = [(a * x + b * y) % modulus
                     for x, y in product(range(modulus), repeat=2)]
            multiplicities = [image.count(h) for h in sorted(set(image))]
            require(len(set(multiplicities)) == 1, 'uniform image fibers')
            for offset in range(2 * modulus):
                base = sum(agrees(2 * x + offset, 2 * modulus, 2) for x in image)
                doubled = sum(agrees(2 * (a * x + b * y) + offset, 2 * modulus, 2)
                              for x, y in product(range(2 * modulus), repeat=2))
                require(doubled == 4 * base, 'common-denominator independence')
                period_cases += 1
    for numerator in range(-32, 33):
        for gap in GAPS:
            coarse = Fraction(rounded_numerator(numerator, 16, 0))
            fine = Fraction(rounded_numerator(numerator, 16, gap), 1 << gap)
            for target in (Fraction(-7, 3), Fraction(0), Fraction(11, 5)):
                result = target + coarse - fine
                require((result == target) == agrees(numerator, 16, gap),
                        'literal arbitrary-dirty restoration')
                require(result - target == coarse - fine, 'target-independent defect')
                dirty_cases += 1
    return {'period_cases': period_cases, 'dirty_cases': dirty_cases}


def semantic_controls():
    # At a tie, closing both ends would incorrectly accept both H[2] points.
    require(agrees(-1, 4, 1), 'lower tie must be admitted')
    require(not agrees(1, 4, 1), 'upper tie must be excluded')
    require(not agrees(1, 2, 1), 'nonintegral scalar is not universally safe')
    # A cyclic order-eight image has only two 2-torsion points, not eight.
    count = sum(agrees(x, 8, 1) for x in range(8))
    require(count == 4 and count * 8 > 8, 'full-group replacement must fail')
    # Four output coordinates may contain only one independent residue factor.
    diagonal = sum(all(agrees(x, 8, 1) for _ in range(4)) for x in range(8))
    require(diagonal == 4 and diagonal * 16 > 8, 'ambient-dimension bound must fail')
    group = generated_group(4, (1, 2), (0, 0))
    fixed = sum(agrees(x, 4, 1) and agrees(y, 4, 1) for x, y in group)
    require(fixed == 1 and len(group) == 4, 'fixed embedding can be strict')
    require(agrees(0, 8, 1), 'singleton box can be entirely safe')
    odd = sum(agrees(x, 3, 1) for x in range(3))
    require(odd == 1, 'odd-order group can make the bound uninformative')
    return 8


def source_hashes():
    names = ('PROOF.md', 'README.md', 'SOURCES.json', 'TASK.json',
             'VERIFY.json', 'verify.py')
    return {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
            for name in names}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', type=Path)
    parser.add_argument('--check-receipt', type=Path)
    args = parser.parse_args()
    if args.receipt is not None:
        require(not args.receipt.resolve().is_relative_to(PACKAGE),
                'generated receipts must be outside the package')
    result = {'claim_type': 'scoped proof with finite corroboration',
              'subgroup_census': subgroup_census(),
              'rounding_oracle_cases': rounding_oracle(),
              'sharp_examples': sharp_examples(),
              'period_and_dirty': period_and_dirty_checks(),
              'semantic_controls': semantic_controls(),
              'sha256': source_hashes()}
    encoded = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if args.check_receipt is not None:
        # Canonical bytes reject changed values, Boolean integers and extra fields.
        require(args.check_receipt.read_bytes() == encoded.encode(), 'receipt mismatch')
    if args.receipt is not None:
        with args.receipt.open('x', encoding='utf-8') as output:
            require(output.write(encoded) == len(encoded), 'short receipt write')
    print(encoded, end='')
    print('PASS_DYADIC_ROUNDING_AGREEMENT_DENSITY')


if __name__ == '__main__':
    main()
