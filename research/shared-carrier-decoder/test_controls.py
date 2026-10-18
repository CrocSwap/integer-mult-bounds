#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Reject changes that break the decoder or its physical contract."""
from copy import deepcopy
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from model import N, basis, build, distance, require
from physical import Array, Executor, SIZE
from verify import CliffordAudit, compare_receipt, frame_replay, symbolic_replay


def rejected(name, action, expected):
    try:
        action()
    except ValueError as error:
        require(expected in str(error), f'{name}: wrong rejection: {error}')
    else:
        raise ValueError(f'{name}: bad construction was accepted')
    print('PASS_CONTROL_' + name, flush=True)


def omit(word, phase):
    changed = deepcopy(word)
    index = next(i for i, event in enumerate(changed['events']) if event.get('phase') == phase)
    del changed['events'][index]
    return changed


def main():
    expected = json.loads((HERE / 'EXPECTED.json').read_text())
    actual = deepcopy(expected)
    for entry in actual['words'].values():
        for key in ('profile', 'copy_profile', 'move_profile'):
            entry['frame'][key] = {int(rank): count for rank, count in entry['frame'][key].items()}
    compare_receipt(actual, expected)
    for name, value in (('BOOLEAN_RECEIPT', True), ('FLOAT_RECEIPT', 1.0)):
        changed = deepcopy(expected)
        changed['words']['coordinate']['physical']['temporary_streams_peak'] = value
        rejected(name, lambda: compare_receipt(actual, changed), 'committed certificate agreement')
    with tempfile.TemporaryDirectory(prefix='decoder missing receipt ') as directory:
        copy = Path(directory) / 'decoder'
        shutil.copytree(HERE, copy)
        (copy / 'EXPECTED.json').unlink()
        result = subprocess.run([sys.executable, '-I', '-B', str(copy / 'verify.py')],
                                cwd=directory, capture_output=True, text=True, check=False)
        require(result.returncode != 0 and 'committed certificate missing' in result.stderr,
                'missing certificate must fail at the CLI boundary')
    print('PASS_CONTROL_MISSING_CERTIFICATE', flush=True)
    word = build(True)
    for phase in ('compensate', 'restore_gather', 'restore_source', 'source_read'):
        changed = omit(word, phase)
        rejected('OMIT_' + phase.upper(), lambda: symbolic_replay(changed), 'forward arbitrary-input map')

    changed = deepcopy(word)
    event = next(e for e in changed['events'] if e['op'] == 'copy_add' and e['term'] == word['geometry']['pivot'])
    event['q'] = '1'
    rejected('WRONG_DECODER_COEFFICIENT', lambda: symbolic_replay(changed), 'forward arbitrary-input map')

    changed = deepcopy(word)
    starts = [i for i, e in enumerate(changed['events']) if e['op'] == 'copy_begin']
    ends = [i + 1 for i, e in enumerate(changed['events']) if e['op'] == 'copy_end']
    groups = [changed['events'][a:b] for a, b in zip(starts, ends)]
    changed['events'] = changed['events'][:starts[0]] + groups[-1] + sum(groups[:-1], []) + changed['events'][ends[-1]:]
    rejected('NONZERO_ENDPOINT_FIRST', lambda: frame_replay(changed), 'copy common frame')

    changed = deepcopy(word)
    event = next(e for e in changed['events'] if e['op'] == 'copy_begin' and e['after'])
    event['after'] = [word['geometry']['labels'][word['geometry']['extra']]]
    rejected('ILLEGAL_COPY_ENDPOINT', lambda: frame_replay(changed), 'copy endpoint outside source span')

    changed = deepcopy(word)
    idle = changed['unused'][0]
    changed['events'] = [e for e in changed['events'] if not (e['op'] == 'move' and e['role'] == idle)]
    rejected('UNPAID_IDLE_TAIL', lambda: frame_replay(changed), 'all physical sink frames')

    changed = deepcopy(word)
    index = next(i for i, e in enumerate(changed['events']) if e['op'] == 'copy_add')
    changed['events'].insert(index, dict(op='copy_end', term=changed['events'][index]['term']))
    rejected('EARLY_COPY_ERASURE', lambda: frame_replay(changed), 'copy term lifetime')

    audit = CliffordAudit()
    event = next(e for e in word['events'] if e['op'] == 'copy_begin' and e['after'])
    before, after = basis(event['before']), basis(event['after'])
    _, original, compiled = audit.transition(before, after, distance(before, after))
    seed = [0] * SIZE
    seed[0] = 1
    executor = Executor()
    wanted = executor.apply(Array(seed, [0] * SIZE), original.circuit)
    bad_phase = compiled.circuit + [('phase', 1)]
    rejected('BINARY_FRAME_WITH_WRONG_GLOBAL_PHASE',
             lambda: require(executor.apply(Array(seed, [0] * SIZE), bad_phase).same(wanted), 'exact physical copy phase'),
             'exact physical copy phase')
    first_c = next(i for i, e in enumerate(compiled.circuit) if e[0] == 'C')
    bad_child = compiled.circuit[:first_c] + compiled.circuit[first_c + 1:]
    rejected('OMITTED_RECURSIVE_FACTOR',
             lambda: require(executor.apply(Array(seed, [0] * SIZE), bad_child).same(wanted), 'exact physical copy operator'),
             'exact physical copy operator')
    print('PASS_SHARED_CARRIER_CONTROLS controls=14')


if __name__ == '__main__':
    main()
