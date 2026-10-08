#!/usr/bin/env python3
"""Compose PR62's interval graph, PR57's compiler and PR60's slot priority.

The scalar graph is unchanged: Avi Eisenberg / ikeboy with Anthropic Claude
assistance. Joint frame synthesis is eumemic's PR57 with OpenAI Codex
assistance. Descending-rank reclamation is Chafik Boukhalfa's PR60 with
OpenAI Codex assistance. This file packages and checks their composition;
it does not claim a new graph or priority rule. Inherited notices remain.
"""
import sys
sys.dont_write_bytecode = True
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
import argparse
import gzip
from hashlib import sha256
import importlib.util
import inspect
import json
from pathlib import Path

import binary_frame_compiler as compiler

ROOT = Path(__file__).resolve().parents[2]
PIN = ROOT / 'references/frame-compiler/pr62'


def check_sources():
    manifest = json.loads((PIN / 'SOURCE.json').read_text())
    for name, digest in manifest['files'].items():
        assert sha256((PIN / name).read_bytes()).hexdigest() == digest, name
    dependency = PIN / manifest['shared_dependency_manifest']
    assert sha256(dependency.read_bytes()).hexdigest() == manifest['shared_dependency_manifest_sha256']
    for name, digest in json.loads(dependency.read_text())['files'].items():
        assert sha256((dependency.parent / name).read_bytes()).hexdigest() == digest, name
    return manifest


def compile_axis(h):
    assert h in (23, 25)
    check_sources()
    spec = importlib.util.spec_from_file_location('ranked_interval_pr62', PIN / 'research/pair-assembly/pair_graph.py')
    producer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(producer)
    graph = producer.graph(h)
    scalar = graph.verify()
    source = inspect.getsource(compiler.compile_)
    before = 'for s in sorted(retired):'
    after = "for s in sorted(retired, key=lambda s: (-blocks[frames[s]]['rank'], s)):"
    assert source.count(before) == 1
    namespace = dict(vars(compiler))
    exec(compile(source.replace(before, after), __file__ + ':ranked_compile', 'exec'), namespace)
    previous = compiler.graph
    compiler.graph = lambda _: graph
    try:
        result, word = namespace['compile_'](h, matching=True, reclaim=True, dirty=True)
    finally:
        compiler.graph = previous
    result['scalar'] = scalar
    result['baseline_pr62_stacked_roles'] = {23: 27918, 25: 36586}[h]
    return result, word


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--h', type=int, choices=(23, 25), required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--word', type=Path, required=True)
    args = parser.parse_args()
    result, word = compile_axis(args.h)
    raw = (json.dumps(word, separators=(',', ':')) + '\n').encode()
    args.word.write_bytes(gzip.compress(raw, mtime=0))
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result), flush=True)
