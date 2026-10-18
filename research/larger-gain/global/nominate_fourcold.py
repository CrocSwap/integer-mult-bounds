#!/usr/bin/env python3
"""Nominate literal owners by repacking only single-nine and rank48 bins.

SciPy nominates an integer window allocation. Every expanded owner is then
checked exactly; independent physical controller admission remains required.
"""

import argparse
from collections import Counter, defaultdict
import copy
import gzip
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix, csr_matrix
from scipy.sparse.csgraph import maximum_flow


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def degrees_to_calls(demands, bin_degrees):
    """Bipartite Havel-Hakimi; no bin repeats a complete call."""
    remaining = list(bin_degrees)
    result = [[] for _ in remaining]
    for time, demand in sorted(demands.items(), key=lambda p: (-p[1], p[0])):
        chosen = sorted(range(len(remaining)), key=lambda j: (-remaining[j], j))[:demand]
        require(len(chosen) == demand and all(remaining[j] > 0 for j in chosen),
                'Integer allocation has no simple bin/call expansion')
        for j in chosen:
            result[j].append(time)
            remaining[j] -= 1
    require(not any(remaining), 'Unfilled bin degrees')
    return result


def restricted_degrees(demands, ports, forbidden):
    times = sorted(demands)
    sink = 1 + len(times) + len(ports)
    rr, cc, vv = [], [], []
    for index, time in enumerate(times):
        rr.append(0); cc.append(1 + index); vv.append(demands[time])
        for j, port in enumerate(ports):
            if time != forbidden[port]:
                rr.append(1 + index); cc.append(1 + len(times) + j); vv.append(1)
    for j in range(len(ports)):
        rr.append(1 + len(times) + j); cc.append(sink); vv.append(3)
    graph = csr_matrix((vv, (rr, cc)), shape=(sink + 1, sink + 1), dtype=np.int64)
    flow = maximum_flow(graph, 0, sink)
    require(flow.flow_value == sum(demands.values()), 'Restricted bin flow is infeasible')
    return [[time for i, time in enumerate(times)
             if flow.flow[1 + i, 1 + len(times) + j] == 1] for j in range(len(ports))]


