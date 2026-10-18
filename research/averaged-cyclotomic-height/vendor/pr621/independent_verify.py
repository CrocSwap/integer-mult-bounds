#!/usr/bin/env python3
"""Check the cyclotomic identities with independent SymPy arithmetic."""

import argparse
import json
from math import gcd
from pathlib import Path
from sympy import Poly, QQ, Symbol, cyclotomic_poly
from sympy.polys.matrices import DomainMatrix


def require(condition):
    if not condition:
        raise ValueError('Exact identity check failed')


def check(q, power):
    x, z = (Symbol('x'), Symbol('z'))
    field = QQ.alg_field_from_poly(Poly(cyclotomic_poly(q, x), x), alias='u')
    u = field([1, 0])
    n = q - 1
    residue_prime = int(cyclotomic_poly(q, x).subs(x, 1))
    require(residue_prime >= 2)

    def embed(value, exponent):
        result = field.zero
        root = u ** (exponent % q)
        for coefficient in value.to_list():
            result = result * root + field(coefficient)
        return result

    def encode(value):
        return [str(coefficient) for coefficient in value.to_list()]

    prefix = field.one
    f = []
    for j in range(q):
        if j:
            prefix *= field.one - u ** (power * j % q)
        f.append(field(q) / prefix)
    require(f[0] == field(q) and f[-1] == field.one)
    for j in range(q):
        product = field.one
        for s in range(j + 1, q):
            product *= field.one - u ** (power * s % q)
        require(f[j] == product)
        coefficients = f[j].to_list()
        require(all((coefficient.denominator == 1 for coefficient in coefficients)))
        require(int(sum(coefficients)) % residue_prime == (1 if j == n else 0))
    star = [embed(value, -1) for value in reversed(f)]
    matrix = [[field.zero] * (2 * n) for _ in range(2 * n)]
    for polynomial, start in ((f, 0), (star, n)):
        for offset in range(n):
            for degree, coefficient in enumerate(polynomial):
                matrix[degree + offset][start + offset] = coefficient
    dm = DomainMatrix(matrix, (2 * n, 2 * n), field)
    determinant = dm.det()
    require(determinant != field.zero)
    require(embed(determinant, -1) == determinant)
    require(all(coefficient.denominator == 1
                for coefficient in determinant.to_list()))
    require(int(sum(determinant.to_list())) % residue_prime
            == (-1) ** n % residue_prime)
    inverse = dm.inv().to_list()
    cofactor_column = [row[0] * determinant for row in inverse]
    require(all(coefficient.denominator == 1
                for value in cofactor_column for coefficient in value.to_list()))
    for row, values in enumerate(matrix):
        actual = sum((value * cofactor for value, cofactor in
                      zip(values, cofactor_column)), field.zero)
        require(actual == (determinant if row == 0 else field.zero))
    real_norm = field.one
    for exponent in range(1, q // 2 + 1):
        if gcd(exponent, q) == 1:
            real_norm *= embed(determinant, exponent)
    require(len(real_norm.to_list()) == 1)
    require(real_norm.to_list()[0].denominator == 1)
    require(real_norm != field.zero)
    full_norm = field.one
    for exponent in range(1, q):
        if gcd(exponent, q) == 1:
            full_norm *= embed(determinant, exponent)
    require(full_norm == real_norm * real_norm)
    fp = Poly.from_list(list(reversed(f)), z, domain=field)
    gp = Poly.from_list(list(reversed(star)), z, domain=field)
    require(fp.gcd(gp).degree() == 0)
    require(fp.rep.resultant(gp.rep) == field((-1) ** n) * determinant)
    inverse_checks = []
    pp = fp.quo_ground(q)
    for length in (1, 2, 4, 8):
        modulus = Poly(z ** length - 1, z, domain=field)
        reciprocal = pp.invert(modulus)
        require((pp * reciprocal).rem(modulus) == Poly(1, z, domain=field))
        inverse_checks.append(length)
    unit = Poly(z ** n - 1, z, domain=field)
    unit_star = -unit
    require(unit.resultant(unit_star) == 0)
    missing_conjugation = Poly.from_list(f, z, domain=field)
    bad = False
    for exponent in range(q):
        point = u ** exponent
        v = fp.rep.eval(point)
        r = missing_conjugation.rep.eval(point)
        if v * embed(v, -1) != r * embed(r, -1):
            bad = True
            break
    require(bad)
    return {
        'order': q,
        'residue_prime': residue_prime,
        'field_degree': int(field.mod.degree()),
        'primitive_power': power,
        'coefficient_order': 'descending powers of u',
        'resultant': encode(determinant),
        'real_subfield_norm': encode(real_norm)[0],
        'full_field_norm': encode(full_norm)[0],
        'cofactor_identity': True,
        'primitive_ideal_reduction': 'f=z^(order-1), determinant=(-1)^(order-1)',
        'exact_cyclic_inverse_lengths': inverse_checks,
        'unit_root_negative_control': 'zero resultant',
        'missing_conjugation_negative_control': 'different exact squared modulus',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    cases = [check(radix, power) for radix, power in
             ((3, 1), (4, 1), (5, 2), (7, 1), (8, 1), (8, 3),
              (9, 1), (11, 1), (11, 4))]
    result = {
        'status': 'PASS',
        'scope': 'Exact finite identities. The written proof supplies the uniform theorem.',
        'cases': cases,
    }
    payload = json.dumps(result, indent=2) + '\n'
    if args.output is None:
        print(payload, end='')
    else:
        args.output.write_text(payload)
