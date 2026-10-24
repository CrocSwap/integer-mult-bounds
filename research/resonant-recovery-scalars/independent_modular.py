#!/usr/bin/env python3
"""Independent packed-monomial modular check of the odd denominator witness.

Does not import the primary checker or execute the predecessor's code.
The exact proof remains in README.md and the primary integer certificate.
"""
import argparse
import ast
from fractions import Fraction
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUT = HERE.parent / 'resonant-all-width-projector'
PINS = {'verify.py': '29554fca57ad1b91469cbd65543882ebdaf8cafa93b8dc2ff37b00baef03e930',
        'TARGET.json': 'e7df852b5c641f326ac67cd35cea8da6cfdd059fa12df1cf6fb758bb4206d684'}
IDENTITY = bytes(list(range(8)) + [0] * 8)
MINUS = bytes(list(range(8)) + [2] * 8)
WITNESS = bytes([0, 1, 3, 2, 4, 5, 7, 6, 0, 0, 1, 3, 0, 0, 3, 1])
MODULUS = 3 ** 5 * 5 * 7


def require(ok, message):
    if not ok:
        raise ValueError(message)


def compose(first, second):
    """Packed permutation/phase composition, applying second first."""
    out = bytearray(16)
    for column in range(8):
        middle = second[column]
        out[column] = first[middle]
        out[8 + column] = (second[8 + column] + first[8 + middle]) & 3
    return bytes(out)


def inverse(word):
    out = bytearray(16)
    for column in range(8):
        row = word[column]
        out[row] = column
        out[8 + row] = (-word[8 + column]) & 3
    return bytes(out)


def inputs():
    raw = {}
    for name, pin in PINS.items():
        data = (INPUT / name).read_bytes()
        require(hashlib.sha256(data).hexdigest() == pin, 'independent input hash: ' + name)
        raw[name] = data
    polynomial = None
    for node in ast.parse(raw['verify.py']).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'POLY' for t in node.targets):
            polynomial = ast.literal_eval(node.value)
    require(polynomial is not None and len(polynomial) == 19, 'literal polynomial')
    records = json.loads(raw['TARGET.json'])
    A = {}
    for record in records:
        p, phase = record['permutation'], record['phase_i']
        coefficient = Fraction(record['coefficient']) * 16
        require(sorted(p) == list(range(8)) and len(phase) == 8 and all(0 <= x < 4 for x in phase), 'literal monomial')
        require(coefficient in (-1, 1), 'literal coefficient')
        word = bytes(p + phase)
        require(word not in A, 'duplicate target term')
        A[word] = int(coefficient)
    require(len(A) == 256, 'target support')
    return polynomial, A


def factors(A):
    generators = [MINUS, bytes([j ^ 1 for j in range(8)] + [1] * 8)]
    generators += [bytes(list(range(8)) + [2 * ((j >> bit) & 1) for j in range(8)]) for bit in range(3)]
    subgroup = {IDENTITY}
    for g in generators:
        subgroup.update([compose(g, h) for h in tuple(subgroup)])
    require(len(subgroup) == 32, 'output subgroup')
    require(all({compose(g, h) for h in subgroup} == subgroup for g in generators),
            'literal subgroup closure')
    remaining = set(A)
    representatives = []
    while remaining:
        word = min(remaining)
        orbit = {compose(h, word) for h in subgroup}
        require(orbit <= remaining and all(A[h] == A[word] for h in orbit), 'signed left-coset factorization')
        representatives.append((word, A[word]))
        remaining.difference_update(orbit)
    require(len(representatives) == 8, 'eight signed cosets')
    r0 = representatives[0][0]
    ri = inverse(r0)
    b = [(compose(ri, word), sign) for word, sign in representatives]
    d = [compose(compose(ri, word), r0) for word in generators]
    return b, d


