#!/usr/bin/env python3
"""Replay the exact frozen PR727 adapter and its original PR626 reference.

Brian / JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
The original checker and construction retain their predecessor attribution.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'research/complex-k492-owner-repair/extras/check_owner_map.py'
WORK = ROOT / 'research/community-k492-audit/pr622/replay'
PINS = json.loads((HERE / 'SOURCES.json').read_text())



def check_pins():
    for name, expected in PINS['pr727']['files'].items():
        if hashlib.sha256((HERE / 'vendor/pr727' / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Pinned PR727 source changed: ' + name)
    for relative, pin in PINS['files'].items():
        if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != pin['sha256']:
            raise ValueError('Pinned input changed: ' + relative)


check_pins()
spec = importlib.util.spec_from_file_location('pinned_pr727', HERE / 'vendor/pr727/adapter.py')
PR727 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(PR727)


def checker_source(engine):
    raw = SOURCE.read_bytes()
    pin = PINS['files'][SOURCE.relative_to(ROOT).as_posix()]['sha256']
    if hashlib.sha256(raw).hexdigest() != pin:
        raise ValueError('Pinned checker changed')
    text = raw.decode()
    if engine == 'bitset':
        text = PR727.transformed(text)
    elif engine != 'reference':
        raise ValueError('Unknown engine: ' + engine)
    return text


def execute(engine, output):
    """Run the complete checker, including native pins and exact moments."""
    if output.exists():
        raise ValueError('Use a fresh output path: ' + str(output))
    previous_argv = sys.argv
    try:
        sys.argv = [str(SOURCE), '--work', str(WORK), '--out', str(output)]
        namespace = {'__file__': str(SOURCE), '__name__': '__main__',
                     'interval_mask': PR727.interval_mask, 'is_prefix': PR727.is_prefix}
        exec(compile(checker_source(engine), str(SOURCE), 'exec'), namespace)
        return namespace
    finally:
        sys.argv = previous_argv


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', choices=('reference', 'bitset'), default='bitset')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    check_pins()
    execute(args.engine, args.out)


if __name__ == '__main__':
    main()
