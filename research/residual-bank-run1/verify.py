#!/usr/bin/env python3
"""Offline verification of the rank-22 bank-absorption accounting construction.

Read-only unless --write: pins every vendored input byte, rebuilds the absorption
schedule and the exact arithmetic from those inputs, and reproduces certificate.json.

    python3 -B verify.py           # check
    python3 -B verify.py --write   # authoring: regenerate certificate.json and SOURCE.json

The physical realization obligations (R1-R4, obligations.json) are checked for
presence and are NOT discharged here; the certificate's scope says so literally.
"""
import argparse
import json
import sys
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

PINNED = [
    'inputs/absorbed-occurrences.json',
    'references/pr193-source-assisted-v4.certificate.json',
    'references/pr200-bit.certificate.json',
    'references/pr205-packed.certificate.json',
    'interval_moment.py',
    'paired_cube_assembly.py',
    'banks.py',
    'obligations.json',
]


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def pins():
    manifest = json.loads((HERE / 'SOURCE.json').read_text())
    actual = {name: digest(HERE / name) for name in PINNED}
    assert actual == manifest['files'], 'Pinned input bytes changed'
    return actual


def serial(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


def build():
    import schedule as sched
    import arithmetic as arith
    schedule = sched.build()
    arith_result = arith.build(schedule)
    obligations = json.loads((HERE / 'obligations.json').read_text())
    open_ids = [o['id'] for o in obligations['obligations']]
    assert open_ids == ['R1', 'R2', 'R3', 'R4'] and all(o['status'] == 'OPEN' for o in obligations['obligations'])
    occ = json.loads((HERE / 'inputs/absorbed-occurrences.json').read_text())
    kappa = arith_result['after_assembly']['kappa']
    record = {
        'status': 'CONDITIONAL accounting construction for the rank-22 bank absorption: '
                  'schedule, retained ledger, whole-bank volume, exact paid moments, finite '
                  'ordinary composition and balanced assembly are certified here; the physical '
                  'realization obligations R1-R4 (obligations.json) are OPEN and the kappa below '
                  'is conditional on them. Not a completed finite witness; not an unconditional '
                  'multiplication theorem.',
        'kappa': kappa,
        'decimal': float(kappa),
        'binding': arith_result['after_assembly']['binding'],
        'new_residual_type': {
            'rank': schedule['absorbed_family']['rank'],
            'occurrences_three_copies': schedule['absorbed_family']['occurrences_three_copies'],
            'dirt_volume_registers': schedule['absorbed_family']['dirt_volume_registers'],
            'banks': schedule['banks']['banks_from_volume'],
            'provenance_counts_per_vertex': schedule['absorbed_family']['provenance_counts_per_vertex'],
        },
        'schedule': schedule,
        'arithmetic': arith_result,
        'obligations': open_ids,
        'comparison': {
            'main_reviewed_kappa': '330942774629799/500000000000000000',
            'pr205_packed_kappa': '683061299399923/1000000000000000000',
            'pr208_priced_rung1_target': '7004273/10^10',
            'complex_cap': str(arith_result['complex_coarse']),
        },
        'source_pins': {name: digest(HERE / name) for name in PINNED},
    }
    return serial(record)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='authoring: regenerate certificate.json')
    args = parser.parse_args()
    assert not sys.flags.optimize, 'assertions must stay enabled'
    before = None if args.write else pins()
    record = build()
    target = HERE / 'certificate.json'
    if args.write:
        manifest = {'files': {name: digest(HERE / name) for name in PINNED}}
        (HERE / 'SOURCE.json').write_text(json.dumps(manifest, indent=1, sort_keys=True) + '\n')
        target.write_text(json.dumps(record, indent=1, sort_keys=True) + '\n')
    else:
        assert record == json.loads(target.read_text()), 'certificate.json differs'
        assert pins() == before, 'inputs changed during verification'
    print('PASS rank-22 absorption schedule, retained ledger, whole-bank volume, exact moments, '
          'ordinary composition, 47-constraint assembly; obligations R1-R4 open')
    print('conditional kappa = ' + str(record['kappa']))


if __name__ == '__main__':
    main()
