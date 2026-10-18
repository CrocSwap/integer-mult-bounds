# SPDX-License-Identifier: Apache-2.0
"""Construct the 8+8+8+8+5 bank envelope and the bridge-aware T37 plan.

Extends Hao Yan's PR858 two-bank lift. The last group has five active residual
lanes; its padding is their exact orthogonal complement. These dedicated banks
are removed from the final hosted controller, not selected recursive children.
"""
import argparse
import copy
from pathlib import Path
from common import HERE, ROOT, read, require, sha, identity, dump, write_gzip, load


def lift(source):
    require((source['live'], source['physical']) == (11704, 12218), 'T8 source stock')
    data0, bank0, data, live = 7168, 4536, 33152, 55832
    t = copy.deepcopy(source)
    t['calls'] = []
    for call in source['calls']:
        for group, lanes in enumerate((8, 8, 8, 8, 5)):
            if call['replica'] >= lanes:
                continue
            new = copy.deepcopy(call)
            new['replica'] += 8*group
            new['owners'] = [[family+data0*group if family < data0 else
                              data+group*bank0+family-data0, route]
                             for family, route in new['owners']]
            t['calls'].append(new)
    for child in t['idle_children']:
        require(child['replicas'] == 8, 'T8 idle multiplicity')
        child['replicas'] = 37
    for event in t['execution_schedule']:
        if 'replicas' in event:
            require(event['replicas'] == list(range(8)), 'T8 sweep multiplicity')
            event['replicas'] = list(range(37))
        if event['kind'] == 'bank_padding_cover_sweep':
            event['families'] = [data, live]
        elif event['kind'] == 'translate_every_live_family':
            event.update(families=[0, live], charged_calls_per_cover=live)
    t['bank_padding']['families'], t['bank_padding']['children'] = [], []
    for group, lanes in enumerate((8, 8, 8, 8, 5)):
        for child in source['bank_padding']['children']:
            new = copy.deepcopy(child)
            new['family'] = data+group*bank0+child['family']-data0
            width, remainder = divmod(73-child['rank'], 8)
            require(remainder == 0 and 1 <= width <= 9, 'Dedicated bank residual width')
            require(child['axis_indices'] == list(range(8*width, 73)), 'Original complement coordinates')
            require(list(map(int, child['orthogonal_axes'])) ==
                    [1 << i for i in child['axis_indices']], 'Original complement axes')
            new.update(axis_indices=list(range(lanes*width, 73)), rank=73-lanes*width)
            new['orthogonal_axes'] = [1 << i for i in new['axis_indices']]
            t['bank_padding']['children'].append(new)
            t['bank_padding']['families'].append(new['family'])
    t['bank_padding']['semantics'] = (
        'Each listed coordinate complement acts once after its bank group has '
        'completed its 8, 8, 8, 8 or 5 disjoint residual lanes. Final hosting removes '
        'every dedicated bank and padding child.')
    t['cover_final_correction'].update(families=[0, live], charged_calls_per_cover=live)
    t['private_namespace'] = {key: [live+x-source['live'] for x in interval]
                              for key, interval in source['private_namespace'].items()}
    t.update(live=live, physical=live+514, version='t37-8-8-8-8-5-bank-envelope-v1')
    t['route_semantics']['helper'] = (
        'Bank group floor(replica/8), original lane replica%8. Groups have 8,8,8,8,5 '
        'active lanes; residual and spectator routes remain literal source routes.')
    t['replica_lift'] = dict(groups=[8, 8, 8, 8, 5], replicas=37, data_stock=data,
                             bank_stock=22680, source_template_content_sha256=identity(source),
                             phase_recipe_unchanged=True)
    return t


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--owners', type=Path, required=True)
    parser.add_argument('--order', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Lift output must be new')
    source = read(args.base/'split-centres/GLOBAL-TEMPLATE.json.gz')
    t = lift(source)
    original = read(ROOT/'research/gauge44-frames-x/data/PLAN.json')
    windows_module = load(HERE/'vendor/pr870/t16/build_parent.py', 'unchanged_physical_windows')
    require(windows_module.actual_windows(source, original['order'])[0] == original['windows'],
            'Original T8 physical-window replay')
    order, owners = read(args.order), read(args.owners)
    windows, schedule = windows_module.actual_windows(t, order)
    plan = read(HERE/'vendor/pr870/data/T8/PLAN.json')
    profile = {int(k): 333*v for k, v in read(HERE/'data/CLAIM.json')['local_profile'].items()}
    for rank, count in ((48, 11086), (1, 6)):
        profile[rank] = profile.get(rank, 0)+count
    plan.update(T=37, live=33152, deficit=11840, order=order, windows=windows,
                profile=dict(sorted(profile.items())), status='FROZEN_EXPLICIT_T37_WHOLE_OWNER_NOMINATION',
                mode='gauge44-U8-t37-21-plus-16-ten-role-trade',
                solver_status='Inherited T21 plus T16, ten frozen edits; no runtime optimizer')
    for field in ('provider_calls', 'per_call_widths'):
        bycall = {(c['stage'], c['replica']): c for c in plan[field]}
        plan[field] = []
        for time, (stage, replica) in enumerate(order):
            call = copy.deepcopy(bycall[stage, replica % 8])
            call['replica'] = replica
            if 'time' in call:
                call['time'] = time
            plan[field].append(call)
    plan['assignment_sha256'] = sha(args.owners)
    plan['assignment_content_sha256'] = identity(owners)
    plan['replica_lift'] = dict(groups=[8, 8, 8, 8, 5], source_replicas=8, replicas=37,
                                parent_template_content_sha256=identity(t),
                                owners_file_sha256=sha(args.owners), schedule_content_sha256=identity(schedule),
                                window_semantics='Strict physical source-event intervals, including bridges')
    at = {tuple(k): time for time, k in enumerate(order)}
    require(len(at) == 333 and len(owners) == 167832, 'T37 invocation/role inventory')
    for role in owners:
        require(role['time'] == at[role['stage'], role['replica']] and
                role['time'] in windows[f"{role['owner_replica']},{role['child']}"][1],
                'Actual source-event owner window')
    require(sum(rank*count for rank, count in profile.items()) == 73*33152-11840, 'T37 rank mass')
    args.out.mkdir(parents=True)
    write_gzip(args.out/'GLOBAL-TEMPLATE.json.gz', t)
    dump(args.out/'PLAN.json', plan)
    dump(args.out/'PARENT-LIFT.json', dict(status='PASS_T37_BANK_ENVELOPE_AND_PHYSICAL_WINDOWS',
                                         calls=333, checked_roles=len(owners), windows=len(windows),
                                         bank_groups=[8, 8, 8, 8, 5], parent_content_sha256=identity(t),
                                         actual_schedule_sha256=identity(schedule)))


if __name__ == '__main__':
    main()
