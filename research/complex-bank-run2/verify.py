#!/usr/bin/env python3
"""Offline verification of the rung-2 ledger, its prices and its assembly.

Read-only unless `--write`: pins every vendored byte, rebuilds the rung-2 ledger, both
paid moments, the 47-constraint assembly and the independent PR208 replica from those
inputs, and compares the result with `certificate.json`.

    python3 -B verify.py           # check
    python3 -B verify.py --write   # authoring: regenerate certificate.json and SOURCE.json

The complex-side bank construction obligations (C1-C5 in `obligations.json`, plus the
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
import run2  # noqa: E402


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
    assert owed == ['C1', 'C2', 'C3', 'C4', 'C5'], owed
    assert all(item['status'] == 'OPEN' for item in obligations['obligations'])
    inherited = [item['id'] for item in obligations['inherited']]
    assert inherited == ['R1', 'R2', 'R3', 'R4'], inherited
    assert all(item['status'] == 'OPEN' for item in obligations['inherited'])
    vendored = json.loads((HERE / 'references' / 'pr219-run1' / 'obligations.json').read_text())
    assert [item['id'] for item in vendored['obligations']] == inherited, \
        'the inherited obligation set must be #219\'s own'
    return owed + inherited


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--write', action='store_true',
                        help='authoring: regenerate certificate.json and SOURCE.json')
    args = parser.parse_args()
    assert not sys.flags.optimize, 'assertions must stay enabled'

    before = None if args.write else check_manifest()
    record = run2.build()
    owned = check_obligations()
    target = HERE / 'certificate.json'
    if args.write:
        (HERE / 'SOURCE.json').write_text(
            json.dumps({'files': pins.manifest()}, indent=1, sort_keys=True) + '\n', newline='\n')
        target.write_text(json.dumps(record, indent=1, sort_keys=True, default=str) + '\n',
                          newline='\n')
        read = record
    else:
        read = json.loads(target.read_text())
        assert read == json.loads(json.dumps(record, default=str)), 'certificate.json differs'
        assert check_manifest() == before, 'inputs changed during verification'

    print('PASS rung-2 ledger, whole-bank volume and retained row identity, both paid moments '
          'on the 10^-18 grid, the 47-constraint assembly with its adjacent point rejected, '
          'the PR208 replica, and #207/#219 reproduced exactly; obligations %s OPEN'
          % ', '.join(owned))
    print('rung 2 conditional kappa = ' + str(read['kappa']) + ' (binding ' + read['binding'] + ')')


if __name__ == '__main__':
    main()
