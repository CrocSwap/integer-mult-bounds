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
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

import pins  # noqa: E402
import run3  # noqa: E402


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def read_manifest():
    return json.loads((HERE / 'SOURCE.json').read_text())['files']


def check_manifest():
    actual = pins.manifest()
    assert actual == read_manifest(), 'pinned input bytes changed'
    return actual


def check_obligations():
    obligations = json.loads((HERE / 'obligations.json').read_text())
    owed = [item['id'] for item in obligations['obligations']]
    assert owed == ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'T1'], owed
    assert all(item['status'] == 'OPEN' for item in obligations['obligations'])
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
    record = run3.build()
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
    print('rungs %s at %s banks, kappa %s'
          % (record['top']['families_absorbed'], record['top']['banks'], record['kappa']))


if __name__ == '__main__':
    main()
