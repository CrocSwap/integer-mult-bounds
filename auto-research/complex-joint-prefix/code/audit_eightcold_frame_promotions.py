#!/usr/bin/env python3
"""Bind all eight cold kernels to PR569's independent frame-only audit.

Prepared with OpenAI Codex assistance. Apache-2.0.
Imports the unchanged check() from PR569 f20a68b4b126780419c292571411022bb1d006d6,
providers/audit_frame_promotions.py, copied as audit_frame_promotions_base.py.
The new adapter binds fresh source/final 38-control receipts by exact gate
locations, and source static44/rank-five controls by their pinned selection.
Every admission check is explicit and remains active under python -O.
"""
import argparse
import copy
from fractions import Fraction
import json
from pathlib import Path

import audit_frame_promotions_base as base

require, read, sha = base.require, base.read, base.sha
PIVOTS = {494, 495, 506, 507, 518, 519, 530, 531}


def kernel_controls(word, recipe):
    """Derive expected omissions independently of stored control receipts."""
    kernels = recipe['kernels']
    require(len(kernels) == 8 and {k['pivot'] for k in kernels} == PIVOTS,
            'Wrong eight-kernel recipe')
    result, all_positions = [], set()
    for kernel in kernels:
        positions = []
        for donor in kernel['gates']:
            q = Fraction(donor['coefficient'])
            event = ['add', donor['donor'], kernel['pivot'], -q.numerator,
                     q.denominator, kernel['frame']]
            hits = [[part, index] for part in ('A', 'B')
                    for index, gate in enumerate(word[part]) if gate == event]
            require(len(hits) == 1, 'Kernel donor gate not uniquely present')
            position = tuple(hits[0])
            require(position not in all_positions, 'Repeated kernel donor gate')
            all_positions.add(position)
            positions.append(hits[0])
        for omitted in [[p] for p in positions] + [positions]:
            result.append(dict(pivot=kernel['pivot'], omitted=omitted,
                               forward_rejected=True, reflected_rejected=True))
    require(len(all_positions) == 30 and len(result) == 38,
            'Wrong donor gate or omission count')
    return result


def bind_cold(control, word, digest, recipe):
    require(control['status'] == 'PASS_EXACT_MULTICUT_KERNEL_OMISSION_CONTROLS',
            'Wrong cold control status')
    require(control['word_sha256'] == digest, 'Stale cold controls')
    require(control['columns_each_orientation'] == 728 and
            control['correct_compensation_frozen'] is True,
            'Incomplete cold scalar scope')
    require(control['controls'] == kernel_controls(word, recipe),
            'Wrong cold omission identities or outcomes')


def bind_scalar(control, digest, selection_digest, pivots, marker):
    require(control['status'] == 'PASS_EXACT_RATIONAL_FORWARD_AND_INVERSE_TRANSPOSE'
            and control['word_sha256'] == digest and
            control['selection_sha256'] == selection_digest,
            'Stale source scalar controls')
    require(control['columns_each_orientation'] == 728 and
            control['kernel_pivots'] == len(pivots) and
            control['controls'] == {str(p): marker for p in pivots},
            'Wrong source scalar omission identities or outcomes')


