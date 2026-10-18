#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fractions-only certificate that the literal allocation attains the fixed-capacity packing optimum.

certificates/RELAX-CAP.json stores the 9-pattern optimal basis of the fractional relaxation of PR2917's
unchanged inventory (bins 672/448/448/448 per replica of capacity 8/16/32/48, all 1,163 count-vector
patterns, one idle child per bin, the complete per-call local profile paid). tools/relax_exact.py checks,
with exact rationals only: primal feasibility of the basis (so the cap is at least its root) and the sign of
every pattern's reduced cost at the upper end of the root bracket (weak duality: the cap is at most that
end). This script then checks that the literal complete profile of allocation/PROFILE.json EQUALS the
basic solution's profile summed over the 74 replicas (666 calls x local + 74 x idle), and that its exact
root bracket equals the cap bracket. Hence no allocation of these words, under these capacities and this
relaxation, can have a larger complex endpoint. It is not a bound over changed words or other templates.
Marius-Paul Dumitrean, with substantial AI assistance (Claude Code). The relaxation model and root
arithmetic are ours (research/t37-word-level-census-r12 lineage); the moment model is the shared
complete-profile moment used by PR2857/PR2917.
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

def main():
    if not __debug__:
        raise SystemExit('refusing python -O')
    cert = read(P / 'certificates/RELAX-CAP.json')
    words = [read(P / f'data/WORD-{t}.json.gz') for t in ('base', 'extra')]
    for w in words:
        assert {k: v for k, v in w['report']['local_profile'].items()} == cert['local_per_call'], 'certificate local profile = actual words'
        assert {k: v for k, v in w['report']['width_inventory'].items()} == cert['inventory_per_call'], 'certificate inventory = actual words'
    r = RE.verify_basis(cert['local_per_call'], cert['inventory_per_call'], cert['basis_patterns'])
    assert r['status'] == 'PASS_EXACT_RELAXATION_CAP' and r['patterns'] == 1163
    assert Q(r['cap_lower']) == Q(cert['cap_lower']) and Q(r['cap_upper']) == Q(cert['cap_upper'])
    T, calls = 74, 666
    expected = {}
    for k, v in cert['local_per_call'].items():
        expected[int(k)] = expected.get(int(k), 0) + calls * v
    for k, v in r['idle_per_replica'].items():
        n = T * Q(v)
        assert n.denominator == 1, 'integral idle multiplicity at T74'
        expected[int(k)] = expected.get(int(k), 0) + int(n)
    profile = {int(k): v for k, v in read(P / 'allocation/PROFILE.json').items()}
    assert profile == expected, 'literal complete profile equals the fractional optimum profile'
    lo, hi = R.kappa_from_profile(profile, T)
    assert (lo, hi) == (Q(cert['cap_lower']), Q(cert['cap_upper'])), 'literal root bracket equals the cap bracket'
    # rejection controls: a perturbed basis and a perturbed profile must fail
    controls = {}
    try:
        bad = [dict(e) for e in cert['basis_patterns']]; bad[0] = dict(bad[0]); bad[0]['widths'] = list(bad[0]['widths']) + [4]
        RE.verify_basis(cert['local_per_call'], cert['inventory_per_call'], bad)
    except Exception as error:
        controls['perturbed_basis_pattern'] = str(error)[:120]
    else:
        raise AssertionError('perturbed basis accepted')
    # a finer split of one idle rank-3 child into rank 1 + rank 2 (same rank mass) lowers the root strictly
    # (concavity) and is not the optimum's profile
    finer = dict(profile); finer[3] -= 1; finer[1] += 1; finer[2] += 1
    assert sum(r * n for r, n in finer.items()) == sum(r * n for r, n in profile.items())
    if not R.kappa_from_profile(finer, T)[1] < lo:
        raise AssertionError('a finer idle split must fall strictly below the cap')
    if finer == expected:
        raise AssertionError('profile-equality check must reject a perturbed profile')
    controls['finer_split_strictly_below_cap_and_rejected'] = 'PASS'
    out = dict(status='PASS_LITERAL_ALLOCATION_ATTAINS_FIXED_INVENTORY_CAP', cap_lower=str(lo), cap_upper=str(hi),
               tight_patterns=r['tight_patterns'], strict_patterns=r['strict_patterns'], idle_per_replica=r['idle_per_replica'],
               profile={str(k): v for k, v in sorted(profile.items())}, controls=controls)
    print(json.dumps(out, sort_keys=True))

if __name__ == '__main__':
    main()
