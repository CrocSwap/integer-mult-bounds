"""Exact output-basis prefix recovery. Standalone stdlib, finite certificate only."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import copy,json

def digest(p):return sha256(p.read_bytes()).hexdigest()
def inside(a,b):
 piv={}
 for x in b:
  while x:
   k=x.bit_length()-1
   if k in piv:x^=piv[k]
   else:piv[k]=x;break
 for x in a:
  while x:
   k=x.bit_length()-1
   if k not in piv:return False
   x^=piv[k]
 return True

def roles(g):return [g[2]]+[r for r,_,_ in g[3]]+(g[4] if g[0]=='out' else [])
def flat(z):
 for part in ['A','B']:
  for g in z[part]:
   for r,a,b in g[3]:yield ((g[2],r) if g[0]=='in' else (r,g[2]))+(Q(a,b),)
def helper_word(z):
 v=z['v'];return [(t,s,q) for t,s,q in flat(z) if not(v<=t<2*v)]
def replay(z):
 v=z['v'];n=2*v+z['R'];rows=[{i:Q(1)} for i in range(n)]
 def ax(t,source,q):
  for k,a in list(source.items()):
   value=rows[t].get(k,Q(0))+q*a
   if value:rows[t][k]=value
   else:rows[t].pop(k,None)
 for part in ['A','B']:
  if part=='B':
   total={k:dict(rows[r]) for k,r,_ in z['ret']}
   for t,entry in enumerate(z['scat']['table']):
    for k,a,b in entry:ax(v+t,total[k],Q(a,b))
  for g in z[part]:
   for r,a,b in g[3]:
    t,s=(g[2],r) if g[0]=='in' else (r,g[2]);ax(t,dict(rows[s]),Q(a,b))
 return rows

def rehist(z):
 v=z['v'];cur=z['start'][:];hist={k:Counter() for k in ['x','y','s','c']};visits=0
 def visit(r,f):
  nonlocal visits
  old=cur[r];assert inside(z['frames'][old],z['frames'][f]),(r,old,f)
  if old!=f:
   rank=len(z['frames'][f])-len(z['frames'][old]);assert rank>0
   hist['x' if r<v else 'y' if r<2*v else 's'][rank]+=1;cur[r]=f;visits+=1
 for part in ['A','B']:
  if part=='B':
   for _,_,f in z['ret']:hist['c'][len(z['frames'][f])]+=1
  for g in z[part]:
   for r in roles(g):visit(r,g[1])
 for r,f in enumerate(z['final']):visit(r,f)
 z['blocks']={k:{str(r):n for r,n in sorted(h.items())} for k,h in hist.items()};z['N']=sum(r*n for h in hist.values() for r,n in h.items());return visits

def transform(z):
 assert z['v']==120 and z['R']==781 and z['h']==9
 assert z['B'][860]==['in',485,125,[[358,1,2]]]
 assert z['B'][1164]==['in',904,125,[[367,1,2]]]
 assert all(g[1]==0 for g in z['B'][:25])
 new=copy.deepcopy(z)
 new['B'].insert(1165,['in',904,125,[[124,1,1]]]);new['B'].pop(860);new['B'].insert(25,['in',0,125,[[124,-1,1]]])
 visits=rehist(new);oldrows=replay(z);assert replay(new)==oldrows
 assert helper_word(new)==helper_word(z)
 for k in z:
  if k not in ['B','blocks','N']:assert new[k]==z[k],k
 delta={}
 for block in z['blocks']:
  for r in set(z['blocks'][block])|set(new['blocks'][block]):
   amount=new['blocks'][block].get(r,0)-z['blocks'][block].get(r,0)
   delta[int(r)]=delta.get(int(r),0)+amount
 delta={r:d for r,d in delta.items() if d};assert delta=={1:1,3:-1,4:-1,6:1};assert z['N']==new['N']
 for gi in [25,1165]:
  bad=copy.deepcopy(new);bad['B'].pop(gi);assert replay(bad)!=oldrows
 return new,dict(status='PASS_EXACT_OUTPUT_BASIS_RECOVERY',dirty_columns=len(oldrows),histogram_delta=delta,rank_mass_delta=0,net_literal_scalar_gates=1,nested_transitions=visits,helper_cleanup_subword_unchanged=True,negative_controls=['omit zero-frame setup','omit frame904 recovery'],scope='Exact finite full raw operator and paid target paths. Separate scalar/phase/bank/invoice/outer checks and inherited all-size interfaces required; no kappa claimed.')

def main():
 p=ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);p.add_argument('--source-sha256',required=True);a=p.parse_args();assert digest(a.source)==a.source_sha256;assert not a.output.exists()
 new,receipt=transform(json.loads(a.source.read_bytes()));blob=json.dumps(new,sort_keys=True,separators=(',',':')).encode();a.output.mkdir(parents=True);(a.output/'candidate.json').write_bytes(blob);receipt.update(source_sha256=a.source_sha256,candidate_sha256=sha256(blob).hexdigest());(a.output/'RECEIPT.json').write_text(json.dumps(receipt,indent=2));assert digest(a.source)==a.source_sha256;print(json.dumps(receipt))
if __name__=='__main__':main()
