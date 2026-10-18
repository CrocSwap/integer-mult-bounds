# SPDX-License-Identifier: Apache-2.0
"""Finite whole-owner invoice by explicit event positions and sorted intervals.

Ross Richardson, with substantial OpenAI Codex assistance. The mathematical
owner/window model is credited to Tekalign, Marius-Paul Dumitrean, Mason Hale,
Yiyang Lu, Dugongue, Jeremy Diviney and Jeremy Kothe. No predecessor executable
is imported. This proves the named combinatorial invoice, not native admission.
"""
from bisect import bisect_left
from collections import Counter, defaultdict
import hashlib
import json


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def integer(value, low, high, reason):
    need(type(value) is int and low <= value < high, reason)
    return value


def event_windows(order, template, plan):
    """Return (replica,child)->(capacity,last source call,consumer call).

    Accesses are collected first and searched with bisect. The fractional
    event position distinguishes an idle consumer from a later bridge in the
    same call. Cached PLAN.windows and template replica/stock totals are unused.
    """
    need(type(order) is list and len(order) > 0 and len(order) % 9 == 0,
         'nine-stage order shape')
    replicas = len(order) // 9
    positions = {}
    for time, call in enumerate(order):
        need(type(call) is list and len(call) == 2, 'call shape')
        stage, replica = call
        integer(stage, 0, 9, 'stage domain')
        integer(replica, 0, replicas, 'replica domain')
        need((replica, stage) not in positions, 'duplicate call')
        positions[replica, stage] = time
    need(set(positions) == {(r, s) for r in range(replicas) for s in range(9)},
         'complete call domain')
    need(all(positions[r, s] < positions[r, s + 1]
             for r in range(replicas) for s in range(8)), 'replica chronology')

    local_recipe = [x for x in template['recipe'] if x['kind'] == 'local']
    need(len(local_recipe) == 9 and {x['stage'] for x in local_recipe} == set(range(9)),
         'nine local source stages')
    pair = {}
    for item in local_recipe:
        integer(item['stage'], 0, 9, 'recipe stage')
        pair[item['stage']] = integer(item['pair'], 0, 4, 'recipe pair')

    # A port-complete table avoids silently dropping an empty owner bin.
    bins = {}
    for item in template['idle_children']:
        child = integer(item['child'], 0, 18, 'child domain')
        port = integer(item['port'], 0, 112, 'idle port domain')
        cap = integer(item['rank'], 1, 73, 'idle capacity')
        need((child, port) not in bins, 'duplicate idle bin')
        bins[child, port] = cap
    need(set(bins) == {(c, p) for c in range(18) for p in range(112)},
         'complete child-port bins')
    capacities = {}
    for child in range(18):
        values = {bins[child, p] for p in range(112)}
        need(len(values) == 1, 'port-independent child capacity')
        capacities[child] = values.pop()

    blocks = {}
    current = None
    for event in template['execution_schedule']:
        kind = event['kind']
        if kind in ('bank_padding_cover_sweep', 'translate_every_live_family'):
            continue
        if kind == 'local_cover_sweep':
            current = event['stage']
            integer(current, 0, 9, 'schedule stage')
            need(current not in blocks, 'duplicate stage block')
            blocks[current] = []
        need(current is not None, 'event before first local source')
        need(kind in ('local_cover_sweep', 'idle_cover_sweep', 'bridge',
                      'terminal_Y_translations', 'terminal'), 'known source event')
        blocks[current].append(event)
    need(set(blocks) == set(range(9)), 'complete stage blocks')

    # Match the bridge/local source graph, independently of its idle consumers.
    schedule_graph = []
    for stage in range(9):
        for event in blocks[stage]:
            if event['kind'] == 'local_cover_sweep':
                schedule_graph.append(('local', stage, pair[stage]))
            elif event['kind'] == 'bridge':
                schedule_graph.append(('bridge', event['src'], event['dst'], event['coefficient']))
    recipe_graph = []
    for event in template['recipe']:
        if event['kind'] == 'local':
            recipe_graph.append(('local', event['stage'], event['pair']))
        elif event['kind'] == 'bridge':
            recipe_graph.append(('bridge', event['src'], event['dst'], event['coefficient']))
        else:
            need(event['kind'] == 'terminal', 'known recipe event')
    need(schedule_graph == recipe_graph, 'source graph binding')

    accesses = defaultdict(list)
    consumers = {}
    for time, (stage, replica) in enumerate(order):
        for slot, event in enumerate(blocks[stage]):
            position = (time, slot)
            kind = event['kind']
            if kind == 'local_cover_sweep':
                accesses[replica, pair[stage]].append(position)
            elif kind == 'bridge':
                for bank in (event['src'], event['dst']):
                    integer(bank, 0, 4, 'bridge bank')
                    accesses[replica, bank].append(position)
            elif kind == 'idle_cover_sweep':
                bank = integer(event['pair'], 0, 4, 'idle bank')
                for child in event['child_indices']:
                    if child not in capacities:
                        # Source children18,19 have no positive-rank idle bin.
                        need(child in (18, 19), 'unpriced child')
                        continue
                    need((replica, child) not in consumers, 'duplicate idle consumer')
                    need(plan['pairs'][str(child)] == bank, 'child bank binding')
                    integer(plan['sides'][str(child)], 0, 2, 'child side')
                    consumers[replica, child] = (position, bank)
    need(set(consumers) == {(r, c) for r in range(replicas) for c in capacities},
         'complete idle consumers')
    for timeline in accesses.values():
        timeline.sort()
    result = {}
    for key, (position, bank) in consumers.items():
        replica, child = key
        timeline = accesses[replica, bank]
        i = bisect_left(timeline, position)
        previous = timeline[i - 1][0] if i else -1
        result[key] = (capacities[child], previous, position[0])
    # A physical family may have several child names at different cuts.
    # Their full loan windows must be disjoint, not merely the listed loans.
    lifetimes = defaultdict(list)
    for (replica, child), (_, lo, hi) in result.items():
        side = plan['sides'][str(child)]
        lifetimes[replica, plan['pairs'][str(child)], side].append((lo, hi, child))
    for channel_windows in lifetimes.values():
        ordered = sorted(channel_windows)
        need(all(old[1] <= new[0] for old, new in zip(ordered, ordered[1:])),
             'disjoint physical-family loan lifetimes')
    return replicas, result


