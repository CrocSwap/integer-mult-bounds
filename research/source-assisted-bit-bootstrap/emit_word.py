"""Source-assisted BIT global word: exact finite construction, no optimized Python."""
if not __debug__: raise RuntimeError("Exact verifier requires assertions; do not use -O")
from pathlib import Path
import sys,json,hashlib
from collections import defaultdict,Counter
HERE=Path(__file__).resolve().parent
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,required=True);args=ap.parse_args();BASE=args.output_dir.resolve();BASE.mkdir(parents=True,exist_ok=True)
REF=HERE.parents[1]
sys.path.insert(0,str(HERE))
import common_frame_network184 as N
save={}; original=N.aligned_rewrite
def capture(chk,edges,roots,injections,dim):
 out=original(chk,edges,roots,injections,dim)
 save.update(chk=chk,oldedges=edges,roots=roots,injections=injections,newedges=out[0],newinj=out[1],controls=out[2])
 return out
N.aligned_rewrite=capture
network=N.build(REF,True,True);network['source']='github:eumemic/integer-mult-bounds@2c4a380126640abfcdce398ced255d1dd5d1d007';network['source_assisted_origin']='CrocSwap/integer-mult-bounds PR184@4b5fc7fb45a77b6c7b9d886d30ad5b57eae553fa';(BASE/'current168-network.json').write_text(json.dumps(network,sort_keys=True)+'\n'); chk=save['chk']; chk.frames(); chk.decoder(); chk.geometry()
g,w=chk.g,chk.w; dims=chk.dimf; dim=lambda v:dims[v[1]]
oldorder=sorted(w['phase1'])+[i for i in range(len(w['ops'])) if i not in set(w['phase1'])]
oldpset=set(w['phase1']); oldphase=lambda i:int(i not in oldpset)
oldcontent={int(s):1<<int(x) for x,s in w['sources'].items()}; current={int(s):(0,w['source_frame'][int(x)]) for x,s in w['sources'].items()}
edge_roles=defaultdict(list); last={}
def move(s,v):
 if s in current and current[s]!=v and oldcontent.get(s,0): edge_roles[current[s],v,oldcontent[s]].append(s)
 current[s]=v
for i in oldorder:
 a,b,_=w['ops'][i]; v=(oldphase(i),w['op_frame'][i]); move(a,v);move(b,v); oldcontent[a]=oldcontent.get(a,0)^oldcontent.get(b,0);last[a]=last[b]=v
for root,s,f in zip(g['roots'],w['rootroles'],w['root_frame']):move(s,(int(root['kind']!='center'),f))
assert not [(v,r) for v,r in save['roots'].items() if dim(v)<=3]
assert all(len(set(s))==1 for (u,v,m),s in edge_roles.items() if dim(u)<=3<dim(v)), 'duplicated boundary physical roles'
print('network captured',flush=True)
# Graph edges carry one independent physical row each. All low vertices have independent C modulo E.
inc=defaultdict(list);out=defaultdict(list)
for (u,v),rows in save['newedges'].items():
 for mask in rows:
  edge=(u,v,mask);out[u].append(edge);inc[v].append(edge)
vertices=sorted({v for v in set(inc)|set(out)|set(save['newinj'])|set(save['controls']) if dim(v)<=3},key=lambda x:(x[0],dim(x),x))
ops=[];chains=[];fresh=[];edge_slot={};retired=defaultdict(list);phaseops=[[],[]]; old_to_new={}; matrices=[]
def newslot():
 s=len(chains); chains.append([]);fresh.append(0);return s
def touch(s,f):
 if not chains[s] or chains[s][-1]!=f:
  assert not chains[s] or chk.sub(chains[s][-1],f),(s,chains[s][-1],f)
  chains[s].append(f)
def gate(a,b,v,external=False):
 touch(a,v[1])
 if external:
  assert chk.in_frame(chk.chi[b],v[1]); fresh[a]^=1<<b
 else: touch(b,v[1]);fresh[a]^=fresh[b]
 item=['x' if external else 'a',a,b,v[1]]; phaseops[v[0]].append(item)
def matrix_word(M):
 n=len(M); A=list(M); reductions=[]
 for col in range(n):
  pivot=next(i for i in range(col,n) if A[i]>>col&1)
  if pivot!=col:
   for a,b in [(col,pivot),(pivot,col),(col,pivot)]: A[a]^=A[b]; reductions.append((a,b))
  for i in range(n):
   if i!=col and A[i]>>col&1:A[i]^=A[col];reductions.append((i,col))
 assert A==[1<<i for i in range(n)]
 return list(reversed(reductions))
for vertex in vertices:
 C=[];slots=[]
 for edge in sorted(inc[vertex]):
  slots.append(edge_slot[edge]);C.append(edge[2]);touch(slots[-1],vertex[1])
 for mask in save['newinj'].get(vertex,[]):
  assert mask.bit_count()==1
  s=newslot();gate(s,mask.bit_length()-1,vertex,True);slots.append(s);C.append(mask)
 outgoing=sorted(out[vertex]);D=[e[2] for e in outgoing];E=sorted(save['controls'].get(vertex,()))
 if E:
  assert not C
  express=N.expressions(E)
  for edge,mask in zip(outgoing,D):
   s=newslot(); coeff=express(mask)
   for i,e in enumerate(E):
    if coeff>>i&1: assert e.bit_count()==1;gate(s,e.bit_length()-1,vertex,True)
   edge_slot[edge]=s
  continue
 assert len(N.F2Basis(C))==len(C)
 expr=N.expressions(C); desired=[expr(d) for d in D]
 n=len(C);t=len(D);r=len(N.F2Basis(D));b=max(0,t-r)
 slots.extend(newslot() for _ in range(b));M=[];basis=N.F2Basis();dirty=0
 for row in desired:
  if not basis.add(row):
   row^=1<<(n+dirty);dirty+=1;assert basis.add(row)
  M.append(row)
 assert dirty==b
 for i in range(n):
  row=1<<i
  if basis.add(row):M.append(row)
 assert len(M)==len(slots)==n+b
 for a,b0 in matrix_word(M):gate(slots[a],slots[b0],vertex)
 for edge,s in zip(outgoing,slots):
  assert fresh[s]==edge[2],(vertex,edge,fresh[s]);edge_slot[edge]=s
 for s in slots[t:]:retired[vertex].append(s)
 matrices.append([vertex,n,t,b,M])
