#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay eight additional GF(2) births using the submitted #7781 calibration.

The pinned #7781 package supplies the calibration and predecessor word.
Ali Romman's #7776 and the #7000/#7001 BIT lineage supply the retained
native tape, physical verifier and paired caller.
"""

import argparse
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys


PARENT_HEAD = '913fb6febe28cc3ccad1c16de8e45b8bce0da063'
PARENT_SHA = '861f5181e4f34db638ab0c573c319fe26ff034d63b21242d67220a4a5d6433ff'
PARENT_GZIP = 'a63f07a5f5ac4aa28b5b635c7836f36efafd03b735ab13f24c8b481d137d54e8'
PARENT_REPLAY = '56a0c8737f93926ed0e86ea5618cbf6397441e72bba99dd1c10fb6cc15be446e'
JOURNAL_SHA = '7fa07209cee23b15d9bbd178bab4bed7bb01b7ce2da743744e6ddbd9d3f5920c'
WORD_SHA = '0cfae4f0a7a47628f7ce45b5c11bcacbb2957592f5be511230434d7b7e8f0d37'
TARGET = '0.00387981257853'
PRICE = Path('research/paired-query-only-bit/independent/interval_gate.py')
PRICE_SHA = '8dc2bc4c64cba3f83c664373984a075f1a14b4d53958084091345c8cab189dec'


def check_bytes(path, expected):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != expected:
        raise ValueError(f'SHA-256 pin for {path}')
    return raw


def load_parent(path):
    raw = check_bytes(path, PARENT_REPLAY)
    scope = {'__file__': str(path), '__name__': 'pinned_p7781_replay'}
    from types import ModuleType

    module = ModuleType(scope['__name__'])
    module.__dict__.update(scope)
    sys.modules[module.__name__] = module
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def recount(word, caller, app, audit):
    native_paid, native_targets, native = audit.source_audit(word)
    app.reverse(word)
    targets, paid, positions = app.frames_and_sites(word, caller, native, audit)
    return paid, targets, positions, native_paid, native_targets, native


def rebuild(root, parent_word, parent_replay, journal_path):
    replay = load_parent(parent_replay)
    for path, digest in replay.SOURCE_PINS.items():
        check_bytes(root / path, digest)
    check_bytes(root / PRICE, PRICE_SHA)
    edge = replay.module(root / replay.ALI / 'bit_native.py', 'bit_native')
    app = replay.module(root / replay.ALI / 'bit_application.py', 'additional_birth_app')
    audit = replay.module(root / replay.PAIRED / 'retained/audit_binary_mixed.py', 'additional_birth_audit')
    paired = replay.module(root / replay.PAIRED / 'check.py', 'additional_birth_caller')
    iv = replay.module(root / PRICE, 'additional_birth_price')
    need = replay.need
    parent = json.loads(gzip.decompress(check_bytes(parent_word, PARENT_GZIP)))
    journal = json.loads(check_bytes(journal_path, JOURNAL_SHA))
    need(edge.digest(parent) == PARENT_SHA == journal['source_word_sha256']
         and (journal['source_pr'], journal['source_head']) == (7781, PARENT_HEAD), 'exact #7781 source')
    initial, final, moves, rows, clocks = edge.extract(parent)
    need((len(initial), len(moves), len(parent['frames'])) == (672, 2876, 636), 'literal parent inventory')
    base = replay.Network(initial, final, moves, rows)
    base.validate(edge, False)
    graph = base.transpose()
    steps = journal['steps']
    need(len(steps) == 8, 'eight new helpers')
    for step in steps:
        need(clocks[step['source_packet']] == step['baseline_source_move_clock'], 'literal parent MOVE clock')
        graph, fresh = replay.apply_birth(graph, step, parent['frames'], edge, audit)
        need(fresh == step['added_owner'], 'literal fresh public owner')
    forward = graph.transpose()
    order, _, _ = forward.validate(edge, False)
    need((len(forward.initial), len(order)) == (680, 2884)
         and sorted(forward.initial) == journal['public_owner_order'], 'all public owners and charged packets')
    changed = {step['witness']['role'] for step in steps}
    need(all((forward.initial[h], forward.final[h]) == (initial[h], final[h])
             for h in set(initial) - changed), 'unchanged endpoints of all other owners')
    word = edge.emit_word(parent, forward.initial, forward.final, forward.moves, forward.rows, order)
    need(edge.digest(word) == journal['word_sha256'] == WORD_SHA, 'canonical emitted program')

    caller = app.read_pinned(root, replay.PAIRED / 'EFREE-CALLER.json.gz', app.CALLER_SHA)
    paid, targets, positions, native_paid, native_targets, native = recount(word, caller, app, audit)
    base_paid, base_targets, base_positions, *_ = recount(parent, caller, app, audit)
    need(positions['native_calls'] == base_positions['native_calls'] == 36
         and positions['rank_surplus'] == base_positions['rank_surplus'] == 1506, 'complete 36-call invoice')
    for field, base_profile, actual in [('paid', base_paid, paid), ('target', base_targets, targets)]:
        predicted = base_profile.copy()
        for step in steps:
            daughters = step[f'{field}_daughter_ranks']
            predicted[sum(daughters)] -= 36
            for rank in daughters:
                predicted[rank] += 36
        need(+predicted == actual, f'complete {field} histogram matches the exact daughter grades')
    coefficients = paired.forward(caller)
    need(coefficients == audit.backward(caller) == 38**2, 'every paired caller coefficient in both directions')
    ordinary = app.ordinary(word, caller, targets, paid)

    corrupted, clock, label = replay.zero_paid_packet(word, order.index(steps[0]['new_packet']))
    controls = {
        'zero_first_new_paid': {
            'clock': clock, 'bank': label, 'removed_adds': len(word['program']) - len(corrupted['program']),
            'forward_rejection': replay.rejection(lambda: audit.source_audit(corrupted),
                                                  'all-column native scalar endpoint'),
            'adjoint_rejection': replay.rejection(lambda: app.reverse(corrupted),
                                                  'independent emitted-word full transpose'),
        },
        'omit_last_clear': replay.rejection(
            lambda: audit.source_audit(word | {'program': word['program'][:-1]}),
            'all endpoints and owned lifetimes'),
    }
    trial = Fraction(TARGET)
    before = iv.sub(iv.moment(base_targets, trial), iv.moment(base_paid, trial))
    after = iv.sub(iv.moment(targets, trial), iv.moment(paid, trial))
    gain = iv.sub(after, before)
    need(gain[0] > 0 and after[1] < 0, 'directed improvement with remaining target deficit')
    return word, dict(status='PASS_EIGHT_SECOND_GENERATION_BIT_BIRTHS', parent_pr=7781, parent_head=PARENT_HEAD,
                      source_word_sha256=PARENT_SHA, word_sha256=WORD_SHA, parent_replay_sha256=PARENT_REPLAY,
                      journal_sha256=JOURNAL_SHA, native_paid=native_paid, native_targets=native_targets,
                      paid=paid, targets=targets, signed_positions=positions,
                      native={k: v for k, v in native.items() if k != 'charts'}, ordinary=ordinary,
                      native_coefficients_each_orientation=word['public']**2,
                      caller_coefficients_each_orientation=coefficients, controls=controls,
                      target=TARGET, parent_margin_at_target=iv.show(before), margin_at_target=iv.show(after),
                      gain_at_target=iv.show(gain))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True, help='Pinned original #7776 source tree')
    parser.add_argument('--parent-word', type=Path, required=True, help='Submitted #7781 binary WORD.json.gz')
    parser.add_argument('--parent-replay', type=Path, help='Submitted #7781 binary replay.py beside the word by default')
    parser.add_argument('--journal', type=Path, required=True, help='Pinned eight-step journal')
    parser.add_argument('--out', type=Path, required=True, help='Output directory')
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    parent_replay = args.parent_replay or args.parent_word.with_name('replay.py')
    word, receipt = rebuild(args.source_root, args.parent_word, parent_replay, args.journal)
    wire = (json.dumps(word, separators=(',', ':')) + '\n').encode()
    packed = gzip.compress(wire, mtime=0)
    receipt.update(word_file_sha256=sha256(wire).hexdigest(), word_gzip_sha256=sha256(packed).hexdigest())
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'WORD.json.gz').write_bytes(packed)
    (args.out / 'REPLAY.json').write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n')
    print(receipt['status'], receipt['word_sha256'])


if __name__ == '__main__':
    main()
