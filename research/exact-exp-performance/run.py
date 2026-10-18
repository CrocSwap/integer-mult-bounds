#!/usr/bin/env python3
"""Replay the pinned complete owner check, optionally replacing only E.exp."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import runpy
import sys

from fast_exp import exp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = ROOT / 'research/complex-k492-owner-repair'
REFERENCE = PACKAGE / 'extras/exact_intervals.py'
FIXTURE = ROOT / 'research/community-k492-audit/pr622/replay'


def check_sources():
    manifest = json.loads((HERE / 'SOURCE.json').read_text())
    for name, expected in manifest['files'].items():
        actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError('Pinned input changed: ' + name)


def replay(engine, out):
    check_sources()
    out = out.resolve()
    if out.exists() or out.is_relative_to(ROOT):
        raise ValueError('Use a fresh output path outside the repository')
    original_spec = importlib.util.spec_from_file_location
    original_argv = sys.argv
    replacements = []

    def spec_with_exp(name, location, *args, **kwargs):
        spec = original_spec(name, location, *args, **kwargs)
        if Path(location).resolve() == REFERENCE:
            original_exec = spec.loader.exec_module

            def exec_with_exp(module):
                original_exec(module)
                module.exp = exp
                replacements.append(str(location))

            spec.loader.exec_module = exec_with_exp
        return spec

    try:
        if engine == 'integer':
            importlib.util.spec_from_file_location = spec_with_exp
        sys.argv = [str(PACKAGE / 'extras/check_owner_map.py'),
                    '--work', str(FIXTURE), '--out', str(out)]
        runpy.run_path(sys.argv[0], run_name='__main__')
    finally:
        importlib.util.spec_from_file_location = original_spec
        sys.argv = original_argv
    if len(replacements) != (1 if engine == 'integer' else 0):
        raise ValueError('Exponential replacement was not applied exactly once')
    expected = json.loads((HERE / 'SOURCE.json').read_text())['owner_receipt_sha256']
    if hashlib.sha256(out.read_bytes()).hexdigest() != expected:
        raise ValueError('Owner receipt differs from pinned reference')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', choices=('reference', 'integer'), required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    replay(args.engine, args.out)


if __name__ == '__main__':
    main()
