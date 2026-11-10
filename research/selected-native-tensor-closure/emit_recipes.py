#!/usr/bin/env python3
"""Rebuild the selected candidate recipes with the credited source compiler.

This is a candidate producer, not the independent acceptance checker. The
complete payload must match the already registered selected recipe digest.
"""
from __future__ import annotations

from functools import lru_cache
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = ROOT/'research/p104-helper470-twin-rung-removal/WORD.json.gz'
RESULT = ROOT/'research/p104-helper470-twin-rung-removal/RESULT.json'
COMPILER = ROOT/'research/p104-native-channel/vendor/clifford_exact.py'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def produce():
    need(hashlib.sha256(WORD.read_bytes()).hexdigest() == '7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f',
         'selected word pin')
    need(hashlib.sha256(COMPILER.read_bytes()).hexdigest() == '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962',
         'candidate compiler pin')
    need(hashlib.sha256(RESULT.read_bytes()).hexdigest() == '84fcbe2a0b64307b5703c363408042bdd91555b0419509aa50daa43b3b1924ad',
         'selected result pin')
    word = json.loads(gzip.decompress(WORD.read_bytes()))
    result = json.loads(RESULT.read_bytes())
    spec = importlib.util.spec_from_file_location('credited_candidate_compiler', COMPILER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    # The candidate producer is deliberately the source implementation. All
    # acceptance, including absolute phases, uses gauss_trace independently.
    @lru_cache(None)
    def chart(index):
        return module.canonical_frame(9, tuple(word['frames'][index]))
    main = set(word['live']) | {r+112 for r in word['live']}
    pairs = {(event[2], event[3]) for event in word['program'] if event[0] == 'MOVE'}
    pairs |= {(word['initial'][r], word['final'][r]) for r in range(word['public']) if r not in main}
    records = []
    for i, (a, b) in enumerate(sorted(pairs)):
        recipe, _ = module.lower_child(chart(a).adjoint().then(chart(b)))
        records.append([a, b, recipe])
        if i % 250 == 0:
            print('candidate_pairs', i, len(pairs), flush=True)
    adapters = []
    for role, q in zip(word['live'], word['ports'], strict=True):
        entry = module.cgate(9, q, 1).adjoint().then(chart(word['initial'][role]))
        exit_ = chart(word['final'][role+112]).adjoint().then(module.cgate(9, q, -1).then(module.fourier(9)))
        for kind, op in (('input', entry), ('output', exit_)):
            recipe, _ = module.lower_child(op)
            adapters.append({'kind': kind, 'role': role, 'port': q, 'recipe': recipe})
    payload = records+[item['recipe'] for item in adapters]
    digest = hashlib.sha256(canonical(payload)).hexdigest()
    need(digest == result['native']['recipe_payload_sha256'], 'complete payload equals selected registered recipes')
    return {'schema': 'selected-native-tensor-closure/1', 'pairs': records, 'adapters': adapters,
            'source_word_sha256': hashlib.sha256(WORD.read_bytes()).hexdigest(), 'recipe_payload_sha256': digest}


def main():
    value = produce()
    raw = canonical(value)+b'\n'
    target = HERE/'NATIVE.json.gz'
    if '--write' in sys.argv:
        target.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
    else:
        need(gzip.decompress(target.read_bytes()) == raw, 'complete regenerated payload bytes')
    print('PASS_SELECTED_NATIVE_RECIPE_EMISSION', value['recipe_payload_sha256'])


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='native-candidate-pycache-') as cache:
        sys.pycache_prefix = cache
        sys.dont_write_bytecode = True
        main()
