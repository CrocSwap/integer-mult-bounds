# SPDX-License-Identifier: Apache-2.0
"""Replay the code-disjoint T37 endpoint check and its negative controls.

Usage: python3 -B research/t37-endpoints-independent/verify.py --work NEW_EMPTY_DIR
Expected last line: PASS_T37_ENDPOINTS_INDEPENDENT_REPLAY
"""
import argparse
import json
import subprocess
import sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

import endpoints as E

HERE = Path(__file__).resolve().parent


def rejects(name, fn, reason):
    try:
        fn()
    except ValueError as exc:
        if reason not in str(exc):
            raise SystemExit(f'FAIL control {name} rejected for another reason: {exc}')
        return name
    raise SystemExit(f'FAIL control {name} was accepted')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--work', required=True)
    work = Path(ap.parse_args().work).resolve()
    E.require(not work.exists(), 'work directory must not exist')
    work.mkdir(parents=True)
    proc = subprocess.run([sys.executable, '-B', str(HERE / 'endpoints.py'), str(work / 'RESULT.json')],
                          cwd=HERE, capture_output=True, text=True)
    sys.stdout.write(proc.stdout)
    E.require(proc.returncode == 0, 'endpoints.py failed:\n' + proc.stderr)
    E.require(json.loads((work / 'RESULT.json').read_text()) == json.loads((HERE / 'RESULT.json').read_text()),
              'RESULT.json differs from the committed result')
    assembly = E.pinned('assembly')
    bit = E.pinned('bit_record')
    H, W, m = E.template_profile()
    b, c = Q(assembly['complex_lower']), Q(assembly['bit_lower'])
    Hb = Counter({int(k): v for k, v in bit['nine']['profile'].items()})
    Wb = bit['nine']['bit']['live']
    passed = [
        rejects('C1_next_grid_point_claimed', lambda: E.certify_endpoint(dict(H), m, W, b + Q(1, 10 ** 24), False),
                'not below one'),
        rejects('C2_one_extra_rank_one_child', lambda: E.certify_endpoint(dict(H + Counter({1: 1})), m, W, b, False),
                'not below one'),
    ]
    passed.append(rejects('C3_dimension_72', lambda: E.certify_endpoint(dict(H), 72, W, b, False), 'not below one'))
    passed.append(rejects('C4_bit_without_surcharge', lambda: E.certify_endpoint(dict(Hb), 64, Wb, c, False),
                          'not above one at the next grid point'))

    def c5():
        k, margin = E.kappa_from(b, c)
        E.require(k + Q(1, 10 ** 18) < margin, 'next kappa grid point is not admissible')
    passed.append(rejects('C5_next_kappa_grid_point', c5, 'next kappa grid point is not admissible'))
    saved = E.TAYLOR
    E.TAYLOR = 2
    try:
        passed.append(rejects('C6_truncated_exponential', lambda: E.certify_endpoint(dict(H), m, W, b, False),
                              'not below one'))
    finally:
        E.TAYLOR = saved
    good = dict(E.PINS['assembly'])
    E.PINS['assembly']['sha256'] = '0' * 64
    try:
        passed.append(rejects('C7_assembly_pin', lambda: E.pinned('assembly'), 'digest'))
    finally:
        E.PINS['assembly'] = good
    print('controls rejected as expected:', ', '.join(passed))
    print('PASS_T37_ENDPOINTS_INDEPENDENT_REPLAY')


if __name__ == '__main__':
    main()
