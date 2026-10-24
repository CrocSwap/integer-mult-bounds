#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Meaningful mutation controls on the actual adapted FOUR native transport.

Fresh output directories; baseline must pass before six precise mutations.
The explicit scale1 gate is not a mathematical target climb obligation by
itself: a later framed add may perform the same climb implicitly. We instead
delete the required target level metadata to test the CUT interface obligation.
"""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def remove_B_gate(word, index):
    del word['B'][index]
    for warp in word['warps']:
        if warp[0] > index:
            warp[0] -= 1


def mutate(original, kind):
    word = copy.deepcopy(original)
    prefix = word['seed39']['prelude_events']
    correction = next(i for i, e in enumerate(word['A'][:prefix]) if e[0] == 'add')
    if kind == 'missing_lifted_target_level':
        target = word['A'][correction][1]
        del word['target_levels'][str(target - word['report']['v'])]
    elif kind == 'omitted_compensation':
        del word['A'][correction]
    elif kind == 'wrong_compensation_sign':
        word['A'][correction][3] *= -1
    elif kind == 'omitted_lender_restoration':
        i = next(i for i, e in enumerate(word['B']) if e[:5] == ['add', 33, 49, 1, 2])
        remove_B_gate(word, i)
    elif kind == 'omitted_cleanup_inverse':
        i = next(i for i, e in enumerate(word['cleanup']) if e[:3] == ['warp', 33, -49])
        del word['cleanup'][i]
    elif kind == 'omitted_prelude_unwarp':
        i = next(i for i, e in enumerate(word['A'][:prefix]) if e[:3] == ['warp', 33, -49])
        del word['A'][i]
    else:
        raise ValueError(kind)
    return word


def main():
    if not __debug__:
        raise RuntimeError('assertions must remain enabled')
    ap = argparse.ArgumentParser()
    ap.add_argument('--workdir', type=Path)
    ap.add_argument('--out', type=Path, default=HERE / 'TRANSPORT-CONTROLS.json')
    args = ap.parse_args()
    work = args.workdir or Path(tempfile.mkdtemp(prefix='seed39-four-transport-controls-'))
    if args.workdir is not None:
        work.mkdir(parents=True, exist_ok=False)
    records = []
    converter = HERE / 'transport_lifted.py'
    for tag in ['base', 'extra']:
        source = HERE / 'words' / f'FOUR-{tag}.json.gz'
        original = json.loads(gzip.decompress(source.read_bytes()))
        positive = subprocess.run([sys.executable, '-B', str(converter), str(source), str(work / f'{tag}-positive')], capture_output=True, text=True)
        assert positive.returncode == 0, positive.stderr[-2000:]
        audit = json.loads((work / f'{tag}-positive' / 'SCALAR-FRAME-AUDIT.json').read_text())
        assert audit['status'] == 'PASS_BORROW_WORD_FREE_ALGEBRA_ALL_COLUMNS_AND_NATIVE_FRAMES'
        for kind in ['missing_lifted_target_level', 'omitted_compensation', 'wrong_compensation_sign',
                     'omitted_lender_restoration', 'omitted_cleanup_inverse', 'omitted_prelude_unwarp']:
            word = mutate(original, kind)
            raw = json.dumps(word, sort_keys=True, separators=(',', ':')).encode()
            path = work / f'{tag}-{kind}.json.gz'
            path.write_bytes(gzip.compress(raw, mtime=0))
            tested = subprocess.run([sys.executable, '-B', str(converter), str(path), str(work / f'{tag}-{kind}-out')], capture_output=True, text=True)
            assert tested.returncode != 0, ('mutation accepted', tag, kind)
            if kind == 'missing_lifted_target_level':
                assert 'assert all(cur[v + t] == levels.get(str(t), 0)' in tested.stderr, tested.stderr[-2000:]
                detection = 'CUT target frame differs from declared level'
            else:
                assert 'arbitrary-input endpoint (free warp algebra)' in tested.stderr, tested.stderr[-2000:]
                detection = 'arbitrary-input free-operator endpoint differs'
            records.append(dict(provider=tag, mutation=kind, rejected=True, detection=detection,
                                mutation_sha256=hashlib.sha256(raw).hexdigest(),
                                source_word_sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
            print('REJECTED', tag, kind, flush=True)
    paths = [converter, Path(__file__).resolve()] + [HERE / 'words' / f'FOUR-{tag}.json.gz' for tag in ['base', 'extra']]
    out = dict(status='PASS_ADAPTED_FOUR_TRANSPORT_12_MUTATION_CONTROLS',
               positive_words=2, negative_controls=records,
               source_sha256={str(p.relative_to(HERE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
               scope='Fresh forward and inverse-transpose all-column native transport of both unmutated words, then six focused mutations each. Gaussian recipes, native phase budgets, owner fill and outer bound require separate checks.',
               attribution='Tekalign (@tekuuu), with substantial OpenAI Codex assistance. Apache-2.0.')
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    print(out['status'])


if __name__ == '__main__':
    main()
