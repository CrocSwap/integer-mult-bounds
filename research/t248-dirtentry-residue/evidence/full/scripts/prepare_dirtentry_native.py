#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound PR2833 native preparation; derived from PR2839's preparer.

Credit: Tekalign (@tekuuu), Jeremy Kothe (@jeremykothe2) and source notices.
This composition driver uses unchanged source/validators and four fresh chains.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse, hashlib, gzip, json, os, platform, shutil, subprocess, sys, tarfile, threading, time
SOURCE_SHA='c8ec4d1b7be08d2ad30730a07392ad9cb6d0222f2c35bef43c9a80a39b16e41f'
SOURCE_COMMIT='pr2833-dirtentry'
PARENT_SHA='e0eefc96567fbb45e19e6de0ca295381dbe0e686c08ddc783639b065c7c791d4'
def need(x,m):
 if not x: raise RuntimeError(m)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def write(p,v): p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
def tree(p,exclude=()):
 d={}
 for f in sorted(p.rglob('*')):
  need(not f.is_symlink(),'source symlink')
  if f.is_file() and f.relative_to(p).as_posix() not in exclude:d[f.relative_to(p).as_posix()]=sha(f)
 return d
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--jobs',type=int,default=4);a=ap.parse_args()
 need(not sys.flags.optimize and 1<=a.jobs<=4,'enabled assertions and max4 jobs')
 sys.dont_write_bytecode=True
 source=a.source.resolve();work=a.work.resolve()
 need(sha(source/'MANIFEST.json')==SOURCE_SHA,'exact PR2833 manifest')
 pins=read(source/'MANIFEST.json');need(len(pins)==541 and tree(source,('MANIFEST.json',))==pins,'complete PR2833 source')
 need(not work.exists() and not work.is_relative_to(source),'fresh external work');work.mkdir(parents=True)
 cache=work/'native-cache';cache.mkdir();old=source/'vendor/pr1297'
 need(sha(old/'MANIFEST.json')==PARENT_SHA,'retained parent pin')
 words={tag:source/('new/borrow/words/BORROW-WORD-43'+tag+'.json.gz') for tag in ('base','extra')}
 retained={tag:old/name for tag,name in [('base','gauge44-word.json.gz'),('extra','extra-word.json.gz')]}
 layout=work/'retained-layout';layout.mkdir()
 with tarfile.open(old/'upstream-layout.tar.gz') as archive:
  need(all(m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts for m in archive.getmembers()),'safe retained archive')
  archive.extractall(layout,filter='data')
 rd=layout/'joint1148-round45/source/research/k8-eight-ends/replay_native.py';need(rd.is_file(),'retained native driver')
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',BW_IDLE='0')
 for k in ['PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_DISCOVER','WITNESS_RECORD']:env.pop(k,None)
 stages=[];mutex=threading.Lock();start=time.monotonic()
 def run(name,script,*args):
  before=time.monotonic();log=work/(name+'.log');cmd=[sys.executable,'-B',str(script),*map(str,args)]
  with log.open('w') as f:r=subprocess.run(cmd,cwd=work,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT)
  with mutex:
   stages.append(dict(name=name,exit_code=r.returncode,command=cmd,script_sha256=sha(script),log_sha256=sha(log),seconds=time.monotonic()-before));write(work/'STAGES.json',stages)
  need(r.returncode==0,'failed '+name+'; '+str(log));print('PASS',name,flush=True)
 def fresh(tag):
  isret=tag.startswith('retained-');word=retained[tag[9:]] if isret else words[tag];entry=cache/sha(word)
  if isret:run('native-'+tag,rd,word,entry)
  else:
   fw=work/('fast-'+tag);run('native-'+tag,source/'new/fastnative/run_native.py',word,fw)
   need(read(fw/'RESULT.json')['status']=='PASS_COMPLETE_T74_NATIVE_REPLAY','complete sparse native result');shutil.copytree(fw/'native',entry)
  need(read(entry/'local/FULL-WORD.json.gz')==read(word),'complete native word identity')
  s=read(entry/'STEPS.json');need([v['step'] for v in s]==['native','ledgers','local-replay','wrappers','phases'] and all(v['exit_code']==0 for v in s),'five native stages')
  write(entry/'CACHE.json',dict(word_sha256=sha(word),files=tree(entry)))
 with ThreadPoolExecutor(max_workers=a.jobs) as pool:list(pool.map(fresh,['base','extra','retained-base','retained-extra']))
 run('retained-parent',old/'verify.py','--work',work/'retained-parent','--base-native-from',cache/sha(retained['base']),'--extra-native-from',cache/sha(retained['extra']))
 parent=read(work/'retained-parent/RESULT.json');pstages=read(work/'retained-parent/STAGES.json')
 need(len(pstages)==16 and all(v['exit_code']==0 for v in pstages),'retained 16 stages')
 need(parent['status']=='PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION' and parent['kappa']==read(old/'CLAIM.json')['kappa'],'retained exact admission')
 receipts=cache/'_receipts'/PARENT_SHA;receipts.mkdir(parents=True)
 for n in ['RESULT.json','STAGES.json']:shutil.copy2(work/'retained-parent'/n,receipts/n)
 write(receipts/'RECEIPT.json',dict(schema='parent-receipt/1',vendor_manifest_sha256=PARENT_SHA,claim_sha256=sha(old/'CLAIM.json'),words={t:sha(w) for t,w in retained.items()},files={n:sha(receipts/n) for n in ['RESULT.json','STAGES.json']}))
 need(tree(source,('MANIFEST.json',))==pins,'unchanged full source')
 receipt=dict(status='PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE',source_commit=SOURCE_COMMIT,manifest_sha256=SOURCE_SHA,providers={t:dict(word_sha256=sha(w),complete_native_files=tree(cache/sha(w),('CACHE.json',))) for t,w in words.items()},retained_parent_receipt_sha256=sha(receipts/'RECEIPT.json'),cache_files=tree(cache),fresh_current_provider_count=2,fresh_retained_native_count=2,reused_retained_native_count=0,fresh_retained_parent=True,reused_retained_parent=False,retained_reuse_receipt_sha256=None)
 write(work/'NATIVE-RECEIPT.json',receipt)
 write(work/'RESULT.json',dict(status='PASS_PR2833_FRESH_NATIVE_PREPARATION',native_receipt_sha256=sha(work/'NATIVE-RECEIPT.json'),source_manifest_sha256=SOURCE_SHA,preparer_sha256=sha(Path(__file__)),source_file_count=541,stages=stages,seconds=time.monotonic()-start,python=platform.python_version(),scope='Four fresh native chains plus retained parent; no replica/outer admission yet.'))
 print('PASS_PR2833_FRESH_NATIVE_PREPARATION',flush=True)
if __name__=='__main__':main()
