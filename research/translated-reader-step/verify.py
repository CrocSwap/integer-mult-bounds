#!/usr/bin/env python3
"""Check the new reader step. Nick Petalas. Apache-2.0."""
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys

from kernels import require, supplied_factors
from word import apply_word, change, metrics, packed_source, pair_product, prior_basis, translated

HERE = Path(__file__).resolve().parent


def factor_checks(source, reader, new_source, new_reader):
    expected = pair_product(source, reader)
    require(pair_product(new_source, new_reader) == expected,
            'every changed-pair product coefficient')
    require(all(new_source[j] == source[j] for j in range(30) if j != 1),
            'untouched scatter columns')
    require(all(new_reader[j] == reader[j] for j in range(30) if j != 0),
            'untouched gather rows')
    restored_s, restored_d = new_source[:], new_reader[:]
    change(restored_s, restored_d, Fraction(1, 5))
    require(restored_s == source and restored_d == reader, 'inverse basis')
    require(len(new_source[1]) - len(source[1]) == 8, 'eight new scatter terms')
    require(len(reader[0]) - len(new_reader[0]) == 12, 'twelve fewer gather terms')
    return len(expected)


def controls(source, reader):
    expected = pair_product(source, reader)
    rejected = []
    for defect in ('omit-scatter', 'wrong-sign', 'omit-gather', 'wrong-translation'):
        s, d = source[:], reader[:]
        change(s, d)
        if defect == 'omit-scatter':
            s[1] = source[1]
        elif defect == 'wrong-sign':
            other_s, other_d = source[:], reader[:]
            change(other_s, other_d, Fraction(1, 5))
            s[1] = other_s[1]  # The opposite gather is intentionally unused.
        elif defect == 'omit-gather':
            d[0] = reader[0]
        else:
            s[1] = translated(s[1], 1)
        require(pair_product(s, d) != expected, 'reject ' + defect)
        rejected.append(defect)
    for invalid in (-1, 512):
        try:
            translated(reader[1], invalid)
        except ValueError:
            rejected.append('invalid-translation-' + str(invalid))
        else:
            raise ValueError('invalid translation accepted')
    for defect in ('inexact-coefficient', 'missing-mode'):
        try:
            if defect == 'inexact-coefficient':
                change(source[:], reader[:], -0.2)
            else:
                change(source[:29], reader[:])
        except ValueError:
            rejected.append(defect)
        else:
            raise ValueError('invalid input accepted: ' + defect)
    return rejected


def literal_check(source, reader, new_source, new_reader):
    data = [[((port + 7) * (address + 11)) % 17 - 8
             for address in range(512)] for port in range(112)]
    bank = [[((mode + 3) * (address + 5)) % 13 - 6
             for address in range(512)] for mode in range(30)]
    old_out, old_bank, old_count, old_scale = apply_word(source, reader, data, bank)
    new_out, new_bank, new_count, new_scale = apply_word(new_source, new_reader, data, bank)
    for port in range(112):
        for address in range(512):
            require(old_out[port][address] * new_scale == new_out[port][address] * old_scale,
                    'literal data endpoint')
    for mode in range(30):
        for address in range(512):
            require(old_bank[mode][address] == old_scale * bank[mode][address]
                    and new_bank[mode][address] == new_scale * bank[mode][address],
                    'literal arbitrary dirty restoration')
    require((old_count, new_count) == (20320, 20312), 'executed coefficient counts')
    return {'payloads': 1, 'data_coordinates': 57344,
            'dirty_coordinates': 15360, 'executed_counts': [old_count, new_count]}


def invoice_checks(before, after):
    require(before['coefficient_adds'] == 20320 and after['coefficient_adds'] == 20312,
            'strict complete coefficient saving')
    require((after['source_coefficients'], after['reader_coefficients']) == (228, 9928),
            'complete factor supports')
    require((before['common_denominator'], after['common_denominator']) == (960, 4800),
            'charged denominator increase')
    require((before['axis_translation_units'], after['axis_translation_units'])
            == (91924, 91852), 'complete axis invoice')
    require(after['nonidentity_shift_adds'] == 20312, 'every translation charged')
    require((after['maximum_coefficient'], after['source_row_l1'], after['reader_row_l1'])
            == ('9/8', '43/16', '72'), 'coefficient and norm bounds')


def main():
    require(sys.version_info >= (3, 12), 'CPython 3.12 or later')
    columns, reader, directions = supplied_factors()
    source = packed_source(columns, directions)
    prior_basis(source, reader)
    new_s, new_d = source[:], reader[:]
    change(new_s, new_d)
    before, after = metrics(source, reader), metrics(new_s, new_d)
    invoice_checks(before, after)
    compared = factor_checks(source, reader, new_s, new_d)
    rejected = controls(source, reader)
    literal = literal_check(source, reader, new_s, new_d)
    files = sorted(path for path in HERE.iterdir() if path.is_file())
    require(len(files) <= 12, 'package file bound')
    hashes = {path.name: sha256(path.read_bytes()).hexdigest() for path in files}
    print(json.dumps({'status': 'PASS_TRANSLATED_READER_STEP',
                      'before': before, 'after': after,
                      'new_operation': {'source_mode': 1, 'target_mode': 0,
                                        'coefficient': '-1/5', 'translation': 0},
                      'compared_pair_product_coefficients': compared,
                      'rejection_controls': rejected, 'literal': literal,
                      'package_sha256': hashes}, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
