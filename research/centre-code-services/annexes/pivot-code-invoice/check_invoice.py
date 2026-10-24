#!/usr/bin/env python3
"""Check the existing pivot invoice and the exact inverse division domain."""

import argparse
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PAYLOAD = ('frozen/work/centre-encoding-campaign-20261014/lanes/'
           'new-core-transfer-20261017/low-displacement-20261020/'
           'pivot-codes/final-normal/PIVOT-CODES.json')
PIN = '49044ce1a2ef7a591084ba344e6d13d16e3e47ea56fd977c8c2218aed6b3a670'


def need(value, message):
    if not value:
        raise ValueError(message)


def identity():
    return [{j: Fraction(1)} for j in range(112)]


def invoice(word):
    scalar = multiply = divide = 0
    for op, _, _, value in word:
        c = Fraction(value)
        n, d = abs(c.numerator), c.denominator
        if op == 'fixed_multiply':
            need(c == 3, 'The fixed multiplier is three')
            multiply += 2
        elif op == 'fixed_divide':
            need(c == 3, 'The fixed divisor is three')
            divide += 2
        else:
            need(d & (d - 1) == 0, 'The scalar denominator is binary')
            if op == 'scale':
                need(n and n & (n - 1) == 0, 'The scalar scale is a binary unit')
                scalar += 2 * (abs(n.bit_length() - d.bit_length()) + (c < 0))
            else:
                need(op == 'add', 'The scalar opcode is declared')
                scalar += 2 * (1 + n.bit_length() + n.bit_count() + d.bit_length())
    return {'old_real_scalar_units': scalar, 'real_multiply3_scans': multiply,
            'real_divide3_scans': divide}


def replay(word, initial):
    rows = [dict(row) for row in initial]
    divisions = []
    for index, (op, target, source, value) in enumerate(word):
        need(0 <= target < 112, 'Only the declared data bank changes')
        c = Fraction(value)
        if op == 'add':
            need(0 <= source < 112 and source != target, 'Only distinct data sources')
            row = dict(rows[target])
            for j, v in rows[source].items():
                row[j] = row.get(j, Fraction(0)) + c * v
            rows[target] = {j: v for j, v in row.items() if v}
        else:
            need(op in ('scale', 'fixed_multiply', 'fixed_divide'), 'Declared scalar opcode')
            if op == 'fixed_divide':
                need(c == 3, 'The inverse divisor is three')
                valid = all(v.denominator & (v.denominator - 1) == 0
                            and v.numerator % 3 == 0 for v in rows[target].values())
                divisions.append({'opcode': index, 'field': target,
                                  'all_dyadic_coefficients_divisible_by_three': valid})
                c = 1 / c
            rows[target] = {j: c * v for j, v in rows[target].items() if c * v}
    return rows, divisions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    raw = (HERE / PAYLOAD).read_bytes()
    need(sha256(raw).hexdigest() == PIN, 'Exact retained pivot program')
    data = json.loads(raw)
    forward = data['scalar_words']['code']
    backward = data['scalar_words']['inverse_code']
    forward_invoice, backward_invoice = invoice(forward), invoice(backward)
    need(forward_invoice == {'old_real_scalar_units': 2078, 'real_multiply3_scans': 16,
                             'real_divide3_scans': 0}, 'The forward invoice is exact')
    need(backward_invoice == {'old_real_scalar_units': 2078, 'real_multiply3_scans': 0,
                              'real_divide3_scans': 16}, 'The inverse invoice is exact')
    encoded, _ = replay(forward, identity())
    decoded, valid_divisions = replay(backward, encoded)
    need(decoded == identity(), 'The inverse restores every encoded data column')
    need(len(valid_divisions) == 8 and all(
        row['all_dyadic_coefficients_divisible_by_three'] for row in valid_divisions),
        'Each inverse division is exact on the code image')
    generic, generic_divisions = replay(backward, identity())
    need(any(not row['all_dyadic_coefficients_divisible_by_three']
             for row in generic_divisions), 'A generic inverse needs its grid premise')
    witness = next((i, j, str(v)) for i, row in enumerate(generic)
                   for j, v in row.items() if v.denominator % 3 == 0)
    result = {'status': 'PASS_PIVOT_CODE_INVOICE_DOMAIN', 'payload_sha256': PIN,
              'checker_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
              'forward_invoice': forward_invoice, 'inverse_invoice': backward_invoice,
              'valid_image_divisions': valid_divisions, 'all_112_data_columns_restored': True,
              'generic_inverse_non_dyadic_witness': witness,
              'scope': 'Exact existing literal word and inverse domain; no claim that an arbitrary middle operation preserves the code image.'}
    (args.out / 'CHECKS.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'])


if __name__ == '__main__':
    main()
