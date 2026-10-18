#!/usr/bin/env python3
"""Equivalence and controls for the joint-dual replay fast adapter.

Checks, in order:
  1. Source-freeze binding: the historical replay/prepare/test files and both
     pinned words still match the frozen `research/joint-dual/SOURCE.json`
     record, so the adapter is compared against the frozen chain.
  2. Clean-word equivalence on both pinned words: legacy `replay` and the fast
     adapter return equal receipts, equal to the recorded compiler receipt;
     the transitions stage (delegated unchanged) equals the recorded receipt.
  3. Full literal cross-check: for every output of both words, the mask
     algebra equals the historical literal scan expression.
  4. Mutation matrix: the exact twelve mutations of `tests/test_joint_reclaim.py`
     on both words; the historical module is the oracle: every accept/reject
     outcome agrees between legacy and fast implementations, the eleven
     documented rejections reject, and the scatter-reversal case accepts with
     equal receipts.
  5. Failure controls: a corrupted containment table is detected by the
     cross-check; an unchecked word rejects; -O runs refuse to start.

No timing is used as a gate; paired timings live in benchmark.py.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')

from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'scripts' / 'experiments'))

import binary_frame_replay as legacy
import binary_frame_profile_prepare as legacy_prepare
import fast_replay

WORDS = {h: ROOT / f'certificates/joint-dual-word-{h}.json.gz' for h in (23, 25)}
FREEZE = json.loads((ROOT / 'research/joint-dual/SOURCE.json').read_text())
RECORDED = json.loads((ROOT / 'certificates/joint-dual-compiler.json').read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def js(value):
    return json.loads(json.dumps(value))


def literal_expected(triples, common, triple):
    # The exact historical scan expression, written out independently here.
    return sum(1 << i for i, t in enumerate(triples)
               if common in t and not (set(t) & (set(triple) - {common})))


def outcome(check, *args):
    try:
        receipt = check(*args)
    except Exception as exc:  # rejection class and message are recorded, not trusted
        return ('reject', type(exc).__name__)
    return ('accept', hashlib.sha256(json.dumps(js(receipt), sort_keys=True).encode()).hexdigest()[:16])


def mutations():
    """The exact mutation matrix of tests/test_joint_reclaim.py (historical, frozen)."""
    def omitted_literal_xor(word):
        word['ops'].pop(0)

    def self_xor(word):
        word['ops'][0][1] = word['ops'][0][0]

    def non_nested_operation_frame(word):
        narrow = next(i for i, (core, cover) in enumerate(word['frames']) if core == cover)
        operation = next(op for op in word['ops'] if word['frames'][op[2]][0] != word['frames'][op[2]][1])
        operation[2] = narrow

    def aliased_terminal_role(word):
        word['outputs'][1][0] = word['outputs'][0][0]

    def missing_copied_center(word):
        index = next(i for i, (_, _, _, target) in enumerate(word['outputs']) if len(target) == 1)
        word['outputs'].pop(index)

    def omitted_transition(word):
        word['events'].pop(0)

    def understated_physical_width(word):
        word['R'] -= 1

    def self_cancelling_uncharged_scatter(word):
        # PR #64 (rfu08) counterexample: algebraic cancellation cannot
        # authorize extra incidences absent from outputs.
        outputs = {record[0] for record in word['outputs']}
        slot = next(s for s in range(word['R']) if s not in outputs)
        rogue = [word['v'], 2 * word['v'] + slot]
        word['scatter'].extend([rogue, rogue])

    def negative_operation_frame_index(word):
        word['ops'][0][2] -= len(word['frames'])

    def cancelled_repetitions_of_paid_scatter(word):
        word['scatter'].extend([word['scatter'][0], word['scatter'][0]])

    def missing_scatter(word):
        word['scatter'].pop(0)

    return [
        ('omitted_literal_xor', 'both', omitted_literal_xor),
        ('self_xor', 'replay', self_xor),
        ('non_nested_operation_frame', 'both', non_nested_operation_frame),
        ('aliased_terminal_role', 'replay', aliased_terminal_role),
        ('missing_copied_center', 'both', missing_copied_center),
        ('omitted_transition', 'transitions', omitted_transition),
        ('understated_physical_width', 'both', understated_physical_width),
        ('self_cancelling_uncharged_scatter', 'both', self_cancelling_uncharged_scatter),
        ('negative_operation_frame_index', 'replay', negative_operation_frame_index),
        ('cancelled_repetitions_of_paid_scatter', 'both', cancelled_repetitions_of_paid_scatter),
        ('missing_scatter', 'both', missing_scatter),
    ]


def check_freeze():
    for name in ('scripts/experiments/binary_frame_replay.py',
                 'scripts/experiments/binary_frame_profile_prepare.py',
                 'tests/test_joint_reclaim.py'):
        require(FREEZE['files'][name] == sha(ROOT / name), 'frozen source drift: ' + name)
    for h, path in WORDS.items():
        require(FREEZE['files'][f'certificates/joint-dual-word-{h}.json.gz'] == sha(path),
                f'pinned word drift: h={h}')
    return dict(frozen_sources=3, pinned_words=2)


def check_clean_words():
    receipts = {}
    for h, word in WORDS.items():
        old = js(legacy.replay(word))
        new = js(fast_replay.replay(word))
        require(old == new, f'legacy/fast replay receipts differ: h={h}')
        require(old == RECORDED['axes'][str(h)]['replay'], f'receipt differs from recorded compiler receipt: h={h}')
        with tempfile.TemporaryDirectory(prefix='jd-replay-fast-') as directory:
            destination = Path(directory) / f'word{h}.bin'
            old_transitions = js(legacy_prepare.prepare(word, destination))
            new_transitions = js(fast_replay.prepare(word, destination))
            require(old_transitions == new_transitions, f'transitions receipts differ: h={h}')
            recorded = json.loads((ROOT / f'certificates/joint-dual-transitions-{h}.json').read_text())
            require(old_transitions == recorded, f'transitions receipt differs from recorded: h={h}')
        receipts[h] = old
    return receipts


def check_literal_cross_check():
    total = 0
    for h, word in WORDS.items():
        raw = json.loads(gzip.decompress(Path(word).read_bytes()))
        triples, center, pair, destinations, lookup = fast_replay.tables(h)
        for s, g, common, triple in raw['outputs']:
            require(fast_replay.expected_mask(center, pair, common, triple) ==
                    literal_expected(triples, common, triple), f'mask scan mismatch: h={h} output {s}')
            if len(triple) == 1:
                require(destinations[common] == [i for i, t in enumerate(triples) if common in t],
                        f'destination list mismatch: h={h}')
            else:
                require([lookup[tuple(triple)]] == [triples.index(tuple(triple))],
                        f'triple lookup mismatch: h={h}')
            total += 1
    return total


def check_mutation_matrix():
    rows = []
    with tempfile.TemporaryDirectory(prefix='jd-mutations-') as directory:
        work = Path(directory)
        for h, source in WORDS.items():
            original = json.loads(gzip.decompress(Path(source).read_bytes()))
            cases = [(name, scope, mutate) for name, scope, mutate in mutations()]
            cases.append(('scatter_order_acceptance', 'both', None))
            for name, scope, mutate in cases:
                changed = deepcopy(original)
                if mutate is None:
                    changed['scatter'].reverse()
                else:
                    mutate(changed)
                path = work / f'word-{h}-{name}.json'
                path.write_text(json.dumps(changed, separators=(',', ':')) + '\n', encoding='utf-8')
                outcomes = {
                    'replay': (outcome(legacy.replay, path), outcome(fast_replay.replay, path)),
                    'transitions': (outcome(legacy_prepare.prepare, path, work / 'transitions.bin'),
                                    outcome(fast_replay.prepare, path, work / 'transitions.bin')),
                }
                for checker, (old, new) in outcomes.items():
                    require(old == new,
                            f'outcome differs for {name} h={h} checker={checker}: {old} vs {new}')
                if mutate is not None:
                    checked = ('replay', 'transitions') if scope == 'both' else (scope,)
                    for checker in checked:
                        require(outcomes[checker][0][0] == 'reject',
                                f'historical checker did not reject {name} h={h} checker={checker}')
                else:
                    require(outcomes['replay'][0][0] == 'accept' and outcomes['transitions'][0][0] == 'accept',
                            f'scatter reversal must accept in both checkers: h={h}')
                rows.append(dict(h=h, mutation=name, scope=scope,
                                 replay=outcomes['replay'][0], transitions=outcomes['transitions'][0]))
    return rows


def check_failure_controls():
    detected = {}
    for h, word in WORDS.items():
        raw = json.loads(gzip.decompress(Path(word).read_bytes()))
        triples, center, pair, destinations, lookup = fast_replay.tables(h)
        corrupt = [row[:] for row in pair]
        corrupt[0][1], corrupt[0][2] = corrupt[0][2], corrupt[0][1]
        mismatches = sum(
            1 for s, g, common, triple in raw['outputs']
            if fast_replay.expected_mask(center, corrupt, common, triple) !=
            literal_expected(triples, common, triple))
        require(mismatches > 0, f'corrupted table escaped the cross-check: h={h}')
        clean = sum(
            1 for s, g, common, triple in raw['outputs']
            if fast_replay.expected_mask(center, pair, common, triple) !=
            literal_expected(triples, common, triple))
        require(clean == 0, f'clean table disagrees with literal scan: h={h}')
        detected[h] = mismatches
    unchecked = dict(h=3, v=1, R=1, frames=[[7, 7]], sources={'0': 0},
                     ops=[], outputs=[], scatter=[], events=[[0, -1, 0]])
    with tempfile.TemporaryDirectory(prefix='jd-unchecked-') as directory:
        path = Path(directory) / 'word.json'
        path.write_text(json.dumps(unchecked) + '\n', encoding='utf-8')
        require(outcome(fast_replay.replay, path)[0] == 'reject', 'unchecked word must reject')
        require(outcome(fast_replay.prepare, path, Path(directory) / 'transitions.bin')[0] == 'reject',
                'unchecked word must reject in the transitions stage')
        guarded = subprocess.run([sys.executable, '-O', str(HERE / 'fast_replay.py'), str(path)],
                                 capture_output=True, text=True)
        require(guarded.returncode != 0 and 'Assertions must remain enabled' in guarded.stderr,
                '-O entry must refuse to run')
    return dict(corrupted_table_mismatches=detected, unchecked_word=True, optimize_guard=True)


def check_frozen_suite():
    """Adoption simulation: the frozen historical test module passes unmodified
    against the adapter through shim/binary_frame_replay.py (suite_arm.py)."""
    process = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'suite_arm.py'), str(ROOT), 'fast'],
                             capture_output=True, text=True, cwd=str(ROOT))
    require(process.returncode == 0, 'frozen suite arm failed:\n' + process.stdout + process.stderr)
    record = json.loads(process.stdout.strip().splitlines()[-1])
    require(record['failures'] == 0 and record['errors'] == 0 and record['tests'] > 0,
            f'frozen suite did not pass against the adapter: {record}')
    require('joint-dual-replay-fast' in record['replay_module'].replace('\\', '/'),
            f'frozen suite did not use the adapter: {record}')
    return dict(frozen_suite_tests=record['tests'], frozen_suite_seconds=record['seconds'])


def verify():
    freeze = check_freeze()
    receipts = check_clean_words()
    outputs = check_literal_cross_check()
    rows = check_mutation_matrix()
    controls = check_failure_controls()
    controls.update(check_frozen_suite())
    result = dict(
        status='PASS_JOINT_DUAL_REPLAY_FAST_EQUIVALENCE',
        words=sorted(receipts), outputs_cross_checked=outputs,
        mutation_cases=len(rows), mutation_rows=rows,
        retained_checks='historical check_word, every replay assertion and both full-basis orientations, the unchanged transitions stage, and the frozen tests/test_joint_reclaim.py matrix as oracle',
        invalidation='containment tables are rebuilt from the word on every call; no persistent cache; source-freeze and word pins checked each run',
        controls=controls, freeze=freeze,
        scope='Opt-in adapter equivalence on the two frozen joint-dual words; no kappa, certificate, supplier or frontier change.')
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


if __name__ == '__main__':
    result = verify()
    if '--record' in sys.argv[1:]:
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
