#!/usr/bin/env python3
"""Replay the PR36 scalar DAG with original envelopes and fixed I+J profiles.

The graph and profiler derive from icekylinx PR36/32; envelope replay and
source-growth CRT from Dominik Scholz PR35 (9c345a2). See SOURCE.json.
Substantial OpenAI GPT-6 Astra/Codex assistance. Apache-2.0.
"""
import gc
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from partial_swap.graph import graph, export
from partial_swap.positive import read

def original_labels(path):
    h,v,n,q,args,core,cover,roots,kind,active=read(str(path));full=(1<<h)-1
    additions=0;dependencies=0;sources=0
    for x in range(1,n):
        if not active[x]:continue
        assert not core[x]&~cover[x]
        if not args[2*x]:
            assert core[x]==cover[x] and core[x].bit_count()==3;sources+=1
            continue
        assert core[x].bit_count() in (1,2);additions+=1
        for y in args[2*x:2*x+2]:
            assert active[y] and y<x
            assert not core[x]&~core[y] and not cover[y]&~cover[x]
            dependencies+=1
    for x,total in zip(roots,kind):
        assert core[x].bit_count()==1
        if total:assert cover[x]==full
        else:assert (full^cover[x]).bit_count()==2
    assert sources==v and dependencies==2*additions
    return dict(h=h,exact_original_envelopes=additions,exact_dependency_inclusions=dependencies,
                output_frames=q,source_lines=v,reverse_complements_by_exact_duality=True)

def run():
    assert not sys.flags.optimize, 'Assertions must remain enabled'
    from verify import check_sources
    check_sources()
    with tempfile.TemporaryDirectory(prefix='copied-fixed-') as tmp:
        work = Path(tmp)
        exe = work/'profiles'
        subprocess.run([*shlex.split(os.environ.get('CXX', 'c++')), '-O3', '-std=c++17',
                        '-I', str(ROOT/'scripts/partial_swap'),
                        str(HERE/'rankone_profiles.cpp'), '-o', str(exe)], check=True)
        for h in (23, 25):
            circuit = graph(h)
            scalar = circuit.verify()
            dag = work/f'h{h}.bin'
            export(circuit, dag)
            circuit.support_in.cache_clear()
            del circuit
            gc.collect()
            labels = original_labels(dag)
            raw = subprocess.check_output([str(exe), str(dag), str(dag)+'.links'], text=True)
            original = json.loads(raw)
            assert dict(scalar=scalar, labels=labels, original=original) == json.loads(
                (HERE/f'producer-{h}.json').read_text()), f'producer {h}'
            actual = json.loads(Path(str(dag)+'.round3_rankone_certified_profiles.json').read_text())
            assert actual == json.loads((HERE/f'profiles-{h}.json').read_text()), f'profile {h}'
            print('PASS complete copied-fixed producer replay h', h, flush=True)


if __name__ == '__main__':
    run()
