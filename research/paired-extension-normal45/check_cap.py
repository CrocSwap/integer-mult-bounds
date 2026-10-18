#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fractions-only certificate of the fixed-capacity packing cap of the new words, and the literal gap to it.

certificates/RELAX-CAP.json stores the 9-pattern optimal basis of the fractional relaxation of this package's
inventory {4:26,5:2,7:62,8:100,9:218} with local profile {1:2434,2:632,3:286,4:104,5:26,8:8} (bins 672/448/448/448
per replica of capacity 8/16/32/48, all 1,163 count-vector patterns, one idle child per bin, the complete per-call
local profile paid). tools/relax_exact.py checks, with exact rationals only, the basis' primal feasibility (the cap
is at least its root) and the sign of every pattern's reduced cost at the upper end of the root bracket (weak
duality: the cap is at most that end). Unlike PR2930's cap of PR2917's words, this optimum is FRACTIONAL per
replica ([9^5] x 396/5 and [] x 1844/5 at cap 48; 74 x 396/5 is not an integer), so no allocation can realize this
basic solution literally. This script checks that the literal profile allocation/PROFILE.json is a complete
profile of these words (666 calls x local + idle children, rank mass 74 x 65,088), that its exact root bracket lies
below the cap (as weak duality requires), and records the exact gap. No optimality of the literal fill among
integral allocations is claimed. Marius-Paul Dumitrean, with substantial AI assistance (Claude Code). The
relaxation model and root arithmetic are ours (research/t37-word-level-census-r12 lineage, as shipped by PR2930).
"""
import gzip, json, sys
from fractions import Fraction as Q
from pathlib import Path
P = Path(__file__).resolve().parent
sys.path.insert(0, str(P / 'tools'))
import relax_exact as RE
import root as R

# PR2930's certificate for PR2917's inventory {8:96,9:222}: the SAME nine optimal patterns, with that inventory's basic
# counts. The changed inventory keeps the pattern set and moves the counts ([9^5] 81 -> 396/5, [] 367 -> 1844/5, ...),
# so the old stored counts must be rejected (control).
STALE_BASIS = [(8, [8], '672'), (16, [7, 9], '352'), (32, [7, 7, 9, 9], '103'), (16, [8, 8], '96'), (48, [9] * 5, '81'),
               (32, [5, 9, 9, 9], '18'), (32, [9, 9, 9], '93'), (32, [4, 9, 9, 9], '234'), (48, [], '367')]

def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw)

def main():
    if not __debug__:
        raise SystemExit('refusing python -O')
    cert = read(P / 'certificates/RELAX-CAP.json')
    words = [read(P / f'data/WORD-{t}.json.gz') for t in ('base', 'extra')]
    for w in words:
        assert dict(w['report']['local_profile']) == cert['local_per_call'], 'certificate local profile = actual words'
        assert dict(w['report']['width_inventory']) == cert['inventory_per_call'], 'certificate inventory = actual words'
    r = RE.verify_basis(cert['local_per_call'], cert['inventory_per_call'], cert['basis_patterns'])
    assert r['status'] == 'PASS_EXACT_RELAXATION_CAP' and r['patterns'] == 1163
    cap_lo, cap_hi = Q(r['cap_lower']), Q(r['cap_upper'])
    assert (cap_lo, cap_hi) == (Q(cert['cap_lower']), Q(cert['cap_upper']))
    T, calls = 74, 666
    fractional = {k: str(T * Q(v)) for k, v in r['idle_per_replica'].items() if (T * Q(v)).denominator != 1}
    assert fractional, 'the optimal basic solution is fractional at T74'
    profile = {int(k): v for k, v in read(P / 'allocation/PROFILE.json').items()}
    assert sum(r_ * n for r_, n in profile.items()) == T * R.MASS_PER_REPLICA, 'complete rank mass 74 x 65088'
    idle = dict(profile)
    for k, v in cert['local_per_call'].items():
        idle[int(k)] = idle.get(int(k), 0) - calls * v
    assert all(v >= 0 for v in idle.values()), 'literal profile pays the complete local profile of every call'
    idle = {k: v for k, v in sorted(idle.items()) if v}
    lo, hi = R.kappa_from_profile(profile, T)
    assert lo < hi <= cap_hi and hi <= cap_lo + Q(1, 10 ** 25), 'literal root at most the cap (weak duality)'
    gap = (cap_lo - hi, cap_hi - lo)
    assert 0 < gap[0] <= gap[1] < Q(1, 10 ** 9), 'recorded gap below 1e-9'
    controls = {}
    try:
        bad = [dict(e) for e in cert['basis_patterns']]; bad[0] = dict(bad[0]); bad[0]['widths'] = list(bad[0]['widths']) + [4]
        RE.verify_basis(cert['local_per_call'], cert['inventory_per_call'], bad)
    except Exception as error:
        controls['perturbed_basis_pattern'] = str(error)[:160]
    else:
        raise AssertionError('perturbed basis accepted')
    try:
        RE.verify_basis(cert['local_per_call'], cert['inventory_per_call'], [{'capacity': c, 'widths': w, 'count_per_replica': n} for c, w, n in STALE_BASIS])
    except Exception as error:
        controls['stale_pr2930_counts_for_changed_inventory'] = str(error)[:160]
    else:
        raise AssertionError('the old-inventory basic counts must not certify the changed inventory')
    assert sorted((c, tuple(w)) for c, w, n in STALE_BASIS) == sorted((e['capacity'], tuple(e['widths'])) for e in cert['basis_patterns']), 'same optimal pattern set as PR2930'
    over = dict(profile); over[48] -= 1; over[24] = over.get(24, 0) + 2      # a finer idle split of the same rank mass
    if not R.kappa_from_profile(over, T)[1] < lo:
        raise AssertionError('a finer idle split must lower the literal root (concavity)')
    controls['finer_idle_split_lowers_root'] = 'PASS'
    out = dict(status='PASS_LITERAL_ALLOCATION_BELOW_FIXED_INVENTORY_CAP_WITH_RECORDED_GAP', cap_lower=str(cap_lo), cap_upper=str(cap_hi),
               literal_lower=str(lo), literal_upper=str(hi), gap_lower=str(gap[0]), gap_upper=str(gap[1]), gap_float=float(gap[0]),
               tight_patterns=r['tight_patterns'], strict_patterns=r['strict_patterns'], idle_per_replica=r['idle_per_replica'],
               fractional_at_T74=fractional, literal_idle=idle, profile={str(k): v for k, v in sorted(profile.items())}, controls=controls)
    print(json.dumps(out, sort_keys=True))

if __name__ == '__main__':
    main()
