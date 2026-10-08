#!/usr/bin/env python3
"""Compile aligned split frames with profile-cost pending live reclamation."""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True

import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import os
import shlex
import subprocess
import tempfile

import balanced_split_engine
import balanced_split_exchange_engine
ENGINES = {23: balanced_split_engine, 25: balanced_split_exchange_engine}
import balanced_split_graph as producer

ROOT = Path(__file__).resolve().parents[2]


def source_record():
    return dict(pr65=producer.checked_manifest(producer.BASELINE),
                pr67=producer.checked_manifest(ROOT / 'references/frame-compiler/pr67'),
                pr68=producer.checked_manifest(ROOT / 'references/frame-compiler/pr68'),
                pr69=producer.checked_manifest(ROOT/'references/frame-compiler/pr69'),
                pr70=producer.checked_manifest(ROOT/'references/frame-compiler/pr70'),
                pr71=producer.checked_manifest(ROOT/'references/frame-compiler/pr71'),
                inherited=producer.checked_manifest(ROOT / 'references/frame-compiler/pr48'))


def compile_axis(h):
    config = producer.configuration(h)
    compiler = ENGINES[h]
    provenance = json.loads((ROOT/'research/balanced-split/engine-provenance.json').read_text())
    assert sha256(Path(compiler.__file__).read_bytes()).hexdigest() == provenance[str(h)]['portable_engine_sha256'], 'Selected engine changed'
    previous_graph, previous_build = compiler.graph, compiler.build
    absent = object()
    runtime_names = ('oracles', 'ORACLE_EXE', 'ORACLE_INPUT', 'PENDING_COST')
    previous_runtime = {name:getattr(compiler, name, absent) for name in runtime_names}
    try:
        compiler.graph = producer.graph
        compiler.build = producer.ordered_build(previous_build, h)
        compiler.PENDING_COST = True
        with tempfile.TemporaryDirectory(prefix='balanced-split-compile-') as directory:
            work = Path(directory)
            oracle = work/'profile-oracle'
            subprocess.run([*shlex.split(os.environ.get('CXX', 'c++')), '-O3', '-std=c++17',
                '-I', str(ROOT/'references/frame-compiler/pr48/scripts/partial_swap'),
                str(ROOT/'references/frame-compiler/pr67/research/slot-cost-rank-pair/profile_oracle.cpp'),
                '-o', str(oracle)], check=True)
            compiler.oracles = []
            compiler.ORACLE_EXE, compiler.ORACLE_INPUT = str(oracle), str(work/'oracle-input.bin')
            try:
                result, word = compiler.compile_(h, matching=True, reclaim=True, dirty=True)
            finally:
                for process in compiler.oracles:
                    process.stdin.close()
                    assert process.wait(timeout=10) == 0, 'Discovery profile oracle failed'
    finally:
        compiler.graph, compiler.build = previous_graph, previous_build
        for name, value in previous_runtime.items():
            if value is absent:
                if hasattr(compiler, name):
                    delattr(compiler, name)
            else:
                setattr(compiler, name, value)
    result.pop('seconds', None)
    result['scalar'] = producer.graph(h).verify()
    result['graph_configuration'] = config
    result['source_pr65_head'] = source_record()['pr65']['commit']
    result['baseline_pr65_roles'] = {23: 27918, 25: 36586}[h]
    result['source_pr67_head'] = source_record()['pr67']['commit']
    result['source_pr68_head'] = source_record()['pr68']['commit']
    result['reclamation_order'] = 'all eligible retired ranks, exact integer profile cost, XOR count, slot ID'
    result['pending_live_controls'] = True
    result['pending_cost_uses_next_use_frame'] = True
    result['paid_clones'] = 0
    result['future_unit_completion'] = True
    result['carry_exchange_passes'] = config['carry_exchange_passes']
    assert result['stats'].get('carry_exchanges', 0) == {23:0, 25:1000}[h]
    for number in (69,70,71):
        result['source_pr'+str(number)+'_head'] = source_record()['pr'+str(number)]['commit']
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
