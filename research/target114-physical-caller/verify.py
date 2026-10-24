#!/usr/bin/env python3
"""Bounded, source-byte authenticated caller admission and physical calibration."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from source_binding import build, need, authenticate
from copy import deepcopy


def source_controls():
    rows = json.loads((Path(__file__).resolve().parent / 'SOURCES.json').read_text())['files']
    first = next(i for i, row in enumerate(rows) if row['usage'] == 'input')
    changed = deepcopy(rows); changed[first]['sha256'] = '0' * 64
    omitted = rows[:first] + rows[first + 1:]
    rejected = []
    for label, altered in [('omitted_input', omitted), ('changed_input_sha', changed),
                            ('duplicate_input', rows + [rows[first]])]:
        try:
            authenticate(altered)
        except ValueError:
            rejected.append(label)
        else:
            raise ValueError('invalid source manifest admitted ' + label)
    return rejected


def run(unbound=False):
    caller, catalogue, legacy, historical, source = build()
    if unbound:
        legacy.CALLER = historical
        from call_checks import run as call
        try:
            call(catalogue)
        except ValueError as error:
            need(str(error) == 'physical Tape allocation inside a completed macro',
                 'exact unbound allocation selector failure')
            return dict(status='REJECT_UNBOUND_COMPACT_MODULES', reason=str(error))
        raise ValueError('unbound compact allocation sites unexpectedly admitted')
    import admission
    from call_checks import run as call
    report = dict(status='PASS_TARGET114_PHYSICAL_REFINEMENT_BOUNDARY', source=source,
                  source_rejections=source_controls(),
                  admission=admission.run(caller, catalogue), physical_call=call(catalogue))
    with TemporaryDirectory(prefix='target114-cold-child-') as temporary:
        process = subprocess.run([sys.executable, '-X', 'pycache_prefix=' + temporary,
                                  '-Werror', '-B', str(Path(__file__).resolve()), '--unbound'],
                                 text=True, capture_output=True, timeout=120)
    need(process.returncode == 0, 'unbound source control: ' + process.stderr)
    report['allocation_selector_control'] = json.loads(process.stdout)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--unbound', action='store_true')
    args = parser.parse_args()
    report = run(args.unbound)
    if not args.unbound:
        expected = json.loads((Path(__file__).resolve().parent / 'RESULT.json').read_text())
        # Compare scalar types as well as values; assertions are never the gate.
        canonical = lambda value: json.dumps(value, sort_keys=True, separators=(',', ':'))
        need(canonical(report) == canonical(expected), 'retained exact caller receipt')
    print(json.dumps(report, sort_keys=True, indent=2))
