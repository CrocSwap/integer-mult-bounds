"""Restored dirty-carrier wrapper for the exact PR1940 P104 delivery schedule.
Logical/frame certificate only; no complete supplier or kappa claim.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
from copy import deepcopy
import importlib.util,json,hashlib,os
HERE=Path(__file__).resolve().parent
SOURCE=HERE/'source/research/p104-target-order-delivery'
if not SOURCE.exists():SOURCE=HERE.parent/'kernel106/source/research/p104-target-order-delivery'
def require(c,msg):
 if not c:raise ValueError(msg)
def load():
 s=importlib.util.spec_from_file_location('p104',SOURCE/'verify.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def geometry(ref):
 g=ref.geometry();lines=ref.roots();gram=[[ref.inner(a,b) for b in lines] for a in lines]
 binary=[sum(((x+1)&1)<<j for j,x in enumerate(row)) for row in gram];ind=[];ix=[]
 for i,row in enumerate(binary):
  if not ref.in_span(row,ind):ind.append(row);ix.append(i)
 labels=[sum(((row>>j)&1)<<k for k,j in enumerate(ix)) for row in binary];byroot=dict(zip(lines,labels))
 g['source_frames']=[list(ref.basis([byroot[r] for r,row in zip(g['ports'],g['t']) if row[k]])) for k in range(8)]
 g['target_frames']=[list(ref.basis([byroot[s] for s in lines if (ref.inner(r,s)+1)%2==0])) for r in g['ports']]
 require(all(len(f)==8 for f in g['source_frames']+g['target_frames']),'bad source/target hyperplane')
 return g

def build():
 ref=load();g=geometry(ref);c=json.loads((SOURCE/'SCHEDULE.json').read_text());orders=ref.orders_from_tree(c,g['masks']);events=ref.events_from_orders(orders,g['masks'])
 chains=c['chains'];assignment={};carriers=[]
 for k,cs in enumerate(chains):
  for ci,chain in enumerate(cs):
   i=len(carriers);carriers.append((k,ci));
   for mask in chain:assignment[k,mask]=i
 F=lambda mask:list(ref.basis([g['labels'][k] for k in range(8) if mask>>k&1]))
 full=[1<<j for j in range(9)];initial={f'Q{k}':f for k,f in enumerate(g['source_frames'])};initial.update({f'H{i}':[] for i in range(len(carriers))});initial.update({f'Y{t}':[] for t in range(104)})
 program=[];cur=deepcopy(initial)
 def move(reg,dest):
  old=cur[reg]
  if set(ref.basis(old))!=set(ref.basis(dest)):
   program.append(['transport',reg,old,dest,abs(len(old)-len(dest))]);cur[reg]=dest
 # Cancel initial dirty symbols before any target leaves frame zero.
 for _,mask,k,t in events:program.append(['add',f'Y{t}',f'H{assignment[k,mask]}',-g['d'][t][k],[]])
 for i,(k,ci) in enumerate(carriers):move(f'H{i}',F(1<<k))
 # One private centre copy is live at a time. All carriers stand at its E_k.
 for k in range(8):
  qf=g['source_frames'][k];ef=F(1<<k)
  program.extend([['zero','C',qf],['copy','C',f'Q{k}',qf],['transport','C',qf,ef,7]])
  for i,(kk,ci) in enumerate(carriers):
   if kk==k:program.append(['add',f'H{i}','C',1,ef])
  program.append(['erase','C',ef])
 # The exact chronological per-target schedule from PR1940.
 for _,mask,k,t in events:
  i=assignment[k,mask];f=F(mask);move(f'H{i}',f);move(f'Y{t}',f)
  program.append(['add',f'Y{t}',f'H{i}',g['d'][t][k],f])
 for t,f in enumerate(g['target_frames']):move(f'Y{t}',f)
 # Finish normal source/helper lifetimes, then remove query from each helper.
 for k in range(8):move(f'Q{k}',full)
 for i,(k,ci) in enumerate(carriers):
  move(f'H{i}',full);program.append(['add',f'H{i}',f'Q{k}',-1,full])
 return {'initial_frames':initial,'final_frames':cur,'carriers':carriers,'program':program}

def audit(w):
 ref=load();g=geometry(ref);basis=ref.basis
 eq=lambda a,b:ref.rank(a)==ref.rank(b)==ref.rank(a+b)
 subset=lambda a,b:all(ref.in_span(x,b) for x in a)
 names=list(w['initial_frames']);rows={r:{r:Q(1)} for r in names};frames=deepcopy(w['initial_frames']);paid=Counter();category={k:Counter() for k in ['query_copy','query_parent','dirty_carrier','target']};scalar=Counter();l1=Q(1);trace=[]
 for index,e in enumerate(w['program']):
  op=e[0]
  if op=='transport':
   _,r,a,b,rank=e;require(r in frames and eq(frames[r],a),'transport entry')
   require(subset(a,b) or subset(b,a),'nonnested frames');require(rank==abs(ref.rank(a)-ref.rank(b)) and rank>0,'wrong rank')
   require(r=='C' or subset(a,b),'live register descended')
   paid[rank]+=1;category['query_copy' if r=='C' else 'query_parent' if r.startswith('Q') else 'dirty_carrier' if r.startswith('H') else 'target'][rank]+=1;frames[r]=b
  elif op=='zero':
   _,r,f=e;require(r=='C' and r not in frames,'zero live register');rows[r]={};frames[r]=f;scalar[op]+=1
  elif op=='erase':
   _,r,f=e;require(r=='C' and eq(frames[r],f),'erase frame');del rows[r];del frames[r];scalar[op]+=1
  elif op=='copy':
   _,r,s,f=e;require(eq(frames[r],f) and eq(frames[s],f) and not rows[r],'copy frame/initialization');rows[r]=dict(rows[s]);scalar[op]+=1
  elif op=='add':
   _,r,s,a,f=e;require(r!=s and eq(frames[r],f) and eq(frames[s],f),'addition frame')
   for j,x in list(rows[s].items()):
    y=rows[r].get(j,Q(0))+a*x
    if y:rows[r][j]=y
    else:rows[r].pop(j,None)
   scalar[op]+=1
  else:raise ValueError('unknown event')
  l1=max(l1,max((sum(abs(x) for x in row.values()) for row in rows.values()),default=Q(0)))
 require(set(frames)==set(names),'private lifetime open')
 for r in names:
  require(eq(frames[r],w['final_frames'][r]),'wrong final frame')
  expected={r:Q(1)}
  if r.startswith('Y'):
   t=int(r[1:]);expected.update({f'Q{k}':Q(a) for k,a in enumerate(g['d'][t]) if a})
  require(rows[r]==expected,'wrong endpoint '+r)
 return {'columns':len(names),'paid_profile':dict(sorted(paid.items())),'categories':{k:dict(sorted(v.items())) for k,v in category.items()},'scalar_events':dict(scalar),'prefix_l1':str(l1),'events':len(w['program'])}

def run(write=False):
 require(os.path.ismount('/Volumes/SP AI 01_16') or not write,'SSD absent')
 w=build();r=audit(w);controls={}
 def reject(name,change):
  z=deepcopy(w);change(z['program'])
  try:audit(z)
  except (ValueError,KeyError):controls[name]='REJECTED'
  else:raise ValueError('accepted '+name)
 reject('missing_precompensation',lambda es:es.pop(0))
 reject('wrong_precompensation_sign',lambda es:es[0].__setitem__(3,-es[0][3]))
 reject('missing_final_query_removal',lambda es:es.pop())
 reject('wrong_final_query_removal_sign',lambda es:es[-1].__setitem__(3,1))
 reject('missing_singleton_carrier_climb',lambda es:es.pop(next(i for i,e in enumerate(es) if e[0]=='transport' and e[1].startswith('H'))))
 reject('wrong_copy_rank',lambda es:next(e for e in es if e[0]=='transport' and e[1]=='C').__setitem__(4,6))
 reject('missing_private_erase',lambda es:es.pop(next(i for i,e in enumerate(es) if e[0]=='erase')))
 reject('wrong_read_coefficient',lambda es:next(e for e in es[416:] if e[0]=='add' and e[1].startswith('Y')).__setitem__(3,3))
 r.update(status='PASS_RESTORED_DIRTY_P104_DELIVERY_FRAME_MODEL',controls=controls,dirty_carriers=32,dirty_width_inventory={'9':32},private_copy_slots=1,
  boundary='Eight arbitrary independent query streams enter at their rank-eight gather hyperplanes and exit at full rank nine. 104 arbitrary targets enter at zero and exit at their rank-eight hyperplanes. 32 arbitrary dirty carriers enter at zero, exit at full rank nine and retain their normalized input contents. Every supplied query is preserved in normalized coordinates.',
  scope='Exact rational coefficient columns and physical binary frame incidence under inherited canonical chart/child lemmas. No literal Gaussian phase/compiler replay, full P104 gather or side-correction word, owner packing, precision admission, or new kappa.')
 mass=lambda d:sum(int(k)*v for k,v in d.items())
 r['rank_mass']=mass(r['paid_profile']);r['coverage_mass']=8+32*9+104*8;r['mass_beyond_frame_coverage']=r['rank_mass']-r['coverage_mass'];require(r['mass_beyond_frame_coverage']==56,'unexpected mass')
 if write:
  (HERE/'DIRTY-WITNESS.json').write_text(json.dumps(w,indent=2)+'\n');(HERE/'DIRTY-RESULT.json').write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps(r,indent=2));return r
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();run(a.write)
