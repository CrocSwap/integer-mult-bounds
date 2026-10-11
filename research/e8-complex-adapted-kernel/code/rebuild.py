"""Frozen exact shared-donor kernel reconstruction; no optimizer.
Kernel discovery: DreamingOfClouds/Claude PR449. Exact release reconstruction:
chafreaky/OpenAI Codex. Apache-2.0. Usage: rebuild.py PARENT_FULL_WORD OUT_JSON.
"""
import copy,gzip,hashlib,json,sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ld=lambda p:json.loads(gzip.decompress(Path(p).read_bytes())) if str(p).endswith('.gz') else json.loads(Path(p).read_text())
w=ld(sys.argv[1]);expected=ld(ROOT/'data/word.json.gz');selection=ld(ROOT/'data/kernel.json')['classes']
v=120;R=w['report']['R'];n=240+R;assert R==560 and not w.get('start_extra') and not w.get('target_levels')
def basis(vectors):
 rows={}
 for x in vectors:
  for k in sorted(rows,reverse=True):
   if x>>k&1:x^=rows[k]
  if x:
   k=x.bit_length()-1
   for j in rows:
    if rows[j]>>k&1:rows[j]^=x
   rows[k]=x
 return tuple(rows[k] for k in sorted(rows,reverse=True))
def contained(a,b):return basis(list(a)+list(b))==basis(b)
def apply(e,rows):
 if e[0]=='scale':
  q=Q(e[2],e[3]);rows[e[1]]={i:q*z for i,z in rows[e[1]].items()}
 else:
  d,s=e[1:3];q=Q(e[3],e[4]);assert d!=s
  for i,z in list(rows[s].items()):
   a=rows[d].get(i,Q(0))+q*z
   if a:rows[d][i]=a
   else:rows[d].pop(i,None)
M=[{i:Q(1)} for i in range(n)]
for e in w['A']+w['cut']+w['B']:apply(e,M)
dirty=[{} for _ in range(n)]
for t in range(v,2*v):dirty[t]={i:z for i,z in M[t].items() if i>=240}
for e in w['precondition']:apply(e,dirty)
cols=[{t:dirty[v+t][240+h] for t in range(v) if 240+h in dirty[v+t]} for h in range(R)]
first={}
for e in w['A']+w['B']:
 for r in [e[1]]+([e[2]] if e[0]=='add' else []):
  if r>=240:first.setdefault(r-240,basis(e[-1]))
def solve(ds,p):
 a=[[cols[d].get(t,Q(0)) for d in ds]+[cols[p].get(t,Q(0))] for t in range(v)];row=0;piv=[]
 for j in range(len(ds)):
  k=next((k for k in range(row,len(a)) if a[k][j]),None)
  assert k is not None,'the selected donor columns must be independent'
  a[row],a[k]=a[k],a[row];q=a[row][j];a[row]=[z/q for z in a[row]]
  for k in range(len(a)):
   if k!=row and a[k][j]:
    q=a[k][j];a[k]=[u-q*z for u,z in zip(a[k],a[row])]
  piv.append(j);row+=1
 assert all(not a[k][-1] for k in range(row,len(a)))
 result={ds[j]:a[i][-1] for i,j in enumerate(piv) if a[i][-1]}
 assert all(cols[p].get(t,0)==sum(z*cols[d].get(t,0) for d,z in result.items()) for t in range(v))
 return result
pre=[];start={};roles=set();relations=[]
for g in selection:
 E=g['E'];ds=g['donors'];ps=g['pivots'];all_=ds+ps
 assert len(E)==1 and E[0].bit_count()%2==0 and len(set(all_))==len(all_) and not roles&set(all_);roles.update(all_)
 assert all(contained(E,first[h]) for h in all_)
 for p in ps:
  rel=solve(ds,p);start[240+p]=E
  for d,q in rel.items():pre.append(['add',240+d,240+p,-q.numerator,q.denominator,E])
  relations.append(dict(pivot=p,entrance=E,donors=[[d,str(q)] for d,q in rel.items()]))
assert len(start)==79 and len(selection)==14
out=copy.deepcopy(w);out['R']=R;out['A']=pre+out['A'];full=tuple(1<<i for i in range(8,-1,-1));out['cleanup']=[]
for e in reversed(out['A']+out['B']):
 if not v<=e[1]<2*v:
  q=copy.deepcopy(e)
  if q[0]=='add':q[3]*=-1
  else:q[2],q[3]=q[3],q[2]
  q[-1]=list(full);out['cleanup'].append(q)
out['start_extra']={str(r):E for r,E in start.items()};out['target_levels']={}
cur=[(p,) for p in w['ports']]+[()]*(v+R)
for r,E in start.items():cur[r]=basis(E)
paid=Counter()
def climb(r,F):
 F=basis(F);old=cur[r];assert contained(old,F)
 if old!=F:paid[len(F)-len(old)]+=1;cur[r]=F
for part in ('A','B'):
 if part=='B':
  assert all(cur[r]==basis(F) for r,F in zip(w['centers'],w['center_frames'])) and all(not cur[r] for r in range(v,2*v))
  for F in w['center_frames']:paid[len(basis(F))]+=1
 for e in out[part]:
  for r in [e[1]]+([e[2]] if e[0]=='add' else []):climb(r,e[-1])
for r in range(n):climb(r,basis([z for z in range(1,512) if not (z&w['ports'][r-v]).bit_count()%2]) if v<=r<2*v else full)
out['report']['local_profile']={str(k):z for k,z in paid.items()}
# These two parent discovery estimates vary in the last float bits across platforms.
# They are provenance metadata, never an input to exact reconstruction or pricing.
metadata=['complex_coarse_float','gain_percent_float']
for key in metadata:
 assert isinstance(out['report'][key],float) and isinstance(expected['report'][key],float)
 assert abs(out['report'][key]-expected['report'][key])<1e-12
 out['report'][key]=expected['report'][key]
assert out==expected,'frozen kernel word is not the selected exact reconstruction'
result=dict(status='PASS_EXACT_COMPLEX_KERNEL_REBUILD',pivots=79,entrance_rank=79,distinct_entrances=14,pre_additions=len(pre),
 canonical_word_sha256=hashlib.sha256(json.dumps(out,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
 local_profile=dict(sorted(paid.items())),frozen_discovery_float_metadata=metadata,relations=relations,all_response_relations_exact=True,all_first_frames_contain_entrances=True)
Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n');print(result['status'],len(pre),'pre additions')
