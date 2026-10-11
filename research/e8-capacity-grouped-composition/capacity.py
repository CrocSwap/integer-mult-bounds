"""Apply pinned PR421 capacity construction and PR422/421 selections to frozen208.
No search or scalar compiler is implemented here. All source leaves retain native bytes.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import hashlib,importlib.util,json,os,subprocess,sys
if not __debug__:raise RuntimeError('Assertions required')
sys.dont_write_bytecode=True
import capacity_source as T
SOURCE='eedfb5796c8b2b5b202a1e7fee2785b6b23cd1f017794d3f8ddb19c87bd0a384'
EXPECTED='9b0664bc1f8eed0fda952f6f3f1f4636b527fba35a3735cbff9a5a45384c660c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
def run(package,source,fresh_out):
 package=Path(package).resolve();source=Path(source).resolve();out=Path(fresh_out).absolute()
 assert sha(source)==SOURCE and not out.exists()and not out.is_symlink()and not out.resolve().is_relative_to(package)
 for p in[out]+list(out.parents):assert not p.is_symlink()
 meta=T.metadata(package);T.decode(package);packing=package/meta['packing']['path']
 assert packing.is_file()and not packing.is_symlink()and sha(packing)==meta['packing']['sha256']
 out.mkdir(parents=True);native=T.restore(package,out/'native');before=T.check(package,native)
 spec=importlib.util.spec_from_file_location('_native_capacity_common',native/'common.py');C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
 config=read(native/'CONFIG422.json');assert config['replicas']==64 and config['deficit_per_replica']==312
 c=read(source);rows=C.replay(c);selection=read(native/'SELECTION422.json')+read(native/'SELECTION421.json')
 pivots=[p['pivot']for plan in selection for p in plan['pivots']];assert pivots==[766,917,627,948,672,435,367]
 assert all(p not in dict(c['ext'])and c['start'][p]==0 for p in pivots)
 for plan in selection:
  for p in plan['pivots']:
   assert all(rows[t].get(p['pivot'],Q(0))+sum(Q(a)*rows[t].get(int(d),Q(0))for d,a in p['coefficients'].items())==0 for t in range(c['v'],2*c['v']))
 (out/'SELECTION.json').write_text(json.dumps(selection,sort_keys=True,indent=2)+'\n')
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None)
 command=[sys.executable,'-B',str(native/'construct.py'),str(source),str(out/'SELECTION.json'),str(out/'word'),'--source-sha256',SOURCE,'--expected-sha256',EXPECTED]
 with(out/'construct.log').open('w')as log:subprocess.run(command,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 r=read(out/'word/RECEIPT.json');assert r['candidate_sha256']==EXPECTED and sha(out/'word/candidate.json')==EXPECTED
 assert r['gauges']==215 and r['new_gates']==27 and len(r['changed_original_frames'])==6
 assert all(g['part']=='A'for g in r['changed_original_frames'])and len(r['adverse_controls'])==7 and all(g['rejected']for g in r['adverse_controls'])
 assert r['all1021raw_and_snapshot_columns_right_multiplied_by_literal_prepended_word']and r['all_gauged_response_columns_zero']
 assert {int(k):v for k,v in r['local_delta'].items()}=={1:10,3:4,4:-4,5:-2,6:2,7:1,8:-3}
 candidate=read(out/'word/candidate.json');ext=dict(candidate['ext']);v=candidate['v'];n=2*v+candidate['R'];h=candidate['h']
 assert (h,v,candidate['R'])==(9,120,781)
 counts=Counter(h-len(candidate['frames'][ext[r]])if r in ext else h for r in range(2*v,n))
 expected={int(k):64*z for k,z in counts.items()};seen=Counter();pads=Counter();banks=0
 for p in read(packing):
  assert type(p)is dict and set(p)<=({'count','padding'}|{'r'+str(r)for r in expected})
  assert all(type(z)is int and z>=0 for z in p.values())and p['count']>0
  ranks={int(k[1:]):z for k,z in p.items()if k.startswith('r')};rank=sum(k*z for k,z in ranks.items())
  assert rank+p['padding']==73 and 0<=p['padding']<=48
  for k,z in ranks.items():seen[k]+=z*p['count']
  if p['padding']:pads[p['padding']]+=p['count']
  banks+=p['count']
 assert dict(seen)==expected and banks==5873 and dict(pads)=={1:2873}
 assert expected==dict(zip(meta['packing']['ranks'],meta['packing']['counts']))
 assert before==T.check(package,native)and sha(source)==SOURCE and sha(packing)==meta['packing']['sha256']
 (out/'candidate.json').write_bytes((out/'word/candidate.json').read_bytes());(out/'patterns-T64.json').write_bytes(packing.read_bytes())
 r.update(status='PASS_UNCHANGED421_CONSTRUCTOR_WITH422_AND421_SELECTIONS_ON_FROZEN208',native_source=before,native_config_sha256=sha(native/'CONFIG422.json'),config_score_labels_are_unused_provenance=True,new_relations_all_response_coordinates_zero=True,packing=dict(replicas=64,banks_per_stage=banks,residual_counts=expected,padding=dict(pads),sha256=sha(packing),provenance=meta['packing']['provenance']),scope='Exact finite source reconstruction, whole/snapshot operator premise, chronological frame controls and integer residual packing only. Fresh215-token restoration, actual paid primitives, frame ledgers, Gaussian phases, native owner/bank decode/invoice and supplier pricing remain mandatory separate checks. No fixed-sixths, all-size or unconditional theorem claim.')
 (out/'RECONSTRUCTION.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n');return out/'candidate.json',r
if __name__=='__main__':
 assert len(sys.argv)==4,'PACKAGE SOURCE208 FRESH_OUT';candidate,r=run(*sys.argv[1:]);print(r['status'],r['candidate_sha256'])
