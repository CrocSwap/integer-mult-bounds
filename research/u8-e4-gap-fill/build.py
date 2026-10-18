"""Apply the literal E4 frame and whole-owner edits. No optimizer runs.

Based on BlockInvert's PR664-style promotions, PR799/X4 and PR869/870 U8,
and Jonathan Capalbo's PR942 owners. Prepared with OpenAI Codex assistance.
Apache-2.0; predecessor source and licenses remain in the repository.
"""
import argparse
import copy
from pathlib import Path
from support import P, T37, compressed, dump, identity, read, require, sha, validate_sources


def construct(word, owners):
    edit = read(P / 'LOCAL-EDIT.json')
    require(identity(word) == edit['source_word_identity'], 'Fresh U8 raw source identity')
    result = copy.deepcopy(word)
    for change in edit['entrances']:
        key = str(change['register'])
        require(result['start_extra'][key] == change['before'], 'Entrance edit precondition')
        result['start_extra'][key] = change['after']
    for change in edit['gate_frames']:
        gate = result[change['section']][change['index']]
        require(gate == change['before'], 'Gate edit precondition')
        require(change['before'][:-1] == change['after'][:-1], 'Scalar word must be unchanged')
        result[change['section']][change['index']] = change['after']
    for key, values in edit['report_changes'].items():
        require(result['report'][key] == values['before'], 'Report edit precondition')
        result['report'][key] = values['after']
    require(identity(result) == edit['result_word_identity'], 'Nominated E4 raw identity')
    owner_edits = read(P / 'OWNER-EDITS.json')
    require(identity(owners) == owner_edits['source_owners_identity'], 'T37 owner source identity')
    lookup = {(z['stage'], z['replica'], z['helper']): i for i, z in enumerate(owners)}
    require(len(lookup) == len(owners) == 167832, 'Whole-role source inventory')
    changed = copy.deepcopy(owners)
    keys = set()
    for entry in owner_edits['edits']:
        before, after = entry['before'], entry['after']
        key = tuple(before[k] for k in ('stage', 'replica', 'helper'))
        require(key not in keys, 'Duplicate owner edit')
        keys.add(key)
        require(key == tuple(after[k] for k in ('stage', 'replica', 'helper')), 'Whole-role identity')
        require(changed[lookup[key]] == before, 'Owner edit precondition')
        changed[lookup[key]] = after
    require(len(keys) == 20, 'Complete owner edit inventory')
    require(identity(changed) == owner_edits['result_owners_identity'], 'Frozen owner result')
    return result, changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--u8-word', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    validate_sources()
    require(not args.out.exists(), 'Use a fresh output directory')
    word, owners = construct(read(args.u8_word), read(T37 / 'OWNERS.json.gz'))
    args.out.mkdir(parents=True)
    compressed(args.out / 'WORD.json.gz', word)
    compressed(args.out / 'OWNERS.json.gz', owners)
    dump(args.out / 'CONSTRUCTION.json', dict(
        status='PASS_LITERAL_E4_AND_T37_OWNER_CONSTRUCTION',
        source_word_sha256=sha(args.u8_word), source_word_identity=identity(read(args.u8_word)),
        word_identity=identity(word), owners_identity=identity(owners),
        entrances=4, gate_frames=12, owner_records=20, scalar_gates_changed=0,
        dispatch={'gauge44': 332, 'gauge44_e4': 1}, modified_call=[0, 0]))
    print('PASS_LITERAL_E4_AND_T37_OWNER_CONSTRUCTION')


if __name__ == '__main__':
    main()
