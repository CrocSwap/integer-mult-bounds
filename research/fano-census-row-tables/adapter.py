#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Run the complete pinned PR3168 verifier with an opt-in census engine."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'research/centre-seven-owner-fano-independent/verify.py'
EXPECTED = SOURCE.with_name('RESULT.json')


def load_kernel():
    spec = importlib.util.spec_from_file_location('fano_row_tables', HERE / 'kernel.py')
    kernel = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kernel)
    return kernel


def check_pins():
    for row in json.loads((HERE / 'SOURCES.json').read_bytes())['files']:
        if row['usage'] == 'input':
            if hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() != row['sha256']:
                raise ValueError('source pin: ' + row['path'])


def reference():
    check_pins()
    module = types.ModuleType('pinned_fano_reference')
    module.__file__ = str(SOURCE)
    exec(compile(SOURCE.read_bytes(), str(SOURCE), 'exec'), module.__dict__)
    return module


def run(engine):
    module = reference()
    if engine == 'tables':
        module.relation_census = load_kernel().relation_census
    elif engine != 'reference':
        raise ValueError('unknown engine')
    result = module.canonical(module.build())
    if result != EXPECTED.read_bytes():
        raise ValueError('complete PR3168 receipt differs')
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--engine', choices=('reference', 'tables'), default='tables')
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    if args.output and args.output.exists():
        raise SystemExit('output exists')
    result = run(args.engine)
    if args.output:
        with args.output.open('xb') as stream:
            stream.write(result)
    print('PASS_FANO_ROW_TABLES_COMPLETE_RECEIPT', args.engine)


if __name__ == '__main__':
    main()
