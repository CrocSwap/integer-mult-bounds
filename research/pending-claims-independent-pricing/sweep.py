# SPDX-License-Identifier: Apache-2.0
"""Code-disjoint pricing of every pending conditional-kappa claim at or above the selected record.

Usage: sweep.py OUT.json

Reads SNAPSHOT.json (each claim's committed profile, live stock, calls, complex endpoint and kappa,
copied from the PR's pinned head with the git blob id of every source file). For every claim:
  1. rank mass and deficit, and the coverage form D = W - 64 N of the nine-stage hosted template;
  2. the halving guard 73^2 > 2 r_max^2;
  3. the recorded complex endpoint: moment < 1 there and > 1 at the next 10^-24 grid point;
  4. kappa from the selected outer reduction with the unchanged PR589 bit endpoint, compared with
     the record and the title.
Nothing is fetched or executed from the PRs; rebind.py re-checks the snapshot against the heads.
"""
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

from arith import certify, kappa_from, require

HERE = Path(__file__).resolve().parent
M = 73
BIT = Q('1733427039589844234749/1000000000000000000000000')      # PR589, unchanged in every claim
ASSUMED = {1019: (33152, 333, 'same construction as the selected T37 record; the PR does not record W or N'),
           1030: (7168, 72, 'not recorded in the PR; the unique W with mass = 72W + 64N for N = 72')}


def price(c):
    H = {int(r): n for r, n in c['profile'].items()}
    W, N, note = c['live'], c['calls'], None
    if W is None:
        W, N, note = ASSUMED[c['pr']]
    mass = sum(r * n for r, n in H.items())
    D = M * W - mass
    b = Q(c['complex_lower'])
    grid = Q(1, 10 ** 24) if c['pr'] == 1019 else Q(1, 10 ** 18)
    row = dict(pr=c['pr'], head=c['head'], live=W, calls=N, assumed_live=note, rank_mass=mass, deficit=D,
               deficit_equals_W_minus_64N=(D == W - 64 * N), max_child=max(H), halving=M * M > 2 * max(H) ** 2,
               complex_lower=str(b), claimed_kappa_decimal=c['claimed_kappa_decimal'], record_kappa=c['record_kappa'])
    try:
        row['moment_minus_one'] = certify(H, M, W, b)
        row['endpoint_certified'] = True
    except ValueError as e:
        row['endpoint_certified'] = False
        row['endpoint_failure'] = str(e)
    k, margin, binding = kappa_from(b, BIT, grid)
    digits = len(str(grid.denominator)) - 1
    exact = '0.' + str(k.numerator * (grid.denominator // k.denominator)).zfill(digits)
    bit_ok = c.get('bit_lower') in (None, str(BIT)) or Q(c['bit_lower']) == BIT
    row.update(kappa=str(k), kappa_exact_decimal=exact, binding=binding, kappa_grid=str(grid), record_bit_is_pr589=bit_ok,
               kappa_equals_record=(k == Q(c['record_kappa'])),
               kappa_equals_title=(exact.rstrip('0') == c['claimed_kappa_decimal'].rstrip('0')))
    return row


def main():
    snap = json.loads((HERE / 'SNAPSHOT.json').read_text())
    rows = [price(c) for c in sorted(snap, key=lambda c: c['pr'])]
    out = dict(status='PASS_PENDING_CLAIMS_PRICED', base_commit='2921874911956718fcaaaf9396fe8267b3cfa9f0',
               method='code-disjoint: atanh prime chain, Taylor exp with Lagrange remainder, 2^-320 outward rounding',
               claims=rows,
               summary=dict(claims=len(rows), endpoints_certified=sum(r['endpoint_certified'] for r in rows),
                            kappa_matches_record=sum(r['kappa_equals_record'] for r in rows),
                            deficit_identity_holds=sum(r['deficit_equals_W_minus_64N'] for r in rows)))
    with open(sys.argv[1], 'w') as f:
        f.write(json.dumps(out, indent=1, sort_keys=True) + '\n')
    print(out['status'], json.dumps(out['summary']))
    for r in rows:
        print(f"#{r['pr']:5d} W {r['live']:6d} N {r['calls']:3d} D {r['deficit']:6d} D=W-64N {str(r['deficit_equals_W_minus_64N']):5s}"
              f" endpoint {'ok' if r['endpoint_certified'] else 'FAIL'}  kappa {float(Q(r['kappa'])):.18f}"
              f" record {'=' if r['kappa_equals_record'] else '!='}  title {'=' if r['kappa_equals_title'] else '!='}"
              f"{'  (assumed W)' if r['assumed_live'] else ''}")


if __name__ == '__main__':
    main()
