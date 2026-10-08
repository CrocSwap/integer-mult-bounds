#!/usr/bin/env python3
"""Joint frame synthesis with descending-rank reclamation on the PR55 producer.

The source graph is unmodified and hash-pinned, including its original credits.
The circuit dependencies are byte-identical to the pinned PR48 files. This
dedicated compiler changes only retired-slot selection priority relative to
PR58. The original shared PR57 compiler remains unchanged for its baseline.
Every generated word checks the full input and dirty basis in both orientations;
verify_joint_dual.py separately replays the word, profiles, and conditional bound.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')

import sys
sys.dont_write_bytecode = True
import argparse
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

import joint_dual_reclaim_compiler as compiler

ROOT = Path(__file__).resolve().parents[2] / 'references/frame-compiler/pr55'
MANIFEST = json.loads((ROOT / 'SOURCE.json').read_text())
for name, digest in MANIFEST['files'].items():
    assert sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
assert sha256((ROOT / MANIFEST['shared_dependency_manifest']).read_bytes()).hexdigest() == MANIFEST['shared_dependency_manifest_sha256']
spec = importlib.util.spec_from_file_location('pinned_joint_dual_graph', ROOT / 'research/skip-suffix/skip_graph.py')
producer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(producer)


def compile_axis(h):
    assert h in (23, 25)
    previous = compiler.graph
    compiler.graph = producer.graph
    try:
        result, word = compiler.compile_(h, matching=True, reclaim=True, dirty=True)
    finally:
        compiler.graph = previous
    result.pop('seconds', None)
    result['scalar'] = producer.graph(h).verify()
    result['source_pr55_head'] = MANIFEST['commit']
    result['baseline_pr57_roles'] = {23: 31416, 25: 41264}[h]
    result['baseline_pr58_roles'] = {23: 30790, 25: 40446}[h]
    result['reclamation_order'] = 'descending current frame rank, then slot ID'
    return result, word


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--h', type=int, choices=(23, 25), required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--word', type=Path, required=True)
    args = parser.parse_args()
    result, word = compile_axis(args.h)
    raw = (json.dumps(word, separators=(',', ':')) + '\n').encode()
    if args.word.suffix == '.gz':
        with args.word.open('wb') as stream:
            with gzip.GzipFile(fileobj=stream, mode='wb', mtime=0) as archive:
                archive.write(raw)
    else:
        args.word.write_bytes(raw)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result), flush=True)
