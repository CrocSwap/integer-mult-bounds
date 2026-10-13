"""Audit the frozen owner map and its callwise fixed point using integers.

The parent window catalogue is an explicit input. The package's independent
global verifier must additionally derive the windows from the actual program.
This audit does not certify local algebra, phase charts, or an exponent.
"""
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import hashlib
import json

from reuse_owners import packed, read, sha, signature


HERE = Path(__file__).resolve().parent


def semantic_sha(path):
    return hashlib.sha256(packed(read(path))).hexdigest()


def add_inputs(parser):
    parser.add_argument('--parent-plan', type=Path, required=True)
    parser.add_argument('--parent-owners', type=Path, required=True)
    provider = parser.add_mutually_exclusive_group(required=True)
    provider.add_argument('--local44', type=Path, help='Independently checked native provider directory')
    provider.add_argument('--raw-word', type=Path, help='New FULL-WORD.json.gz; nomination signature only')


def bound_inputs(args, manifest):
    assert sha(args.parent_plan) == manifest['parent_plan_sha256'], 'Wrong parent PLAN'
    assert sha(args.parent_owners) == manifest['parent_owners_sha256'], 'Wrong parent OWNERS'
    plan = read(args.parent_plan)
    assert (plan['K'], plan['T'], plan['M'], plan['L'], plan['live']) == (4, 8, 73, 9, 7168)
    provider_path = args.local44 if args.local44 is not None else args.raw_word
    sig = signature(provider_path)
    expected = manifest['new_provider']
    assert len(sig['widths']) == expected['R']
    assert hashlib.sha256(packed(sig['widths'])).hexdigest() == expected['width_vector_sha256']
    assert sig['profile'] == {int(r): n for r, n in expected['profile'].items()}
    assert Counter(sig['widths']) == {int(w): n for w, n in expected['width_histogram'].items()}
    assert sum(sig['widths']) == expected['width_sum']
    assert sum(r*n for r, n in sig['profile'].items()) == expected['rank_mass']
    return plan, sig, provider_path


