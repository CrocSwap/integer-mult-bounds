#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fresh unchanged T488 literal reconstruction, retimed bill and independent audit."""
from pathlib import Path
from collections import Counter
import argparse,gzip,hashlib,json,os,subprocess,sys,time
HERE=Path(__file__).resolve().parent

def need(x,m):
 if not x:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def snapshot():
 roots=[HERE/'upstream',HERE/'source',HERE/'native']
 files=[p for root in roots for p in root.rglob('*') if p.is_file()]
 files += [p for p in HERE.iterdir() if p.is_file()]
 return {str(p.relative_to(HERE)):sha(p) for p in files}

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--fresh-native-cache',type=Path,help='Optional fresh full-replay native-cache; match decoded canonical payloads before owner execution');a=ap.parse_args()
 need(__debug__ and not sys.flags.optimize,'Enabled assertions required before owner replay')
 out=a.out.resolve();need(not out.exists(),'Fresh output directory required');need(out!=HERE,'Output must not equal package')
 for name in ('upstream','source','native'):need(HERE/name not in out.parents and out!=HERE/name,'Output inside frozen input tree')
 before=snapshot();der=read(HERE/'DERIVATION.json');binding=read(HERE/'NATIVE-BINDING.json')
 for name,key in [('independent_literal.py','derived_script_sha256'),('upstream/independent_literal.py','predecessor_script_sha256')]:need(sha(HERE/name)==der[key],'auditor source '+name)
 for rel,digest in read(HERE/'upstream/ARTIFACTS.json').items():need(sha(HERE/'upstream'/rel)==digest,'upstream artifact '+rel)
 for rel,digest in read(HERE/'SOURCE-CLOSURE.json')['files'].items():need(sha(HERE/'source'/rel)==digest,'closure source '+rel)
 native={};fresh_matches={}
 for tag in ('base','extra'):
  p=HERE/'native'/f'checked-{tag}'/'CANONICAL-WORD.json.gz';need(sha(p)==der['native_pins'][tag],'native pin '+tag);payload=gzip.decompress(p.read_bytes());need(hashlib.sha256(payload).hexdigest()==binding[tag]['payload_sha256'],'native decoded payload '+tag);native[tag]=json.loads(payload)
  if a.fresh_native_cache:
   matches=[f for f in a.fresh_native_cache.resolve().glob('*/local/CANONICAL-WORD.json.gz') if gzip.decompress(f.read_bytes())==payload];need(len(matches)==1,'unique fresh canonical payload '+tag);fresh_matches[tag]=str(matches[0])
 oldlocal=read(HERE/'upstream/CANDIDATE.json')['local_profile'];oldlocal={int(k):v for k,v in oldlocal.items()};locals=[{int(k):v for k,v in native[t]['local_profile'].items()} for t in ('base','extra')];need(locals[0]==locals[1], 'same retimed bill');newlocal=locals[0];need(newlocal=={1:2437,2:724,3:226,4:102,5:20,8:8},'retimed local bill')
 out.mkdir(parents=True);(out/'tmp').mkdir();env=os.environ.copy();env.update(OWNER_SOURCE_REPO=str(HERE/'source'),PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(out/'tmp'));start=time.monotonic()
 def run(script,args,name):
  with (out/name).open('w') as log:subprocess.run([sys.executable,'-B',str(script),*args],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 literal=out/'literal';run(HERE/'upstream/portable_expand.py',['--out',str(literal)],'materialize.log')
 generated=read(literal/'PROFILE.json');need(sha(literal/'PROFILE.json')==read(HERE/'upstream/EXPECTED.json')['literal_files']['PROFILE.json'],'fresh original profile authentication')
 (out/'ORIGINAL-PROFILE.json').write_bytes((literal/'PROFILE.json').read_bytes());calls=len(read(literal/'ORDER.json'));need(calls==4392,'T488 call count')
 total=Counter({int(k):v for k,v in generated.items()})
 for rank in oldlocal.keys()|newlocal.keys():total[rank]+=calls*(newlocal.get(rank,0)-oldlocal.get(rank,0))
 need(all(v>0 for v in total.values()),'positive retimed histogram');(literal/'PROFILE.json').write_text(json.dumps(dict(sorted(total.items())),indent=2)+'\n')
 env.update(OWNER_LITERAL_DIR=str(literal),OWNER_NATIVE_DIR=str(HERE/'native'),OWNER_AUDIT_OUTPUT=str(out/'RESULT.json'))
 run(HERE/'independent_literal.py',[],'independent-audit.log');result=read(out/'RESULT.json');need(result['profile']=={str(k):v for k,v in sorted(total.items())},'independent fresh histogram matches generated bill delta');need(len(result['controls'])==5,'five semantic rejection controls')
 run(HERE/'upstream/test_owner_guards.py',[],'owner-guards.log');need('PASS_OWNER_GUARDS 14' in (out/'owner-guards.log').read_text(),'14 predecessor guards')
 need(snapshot()==before,'package input drift')
 receipt={'status':'PASS_FRESH_T488_RETIMED_LITERAL_OWNER_AUDIT','seconds':time.monotonic()-start,'python':sys.version,'fresh_literal_reconstruction':True,'fresh_independent_audit':True,'roles':result['roles'],'calls':calls,'replicas':result['replicas'],'physical':result['physical'],'profile':result['profile'],'idle':result['idle'],'local_bill':newlocal,'controls':result['controls'],'predecessor_guard_count':14,'fresh_native_payload_matches':fresh_matches,'native_payload_pins':{t:binding[t]['payload_sha256'] for t in binding},'package_inputs_unchanged':True,'scope':'Bounded owner/interface audit derives windows,families,prefixes,idle and full profile from freshly generated literal rows and pinned retimed frames. Separate native/operator/full admission remains required.'}
 (out/'RUN.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
