#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent F2 pending-axis and chronological reservation audit of PR1094.

Prepared for Akiva with substantial OpenAI Codex assistance. Reads pinned data
only; imports no supplier, compiler, owner auditor or pricing implementation.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PORTS, PAIRS, REPLICAS, STAGES = 112, 4, 16, 9


class Rejected(ValueError):
    pass


def require(ok, rule):
    if not ok:
        raise Rejected(rule)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rank(vectors):
    pivots = {}
    for vector in vectors:
        require(type(vector) is int and 0 < vector < 1 << 73, 'AXIS_DOMAIN')
        while vector:
            pivot = vector.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = vector
                break
            vector ^= pivots[pivot]
    return len(pivots)


def orthonormal(vectors):
    return all((x & y).bit_count() % 2 == int(i == j)
               for i, x in enumerate(vectors) for j, y in enumerate(vectors[:i + 1]))


def source_geometry(template, phases):
    """Rebuild child placement, independently check the cross-child Gram premise."""
    events = template['execution_schedule'][:30]
    require(len(events) == 30, 'SOURCE_EVENT_COUNT')
    require([e['kind'] for e in template['execution_schedule'][30:]] ==
            ['bank_padding_cover_sweep', 'translate_every_live_family'], 'SOURCE_GLOBAL_TAIL')
    pairs = {e['stage']: e['pair'] for e in template['recipe'] if e['kind'] == 'local'}
    require(set(pairs) == set(range(STAGES)), 'SOURCE_STAGE_INVENTORY')
    blocks, placement = defaultdict(list), {}
    stage = -1
    for index, event in enumerate(events):
        if event['kind'] == 'local_cover_sweep':
            require(event['stage'] == stage + 1, 'SOURCE_STAGE_ORDER')
            stage += 1
        require(stage >= 0, 'SOURCE_FIRST_EVENT')
        blocks[stage].append((index, event))
        if event['kind'] == 'idle_cover_sweep':
            require(len(event['child_indices']) == 2, 'SOURCE_IDLE_SIDES')
            for side, child in enumerate(event['child_indices']):
                require(child not in placement, 'SOURCE_CHILD_INVENTORY')
                placement[child] = (event['pair'], side)
    require(set(blocks) == set(range(STAGES)), 'SOURCE_BLOCK_INVENTORY')
    require(set(placement) == set(range(20)), 'SOURCE_CHILD_INVENTORY')
    axes, bases = {}, {}
    recipes = {r['port']: r for r in phases['recipes']}
    require(len(recipes) == len(phases['recipes']) == PORTS, 'SOURCE_PORT_INVENTORY')
    require(set(recipes) == set(range(PORTS)), 'SOURCE_PORT_INVENTORY')
    gram_entries = 0
    for port, recipe in recipes.items():
        children = recipe['idle_children']
        if isinstance(children, dict):
            children = [children[str(i)] for i in range(20)]
        require(len(children) == 20, 'SOURCE_PHASE_CHILDREN')
        by_family = defaultdict(list)
        for child, item in enumerate(children):
            vectors = item['orthogonal_axes']
            require(type(item['rank']) is int and item['rank'] == len(vectors), 'CHILD_RANK')
            require(rank(vectors) == len(vectors), 'CHILD_LINEAR_INDEPENDENCE')
            require(orthonormal(vectors), 'CHILD_GRAM')
            axes[child, port] = tuple(vectors)
            by_family[placement[child]].extend(vectors)
        for (pair, side), vectors in by_family.items():
            require(len(vectors) == len(set(vectors)), 'CROSS_CHILD_SET_DISJOINTNESS')
            require(orthonormal(vectors), 'CROSS_CHILD_GRAM')
            require(rank(vectors) == len(vectors), 'CROSS_CHILD_LINEAR_INDEPENDENCE')
            bases[pair, side, port] = tuple(vectors)
            gram_entries += len(vectors) * (len(vectors) + 1) // 2
    return dict(blocks=blocks, placement=placement, pairs=pairs, axes=axes,
                bases=bases, gram_entries=gram_entries)


