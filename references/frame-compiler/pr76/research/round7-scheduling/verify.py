#!/usr/bin/env python3
"""Reproduce the frozen envelope/exchange witness and its exact certificate."""
import argparse
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import json
from pathlib import Path
import subprocess
import sys
import tempfile

if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
SELECTED = HERE / 'selected-both'


def read(path):
    return json.loads(path.read_text())


def run(script, *args):
    subprocess.run([sys.executable, str(HERE / script), *map(str, args)], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--regenerate', action='store_true',
                        help='Also deterministically compile both physical words')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='envelope-exchange-') as directory:
        work = Path(directory)
        receipt = work / 'validation.json'
        run('validate_selected.py', '--bundle', SELECTED, '--output', receipt)
        assert read(receipt) == read(HERE / 'validation-receipt.json'), 'Replay receipt changed'

        from validate_selected import BASE, refine
        from width_bridge import bridge_for_width
        certificate = read(SELECTED / 'arithmetic.json')
        inherited = read(BASE / 'references/frame-compiler/pr48/research/copied-fixed/certificate.json')['finite_bridge']
        bridge = bridge_for_width(inherited, certificate['profile']['W'])
        refine.balanced.validate_bridge(bridge)
        for section, field in (('bit', 'wire_bits'), ('rows', 'coefficient'), ('rows', 'degree_gap')):
            stale = deepcopy(bridge)
            stale[section][field] = inherited[section][field]
            assert Q(stale[section][field]) != Q(bridge[section][field])
            try:
                refine.balanced.validate_bridge(stale)
            except refine.balanced.InvalidAssembly:
                pass
            else:
                raise AssertionError('Stale bridge field accepted: ' + field)

        if args.regenerate:
            axes = {h: work / str(h) for h in (23, 25)}
            for h, axis in axes.items():
                run('run.py', '--h', h, '--work-dir', axis)
                assert read(axis / f'result-{h}.json') == read(SELECTED / f'result-{h}.json')
                actual = gzip.decompress((axis / f'word-{h}.json.gz').read_bytes())
                expected = gzip.decompress((SELECTED / f'word-{h}.json.gz').read_bytes())
                assert actual == expected, f'Physical word changed at h={h}'
                extra = ('--other-profile', axes[23] / 'profile-23.json') if h == 25 else ()
                run('screen_width.py', '--h', h, '--work-dir', axis, *extra)
                assert read(axis / f'profile-{h}.json') == read(SELECTED / f'profile-{h}.json')
                assert read(axis / f'transitions-{h}.bin.json') == read(SELECTED / f'transitions-{h}.bin.json')
            assert read(axes[25] / 'arithmetic.json') == certificate, 'Exact arithmetic certificate changed'
    print('PASS frozen witness, independent replay, exact arithmetic and width failure controls')
    if args.regenerate:
        print('PASS deterministic compilation of both words and complete certificate regeneration')


if __name__ == '__main__':
    main()
