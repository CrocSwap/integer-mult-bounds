#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay exact PR2857 first, then regenerate and completely admit this derivative.

No network or edits to frozen sources. The two unchanged current provider chains
are reused from this run's authenticated PR2857 replay. Retained predecessors use
PR2857's explicit full-tree cache bindings. Codex-assisted.
"""
import argparse, hashlib, io, json, os, subprocess, sys, tarfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
HEAD='0b2e2537b368a0cade07ce3f71452ea018ebe394'
PREFIX='research/shared-kernel-repacking/'
def need(ok,s):
 if not ok:raise ValueError(s)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--jobs',type=int,choices=[1,2],default=2);a=ap.parse_args();a.repo=a.repo.resolve();a.work=a.work.resolve()
 need(not sys.flags.optimize,'assertions enabled');need(not a.work.exists(),'fresh external work');a.work.mkdir(parents=True);dep=a.work/'pr2857';dep.mkdir()
 raw=subprocess.check_output(['git','-C',str(a.repo),'archive',HEAD,PREFIX.rstrip('/')])
 with tarfile.open(fileobj=io.BytesIO(raw)) as ar:
  for m in ar:
   if m.isdir():continue
   need(m.isfile() and m.name.startswith(PREFIX),'regular pinned source');rel=Path(m.name[len(PREFIX):]);need(not rel.is_absolute() and '..' not in rel.parts,'safe path');p=dep/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(ar.extractfile(m).read())
 need({p.relative_to(dep).as_posix():sha(p) for p in dep.rglob('*') if p.is_file()}==json.loads((HERE/'DEPENDENCIES.json').read_text())['pr2857_files'],'entire PR2857 source tree')
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1');env.pop('PYTHONOPTIMIZE',None);stages=[]
 def run(name,args):
  argv=[sys.executable,'-B']+[str(x) for x in args];log=a.work/(name+'.log')
  with log.open('w') as f:r=subprocess.run(argv,env=env,stdout=f,stderr=subprocess.STDOUT)
  stages.append({'name':name,'argv':argv,'exit_code':r.returncode,'log_sha256':sha(log)});(a.work/'STAGES.json').write_text(json.dumps(stages,indent=2)+'\n');need(r.returncode==0,'failed '+name);print('PASS',name,flush=True)
 source=a.work/'pr2833';run('materialize-source',[dep/'materialize_source.py','--repo',a.repo,'--out',source])
 cache=a.work/'retained-cache';cache.mkdir()
 with tarfile.open(dep/'evidence/retained/NATIVE-CACHE.tar.gz') as ar:ar.extractall(cache,filter='data')
 baseline=a.work/'baseline';run('baseline-complete',[dep/'reproduce.py','--source',source,'--words',dep/'words','--fill',dep/'FILL.json.gz','--order',dep/'ORDER.json','--dispatch',dep/'DISPATCH.json','--retained-cache',cache,'--retained-receipt',dep/'evidence/retained/NATIVE-RECEIPT.json','--comparison-claim',dep/'sources/PR2848-CLAIM.json','--comparison-latest-claim',dep/'sources/PR2853-OUTER-CLAIM.json','--work',baseline,'--jobs',a.jobs])
 candidate=a.work/'candidate';run('generate',[HERE/'generate.py',dep,candidate]);run('independent-owners',[HERE/'independent.py',dep,candidate,'--out',candidate/'INDEPENDENT-OWNERS.json']);run('exact-moment',[HERE/'exact_moment.py',candidate,dep,'--out',candidate/'EXACT-MOMENT.json'])
 admitted=a.work/'admission';helpers=dep/'vendor/pr2839'
 run('complete-admission',[dep/'admit_shared_replica.py','--source',baseline/'source','--fill',candidate/'FILL.json.gz','--order',candidate/'ORDER.json','--dispatch',candidate/'DISPATCH.json','--native-cache',baseline/'native/native-cache','--native-receipt',baseline/'native/NATIVE-RECEIPT.json','--work',admitted,'--replica-helper-dir',helpers,'--reconstructor',helpers/'reconstruct_replica.py','--comparison-claim',dep/'sources/PR2848-CLAIM.json','--blocknorm-checker',helpers/'blocknorm_certificate.py','--source-profile','shared-four','--comparison-profile','pr2848','--jobs',a.jobs])
 run('final-binding',[HERE/'verify_release_binding.py','--admission',admitted,'--moment',candidate/'EXACT-MOMENT.json','--baseline',baseline/'RESULT.json'])
 print('PASS_COMPLETE_PAIRED_CONCENTRATION')
if __name__=='__main__':main()
