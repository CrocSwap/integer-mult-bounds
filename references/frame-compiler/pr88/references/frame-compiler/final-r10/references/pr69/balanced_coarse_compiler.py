#!/usr/bin/env python3
"""Balance each four-edge coarse sum in PR62 into two column pair-star sums.

Instead of a three-addition chain, use (e(a,b)+e(a2,b))+(e(a,b2)+e(a2,b2)).
The existing interning shares pair-star sums with the strip computations.
Only the coarse-edge construction changes. The full graph is checked and
compiled, so all remaining copies and clearing operations remain charged.

Base graph: Avi Eisenberg / ikeboy, with Anthropic Claude assistance (#62).
Compiler: eumemic with OpenAI Codex assistance (#57). Rank priority: Chafik
Boukhalfa with OpenAI Codex assistance (#60). Their unchanged composition
is also published by Dominik Scholz with OpenAI Codex assistance (#63).
This coarse-sum experiment was prepared with OpenAI Codex assistance.
All inherited licenses and notices remain.
"""
import sys
sys.dont_write_bytecode = True
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
import argparse
import gzip
from hashlib import sha256
import inspect
import json
from pathlib import Path

import binary_frame_compiler as compiler
import ranked_interval_compiler as predecessor

ROOT = Path(__file__).resolve().parents[2]
PIN = ROOT / 'references/frame-compiler/balanced-coarse'
BEFORE = '''            coarse = {(i, j): self.total([e(a, b) for a in groups[i] for b in groups[j]])
                      for i, j in combinations(range(ng), 2)}'''
AFTER = '''            def coarse_sum(i, j):
                columns = [self.total([e(a,b) for a in groups[i]]) for b in groups[j]]
                return self.total(columns)
            coarse = {(i,j):coarse_sum(i,j) for i,j in combinations(range(ng),2)}'''


def check_sources():
    predecessor.check_sources()
    manifest = json.loads((PIN / 'SOURCE.json').read_text())
    for name, digest in manifest['files'].items():
        assert sha256((PIN / name).read_bytes()).hexdigest() == digest, name
    dependency = PIN / manifest['shared_dependency_manifest']
    assert sha256(dependency.read_bytes()).hexdigest() == manifest['shared_dependency_manifest_sha256']
    return manifest


def graph(h):
    assert h in (23, 25)
    check_sources()
    path = predecessor.PIN / 'research/pair-assembly/pair_graph.py'
    source = path.read_text()
    assert source.count(BEFORE) == 1
    namespace = {'__file__': str(path), '__name__': 'balanced_coarse_pr62'}
    exec(compile(source.replace(BEFORE, AFTER), str(path) + ':balanced_coarse', 'exec'), namespace)
    result = namespace['graph'](h)
    result.verify()
    return result


def compile_axis(h):
    circuit = graph(h)
    source = inspect.getsource(compiler.compile_)
    before = 'for s in sorted(retired):'
    after = "for s in sorted(retired, key=lambda s: (-blocks[frames[s]]['rank'], s)):"
    assert source.count(before) == 1
    namespace = dict(vars(compiler))
    exec(compile(source.replace(before, after), __file__ + ':ranked_compile', 'exec'), namespace)
    # build() is the original function and resolves graph in compiler's globals.
    previous = compiler.graph
    compiler.graph = lambda _: circuit
    try:
        result, word = namespace['compile_'](h, matching=True, reclaim=True, dirty=True)
    finally:
        compiler.graph = previous
    result['scalar'] = circuit.verify()
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
