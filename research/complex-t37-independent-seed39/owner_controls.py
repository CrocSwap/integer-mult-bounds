# SPDX-License-Identifier: Apache-2.0
# Prepared by Tekalign (@tekuuu) with substantial OpenAI Codex assistance.
"""Independently reject omitted T37/T21/T16 edits and both missing delays.

Source maps are reconstructed from pinned predecessor code. Each source is
first accepted using independently expanded events, actual windows, charts
and its original 512-bit payload. T37 uses its explicit order and the paid
1024-bit payload. Geometry controls must fail before profile comparison.
"""
import argparse
from pathlib import Path
from common import HERE, ROOT, read, require, dump, load, identity, sha
from build_owners import source_maps, merged_order, move

GEOMETRY_REJECTIONS = {
    'strict bridge-aware idle window',
    'duplicate helper or family within whole invocation',
    'overlapping or out-of-capacity slice',
    'gap in pending prefix',
}


def omitted_edits(audit, context, roles, edits, plan):
    bykey = {(r['stage'], r['replica'], r['helper']): i for i, r in enumerate(roles)}
    rejected = []
    for edit in edits:
        index = bykey[tuple(edit['role'])]
        replacement = dict(roles[index])
        move(replacement, edit['before'], plan)
        bad = roles.copy()
        bad[index] = replacement
        try:
            audit.check_roles(context, bad)
        except ValueError as error:
            reason = str(error)
            require(reason in GEOMETRY_REJECTIONS,
                    'Omitted edit rejected without a geometric obstruction: '+reason)
            rejected.append(dict(role=edit['role'], reason=reason))
        else:
            raise ValueError('Accepted omitted edit: '+str(edit['role']))
    return rejected


def omitted_delay(audit, inputs, roles, order, payload):
    at = {tuple(key): time for time, key in enumerate(order)}
    bad = [dict(role, time=at[role['stage'], role['replica']]) for role in roles]
    # Recompute event windows from the alternative schedule, rather than
    # retaining good-schedule windows or rejecting on a stale time field.
    other = audit.make_context(*inputs, bad, order=order, payload=payload)
    try:
        audit.check_roles(other, bad)
    except ValueError as error:
        require(str(error) == 'strict bridge-aware idle window', 'Delay control must cross an actual idle boundary')
        return str(error)
    raise ValueError('Accepted omitted interleaving delay')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--local', type=Path, required=True)
    parser.add_argument('--owners', type=Path, required=True)
    parser.add_argument('--order', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    audit = load(HERE/'independent_check.py', 'independent_t37_owner_controls')
    parent = read(args.base/'split-centres/GLOBAL-TEMPLATE.json.gz')
    phases = read(args.base/'work/complex-nine-native/DATA-PHASES.json')
    ports = read(args.base/'split-centres/CANONICAL-WORD.json.gz')['ports']
    word = read(args.local/'CANONICAL-WORD.json.gz')
    replay = read(args.local/'INDEPENDENT-LOCAL-REPLAY.json')
    inputs = parent, phases, ports, word, replay
    source = ROOT/'research/gauge44-frames-x/data'
    plan, roles21, order21, roles16, order16, details21 = source_maps(source/'PLAN.json', source/'OWNERS.json.gz')
    roles = read(args.owners)
    order_path = args.order or args.owners.with_name('ORDER.json')
    order = read(order_path)
    # This assertion does not use the constructor's suborder-check function.
    require([key for key in order if key[1] < 21] == order21 and
            [[s, r-21] for s, r in order if r >= 21] == order16,
            'Independent complete source-subsequence preservation')
    audit.T, audit.EXPECTED_IDLE = 37, {48: 11086, 1: 6}
    context = audit.make_context(*inputs, roles, order=order, payload=1024)
    result37 = audit.check_roles(context, roles)
    try:
        audit.check_roles(dict(context, payload=512), roles)
    except ValueError as error:
        require(str(error) == 'prefix reserve', 'Underpaid payload must fail the prefix bound')
        payload_rejection = str(error)
    else:
        raise ValueError('Accepted T37 with the old 512-bit payload')
    edits37 = read(HERE/'data/EDITS.json')
    rejected37 = omitted_edits(audit, context, roles, edits37, plan)
    require(len(rejected37) == 10, 'Ten T37 omitted-edit rejections')
    delay37 = omitted_delay(audit, inputs, roles, merged_order(order21, order16, shift=0), 1024)

    audit.T, audit.EXPECTED_IDLE = 21, {48: 6292, 3: 1, 1: 3}
    context21 = audit.make_context(*inputs, roles21, order=order21, payload=512)
    result21 = audit.check_roles(context21, roles21)
    edits21 = []
    for old in read(HERE/'vendor/pr890/data/EDITS.json'):
        time, helper = old['role']
        edits21.append(dict(role=[*order21[time], helper], before=old['before']))
    rejected21 = omitted_edits(audit, context21, roles21, edits21, plan)
    require(len(rejected21) == 9, 'Nine inherited T21 omitted-edit rejections')
    old_order21 = [[s, r+8*g] for s, r in plan['order'] for g in range(3) if r+8*g < 21]
    delay21 = omitted_delay(audit, inputs, roles21, old_order21, 512)

    audit.T, audit.EXPECTED_IDLE = 16, {48: 4793, 44: 1, 2: 1, 1: 2}
    context16 = audit.make_context(*inputs, roles16, order=order16, payload=512)
    result16 = audit.check_roles(context16, roles16)
    builder16 = load(HERE/'vendor/pr870/t16/build_owners.py', 'pinned_t16_control_edits')
    fields = ('owner_replica', 'child', 'port', 'offset')
    edits16 = [dict(role=[*order16[time], helper], before=dict(zip(fields, old)))
               for time, helper, width, old, new in builder16.EDITS]
    rejected16 = omitted_edits(audit, context16, roles16, edits16, plan)
    require(len(rejected16) == 11, 'Eleven inherited T16 omitted-edit rejections')
    dump(args.out, dict(
        status='PASS_T37_T21_T16_OMITTED_EDITS_AND_DELAYS',
        owners_sha256=sha(args.owners), owners_content_sha256=identity(roles),
        order_sha256=sha(order_path), order_content_sha256=identity(order),
        source_suborders_preserved=True, source_suborders_checked_independently=True,
        omitted_edit_controls=rejected37, omitted_delay_rejection=delay37,
        underpaid_payload_rejection=payload_rejection,
        t37_independent_acceptance=result37,
        inherited_t21=dict(owners_content_sha256=identity(roles21), order_content_sha256=identity(order21),
                           independent_acceptance=result21, omitted_edit_controls=rejected21,
                           omitted_delay_rejection=delay21),
        inherited_t16=dict(owners_content_sha256=identity(roles16), order_content_sha256=identity(order16),
                           independent_acceptance=result16, omitted_edit_controls=rejected16),
        source_plan_sha256=sha(source/'PLAN.json'), source_owners_sha256=sha(source/'OWNERS.json.gz'),
        scope='All 30 omitted edits fail actual geometry; both missing delays cross independently rebuilt idle boundaries. Source checks use original payload512; final T37 uses paid payload1024.'))
    print('PASS 10 T37 + 9 T21 + 11 T16 omitted edits and both actual-window delay controls')


if __name__ == '__main__':
    main()
