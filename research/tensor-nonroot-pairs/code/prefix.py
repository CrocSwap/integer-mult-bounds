"""Exact finite interval target-factoring constructor (stdlib only).
Usage: python -B reconstruct.py SOURCE_WORD NEW_OUTPUT_DIRECTORY
Inherited all-size compiler, target-label, correlated-hosting and analytic contracts remain assumptions.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
import argparse,copy,hashlib,json
SOURCE='2da477f6743f463fbcdce8c2b56e5bbdf27575cb2127737715d8b987cae17a84'
EXPECTED='b866c92679031e010bb9732cb192ebe64509c8e34dd63797ab81f4b758b50d7f'
STEPS=[dict(u=122,d=123,start=0,end=178,setup_frame=0,recover_frame=813,remove=[[2,240]]),dict(u=210,d=123,start=1,end=62,setup_frame=0,recover_frame=534,remove=[[4,240]])]
def rank(a):
 rows=[]
 for aa in a:
  r=list(map(Q,aa))
  for s in rows:
   p=next(i for i,x in enumerate(s)if x)
   if r[p]:q=r[p]/s[p];r=[x-q*y for x,y in zip(r,s)]
  if any(r):rows.append(r)
 return len(rows)
def rewrite(z,sel):
 w=copy.deepcopy(z);B=[];cuts=[];rm=set(map(tuple,sel['remove']))
 for i,(f,d,ss)in enumerate(z['B']):
  if i==sel['start']:cuts.append(len(B));B.append([sel['setup_frame'],sel['u'],[sel['d']]])
  src=[s for s in ss if(i,s)not in rm]
  if src:B.append([f,d,src])
  if i==sel['end']:cuts.append(len(B));B.append([sel['recover_frame'],sel['u'],[sel['d']]])
 w['B']=B;return w,cuts
def check(z,dims):
 v=z['v'];n=2*v+z['R'];frames=list(map(frozenset,z['frames']));cur=z['start'][:];x=[1<<i for i in range(n)];supp=[Counter({i:1})if i<v else Counter()for i in range(n)];H=Counter();target_reads=0
 def visit(r,f):
  a=cur[r];assert frames[a]<=frames[f],('frame',r,a,f)
  if a!=f:dr=dims[f]-dims[a];assert dr>0;H[dr]+=1;cur[r]=f
 def run(phase):
  nonlocal target_reads
  for k,(f,d,ss)in enumerate(z[phase]):
   assert d>=v and d not in ss and len(ss)==len(set(ss))
   for r in [d]+ss:visit(r,f)
   for s in ss:
    assert set(supp[s])<=frames[f],('integer operand span',phase,k,s)
    if v<=s<2*v:target_reads+=1
    x[d]^=x[s];supp[d].update(supp[s])
   if d>=2*v:assert set(supp[d])<=frames[f]
 run('D');assert cur==z['start'];run('A');assert all(cur[t]==0 for t in range(v,2*v))
 cp=[x[r]for r in z['ret']]
 for r in z['ret']:H[dims[cur[r]]]+=1
 for t,ss in enumerate(z['scatter']):
  for k in ss:x[v+t]^=cp[k]
 run('B');run('C')
 for r,f in enumerate(z['final']):visit(r,f)
 expected=[1<<i for i in range(n)]
 for t in range(v):expected[v+t]^=1<<t
 assert x==expected,'raw arbitrary-dirty identity'
 return dict(columns=n,profile=dict(sorted(H.items())),target_reads=target_reads,all_integer_operand_spans=True)
def construct(z):
 dims=[rank([z['lines'][i]for i in f])for f in z['frames']];base=check(z,dims);runs=[];controls={}
 for num,sel in enumerate(STEPS,1):
  w,cuts=rewrite(z,sel);got=check(w,dims)
  for name,idx in zip(['omit setup','omit recovery'],cuts):
   bad=copy.deepcopy(w);bad['B'].pop(idx)
   try:check(bad,dims)
   except AssertionError:controls[f'{num}: {name}']='REJECTED'
   else:raise AssertionError('vacuous mutation')
  bad=copy.deepcopy(w);bad['B'][cuts[1]][0]=0
  try:check(bad,dims)
  except AssertionError:controls[f'{num}: recovery at frame0']='REJECTED'
  else:raise AssertionError('vacuous frame mutation')
  runs.append(dict(selection=sel,check=got));z=w
 delta={r:runs[-1]['check']['profile'].get(r,0)-base['profile'].get(r,0)for r in set(base['profile'])|set(runs[-1]['check']['profile'])};delta={r:n for r,n in delta.items()if n};assert delta=={1:2,2:-1,3:-1,4:-2,5:1,6:1}
 return z,dict(status='PASS_EXACT_TWO_PARTIAL_PREFIX_FACTORS',base=base,steps=runs,delta=delta,controls=controls,scope='Finite unchanged-source-bound word; no standalone all-size multiplication claim.')
def main():
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();src=a.source.read_bytes();assert hashlib.sha256(src).hexdigest()==SOURCE;assert not a.output.exists();z,receipt=construct(json.loads(src));blob=json.dumps(z,sort_keys=True,separators=(',',':')).encode();assert hashlib.sha256(blob).hexdigest()==EXPECTED;a.output.mkdir(parents=True);(a.output/'candidate.json').write_bytes(blob);receipt.update(source_sha256=SOURCE,candidate_sha256=EXPECTED);(a.output/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
