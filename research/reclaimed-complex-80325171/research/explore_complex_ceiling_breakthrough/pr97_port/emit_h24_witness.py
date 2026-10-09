import sys,os
if sys.flags.optimize or os.environ.get("PYTHONOPTIMIZE"):
 raise RuntimeError("Optimized Python is not permitted for scientific checks")
"""Original exact two-term relation screen; no dirty physical word emitted."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from witness_tools import Writer,expression
import struct,hashlib
_own_file=__file__; __file__=str(Path(__file__).parent/'screen_joint.py')
exec(compile(Path(__file__).read_text(),__file__,'exec'))
__file__=_own_file
from collections import defaultdict,Counter
import time,json,resource
expected=json.loads((root/'TWO_TERM_SCREEN.json').read_text())
graph_file=root/'H24_GRAPH.bin'
with graph_file.open('wb') as f:
 f.write(struct.pack('<4I',h,g.v,len(alive),len(roots)))
 for x in sorted(alive):
  aa,bb=g.a[x]or(0,0);f.write(struct.pack('<7I',x,aa,bb,g.c[x],g.u[x],g.r[x],g.ty[x]))
 for x in roots:f.write(struct.pack('<I',x))
header=dict(version=1,head='f5f9c56e637463cac1e300d1589ccf42838f688a',h=h,v=g.v,R=expected['profile']['R'],graph_sha256=hashlib.sha256(graph_file.read_bytes()).hexdigest(),graph_file=graph_file.name,initial_original_dirty_roles=list(range(expected['profile']['R'])),initial_frame=0,initial_fresh_signals='V injections only; zero elsewhere',coefficient_encoding='[numerator,positive_denominator]; real rational',terminal_order='20240 exact split side occurrences followed by E0..22 and T; see H24_TERMINALS.json',source_storage='Read-only2024 source streams,2024 distinct targets,all original auxiliary roles disjoint',expected_positive_children=expected['profile']['child_histogram'])
header['source_hashes']={str(p.relative_to(root.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),root/'witness_tools.py',root/'screen_joint.py',root/'screen_groups.py',root/'reconstruct_h24.py']}
triple_id={t:i for i,t in enumerate(g.triples)}
terminal_data=dict(sides=[[j,x,triple_id[t],sg,2]for j,(t,x,sg)in enumerate(pieces)],centers=[dict(index=i,node=x,name=['E',i]if i<h-1 else['T'])for i,x in enumerate(centers)])
(root/'H24_TERMINALS.json').write_text(json.dumps(terminal_data,separators=(',',':'))+'\n')
header['terminal_binding_sha256']=hashlib.sha256((root/'H24_TERMINALS.json').read_bytes()).hexdigest()
header['stage2_exterior']='Actual paid552 entrance C_B; no translated-gauge exit substitution'
header['data_classes']='Two529 connectors;four23 fronts;inverse rank1 endpoint copy;pretranslate P_U*1;negate;bankexchange'
writer=Writer(root/'H24_EVENTS.jsonl.gz',header)
chosen=selected.copy()
selected_by_block=defaultdict(list)
for uid,(k,i) in chosen.items():selected_by_block[k].append((uid,i))
# Every ordinary node is interned by exact source support. Centre nodes use exact packed integer vectors.
key=[None]*len(g.a)
for x in sorted(alive):
 if g.ty[x]!=3:key[x]=g.s[x]
 else:
  # A tagged integer-lane vector prevents mistaking B-centre multiplicity for ordinary support.
  def coeff_of(y):
   if g.ty[y]==3:return key[y][1]
   bits=g.s[y];out=0
   while bits:
    bit=bits&-bits;bits-=bit;out|=1<<(5*(bit.bit_length()-1))
   return out
  aa,zz=g.a[x];key[x]=('integer',coeff_of(aa)+coeff_of(zz))
node_for_key={key[x]:x for x in sorted(alive)}
parents=defaultdict(list)
for x in sorted(alive):
 if g.a[x]:
  a,b=g.a[x];parents[a].append((x,b));parents[b].append((x,a))
relation_types=Counter();relation_probes=0
# source index mapping identity preserves exact coefficients on arbitrary source data.
ins_uid={}
for uid,(y,k,terminal) in enumerate(uses):
 if not terminal:ins_uid[k,y]=uid
frames=[];sig=[];state=[];assigned={};pending_next={};pending_sig=defaultdict(set);retired_sig=defaultdict(set);retired_rank=[set() for _ in range(h+1)]
candidate_rank=[set() for _ in range(h+1)]
ret_all=0;ret_kind=[0]*4;ret_cover=[0]*h;ret_core=[0]*h;ret_rank_bits=[0]*(h+1)
def idx(s,add):
 global ret_all
 bit=1<<s;F=frames[s];t=g.ty[F];r=g.r[F]
 if add:ret_all|=bit;ret_kind[t]|=bit;ret_rank_bits[r]|=bit
 else:ret_all&=~bit;ret_kind[t]&=~bit;ret_rank_bits[r]&=~bit
 for j in range(h):
  if g.u[F]>>j&1:
   if add:ret_cover[j]|=bit
   else:ret_cover[j]&=~bit
  if g.c[F]>>j&1:
   if add:ret_core[j]|=bit
   else:ret_core[j]&=~bit
def eligible(E):
 t=g.ty[E];mask=g.u[E];core=g.c[E]
 if t==1:
  bits=ret_kind[1]
  for j in range(h):
   if core>>j&1:bits&=ret_core[j]
 elif t==2:bits=ret_all if mask==(1<<h)-1 else ret_kind[1]|ret_kind[2]
 else:
  j=core.bit_length()-1
  # Type2 coordinate subsets of the singleton core are absent; verify selected control directly.
  bits=(ret_kind[1]&ret_core[j])|(ret_kind[3]&ret_core[j])
  coord=ret_kind[2]
  for k in range(h):
   if k!=j:coord&=~ret_cover[k]
  return bits|coord
 for j in range(h):
  if not(mask>>j&1):bits&=~ret_cover[j]
 return bits
def bit_indices(bits):
 while bits:
  bit=bits&-bits;bits-=bit;yield bit.bit_length()-1
H2=Counter();reclaims=Counter();raised_controls=Counter();created=0;basis_scalars=0;clearing_probes=0
def refresh(z):
 active=len(retired_sig[z])+len(pending_sig[z])>=2
 for s in retired_sig[z]:
  if active:candidate_rank[g.r[frames[s]]].add(s)
  else:candidate_rank[g.r[frames[s]]].discard(s)
sstart=time.monotonic()
def new(E,value):
 global created
 s=len(frames);frames.append(E);sig.append(value);state.append('local');H2[g.r[E]]+=1;created+=1;writer.write('activate',s,0,E);
 if value:writer.write('inject',s,E-1,[1,1],E)
 return s

def raise_(s,E):
 old=frames[s];assert contains(old,E)
 if old!=E and state[s]=='retired':idx(s,False)
 if old!=E:
  if state[s]=='retired':
   retired_rank[g.r[old]].remove(s);retired_rank[g.r[E]].add(s)
   if s in candidate_rank[g.r[old]]:candidate_rank[g.r[old]].remove(s);candidate_rank[g.r[E]].add(s)
  H2[g.r[E]-g.r[old]]+=1;writer.write('raise',s,old,E);frames[s]=E
  if state[s]=='retired':idx(s,True)

def pending(s,uid):
 assert s not in pending_next;state[s]='pending';pending_next[s]=uid;pending_sig[sig[s]].add(s);assigned[uid]=s;refresh(sig[s]);writer.write('promise',uid,s,uses[uid][0],blocks[uses[uid][1]]['nodes'][0],uses[uid][2])

def consume(s):
 uid=pending_next.pop(s);writer.write('consume',uid,s);pending_sig[sig[s]].remove(s);state[s]='local';refresh(sig[s])

def retire(s):
 assert state[s]=='local';state[s]='retired';retired_sig[sig[s]].add(s);retired_rank[g.r[frames[s]]].add(s);idx(s,True);refresh(sig[s]);writer.write('retire',s,frames[s])

def acquire(E,anchors):
 global clearing_probes,relation_probes
 b=g.r[E];anchor_keys=defaultdict(list)
 for s in anchors:anchor_keys[sig[s]].append(s)
 anchored_rank=defaultdict(set)
 for z in anchor_keys:
  for q in retired_sig[z]:anchored_rank[g.r[frames[q]]].add(q)
 # Exact duplicate index removes only candidates with no possible equal-signal control.
 # highest-rank eligible retired role first. The exact ordering is frozen; no schedule search.
 legal=eligible(E)
 for a in range(b,0,-1):
  for s in bit_indices(legal&ret_rank_bits[a]):
   clearing_probes+=1
   z=sig[s];rs=retired_sig[z];ps=pending_sig[z]
   # Two-term dependencies can clear a signal without an equal-signal control.
   assert contains(frames[s],E)
   control=None
   for q in anchor_keys.get(z,()):
    if q!=s and contains(frames[q],E):control=q;break
   if control is None:
    for q in sorted(ps):
     _,k,terminal=uses[pending_next[q]]
     G=blocks[k]['nodes'][0]
     # Terminal controls may not move beyond their own native terminal frame.
     if contains(frames[q],E) and contains(E,G):control=q;break
   if control is None:
    for q in sorted(rs):
     if q!=s and contains(frames[q],E):control=q;break
   controllers=[];relation_type='duplicate'
   if control is not None:controllers=[control]
   else:
    def locate(zk,other=None):
     for q in anchor_keys.get(zk,()):
      if q!=s and q!=other and contains(frames[q],E):return q
     for q in sorted(pending_sig[zk]):
      if q==s or q==other:continue
      _,kg,_=uses[pending_next[q]];GG=blocks[kg]['nodes'][0]
      if contains(frames[q],E) and contains(E,GG):return q
     for q in sorted(retired_sig[zk]):
      if q!=s and q!=other and contains(frames[q],E):return q
     return None
    xn=node_for_key[z];relations=[]
    if g.a[xn]:
     aa,bb=g.a[xn];relations.append((aa,bb,'sum'))
    relations.extend((pp,other,'difference') for pp,other in parents[xn])
    for a_node,b_node,kind in relations:
     relation_probes+=1
     za,zb=key[a_node],key[b_node]
     if not(anchor_keys.get(za) or pending_sig[za] or retired_sig[za]):continue
     if not(anchor_keys.get(zb) or pending_sig[zb] or retired_sig[zb]):continue
     ca=locate(za)
     if ca is None:continue
     cb=locate(zb,ca)
     if cb is None:continue
     # Relations come literally from x=a+b in the exact integer-coefficient DAG.
     if kind=='sum':assert g.a[xn]==(a_node,b_node)
     else:assert g.a[a_node] in ((xn,b_node),(b_node,xn))
     controllers=[ca,cb];relation_type=kind;break
   if not controllers:continue
   for control in controllers:
    c=g.r[frames[control]];raise_(control,E);raised_controls[c,b]+=1
   relation_types[relation_type]+=1
   raise_(s,E);idx(s,False);retired_sig[z].remove(s);retired_rank[b].remove(s);candidate_rank[b].discard(s);state[s]='local';refresh(z)
   if relation_type=='duplicate':assert sig[s]==sig[controllers[0]] # Exact equality.
   writer.scalar(s,[(q,-1 if relation_type!='difference' or j==0 else 1)for j,q in enumerate(controllers)],E);writer.write('reuse',s,E,relation_type);sig[s]=0;reclaims[a,b]+=1
   return s
 return new(E,0)

for step,k in enumerate(order):
 b=blocks[k];E=b['nodes'][0];outuses=[uid for uid in b['use_ids'] if uid not in chosen]
 outvalues=sorted({uses[uid][0] for uid in outuses});assert outvalues==sorted(set(b['outs']))
 if not b['ins']:
  for uid in outuses:
   s=new(E,key[E]);pending(s,uid)
 else:
  incoming=[assigned[ins_uid[k,y]] for y in b['ins']];assert len(set(incoming))==len(incoming)
  for s,y in zip(incoming,b['ins']):assert sig[s]==key[y];consume(s);raise_(s,E)
  bb=[];labels=[];matrix_rows=[];output_slots={}
  for x in outvalues:
   if ins(b['coeff'][x],bb):labels.append(('value',x));matrix_rows.append(b['coeff'][x])
  for uid,i in sorted(selected_by_block[k]):
   assert ins({i:1},bb);labels.append(('carry',(uid,b['ins'][i])));matrix_rows.append({i:F(1)})
  for i,y in enumerate(b['ins']):
   if ins({i:1},bb):labels.append(('retire',y));matrix_rows.append({i:F(1)})
  assert len(labels)==len(incoming)
  writer.block(incoming,matrix_rows,E,labels)
  for s,(kind,data) in zip(incoming,labels):
   if kind=='carry':uid,y=data;sig[s]=key[y];pending(s,uid)
   else:
    sig[s]=key[data]
    if kind=='value':output_slots[data]=s
    else:retire(s)
  independent_outputs=list(output_slots)
  for x in outvalues:
   if x not in output_slots:
    s=acquire(E,list(output_slots.values()));assert sig[s]==0;ee=expression([b['coeff'][y]for y in independent_outputs],b['coeff'][x]);writer.scalar(s,[(output_slots[independent_outputs[i]],q)for i,q in ee.items()],E);sig[s]=key[x];output_slots[x]=s
  used=set()
  for uid in outuses:
   x=uses[uid][0];s=output_slots[x]
   if x in used:
    s=acquire(E,list(output_slots.values()));assert sig[s]==0;writer.scalar(s,[(output_slots[x],F(1))],E);sig[s]=key[x]
   used.add(x);pending(s,uid)
 if step%5000==0:
  prog=dict(step=step,regions=len(order),created=created,reclaimed=sum(reclaims.values()),probes=clearing_probes,seconds=time.monotonic()-sstart,rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
  (root/'H24_WITNESS_PROGRESS.json').write_text(json.dumps(prog,indent=2)+'\n');print(json.dumps(prog),flush=True)
# Terminal cleanup and retained copied centres. All original auxiliary roles accounted.
terminal_slots=[]
for uid,(x,k,terminal) in enumerate(uses):
 if not terminal:continue
 s=assigned[uid];assert sig[s]==key[x];consume(s);E=blocks[k]['nodes'][0];raise_(s,E);terminal_slots.append(s)
 # exact roots order via uid's suffix
 j=uid-(len(uses)-len(roots));rr=g.r[E]
 if j<len(pieces):
  H2[h-1-rr]+=1;H2[1]+=1;writer.write('side_terminal',s,E,j,x,[pieces[j][2],2],h-1-rr,1,triple_id[pieces[j][0]])
 else:
  H2[rr]+=1;H2[h-rr]+=1;writer.write('center_terminal',s,E,j-len(pieces),x,rr,h-rr,'forward_copy_C_U_inverse;inverse_read_copy_C_U',['E',j-len(pieces)]if j-len(pieces)<h-1 else['T'])
 state[s]='terminal'
assert len(set(terminal_slots))==len(roots)
assert not pending_next
for s in range(len(frames)):
 if state[s]=='retired':H2[h-g.r[frames[s]]]+=1;writer.write('cleanup',s,frames[s],h-g.r[frames[s]])
 else:assert state[s]=='terminal'
assert len(frames)==base_R-len(chosen)-sum(reclaims.values())
assert sum(t*n for t,n in H2.items())==h*len(frames)+ell
ans=profile(len(frames),H2)
assert ans['R']==expected['profile']['R'] and {str(k):v for k,v in ans['histogram'].items()}==expected['profile']['histogram']
assert dict(relation_types)==expected['relation_types']
witness=writer.finish(ans)
(root/'H24_WITNESS_STATS.json').write_text(json.dumps(witness,indent=2)+'\n')
result=dict(status='Author exact fresh-signal and actual-binary-frame two-term DAG-relation reclamation screen; no emitted GL gate word, complete dirty replay, or accepted supplier',profile=ans,reclaimed=sum(reclaims.values()),relation_types=dict(relation_types),relation_probes=relation_probes,reclamation_rank_pairs={f'{a}->{b}':n for (a,b),n in sorted(reclaims.items())},control_raise_rank_pairs={f'{a}->{b}':n for (a,b),n in sorted(raised_controls.items())},probes=clearing_probes,seconds=time.monotonic()-sstart,rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
(root/'H24_WITNESS_REPLAY_SCREEN.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
