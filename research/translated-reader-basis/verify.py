#!/usr/bin/env python3
"""Verify one translated dyadic reader improvement. Nick Petalas. Apache-2.0."""
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys

from kernels import require, supplied_factors
from word import apply_word, change, metrics, packed_source, pair_product, translated

HERE = Path(__file__).resolve().parent


def factor_checks(source, reader, changed_source, changed_reader):
    expected = pair_product(source, reader)
    require(pair_product(changed_source, changed_reader) == expected,
            'every coefficient of the changed pair product')
    require(all(changed_source[j] == source[j] for j in range(30) if j != 1),
            'untouched scatter columns')
    require(all(changed_reader[j] == reader[j] for j in range(30) if j != 4),
            'untouched gather rows')
    require(translated(translated(reader[1], 258), 258) == reader[1],
            'literal translation involution')
    restored_s, restored_d = changed_source[:], changed_reader[:]
    change(restored_s, restored_d, Fraction(-2))
    require(restored_s == source and restored_d == reader, 'literal inverse basis')
    return len(expected)


def controls(source, reader, expected):
    count = 0
    for defect in ('omit-scatter', 'wrong-scatter-sign', 'wrong-scatter-shift', 'omit-gather'):
        s, d = source[:], reader[:]
        change(s, d)
        if defect == 'omit-scatter':
            s[1] = source[1]
        elif defect == 'wrong-scatter-sign':
            s[1] = source[1]
            reverse_s, reverse_d = source[:], reader[:]
            change(reverse_s, reverse_d, Fraction(-2))
            # Only the wrong scatter is used; the changed gather is intentional discard.
            s[1] = reverse_s[1]
        elif defect == 'wrong-scatter-shift':
            other_s, other_d = source[:], reader[:]
            change(other_s, other_d, shift=259)
            s[1] = other_s[1]
        else:
            d[4] = reader[4]
        require(pair_product(s, d) != expected, 'reject ' + defect)
        count += 1
    for invalid in (-1, 512):
        try:
            translated(reader[1], invalid)
        except ValueError:
            count += 1
        else:
            raise ValueError('invalid translation accepted')
    return count


def literal_check(source, reader, changed_source, changed_reader):
    data = [[((port + 7) * (address + 11)) % 17 - 8
             for address in range(512)] for port in range(112)]
    bank = [[((mode + 3) * (address + 5)) % 13 - 6
             for address in range(512)] for mode in range(30)]
    old_out, old_bank, old_count, old_scale = apply_word(source, reader, data, bank)
    new_out, new_bank, new_count, new_scale = apply_word(changed_source, changed_reader, data, bank)
    checked_data = checked_bank = 0
    for port in range(112):
        for address in range(512):
            require(old_out[port][address] * new_scale == new_out[port][address] * old_scale,
                    'complete literal data endpoint')
            checked_data += 1
    for mode in range(30):
        for address in range(512):
            require(old_bank[mode][address] == old_scale * bank[mode][address]
                    and new_bank[mode][address] == new_scale * bank[mode][address],
                    'complete literal dirty restoration')
            checked_bank += 1
    require((old_count, new_count) == (20352, 20320), 'executed coefficient counts')
    return {'payloads': 1, 'data_coordinates': checked_data,
            'dirty_coordinates': checked_bank, 'executed_counts': [old_count, new_count]}


def main():
    require(sys.version_info >= (3, 12), 'CPython 3.12 or later')
    columns, reader, directions = supplied_factors()
    source = packed_source(columns, directions)
    changed_s, changed_d = source[:], reader[:]
    change(changed_s, changed_d)
    before, after = metrics(source, reader), metrics(changed_s, changed_d)
    require(before['coefficient_adds'] == 20352 and after['coefficient_adds'] == 20320,
            'strict complete coefficient saving')
    require(before['common_denominator'] == after['common_denominator'] == 960,
            'unchanged common denominator')
    require((after['source_coefficients'], after['reader_coefficients']) == (220, 9940),
            'complete factor support counts')
    require((before['axis_translation_units'], after['axis_translation_units']) == (92036, 91924),
            'complete axis-translation invoice')
    require((after['maximum_coefficient'], after['source_row_l1'], after['reader_row_l1'])
            == ('9/8', '43/16', '72'), 'new coefficient and norm costs')
    compared = factor_checks(source, reader, changed_s, changed_d)
    rejected = controls(source, reader, pair_product(source, reader))
    literal = literal_check(source, reader, changed_s, changed_d)
    files = sorted(path for path in HERE.iterdir() if path.is_file())
    require(len(files) <= 12, 'package file bound')
    hashes = {path.name: sha256(path.read_bytes()).hexdigest() for path in files}
    print(json.dumps({'status': 'PASS_TRANSLATED_READER_BASIS',
                      'before': before, 'after': after,
                      'operation': {'source_mode': 1, 'target_mode': 4,
                                    'coefficient': '2', 'translation': 258},
                      'compared_pair_product_coefficients': compared,
                      'rejection_controls': rejected, 'literal': literal,
                      'package_sha256': hashes}, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