def colored_three_slots(eights, nines, ports, forbidden):
    demands = [(time, width, value) for width, counts in ((8, eights), (9, nines))
               for time, value in counts.items() if value]
    times = sorted(set(eights) | set(nines))
    middle = {(time, port): 1 + len(demands) + i
              for i, (time, port) in enumerate((t, p) for t in times for p in ports
                                               if t != forbidden[p])}
    bin_start = 1 + len(demands) + len(middle)
    sink = bin_start + len(ports)
    rr, cc, vv = [], [], []
    for i, (time, _, value) in enumerate(demands):
        rr.append(0); cc.append(1 + i); vv.append(value)
        for port in ports:
            if (time, port) in middle:
                rr.append(1 + i); cc.append(middle[time, port]); vv.append(1)
    for j, port in enumerate(ports):
        for time in times:
            if (time, port) in middle:
                rr.append(middle[time, port]); cc.append(bin_start + j); vv.append(1)
        rr.append(bin_start + j); cc.append(sink); vv.append(3)
    flow = maximum_flow(csr_matrix((vv, (rr, cc)), shape=(sink + 1, sink + 1), dtype=np.int64), 0, sink)
    require(flow.flow_value == sum(value for _, _, value in demands), 'Colored owner expansion failed')
    return [[(time, width) for i, (time, width, _) in enumerate(demands)
             if (time, port) in middle and flow.flow[1 + i, middle[time, port]] == 1] for port in ports]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=Path, required=True)
    for name in ('zero', 'four', 'eight'):
        ap.add_argument('--' + name + '-local', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--seconds', type=float, default=60)
    args = ap.parse_args()
    require(not args.out.exists(), 'Use a new output directory')
    source_plan = args.source / 'data/PLAN.json'
    source_owners = args.source / 'data/OWNERS.json.gz'
    plan, roles = read(source_plan), read(source_owners)
    original = copy.deepcopy(plan)
    bins = defaultdict(list)
    for row in roles:
        bins[row['owner_replica'], row['child'], row['port']].append(row)
    groups = []
    for key, (capacity, window) in plan['windows'].items():
        replica, child = map(int, key.split(','))
        if capacity == 8:
            ports = list(range(112))
            require(all([r['width'] for r in bins[replica, child, port]] == [8]
                        for port in ports), 'Unexpected original rank8 pattern')
        elif capacity == 16:
            ports = [port for port in range(112)
                     if sorted(r['width'] for r in bins[replica, child, port]) in ([9], [8, 8])]
        elif capacity == 32:
            ports = list(range(112))
            require(all(sorted(r['width'] for r in bins[replica, child, port]) == [5, 9, 9, 9]
                        for port in ports), 'Unexpected original rank32 pattern')
        elif capacity == 48:
            ports = list(range(112))
            require(all(not bins[replica, child, port] or
                        [r['width'] for r in bins[replica, child, port]] == [9] * 5
                        for port in ports), 'Unexpected original rank48 pattern')
        else:
            continue
        if ports:
            group = dict(replica=replica, child=child, capacity=capacity, window=window, ports=ports)
            if capacity == 32:
                group['forbidden'] = {port: next(r['time'] for r in bins[replica, child, port]
                                               if r['width'] == 5) for port in ports}
            groups.append(group)
    movable = {(g['replica'], g['child'], port) for g in groups for port in g['ports']}
    is_movable = lambda r: r['width'] in (8, 9) and (r['owner_replica'], r['child'], r['port']) in movable
    demand = Counter(r['time'] for r in roles if is_movable(r) and r['width'] == 9)
    old_eights = Counter(r['time'] for r in roles if is_movable(r) and r['width'] == 8)
    require(all(demand[t] >= 3 for t in range(72)), 'Insufficient movable helpers')

    upper, labels, rows, lower_bounds, upper_bounds, costs = [], [], [], [], [], []

    def variable(label, bound, cost=0):
        index = len(upper)
        labels.append(label)
        upper.append(bound)
        costs.append(cost)
        return index

    def constraint(coefficients, lower, upper):
        rows.append(coefficients)
        lower_bounds.append(lower)
        upper_bounds.append(upper)

    eight_flow, nine_flow, conversions, full_bins, short_bins = defaultdict(list), defaultdict(list), [], [], []
    for gi, group in enumerate(groups):
        size = len(group['ports'])
        if group['capacity'] == 8:
            eights = {}
            for time in group['window']:
                e = variable(('eight', gi, time), size)
                eights[time] = e
                eight_flow[time].append(e)
            constraint({e: 1 for e in eights.values()}, size, size)
            group['eights'] = eights
        elif group['capacity'] == 16:
            c = variable(('convert', gi), size, 7 * math.log(7))
            group['convert'] = c
            conversions.append(c)
            eights, nines = {}, {}
            for time in group['window']:
                e = variable(('eight', gi, time), size)
                n = variable(('nine', gi, time), size)
                eights[time], nines[time] = e, n
                eight_flow[time].append(e)
                nine_flow[time].append(n)
                constraint({e: 1, c: -1}, -np.inf, 0)
                constraint({n: 1, c: 1}, -np.inf, size)
            constraint({**{e: 1 for e in eights.values()}, c: -2}, 0, 0)
            constraint({**{n: 1 for n in nines.values()}, c: 1}, size, size)
            group['eights'], group['nines'] = eights, nines
        elif group['capacity'] == 32:
            nines, eights = {}, {}
            for time in group['window']:
                bound = size - sum(t == time for t in group['forbidden'].values())
                n = variable(('nine', gi, time), bound)
                e = variable(('eight', gi, time), bound)
                nines[time] = n
                eights[time] = e
                nine_flow[time].append(n)
                eight_flow[time].append(e)
                constraint({n: 1, e: 1}, -np.inf, bound)
            constraint({n: 1 for n in list(nines.values()) + list(eights.values())}, 3 * size, 3 * size)
            group['nines'], group['eights'] = nines, eights
        else:
            patterns = {count: variable(('pattern48', gi, count), size,
                                        -(48 - 9 * count) * math.log(48 - 9 * count)) for count in range(6)}
            group['patterns'] = patterns
            constraint({v: 1 for v in patterns.values()}, size, size)
            nines = {}
            for time in group['window']:
                n = variable(('nine', gi, time), size)
                nines[time] = n
                nine_flow[time].append(n)
                constraint({n: 1, **{v: -1 for count, v in patterns.items() if count}}, -np.inf, 0)
            constraint({**{n: 1 for n in nines.values()}, **{v: -count for count, v in patterns.items()}}, 0, 0)
            group['nines'] = nines
    for time in range(72):
        constraint({v: 1 for v in eight_flow[time]}, old_eights[time] + 3, old_eights[time] + 3)
        constraint({v: 1 for v in nine_flow[time]}, demand[time] - 3, demand[time] - 3)
    rr, cc, vv = [], [], []
    for i, row in enumerate(rows):
        for j, value in row.items():
            rr.append(i); cc.append(j); vv.append(value)
    matrix = coo_matrix((vv, (rr, cc)), shape=(len(rows), len(upper))).tocsc()
    result = milp(np.array(costs), integrality=np.ones(len(upper)),
                  bounds=Bounds(np.zeros(len(upper)), upper),
                  constraints=LinearConstraint(matrix, lower_bounds, upper_bounds),
                  options={'time_limit': args.seconds, 'mip_rel_gap': 0})
    print('MIP', result.status, result.message, flush=True)
    require(result.x is not None, 'No integer window nomination')
    x = np.rint(result.x).astype(int)
    require(np.max(np.abs(result.x - x)) < 1e-6, 'Nonintegral nomination')
    require(all(0 <= int(value) <= upper[i] for i, value in enumerate(x)), 'Variable outside bounds')
    for row, lo, hi in zip(rows, lower_bounds, upper_bounds):
        value = sum(coefficient * int(x[i]) for i, coefficient in row.items())
        require(lo <= value <= hi, 'Exact constraint failed')

    # Helper names may be permuted within a complete call before geometry is
    # reassigned. This puts precisely the three newly shorter helpers into the
    # movable pool without disturbing widths or the fixed owners.
    swaps = []
    bycall = defaultdict(dict)
    for row in roles:
        bycall[row['time']][row['helper']] = row
    for time in range(72):
        for helper in (282, 294, 306):
            row = bycall[time][helper]
            if not is_movable(row):
                donor = next(r for r in bycall[time].values()
                             if is_movable(r) and r['width'] == 9 and r['helper'] not in (282, 294, 306))
                other = donor['helper']
                require(row['width'] == donor['width'] == 9, 'Helper swap width mismatch')
                row['helper'], donor['helper'] = other, helper
                bycall[time][other], bycall[time][helper] = row, donor
                swaps.append([time, helper, other])
    pools = defaultdict(list)
    fixed = []
    for row in roles:
        if is_movable(row):
            pools[row['time'], 8 if row['helper'] in (282, 294, 306) else row['width']].append(row['helper'])
        else:
            if row['width'] == 5 and (row['owner_replica'], row['child'], row['port']) in movable:
                row['offset'] = 0
            fixed.append(row)
    for value in pools.values():
        value.sort(reverse=True)
    rebuilt = list(fixed)
    allocation = []
    for group in groups:
        ports = group['ports']
        if group['capacity'] == 8:
            lists = degrees_to_calls({t: int(x[i]) for t, i in group['eights'].items()}, [1] * len(ports))
            widths = [8] * len(ports)
        elif group['capacity'] == 16:
            c = int(x[group['convert']])
            lists = degrees_to_calls({t: int(x[i]) for t, i in group['eights'].items()}, [2] * c)
            lists += degrees_to_calls({t: int(x[i]) for t, i in group['nines'].items()}, [1] * (len(ports) - c))
            widths = [8] * c + [9] * (len(ports) - c)
        elif group['capacity'] == 32:
            slot_lists = colored_three_slots({t: int(x[i]) for t, i in group['eights'].items()},
                                             {t: int(x[i]) for t, i in group['nines'].items()},
                                             ports, group['forbidden'])
        else:
            degrees = [count for count, variable_index in group['patterns'].items()
                       for _ in range(int(x[variable_index]))]
            lists = degrees_to_calls({t: int(x[i]) for t, i in group['nines'].items()}, degrees)
            widths = [9] * len(ports)
        if group['capacity'] != 32:
            slot_lists = [[(time, width) for time in times] for width, times in zip(widths, lists)]
        replica, child = group['replica'], group['child']
        for port, slots in zip(ports, slot_lists):
            offset = 5 if group['capacity'] == 32 else 0
            for time, width in sorted(slots):
                require(pools[time, width], 'Missing literal helper')
                helper = pools[time, width].pop()
                stage, call_replica = plan['order'][time]
                rebuilt.append(dict(child=child, copy=replica * 112 + port,
                                    family=replica * 896 + (2 * plan['pairs'][str(child)] + plan['sides'][str(child)]) * 112 + port,
                                    helper=helper, offset=offset, owner_replica=replica,
                                    port=port, replica=call_replica, stage=stage, time=time, width=width))
                offset += width
        allocation.append(dict(replica=replica, child=child, capacity=group['capacity'],
                               patterns=dict(Counter(str(tuple(sorted(width for _, width in slots))) for slots in slot_lists))))
    require(not any(pools.values()), 'Unassigned literal helpers')

    for name in ('zero', 'four', 'eight'):
        pid = 'rank5_' + name + '_cold'
        directory = getattr(args, name + '_local')
        canonical, checks = read(directory / 'CANONICAL-WORD.json.gz'), read(directory / 'LOCAL-CHECKS.json')
        description = plan['provider_registry'][pid]
        widths = [9 - len(canonical['frames'][frame]) for frame in canonical['start'][224:]]
        require([i for i, (a, b) in enumerate(zip(description['widths'], widths)) if a != b] == [282, 294, 306], 'Unexpected provider width changes')
        description['widths'] = widths
        description['artifact_sha256'] = {name: sha(directory / name) for name in description['artifact_sha256']}
        require(checks['forward']['paid_profile'] == checks['backward']['paid_profile'], 'Orientation profile mismatch')
        description['actual_paid_profile'] = checks['forward']['paid_profile']
        description['orientation_program_sha256'] = {key: value['sha256'] for key, value in checks.items()}
    selected = {(c['stage'], c['replica']): c for c in plan['provider_calls']}
    paid = Counter()
    for call in plan['provider_calls']:
        description = plan['provider_registry'][call['provider']]
        call['local_program_sha256'] = description['orientation_program_sha256'][call['orientation']]
        paid.update({int(k): value for k, value in description['actual_paid_profile'].items()})
    for call in plan['per_call_widths']:
        call['widths'] = plan['provider_registry'][selected[call['stage'], call['replica']]['provider']]['widths']
    occupied, call_families, call_helpers = defaultdict(set), defaultdict(set), defaultdict(set)
    for row in rebuilt:
        time, family, helper = row['time'], row['family'], row['helper']
        require(family not in call_families[time] and helper not in call_helpers[time], 'Whole owner or helper repeated')
        call_families[time].add(family); call_helpers[time].add(helper)
        cap, window = plan['windows'][f"{row['owner_replica']},{row['child']}"]
        require(time in window and row['offset'] >= 0 and row['offset'] + row['width'] <= cap, 'Invalid window or footprint')
        key = row['owner_replica'], row['child'], row['port']
        cells = set(range(row['offset'], row['offset'] + row['width']))
        require(not occupied[key] & cells, 'Residual overlap')
        occupied[key] |= cells
        call = plan['provider_calls'][time]
        require(row['width'] == plan['provider_registry'][call['provider']]['widths'][helper], 'Wrong literal width')
    require(all(call_helpers[time] == set(range(504)) for time in range(72)), 'Incomplete helper calls')
    remainders = Counter()
    for key, (capacity, _) in plan['windows'].items():
        replica, child = map(int, key.split(','))
        for port in range(112):
            cells = occupied[replica, child, port]
            require(cells == set(range(len(cells))), 'Non-prefix residual placement')
            if capacity > len(cells):
                remainders[capacity - len(cells)] += 1
    paid.update(remainders)
    require(sum(rank * number for rank, number in paid.items()) == 520704, 'Rank mass changed')
    rebuilt.sort(key=lambda r: (r['time'], r['helper']))
    raw = json.dumps(rebuilt, sort_keys=True, separators=(',', ':')).encode()
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    compressed = compressed[:9] + b'\xff' + compressed[10:]
    plan.update(status='FOUR_COLD_LITERAL_OWNER_NOMINATION_PENDING_ADMISSION',
                profile=dict(sorted(paid.items())), source_plan_sha256=sha(source_plan),
                source_owners_sha256=sha(source_owners), assignment_sha256=hashlib.sha256(compressed).hexdigest())
    args.out.mkdir(parents=True)
    (args.out / 'OWNERS.json.gz').write_bytes(compressed)
    (args.out / 'PLAN.json').write_text(json.dumps(plan, indent=2) + '\n')
    receipt = dict(status='PASS_EXACT_LITERAL_OWNER_NOMINATION_PENDING_PHYSICAL_ADMISSION',
                   source_plan_sha256=sha(source_plan), source_owners_sha256=sha(source_owners),
                   owners_sha256=sha(args.out / 'OWNERS.json.gz'), plan_sha256=sha(args.out / 'PLAN.json'),
                   fixed_roles=len(fixed), rebuilt_roles=len(rebuilt)-len(fixed), helper_swaps=swaps,
                   idle_remainders=dict(sorted(remainders.items())), profile=dict(sorted(paid.items())),
                   integer_variables=len(upper), integer_constraints=len(rows), allocations=allocation,
                   scope='Explicit whole-owner windows, disjoint residual prefixes, per-call uniqueness and literal selected widths checked. SciPy nominates only. Independent physical chronology, invoice, and exact recurrence admission remain mandatory.')
    (args.out / 'NOMINATION.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({key: receipt[key] for key in ('status', 'idle_remainders', 'profile')}))


if __name__ == '__main__':
    main()
