"""Verify this new composition only; no network, search, or unchanged PR pipelines."""
import argparse,concurrent.futures,gzip,hashlib,json,os,subprocess,sys,time
from pathlib import Path
assert __debug__, 'Do not disable assertions'
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);a=ap.parse_args();out=a.output.resolve();assert not out.exists() and not out.is_relative_to(ROOT);out.mkdir(parents=True)
manifest=json.loads((ROOT/'MANIFEST.json').read_text());actual={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.rglob('*') if p.is_file() and p.name!='MANIFEST.json'}
# Include inherited files with the same basename; exclude only our own manifest.
actual={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.rglob('*') if p.is_file() and p!=ROOT/'MANIFEST.json'}
assert actual==manifest['files'],'Manifest mismatch'
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',COMPLEX_PUBLIC=str(ROOT/'public'),OUTPUT_SHEAR_BASE=str(ROOT/'public/378/source/research/e8-complex-far-retiming'));env.pop('PYTHONOPTIMIZE',None)
for key in ['COMPLEX_CERT','COMPLEX_OUTPUT','COMPLEX_SINK_AUDIT','COMPLEX_PREWHITE','COMPLEX_BASELINE_OUTPUT']:env.pop(key,None)
checks=[]
def run(name,cmd,extra=None):
 e=dict(env);e.update(extra or {});start=time.monotonic();log=out/(name+'.log');print(name,flush=True)
 with log.open('w',encoding='utf-8') as f:r=subprocess.run([str(x) for x in cmd],env=e,stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0,(name,r.returncode,str(log));checks.append({'name':name,'seconds':time.monotonic()-start,'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()})
def py(name,file,*args,extra=None):run(name,[sys.executable,'-B',ROOT/'code'/file,*args],extra)
try:
 py('prefix-reconstruction','bit-complex-output-shear-pack.py',out/'reconstructed')
 cp=out/'reconstructed/gcert1-e8-r783-output-shear-pack.json.gz'
 assert gzip.decompress(cp.read_bytes())==gzip.decompress((ROOT/'data/prefix18.json.gz').read_bytes())
 far={'COMPLEX_OUTPUT':str(out/'far')};candidate={'COMPLEX_CERT':str(cp),'COMPLEX_OUTPUT':str(out/'complex'),'COMPLEX_BASELINE_OUTPUT':str(out/'far')}
 env.pop('COMPLEX_CERT',None)
 py('changed-far-component','complex-compose.py',extra=far)
 py('far-phase-basis','complex-clifford.py',extra=far)
 py('new-prefix-component','complex-compose.py',extra=candidate)
 py('new-prefix-phases','complex-clifford-delta.py',extra=candidate)
 prefix=json.loads((out/'complex/RESULT.json').read_text());assert prefix['coarse']=='100119912566839/100000000000000000'
 hetero={'COMPLEX_CERT':str(cp),'COMPLEX_OUTPUT':str(out/'hetero'),'COMPLEX_SINK_AUDIT':str(ROOT/'data/sink-audit.json'),'COMPLEX_PREWHITE':str(ROOT/'data/prewhite.json')}
 py('heterogeneous-local','complex-hetero-compose.py',extra=hetero)
 py('heterogeneous-endpoint-phases','complex-bank-phase.py',extra=hetero)
 binary=out/('heterobanks.exe' if os.name=='nt' else 'heterobanks')
 run('compile-banks',[env.get('CXX','g++'),'-O2','-std=c++17','-I'+str(ROOT/'public/381/source/research/e8-nine-stage-kappa/code/bit/checkers'),ROOT/'code/root-heterobanks.cpp','-o',binary])
 run('literal-bank-geometry',[binary,cp.with_suffix(''),out/'HETEROBANKS.json'])
 py('independent-bank-review','bit-heterobank-review.py','--banks',out/'HETEROBANKS.json','--certificate',cp,'--sink-audit',ROOT/'data/sink-audit.json','--output',out/'BANK-REVIEW.json')
 py('global-template','root-global.py',extra={**hetero,'HETEROBANKS':str(out/'HETEROBANKS.json'),'BANK_PHASE':str(out/'hetero/BANK-ENDPOINT-PHASE.json'),'BANK_REVIEW':str(out/'BANK-REVIEW.json')})
 cx=json.loads((out/'hetero/RESULT.json').read_text());assert cx['coarse']=='40048866680681/40000000000000000'
 py('new-bit-composition','bit-compose-replay.py',out/'bit','--pr381',ROOT/'public/381/source/research/e8-nine-stage-kappa','--reuse',ROOT/'public/376/source/research/e8-bit-helper-reuse','--complex',cx['coarse'])
 bit=json.loads((out/'bit/BIT-COMPOSITION-RECEIPT.json').read_text());price=bit['pricing'];assert price['kappa']=='125027527861191/125000000000000000'
 result={'status':'PASS_NEW_E8_PREFIX_RESTORATION_CONDITIONAL_COMPOSITION','kappa':price['kappa'],'kappa_decimal':'0.001000220222889528','bit_coarse':price['bit_coarse'],'complex_coarse':cx['coarse'],'checks':checks,'manifest_sha256':hashlib.sha256((ROOT/'MANIFEST.json').read_bytes()).hexdigest(),'scope':'Finite conditional construction, not a Lean proof or unconditional multiplication theorem. See PROOF.md and README.md.'}
 (out/'RESULT.json').write_text(json.dumps(result,indent=2));print(result['status'],result['kappa'],flush=True)
except BaseException as e:
 (out/'FAILURE.json').write_text(json.dumps({'error':str(e),'completed':checks},indent=2));raise
