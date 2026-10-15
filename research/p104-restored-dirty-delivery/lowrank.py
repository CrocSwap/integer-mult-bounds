"""Experimental complete P104 low-rank channel: no side-correction or kappa claim.
Uses exact PR1940 chain cover through our kernel107 dirty delivery.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from copy import deepcopy
import sys,json,hashlib
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import dirty_delivery as old
ref=old.load();g=old.geometry(ref)
def require(ok,msg):
 if not ok:raise ValueError(msg)
lines=ref.roots();binary=[sum(((ref.inner(r,s)+1)&1)<<j for j,s in enumerate(lines)) for r in lines]
ind=[];ix=[]
for i,row in enumerate(binary):
 if not ref.in_span(row,ind):ind.append(row);ix.append(i)
labels=[sum(((row>>j)&1)<<k for k,j in enumerate(ix)) for row in binary]
byroot=dict(zip(lines,labels))
# Each selected root's pairings with a vector are literally its label coordinates.
# Extend that correspondence linearly to all 512 vectors.
functionals={0:0}
for k,i in enumerate(ix):
 for v,f in list(functionals.items()):functionals[v^labels[i]]=f^(1<<k)
require(len(functionals)==512,'nondegenerate pairing')
def pair(v,w):return (functionals[v]&w).bit_count()%2
def perp(frame):return list(ref.basis([v for v in range(512) if all(pair(v,a)==0 for a in frame)]))
def eq(a,b):return ref.rank(a)==ref.rank(b)==ref.rank(a+b)
for r,a in zip(lines,labels):
 for s,b in zip(lines,labels):require(pair(a,b)==(ref.inner(r,s)+1)%2,'pairing reconstruction')
full=[1<<i for i in range(9)]

# T has the same 104 distinct support masks as D, so reuse the pinned schedule
# by matching masks. Its direct query inputs are singleton b_k frames; no copy.
w=old.build(); masksT=[sum(bool(x)<<k for k,x in enumerate(row)) for row in g['t']]
require(set(masksT)==set(g['masks']) and len(set(masksT))==104,'support isomorphism')
perm={t:masksT.index(mask) for t,mask in enumerate(g['masks'])}
blabel=[byroot[b] for a,b in g['pairs']]
def fmap(frame):
 # Scatter carrier/target frames in the original witness are spans of a_k.
 # Replace those basis vectors linearly by b_k; final target H is explicit.
 spans={0:0}
 for a,b in zip(g['labels'],blabel):
  for v,f in list(spans.items()):spans[v^a]=f^b
 return list(ref.basis([spans[x] for x in frame]))
# Rebuild chronological scatter using the same events but direct singleton Q.
initial={f'Q{k}':[blabel[k]] for k in range(8)}
initial.update({f'H{i}':[] for i in range(32)})
initial.update({f'Y{t}':[] for t in range(104)})
cur=deepcopy(initial);p=[]
def move(r,f):
 if not eq(cur[r],f):p.append(['transport',r,cur[r],f,len(f)-len(cur[r])]);cur[r]=f
# Original programme contains precompensation then injections then reads.
for e in w['program']:
 op=e[0]
 if op in ['zero','copy','erase']:continue
 if op=='transport':
  _,r,a,b,cost=e
  if r=='C' or r.startswith('Q'):continue
  if r.startswith('Y'):
   t=perm[int(r[1:])];r=f'Y{t}'
   dest=perp([byroot[g['ports'][t]]]) if len(b)==8 else fmap(b)
  else:dest=full if len(b)==9 else fmap(b)
  move(r,dest)
 elif op=='add':
  _,r,s,c,f=e
  if s=='C':
   k=w['carriers'][int(r[1:])][0];s=f'Q{k}';f=[blabel[k]]
  elif r.startswith('Y'):
   t=perm[int(r[1:])];r=f'Y{t}';k=w['carriers'][int(s[1:])][0]
   c=g['t'][t][k]*(-1 if not f else 1);f=[] if not f else fmap(f)
  elif r.startswith('H') and s.startswith('Q'):
   move(s,full);f=full
  p.append(['add',r,s,c,f])
for k in range(8):move(f'Q{k}',full)
# Adjoint: reverse events, transpose each scalar elementary operation and
# replace every frame by its orthogonal complement. No private state needed.
gather=[]
rename=lambda r:('X'+r[1:] if r.startswith('Y') else 'G'+r[1:] if r.startswith('H') else r)
for e in reversed(p):
 if e[0]=='add':_,r,s,c,f=e;gather.append(['add',rename(s),rename(r),c,perp(f)])
 else:_,r,a,b,c=e;gather.append(['transport',rename(r),perp(b),perp(a),c])
for k in range(8):require(eq(perp([blabel[k]]),g['source_frames'][k]),'gather/delivery boundary')
# Cancel initial query dirt at zero, gather, deliver D/4, then restore queries.
program=[]
for t,row in enumerate(g['d']):
 for k,c in enumerate(row):
  if c:program.append(['add',f'Y{t}',f'Q{k}',-Q(c,4),[]])
program+=gather
for e in w['program']:
 z=deepcopy(e)
 for i in [1,2] if e[0] in ['add','copy'] else [1]:
  if isinstance(z[i],str) and z[i].startswith('H'):z[i]='D'+z[i][1:]
 if z[0]=='add' and z[1].startswith('Y'):z[3]=Q(z[3],4)
 program.append(z)
for k in range(8):
 for s,row in enumerate(g['t']):
  if row[k]:program.append(['add',f'Q{k}',f'X{s}',-row[k],full])
start={f'X{s}':[byroot[r]] for s,r in enumerate(g['ports'])}
start.update({f'Y{t}':[] for t in range(104)})
start.update({f'Q{k}':[] for k in range(8)})
start.update({f'{h}{i}':[] for h in ['G','D'] for i in range(32)})

def audit(es,check=True):
 frames=deepcopy(start);rows={r:{r:Q(1)} for r in start};paid=Counter();phasepaid={'gather':Counter(),'delivery':Counter()};maxl1=Q(1)
 for index,e in enumerate(es):
  op=e[0]
  if op=='transport':
   _,r,a,b,c=e;require(eq(frames[r],a),'transport start '+str(index))
   require(c==abs(ref.rank(a)-ref.rank(b)) and c>0,'rank')
   require(all(ref.in_span(x,b) for x in a) if r!='C' else all(ref.in_span(x,a) for x in b),'monotone')
   frames[r]=b;paid[c]+=1
  elif op=='add':
   _,r,s,c,f=e;require(eq(frames[r],f) and eq(frames[s],f),'add frame '+str(index))
   for j,v in list(rows[s].items()):
    value=rows[r].get(j,Q(0))+c*v
    if value:rows[r][j]=value
    else:rows[r].pop(j,None)
  elif op=='zero':
   _,r,f=e;require(r not in frames,'zero');frames[r]=f;rows[r]={}
  elif op=='copy':
   _,r,s,f=e;require(not rows[r] and eq(frames[r],f) and eq(frames[s],f),'copy');rows[r]=dict(rows[s])
  elif op=='erase':
   _,r,f=e;require(eq(frames[r],f),'erase');del frames[r];del rows[r]
  else:raise ValueError(op)
  maxl1=max(maxl1,max(sum(abs(v) for v in row.values()) for row in rows.values()))
 require(set(rows)==set(start),'private lifetime')
 if check:
  for r in start:
   expected={r:Q(1)};end=full
   if r.startswith('Y'):
    t=int(r[1:]);end=g['target_frames'][t]
    for s,root in enumerate(g['ports']):
     c=Q(ref.inner(g['ports'][t],root),2)
     if c:expected[f'X{s}']=c
   require(rows[r]==expected,'endpoint '+r);require(eq(frames[r],end),'final frame '+r)
 return dict(columns=len(start),events=len(es),paid_profile=dict(sorted(paid.items())),rank_mass=sum(k*v for k,v in paid.items()),prefix_l1=str(maxl1),helpers=72,helper_widths={9:72})
if __name__=='__main__':
 r=audit(program);controls={}
 final={r:(g['target_frames'][int(r[1:])] if r.startswith('Y') else full) for r in start}
 witness=dict(initial_frames=start,final_frames=final,program=program)
 (Path(__file__).resolve().parent/'LOWRANK-WITNESS.json').write_text(json.dumps(witness,default=str)+'\n')
 for name,index in [('missing_initial_query_compensation',0),('missing_final_query_cleanup',len(program)-1)]:
  mutant=deepcopy(program);mutant.pop(index)
  try:audit(mutant)
  except ValueError as e:controls[name]=str(e)
  else:raise ValueError('control accepted')
 r.update(status='PASS_EXACT_P104_LOW_RANK_CHANNEL_FRAME_MODEL',controls=controls,scope='Complete low-rank G/2 channel only. Missing I-G/2 side correction, concrete phase recipes, global hosting and kappa. All 72 helpers are arbitrary dirty inputs restored at full frame.',gather_private_copy_cost=0,delivery_private_copy_cost=56)
 r['input_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'dirty_delivery.py',old.SOURCE/'SCHEDULE.json',old.SOURCE/'verify.py']}
 out=Path(__file__).resolve().parent/'RESULT.json';out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
