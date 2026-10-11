"""Source-bound enlargement of gauge891 by four additional dimensions.
Own fixed witness, executed by the unchanged PR423 constructor already restored
by enlarge.py. No search runs in this verifier. OpenAI Codex assistance.
"""
from pathlib import Path
from collections import Counter
import copy,hashlib,importlib.util,json,os,subprocess,sys
if not __debug__:raise RuntimeError('Assertions required')
sys.dont_write_bytecode=True
import enlargement_source as T
SOURCE='773e95ecfeb61da70e27bcd6524e755eb7d748fe122beba5aba0b9dfb6fe5313'
BASELINE='9b0664bc1f8eed0fda952f6f3f1f4636b527fba35a3735cbff9a5a45384c660c'
EXPECTED='c7e071e34bd37d14e7969dbc895206b550ec9e172e68b5633b2e927a3b0c2dfd'
SELECTION=[dict(pivot=891,basis=[256,195,32,16,15])]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
def run(package,source,baseline,native,fresh_out):
 package,source,baseline,native=map(lambda p:Path(p).resolve(),(package,source,baseline,native));out=Path(fresh_out).absolute()
 assert sha(source)==SOURCE and sha(baseline)==BASELINE and not out.exists()and not out.is_symlink()and not out.resolve().is_relative_to(package)
 for p in[out]+list(out.parents):assert not p.is_symlink()
 before=T.check(package,native);out.mkdir(parents=True);initial=read(source);base=read(baseline)
 spec=importlib.util.spec_from_file_location('_native_refinement_common',native/'common.py');C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
 old=initial['frames'][dict(initial['ext'])[891]];assert len(old)==1
 (out/'SELECTION.json').write_text(json.dumps(SELECTION,sort_keys=True,indent=2)+'\n')
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None)
 cmd=[sys.executable,'-B',str(native/'construct.py'),str(source),str(out/'SELECTION.json'),str(out/'word'),'--source-sha256',SOURCE,'--expected-sha256',EXPECTED]
 with(out/'construct.log').open('w')as log:subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 candidate=out/'word/candidate.json';assert sha(candidate)==EXPECTED;result=read(out/'word/RECEIPT.json');final=read(candidate)
 assert result['gauges']==215 and result['new_gates']==0 and result['selection']==SELECTION
 assert result['all1021raw_and_snapshot_columns_unchanged']and result['all_gauged_response_columns_zero']
 assert len(result['changed_original_frames'])==len(result['adverse_controls'])==4 and all(c['rejected']for c in result['adverse_controls'])
 assert {(c['part'],c['index'])for c in result['changed_original_frames']}=={('A',134),('A',139),('A',144),('B',398)}
 assert len(final['frames'][dict(final['ext'])[891]])==5
 for initial_word in [initial,base]:
  for part in ['A','B']:assert [g[:1]+g[2:]for g in initial_word[part]]==[g[:1]+g[2:]for g in final[part]]
  assert C.replay(initial_word)==C.replay(final)
  a=copy.deepcopy(initial_word);b=copy.deepcopy(final)
  for word in[a,b]:word['B']=[];word['scat']['table']=[[]for _ in range(word['v'])]
  assert C.replay(a)==C.replay(b)
 changes=[dict(part=part,index=i,old=a[1],new=b[1])for part in['A','B']for i,(a,b)in enumerate(zip(base[part],final[part]))if a[1]!=b[1]]
 assert len(changes)==33;controls=[]
 for change in changes:
  bad=copy.deepcopy(final);bad[change['part']][change['index']][1]=change['old']
  try:C.rehist_and_audit(bad)
  except AssertionError:controls.append(dict(name='revert_final_required_frame',part=change['part'],index=change['index'],rejected=True))
  else:raise AssertionError('Final required frame reversion accepted')
 ext=dict(final['ext']);counts=Counter(final['h']-len(final['frames'][ext[r]])if r in ext else final['h']for r in range(2*final['v'],2*final['v']+final['R']))
 assert dict(counts)=={9:566,8:148,7:24,5:18,4:25}and len(ext)==215 and sum(len(final['frames'][f])for r,f in final['ext'])==393
 assert before==T.check(package,native)and sha(source)==SOURCE and sha(baseline)==BASELINE and sha(candidate)==EXPECTED
 (out/'candidate.json').write_bytes(candidate.read_bytes())
 result.update(status='PASS_OWN891_FOUR_DIMENSION_WITNESS_UNCHANGED423_CONSTRUCTOR',native_source=before,baseline215_sha256=BASELINE,selection_provenance='applecrusher with OpenAI Codex; bounded exhaustive121-subspace screen, followed by unchanged PR423 constructor. No upstream claim of this selection is made.',total_enlarged_entrances=15,entrance_rankmass=393,new_scalar_gates=0,scalar_groups_unchanged=True,all1021raw_and_snapshot_columns_unchanged_from215=True,final_propagated_frames=changes,final_frame_reversion_controls=controls,residual_rank_counts=dict(counts),scope='Exact finite literal reconstruction, unchanged full raw and retained snapshot operators, final frame nesting and actual reversion controls. All local response/token/primitive/Gaussian/owner/bank/finite/analytic validations are freshly run separately. No unconditional or fixed-sixths claim.')
 (out/'RECONSTRUCTION.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');return out/'candidate.json',result
if __name__=='__main__':
 assert len(sys.argv)==6,'PACKAGE SOURCE14 BASELINE215 NATIVE423 FRESH_OUT';c,r=run(*sys.argv[1:]);print(r['status'],r['candidate_sha256'])
