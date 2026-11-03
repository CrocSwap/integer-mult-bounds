"""Additive control receipts. Source-only draft; importing is not admission.

Gates deliberately do not use assert, including in optimized Python.
"""
from hashlib import sha256
import json

SCHEMA = 'h25-native-field-control-receipt-v1'


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def plain(value, depth=0):
    need(depth < 12, 'control receipt depth')
    if value is None or type(value) in (bool, int, str):
        if type(value) is str:
            need(len(value) <= 4096, 'control receipt string bound')
        return
    need(type(value) in (tuple, list, dict), 'control receipt foreign value')
    need(len(value) <= 1024, 'control receipt collection bound')
    if type(value) is dict:
        need(all(type(k) is str for k in value), 'control receipt key type')
        for k, v in value.items():
            plain(k, depth + 1)
            plain(v, depth + 1)
    else:
        for v in value:
            plain(v, depth + 1)


def record(case_id, observed, expected, details=None):
    plain(observed)
    plain(expected)
    details = {} if details is None else details
    plain(details)
    need(type(details) is dict, 'control details exact type')
    need(type(case_id) is str, 'control case id type')
    need(type(observed) is dict and type(expected) is dict, 'control observation shape')
    need(observed == expected, 'control expectation differs: ' + case_id)
    # Only the actual runner calls this after collecting its observation.
    return {'case_id': case_id, 'status': 'OBSERVED_EXPECTATION_MATCH',
            'observed': observed, 'expected': expected, 'details': details}


def validate(receipt, case_ids, literal_count, expected_by_case, mode):
    plain(receipt)
    need(type(receipt) is dict and set(receipt) ==
         {'schema', 'mode', 'case_count', 'records', 'observation_sha256'},
         'control receipt exact keys')
    need(type(mode) is str and mode in ('normal', 'optimized'), 'control mode')
    need(receipt['schema'] == SCHEMA and receipt['mode'] == mode, 'control receipt schema/mode')
    need(type(literal_count) is int and type(receipt['case_count']) is int and
         receipt['case_count'] == literal_count == len(case_ids) == len(expected_by_case),
         'control receipt literal count')
    rows = receipt['records']
    need(type(rows) is list and len(rows) == literal_count, 'control record count')
    need(tuple(r.get('case_id') for r in rows if type(r) is dict) == case_ids,
         'control record order/duplicate/missing')
    for row in rows:
        need(set(row) == {'case_id', 'status', 'observed', 'expected', 'details'}, 'control record exact keys')
        need(row['status'] == 'OBSERVED_EXPECTATION_MATCH', 'control record status')
        expected = expected_by_case[row['case_id']]
        need(row['expected'] == expected and row['observed'] == expected,
             'control receipt independent expectation')
    encoded = json.dumps(rows, sort_keys=True, separators=(',', ':')).encode('ascii')
    need(type(receipt['observation_sha256']) is str and
         receipt['observation_sha256'] == sha256(encoded).hexdigest(), 'control observation digest')
    return receipt


def finish(rows, case_ids, literal_count, expected_by_case, mode):
    receipt = {'schema': SCHEMA, 'mode': mode, 'case_count': len(rows), 'records': rows,
               'observation_sha256': sha256(json.dumps(rows, sort_keys=True,
                 separators=(',', ':')).encode('ascii')).hexdigest()}
    return validate(receipt, case_ids, literal_count, expected_by_case, mode)
