# SPDX-License-Identifier: Apache-2.0
# Prepared by Tekalign (@tekuuu) with substantial OpenAI Codex assistance.
"""Compose pinned T21 and T16 maps and apply a literal ten-role remainder trade.

Chafik Boukhalfa's PR890 T21 and Hao Yan's PR858 T16 constructors are vendored
unchanged. Their complete call subsequences are preserved. Six roles change
owner bins and four more change prefix offsets. No solver is used. Actual
source-event windows and all role charts are checked independently afterwards.
"""
import argparse
import copy
import sys
from pathlib import Path
from common import HERE, ROOT, read, require, sha, identity, dump, write_gzip, load

T21 = HERE/'vendor/pr890'
EXPECTED_CONTENT = '41234f89e8afb1a4cd9adc7d7a46e8d5118b5b4cbd77de711c8cb3b90463260c'


def t21_builder():
    # PR890 uses an absolute `from common import ...`. Give the immutable
    # source its own immutable common module while it is imported, then
    # restore this package's import binding. No vendor source is rewritten.
    previous = sys.modules.get('common')
    sys.modules['common'] = load(T21/'common.py', 'pinned_pr890_common')
    try:
        return load(T21/'build_owners.py', 'pinned_pr890_t21_owners')
    finally:
        if previous is None:
            del sys.modules['common']
        else:
            sys.modules['common'] = previous


def source_maps(source_plan, source_owners):
    pins = read(HERE/'VENDOR-PINS.json')
    for label, paths in [('pr890', pins['pr890']['files']),
                         ('pr870', {'t16/build_owners.py': pins['pr870']['files']['t16/build_owners.py']})]:
        for relative, expected in paths.items():
            require(sha(HERE/'vendor'/label/relative) == expected, 'Pinned owner source: '+relative)
    builder16 = load(HERE/'vendor/pr870/t16/build_owners.py', 'pinned_t16_owners')
    require(sha(source_plan) == builder16.SOURCE_PLAN_SHA256 and
            sha(source_owners) == builder16.SOURCE_OWNERS_SHA256, 'PR799 T8 source pins')
    plan, source = read(source_plan), read(source_owners)
    roles21, order21, details21 = t21_builder().construct(source_plan, source_owners)
    roles16 = builder16.construct(source, plan)
    require(builder16.audit(roles16, plan) == {1: 2, 2: 1, 44: 1, 48: 4793}, 'Inherited T16 audit')
    order16 = [[s, r+8*g] for s, r in plan['order'] for g in range(2)]
    require(identity(roles16) == details21['t16_content_sha256'], 'Same pinned T16 in both groups')
    return plan, roles21, order21, roles16, order16, details21


def merged_order(order21, order16, shift=-528):
    decorated = [(16*i, 0, s, r) for i, (s, r) in enumerate(order21)]
    decorated += [(21*j+shift, 1, s, r+21) for j, (s, r) in enumerate(order16)]
    return [[s, r] for _, _, s, r in sorted(decorated)]


def check_source_suborders(order, order21, order16):
    require([key for key in order if key[1] < 21] == order21, 'Complete T21 source suborder')
    require([[s, r-21] for s, r in order if r >= 21] == order16, 'Complete T16 source suborder')
    require(len(order) == 333 and set(map(tuple, order)) ==
            {(s, r) for s in range(9) for r in range(37)}, 'T37 complete invocation inventory')


def location(role):
    return {k: role[k] for k in ('owner_replica', 'child', 'port', 'offset')}


def move(role, destination, plan):
    role.update(destination)
    r, child, port = (role[k] for k in ('owner_replica', 'child', 'port'))
    role['copy'] = r*112+port
    role['family'] = r*896+(2*plan['pairs'][str(child)]+plan['sides'][str(child)])*112+port


def construct(source_plan, source_owners):
    plan, roles21, order21, roles16, order16, details21 = source_maps(source_plan, source_owners)
    roles = copy.deepcopy(roles21)
    for old in roles16:
        role = dict(old)
        for key in ('replica', 'owner_replica'):
            role[key] += 21
        role['copy'] += 21*112
        role['family'] += 21*896
        roles.append(role)
    order = merged_order(order21, order16)
    check_source_suborders(order, order21, order16)
    at = {tuple(key): time for time, key in enumerate(order)}
    for role in roles:
        role['time'] = at[role['stage'], role['replica']]
    roles.sort(key=lambda r: (r['time'], r['helper']))
    before = copy.deepcopy(roles)
    bykey = {(r['stage'], r['replica'], r['helper']): r for r in roles}
    require(len(bykey) == 333*504, 'Joined role identities')
    edits = read(HERE/'data/EDITS.json')
    require(len(edits) == 10 and len({tuple(e['role']) for e in edits}) == 10, 'Ten distinct literal edits')
    for edit in edits:
        role = bykey[tuple(edit['role'])]
        require(role['time'] == edit['time'] and role['width'] == edit['width'] and
                location(role) == edit['before'], 'Frozen edit source location, width and time')
        move(role, edit['after'], plan)
    changed = sum(location(a) != location(b) for a, b in zip(before, roles))
    relocated = sum(any(a[k] != b[k] for k in ('owner_replica', 'child', 'port'))
                    for a, b in zip(before, roles))
    require(changed == 10 and relocated == 6, 'Exactly ten edits and six bin relocations')
    require(identity(roles) == EXPECTED_CONTENT, 'Frozen T37 owner content')
    return roles, order, dict(
        source_plan_sha256=sha(source_plan), source_owners_sha256=sha(source_owners),
        t21_content_sha256=identity(roles21), t16_content_sha256=identity(roles16),
        t21_order_content_sha256=identity(order21), t16_order_content_sha256=identity(order16),
        t16_omitted_edit_controls=details21['t16_omitted_edit_controls'],
        t21_constructor_details=details21, changed_roles=changed, relocated_roles=relocated,
        interleave=dict(t21_key='16*i', t16_key='21*j-528', tie='T21 first'),
        both_source_suborders_preserved=True)


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
        status='PASS_LITERAL_T21_PLUS_T16_TEN_ROLE_CONSTRUCTION', roles=len(roles),
        calls=len(order), owners_sha256=sha(args.out/'OWNERS.json.gz'),
        owners_content_sha256=identity(roles), order_content_sha256=identity(order), **details))
    print('PASS literal T21 plus T16 construction: 167832 roles, 10 edits, 6 relocations')


if __name__ == '__main__':
    main()
