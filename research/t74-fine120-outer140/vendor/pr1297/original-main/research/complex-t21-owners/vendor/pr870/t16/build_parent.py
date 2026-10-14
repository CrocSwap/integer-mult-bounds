#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Hao Yan (@FanPUYen)
"""Lift the PR741 controller and PR799 provider plan to sixteen replicas.

Authored with OpenAI Codex assistance. Precursor credit: the PR514/PR484/PR507
controller lineage, PR558/PR589 admission, Chafik Boukhalfa's PR741 frames
and owner map, and Jeremy Kothe's PR799 paired-read-exchange provider.
This script changes only the global replica namespace and the nominated owner
map; it reuses the exact local programs and exact data-phase recipes.
"""
import argparse
import copy
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

SOURCE_PLAN_SHA256 = '5f40e7ccfca61f298539b4f41286d2a9d62caf947057f9cec82aa53f73f707fd'
SOURCE_OWNERS_SHA256 = '99d1c4caf85855c353d30f122d9efbd9e51562914facded13027f347b18a6082'


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def portable_gzip(raw):
    compressed = bytearray(gzip.compress(raw, mtime=0))
    compressed[9] = 255  # RFC1952 OS=unknown, independent of zlib/Python platform.
    return bytes(compressed)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def content_sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def lift_parent(source, copies=2):
    """A direct sum of bank/data stocks; erased private streams are shared.

    copies=1 is deliberately the identity, byte-for-byte after canonicalization.
    The helper routes retain replica lanes 0..7 in each *separate* bank group.
    No axis index is inferred from the new global replica label 8..15.
    """
    require(type(copies) is int and copies in (1, 2), 'only identity or T16 lift')
    t = copy.deepcopy(source)
    if copies == 1:
        return t
    require(source['m'] == 73, 'source dimension')
    require(len(source['calls']) == 72, 'source calls')
    data = 8*8*112
    bank_stock = source['live'] - data
    private_stock = source['physical'] - source['live']
    require((bank_stock, private_stock) == (9*504, 504+8+2), 'source namespace')
    require({(c['stage'], c['replica']) for c in source['calls']} ==
            {(s, r) for s in range(9) for r in range(8)}, 'source coverage')
    new_data = copies*data
    new_live = copies*source['live']
    new_physical = new_live + private_stock
    t['calls'] = []
    for c in source['calls']:
        for group in range(copies):
            new = copy.deepcopy(c)
            new['replica'] = c['replica'] + 8*group
            owners = []
            for family, route in c['owners']:
                require(0 <= family < source['live'], 'owner outside live stock')
                mapped = (family + data*group if family < data else
                          new_data + group*bank_stock + family - data)
                owners.append([mapped, copy.deepcopy(route)])
            new['owners'] = owners
            t['calls'].append(new)
    # Every data/idle recipe is a portwise direct sum, hence only multiplicity
    # changes. Its local axis labels and exact phase words stay unchanged.
    for child in t['idle_children']:
        require(child['replicas'] == 8, 'source idle multiplicity')
        child['replicas'] *= copies
    for event in t['execution_schedule']:
        if 'replicas' in event:
            require(event['replicas'] == list(range(8)), 'source sweep replicas')
            event['replicas'] = list(range(8*copies))
        if event['kind'] == 'bank_padding_cover_sweep':
            event['families'] = [new_data, new_live]
        elif event['kind'] == 'translate_every_live_family':
            event['families'] = [0, new_live]
            event['charged_calls_per_cover'] = new_live
    t['bank_padding']['families'] = []
    t['bank_padding']['children'] = []
    for group in range(copies):
        for family in source['bank_padding']['families']:
            t['bank_padding']['families'].append(new_data + group*bank_stock + family - data)
        for child in source['bank_padding']['children']:
            new = copy.deepcopy(child)
            new['family'] = new_data + group*bank_stock + child['family'] - data
            t['bank_padding']['children'].append(new)
    t['cover_final_correction'].update(families=[0, new_live], charged_calls_per_cover=new_live)
    t['private_namespace'] = {
        key: [new_live + x - source['live'] for x in interval]
        for key, interval in source['private_namespace'].items()
    }
    t.update(live=new_live, physical=new_physical,
             version='t16-direct-sum-two-bank-groups-parent-v1')
    t['route_semantics']['helper'] = (
        'Two independent groups of nine dedicated banks. Group floor(replica/8) '
        'selects the bank namespace; the stored original helper route retains '
        'lane replica%8. All original residual/spectator axes are unchanged.')
    t['loop_order'] = (
        'For each recipe phase: the explicit calls order, then every cover class d; '
        'each local invocation completes before the next. Each original replica '
        'has a disjoint data and bank namespace in its group; private erased '
        'streams are reused between completed calls.')
    t['replica_lift'] = dict(
        source_template_content_sha256=content_sha(source), groups=copies,
        source_replicas=8, replicas=8*copies, data_stock=new_data,
        bank_stock=copies*bank_stock, banks_per_stage=copies*504,
        private_helpers=504, local_programs_content_sha256=content_sha(source['local_programs']),
        construction='direct sum of data and dedicated banks; share only restored private streams',
        phase_recipe_unchanged=True)
    # Source data and helper owner routes are preserved literally in each copy.
    for c in t['calls']:
        group, replica = divmod(c['replica'], 8)
        old = next(z for z in source['calls'] if (z['stage'], z['replica']) == (c['stage'], replica))
        require([r for f, r in c['owners']] == [r for f, r in old['owners']], 'route changed')
        require(c['window'] == old['window'], 'local window changed')
        require(len({f for f, r in c['owners']}) == len(c['owners']), 'per-call owner alias')
    require(t['local_programs'] == source['local_programs'], 'program changed')
    require(t['recipe'] == source['recipe'], 'data recipe changed')
    require(len(t['bank_padding']['children']) == copies*bank_stock, 'bank padding count')
    require(t['physical'] == t['live']+514, 'private namespace size')
    return t