def helper_widths(word):
    count = word['report']['R']
    require(type(count) is int and count == 480, 'HELPER_COUNT')
    full = [1 << i for i in range(9)]
    widths = []
    for register in range(224, 224 + count):
        final = word['helper_final'].get(str(register), full)
        initial = word['start_extra'].get(str(register), [])
        require(rank(final + initial) == rank(final), 'HELPER_NESTING')
        width = rank(final) - rank(initial)
        require(0 < width <= 9, 'HELPER_WIDTH')
        widths.append(width)
    return widths


def chronological_events(geometry, order):
    require(len(order) == STAGES * REPLICAS and
            set(map(tuple, order)) == {(s, r) for s in range(STAGES) for r in range(REPLICAS)},
            'CALL_INVENTORY')
    events, projection = [], defaultdict(list)
    for time, (stage, replica) in enumerate(order):
        for index, event in geometry['blocks'][stage]:
            projection[replica].append(index)
            events.append((time, replica, event))
    require(all(projection[r] == list(range(30)) for r in range(REPLICAS)), 'SOURCE_PROJECTION')
    return events


def sweep(geometry, widths, roles, order, events):
    """Hold chart reservations until their actual idle sweep, without PLAN windows.

    A reservation is an accounting mark, not an execution of the scalar word.
    Local/bridge source touches must see no unreleased mark on either side.
    """
    require(len(roles) == len(order) * len(widths), 'ROLE_COUNT')
    calls, helper_sets = defaultdict(list), defaultdict(set)
    family_sets = defaultdict(set)
    for role in roles:
        require(all(type(v) is int for v in role.values()), 'ROLE_INTEGER_DOMAIN')
        time, helper = role['time'], role['helper']
        require(0 <= time < len(order), 'ROLE_CALL_DOMAIN')
        require((role['stage'], role['replica']) == tuple(order[time]), 'ROLE_CALL_BINDING')
        require(0 <= helper < len(widths) and helper not in helper_sets[time], 'ROLE_HELPER_INVENTORY')
        helper_sets[time].add(helper)
        require(role['width'] == widths[helper], 'ROLE_WIDTH')
        owner, child, port = role['owner_replica'], role['child'], role['port']
        require(0 <= owner < REPLICAS and child in geometry['placement'] and 0 <= port < PORTS,
                'ROLE_OWNER_DOMAIN')
        pair, side = geometry['placement'][child]
        family = owner * 896 + (2 * pair + side) * PORTS + port
        require(role['family'] == family and role['copy'] == owner * PORTS + port, 'ROLE_FAMILY_BINDING')
        require(family not in family_sets[time], 'ROLE_FAMILY_COLLISION')
        family_sets[time].add(family)
        stage, replica = order[time]
        require((owner, pair) != (replica, geometry['pairs'][stage]), 'ROLE_ACTIVE_PAIR')
        offset, width = role['offset'], role['width']
        axes = geometry['axes'][child, port]
        require(0 <= offset and offset + width <= len(axes), 'ROLE_SLICE_DOMAIN')
        calls[time].append(role)
    require(all(helper_sets[t] == set(range(len(widths))) for t in range(len(order))),
            'ROLE_HELPER_INVENTORY')
    reservations, closed, occupied = defaultdict(dict), set(), defaultdict(set)
    held = 0
    cuts = [0]
    total = 0
    call_count = 0
    idle_profile = Counter()

    def touch(replica, pair):
        require(all(not reservations[replica, pair, side, port]
                    for side in range(2) for port in range(PORTS)), 'SOURCE_TOUCH_WITH_RESERVATION')

    for time, replica, event in events:
        kind = event['kind']
        if kind == 'local_cover_sweep':
            touch(replica, geometry['pairs'][event['stage']])
            require(tuple(order[time]) == (event['stage'], replica), 'EVENT_CALL_BINDING')
            call_count += 1
            for role in calls[time]:
                owner, child, port = role['owner_replica'], role['child'], role['port']
                require((owner, child) not in closed, 'ROLE_AFTER_IDLE_SWEEP')
                pair, side = geometry['placement'][child]
                start, width = role['offset'], role['width']
                physical = reservations[owner, pair, side, port]
                for offset in range(start, start + width):
                    axis = geometry['axes'][child, port][offset]
                    require(axis not in physical, 'RESERVATION_COLLISION')
                    physical[axis] = child
                    occupied[owner, child, port].add(offset)
                held += width
                total += width
        elif kind == 'bridge':
            touch(replica, event['src'])
            touch(replica, event['dst'])
        elif kind == 'idle_cover_sweep':
            for side, child in enumerate(event['child_indices']):
                require((replica, child) not in closed, 'DUPLICATE_IDLE_SWEEP')
                closed.add((replica, child))
                for port in range(PORTS):
                    physical = reservations[replica, event['pair'], side, port]
                    release = [axis for axis, c in physical.items() if c == child]
                    for axis in release:
                        del physical[axis]
                    held -= len(release)
                    used = occupied[replica, child, port]
                    require(used == set(range(len(used))), 'OCCUPIED_PREFIX_GAP')
                    remaining = len(geometry['axes'][child, port]) - len(used)
                    if remaining:
                        idle_profile[remaining] += 1
        elif kind in ('terminal_Y_translations', 'terminal'):
            for pair in range(PAIRS):
                touch(replica, pair)
        else:
            raise Rejected('UNSUPPORTED_SOURCE_EVENT')
        cuts.append(held)
    require(call_count == len(order), 'EXECUTED_CALL_COUNT')
    require(len(closed) == 20 * REPLICAS and held == 0 and all(not v for v in reservations.values()),
            'UNCLOSED_RESERVATION')
    return dict(roles=len(roles), calls=call_count, source_events=len(events), cuts=len(cuts),
                reserved_axis_instances=total, peak_reserved_axes=max(cuts),
                peak_cut_indices=[i for i, n in enumerate(cuts) if n == max(cuts)],
                cut_reserved_axes=cuts,
                cut_trace_sha256=hashlib.sha256(json.dumps(cuts, separators=(',', ':')).encode()).hexdigest(),
                idle_profile={str(k): v for k, v in sorted(idle_profile.items())})


