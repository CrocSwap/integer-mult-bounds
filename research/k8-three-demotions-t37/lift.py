#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Build the fixed T37 bank envelope and its source-event windows."""
import argparse
import copy
from collections import Counter, defaultdict
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def identity(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_gzip(path, value):
    raw = bytearray(gzip.compress(canonical(value), mtime=0))
    raw[9] = 255
    path.write_bytes(raw)


def lift(source):
    need((source['live'], source['physical']) == (11704, 12218), 'T8 source stock')
    data0, bank0, data, live = 7168, 4536, 33152, 55832
    groups = (8, 8, 8, 8, 5)
    target = copy.deepcopy(source)
    target['calls'] = []
    for call in source['calls']:
        for group, lanes in enumerate(groups):
            if call['replica'] >= lanes:
                continue
            new = copy.deepcopy(call)
            new['replica'] += 8*group
            new['owners'] = [[family+data0*group if family < data0 else
                              data+group*bank0+family-data0, route]
                             for family, route in new['owners']]
            target['calls'].append(new)
    for child in target['idle_children']:
        need(child['replicas'] == 8, 'T8 idle multiplicity')
        child['replicas'] = 37
    for event in target['execution_schedule']:
        if 'replicas' in event:
            need(event['replicas'] == list(range(8)), 'T8 sweep multiplicity')
            event['replicas'] = list(range(37))
        if event['kind'] == 'bank_padding_cover_sweep':
            event['families'] = [data, live]
        elif event['kind'] == 'translate_every_live_family':
            event.update(families=[0, live], charged_calls_per_cover=live)
    target['bank_padding']['families'], target['bank_padding']['children'] = [], []
    for group, lanes in enumerate(groups):
        for child in source['bank_padding']['children']:
            new = copy.deepcopy(child)
            new['family'] = data+group*bank0+child['family']-data0
            width, remainder = divmod(73-child['rank'], 8)
            need(remainder == 0 and 1 <= width <= 9, 'dedicated bank width')
            need(child['axis_indices'] == list(range(8*width, 73)), 'original complement indices')
            need(list(map(int, child['orthogonal_axes'])) ==
                 [1 << i for i in child['axis_indices']], 'original complement axes')
            new.update(axis_indices=list(range(lanes*width, 73)), rank=73-lanes*width)
            new['orthogonal_axes'] = [1 << i for i in new['axis_indices']]
            target['bank_padding']['children'].append(new)
            target['bank_padding']['families'].append(new['family'])
    target['bank_padding']['semantics'] = (
        'Each complement follows the complete calls in its bank group. '
        'Final hosting removes all dedicated banks and their padding children.')
    target['cover_final_correction'].update(families=[0, live], charged_calls_per_cover=live)
    target['private_namespace'] = {key: [live+x-source['live'] for x in interval]
                                  for key, interval in source['private_namespace'].items()}
    target.update(live=live, physical=live+514, version='r480-t37-bank-envelope-v1')
    target['route_semantics']['helper'] = (
        'The bank group is replica//8. Each local lane is replica%8. '
        'Residual and spectator routes retain their source coordinates.')
    target['replica_lift'] = dict(groups=list(groups), replicas=37, data_stock=data,
                                 bank_stock=22680, source_template_content_sha256=identity(source),
                                 phase_recipe_unchanged=True)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    need(not args.out.exists(), 'Choose a new lift directory')
    original = read(HERE / 'vendor/pr1074/T8/PLAN.json')
    owner_path = HERE / 'OWNERS.json.gz'
    owners, order = read(owner_path), read(HERE / 'ORDER.json')
    source = read(args.base / 'split-centres/GLOBAL-TEMPLATE.json.gz')
    need(source['exact_data_phase_recipe_sha256'] ==
         sha(args.base / 'work/complex-nine-native/DATA-PHASES.json'), 'data phase binding')
    module_path = HERE / 'vendor/pr1074/t16/build_parent.py'
    spec = importlib.util.spec_from_file_location('source_windows', module_path)
    windows_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(windows_module)
    need(windows_module.actual_windows(source, original['order'])[0] == original['windows'],
         'T8 source window replay')
    parent = lift(source)
    windows, schedule = windows_module.actual_windows(parent, order)
    used = defaultdict(set)
    at = {tuple(key): time for time, key in enumerate(order)}
    need(len(at) == 333 and len(owners) == 159840, 'complete call and helper inventory')
    for role in owners:
        need(role['time'] == at[role['stage'], role['replica']], 'role call time')
        capacity, times = windows[f"{role['owner_replica']},{role['child']}"]
        need(role['time'] in times, 'source-event window')
        group = role['owner_replica'], role['child'], role['port']
        cells = set(range(role['offset'], role['offset']+role['width']))
        need(not (used[group] & cells) and max(cells) < capacity, 'whole-helper capacity')
        used[group].update(cells)
    idle = Counter()
    for key, (capacity, _) in windows.items():
        replica, child = map(int, key.split(','))
        for port in range(112):
            cells = used[replica, child, port]
            need(cells == set(range(len(cells))), 'pending prefix')
            if len(cells) < capacity:
                idle[capacity-len(cells)] += 1
    need(idle == {1: 834, 48: 11374}, 'attaining idle profile')
    local = {int(r): n for r, n in original['provider_registry']['gauge44']['actual_paid_profile'].items()}
    profile = Counter({r: 333*n for r, n in local.items()})
    profile.update(idle)
    plan = copy.deepcopy(original)
    plan.update(T=37, live=33152, deficit=11840, order=order, windows=windows,
                profile={str(r): n for r, n in sorted(profile.items())},
                status='FROZEN_EXPLICIT_R480_T37_OWNER_NOMINATION',
                mode='k8-three-demotions-all-replica-optimum',
                solver_status='Frozen exact pattern flow and bipartite matching decomposition', gap=None)
    for field in ('provider_calls', 'per_call_widths'):
        bycall = {(c['stage'], c['replica']): c for c in original[field]}
        plan[field] = []
        for time, (stage, replica) in enumerate(order):
            call = copy.deepcopy(bycall[stage, replica % 8])
            call['replica'] = replica
            if 'time' in call:
                call['time'] = time
            plan[field].append(call)
    plan['assignment_sha256'] = sha(owner_path)
    plan['assignment_content_sha256'] = identity(owners)
    plan['replica_lift'] = dict(groups=[8, 8, 8, 8, 5], source_replicas=8, replicas=37,
                               parent_template_content_sha256=identity(parent),
                               owners_file_sha256=sha(owner_path), schedule_content_sha256=identity(schedule),
                               window_semantics='Strict physical source-event intervals, including bridges')
    need(sum(r*n for r, n in profile.items()) == 73*33152-11840, 'T37 rank mass')
    args.out.mkdir(parents=True)
    write_gzip(args.out / 'GLOBAL-TEMPLATE.json.gz', parent)
    (args.out / 'PLAN.json').write_text(json.dumps(plan, indent=2)+'\n')
    receipt = dict(status='PASS_R480_T37_BANK_LIFT_AND_WINDOWS', calls=333, roles=159840,
                   parent_live=55832, parent_physical=56346, bank_groups=[8,8,8,8,5],
                   idle=dict(sorted(idle.items())), literal_windows=len(windows),
                   parent_content_sha256=identity(parent), schedule_content_sha256=identity(schedule))
    (args.out / 'PARENT-LIFT.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(receipt['status'])


if __name__ == '__main__':
    main()
