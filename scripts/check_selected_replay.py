#!/usr/bin/env python3
"""Bind a completed gen4 finite replay to the selected publication.

Compare every certificate field, preserving JSON types and list order while
allowing object-key order and equivalent exact rational strings. The certificate
has no volatile metadata. Only verification.json's seconds/timings may vary;
all other receipt fields are checked. This check neither runs a supplier nor
proves the retained all-size hypotheses. Use it after the source-bound replay.
"""
import argparse
from decimal import Decimal
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = 'gen4-parity-fused-five-stage-banks/1'
STATUS = 'PASS_IMMUTABLE_PARITY_FUSED_GEN4_FIVE_STAGE_BANKED_CONSTRUCTION'
STAGES = frozenset(('virtual', 'raw', 'bit', 'scalar', 'primes', 'banks',
                    'complex', 'math', 'finite'))
CERTIFICATE_KEYS = frozenset(('assembly', 'binding', 'bit_coarse',
    'bit_moment_interval', 'bit_profile', 'complex_coarse',
    'complex_moment_interval', 'complex_profile', 'finite_bridge',
    'independent_base_two_pass', 'kappa', 'kappa_decimal', 'kappa_scientific',
    'next_bit_grid_excluded', 'ordinary_bootstrap_chain', 'schema', 'scope'))
RECEIPT_KEYS = frozenset(('status', 'manifest_sha256', 'files', 'kappa',
    'kappa_scientific', 'fresh_stages', 'inputs_unchanged', 'timings',
    'seconds', 'negative_controls'))
NUMBER = re.compile(r'[+-]?\d+(?:/\d+|(?:\.\d+)?(?:[eE][+-]?\d+)?)(?=\Z)')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON key: ' + key)
        result[key] = value
    return result


def parse_json(data):
    def invalid_constant(value):
        raise ValueError('Non-finite JSON number: ' + value)
    return json.loads(data, object_pairs_hook=unique_object,
                      parse_float=Decimal, parse_constant=invalid_constant)


def read_json(path):
    return parse_json(path.read_bytes())


def exact(value):
    require(type(value) is str and NUMBER.fullmatch(value) is not None,
            'Expected an exact rational string')
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError('Invalid exact rational: ' + value) from exc


def compare(expected, actual, field='certificate'):
    """Fail on unknown/missing fields, type changes or any mathematical delta."""
    require(type(expected) is type(actual), 'Type differs at ' + field)
    if type(expected) is dict:
        require(expected.keys() == actual.keys(), 'Fields differ at ' + field)
        for key in expected:
            compare(expected[key], actual[key], field + '/' + key)
    elif type(expected) is list:
        require(len(expected) == len(actual), 'Length differs at ' + field)
        for index, (left, right) in enumerate(zip(expected, actual)):
            compare(left, right, field + '/' + str(index))
    elif type(expected) is str:
        if NUMBER.fullmatch(expected) and NUMBER.fullmatch(actual):
            require(exact(expected) == exact(actual), 'Value differs at ' + field)
        else:
            require(expected == actual, 'Value differs at ' + field)
    else:
        require(type(expected) in (int, bool, type(None)),
                'Inexact or unsupported certificate value at ' + field)
        require(expected == actual, 'Value differs at ' + field)


def bound_path(root, name):
    require(type(name) is str, 'Invalid selected path')
    path = (root / name).resolve()
    require(path.is_relative_to(root.resolve()) and path.is_file(),
            'Invalid selected path: ' + name)
    return path


def duration(value):
    return (type(value) is int and value >= 0 or
            type(value) is Decimal and value.is_finite() and value >= 0)


def check(record_path, certificate_path, verification_path, root=ROOT):
    record = read_json(record_path)
    require(type(record) is dict, 'Invalid selected publication record')
    frozen_path = bound_path(root, record['certificate'])
    frozen_bytes = frozen_path.read_bytes()
    require(sha256(frozen_bytes).hexdigest() == record['certificate_sha256'],
            'Selected frozen certificate digest differs')
    frozen = parse_json(frozen_bytes)
    fresh = read_json(certificate_path)
    for certificate in (frozen, fresh):
        require(type(certificate) is dict and set(certificate) == CERTIFICATE_KEYS,
                'Unexpected certificate fields')
        require(certificate['schema'] == SCHEMA, 'Unexpected certificate schema')
    compare(frozen, fresh)
    kappa = exact(fresh['kappa'])
    require(kappa > 0 and kappa == exact(record['kappa']) == exact(record['decimal'])
            == exact(fresh['kappa_decimal']), 'Selected publication kappa differs from replay')

    manifest_path = bound_path(root, record['source_manifest'])
    manifest_bytes = manifest_path.read_bytes()
    manifest = parse_json(manifest_bytes)
    require(type(manifest) is dict and type(manifest.get('files')) is dict and manifest['files'],
            'Empty selected source inventory')
    receipt = read_json(verification_path)
    require(type(receipt) is dict and set(receipt) == RECEIPT_KEYS,
            'Unexpected verification receipt fields')
    require(receipt['status'] == STATUS and receipt['inputs_unchanged'] is True,
            'Replay did not report unchanged successful inputs')
    require(receipt['manifest_sha256'] == sha256(manifest_bytes).hexdigest(),
            'Replay source manifest differs from selection')
    require(type(receipt['files']) is int and receipt['files'] == len(manifest['files']),
            'Replay source file count differs')
    compare(sorted(STAGES), receipt['fresh_stages'], 'verification/fresh_stages')
    compare(['omitted ' + stage + ' stage' for stage in sorted(STAGES)],
            receipt['negative_controls'], 'verification/negative_controls')
    compare(fresh['kappa'], receipt['kappa'], 'verification/kappa')
    compare(fresh['kappa_scientific'], receipt['kappa_scientific'],
            'verification/kappa_scientific')
    require(type(receipt['timings']) is dict and set(receipt['timings']) == STAGES
            and all(duration(value) for value in receipt['timings'].values())
            and duration(receipt['seconds']), 'Invalid replay timing metadata')
    return kappa


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', type=Path, default=ROOT / 'certificates/selected-result.json')
    parser.add_argument('--certificate', type=Path, required=True)
    parser.add_argument('--verification', type=Path, required=True)
    args = parser.parse_args()
    try:
        kappa = check(args.record, args.certificate, args.verification)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(1, 'FAIL selected replay binding: ' + str(exc) + '\n')
    print('PASS selected fresh/frozen finite certificate and source binding: ' + str(kappa))


if __name__ == '__main__':
    main()
