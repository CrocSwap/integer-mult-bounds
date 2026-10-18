# SPDX-License-Identifier: Apache-2.0
"""Offline replay of the pending-claims pricing table with negative controls.

Usage: python3 -B research/pending-claims-independent-pricing/verify.py --work NEW_EMPTY_DIR
Expected last line: PASS_PENDING_CLAIMS_PRICING_REPLAY
"""
import argparse
import json
import subprocess
import sys
from fractions import Fraction as Q
from pathlib import Path

import arith
import sweep

HERE = Path(__file__).resolve().parent


def rejects(name, fn, reason):
    try:
        fn()
    except ValueError as e:
        if reason not in str(e):
            raise SystemExit(f'FAIL {name}: rejected for another reason: {e}')
        return name
    raise SystemExit(f'FAIL {name} accepted')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--work', required=True)
    work = Path(ap.parse_args().work).resolve()
    arith.require(not work.exists(), 'work directory must not exist')
    work.mkdir(parents=True)
    p = subprocess.run([sys.executable, '-B', str(HERE / 'sweep.py'), str(work / 'RESULT.json')], cwd=HERE,
                       capture_output=True, text=True)
    sys.stdout.write(p.stdout)
    arith.require(p.returncode == 0, 'sweep failed:\n' + p.stderr)
    got = json.loads((work / 'RESULT.json').read_text())
    arith.require(got == json.loads((HERE / 'RESULT.json').read_text()), 'RESULT.json differs from the committed table')
    s = got['summary']
    arith.require(s['claims'] == s['endpoints_certified'] == s['kappa_matches_record'] == 16, 'summary')
    snap = {c['pr']: c for c in json.loads((HERE / 'SNAPSHOT.json').read_text())}
    top = snap[1061]
    H = {int(r): n for r, n in top['profile'].items()}
    b = Q(top['complex_lower'])
    passed = [
        rejects('C1_extra_rank_one_child', lambda: arith.certify({**H, 1: H[1] + 1}, 73, top['live'], b), 'not below one'),
        rejects('C2_one_replica_less_stock', lambda: arith.certify(H, 73, top['live'] - 896, b), 'not below one'),
        rejects('C3_endpoint_plus_grid', lambda: arith.certify(H, 73, top['live'], b + Q(1, 10 ** 24)), 'not below one'),
    ]

    def c4():
        k, margin, _ = arith.kappa_from(b, sweep.BIT)
        arith.require(k + Q(1, 10 ** 18) < margin, 'next kappa grid point not admissible')
    passed.append(rejects('C4_claimed_kappa_plus_grid', c4, 'next kappa grid point not admissible'))

    def c5():
        k, _, binding = arith.kappa_from(b, b - Q(1, 10 ** 6))
        arith.require(binding == 'complex' and str(k) == top['record_kappa'], 'kappa or binding changes with a weaker bit side')
    passed.append(rejects('C5_weaker_bit_side', c5, 'kappa or binding changes'))
    saved = arith.TAYLOR
    arith.TAYLOR = 2
    try:
        passed.append(rejects('C6_truncated_exponential', lambda: arith.certify(H, 73, top['live'], b), 'not below one'))
    finally:
        arith.TAYLOR = saved
    print('controls rejected as expected:', ', '.join(passed))
    print('PASS_PENDING_CLAIMS_PRICING_REPLAY')


if __name__ == '__main__':
    main()
