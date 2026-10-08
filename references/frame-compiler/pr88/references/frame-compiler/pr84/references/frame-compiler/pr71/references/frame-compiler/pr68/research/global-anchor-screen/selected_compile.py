#!/usr/bin/env python3
"""Regenerate the selected global-anchor words from frozen source.

PR57/PR60 compiler and PR62 graph credits are retained in PROOF.md and SOURCE.
Prepared with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import gzip
import importlib.util
import json
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path[:0]=[str(ROOT/'research/pair-assembly'),str(ROOT/'scripts/experiments')]
from pair_graph import graph
from binary_frame_replay import replay

def compile_axis(h,destination):
    manifest=json.loads((HERE/'selected-manifest.json').read_text())
    frozen=HERE/'compiler-frozen.py'
    assert sha256(frozen.read_bytes()).hexdigest()==manifest['files']['compiler-frozen.py']
    assert sha256((ROOT/'research/pair-assembly/pair_graph.py').read_bytes()).hexdigest()==manifest['graph_sha256']
    spec=importlib.util.spec_from_file_location('global_anchor_frozen',frozen)
    compiler=importlib.util.module_from_spec(spec);spec.loader.exec_module(compiler)
    compiler.graph=graph
    result,word=compiler.compile_(h,matching=True,reclaim=True,dirty=True,rank_first=True,reverse_ties=h==25)
    result.pop('seconds')
    result['mode']['reverse_ties']=h==25
    raw=(json.dumps(word,separators=(',',':'))+'\n').encode()
    assert sha256(raw).hexdigest()==manifest['word_sha256'][str(h)]
    destination.mkdir(parents=True,exist_ok=True)
    target=destination/f'word-{h}.json.gz'
    target.write_bytes(gzip.compress(raw,mtime=0))
    receipt=replay(target)
    (destination/f'receipt-{h}.json').write_text(json.dumps(dict(compiled=result,replay=receipt),indent=2)+'\n')
    print(f'h={h}: identical selected word and independent dirty replay PASS',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--h',type=int,choices=(23,25),required=True);p.add_argument('--work-dir',type=Path,required=True)
    a=p.parse_args();compile_axis(a.h,a.work_dir)
