#!/usr/bin/env python3
"""Validate the source-bound recorded Lean run; this does not execute Lean.
Prepared for ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('four_channel_check', HERE/'check_lean.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def validate(receipt, sources):
    need(receipt['status'] == 'PASS_FOUR_CHANNEL_LEAN', 'recorded status')
    need('version 4.34.1,' in receipt['version'], 'recorded toolchain')
    need(receipt['source_sha256'] == {n: sha256(b).hexdigest() for n,b in sources.items()}, 'formal source binding')
    need(set(receipt['theorem_axioms']) == checker.NAMES, 'theorem inventory')
    need(all(isinstance(v,list) and len(v) == len(set(v)) and
             set(v) <= {'propext','Classical.choice','Quot.sound'}
             for v in receipt['theorem_axioms'].values()), 'axiom inventory')
    need(receipt['rejected_mutations'] == list(checker.CONTROLS), 'control inventory')


def main():
    receipt = json.loads((HERE/'LEAN-CHECK.json').read_text(encoding='utf-8'))
    sources = {name:(HERE/name).read_bytes() for name in checker.SOURCES}
    predecessor = json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))['predecessors'][0]
    need(sha256(sources['Schur.lean']).hexdigest() == predecessor['sha256'], 'exact predecessor bytes')
    validate(receipt,sources)
    cases=[]
    altered = dict(sources, **{'Pivot.lean':sources['Pivot.lean']+b'\n'})
    cases.append(('formal source drift',receipt,altered))
    bad=deepcopy(receipt); bad['theorem_axioms']['Pivot.factor_to_pivot']=['sorryAx']
    cases.append(('untrusted axiom',bad,sources))
    bad=deepcopy(receipt); del bad['theorem_axioms']['Pivot.no_four_channels']
    cases.append(('missing theorem',bad,sources))
    bad=deepcopy(receipt); bad['rejected_mutations']=bad['rejected_mutations'][:-1]
    cases.append(('missing kernel control',bad,sources))
    for label,bad,raw in cases:
        try:
            validate(bad,raw)
        except ValueError:
            continue
        raise ValueError('accepted control: '+label)
    print('PASS_FOUR_CHANNEL_RECORDED_BINDING theorems=12 receipt_controls=4; not a fresh Lean run')


if __name__ == '__main__':
    main()