def audit(plan, sig, owners):
    V, R = 112, 492
    order = [tuple(c) for c in plan['order']]
    assert len(order) == 72 and len(set(order)) == 72
    assert len(owners) == 72*R
    bycall = defaultdict(dict)
    cells = defaultdict(set)
    caps, family, eligible = {}, {}, defaultdict(list)
    for key, (cap, times) in plan['windows'].items():
        rep, child = map(int, key.split(','))
        assert 0 <= cap <= 48 and len(times) == len(set(times))
        for port in range(V):
            g = (rep, child, port)
            caps[g] = cap
            family[g] = rep*8*V + (2*plan['pairs'][str(child)] + plan['sides'][str(child)])*V + port
            for t in times:
                assert 0 <= t < len(order)
                eligible[t].append(g)
    for t, gs in eligible.items():
        assert len({family[g] for g in gs}) == len(gs), 'Multiple eligible children on one family'
        stage, rep = order[t]
        pair = max(0, (stage-1)//2)
        assert all(g[0] != rep or plan['pairs'][str(g[1])] != pair for g in gs)
    for z in owners:
        t, h = z['time'], z['helper']
        assert 0 <= t < len(order) and 0 <= h < R
        assert (z['stage'], z['replica']) == order[t]
        assert h not in bycall[t]
        assert z['width'] == sig['widths'][h]
        g = (z['owner_replica'], z['child'], z['port'])
        assert g in caps and t in plan['windows'][f'{g[0]},{g[1]}'][1]
        assert z['copy'] == g[0]*V + g[2] and z['family'] == family[g]
        off, width = z['offset'], z['width']
        assert 0 <= off and off+width <= caps[g]
        occupied = set(range(off, off+width))
        assert not cells[g] & occupied, 'Overlapping hosted coordinates'
        cells[g] |= occupied
        bycall[t][h] = (g, width)
    for t in range(72):
        assert set(bycall[t]) == set(range(R))
        assert len({family[g] for g, w in bycall[t].values()}) == R
    for occupied in cells.values():
        assert occupied == set(range(len(occupied))), 'Uncompacted hosted coordinates'
    used = {g: len(cells[g]) for g in caps}
    idle = Counter(caps[g]-used[g] for g in caps if caps[g] > used[g])
    paid = Counter({r: 72*n for r, n in sig['profile'].items()})
    paid.update(idle)

    # Independent cost-level fixed-point check. No helper-ID or family-ID
    # tie-breaking is needed: equal capacities give the same histogram.
    for t in range(72):
        old = {g: w for g, w in bycall[t].values()}
        assert len(old) == R
        before = Counter(caps[g]-used[g] for g in eligible[t])
        available = sorted(caps[g]-used[g]+old.get(g, 0) for g in eligible[t])
        want = Counter(sig['widths'])
        after = Counter()
        for cap in available:
            width = next((w for w in sorted(want, reverse=True) if want[w] and w <= cap), 0)
            if width:
                want[width] -= 1
            after[cap-width] += 1
        assert not any(want.values()), 'Greedy assignment unexpectedly infeasible'
        assert after == before, ('Frozen map is not callwise optimal', t)
    mass = sum(r*n for r, n in paid.items())
    assert 73*7168-mass == 2560 and max(paid) == 48
    return {
        'roles': len(owners), 'calls': 72, 'fixed_point_calls_checked': 72,
        'remainder_profile': dict(sorted(idle.items())),
        'global_profile': dict(sorted(paid.items())),
        'rank_mass': mass, 'deficit': 2560, 'maxchild': 48,
        'all_footprints_disjoint_compacted_prefixes': True,
        'all_helper_families_idle_and_outside_active_data': True,
        'one_helper_per_physical_family_per_call': True,
        'every_call_optimal_for_every_concave_remainder_cost': True,
        'global_optimality_claimed': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_inputs(parser)
    parser.add_argument('--owners', type=Path, default=HERE/'frozen/OWNERS.json.gz')
    parser.add_argument('--majorization', type=Path, default=HERE/'frozen/MAJORIZATION.json.gz')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    manifest = read(HERE/'frozen/MANIFEST.json')
    plan, sig, provider_path = bound_inputs(args, manifest)
    assert semantic_sha(args.owners) == manifest['artifacts']['OWNERS.json.gz']['semantic_sha256']
    assert semantic_sha(args.majorization) == manifest['artifacts']['MAJORIZATION.json.gz']['semantic_sha256']
    result = audit(plan, sig, read(args.owners))
    for key in ('remainder_profile', 'global_profile'):
        assert result[key] == {int(r): n for r, n in manifest[key].items()}
    moves = read(args.majorization)
    checked = 0
    for move in moves:
        if move['equal_width_multiset']:
            margins = move['integer_stoploss_margins']
            assert len(margins) == 49 and all(type(x) is int and x >= 0 for x in margins)
            assert margins[0] == margins[-1] == 0
            assert move['strict_majorization'] == bool(any(margins))
            checked += 1
        else:
            assert move['bootstrap'] and move['integer_stoploss_margins'] is None
    assert checked == 288 and len(moves) == 289
    result.update({
        'status': 'PASS_FROZEN_HOSTING_AND_ALL_72_CALLWISE_FIXED_POINTS',
        'parent_plan_sha256': sha(args.parent_plan),
        'parent_owners_sha256': sha(args.parent_owners),
        'owners_semantic_sha256': semantic_sha(args.owners),
        'majorization_semantic_sha256': semantic_sha(args.majorization),
        'stored_integer_majorization_steps': checked,
        'majorization_replay': 'reproduce.py re-executes every step; this audit separately checks the final fixed point.',
        'remaining_scope': 'The package global verifier checks fresh local algebra, phases, windows, invoice, moment, and outer assembly.',
    })
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