def audit(geometry, widths, roles, plan):
    order = plan['order']
    events = chronological_events(geometry, order)
    result = sweep(geometry, widths, roles, order, events)
    require(result['idle_profile'] == plan['_expected_idle'], 'IDLE_PROFILE_BINDING')
    return result


def pinned_inputs(pins=None):
    pins = read(HERE / 'SOURCES.json') if pins is None else pins
    data = {}
    for key, entry in pins['inputs'].items():
        path = (ROOT / entry['path']).resolve()
        require(path.is_relative_to(ROOT) and path.is_file(), 'SOURCE_PATH')
        require(digest(path) == entry['sha256'], 'SOURCE_PIN_' + key)
        data[key] = read(path)
    return pins, data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='Write a deterministic receipt instead of comparing RESULT.json')
    args = parser.parse_args()
    pins, data = pinned_inputs()
    geometry = source_geometry(data['template'], data['phases'])
    widths = helper_widths(data['word'])
    plan = dict(data['plan'], _expected_idle=data['spec']['expected']['idle_remainder_profile'])
    result = audit(geometry, widths, data['owners'], plan)
    local = data['word']['report']['local_profile']
    profile = Counter({int(k): STAGES * REPLICAS * n for k, n in local.items()})
    profile.update({int(k): v for k, v in result['idle_profile'].items()})
    require({str(k): v for k, v in sorted(profile.items())} == data['profile'], 'COMPLETE_PROFILE_BINDING')
    result.update(status='PASS_SELECTED1094_PENDING_AXIS_AUDIT',
                  base_commit=pins['base_commit'], inputs=pins['inputs'],
                  verifier_sha256=digest(Path(__file__)),
                  physical_port_bases=len(geometry['bases']), gram_entries=geometry['gram_entries'],
                  basis_size_histogram={str(k): v for k, v in sorted(Counter(map(len, geometry['bases'].values())).items())},
                  complete_profile={str(k): v for k, v in sorted(profile.items())},
                  scope='Finite source-bound pending-axis independence and chronological reservation audit; no scalar, native, precision, invoice, pricing or all-size proof.')
    if args.out:
        args.out.write_text(json.dumps(result, indent=2) + '\n')
    else:
        require(result == read(HERE / 'RESULT.json'), 'COMMITTED_RECEIPT')
    print(result['status'], f"{result['roles']} roles; {result['gram_entries']} exact Gram entries; {result['cuts']} cuts")


if __name__ == '__main__':
    main()
