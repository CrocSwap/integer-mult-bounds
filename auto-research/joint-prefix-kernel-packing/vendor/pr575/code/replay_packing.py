#!/usr/bin/env python3
"""Rebuild the PR571 owner layout under two explicit helper bijections.

Only the Python standard library is used. This checks unchanged literal slot
geometry, helper inventories, complete calls and the complete paid histogram.
Source-derived bridge/Clifford and local-word admission are separate checks.
Adapted from PR571 frontier-composition/relabel_owners.py; Apache-2.0.
Prepared with OpenAI Codex assistance.
"""
import argparse
from collections import Counter, defaultdict
import copy
import gzip
import hashlib
import json
from pathlib import Path

if not __debug__:
    raise RuntimeError('Assertions must remain enabled')

GEOMETRY = ('K', 'T', 'M', 'L', 'live', 'deficit', 'order', 'windows', 'sides', 'pairs')

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')

def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)

def rebuild(recipe, source_plan, source_owners, plan):
    assert recipe['schema'] == 'source-bound-helper-bijection-v1'
    assert digest(source_plan) == recipe['source_plan_content_sha256']
    assert digest(source_owners) == recipe['source_owners_content_sha256']
    assert {k: plan[k] for k in GEOMETRY} == {k: source_plan[k] for k in GEOMETRY}
    assert len(plan['provider_calls']) == len(source_plan['provider_calls']) == 72
    mappings = recipe['providers']
    assert set(mappings) == set(source_plan['provider_registry'])
    assert {v['target'] for v in mappings.values()} == set(plan['provider_registry'])
    permutations = {}
    for old_id, entry in mappings.items():
        old = source_plan['provider_registry'][old_id]
        new = plan['provider_registry'][entry['target']]
        assert all(old[k] == new[k] for k in ('ports', 'centers'))
        assert len(old['widths']) == len(new['widths']) == 504
        assert all(type(w) is int and 0 < w <= 9 for w in old['widths'] + new['widths'])
        perm = list(range(504))
        used = set()
        for pair in entry['swaps']:
            assert len(pair) == 2 and all(type(h) is int and 0 <= h < 504 for h in pair)
            i, j = pair
            assert i != j and not (set(pair) & used)
            used.update(pair)
            perm[i], perm[j] = perm[j], perm[i]
        assert set(perm) == set(range(504))
        assert all(old['widths'][h] == new['widths'][perm[h]] for h in range(504))
        assert new['actual_paid_profile'] == entry['target_paid_profile']
        permutations[old_id] = perm

    local = Counter()
    dispatch = Counter()
    for t, (old, new) in enumerate(zip(source_plan['provider_calls'], plan['provider_calls'])):
        assert old['time'] == new['time'] == t
        assert [new['stage'], new['replica']] == plan['order'][t]
        assert all(old[k] == new[k] for k in ('stage', 'replica', 'orientation'))
        assert new['provider'] == mappings[old['provider']]['target']
        desc = plan['provider_registry'][new['provider']]
        assert new['local_program_sha256'] == desc['orientation_program_sha256'][new['orientation']]
        assert plan['per_call_widths'][t] == desc['widths']
        local.update({int(r): n for r, n in desc['actual_paid_profile'].items()})
        dispatch[new['provider']] += 1
    assert dict(dispatch) == recipe['dispatch']

    owners = copy.deepcopy(source_owners)
    changed = 0
    for row in owners:
        old_id = source_plan['provider_calls'][row['time']]['provider']
        before = row['helper']
        row['helper'] = permutations[old_id][before]
        changed += row['helper'] != before
    owners.sort(key=lambda row: (row['time'], row['helper']))
    assert len(owners) == 36288
    by_call = defaultdict(list)
    cells = defaultdict(set)
    for row in owners:
        assert all(type(v) is int for v in row.values())
        t = row['time']
        call = plan['provider_calls'][t]
        assert (row['stage'], row['replica']) == (call['stage'], call['replica'])
        desc = plan['provider_registry'][call['provider']]
        assert row['width'] == desc['widths'][row['helper']]
        r, c, p = row['owner_replica'], row['child'], row['port']
        assert 0 <= r < 8 and 0 <= c < 18 and 0 <= p < 112
        assert row['family'] == 896*r + 112*(2*plan['pairs'][str(c)] + plan['sides'][str(c)]) + p
        assert row['copy'] == 112*r + p
        cap, times = plan['windows'][f'{r},{c}']
        footprint = set(range(row['offset'], row['offset'] + row['width']))
        assert t in times and min(footprint) >= 0 and max(footprint) < cap
        assert not cells[r, c, p] & footprint
        cells[r, c, p].update(footprint)
        by_call[t].append(row)
    assert set(by_call) == set(range(72))
    for rows in by_call.values():
        assert len(rows) == len({r['family'] for r in rows}) == 504
        assert {r['helper'] for r in rows} == set(range(504))
    idle = Counter()
    for key, (cap, _) in plan['windows'].items():
        r, c = map(int, key.split(','))
        for p in range(112):
            footprint = cells[r, c, p]
            assert footprint == set(range(len(footprint)))
            if len(footprint) < cap:
                idle[cap-len(footprint)] += 1
    profile = local + idle
    assert {str(r): n for r, n in sorted(profile.items())} == plan['profile'] == recipe['profile']
    assert sum(r*n for r, n in profile.items()) == 520704 == 73*7168-2560
    assert {str(r): n for r, n in sorted(idle.items())} == recipe['idle_remainders']
    assert changed == recipe['changed_helper_rows'] == 72
    return owners, dict(status='PASS_SOURCE_BOUND_HELPER_BIJECTION', roles=len(owners),
                        changed_helper_rows=changed, dispatch=dict(sorted(dispatch.items())),
                        idle_remainders=dict(sorted(idle.items())), profile=dict(sorted(profile.items())),
                        rank_mass=520704, deficit=2560, owners_content_sha256=digest(owners),
                        physical_geometry='Every source role field except helper is preserved.',
                        scope='Finite owner reconstruction and complete-profile recount only; separate local, phase, source-derived geometry, invoice and outer admissions are required.')

