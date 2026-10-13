#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Hao Yan (@FanPUYen)
"""Construct the T16 owner map by eleven frozen edits, without an optimizer.

Authored with OpenAI Codex assistance. Precursor credit: Chafik Boukhalfa's
PR741 frames and owner map, Jeremy Kothe's PR799 paired-read-exchange provider,
and the PR514/PR484/PR507 whole-owner controller lineage.
The original map is duplicated into disjoint replica namespaces. One two-role
augmenting path and two tail-bin repartitions concentrate idle remainders.
Actual source-event windows are checked separately by build_parent.py and the
independent global geometry audit; the source-window screen here is not that
geometric proof.
"""
import argparse
import copy
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

SOURCE_PLAN_SHA256 = '5f40e7ccfca61f298539b4f41286d2a9d62caf947057f9cec82aa53f73f707fd'
SOURCE_OWNERS_SHA256 = '99d1c4caf85855c353d30f122d9efbd9e51562914facded13027f347b18a6082'
EXPECTED_IDLE = {1: 2, 2: 1, 44: 1, 48: 4793}
# (time, helper, width, old(replica,child,port,offset), new(...)).
# Helpers are zero-based, excluding the 224 local data wires.
EDITS = (
    (2, 5, 4, (0, 8, 0, 0), (7, 8, 78, 26)),
    (107, 360, 9, (14, 15, 0, 0), (6, 15, 0, 9)),
    (112, 193, 4, (6, 15, 0, 9), (6, 15, 0, 18)),
    (113, 193, 4, (14, 15, 0, 9), (14, 15, 0, 0)),
    (116, 181, 4, (7, 8, 78, 26), (14, 15, 0, 4)),
    (134, 414, 4, (6, 15, 0, 13), (6, 15, 0, 22)),
    (135, 414, 4, (14, 15, 0, 13), (14, 15, 0, 8)),
    (136, 414, 4, (6, 15, 0, 17), (6, 15, 0, 26)),
    (137, 414, 4, (14, 15, 0, 17), (14, 15, 0, 12)),
    (140, 87, 8, (6, 15, 0, 21), (14, 15, 0, 16)),
    (141, 87, 8, (14, 15, 0, 21), (14, 15, 0, 24)),
)


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def portable_gzip(raw):
    compressed = bytearray(gzip.compress(raw, mtime=0))
    compressed[9] = 255
    return bytes(compressed)


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def location(role):
    return tuple(role[key] for key in ('owner_replica', 'child', 'port', 'offset'))


def move(role, destination, plan):
    replica, child, port, offset = destination
    role.update(owner_replica=replica, child=child, port=port, offset=offset,
                copy=replica*112+port,
                family=replica*896+(2*plan['pairs'][str(child)]+plan['sides'][str(child)])*112+port)


def duplicate(source):
    require(len(source) == 72*504, 'source role count')
    result = []
    for role in source:
        for group in range(2):
            new = dict(role)
            new['owner_replica'] += 8*group
            new['replica'] += 8*group
            new['copy'] = new['owner_replica']*112+new['port']
            new['family'] += 7168*group
            new['time'] = 2*role['time']+group
            result.append(new)
    result.sort(key=lambda role: (role['time'], role['helper']))
    require(len({(r['time'], r['helper']) for r in result}) == len(result), 'duplicate role identity')
    return result


def construct(source, plan):
    roles = duplicate(source)
    bykey = {(r['time'], r['helper']): r for r in roles}
    for time, helper, width, old, new in EDITS:
        role = bykey[time, helper]
        require(location(role) == old and role['width'] == width, 'frozen edit source mismatch')
        move(role, new, plan)
    return roles


