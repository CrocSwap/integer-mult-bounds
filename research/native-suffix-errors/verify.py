"""Exact suffix certificate and forward-injection oracle. Apache-2.0."""
from pathlib import Path
from fractions import Fraction as Q
import json,types,sys,random
HERE=Path(__file__).resolve().parent

def load(name,file):
 m=types.ModuleType(name);m.__file__=str(HERE/file);sys.modules[name]=m
 exec(compile((HERE/file).read_bytes(),m.__file__,'exec'),m.__dict__);return m
B=load('suffix_native_source','native_source.py');S=load('suffix_certificate','suffix.py')

def rejects(action,label):
 try:action()
 except (ValueError,KeyError,IndexError,StopIteration):return
 raise ValueError('Invalid control accepted: '+label)

def forward_injection(program,event,target,roles,backward,v):
 rows={r:{} for r in roles};rows[target]={(('N',0),()):Q(1)}
 for e in program[event+1:]:
  if e[0]=='scalar':
   op=e[1];dst=tuple(op[1])
   if op[0]=='add':v.add(rows[dst],rows[tuple(op[2])],Q(op[3],op[4]))
   elif op[0]=='scale':rows[dst]={key:Q(op[2],op[3])*q for key,q in rows[dst].items()}
   elif op[0]=='clear':rows[dst]={}
   elif op[0]=='copy':rows[dst]=dict(rows[tuple(op[2])])
   else:raise ValueError('Scalar')
  elif e[0]=='warp':rows[tuple(e[1])]=v.warp(rows[tuple(e[1])],e[2],backward)
 return {(r,word):q for r,row in rows.items() for (noise,word),q in row.items() if q}

def endpoint(columns,backward):
 for r,actual in columns.items():
  wanted={} if r[0]=='C' else {(r,()):Q(1)}
  if r[0]=='L':
   i=r[1];source=(112<=i<224) if backward else (0<=i<112)
   if source:
    target=('L',i-112 if backward else i+112);wanted[target,()]=Q(-1 if backward else 1)
  B.need(actual==wanted,'Whole reverse-response endpoint including owned dirty input')

def verify():
 words,chart,v,n=B.sources(B.authenticated());new,local=B.install(words,B.read('PATCHES.json'),n.primitive_allowance)
 results={};sample_checks=0;roles=[('L',i) for i in range(632)]+[('C',0)]
 for label,ws in [('original',words),('rewritten',new)]:
  results[label]={}
  for direction in ('forward','backward'):
   program=ws[direction];b=direction=='backward'
   scalar=[i for i,e in enumerate(program) if e[0]=='scalar'];sample=[scalar[len(scalar)//2],scalar[-3]]
   columns,bounds,counts,mx,saved=S.suffix(program,b,samples=sample);endpoint(columns,b)
   for index in sample:
    target=tuple(program[index][1][1]);B.need(forward_injection(program,index,target,roles,b,v)==saved[index],'Independent complete-suffix impulse response');sample_checks+=1
   result=S.summarize(program,b);B.need(Q(result['uniform_add_scale_bound'])==(4879 if b else 1328),'Exact uniform scalar defect constant')
   budget={cat:Q(cat in ('add','scale')) for cat in result['categories']}
   B.need(S.bound_from_rows(result,budget)==Q(result['uniform_add_scale_bound']),'Explicit class budget')
   result['semantic_word_sha256']=B.digest(program);results[label][direction]=result
 rng=random.Random(20261022);tiny_roles=[('L',0),('L',1),('C',0)];tiny_checks=0
 for _ in range(30):
  program=[]
  for k in range(12):
   t=rng.choice(tiny_roles);op=rng.choice(['add','scale','clear','copy','warp'])
   if op=='warp':program.append(['warp',list(t),rng.choice([-2,-1,1,2]),0,0])
   elif op=='scale':program.append(['scalar',['scale',list(t),rng.choice([-2,-1,1,2]),2],0])
   elif op=='clear':program.append(['scalar',['clear',list(t)],0])
   elif op=='copy':program.append(['scalar',['copy',list(t),list(rng.choice([r for r in tiny_roles if r!=t]))],0])
   else:program.append(['scalar',['add',list(t),list(rng.choice([r for r in tiny_roles if r!=t])),rng.choice([-3,-1,1,3]),2],0])
  for b in (False,True):
   _,_,_,_,saved=S.suffix(program,b,roles=tiny_roles,samples=range(len(program)))
   for index,e in enumerate(program):
    target=tuple(e[1][1] if e[0]=='scalar' else e[1]);B.need(saved[index]==forward_injection(program,index,target,tiny_roles,b,v),'Tiny all-event forward/backward response');tiny_checks+=1
 changes={}
 for d in ('forward','backward'):
  a=results['original'][d];b=results['rewritten'][d];delta=[]
  for x,y in zip(a['persistent_output_rows'],b['persistent_output_rows']):delta.append(sum(Q(y['weights'][c])-Q(x['weights'][c]) for c in ('add','scale')))
  changes[d]={'changed_output_bounds':sum(q!=0 for q in delta),'max_increase':str(max(delta)),'max_decrease':str(-min(delta))}
  B.need(a['uniform_add_scale_bound']==b['uniform_add_scale_bound'],'Unchanged WORST output bound only')
  bad={cat:0 for cat in b['categories']};bad.pop('warp');rejects(lambda:S.bound_from_rows(b,bad),'missing explicit class')
  bad={cat:0 for cat in b['categories']};bad['warp']=-1;rejects(lambda:S.bound_from_rows(b,bad),'negative defect budget')
 return {'status':'PASS_NATIVE_SUFFIX_ERROR_CERTIFICATES','results':results,'per_output_changes':changes,'complete_suffix_oracle_checks':sample_checks,'tiny_programs':30,'tiny_all_event_oracle_checks':tiny_checks,'uniform_forward_add_scale_bound':'1328','uniform_backward_add_scale_bound':'4879','extra_logical_defect_bits_both_directions':13,'physical_defect_contracts_verified':False,'rounded_recursive_induction_verified':False,'new_kappa':False}

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();result=json.loads(json.dumps(verify()))
 if args.write:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
 else:B.need(result==B.read('RESULT.json'),'Deterministic exact receipt')
 print(json.dumps({k:v for k,v in result.items() if k!='results'},sort_keys=True))
