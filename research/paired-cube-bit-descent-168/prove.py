#!/usr/bin/env python3
"""Bit operation-frame descent on PR168's p = 12 bit word: complete word check and exact assembly.

Prepared by Joel Pulikkan (GamingPuzzled) with Anthropic Claude assistance. Apache-2.0.

  1. word.py (PR165's checker, unchanged logic) applies replacement-frames.json to PR168's committed bit word and
     checks every replaced frame: value span inside, exact nondegeneracy, nested physical role chains, preserved
     rank mass, then the complete F2 identity and the defining integer decoder over all source, target and dirty
     columns.  Adverse controls (omitted compensation, missing partner delivery, zero frame) must be rejected.
  2. prime_witnesses.py factors every new integer Gram determinant (residual below 2^80 after 2, 3, 5).
  3. PR168's own scripts/paired_cube_network.py functions, unchanged, certify the bit supplier on the recounted
     child histogram, the complex supplier and finite bridge, and the 47-constraint balanced assembly.  Only the
     bit row and the grid points found here are substituted; the next coarse and kappa grid points are rejected.

Usage: python3 -B research/paired-cube-bit-descent-168/prove.py [--write]
"""
from fractions import Fraction as Q
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / 'scripts'))
sys.dont_write_bytecode = True
from word import Candidate, need
from prime_witnesses import certificate as prime_certificate
import paired_cube_network as N
from structured_bulk_assembly import js

GRID = 10**10
# Stopped-atom exponent. #169 retained theta = 1/1000. The ordinary wrapper
# only needs theta > a_b = (1-theta)*a_star + theta*a_old. For the certified
# coarse saving 6115023/10^10 the tie point is 6115023/10005730424, so
# theta = 6111521/10^10 is admissible and raises the balanced-prefix kappa.
ATOM = Q(6111521, GRID)


def profile(row):
    """Shared-core profile of the recounted bit row, in paired_cube_network's ledger format."""
    H = {int(r): n for r, n in row['child_histogram'].items()}
    need(sum(r * n for r, n in H.items()) == row['rank_per_vertex'], 'rank mass')
    need(row['W_per_vertex'] * row['m'] - row['rank_per_vertex'] == row['deficit_per_vertex'] == 2 * row['v'] - 3 * row['loss'],
         'telescoping deficit')
    need(all(0 < r < row['m'] and n > 0 for r, n in H.items()), 'proper children')
    return dict(m=row['m'], local_dimension=row['h'], W_per_vertex=row['W_per_vertex'],
                rank_per_vertex=row['rank_per_vertex'], deficit_per_vertex=row['deficit_per_vertex'],
                child_multiplicities=dict(sorted(H.items())), maxchild=max(H), edge_count=sum(H.values()))


def set_bit(coarse):
    N.COARSE = coarse
    N.AB = (1 - N.ATOM) * coarse + N.ATOM * N.OLD
    N.ASSEMBLY_BIT = min(N.AB, (1 - N.PHASE_STOP) * N.AC - Q(1, GRID))


def bit_ok(row, k):
    set_bit(Q(k, GRID))
    try:
        return N.bit_certificate(row)
    except (AssertionError, ValueError):
        return None


def largest(ok, lo, hi):
    """Largest k in [lo, hi) with ok(k), given ok(lo) and not ok(hi)."""
    need(ok(lo) and not ok(hi), 'search bracket')
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if ok(mid) else (lo, mid)
    return lo


def main():
    need(not sys.flags.optimize, 'run without -O')
    N.ATOM = ATOM
    word = Candidate([]); word.exact_frames(); row = word.row()
    formal = [word.formal(r) for r in (2, 0)]
    controls = []
    for tamper in ('omit_compensation', 'missing_partner'):
        try: word.formal(2, tamper)
        except ValueError: controls.append(tamper)
        else: raise ValueError('adverse word control accepted: ' + tamper)
    bad = Candidate([]); bad.opframe[bad.changed_frames[0]] = bad.register([])
    try: bad.exact_frames()
    except ValueError: controls.append('zero_operation_frame')
    else: raise ValueError('zero frame accepted')
    primes = prime_certificate()
    need(primes['total_operation_frames'] == row['changed_operation_frames'], 'prime witnesses cover every frame')
    print('PASS bit word: %d replaced frames (%d outside the original), R %d, W %d; F2 and Z identities; controls %s'
          % (row['changed_operation_frames'], row['frames_not_contained_in_original'], row['R'], row['W_per_vertex'], controls), flush=True)

    p = profile(row); N.bitcube_profile = lambda _row: p
    coarse = largest(lambda k: bit_ok(row, k) is not None, 6105820, 6200000)
    bit = bit_ok(row, coarse)
    print('PASS bit supplier: coarse %d/10^10 (PR168 6105820), next grid point rejected' % coarse, flush=True)

    crow = json.loads((ROOT / 'certificates/paired-cube-complex-input.json').read_text())
    phase = N.complex_certificate(crow, N.checked_record())
    bridge = N.finite_bridge(phase, bit, crow)
    def kappa_ok(k):
        try: N.assembly(N.ASSEMBLY_BIT, N.AC, bridge, Q(k, GRID), beta=N.PHASE_STOP); return True
        except AssertionError: return False
    kappa = largest(kappa_ok, 6096379, 6200000)
    result = N.assembly(N.ASSEMBLY_BIT, N.AC, bridge, Q(kappa, GRID), beta=N.PHASE_STOP)
    try: N.prefix_assembly(N.ASSEMBLY_BIT, N.AC, bridge, Q(kappa, GRID), beta=N.PHASE_STOP)
    except AssertionError: controls.append('original_prefix_rejected')
    else: raise ValueError('original-prefix control accepted')
    need(len(result['strict_constraints']) == 47 and len(result['margins']) == 7, 'complete assembly')
    print('PASS assembly: kappa %d/10^10 = %.7e (PR168 6096379/10^10, %+.4f%%); 47 strict constraints, 7 margins; next grid point rejected'
          % (kappa, kappa / GRID, 100 * (kappa / 6096379 - 1)), flush=True)

    cert = js(dict(status='Conditional paired-cube witness with bit operation-frame descent', kappa=Q(kappa, GRID),
        bit_coarse_saving=Q(coarse, GRID), bit_effective_saving=N.AB, assembly_bit=N.ASSEMBLY_BIT,
        complex_saving=N.AC, bit_profile=row, formal=formal, controls=controls, prime_witnesses=primes,
        bit_moment=bit['coarse'], assembly=result,
        scope='PR168 conditional scope and interfaces retained; only the bit operation frames change.'))
    text = json.dumps(cert, indent=2, sort_keys=True) + '\n'
    target = HERE / 'certificate.json'
    if '--write' in sys.argv:
        target.write_text(text); (HERE / 'prime-witnesses.json').write_text(json.dumps(primes, indent=2, sort_keys=True) + '\n')
    else:
        need(target.read_text() == text, 'saved certificate differs')
        need(json.loads((HERE / 'prime-witnesses.json').read_text()) == primes, 'saved prime witnesses differ')
    print('PASS certificate%s' % (' written' if '--write' in sys.argv else ' reproduced'))


if __name__ == '__main__':
    main()