def expect_rejected(name, callback, rejected):
    try:
        callback()
    except (ValueError, KeyError, TypeError):
        rejected.append(name)
    else:
        raise ValueError('Accepted mutation: ' + name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'word', 'recipes', 'kernel-recipes', 'source-controls',
                 'final-controls', 'selection', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--promotion', type=Path)
    parser.add_argument('--promotions', type=int, choices=(0, 4, 8), required=True)
    args = parser.parse_args()
    source, word = read(args.source), read(args.word)
    recipes, kernels, selection = read(args.recipes), read(args.kernel_recipes), read(args.selection)
    source_digest, word_digest = sha(args.source), sha(args.word)
    changed = base.check(source, word, recipes)
    receipts = {}
    cold_values = []
    for label, folder, value, digest in (
            ('source', args.source_controls, source, source_digest),
            ('final', args.final_controls, word, word_digest)):
        path = folder / 'ALL-COLD-CONTROLS.json'
        control = read(path)
        bind_cold(control, value, digest, kernels)
        cold_values.append(control)
        receipts[label + '/' + path.name] = sha(path)
    require(cold_values[0]['compensation_entries'] == cold_values[1]['compensation_entries'],
            'Changed scalar compensation count')
    static_pivots = [p for entry in selection['kernel'] for p in entry['pivots']]
    require(len(static_pivots) == len(set(static_pivots)) == 44, 'Wrong static selection')
    path = args.source_controls / 'STATIC44-SCALAR-AUDIT.json'
    static = read(path)
    bind_scalar(static, source_digest, sha(args.selection), static_pivots,
                'REJECTED_OMITTED_KERNEL_CORRECTION')
    require(static['compensations'] == cold_values[0]['compensation_entries'],
            'Inconsistent compensation count')
    receipts['source/' + path.name] = sha(path)
    if args.promotions:
        require(args.promotion is not None, 'Missing rank-five promotion record')
        promotion_pivots = [p for change in read(args.promotion)['changes'] for p in change['pivots']]
        require(len(promotion_pivots) == len(set(promotion_pivots)) == args.promotions,
                'Wrong rank-five promotion record')
        path = args.source_controls / 'PROMOTED-SCALAR-AUDIT.json'
        promoted = read(path)
        bind_scalar(promoted, source_digest, sha(args.selection), promotion_pivots,
                    'REJECTED_OMITTED_PROMOTED_POSTCENTER_KERNEL_CORRECTION')
        require(promoted['compensations'] == static['compensations'] and
                promoted['program_operations'] == static['program_operations'],
                'Inconsistent source scalar program')
        receipts['source/' + path.name] = sha(path)
    else:
        require(args.promotion is None, 'Unexpected rank-five promotion record')
    rejected = []
    for name in ('scalar_coefficient', 'entrance_outside_recipe', 'cleanup_order'):
        mutant = copy.deepcopy(word)
        if name == 'scalar_coefficient':
            next(event for event in mutant['B'] if event[0] == 'add')[3] += 1
        elif name == 'entrance_outside_recipe':
            mutant['start_extra']['224'] = [1]
        else:
            mutant['cleanup'].reverse()
        expect_rejected(name, lambda: base.check(source, mutant, recipes), rejected)
    for name in ('stale_word_hash', 'missing_omission', 'duplicate_omission',
                 'wrong_omitted_gate', 'accepted_orientation', 'unfrozen_compensation'):
        mutant = copy.deepcopy(cold_values[1])
        if name == 'stale_word_hash':
            mutant['word_sha256'] = '0' * 64
        elif name == 'missing_omission':
            mutant['controls'].pop()
        elif name == 'duplicate_omission':
            mutant['controls'][-1] = copy.deepcopy(mutant['controls'][0])
        elif name == 'wrong_omitted_gate':
            mutant['controls'][0]['omitted'][0][1] += 1
        elif name == 'accepted_orientation':
            mutant['controls'][0]['reflected_rejected'] = False
        else:
            mutant['correct_compensation_frozen'] = False
        expect_rejected(name, lambda: bind_cold(mutant, word, word_digest, kernels), rejected)
    result = dict(
        status='PASS_EIGHT_COLD_FRAME_PROMOTION_SCALAR_TRANSFER',
        source_sha256=source_digest, word_sha256=word_digest,
        recipes_sha256=sha(args.recipes), kernel_recipes_sha256=sha(args.kernel_recipes),
        selection_sha256=sha(args.selection),
        promotion_sha256=sha(args.promotion) if args.promotion else None,
        original_check_sha256=sha(Path(base.__file__)), auditor_sha256=sha(Path(__file__)),
        changed_frames=changed, promotions=32, rank_five_promotions=args.promotions,
        all_scalar_operations_identical=True, source_cold_omissions=38, final_cold_omissions=38,
        source_static_omissions=44, source_rank_five_omissions=args.promotions,
        omission_receipts=receipts, negative_controls_rejected=rejected,
        scope='Unchanged PR569 independent check establishes exact scalar operation/coefficient/order '
              'identity and the prescribed 32 entrances with 96 frame changes. Fresh source scalar '
              'omissions transfer through that equality; all 38 final cold omissions are also replayed '
              'directly. Native geometry, actual profiles, wrappers, full phases, global hosting and '
              'moment admission remain separate fresh checks.')
    args.out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(result['status'], 'negative controls:', len(rejected))


if __name__ == '__main__':
    main()
