"""Eight pinned PR410 entrance enlargements, then ten pinned PR409 promotions.
The original194 relations and fresh frozen-parent target word are retained.
No search runs here. Rohan Arun/OpenAI Codex source attribution is retained.
"""
from pathlib import Path
from hashlib import sha256
import copy,importlib.util,json,os,subprocess,sys
HERE=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_bytes())
digest=lambda p:sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def prepare(source410,source409,parent,output):
 source410,source409,parent,output=map(Path,(source410,source409,parent,output));assert not output.exists();output.mkdir(parents=True)
 ownpath=parent/'normalization/reconstruction/candidate.json'
 assert digest(ownpath)=='3ced59a749d2e61e6a540e423af7bcd1abfef602606f883de99fb83faa61022c'
 def run(name,script,*args):
  with(output/(name+'.log')).open('w')as log:subprocess.run([sys.executable,'-B',str(script),*map(str,args)],stdout=log,stderr=subprocess.STDOUT,check=True)
 run('reference119',source410/'frames/reconstruct.py',source410/'inputs/candidate781.json',output/'reference119',source410/'frames/selection.json')
 old=read(source410/'shared/selection194.json')['plans'];large=read(source410/'shared/enlarged205.json');changes=large['changes'];assert len(changes)==8
 old_by={z['pivot']:(p,z)for p in old for z in p['pivots']};large_by={z['pivot']:(p,z)for p in large['plans']for z in p['pivots']};changed={x['pivot']for x in changes};assert len(changed)==8
 for x in changes:
  op,oz=old_by[x['pivot']];np,nz=large_by[x['pivot']]
  assert oz==nz and op['basis']==x['old']and np['basis']==x['new']
  assert len(np['pivots'])==1 and len(np['basis'])==len(op['basis'])+1
 plans=copy.deepcopy(old)
 for p in plans:
  p['pivots']=[z for z in p['pivots']if z['pivot']not in changed]
  p['donors']=sorted({int(d)for z in p['pivots']for d in z['coefficients']})
 plans=[p for p in plans if p['pivots']]+[copy.deepcopy(large_by[x['pivot']][0])for x in changes]
 assert sum(len(p['pivots'])for p in plans)==194
 write(output/'selection194.json',dict(plans=plans))
 run('enlarged194',source410/'shared/reconstruct.py',source410/'inputs/candidate781.json',output/'enlarged194',output/'selection194.json','--reference119',output/'reference119/candidate.json')
 sp=importlib.util.spec_from_file_location('enlarged410_exact_frames',source410/'frames/reconstruct.py');math=importlib.util.module_from_spec(sp);sp.loader.exec_module(math)
 c=read(output/'enlarged194/candidate.json');base=copy.deepcopy(c);own=read(ownpath)
 for g in own['B']:assert own['frames'][g[1]]==c['frames'][g[1]]
 c['B']=copy.deepcopy(own['B']);assert math.replay(c)==math.replay(base)
 math.rehist_and_audit(c);blob=json.dumps(c,sort_keys=True,separators=(',',':')).encode();(output/'enlarged194-ownB.json').write_bytes(blob)
 run('original204',source409/'construct.py',ownpath,output/'original204')
 run('enlarged204',source409/'construct.py',output/'enlarged194-ownB.json',output/'enlarged204')
 baseline=read(output/'original204/candidate.json');final=read(output/'enlarged204/candidate.json');raw=(output/'enlarged204/candidate.json').read_bytes()
 assert digest(output/'original204/candidate.json')=='ce08d9cf014d70757d628ca3a15d42168f341bb0929135c0b215e284a10a2953'
 assert sha256(raw).hexdigest()=='7ff1782ab6fa0b846d7b00f57a034c05cd64b286eb9c3215efb184d5e9511408'
 assert math.replay(final)==math.replay(baseline)
 assert final['B']==own['B']and len(final['ext'])==204 and sum(len(final['frames'][f])for r,f in final['ext'])==362
 trans=math.rehist_and_audit(final);h0=math.histogram(baseline);h1=math.histogram(final);delta={r:h1[r]-h0[r]for r in h0.keys()|h1.keys()if h1[r]!=h0[r]}
 assert delta=={1:36,2:-23,3:-4,4:1,5:2}
 expected=math.replay(final);controls=[]
 for target in [177,220]:
  for kind,frame,source,coefficient in [('omit_setup',0,221,-1),('omit_restore',892,221,1),('flip_delivery',892,801,-1)]:
   bad=copy.deepcopy(final);hits=[i for i,g in enumerate(bad['B'])if g[0]=='in'and g[1]==frame and g[2]==target and len(g[3])==1 and g[3][0][0]==source and g[3][0][1]==coefficient];assert len(hits)==1
   if kind.startswith('omit'):bad['B'].pop(hits[0])
   else:bad['B'][hits[0]][3][0][1]*=-1
   different=math.replay(bad);assert different!=expected
   controls.append(dict(target=target,mutation=kind,rejected=True,changed_rows=sum(a!=b for a,b in zip(different,expected))))
 (output/'candidate.json').write_bytes(raw)
 result=dict(status='PASS_PINNED_EIGHT_ENLARGEMENTS_THEN_TEN_ORDERED_PROMOTIONS',candidate_sha256=sha256(raw).hexdigest(),parent_candidate_sha256=digest(ownpath),original204_candidate_sha256=digest(output/'original204/candidate.json'),source410_commit='95ad14d5359d62a89e7bb06eb59b68029e77fb6f',source409_commit='212e03d7665d08fc6a037d3e33612cb7fc60874d',gauges=204,dimension_sum=362,changes=changes,selection194_sha256=digest(output/'selection194.json'),enlarged194_candidate_sha256=digest(output/'enlarged194/candidate.json'),enlarged194_ownB_sha256=sha256(blob).hexdigest(),sequential=read(output/'enlarged204/RESULT.json'),histogram_delta_vs_original204=delta,all_raw_columns=1021,nested_transitions=trans,target_resynthesis_mutation_controls=controls,scope='Eight exact frame enlargements of original194 relations, followed by all ten ordered PR409 promotions. The PR410205 selection and its separate206th promotion are not used. Fresh emitted operators, phases, banks and finite arithmetic remain required; no unconditional theorem.')
 write(output/'PREFLIGHT.json',result);return result
