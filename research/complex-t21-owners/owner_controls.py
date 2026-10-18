# SPDX-License-Identifier: Apache-2.0
"""Reject every omitted T21 edit and an omitted interleaving delay."""
import argparse
import copy
from pathlib import Path
from common import HERE, ROOT, read, require, dump, load
from build_owners import move


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--local', type=Path, required=True)
    parser.add_argument('--owners', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    audit = load(HERE/'independent_check.py', 'independent_t21_controls')
    audit.T, audit.EXPECTED_IDLE = 21, {48: 6292, 3: 1, 1: 3}
    parent = read(args.base/'split-centres/GLOBAL-TEMPLATE.json.gz')
    phases = read(args.base/'work/complex-nine-native/DATA-PHASES.json')
    ports = read(args.base/'split-centres/CANONICAL-WORD.json.gz')['ports']
    word = read(args.local/'CANONICAL-WORD.json.gz')
    replay = read(args.local/'INDEPENDENT-LOCAL-REPLAY.json')
    roles = read(args.owners)
    context = audit.make_context(parent, phases, ports, word, replay, roles)
    audit.check_roles(context, roles)
    plan = read(ROOT/'research/gauge44-frames-x/data/PLAN.json')
    rejected = []
    for edit in read(HERE/'data/EDITS.json'):
        bad = copy.deepcopy(roles)
        role = next(r for r in bad if [r['time'], r['helper']] == edit['role'])
        move(role, edit['before'], plan)
        try:
            audit.check_roles(context, bad)
        except ValueError as error:
            rejected.append(dict(role=edit['role'], reason=str(error)))
        else:
            raise ValueError('Accepted omitted T21 edit: '+str(edit['role']))
    require(len(rejected) == 9, 'Nine omitted-edit rejections')
    # A complete, individually ordered schedule with the four-call delay
    # removed. Rebuild its actual event windows before testing the owner map.
    old_order = [(s, r+8*g) for s, r in plan['order'] for g in range(3) if r+8*g < 21]
    at = {key: time for time, key in enumerate(old_order)}
    bad = copy.deepcopy(roles)
    for role in bad:
        role['time'] = at[role['stage'], role['replica']]
    other = audit.make_context(parent, phases, ports, word, replay, bad)
    try:
        audit.check_roles(other, bad)
    except ValueError as error:
        delay_reason = str(error)
    else:
        raise ValueError('Accepted missing four-call delay')
    dump(args.out, dict(status='PASS_NINE_T21_OMITTED_EDITS_AND_DELAY_CONTROL',
                       omitted_edit_controls=rejected, omitted_delay_rejection=delay_reason))
    print('PASS nine omitted edits and delay control')


if __name__ == '__main__':
    main()