def expanded_schedule(parent, order):
    blocks = {}
    globals_ = []
    stage = None
    for index, event in enumerate(parent['execution_schedule']):
        if event['kind'] in ('bank_padding_cover_sweep', 'translate_every_live_family'):
            globals_.append((index, event))
            continue
        if event['kind'] == 'local_cover_sweep':
            stage = event['stage']
            blocks[stage] = []
        require(stage is not None, 'event precedes first stage')
        blocks[stage].append((index, event))
    schedule = []
    for time, (stage, replica) in enumerate(order):
        for index, event in blocks[stage]:
            new = copy.deepcopy(event)
            new.update(source_event=index, replica=replica, replicas=[replica], time=time)
            schedule.append(new)
    for index, event in globals_:
        schedule.append(dict(event, source_event=index))
    return schedule


def actual_windows(parent, order):
    ranks = {c['child']: c['rank'] for c in parent['idle_children']}
    stage_pair = {e['stage']: e['pair'] for e in parent['recipe'] if e['kind'] == 'local'}
    last, intervals, callpos, perrep = {}, {}, {}, {}
    schedule = expanded_schedule(parent, order)
    for pos, event in enumerate(schedule):
        if 'replica' not in event:
            continue
        replica = event['replica']
        perrep.setdefault(replica, []).append(event['source_event'])
        if event['kind'] == 'local_cover_sweep':
            last[replica, stage_pair[event['stage']]] = pos
            callpos[event['time']] = pos
        elif event['kind'] == 'bridge':
            last[replica, event['src']] = last[replica, event['dst']] = pos
        elif event['kind'] == 'idle_cover_sweep':
            for child in event['child_indices']:
                if child in ranks:
                    intervals[replica, child] = (last.get((replica, event['pair']), -1), pos)
    require(all(events == list(range(30)) for events in perrep.values()), 'per-replica projection')
    require([e['source_event'] for e in schedule if 'replica' not in e] == [30, 31], 'global tail')
    require(set(callpos) == set(range(len(order))), 'complete schedule')
    windows = {f'{replica},{child}': [ranks[child], [time for time, pos in sorted(callpos.items()) if start < pos < stop]]
               for (replica, child), (start, stop) in intervals.items()}
    return windows, schedule


