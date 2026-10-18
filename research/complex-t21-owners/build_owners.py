# SPDX-License-Identifier: Apache-2.0
"""Build T16 plus a literal T5 map, delay its calls, apply nine whole-role edits.

Hao Yan's PR858 T16 constructor is reused unchanged through PR870's vendored
copy. T5 is a frozen finite assignment, not a solver dependency. All roles and
windows are independently checked by independent_check.py after construction.
"""
import argparse
import copy
from pathlib import Path
from common import HERE, ROOT, read, require, sha, identity, dump, write_gzip, load


def merged_order(source):
    initial = [(s, r+8*g) for s, r in source['order'] for g in range(3) if r+8*g < 21]
    decorated, count16 = [], 0
    for stage, replica in initial:
        if replica < 16:
            decorated.append((2*count16, 0, stage, replica))
            count16 += 1
        else:
            decorated.append((2*(count16+4)-1, 1, stage, replica))
    return [[s, r] for _, _, s, r in sorted(decorated)]


def location(role):
    return {k: role[k] for k in ('owner_replica', 'child', 'port', 'offset')}


def move(role, destination, plan):
    role.update(destination)
    r, child, port = (role[k] for k in ('owner_replica', 'child', 'port'))
    role['copy'] = r*112+port
    role['family'] = r*896+(2*plan['pairs'][str(child)]+plan['sides'][str(child)])*112+port


def construct(source_plan, source_owners):
    builder = load(HERE/'vendor/pr870/t16/build_owners.py', 'unchanged_t16_owners')
    require(sha(source_plan) == builder.SOURCE_PLAN_SHA256 and
            sha(source_owners) == builder.SOURCE_OWNERS_SHA256, 'PR799 T8 source pins')
    plan, source = read(source_plan), read(source_owners)
    t16 = builder.construct(source, plan)
    require(builder.audit(t16, plan) == {1: 2, 2: 1, 44: 1, 48: 4793}, 'Inherited T16 audit')
    t16_controls = builder.controls(t16, plan)
    require(len(t16_controls) == 11, 'Inherited T16 omitted-edit controls')
    t5 = read(HERE/'data/T5-OWNERS.json.gz')
    require(len(t5) == 45*504, 'T5 literal role inventory')
    roles = copy.deepcopy(t16)
    for old in t5:
        role = dict(old)
        for key in ('replica', 'owner_replica'):
            role[key] += 16
        role['copy'] += 16*112
        role['family'] += 16*896
        roles.append(role)
    order = merged_order(plan)
    at = {tuple(key): time for time, key in enumerate(order)}
    require(len(at) == 189, 'T21 complete invocation inventory')
    for role in roles:
        role['time'] = at[role['stage'], role['replica']]
    roles.sort(key=lambda r: (r['time'], r['helper']))
    before = copy.deepcopy(roles)
    bykey = {(r['time'], r['helper']): r for r in roles}
    require(len(bykey) == 189*504, 'Joined role identities')
    edits = read(HERE/'data/EDITS.json')
    require(len(edits) == 9, 'Nine explicit edits')
    for edit in edits:
        role = bykey[tuple(edit['role'])]
        require(location(role) == edit['before'], 'Frozen edit source location')
        move(role, edit['after'], plan)
    require(sum(a != b for a, b in zip(before, roles)) == 9, 'Exactly nine changed roles')
    return roles, order, dict(t16_omitted_edit_controls=t16_controls,
                              t16_content_sha256=identity(t16),
                              t5_content_sha256=identity(t5), changed_roles=9)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Owner output must be new')
    source = ROOT/'research/gauge44-frames-x/data'
    roles, order, details = construct(source/'PLAN.json', source/'OWNERS.json.gz')
    args.out.mkdir(parents=True)
    write_gzip(args.out/'OWNERS.json.gz', roles)
    dump(args.out/'ORDER.json', order)
    dump(args.out/'OWNER-CONSTRUCTION.json', dict(
        status='PASS_LITERAL_T16_PLUS_T5_NINE_ROLE_CONSTRUCTION', roles=len(roles),
        owners_sha256=sha(args.out/'OWNERS.json.gz'), owners_content_sha256=identity(roles), **details))


if __name__ == '__main__':
    main()
