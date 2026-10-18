#!/usr/bin/env python3
"""Compare every Leech row and the complete nine-screen certificate."""
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from replay import ROOT, certificate, require


def verify():
    streams = {}
    payloads = {}
    executed = {}
    for mode in ('baseline', 'lanes'):
        streams[mode] = []
        payloads[mode], executed[mode] = certificate(mode, streams[mode].append)
    require(payloads['baseline'] == payloads['lanes'], 'Certificate mismatch')
    require(streams['baseline'] == streams['lanes'], 'Full row stream mismatch')
    fixtures = json.loads((ROOT / 'scripts/experiments/affine_vector_witnesses.json').read_text())
    require(len(streams['baseline']) == len(fixtures['leech']) == 5,
            'Incomplete Leech fixture coverage')
    cases = []
    for fixture, rows in zip(fixtures['leech'], streams['lanes']):
        columns = len(fixture['global_indices'])
        require(len(rows) == len(fixture['independent_rows']), 'Missing rows')
        cases.append({'shift': fixture['shift'], 'signed': fixture['signed'],
                      'rows': len(rows), 'columns': columns,
                      'rows_sha256': sha256(b''.join(
                          r.to_bytes((columns + 7) // 8, 'little') for r in rows)).hexdigest()})
    result = {'status': 'PASS_LEECH_BYTE_LANES', 'assignment_seed': 86,
              'cases': cases, 'full_rows_compared': sum(x['rows'] for x in cases),
              'matrix_entries_compared': sum(x['rows'] * x['columns'] for x in cases),
              'complete_certificate_sha256': sha256(payloads['lanes']).hexdigest(),
              'executed_geometry_sha256': executed,
              'scope': 'Five historical Leech minors and unchanged nine-screen certificate; no new kappa.'}
    return result


def check_receipt(result):
    expected = HERE / 'EXPECTED.json'
    require(expected.is_file(), 'Missing expected receipt')
    require(result == json.loads(expected.read_text()), 'Stored verification receipt differs')


if __name__ == '__main__':
    result = verify()
    check_receipt(result)
    print(json.dumps(result, indent=2, sort_keys=True))
    print('PASS_LEECH_BYTE_LANES all_frozen_rows_equal=true cases=5')
