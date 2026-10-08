#!/usr/bin/env python3
"""Compile the frozen final frame composition and exactly relabel coordinates.

Chafik Boukhalfa with OpenAI Codex assistance. Uses credited PR65/67/68/69/70
construction, Thomas DiFiore's PR74 order and relabeling, and Rohan Arun's
PR78 coordinate-flag search idea and PR82 coordinate-aware oracle pricing. Original notices and source bytes are retained.
"""
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
_previous_path = sys.path[:]
try:
    import final_frame_engine as compiler
finally:
    sys.path[:] = _previous_path
from final_frame_nodeops import relabel,verify_dense
import final_frame_graph as producer
ENGINES = {23: compiler, 25: compiler}
ROOT = Path(__file__).resolve().parents[2]


def source_record():
    paths = {f'pr{n}':ROOT/f'references/frame-compiler/pr{n}' for n in (65,67,68,69,70,71,74,78,79,82,84)}
    paths.update(inherited=ROOT/'references/frame-compiler/pr48', indexed_r5=ROOT/'references/frame-compiler/indexed-r5',final_r10=ROOT/'references/frame-compiler/final-r10')
    return {name:producer.checked_manifest(path) for name,path in paths.items()}


def compile_axis(h):
    config = producer.configuration(h)
    provenance = json.loads((ROOT/'research/final-frame/engine-provenance.json').read_text())
    for record in provenance.values():
        actual = ROOT/'scripts/experiments'/record['portable_engine']
        assert sha256(actual.read_bytes()).hexdigest() == record['portable_engine_sha256'], 'Selected source changed'
        assert actual.read_bytes() == (ROOT/record['original']).read_bytes(), 'Portable source differs'
    selection = json.loads((ROOT/'research/final-frame/discovery-selection.json').read_text())['axes'][str(h)]
    binding=json.loads((ROOT/'research/final-frame/word-bindings.json').read_text())[str(h)]
    previous_graph, previous_build = compiler.graph, compiler.build
    absent = object()
    names = ('oracles','ORACLE_EXE','ORACLE_INPUT','PENDING_COST','OUTPUT_MODE','ORACLE_COORDINATES','THREE_CYCLE_PASSES')
    previous = {name:getattr(compiler,name,absent) for name in names}
    try:
        compiler.graph = producer.graph
        compiler.PENDING_COST = True
        compiler.OUTPUT_MODE = config['output_mode']
        compiler.ORACLE_COORDINATES = config['coordinate_permutation'] if config['oracle_coordinate_pricing'] else list(range(h))
        compiler.THREE_CYCLE_PASSES = config['three_cycle_passes']
        with tempfile.TemporaryDirectory(prefix='final-frame-compile-') as directory:
            work=Path(directory);oracle=work/'profile-oracle'
            subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17',
                '-I',str(ROOT/'references/frame-compiler/pr48/scripts/partial_swap'),
                str(ROOT/'references/frame-compiler/pr67/research/slot-cost-rank-pair/profile_oracle.cpp'),
                '-o',str(oracle)],check=True)
            compiler.oracles=[];compiler.ORACLE_EXE=str(oracle);compiler.ORACLE_INPUT=str(work/'oracle-input.bin')
            try:
                result,word=compiler.compile_(h,matching=True,reclaim=True,dirty=True)
            finally:
                for process in compiler.oracles:
                    process.stdin.close()
                    assert process.wait(timeout=10)==0,'Profile oracle failed'
    finally:
        compiler.graph,compiler.build=previous_graph,previous_build
        for name,value in previous.items():
            if value is absent:
                if hasattr(compiler,name):delattr(compiler,name)
            else:setattr(compiler,name,value)
    result.pop('seconds',None)
    parent = json.loads((ROOT/f'research/final-frame/parent-result-{h}.json').read_text())
    parent.pop('seconds',None)
    assert json.loads(json.dumps(result)) == parent, 'Frozen parent compiler receipt differs'
    raw=lambda value:(json.dumps(value,separators=(',',':'))+'\n').encode()
    parent_sha=sha256(raw(word)).hexdigest()
    assert parent_sha == binding['parent_word_sha256'], 'Frozen parent physical word differs'
    word = relabel(word,config['coordinate_permutation'])
    selected_sha=sha256(raw(word)).hexdigest()
    assert selected_sha == selection['word_sha256'], 'Selected relabeled physical word differs'
    assert result['roles']==selection['roles']
    checked=producer.graph(h);scalar=checked.verify();scalar['dense_global_support']=verify_dense(checked)
    assert scalar==json.loads((ROOT/f'research/final-frame/scalar-{h}.json').read_text())
    result.update(scalar=scalar,graph_configuration=config,
        parent_word_sha256=parent_sha,selected_word_sha256=selected_sha,
        coordinate_relabeling='PR74 exact bijection of sources, frames, scatter rows and output targets; ordinary and dirty columns independently replayed after relabeling',
        paid_clones=0,index_order='retired descending rank then slot; pending insertion order',
        future_unit_completion=True,carry_exchange_passes=3,carry_two_cycle_passes=3,
        pending_cost_uses_next_use_frame=True,three_cycle_passes=config['three_cycle_passes'],
        oracle_coordinate_pricing=config['oracle_coordinate_pricing'],node_order=config['node_order'],
        source_r10_sha256=provenance['engine']['original_source_manifest_sha256'])
    return result,word


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--h',type=int,choices=(23,25),required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--word',type=Path,required=True)
    args=parser.parse_args();result,word=compile_axis(args.h)
    raw=(json.dumps(word,separators=(',',':'))+'\n').encode()
    args.word.write_bytes(gzip.compress(raw,mtime=0) if args.word.suffix=='.gz' else raw)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)