def invoice(order, fill, dispatch_rows, plan, template, providers,
            claimed_profile=None, claimed_physical=None):
    replicas, windows = event_windows(order, template, plan)
    calls = len(order)
    dispatch = {}
    for row in dispatch_rows:
        need(type(row) is list and len(row) == 3, 'dispatch row shape')
        stage, replica, provider = row
        integer(stage, 0, 9, 'dispatch stage')
        integer(replica, 0, replicas, 'dispatch replica')
        need(type(provider) is str and provider in providers, 'dispatch provider')
        need((stage, replica) not in dispatch, 'duplicate dispatch')
        dispatch[stage, replica] = provider
    need(set(dispatch) == set(map(tuple, order)), 'complete dispatch')
    need(fill['columns'] == ['time', 'helper', 'owner_replica', 'child', 'port', 'offset'],
         'role column contract')
    for row in fill.get('dispatch_overrides', []):
        need(len(row) == 3 and dispatch.get(tuple(row[:2])) == row[2], 'dispatch override')
    need(type(fill['rows']) is list and len(fill['rows']) == calls * 408,
         'complete helper role count')
    widths, local = {}, {}
    buffer_counts, center_counts = set(), set()
    for name, record in providers.items():
        need(len(record['widths']) == 408, '408 ordered helper widths')
        for width in record['widths']:
            integer(width, 1, 10, 'helper width domain')
        widths[name] = record['widths']
        local[name] = Counter(record['profile'])
        for rank, count in local[name].items():
            integer(rank, 1, 73, 'local rank domain')
            integer(count, 1, 10**8, 'local multiplicity')
        buffer_counts.add(record['buffer_count'])
        center_counts.add(record['center_count'])
    need(len(buffer_counts) == len(center_counts) == 1, 'shared private namespace')
    buffers = buffer_counts.pop()
    centers = center_counts.pop()
    integer(buffers, 0, 481, 'buffer namespace size')
    need(centers == 8, 'eight center namespaces')

    per_call_helpers = [set() for _ in order]
    per_call_families = [set() for _ in order]
    intervals = defaultdict(list)
    for index, row in enumerate(fill['rows']):
        need(type(row) is list and len(row) == 6 and all(type(v) is int for v in row),
             'integer helper role')
        time, helper, owner, child, port, offset = row
        integer(time, 0, calls, 'role time')
        integer(helper, 0, 408, 'role helper')
        integer(port, 0, 112, 'role port')
        need((owner, child) in windows, 'owner child domain')
        cap, previous, deadline = windows[owner, child]
        need(previous < time <= deadline, 'source-event window')
        need(helper not in per_call_helpers[time], 'unique helper at call')
        per_call_helpers[time].add(helper)
        family = (owner, plan['pairs'][str(child)], plan['sides'][str(child)], port)
        need(family not in per_call_families[time], 'distinct physical family at call')
        per_call_families[time].add(family)
        width = widths[dispatch[tuple(order[time])]][helper]
        need(0 <= offset and offset + width <= cap, 'owner capacity')
        intervals[owner, child, port].append((offset, offset + width, index))
    need(all(len(identities) == 408 for identities in per_call_helpers),
         'all helper identities at every call')

    residual = Counter()
    used_mass = 0
    occupied_bins = 0
    for (owner, child), (capacity, _, _) in sorted(windows.items()):
        for port in range(112):
            cursor = 0
            segments = intervals.get((owner, child, port), [])
            for start, end, _ in sorted(segments):
                need(start >= cursor, 'disjoint owner intervals')
                need(start == cursor, 'compact owner prefix')
                cursor = end
            occupied_bins += bool(segments)
            used_mass += cursor
            if cursor < capacity:
                residual[capacity - cursor] += 1
    capacity_mass = sum(capacity * 112 for capacity, _, _ in windows.values())
    need(used_mass == sum(sum(widths[dispatch[tuple(call)]]) for call in order),
         'whole-helper mass identity')
    need(sum(rank * count for rank, count in residual.items()) == capacity_mass - used_mass,
         'complete residual mass identity')
    profile = residual.copy()
    for call in order:
        profile.update(local[dispatch[tuple(call)]])
    rank_mass = sum(rank * count for rank, count in profile.items())
    need(rank_mass == 65088 * replicas, 'global rank mass')
    if claimed_profile is not None:
        need(profile == Counter({int(k): v for k, v in claimed_profile.items()}),
             'complete profile equality')
    live = 896 * replicas
    physical = live + 408 + centers + buffers + 2
    if claimed_physical is not None:
        need(type(claimed_physical) is int and physical == claimed_physical,
             'private stock equality')
    window_payload = [[*key, *value] for key, value in sorted(windows.items())]
    lifetime_streams = len({(r, plan['pairs'][str(c)], plan['sides'][str(c)])
                            for r, c in windows})
    return dict(replicas=replicas, calls=calls, roles=len(fill['rows']),
                source_windows=len(windows), owner_bins=len(windows) * 112,
                physical_lifetime_streams=lifetime_streams,
                physical_lifetime_transitions=len(windows) - lifetime_streams,
                occupied_bins=occupied_bins, capacity_mass=capacity_mass,
                hosted_width_mass=used_mass, residual_profile=dict(sorted(residual.items())),
                profile=dict(sorted(profile.items())), rank_mass=rank_mass,
                live_families=live, physical_families=physical, private_buffers=buffers,
                source_window_sha256=hashlib.sha256(json.dumps(window_payload,
                    separators=(',', ':')).encode()).hexdigest(),
                private_namespace={'centers': [live, live + centers],
                    'helpers': [live + centers, live + centers + 408],
                    'zero_buffers': [live + centers + 408, live + centers + 408 + buffers],
                    'coefficient': [physical - 2, physical]},
                scope='Finite source-event windows, whole-owner intervals, complete local/idle rank bill and namespace count. Native/physical realization, precision, outer and all-size obligations remain separate.')