def lift_plan(source, parent, owners, source_plan_sha, source_owners_sha, owners_sha):
    p = copy.deepcopy(source)
    require(source['T'] == 8 and len(source['order']) == 72, 'source plan dimensions')
    order = [[stage, replica + 8*group] for stage, replica in source['order'] for group in range(2)]
    windows, schedule = actual_windows(parent, order)
    # These windows are recomputed from actual source-event touches, not copied
    # from the old nomination. Their T8 restriction must recover the old plan.
    rank = Counter({int(k): 2*v for k, v in source['profile'].items()})
    rank.update({48: 1, 44: -1, 3: -2, 2: 1})
    rank = +rank
    p.update(status='FROZEN_EXPLICIT_T16_TWO_BANK_DIRECT_SUM_OWNER_NOMINATION',
             mode='gauge44-all144-t16-idle-concentration', T=16, live=14336,
             deficit=5120, profile=dict(sorted(rank.items())), order=order, windows=windows,
             solver_status='explicit two-role augmenting path and two-bin recombination', gap=None,
             source_plan_sha256=source_plan_sha, source_owners_sha256=source_owners_sha,
             assignment_sha256=owners_sha, assignment_content_sha256=content_sha(owners))
    for field in ('provider_calls', 'per_call_widths'):
        p[field] = []
        for old in source[field]:
            for group in range(2):
                new = copy.deepcopy(old)
                new['replica'] += 8*group
                if 'time' in new:
                    new['time'] = 2*old['time']+group
                p[field].append(new)
    at = {tuple(x): i for i, x in enumerate(order)}
    for field in ('provider_calls', 'per_call_widths'):
        p[field].sort(key=lambda c: at[c['stage'], c['replica']])
    p['replica_lift'] = dict(groups=2, source_replicas=8, replicas=16,
                             parent_template_content_sha256=content_sha(parent), owners_file_sha256=owners_sha,
                             window_semantics='strict physical source-event touch intervals, including bridges',
                             schedule_content_sha256=content_sha(schedule))
    require(len(owners) == 144*504, 'owner role count')
    for role in owners:
        require(role['time'] == at[role['stage'], role['replica']], 'role call time')
        require(role['time'] in windows[f"{role['owner_replica']},{role['child']}"][1],
                'owner outside actual source-event window')
    require(sum(int(k)*v for k,v in p['profile'].items()) == 73*p['live']-p['deficit'], 'rank mass')
    return p, schedule


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--source-plan', type=Path, required=True)
    parser.add_argument('--source-owners', type=Path, required=True)
    parser.add_argument('--owners', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'output directory already exists')
    require(sha(args.source_plan) == SOURCE_PLAN_SHA256, 'source plan byte pin')
    require(sha(args.source_owners) == SOURCE_OWNERS_SHA256, 'source owners byte pin')
    source_path = args.base/'split-centres/GLOBAL-TEMPLATE.json.gz'
    source = read(source_path)
    original_plan = read(args.source_plan)
    require(lift_parent(source, 1) == source, 'T8 identity control')
    require(actual_windows(source, original_plan['order'])[0] == original_plan['windows'], 'T8 source-window replay')
    require(source['exact_data_phase_recipe_sha256'] == sha(args.base/'work/complex-nine-native/DATA-PHASES.json'), 'source exact data-phase binding')
    parent = lift_parent(source)
    owners = read(args.owners)
    plan, schedule = lift_plan(original_plan, parent, owners, sha(args.source_plan), sha(args.source_owners), sha(args.owners))
    args.out.mkdir(parents=True)
    (args.out/'GLOBAL-TEMPLATE.json.gz').write_bytes(portable_gzip(canonical(parent)))
    (args.out/'PLAN.json').write_bytes((json.dumps(plan, indent=2)+'\n').encode('utf-8'))
    receipt = dict(status='PASS_T16_DIRECT_SUM_PARENT_AND_LITERAL_SOURCE_WINDOWS',
                   source_template_file_sha256=sha(source_path), source_template_content_sha256=content_sha(source),
                   source_plan_sha256=sha(args.source_plan), source_owners_sha256=sha(args.source_owners),
                   owners_sha256=sha(args.owners),
                   parent_template_file_sha256=sha(args.out/'GLOBAL-TEMPLATE.json.gz'),
                   parent_template_content_sha256=content_sha(parent), plan_sha256=sha(args.out/'PLAN.json'),
                   T8_identity_control=True, T8_source_window_identity=True,
                   local_programs_identical=True, exact_data_phases_identical=True,
                   parent_live=parent['live'], parent_physical=parent['physical'],
                   bank_stock=9072, banks_per_stage=1008, private_helpers=504,
                   source_idle_children_charged=sum(c['replicas'] for c in parent['idle_children']),
                   events=len(schedule), replica_source_events=30, global_source_events=[30,31],
                   calls=len(plan['order']), roles=len(owners), actual_window_membership_checked=len(owners),
                   scope='Legal direct-sum parent namespace and actual source-event windows; full global emitter, geometry, finite invoice, and recurrence admission remain separate checks.')
    (args.out/'PARENT-LIFT-RECEIPT.json').write_bytes((json.dumps(receipt, indent=2)+'\n').encode('utf-8'))
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