# Bind each new low exit to its original high-word physical role.
for edge,s in edge_slot.items():
 u,v,mask=edge
 if dim(v)>3:
  old=next(iter(set(edge_roles[edge])));assert old not in old_to_new or old_to_new[old]==s;old_to_new[old]=s
# Match old low terminal roles with new complements at the exact same last vertex.
oldroots=set(w['rootroles']); donor_old={a for a,b in w['pairs']}
oldretired=defaultdict(list)
for s,v in last.items():
 if dim(v)<=3 and s not in oldroots:oldretired[v].append(s)
for vertex,olds in oldretired.items():
 news=retired[vertex]; required=[s for s in sorted(olds) if s in donor_old]
 assert len(required)<=len(news),(vertex,len(required),len(news))
 for a,b in zip(required,news):old_to_new[a]=b
 for a,b in zip([s for s in sorted(olds) if s not in donor_old],news[len(required):]):old_to_new[a]=b
# Every remaining high-only role receives an independent dirty coordinate.
for i in oldorder:
 if dims[w['op_frame'][i]]<=3:continue
 for s in w['ops'][i][:2]:
  if s not in old_to_new:old_to_new[s]=newslot()
for s in w['rootroles']:assert s in old_to_new
lowR=len(chains)
# High suffix remains literal in each phase. Reindex reads against first following high operation.
newops=[];oldpos_to_new={};oldposition={i:p for p,i in enumerate(oldorder)}
for phase in (0,1):
 newops.extend(phaseops[phase])
 for i in oldorder:
  if oldphase(i)!=phase:continue
  oldpos_to_new[oldposition[i]]=len(newops)
  if dims[w['op_frame'][i]]<=3:continue
  a,b,x=w['ops'][i];a,b=old_to_new[a],old_to_new[b];f=w['op_frame'][i]
  touch(a,f);touch(b,f);fresh[a]^=fresh[b];assert fresh[a]==chk.sup[x],('high value',i)
  newops.append(['a',a,b,f])
 if phase==0:cut=len(newops)
for r,s,f in zip(g['roots'],w['rootroles'],w['root_frame']):
 assert fresh[old_to_new[s]]==chk.sup[r['node']]
 touch(old_to_new[s],f)
oldcut=len(w['phase1']); gauges=[]
for z in w['gauges']:
 z=dict(z);old=z['role'];z['role']=old_to_new[old]
 oldread=w.get('reads',{}).get(str(old),oldcut)
 z['read']=oldpos_to_new[oldread];gauges.append(z)
pairs=[[old_to_new[a],old_to_new[b]] for a,b in w['pairs']]
# Reads originally at the phase cut remain before the new phase-1 low network;
# paired low donors with such a read must already die in phase zero (checked below).
for z in gauges:
 old=next(s for s,n in old_to_new.items() if n==z['role'])
 if w.get('reads',{}).get(str(old),oldcut)==oldcut:z['read']=cut
R=len(chains); when={z['role']:(z['read'],i) for i,z in enumerate(reversed(gauges))}
roleops=defaultdict(list)
for i,op in enumerate(newops):
 roleops[op[1]].append(i)
 if op[0]=='a':roleops[op[2]].append(i)
for z in gauges:
 s=z['role'];assert cut<=z['read']<=roleops[s][0]
 assert chk.sub(z['frame'],chains[s][0])
for a,b in pairs:
 assert roleops[a][-1]<when[b][0],('donor deadline',a,b)
 assert chk.sub(chains[a][-1],next(z['frame'] for z in gauges if z['role']==b))
rootroles=[old_to_new[s] for s in w['rootroles']]
# All-column response uses every elementary XOR; X controls do not contribute old scratch.
response=[0]*R
for root,s in zip(g['roots'],rootroles):
 for t in root['targets']:response[s]^=1<<t
for op in reversed(newops):
 if op[0]=='a':response[op[2]]^=response[op[1]]
for z in gauges:assert response[z['role']]==sum(1<<t for t in z['targets'])
model=dict(source_head='2c4a380126640abfcdce398ced255d1dd5d1d007',R=R,v=chk.v,h=chk.h,ops=newops,cut=cut,roots=g['roots'],rootroles=rootroles,rootframes=w['root_frame'],gauges=gauges,pairs=pairs,chains=chains,response=[hex(x) for x in response],k=chk.k,old_to_new={str(k):v for k,v in old_to_new.items()},full_frame=w['full_frame'])
(BASE/'emitted-word.json').write_text(json.dumps(model,separators=(',',':')))
print(json.dumps(dict(R=R,physical_R=R-len(pairs),ops=len(newops),cut=cut,low_matrices=len(matrices),low_controls=sum(o[0]=='x' for o in newops),pairs=len(pairs),gauges=len(gauges))),flush=True)