def controls(recipe, source_plan, source_owners, plan):
    """Reject changed geometry, provider use, and even inventory-preserving drift."""
    rejected = []
    for name in ('source_owner', 'physical_window', 'duplicate_swap', 'width_slot',
                 'dispatch', 'orientation_program', 'paid_profile'):
        r, s, o, p = copy.deepcopy((recipe, source_plan, source_owners, plan))
        if name == 'source_owner':
            o[0]['offset'] += 1
        elif name == 'physical_window':
            key = next(iter(p['windows']))
            p['windows'][key][0] += 1
        elif name == 'duplicate_swap':
            r['providers']['fourcold_eight']['swaps'].append([299,271])
        elif name == 'width_slot':
            w = p['provider_registry']['eightcold_eight']['widths']
            i, j = w.index(8), w.index(9)
            w[i], w[j] = w[j], w[i]
        elif name == 'dispatch':
            c = next(c for c in p['provider_calls'] if c['provider'] == 'eightcold_eight')
            c['provider'] = 'width7_eight'
        elif name == 'orientation_program':
            p['provider_calls'][0]['local_program_sha256'] = '0'*64
        else:
            p['profile']['2'] -= 3
            p['profile']['3'] += 2
        try:
            rebuild(r, s, o, p)
        except AssertionError:
            rejected.append(name)
        else:
            raise AssertionError('Accepted invalid packing control: ' + name)
    return rejected

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('recipe', 'source-plan', 'source-owners', 'plan', 'owners', 'receipt'):
        ap.add_argument('--' + name, type=Path, required=True)
    args = ap.parse_args()
    recipe = read(args.recipe)
    assert sha(args.source_plan) == recipe['source_plan_sha256']
    assert sha(args.source_owners) == recipe['source_owners_sha256']
    plan = read(args.plan)
    source_plan, source_owners = read(args.source_plan), read(args.source_owners)
    owners, receipt = rebuild(recipe, source_plan, source_owners, plan)
    assert canonical(owners) == gzip.decompress(args.owners.read_bytes())
    assert sha(args.owners) == plan['assignment_sha256']
    receipt.update(recipe_sha256=sha(args.recipe), plan_sha256=sha(args.plan), owners_sha256=sha(args.owners),
                   source_plan_sha256=sha(args.source_plan), source_owners_sha256=sha(args.source_owners))
    receipt['negative_controls_rejected'] = controls(recipe, source_plan, source_owners, plan)
    args.receipt.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(receipt, indent=2))

if __name__ == '__main__':
    main()
