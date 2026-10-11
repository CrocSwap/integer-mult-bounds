#!/usr/bin/env python3
"""Distinct audit of a completed immutable pointwise/native package replay.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
import sys
if not __debug__: raise SystemExit('Assertions required; refusing optimization')
sys.dont_write_bytecode=True
import argparse,hashlib,importlib.util,json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--proof',type=Path,required=True);p.add_argument('--package',type=Path,default=ROOT.parent/'w3-p10-pointwise-native');p.add_argument('--output',type=Path,required=True);p.add_argument('--cxx',default='c++');a=p.parse_args();P=a.proof.resolve();O=a.output.resolve();package=a.package.resolve()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_text())
manifest='eb7a1971163098dfb67b6f3c3b5a40e834c38b628e21d87c4a44c864e7576b64'
assert sha(package/'MANIFEST.json')==manifest
s=importlib.util.spec_from_file_location('construction_integrity',package/'verify.py');vmod=importlib.util.module_from_spec(s);s.loader.exec_module(vmod);assert vmod.integrity()==manifest
v=read(P/'VERIFICATION.json');cert=read(P/'CERTIFICATE.json');assert not(P/'FAILURE.json').exists() and v['inputs_unchanged'] and v['manifest_sha256']==manifest
assert [r['stage']for r in v['fresh_stages']]==vmod.STAGES
assert cert['word_sha256']==sha(P/'candidate/COHORT249-RECORDS.bin')=='05df0a39669bb077a9a2fa527904023a5a9da18cf644e06429d44f2a7ea92603'
assert cert['kappa']==v['kappa']=='198348202417928396741897/250000000000000000000000000'
for name,h in cert['fresh_receipt_hashes'].items():assert sha(P/name)==h
assert not O.exists() and not O.is_relative_to(P) and not O.is_relative_to(package);O.mkdir();(O/'stages').mkdir();(O/'logs').mkdir();py=[sys.executable,'-B'];stages=[]
inputs={str(q):sha(q)for q in P.rglob('*')if q.is_file()};engines={q.relative_to(ROOT).as_posix():sha(q)for q in [Path(__file__),*sorted((ROOT/'code').glob('*'))]if q.is_file()}
def run(name,args):
 with(O/'logs'/(name+'.log')).open('w')as f:subprocess.run(list(map(str,args)),stdout=f,stderr=subprocess.STDOUT,check=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
 stages.append(name);print('PASS',name,flush=True)
run('independent-tiling',py+[ROOT/'code/tiling.py','--proof',P,'--output',O/'stages/bank-tiling.json'])
run('compile-distinct-audit',[a.cxx,'-O2','-std=c++17','-I',package/'vendor/native',ROOT/'code/audit.cpp','-o',O/'audit'])
run('literal-word',[O/'audit',P/'candidate',O,O,'43'])
run('modular-minors',py+[ROOT/'code/minors.py','--proof',P,'--output',O])
run('closed-form-assembly',py+[ROOT/'code/assembly.py',P,O/'ASSEMBLY-AUDIT.json'])
assert inputs=={str(q):sha(q)for q in P.rglob('*')if q.is_file()} and vmod.integrity()==manifest
r=read(O/'RESULT.json');assert r['omission_wrong_rows']==480 and r['forward_wrong_rows']==r['inverse_wrong_rows']==0
assert read(O/'ASSEMBLY-AUDIT.json')['kappa']==cert['kappa']
r.update(kappa=cert['kappa'],manifest_sha256=manifest,word_sha256=cert['word_sha256'],stages=stages,inputs_unchanged=True,input_hashes=inputs,engine_hashes=engines,receipt_hashes={n:sha(O/n)for n in ['RESULT.json','MINOR-AUDIT.json','ASSEMBLY-AUDIT.json','stages/bank-tiling.json']})
(O/'BOUND-RESULT.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n');print('PASS_INDEPENDENT_WORD_AND_ASSEMBLY',flush=True)
