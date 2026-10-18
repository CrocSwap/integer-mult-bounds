#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fractions-only certificates of the fixed-capacity packing caps of the parent and of every stage word, the literal gap of
the shipped allocation to the final cap, and exact comparisons with the current claims.

certificates/RELAX-CAP.json stores the 10-pattern optimal basis of the fractional relaxation of the final words' inventory
{4:26,5:2,6:16,7:52,8:99,9:213} with local profile {1:2445,2:706,3:232,4:108,5:18,8:8} (bins 672/448/448/448 per replica of
capacity 8/16/32/48, all 2,551 count-vector patterns with widths 4..9, one idle child per bin, the complete per-call local
profile paid). certificates/RELAX-STAGES.json stores the optimal bases of the parent (PR2942, 1,163 patterns), of stage 1
(joint rank-7 end frames) and of stage 2 (five extractions). tools/relax_exact.py checks, with exact rationals only, each
basis' primal feasibility (the cap is at least its root) and the sign of every pattern's reduced cost at the upper end of
the root bracket (weak duality: the cap is at most that end). The final optimum is FRACTIONAL per replica (basis
denominators 4 and 20), so no allocation realizes that basic solution literally at T74. This script checks that the
literal profile allocation/PROFILE.json is a complete profile of these words (666 calls x local + idle children, rank mass
74 x 65,088), that its exact root bracket lies below the cap (as weak duality requires), records the exact gap, and compares
the literal lower root exactly with the kappa fields of the pinned comparator claims (PR2969 in allocation/baseline/, and
PR2966, PR2957, PR2942 in comparators/). No optimality of the literal fill among integral allocations is claimed.
Marius-Paul Dumitrean, with substantial AI assistance (Claude Code). The relaxation model and root arithmetic are ours
(research/t37-word-level-census-r12 lineage, as shipped by PR2930).
"""
import gzip, json, sys
from fractions import Fraction as Q
from pathlib import Path
P = Path(__file__).resolve().parent
sys.path.insert(0, str(P / 'tools'))
import relax_exact as RE
import root as R

def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw)

def verify(cert, patterns):
    r = RE.verify_basis(cert['local_per_call'], cert['inventory_per_call'], cert['basis_patterns'])
    assert r['status'] == 'PASS_EXACT_RELAXATION_CAP' and r['patterns'] == patterns
    assert (Q(r['cap_lower']), Q(r['cap_upper'])) == (Q(cert['cap_lower']), Q(cert['cap_upper']))
    return r

def main():
    if not __debug__:
        raise SystemExit('refusing python -O')
    cert = read(P / 'certificates/RELAX-CAP.json')
    stages = read(P / 'certificates/RELAX-STAGES.json')
    words = [read(P / f'data/WORD-{t}.json.gz') for t in ('base', 'extra')]
    parents = [read(P / f'data/PARENT-{t}.json.gz') for t in ('base', 'extra')]
    for w in words:
        assert dict(w['report']['local_profile']) == cert['local_per_call'], 'certificate local profile = actual words'
        assert dict(w['report']['width_inventory']) == cert['inventory_per_call'], 'certificate inventory = actual words'
    for w in parents:
        assert dict(w['report']['local_profile']) == stages['parent']['local_per_call'] and dict(w['report']['width_inventory']) == stages['parent']['inventory_per_call']
    r = verify(cert, 2551)
    cap_lo, cap_hi = Q(r['cap_lower']), Q(r['cap_upper'])
    ladder = [('parent', verify(stages['parent'], 1163)), ('stage1', verify(stages['stage1'], 2551)), ('stage2', verify(stages['stage2'], 2551)), ('stage3', r)]
    assert all(Q(a[1]['cap_upper']) < Q(b[1]['cap_lower']) for a, b in zip(ladder, ladder[1:])), 'every stage raises the fixed-capacity cap'
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
    assert 0 < gap[0] <= gap[1] < Q(1, 10 ** 6), 'recorded gap'
    controls = {}
    try:
        bad = [dict(e) for e in cert['basis_patterns']]; bad[0] = dict(bad[0]); bad[0]['widths'] = list(bad[0]['widths']) + [4]
        RE.verify_basis(cert['local_per_call'], cert['inventory_per_call'], bad)
    except Exception as error:
        controls['perturbed_basis_pattern'] = str(error)[:160]
    else:
        raise AssertionError('perturbed basis accepted')
    stale = RE.verify_basis(stages['stage2']['local_per_call'], cert['inventory_per_call'], cert['basis_patterns'])
    assert stale['status'] == 'PASS_EXACT_RELAXATION_CAP' and Q(stale['cap_upper']) < cap_lo, 'the stage-2 local profile gives a strictly lower cap'
    controls['stage2_local_profile_lowers_the_cap'] = 'cap %s < %s' % (stale['cap_upper'], cert['cap_lower'])
    try:
        RE.verify_basis(cert['local_per_call'], cert['inventory_per_call'], stages['parent']['basis_patterns'])
    except Exception as error:
        controls['parent_basis_for_changed_inventory'] = str(error)[:160]
    else:
        raise AssertionError('the PR2942 basis must not certify the changed inventory')
    over = dict(profile); over[48] -= 1; over[24] = over.get(24, 0) + 2      # a finer idle split of the same rank mass
    if not R.kappa_from_profile(over, T)[1] < lo:
        raise AssertionError('a finer idle split must lower the literal root (concavity)')
    controls['finer_idle_split_lowers_root'] = 'PASS'
    headline = lo // Q(1, 10 ** 24) * Q(1, 10 ** 24) - Q(1, 10 ** 46) - Q(1, 10 ** 70)
    comparisons = {}
    for name, path in [('pr2969', P / 'allocation/baseline/CLAIM.json'), ('pr2966', P / 'comparators/PR2966-CLAIM.json'),
                       ('pr2957', P / 'comparators/PR2957-CLAIM.json'), ('pr2942', P / 'comparators/PR2942-CLAIM.json')]:
        kappa = Q(read(path)['kappa'])
        assert headline > kappa, ('strict gain over', name)
        comparisons[name] = {'kappa': str(kappa), 'gain': str(headline - kappa), 'gain_float': float(headline - kappa)}
    out = dict(status='PASS_LITERAL_ALLOCATION_BELOW_FIXED_INVENTORY_CAP_WITH_RECORDED_GAP', cap_lower=str(cap_lo), cap_upper=str(cap_hi),
               literal_lower=str(lo), literal_upper=str(hi), gap_lower=str(gap[0]), gap_upper=str(gap[1]), gap_float=float(gap[0]),
               tight_patterns=r['tight_patterns'], strict_patterns=r['strict_patterns'], idle_per_replica=r['idle_per_replica'],
               fractional_at_T74=fractional, literal_idle=idle, profile={str(k): v for k, v in sorted(profile.items())}, controls=controls,
               stage_caps={name: {'cap_lower': rr['cap_lower'], 'cap_upper': rr['cap_upper'], 'patterns': rr['patterns']} for name, rr in ladder},
               headline=str(headline), comparisons=comparisons)
    print(json.dumps(out, sort_keys=True))

if __name__ == '__main__':
    main()
