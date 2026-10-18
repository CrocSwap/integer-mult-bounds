# SPDX-License-Identifier: Apache-2.0
"""Independent literal audit of T21's partial dedicated-bank envelope.

No constructor is imported. Every source route, active residual lane, unused
coordinate, private address, data recipe and event multiplicity is checked.
This envelope is an overcharge device; its padding is absent from the final
recursive profile, so padding ranks are not charged as selected children.
"""
import argparse
import copy
from collections import defaultdict
from pathlib import Path
from common import read, require, identity, dump, sha


def audit(source, lifted):
    require((source['live'], source['physical']) == (11704, 12218), 'Source stock')
    require((lifted['live'], lifted['physical']) == (32424, 32938), 'Lifted stock')
    old = {(c['stage'], c['replica']): c for c in source['calls']}
    calls = {(c['stage'], c['replica']): c for c in lifted['calls']}
    require(len(calls) == len(lifted['calls']) == 189 and
            set(calls) == {(s, r) for s in range(9) for r in range(21)}, 'Lifted call inventory')
    used, counts = defaultdict(set), defaultdict(int)
    for (stage, replica), call in calls.items():
        group, lane = divmod(replica, 8)
        prior = old[stage, lane]
        require({k: v for k, v in call.items() if k not in ('replica', 'owners')} ==
                {k: v for k, v in prior.items() if k not in ('replica', 'owners')}, 'Literal source call metadata')
        require(len(call['owners']) == len(prior['owners']) == 728, 'Owner route count')
        require(len({family for family, route in call['owners']}) == 728, 'Per-call family alias')
        for index, ((family, route), (old_family, old_route)) in enumerate(zip(call['owners'], prior['owners'])):
            expected = old_family+7168*group if index < 224 else 18816+4536*group+old_family-7168
            require(family == expected and route == old_route, 'Literal mapped owner route')
            if index < 224:
                require(0 <= family < 18816, 'Data namespace')
                continue
            require(18816 <= family < 32424 and route[0] == 2, 'Dedicated bank namespace')
            if len(route) == 2:
                require(route[1] == lane, 'Full-width lane')
                start, width = 9*lane, 9
            else:
                require(len(route) == 4, 'Entering helper route format')
                start, width = route[1:3]
                require(start == width*lane and 1 <= width < 9, 'Entering residual lane')
            cells = set(range(start, start+width))
            require(not used[family] & cells, 'Disjoint active residual lanes')
            used[family].update(cells)
            counts[family] += 1
    require(set(used) == set(range(18816, 32424)), 'Complete bank family inventory')
    padding = lifted['bank_padding']
    require(padding['families'] == list(range(18816, 32424)), 'Padding family namespace')
    children = {c['family']: c for c in padding['children']}
    require(len(children) == len(padding['children']) == 13608 and set(children) == set(used), 'Padding child inventory')
    for family, cells in used.items():
        group = (family-18816)//4536
        require(counts[family] == (8, 8, 5)[group], 'Active lane multiplicity')
        unused = sorted(set(range(73))-cells)
        child = children[family]
        require(child['axis_indices'] == unused and child['rank'] == len(unused) and
                list(map(int, child['orthogonal_axes'])) == [1 << i for i in unused], 'Exact residual complement')
        require(cells == set(range(len(cells))), 'Residual lanes form coordinate prefix')
    require(len(lifted['idle_children']) == len(source['idle_children']) == 2016, 'Data idle inventory')
    for old_child, child in zip(source['idle_children'], lifted['idle_children']):
        require(old_child['replicas'] == 8 and child == dict(old_child, replicas=21), 'Data idle multiplicity')
    require(lifted['recipe'] == source['recipe'] and lifted['local_programs'] == source['local_programs'], 'Original data recipe and local programs')
    require(len(lifted['execution_schedule']) == len(source['execution_schedule']) == 32, 'Original event count')
    for before, event in zip(source['execution_schedule'], lifted['execution_schedule']):
        expected = copy.deepcopy(before)
        if 'replicas' in expected:
            require(expected['replicas'] == list(range(8)), 'Original event multiplicity')
            expected['replicas'] = list(range(21))
        if expected['kind'] == 'bank_padding_cover_sweep':
            expected['families'] = [18816, 32424]
        elif expected['kind'] == 'translate_every_live_family':
            expected.update(families=[0, 32424], charged_calls_per_cover=32424)
        require(event == expected, 'Lifted source-event semantics')
    require(lifted['cover_final_correction'] == dict(source['cover_final_correction'],
                families=[0, 32424], charged_calls_per_cover=32424), 'Final correction namespace')
    require(lifted['private_namespace'] == {k: [x+20720 for x in v]
                for k, v in source['private_namespace'].items()}, 'Private namespace translation')
    changed = {'version', 'live', 'physical', 'calls', 'idle_children', 'execution_schedule',
               'bank_padding', 'cover_final_correction', 'private_namespace', 'route_semantics', 'replica_lift'}
    require({k: v for k, v in lifted.items() if k not in changed} ==
            {k: v for k, v in source.items() if k not in changed}, 'No unapproved parent fields')
    require({k: v for k, v in lifted['route_semantics'].items() if k != 'helper'} ==
            {k: v for k, v in source['route_semantics'].items() if k != 'helper'}, 'Non-helper route semantics')
    return dict(status='PASS_INDEPENDENT_T21_PARTIAL_BANK_ENVELOPE', calls=189,
                active_helper_lanes=sum(counts.values()), bank_families=len(used),
                maximum_auxiliary_padding_rank=max(c['rank'] for c in children.values()),
                source_content_sha256=identity(source), parent_content_sha256=identity(lifted))


def controls(source, parent):
    mutations = [
        ('missing_fifth_lane', lambda t: t['calls'].pop()),
        ('bank_group_alias', lambda t: t['calls'][2]['owners'][224].__setitem__(0, t['calls'][0]['owners'][224][0])),
        ('missing_complement_axis', lambda t: t['bank_padding']['children'][-1]['axis_indices'].pop()),
        ('stale_complement_rank', lambda t: t['bank_padding']['children'][-1].__setitem__('rank', 1)),
        ('old_idle_multiplicity', lambda t: t['idle_children'][0].__setitem__('replicas', 16)),
        ('missing_sweep_replica', lambda t: t['execution_schedule'][0]['replicas'].pop()),
        ('private_alias', lambda t: t['private_namespace']['centers'].__setitem__(0, 18816)),
        ('short_final_correction', lambda t: t['cover_final_correction'].__setitem__('families', [0, 18816])),
    ]
    rejected = []
    for name, mutate in mutations:
        bad = copy.deepcopy(parent)
        mutate(bad)
        try:
            audit(source, bad)
        except ValueError as error:
            rejected.append(dict(name=name, reason=str(error)))
        else:
            raise ValueError('Accepted parent mutation: '+name)
    return rejected


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--parent', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    source, parent = read(args.source), read(args.parent)
    result = audit(source, parent)
    result['controls_rejected'] = controls(source, parent)
    result['input_sha256'] = dict(source=sha(args.source), parent=sha(args.parent))
    dump(args.out, result)
    print(result['status'], 'controls='+str(len(result['controls_rejected'])))