def action(b, d):
    letters = list(dict.fromkeys([g for g, _ in b] + d + [inverse(g) for g, _ in b]))
    # Right-generator enumeration is independent of the source's left BFS.
    group = [IDENTITY]
    positions = {IDENTITY: 0}
    for word in group:
        for generator in letters:
            next_word = compose(word, generator)
            if next_word not in positions:
                positions[next_word] = len(group)
                group.append(next_word)
                require(len(group) <= 21504, 'group bound')
    require(len(group) == 21504, 'group cardinality')
    tables = {g: [positions[compose(g, word)] for word in group] for g in letters}
    n = len(group)

    def sum_translates(vector, weighted):
        output = [0] * n
        for word, sign in weighted:
            table = tables[word]
            for index, value in enumerate(vector):
                output[table[index]] += sign * value
        return [value % MODULUS for value in output]

    def apply_H(vector):
        current = sum_translates(vector, b)
        for g in reversed(d):
            table = tables[g]
            changed = current[:]
            for index, value in enumerate(current):
                changed[table[index]] += value
            current = [value % MODULUS for value in changed]
        current = sum_translates(current, [(inverse(g), sign) for g, sign in b])
        return [(value * ((MODULUS + 1) // 2)) % MODULUS for value in current]

    return group, positions, apply_H


def valuation(number, prime):
    require(number != 0, 'valuation of nonzero residue')
    count = 0
    while number % prime == 0:
        number //= prime
        count += 1
    return count


def verify():
    polynomial, A = inputs()
    b, d = factors(A)
    group, positions, apply_H = action(b, d)
    q = polynomial[1:]
    vector = [0] * len(group)
    vector[positions[IDENTITY]] = 1
    for k in range(16, -1, -1):
        vector = apply_H(vector)
        vector[positions[IDENTITY]] = (vector[positions[IDENTITY]] + q[k] * pow(64, 17-k, MODULUS)) % MODULUS
    require(not any(apply_H(vector)), 'independent modular annihilator')
    negative = compose(MINUS, WITNESS)
    value = (-vector[positions[WITNESS]] - vector[positions[negative]]) % MODULUS
    denominator = q[0] * 64 ** 17
    expected_numerator = Fraction(1243, 3870720) * denominator
    require(expected_numerator.denominator == 1, 'integer raw witness numerator')
    require(value == expected_numerator.numerator % MODULUS, 'independent even witness residue')
    valuation_receipt = []
    for prime, exponent in ((3, 5), (5, 1), (7, 1)):
        residue = value % prime ** exponent
        nv = valuation(residue, prime)
        dv = valuation(abs(denominator), prime)
        require(nv < exponent and dv - nv == (3 if prime == 3 else 1), 'odd-prime denominator valuation')
        valuation_receipt.append({'prime': prime, 'modulus': prime ** exponent, 'raw_numerator_residue': residue,
                                  'numerator_valuation': nv, 'denominator_valuation': dv,
                                  'reduced_denominator_valuation': dv-nv})
    controls = []
    require((-vector[positions[WITNESS]]) % MODULUS != value, 'negative representative omission')
    controls.append('omit_negative_word')
    changed = vector[:]
    changed[positions[IDENTITY]] = (changed[positions[IDENTITY]] + pow(64, 17, MODULUS)) % MODULUS
    require(any(apply_H(changed)), 'constant polynomial mutation')
    controls.append('constant_polynomial_mutation')
    quarter = bytes(list(range(8)) + [1] * 8)
    require(compose(quarter, quarter) == MINUS and MINUS != IDENTITY, 'quarter-phase square')
    # At f=2 the actual central quarter phase acts as -1, not +1.
    require((quarter[8] + quarter[8]) % 4 == 2, 'literal width-two central phase')
    controls.append('quarter_phase_collapse_at_width_two')
    orientation_word = next(g for g in A if inverse(g) != g and g[:8] != IDENTITY[:8])
    require(compose(inverse(orientation_word), orientation_word) == IDENTITY
            and compose(orientation_word, orientation_word) != IDENTITY,
            'orientation-sensitive monomial inverse')
    controls.append('inverse_orientation')
    return {'status': 'PASS_INDEPENDENT_RESONANT_SCALARS', 'source_pins': PINS,
            'group_size': len(group), 'modulus': MODULUS, 'even_witness_raw_residue': value,
            'odd_prime_valuations': valuation_receipt, 'negative_controls': controls,
            'scope': 'Independent finite modular corroboration of the exact source projector coefficient; not a replacement for exact integer or all-even faithfulness proofs.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = verify()
    path = HERE / 'INDEPENDENT.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        require(json.loads(path.read_text()) == result, 'independent receipt')
    print(result['status'])


if __name__ == '__main__':
    main()
