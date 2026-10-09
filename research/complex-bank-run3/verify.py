#!/usr/bin/env python3
"""Offline verification of the rungs 3 and 4 ledgers, their prices and their assemblies.

Read-only unless `--write`: pins every vendored byte, rebuilds the whole complex-side ladder
(base, rung 2, rungs 3 and 4), both paid moments per rung, the two 47-constraint assemblies,
the PR208-convention replica and the eligibility scan, and compares the result with
`certificate.json`.

    python3 -B verify.py           # check
    python3 -B verify.py --write   # authoring: regenerate certificate.json and SOURCE.json

The complex-side bank construction obligations (C1-C7 and T1 in `obligations.json`, plus the
inherited R1-R4 of #219) are checked for presence and are **not** discharged here; the
certificate's scope says so literally.  Passing this script means the accounting is
consistent and the prices are exact -- not that the rung is physical.
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

import pins  # noqa: E402
import run3  # noqa: E402
import schedule66  # noqa: E402


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def read_manifest():
    return json.loads((HERE / 'SOURCE.json').read_text())['files']


def check_manifest():
    actual = pins.manifest()
    assert actual == read_manifest(), 'pinned input bytes changed'
    return actual


def check_schedule():
    """T1's enumeration: the pinned scan must equal a fresh one, findings and all."""
    pinned = json.loads((HERE / 'schedule66.json').read_text())
    fresh = json.loads(json.dumps(schedule66.tiling(), default=str))
    assert pinned == fresh, 'schedule66.json differs from a fresh enumeration'
    families = pinned['families']
    assert pinned['width'] == 66 and pinned['copies'] == 3, 'the scan must be width 66'
    assert families['11']['priced_banks'] == families['11']['capacity_minimum_banks'] == 531
    for family in ('16', '20'):
        entry = families[family]
        assert entry['whole_bank_volume'], 'the family must fill whole banks by volume'
        assert entry['priced_banks'] < entry['capacity_minimum_banks'], \
            'the priced bank count must fall below the capacity bound'
        assert not entry['fits_the_priced_banks'], 'and the priced count must not fit'
    assert pinned['findings']['mixed_uniform_tilings'] == 0
    assert all(not pinned['subsets'][key]['admissible']
               for key in ('11,16', '11,20', '16,20', '11,16,20')), \
        'no mixed subset may admit a uniform tiling'
    return pinned


def check_prototype(record):
    """The padded schedule's own invariants, as rebuilt into the certificate."""
    padded = record['padded_schedule']
    assert padded['width'] == 66 and padded['copies'] == 3, 'the prototype is width 66'
    assert [step['family'] for step in padded['ladder']] == [11, 16, 20], 'rung order'
    assert [step['banks'] for step in padded['ladder']] == [531, 198, 66], \
        'the prototype must use the capacity minimum, not the volume criterion'
    assert [step['padding_per_bank'] for step in padded['ladder']] == [0, 2, 6], \
        'the padding of T1'
    for step in padded['ladder']:
        assert step['pattern_sum'] == 66, 'every bank must be exactly filled'
        assert step['blocks_per_bank'] * step['banks'] == step['items'], \
            'the schedule must be saturated'
        assert step['stock_drop'] == step['banks'], \
            'the stock must fall by exactly the bank count'
        assert step['family'] == 11 or step['padding_registers'] % step['banks'] == 0
        assert step['eligibility_after'] in ([16, 20], [20], []), 'the ladder climbs'
    assert padded['exhaustive'] and padded['residual_eligibility'] == [], \
        'the whole-bank criterion must be exhausted at the padded top'
    assert Q(record['top']['kappa']) > Q(record['comparison']['volume_criterion_top']), \
        'the padded schedule must beat the volume-criterion accounting it replaces'
    assert record['top']['banks'] == 795, '531 + 198 + 66 banks, the padded schedule'
    return padded


def check_obligations():
    obligations = json.loads((HERE / 'obligations.json').read_text())
    owed = [item['id'] for item in obligations['obligations']]
    assert owed == ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'T1'], owed
    status = {item['id']: item['status'] for item in obligations['obligations']}
    assert all(status[key] == 'OPEN' for key in owed if key != 'T1'), \
        'every obligation but T1 must still be open'
    assert status['T1'] == 'SETTLED_AT_SCHEDULE_LEVEL', \
        "T1 is settled by the schedule prototype, and must be recorded as such"
    t1 = next(item for item in obligations['obligations'] if item['id'] == 'T1')
    assert 'resolution' in t1 and 'prototype66' in t1['resolution'], \
        'T1 must name the artifact that settles it'
    inherited = [item['id'] for item in obligations['inherited']]
    assert inherited == ['R1', 'R2', 'R3', 'R4'], inherited
    assert all(item['status'] == 'OPEN' for item in obligations['inherited'])
    vendored = json.loads((HERE / 'references' / 'pr219-run1' / 'obligations.json').read_text())
    assert [item['id'] for item in vendored['obligations']] == inherited, \
        "the inherited obligation set must be #219's own"
    certificate = json.loads((HERE / 'certificate.json').read_text()) \
        if (HERE / 'certificate.json').exists() else {}
    if certificate:
        assert certificate['obligations'] == owed + inherited, 'certificate obligation list'
        assert not any('bank' in key for key in certificate['blocked_on']
                       ['complex_supplier_has_bank_keys']), \
            'the complex supplier must still have no bank keys'
    return owed + inherited


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--write', action='store_true',
                        help='authoring: regenerate certificate.json and SOURCE.json')
    args = parser.parse_args()
    assert not sys.flags.optimize, 'assertions must stay enabled'

    if not args.write:
        check_manifest()
    check_schedule()
    record = run3.build()
    check_prototype(record)
    check_obligations()
    target = HERE / 'certificate.json'
    if args.write:
        (HERE / 'SOURCE.json').write_text(
            json.dumps({'files': pins.manifest()}, indent=1, sort_keys=True) + '\n',
            newline='\n')
        target.write_text(json.dumps(record, indent=1, sort_keys=True, default=str) + '\n',
                          newline='\n')
        print('wrote certificate.json and SOURCE.json')
        return
    read = json.loads(target.read_text())
    assert read == json.loads(json.dumps(record, default=str)), 'certificate.json differs'
    print('certificate.json matches a fresh rebuild')
    print('tiling        rank 16 and rank 20 price %s and %s banks where their capacity '
          'requires %s and %s; mixed uniform tilings: %d'
          % (record['tiling']['families']['16']['priced_banks'],
             record['tiling']['families']['20']['priced_banks'],
             record['tiling']['families']['16']['capacity_minimum_banks'],
             record['tiling']['families']['20']['capacity_minimum_banks'],
             record['tiling']['findings']['mixed_uniform_tilings']))
    print('prototype     padded schedule %s banks (%s + %s + %s), padding %s per bank, '
          'stock drops %s'
          % (record['top']['banks'], *[step['banks']
                                       for step in record['padded_schedule']['ladder']],
             [step['padding_per_bank'] for step in record['padded_schedule']['ladder']],
             [step['stock_drop'] for step in record['padded_schedule']['ladder']]))
    print('rungs %s at %s banks, kappa %s'
          % (record['top']['families_absorbed'], record['top']['banks'], record['kappa']))


if __name__ == '__main__':
    main()
