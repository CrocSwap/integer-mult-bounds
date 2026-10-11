"""Execute unchanged423 enlargement twice: exact updated422 thirteen plans, then424838.
Both scalar words and all raw/snapshot operators are unchanged from fresh215.
The native424 target125 prefix and any fusion construction are not imported.
"""
from pathlib import Path
from collections import Counter
import copy,hashlib,importlib.util,json,os,subprocess,sys
if not __debug__:raise RuntimeError('Assertions required')
sys.dont_write_bytecode=True
import enlargement_source as T
SOURCE='9b0664bc1f8eed0fda952f6f3f1f4636b527fba35a3735cbff9a5a45384c660c'
INTERMEDIATE='6363be0efb11232f14b2a30a03cbcf50294a93de09638be7b467ba1606c0a675'
EXPECTED='773e95ecfeb61da70e27bcd6524e755eb7d748fe122beba5aba0b9dfb6fe5313'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
def run(package,source,fresh_out):
 package=Path(package).resolve();source=Path(source).resolve();out=Path(fresh_out).absolute()
 assert sha(source)==SOURCE and not out.exists()and not out.is_symlink()and not out.resolve().is_relative_to(package)
 for p in[out]+list(out.parents):assert not p.is_symlink()
 T.decode(package);out.mkdir(parents=True);native=T.restore(package,out/'native');before=T.check(package,native);meta=T.metadata(package)
 spec=importlib.util.spec_from_file_location('_native_enlargement_common',native/'common.py');C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
 initial=read(source);selected=read(native/'SELECTED13.json');native12=read(native/'NATIVE12.json');pair=read(native/'PAIR914960.json');witness=read(native/'WITNESS424.json')
 assert len(native12)==12 and len(pair)==2 and [p['pivot']for p in pair]==[914,960]
 assert selected==[p for p in native12 if p['pivot']!=785]+pair and len(selected)==13
 assert 785 not in dict(initial['ext'])and sum(p['pivot']==785 for p in native12)==1
 assert witness['enlarge838']=={'pivot':838,'basis':[304,204]}and witness['excluded423']==[785]
 assert initial['frames'][dict(initial['ext'])[838]]==[204]
 selection14=[witness['enlarge838']]
 (out/'SELECTION838.json').write_text(json.dumps(selection14,sort_keys=True,indent=2)+'\n')
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None)
 def execute(src,selection,folder,expected=None):
  cmd=[sys.executable,'-B',str(native/'construct.py'),str(src),str(selection),str(out/folder),'--source-sha256',sha(src)]
  if expected:cmd+=['--expected-sha256',expected]
  with(out/(folder+'.log')).open('w')as log:r=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT)
  return r.returncode
 # The original12 selection cannot silently be transferred to nongauged785.
 assert execute(source,native/'NATIVE12.json','rejected-native12')!=0
 assert not(out/'rejected-native12/candidate.json').exists()
 assert execute(source,native/'SELECTED13.json','thirteen',INTERMEDIATE)==0
 middle=out/'thirteen/candidate.json';assert sha(middle)==INTERMEDIATE
 assert execute(middle,out/'SELECTION838.json','fourteen',EXPECTED)==0
 candidate=out/'fourteen/candidate.json';assert sha(candidate)==EXPECTED
 steps=[read(out/'thirteen/RECEIPT.json'),read(out/'fourteen/RECEIPT.json')]
 assert [len(r['changed_original_frames'])for r in steps]==[27,2]
 for r in steps:
  assert r['gauges']==215 and r['new_gates']==0 and r['all1021raw_and_snapshot_columns_unchanged']and r['all_gauged_response_columns_zero']
  assert len(r['adverse_controls'])==len(r['changed_original_frames'])and all(x['rejected']for x in r['adverse_controls'])
 final=read(candidate);assert (final['h'],final['v'],final['R'])==(9,120,781)
 # Check the composition itself, including every required final frame reversion.
 for part in['A','B']:
  assert len(initial[part])==len(final[part])
  assert [g[:1]+g[2:]for g in initial[part]]==[g[:1]+g[2:]for g in final[part]]
 changes=[dict(part=part,index=i,old=a[1],new=b[1])for part in['A','B']for i,(a,b)in enumerate(zip(initial[part],final[part]))if a[1]!=b[1]]
 assert len(changes)==29
 controls=[]
 for change in changes:
  bad=copy.deepcopy(final);bad[change['part']][change['index']][1]=change['old']
  try:C.rehist_and_audit(bad)
  except AssertionError:controls.append(dict(name='revert_final_required_frame',part=change['part'],index=change['index'],rejected=True))
  else:raise AssertionError('Final required frame reversion was accepted')
 assert C.replay(initial)==C.replay(final)
 for c in[initial,final]:c['B']=[];c['scat']['table']=[[]for _ in range(c['v'])]
 assert C.replay(initial)==C.replay(final)
 final=read(candidate);ext=dict(final['ext']);counts=Counter(final['h']-len(final['frames'][ext[r]])if r in ext else final['h']for r in range(2*final['v'],2*final['v']+final['R']))
 assert dict(counts)=={9:566,8:149,7:24,5:18,4:24}
 assert {str(r):64*z for r,z in counts.items()}==witness['inventory64']
 assert len(ext)==215 and sum(len(final['frames'][f])for r,f in final['ext'])==389
 assert before==T.check(package,native)and sha(source)==SOURCE and sha(middle)==INTERMEDIATE and sha(candidate)==EXPECTED
 (out/'candidate.json').write_bytes(candidate.read_bytes())
 result=dict(status='PASS_UNCHANGED423_TWO_STEP_FOURTEEN_ENLARGEMENTS_ON_FRESH215',source_sha256=SOURCE,intermediate_sha256=INTERMEDIATE,candidate_sha256=EXPECTED,native_source=before,selected13_equals_native12_without785_plus_native_pair=True,unadapted_native12_rejected=True,only424_enlarge838_used=True,excluded424_fields=['prefix125'],gauges=215,entrance_rankmass=389,enlarged_entrances=14,new_scalar_gates=0,scalar_groups_unchanged=True,all1021raw_and_snapshot_columns_unchanged=True,propagated_frames=changes,final_frame_reversion_controls=controls,steps=steps,residual_rank_counts=dict(counts),packing_expectation=meta['packing'],scope='Exact finite reconstruction and composed whole/snapshot scalar operator and frame premise only. Fresh native423 local controls require frame-baseline215, with separately recorded target171 omission-control retargeting. Independent215 helper tokens, actual emitted paid primitives, Gaussian phases, serialized banks and invoices, signed9 finite composition and all-size obligations remain separate mandatory checks. No fixed-sixths or unconditional theorem claim.')
 (out/'RECONSTRUCTION.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');return out/'candidate.json',result
if __name__=='__main__':
 assert len(sys.argv)==4,'PACKAGE SOURCE215 FRESH_OUT';candidate,r=run(*sys.argv[1:]);print(r['status'],r['candidate_sha256'])
