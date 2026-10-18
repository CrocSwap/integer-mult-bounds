"""Separate event/owner/chart recount for the one-call mixed construction.

Uses Hao Yan's PR858/PR890 checker with the explicit adaptations below.
It imports neither the owner constructor nor the emitted-controller auditor.
The independent path means a separate computation, not independent human review.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import copy
from collections import Counter
from pathlib import Path
from support import P, T21, T37, dump, identity, load, read, require, sha

CHANGES = [
    ("require(Counter(widths) == {4: 80, 5: 32, 7: 54, 8: 122, 9: 216}, 'current supplier width inventory')",
     "require(len(widths) == R and all(1 <= w <= H for w in widths), 'derived whole-helper widths')"),
    ("width == c['widths'][helper]", "width == c['per_call_widths'][call][helper]"),
    ("profile = Counter({rank: 9 * T * count for rank, count in c['paid'].items()})",
     "profile = Counter()\n    for call in c['order']:\n        profile.update(c['per_call_paid'][call])"),
    ("localbits = max(x['prefix_bits_upper'] for x in c['replay']['local'].values())",
     "localbits = max(x['prefix_bits_upper'] for replay in c['replays'].values() for x in replay['local'].values())"),
    ('2 * 512', '2 * 1024'), ('prefix < 512', 'prefix < 1024'),
    ('charged_prefix_bits=512', 'charged_prefix_bits=1024'), ('1 <= T <= 22', '1 <= T <= 50')]


def adapted_text():
    text = (T21 / 'independent_check.py').read_text()
    for before, after in CHANGES:
        require(text.count(before) == 1, 'Independent adaptation anchor: ' + before)
        text = text.replace(before, after)
    return text


def reject(checker, context, roles, label):
    try:
        checker.check_roles(context, roles)
    except ValueError as error:
        return dict(name=label, reason=str(error))
    raise ValueError('Invalid construction accepted: ' + label)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--baseline942', type=Path, required=True)
    args = parser.parse_args()
    work, baseline = args.work, args.baseline942
    adapter = work / 'independent_mixed_adapter.py'
    adapter.write_text(adapted_text(), encoding='utf-8')
    checker = load(adapter, 'independent_e4_owner_checker')
    checker.T, checker.EXPECTED_IDLE = 37, {1: 2, 48: 11086}
    base = baseline / 'baseline799/global/global/base'
    parent_path = base / 'split-centres/GLOBAL-TEMPLATE.json.gz'
    canonical_path = base / 'split-centres/CANONICAL-WORD.json.gz'
    phases_path = base / 'work/complex-nine-native/DATA-PHASES.json'
    roles_path = work / 'construction/OWNERS.json.gz'
    roles = read(roles_path)
    parent, phases, canonical = map(read, (parent_path, phases_path, canonical_path))
    words, replays, widths, paid, inputs = {}, {}, {}, {}, [parent_path, canonical_path, phases_path, roles_path]
    expected_widths = {'gauge44': {4: 80, 5: 32, 7: 54, 8: 122, 9: 216},
                       'gauge44_e4': {4: 76, 5: 36, 7: 54, 8: 122, 9: 216}}
    for pid, directory in [('gauge44', baseline / 'native/local'), ('gauge44_e4', work / 'native/local')]:
        word_path, replay_path = directory / 'CANONICAL-WORD.json.gz', directory / 'INDEPENDENT-LOCAL-REPLAY.json'
        inputs += [word_path, replay_path]
        word, replay = read(word_path), read(replay_path)
        require(replay['status'] == 'PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY', 'Native replay status')
        require(replay['canonical_word_sha256'] == sha(word_path), 'Native word binding')
        require(set(replay['local']) == {'forward', 'backward'}, 'Both native orientations')
        require(word['ports'] == canonical['ports'], 'Port interface')
        require(len(word['center_frames']) == len(canonical['center_frames']) == 8, 'Centre count')
        require([checker.basis(word['frames'][f]) for f in word['center_frames']] ==
                [checker.basis(canonical['frames'][f]) for f in canonical['center_frames']], 'Ordered centre interface')
        words[pid], replays[pid] = word, replay
        widths[pid], paid[pid] = checker.local_inventory(word, replay)
        require(Counter(widths[pid]) == expected_widths[pid], 'Nominated provider width inventory')
    difference = {i: [a, b] for i, (a, b) in enumerate(zip(widths['gauge44'], widths['gauge44_e4'])) if a != b}
    require(difference == {i: [4, 5] for i in (411, 413, 414, 415)}, 'Only four width changes')
    context = checker.make_context(parent, phases, canonical['ports'], words['gauge44'], replays['gauge44'], roles)
    dispatch = {call: 'gauge44_e4' if call == (0, 0) else 'gauge44' for call in context['order']}
    context.update(per_call_widths={c: widths[p] for c, p in dispatch.items()},
                   per_call_paid={c: paid[p] for c, p in dispatch.items()}, replays=replays)
    receipt = checker.check_roles(context, roles)
    receipt['status'] = 'PASS_INDEPENDENT_MIXED_E4_T37_WINDOWS_CHARTS_PREFIX_ROW'
    receipt['local_profile'] = {p: dict(sorted(v.items())) for p, v in paid.items()}
    receipt['width_inventory'] = {p: dict(sorted(Counter(v).items())) for p, v in widths.items()}
    receipt['provider_counts'] = dict(Counter(dispatch.values()))
    receipt['controls_rejected'] = checker.controls(context, roles)
    incorrect = dict(context, per_call_widths={c: widths['gauge44'] for c in dispatch})
    receipt['controls_rejected'].append(reject(checker, incorrect, roles, 'discard_modified_provider'))
    original = read(T37 / 'OWNERS.json.gz')
    receipt['controls_rejected'].append(reject(checker, context, original, 'discard_all_owner_edits'))
    index = {(z['stage'], z['replica'], z['helper']): i for i, z in enumerate(roles)}
    omitted = []
    for number, change in enumerate(read(P / 'OWNER-EDITS.json')['edits']):
        key = tuple(change['before'][k] for k in ('stage', 'replica', 'helper'))
        broken = roles.copy()
        broken[index[key]] = change['before']
        omitted.append(reject(checker, context, broken, 'omit_owner_edit_' + str(number)))
    receipt['omitted_edits_rejected'] = omitted
    claim = read(P / 'CLAIM.json')
    for key in ('profile', 'idle'):
        require({str(k): v for k, v in receipt[key].items()} == claim[key], 'Independent claim ' + key)
    for key in ('roles', 'calls', 'live', 'physical', 'rank_mass', 'deficit', 'prefix_bits',
                'charged_prefix_bits', 'physical_row_coefficient'):
        require(receipt[key] == claim[key], 'Independent claim ' + key)
    receipt['input_sha256'] = {str(p.resolve()): sha(p) for p in inputs}
    receipt['checker_adaptation'] = dict(source_sha256=sha(T21 / 'independent_check.py'),
                                        adapter_sha256=sha(adapter), changes=CHANGES)
    receipt['owners_identity'] = identity(roles)
    dump(work / 'INDEPENDENT-OWNERS.json', receipt)
    print(receipt['status'], receipt['prefix_bits'], receipt['physical_row_coefficient'])


if __name__ == '__main__':
    main()
