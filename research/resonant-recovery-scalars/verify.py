#!/usr/bin/env python3
"""Exact scalar localization for the source-bound resonant support recovery."""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE = 'research/resonant-all-width-projector'
SOURCE_PINS = {
    'verify.py': '29554fca57ad1b91469cbd65543882ebdaf8cafa93b8dc2ff37b00baef03e930',
    'TARGET.json': 'e7df852b5c641f326ac67cd35cea8da6cfdd059fa12df1cf6fb758bb4206d684',
}
WITNESS = ((0, 1, 3, 2, 4, 5, 7, 6), (0, 0, 1, 3, 0, 0, 3, 1))
EXPECTED_COEFFICIENT = Fraction(1243, 3870720)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def factor(number):
    number = abs(number)
    require(number > 0, 'factor positive integer')
    out = {}
    prime = 2
    while prime * prime <= number:
        while number % prime == 0:
            out[prime] = out.get(prime, 0) + 1
            number //= prime
        prime += 1
    if number > 1:
        out[number] = 1
    return out


def even_class(word):
    """Canonical representative modulo precisely the actual central {-I,I}."""
    permutation, phase = word
    subtract = 2 * (phase[0] // 2)
    return permutation, tuple((x - subtract) % 4 for x in phase)


def load_source():
    for filename, expected in SOURCE_PINS.items():
        data = (ROOT / SOURCE / filename).read_bytes()
        require(hashlib.sha256(data).hexdigest() == expected, 'source hash: ' + filename)
    source = ROOT / SOURCE / 'verify.py'
    module = types.ModuleType('pinned_resonant_projector')
    module.__file__ = str(source)
    exec(compile(source.read_bytes(), str(source), 'exec'), module.__dict__)
    return module


def verify():
    source = load_source()
    raw, ds, b, d, H = source.load_factorization()
    group, apply_H, identity, hv = source.build_action(b, d, H)
    numer, denominator, bound = source.polynomial_certificate(group, apply_H, identity)
    # Source checks the exact integer annihilator, not just a sampled spectrum.
    coefficients = {g: Fraction(n, denominator) for g, n in zip(group, numer) if n}
    minus = (tuple(range(8)), (2,) * 8)
    for g, c in coefficients.items():
        require(coefficients.get(source.mul(minus, g), 0) == c, 'central minus invariance')
    quotient = {}
    for g, c in coefficients.items():
        key = even_class(g)
        quotient[key] = quotient.get(key, Fraction()) + c
    quotient = {g: c for g, c in quotient.items() if c}
    require(len(group) == 21504 and len(coefficients) == 21056 and len(quotient) == 10528,
            'group/projector/even-class support counts')
    lcd = math.lcm(*(c.denominator for c in quotient.values()))
    require(lcd == 3870720, 'minimal even-class coefficient denominator')
    require(factor(lcd) == {2: 12, 3: 3, 5: 1, 7: 1}, 'denominator factorization')
    require(quotient[WITNESS] == EXPECTED_COEFFICIENT, 'explicit simultaneous odd-prime witness')
    require(math.gcd(EXPECTED_COEFFICIENT.numerator, lcd) == 1, 'witness reduced')

    # Sufficiency concerns a decoder, not merely coefficients of P.
    # q is source POLY/x; R(t)=-(q(t)-q(0))/(t*q(0)).
    q = source.POLY[1:]
    require(q[0] == -40131624960, 'source nonzero constant')
    q0_factors = factor(q[0])
    require(q0_factors == {2: 19, 3: 7, 5: 1, 7: 1}, 'actual decoder scalar prime set')
    inverse_poly = [-Fraction(c, q[0]) for c in q[1:]]
    # Polynomial tR(t)=1-q(t)/q(0), before evaluating C=A*A/16.
    left = [Fraction()] + inverse_poly
    right = [Fraction(1)] + [Fraction()] * (len(q) - 1)
    right = [a - Fraction(c, q[0]) for a, c in zip(right, q)]
    require(left == right, 'actual recovery polynomial identity')
    allowed = {2, 3, 5, 7}
    require(all(set(factor(c.denominator)) <= allowed for c in inverse_poly), 'inverse polynomial localization')
    records = json.loads(raw)
    require(all(Fraction(r['coefficient']).denominator == 16 for r in records), 'A is dyadic')
    # C and A*/16 add only powers of 2; R(C)A*/16 is the actual sufficient decoder.
    controls = []
    for missing in (3, 5, 7):
        available = allowed - {missing}
        require(not set(factor(EXPECTED_COEFFICIENT.denominator)) <= available,
                'missing-prime ring incorrectly admitted')
        controls.append('omit_scalar_prime_' + str(missing))
    iword = (tuple(range(8)), (1,) * 8)
    require(even_class(minus) == source.IDENTITY and even_class(iword) != source.IDENTITY,
            'only signs are identified')
    controls.append('do_not_collapse_quarter_phase')
    require(even_class(WITNESS) == WITNESS and quotient[WITNESS] != coefficients[WITNESS],
            'both signs contribute to even coefficient')
    controls.append('do_not_drop_negative_representative')
    bad_left = left[:]
    bad_left[1] = -bad_left[1]
    require(bad_left != right, 'inverse sign mutation')
    controls.append('inverse_polynomial_sign')
    return {
        'status': 'PASS_RESONANT_RECOVERY_SCALARS',
        'source_pins': SOURCE_PINS,
        'source_group_order': len(group),
        'source_projector_support': len(coefficients),
        'even_quotient_support': len(quotient),
        'even_projector_coefficient_lcd': lcd,
        'lcd_factorization': {str(p): e for p, e in factor(lcd).items()},
        'witness': {'permutation': list(WITNESS[0]), 'phase_i': list(WITNESS[1]),
                    'coefficient': str(quotient[WITNESS]),
                    'single_signed_word_coefficient': str(coefficients[WITNESS])},
        'denominator_histogram': {str(d): count for d, count in sorted(Counter(c.denominator for c in quotient.values()).items())},
        'recovery': {'q0': q[0], 'q0_factorization': {str(p): e for p, e in q0_factors.items()},
                     'R_low_first': list(map(str, inverse_poly)), 'formula': 'R(A* A / 16) A* / 16'},
        'necessary_and_sufficient_odd_primes': [3, 5, 7],
        'negative_controls': controls,
        'scope': 'Fixed finite uniform monomial-linear exact recovery of the canonical orthogonal input projection, over Z[i,1/2,1/S], for every positive even width. No oblique, width-dependent, approximate or physical-runtime obstruction.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = verify()
    target = HERE / 'RESULT.json'
    if args.write:
        target.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        require(json.loads(target.read_text()) == result, 'frozen receipt')
    print(result['status'])


if __name__ == '__main__':
    main()
