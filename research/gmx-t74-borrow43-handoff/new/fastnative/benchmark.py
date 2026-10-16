#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Alternating fresh complete native runs; same fixture and no result caching."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import HERE, need, source_bytes
from compare import compare

def main():
 need(__debug__, 'assertions must remain enabled')
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--pairs',type=int,default=3);p.add_argument('--provider',choices=('base','extra'),default='base');p.add_argument('--work',type=Path,required=True);a=p.parse_args()
 need(a.pairs>=1 and not a.work.exists(),'positive pairs and fresh work required')
 source_bytes(HERE/'vendor');word=HERE/f'fixtures/WORD-{a.provider}.json.gz'
 pins=json.loads((HERE/'PINS.json').read_text())
 need(hashlib.sha256(word.read_bytes()).hexdigest()==pins[word.relative_to(HERE).as_posix()],'fixture digest')
 a.work.mkdir(parents=True)
 samples=[];comparisons=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1');env.pop('PYTHONOPTIMIZE',None)
 for i in range(a.pairs):
  paths={}
  for engine in (('reference','sparse') if i%2==0 else ('sparse','reference')):
   out=a.work/f'pair{i}-{engine}';cmd=[sys.executable,'-I','-B',str(HERE/'run_native.py'),str(word),str(out),'--engine',engine]
   start=time.monotonic()
   with (a.work/f'pair{i}-{engine}.log').open('w') as log:r=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=900)
   elapsed=time.monotonic()-start;need(r.returncode==0,'native benchmark run failed '+str(out))
   receipt=json.loads((out/'RESULT.json').read_text());need(receipt['status']=='PASS_COMPLETE_T74_NATIVE_REPLAY','native receipt')
   samples.append({'pair':i,'engine':engine,'wall_seconds':elapsed,'steps':receipt['steps']});paths[engine]=out/'native/local'
   (a.work/'SAMPLES.json').write_text(json.dumps(samples,indent=2)+'\n');print('PASS sample',i,engine,round(elapsed,3),flush=True)
  result=compare(paths['reference'],paths['sparse']);comparisons.append(result);print(result['status'],i,flush=True)
 medians={e:statistics.median(s['wall_seconds'] for s in samples if s['engine']==e) for e in ('reference','sparse')}
 result={'status':'PASS_COMPLETE_T74_NATIVE_BENCHMARK','provider':a.provider,'pairs':a.pairs,'samples':samples,'comparisons':comparisons,'median_wall_seconds':medians,'speedup':medians['reference']/medians['sparse'],'python':platform.python_version(),'platform':platform.platform(),'cpu_count':os.cpu_count(),'input_sha256':hashlib.sha256(word.read_bytes()).hexdigest(),'scope':'Fresh sequential subprocesses; all five stages and independent warp recipe check run each time. No cached result reuse. Shared host; OS caches not flushed. Timings descriptive, not a correctness threshold.'}
 (a.work/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],result['speedup'],flush=True)
if __name__=='__main__':main()
