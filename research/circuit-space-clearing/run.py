#!/usr/bin/env python3
"""Compile a bounded circuit-space clearing experiment on PR67/PR62.

Actual profile-cost oracle: Rohan Arun PR67; compiler lineage PR57/60/63;
graph: Avi Eisenberg PR62. Substantial OpenAI GPT-6 Astra/Codex assistance.
All old notices remain applicable. Apache-2.0. No full-theorem claim.
"""
from pathlib import Path
from hashlib import sha256
import argparse,gzip,importlib.util,json,os,shlex,subprocess,sys
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path[:0]=[str(ROOT/'scripts/experiments'),str(ROOT/'research/pair-assembly')]
from pair_graph import graph
import compiler

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--h',type=int,choices=(23,25),required=True);p.add_argument('--mode',choices=('baseline','pairs','full'),default='pairs');p.add_argument('--work-dir',type=Path,required=True);a=p.parse_args()
 a.work_dir.mkdir(parents=True,exist_ok=True)
 oracle=a.work_dir/'profile-oracle'
 subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17','-I',str(ROOT/'references/frame-compiler/pr48/scripts/partial_swap'),str(HERE/'profile_oracle.cpp'),'-o',str(oracle)],check=True)
 compiler.graph=graph;compiler.oracles=[];compiler.ORACLE_EXE=str(oracle);compiler.ORACLE_INPUT=str(a.work_dir/f'oracle-{a.h}.bin');compiler.SEARCH_MODE=a.mode
 try:
  result,word=compiler.compile_(a.h,matching=True,reclaim=True,dirty=True)
 finally:
  for proc in compiler.oracles:
   proc.stdin.close();assert proc.wait()==0
 raw=(json.dumps(word,separators=(',',':'))+'\n').encode()
 (a.work_dir/f'word-{a.h}.json.gz').write_bytes(gzip.compress(raw,mtime=0))
 (a.work_dir/f'result-{a.h}.json').write_text(json.dumps(dict(mode=a.mode,compiled=result,word_sha256=sha256(raw).hexdigest()),indent=2)+'\n')
 print(json.dumps(result,indent=2),flush=True)