def audit(roles, plan):
    require(len(roles) == 144*504, 'role count')
    order = [(s, r+8*g) for s, r in plan['order'] for g in range(2)]
    require(len(set(order)) == 144, 'call order coverage')
    used, helpers, families = defaultdict(set), defaultdict(set), defaultdict(set)
    capacities = {}
    windows = {}
    for key, (capacity, times) in plan['windows'].items():
        replica, child = map(int, key.split(','))
        for group in range(2):
            capacities[replica+8*group, child] = capacity
            windows[replica+8*group, child] = {2*time+g for time in times for g in range(2)}
    widths = plan['provider_registry']['gauge44']['widths']
    for r in roles:
        time, helper = r['time'], r['helper']
        owner, child, port, offset = location(r)
        require(0 <= time < 144 and order[time] == (r['stage'], r['replica']), 'role invocation')
        require(0 <= helper < 504 and r['width'] == widths[helper], 'helper width')
        require(0 <= owner < 16 and 0 <= port < 112, 'owner range')
        require((owner, child) in capacities, 'owner child')
        require(time in windows[owner, child], 'cloned-window screen')
        require(r['copy'] == owner*112+port, 'copy identity')
        expected_family = owner*896+(2*plan['pairs'][str(child)]+plan['sides'][str(child)])*112+port
        require(r['family'] == expected_family, 'family identity')
        require(helper not in helpers[time], 'duplicate helper')
        require(r['family'] not in families[time], 'two helpers in one family')
        helpers[time].add(helper)
        families[time].add(r['family'])
        cells = set(range(offset, offset+r['width']))
        require(offset >= 0 and offset+r['width'] <= capacities[owner, child], 'capacity overflow')
        key = owner, child, port
        require(not cells & used[key], 'overlapping residual footprint')
        used[key].update(cells)
    require(set(helpers) == set(range(144)) and all(h == set(range(504)) for h in helpers.values()), 'complete helper inventory')
    idle = Counter()
    for (replica, child), capacity in capacities.items():
        for port in range(112):
            cells = used[replica, child, port]
            require(cells == set(range(len(cells))), 'non-prefix residual footprint')
            if len(cells) < capacity:
                idle[capacity-len(cells)] += 1
    require(dict(idle) == EXPECTED_IDLE, 'idle profile')
    return dict(sorted(idle.items()))


def controls(roles, plan):
    failures = []
    for time, helper, width, old, new in EDITS:
        mutant = copy.deepcopy(roles)
        role = next(r for r in mutant if (r['time'], r['helper']) == (time, helper))
        move(role, old, plan)
        try:
            audit(mutant, plan)
        except ValueError as error:
            failures.append(dict(time=time, helper=helper, reason=str(error)))
        else:
            raise ValueError('omitted-edit control accepted: %s' % ((time, helper),))
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-plan', type=Path, required=True)
    parser.add_argument('--source-owners', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'output directory already exists')
    require(sha(args.source_plan) == SOURCE_PLAN_SHA256, 'source plan byte pin')
    require(sha(args.source_owners) == SOURCE_OWNERS_SHA256, 'source owners byte pin')
    plan, source = read(args.source_plan), read(args.source_owners)
    roles = construct(source, plan)
    idle = audit(roles, plan)
    rejected = controls(roles, plan)
    baseline = duplicate(source)
    require(sum(a != b for a, b in zip(baseline, roles)) == 11, 'exact edit count')
    raw = canonical(roles)
    compressed = portable_gzip(raw)
    require(gzip.decompress(compressed) == raw and compressed[4:8] == bytes(4) and compressed[9] == 255, 'portable gzip')
    args.out.mkdir(parents=True)
    (args.out/'OWNERS.json.gz').write_bytes(compressed)
    receipt = dict(status='PASS_EXPLICIT_ELEVEN_EDIT_OWNER_CONSTRUCTION',
                   source_plan_sha256=sha(args.source_plan), source_owners_sha256=sha(args.source_owners),
                   owners_sha256=hashlib.sha256(compressed).hexdigest(),
                   owners_content_sha256=hashlib.sha256(raw).hexdigest(),
                   calls=144, helpers_per_call=504, roles=len(roles), changed_roles=11,
                   edits=EDITS, idle_profile=idle, omitted_edit_controls=rejected,
                   exact_idle_delta_from_doubled_source={48: 1, 44: -1, 3: -2, 2: 1},
                   scope='Explicit owner constructor and structural checks. Actual source-event windows, full global geometry and finite invoice are separately required.')
    (args.out/'OWNER-CONSTRUCTION.json').write_bytes((json.dumps(receipt, indent=2)+'\n').encode('utf-8'))
    print(json.dumps({k: v for k, v in receipt.items() if k not in ('edits', 'omitted_edit_controls')}, indent=2))


if __name__ == '__main__':
    main()
