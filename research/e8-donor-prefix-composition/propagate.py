"""Apply unchanged native416 propagation with418's exact relation transport.
Source01ca is reconstructed separately; this step has no search or new scalar code.
"""
from pathlib import Path
from fractions import Fraction as Q
import hashlib,importlib.util,json,os,subprocess,sys
if not __debug__:raise RuntimeError('Assertions required')
sys.dont_write_bytecode=True
import propagation_source as T
SOURCE='01cae52711bb22f4e3255b0b9e96053a90b76aeaa6799bda9f0fb6aea3618112'
EXPECTED='eedfb5796c8b2b5b202a1e7fee2785b6b23cd1f017794d3f8ddb19c87bd0a384'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
def run(package,source,fresh_out):
 package=Path(package).resolve();source=Path(source).resolve();out=Path(fresh_out).absolute()
 assert sha(source)==SOURCE and not out.exists()and not out.is_symlink()and not out.resolve().is_relative_to(package)
 for p in[out]+list(out.parents):assert not p.is_symlink()
 T.decode(package);out.mkdir(parents=True)
 native=T.restore(package,out/'native');before=T.check(package,native)
 spec=importlib.util.spec_from_file_location('_native_common',native/'common.py');C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
 c=read(source);rows=C.replay(c);original=read(native/'ORIGINAL892.json');selection=read(native/'SELECTION.json')
 def residual(plan):
  pp=plan['pivots'][0];p=pp['pivot'];result={}
  for t in range(c['v'],2*c['v']):
   q=rows[t].get(p,Q(0))+sum(Q(a)*rows[t].get(int(d),Q(0))for d,a in pp['coefficients'].items())
   if q:result[t]=str(q)
  return result
 rejected=residual(original);assert rejected=={133:'1/2',149:'1/2'}
 assert all(not residual(p)for p in selection)
 # The old direct892 donor1010 is already gauged. The transported literal
 # relation is checked against every exact response coordinate before execution.
 assert 1010 in dict(c['ext'])and '1010'in original['pivots'][0]['coefficients']
 assert all('1010'not in p['pivots'][0]['coefficients']for p in selection)
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None)
 command=[sys.executable,'-B',str(native/'construct.py'),str(source),str(native/'SELECTION.json'),str(out/'word'),'--source-sha256',SOURCE,'--expected-sha256',EXPECTED]
 with(out/'construct.log').open('w')as log:subprocess.run(command,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 r=read(out/'word/RECEIPT.json');assert r['candidate_sha256']==EXPECTED and sha(out/'word/candidate.json')==EXPECTED
 assert r['gauges']==208 and r['new_gates']==25 and len(r['changed_original_frames'])==5
 assert all(g['part']=='A'for g in r['changed_original_frames'])and len(r['adverse_controls'])==6 and all(g['rejected']for g in r['adverse_controls'])
 assert r['all1021raw_and_snapshot_columns_right_multiplied_by_literal_prepended_word']and r['all_gauged_response_columns_zero']
 assert {int(k):v for k,v in r['local_delta'].items()}=={1:8,2:-3,3:1,4:-2,7:1,8:-1}
 assert before==T.check(package,native)and sha(source)==SOURCE
 (out/'candidate.json').write_bytes((out/'word/candidate.json').read_bytes())
 r.update(status='PASS_UNCHANGED416_CONSTRUCTOR_WITH418_RELATION_ON_OWN_THREE_PREFIXES',native_source=before,rejected_direct892_residual=rejected,corrected_relations_all_response_coordinates_zero=True,packing_sha256=sha(native/'PATTERNS.json'),scope='Exact finite source reconstruction and full response/snapshot right multiplication only. Fresh208-token restoration, actual paid primitives, propagated frame ledgers, Gaussian phases, native bank decode/invoice and supplier pricing remain separate mandatory checks. No inherited sixth-grid or unconditional theorem claim.')
 (out/'RECONSTRUCTION.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n');return out/'candidate.json',r
if __name__=='__main__':
 assert len(sys.argv)==4,'PACKAGE SOURCE01CA FRESH_OUT';candidate,r=run(*sys.argv[1:]);print(r['status'],r['candidate_sha256'])
