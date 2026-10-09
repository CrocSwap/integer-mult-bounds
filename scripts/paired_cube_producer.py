#!/usr/bin/env python3
# Copyright 2026 icekylinx. Apache-2.0.
# Developed with GPT-6 Astra assistance; integrated with Codex assistance.
"""Regenerate and independently verify the selected round-nine complex input.

The frozen compatible matching is pinned, without relying on a nonunique
maximum-matching implementation. Standard-library Python; no giant raw DAG.
Copyright 2026 icekylinx, Apache-2.0; OpenAI GPT-6 Astra assistance, inherited PR117 notices.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from paired_cube.graph import Graph
from paired_cube.modules import restricted_pairs, restricted_triples, all_but_one, restricted_triples_from, restricted_pairs_from, pair_module_from, all_but_one_from, triple_module_from, merge_outputs
from paired_cube.closure import compile_closure
from paired_cube.gauges import select
from paired_cube.verify import verify

ROOT=Path(__file__).resolve().parents[1]

def regenerate(expected,work=None):
    if sys.flags.optimize:raise ValueError('Run without -O; finite assertions must remain enabled')
    def stage(message):print(message,file=sys.stderr,flush=True)
    reference=ROOT/'references/paired-cube/selected-module'
    pin=json.loads((reference/'SOURCE.json').read_text())
    inherited=ROOT/'references/three-stage-cover/pr117'
    source=json.loads((inherited/'SOURCE.json').read_text())
    assert source['commit']==pin['source_commit']
    for name,digest in source['files'].items():assert hashlib.sha256((inherited/name).read_bytes()).hexdigest()==digest
    assert hashlib.sha256((inherited/'dag.json.gz').read_bytes()).hexdigest()==pin['inherited_dag_sha256']
    frozen=reference/'matching-arcs.json'
    assert hashlib.sha256(frozen.read_bytes()).hexdigest()==pin['matching_arcs_sha256']
    stage('Regenerating paired-cube signed DAG from inherited PR117 restrictions')
    src=ROOT/'references/paired-cube/sources'
    srcpin=json.loads((src/'SOURCE.json').read_text())['files']
    for name,digest in srcpin.items():assert hashlib.sha256((src/name).read_bytes()).hexdigest()==digest
    _G=Graph(11,local=json.loads((src/'local_L1.json').read_text()));g=_G.finish(triple_module_from(src/'tmod_TB31_L1f8_5.9717259e-4.json',11),pair_module_from(src/'pmod_H56snap_w02_5.6251423e-4.json',10),all_but_one_from(src/'qmod_anneal_best01.json',9));g=merge_outputs(g,_G,'f8:00111100')
    g['matching_frames']='coordinate'
    binding={k:g[k] for k in ('inputs','labels','args','signs','roots','centers')}
    assert hashlib.sha256(json.dumps(binding,separators=(',',':')).encode()).hexdigest()==pin['graph_sha256']
    stage('Replaying frozen carrier matching and full binary intersections')
    baseline,witness=compile_closure(g,json.loads(frozen.read_text()))
    stage('Selecting chronological partial gauges and constructing signed physical M')
    actual,word=select(g,baseline,witness);actual=json.loads(json.dumps(actual))
    for key in ('numerical_complex_root','status','gauge_selection',
                'gauge_cost_rejections','gauge_trial_saving'):
        actual.pop(key,None)  # Discovery diagnostics, not exact proof inputs.
    assert actual==expected,'Regenerated selected complex input differs'
    stage('Independently checking signed scalar identity, K, physical word, intersections and target chains')
    checks=verify(g,baseline,witness,word,actual)
    result=dict(source_pin_verified=True,regenerated_from_source=True,certificate_equal=True,selected=actual,checks=checks)
    if work:
        work.mkdir(parents=True,exist_ok=True)
        for name,data in [('graph.json',g),('frames.json',witness),('selection.json',word)]:
            (work/name).write_text(json.dumps(data,separators=(',',':'))+'\n')
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--certificate',type=Path,default=ROOT/'certificates/paired-cube-complex-input.json')
    p.add_argument('--work-dir',type=Path)
    p.add_argument('--output',type=Path)
    a=p.parse_args();result=regenerate(json.loads(a.certificate.read_text()),a.work_dir)
    text=json.dumps(result,indent=2)+'\n'
    if a.output:a.output.write_text(text)
    else:print(text,end='')

if __name__=='__main__':main()
