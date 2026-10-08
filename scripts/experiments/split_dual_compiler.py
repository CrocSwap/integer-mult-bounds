#!/usr/bin/env python3
"""Compile the fixed split/dual graph with the unchanged PR60 ranked engine."""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True

import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path

import joint_dual_reclaim_compiler as compiler
import split_dual_graph as producer

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / 'references/frame-compiler/pr60'


def source_record():
    return dict(split=producer.checked_manifest(producer.SPLIT),
                suffix=producer.checked_manifest(producer.SUFFIX),
                ranked=producer.checked_manifest(BASELINE))


def compile_axis(h):
    producer.configuration(h)
    previous_source = json.loads((BASELINE / 'research/joint-dual/SOURCE.json').read_text())
    name = 'scripts/experiments/joint_dual_reclaim_compiler.py'
    assert sha256((ROOT / name).read_bytes()).hexdigest() == previous_source['files'][name]
    previous = compiler.graph
    try:
        compiler.graph = producer.graph
        result, word = compiler.compile_(h, matching=True, reclaim=True, dirty=True)
    finally:
        compiler.graph = previous
    result.pop('seconds', None)
    result['scalar'] = producer.graph(h).verify()
    result['graph_configuration'] = producer.configuration(h)
    result['source_pr59_head'] = source_record()['split']['commit']
    result['source_pr55_head'] = source_record()['suffix']['commit']
    result['baseline_pr60_roles'] = {23: 30688, 25: 40338}[h]
    result['reclamation_order'] = 'descending current frame rank, then slot ID'
    result['paid_clones'] = 0
    result['pinned_permutation_overrides'] = 0
    return result, word


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--h', type=int, choices=(23, 25), required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--word', type=Path, required=True)
    args = parser.parse_args()
    result, word = compile_axis(args.h)
    raw = (json.dumps(word, separators=(',', ':')) + '\n').encode()
    args.word.write_bytes(gzip.compress(raw, mtime=0) if args.word.suffix == '.gz' else raw)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result), flush=True)
