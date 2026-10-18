#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Portable bounded generator, source, owner and exact-moment checks.
Does not replace reproduce.py's full native/admission/outer replay.
"""
import gzip,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent

def need(ok,s):
 if not ok:raise ValueError(s)
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def main():
 need(not sys.flags.optimize,'assertions enabled')
 manifest=read(HERE/'PACKAGE-MANIFEST.json')
 actual={p.relative_to(HERE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.rglob('*') if p.is_file() and p!=HERE/'PACKAGE-MANIFEST.json'}
 need(actual==manifest,'complete package manifest')
 source=HERE/'source-inputs';pins=read(HERE/'DEPENDENCIES.json')['pr2857_files']
 for p in source.rglob('*'):
  if p.is_file():need(hashlib.sha256(p.read_bytes()).hexdigest()==pins[p.relative_to(source).as_posix()],'pinned source '+p.name)
 with tempfile.TemporaryDirectory(prefix='pair concentration ') as td:
  work=Path(td);candidate=work/'candidate';env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0');env.pop('PYTHONOPTIMIZE',None)
  def run(args):subprocess.run([sys.executable,'-B']+[str(x) for x in args],env=env,check=True)
  run([HERE/'generate.py',source,candidate])
  for name in ['FILL.json.gz','ORDER.json','DISPATCH.json','PROVIDERS.json','PROFILE.json','CONSTRUCTION.json']:need(read(candidate/name)==read(HERE/name),'full generated payload '+name)
  run([HERE/'independent.py',source,candidate,'--out',work/'owners.json'])
  run([HERE/'exact_moment.py',candidate,source,'--out',work/'moment.json'])
  moment=read(work/'moment.json');claim=read(HERE/'CLAIM.json');need(moment['kappa_rational']==claim['kappa'] and moment['gain_rational']==claim['gain'],'frozen exact claim')
  # A corrupted source must be rejected by the generator's fixed source pins.
  import shutil
  corrupt=work/'corrupt';shutil.copytree(source,corrupt);p=corrupt/'FILL.json.gz';p.write_bytes(p.read_bytes()+b'corrupt')
  r=subprocess.run([sys.executable,'-B',str(HERE/'generate.py'),str(corrupt),str(work/'bad-output')],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  need(r.returncode!=0 and b'source FILL.json.gz' in r.stderr,'source mutation rejected')
 print('PASS_BOUNDED_PAIR_CONCENTRATION_WITH_NEGATIVE_CONTROLS')
if __name__=='__main__':main()
