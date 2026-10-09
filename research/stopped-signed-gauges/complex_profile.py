#!/usr/bin/env python3
"""Exact binary target-cap/chain screen on a frozen complex literal word.
Exploratory complete rank ledger only; no new reordered physical contract claim.
"""
from pathlib import Path
from itertools import combinations
from collections import Counter
from functools import lru_cache
import json,gzip,argparse,hashlib,time,math,struct
from collections import defaultdict
HERE=Path(__file__).resolve().parent
if not __debug__:raise SystemExit("Assertions required")

def basis(rows):
 E={}
 for x in rows:
  for p,b in sorted(E.items(),reverse=True):
   if x>>p&1:x^=b
  if x:
   p=x.bit_length()-1
   for q,b in list(E.items()):
    if b>>p&1:E[q]=b^x
   E[p]=x
 return tuple(E[p]for p in sorted(E,reverse=True))
@lru_cache(maxsize=300000)
def null(B,h):
 piv={b.bit_length()-1:b for b in B};out=[]
 for j in range(h):
  if j not in piv:out.append((1<<j)|sum(((b>>j)&1)<<p for p,b in piv.items()))
 return basis(out)
def inside(A,B):
 for x in A:
  for b in B:
   if x>>(b.bit_length()-1)&1:x^=b
  if x:return False
 return True
@lru_cache(maxsize=300000)
def intersect(A,B,h):return null(basis(null(A,h)+null(B,h)),h)
def nondeg(A):
 gram=[sum(((x&y).bit_count()%2)<<j for j,y in enumerate(A))for x in A]
 return len(basis(gram))==len(A)
def ndpart(A):
 work=list(A);out=[]
 while work:
  odd=next((i for i,x in enumerate(work)if x.bit_count()%2),None)
  if odd is not None:
   x=work.pop(odd);out.append(x);work=[y^x if (x&y).bit_count()%2 else y for y in work]
  else:
   pair=next(((i,j)for i,x in enumerate(work)for j,y in enumerate(work[:i])if (x&y).bit_count()%2),None)
   if pair is None:break
   i,j=pair;x,y=work[i],work[j];out.extend([x,y]);work=[z^ (x if (z&y).bit_count()%2 else 0) ^ (y if (z&x).bit_count()%2 else 0)for k,z in enumerate(work)if k not in pair]
 B=basis(out);assert nondeg(B)and inside(B,A);return B

def screen(word,out):
 st=time.time();blob=word.read_bytes();d=json.loads(gzip.decompress(blob));h,v,R=d['h'],d['v'],d['R'];trip=list(combinations(range(h),3));lines=[sum(1<<j for j in T)for T in trip];tid={T:i for i,T in enumerate(trip)}
 root_targets=list(range(v));root_sign=[1]*v
 for a,b in combinations(range(h),2):
  order=sorted((i for i in range(h)if i not in(a,b)),key=lambda i:((i^1)in(a,b),i))
  for i in order:root_targets.append(tid[tuple(sorted((a,b,i)))]);root_sign.append(-1)
 assert len(root_targets)==4*v
 bound=[0]*R;centers=[0]*R
 for s,j,k in d['outputs']:
  if k:centers[s]=1
  else:bound[s]+=1
 for a,b in reversed(d['ops']):bound[b]+=bound[a];centers[b]|=centers[a]
 maxb=max(bound);bits=1
 while (1<<(bits-1))<=maxb:bits*=2
 # Absolute coefficient bound follows by reverse triangle inequality, including
 # any path multiplicity. Each signed packed lane stays strictly within guard.
 cov=[0]*R
 for s,j,k in d['outputs']:
  if not k:cov[s]+=root_sign[j]<<(bits*root_targets[j])
 for a,b in reversed(d['ops']):cov[b]+=cov[a]
 low=sum(1<<(bits*j)for j in range(v));guard=low<<(bits-1);free=set(range(R))-set(d['center_touched']);assert all(not centers[s]for s in free)
 masks={};targetlists={};first={}
 @lru_cache(maxsize=None)
 def frame(node):
  typ,c,u,r=d['frames'][node]
  if typ==2:B=basis(1<<j for j in range(h)if u>>j&1)
  elif c.bit_count()==3:B=(c,)
  else:
   assert typ==1 and c.bit_count()==2;B=basis(c|(1<<j)for j in range(h)if u>>j&1 and not c>>j&1)
  assert len(B)==r and nondeg(B);return B
 edges=zero=0
 for s in sorted(free):
  x=(cov[s]+guard)^guard
  shift=1
  while shift<bits:x|=x>>shift;shift*=2
  mask=x&low;ts=[];plain=0
  while mask:
   z=mask&-mask;mask-=z;t=(z.bit_length()-1)//bits;ts.append(t);plain|=1<<t
  masks[s]=plain;targetlists[s]=tuple(ts);first[s]=frame(d['starts'][s]);edges+=len(ts);zero+=not ts
  assert all(not((row&lines[t]).bit_count()%2)for t in ts for row in first[s])
 print('exact target caps',len(free),'edges',edges,'zero',zero,'bound',maxb,'bits',bits,'seconds',round(time.time()-st,2),flush=True)
 # Every selected target sees a monotone chain. Drop zero selections from this
 # order and perform all their original readouts in the zero-frame phase.
 order=sorted(free,key=lambda s:(len(first[s]),s));nxt=[null((u,),h)for u in lines];sigma={};repairs=Counter()
 for j,s in enumerate(reversed(order)):
  S=first[s]
  for B in set(nxt[t]for t in targetlists[s]):
   S=intersect(S,B,h)
   if not S:break
  if S and not nondeg(S):old=len(S);S=ndpart(S);repairs[old,len(S)]+=1
  if S:
   sigma[s]=S
   for t in targetlists[s]:nxt[t]=S
  if j%5000==0:print('chains',j,'positive',len(sigma),'seconds',round(time.time()-st,2),flush=True)
 seqs=[[]for _ in trip];last=[()for _ in trip]
 for s in order:
  if s not in sigma:continue
  S=sigma[s];assert inside(S,first[s])and nondeg(S)
  for t in targetlists[s]:assert inside(last[t],S);last[t]=S;seqs[t].append(len(S))
 # Complete rank-only complex ledger from the stopped one-child residual rule.
 row=json.loads((word.parent/'producer.json').read_text());H=Counter({i:n for i,n in enumerate(row['histogram'])});H[h]-=h;H[1]+=h
 m=h*h;N=v*v;W=2*N+2*v*R;full=Counter({r:n*2*v for r,n in H.items()});full[m-h]+=2*v*R;full[(h-1)**2]+=2*N;full[h-1]+=4*N;full[1]+=N
 for s,S in sigma.items():
  r=len(first[s]);f=len(S);full[r]-=2*v;full[r-f]+=2*v;full[m-h]-=2*v;full[m-h+f]+=2*v
 for seq in seqs:
  levels=sorted(set([0,h-1]+seq));full[h-1]-=2*v
  for a,b in zip(levels,levels[1:]):full[b-a]+=2*v
 full.pop(0,None);assert all(n>=0 for n in full.values());mass=sum(r*n for r,n in full.items());assert mass==W*m-N+2*v*h*(h-1)
 result=dict(status='EXACT_SIGNED_GEOMETRY_AND_RANK_INVENTORY',h=h,R=R,center_free_roles=len(free),signed_lane_absolute_bound=maxb,signed_lane_bits=bits,exact_nonzero_readout_edges=edges,zero_covector_roles=zero,all_first_frames_inside_all_exact_signed_target_caps=True,selected_positive_roles=len(sigma),sum_sigma_dimensions=sum(map(len,sigma.values())),sigma_dimensions=dict(sorted(Counter(map(len,sigma.values())).items())),nondegenerate_repairs={f'{a},{b}':n for(a,b),n in repairs.items()},all_binary_gram_and_chain_checks=True,m=m,W=W,rank_mass=mass,histogram=dict(sorted(full.items())),word_sha256=hashlib.sha256(gzip.decompress(blob)).hexdigest(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='Exact signed support, F2 first-frame caps, nondegenerate nested readout chains and conditional paid rank ledger. The separately executed gauge_check verifies the reordered signed dirty schedule; recursive bridge and assembly are separate checks.')
 out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');return result,dict(sigma=sigma,order=order,cov_masks=masks,first=first,seqs=seqs)

def build_word(work):
 raw=(work/'graph.bin').read_bytes();at=0
 def read(fmt,n):
  nonlocal at
  out=struct.unpack_from('<'+fmt*n,raw,at);at+=struct.calcsize(fmt)*n;return out
 h,v,n,q=read('I',4);flat=read('I',2*n);args=list(zip(flat[::2],flat[1::2]));core=read('Q',n);cover=read('Q',n);roots=read('I',q);kind=read('I',q);active=read('B',n);assert at==len(raw)
 lab=(work/'graph.labels').read_bytes();ranks=struct.unpack_from('<'+'I'*n,lab);types=struct.unpack_from('<'+'B'*n,lab,4*n);assert len(lab)==5*n
 mb=(work/'matches.bin').read_bytes();count=struct.unpack_from('<I',mb)[0];flat=struct.unpack_from('<'+'I'*(count*2),mb,4);assert len(mb)==4+count*8
 match=dict(zip(flat[::2],flat[1::2]));assert len(match)==count and len(set(match.values()))==count
 useby=defaultdict(list)
 for x in range(1,n):
  if active[x] and args[x][0]:
   for j,y in enumerate(args[x]):useby[y].append(2*x+j)
 for j,x in enumerate(roots):useby[x].append((1<<31)|j)
 def target(e):return roots[e&0x7fffffff]if e>>31 else e//2
 def orderkey(e):
  x=target(e);return(ranks[x],n+(e&0x7fffffff)if e>>31 else x)
 def contained(x,y):
  a,b=types[x],types[y]
  if a==b==1:return not(core[y]&~core[x]or cover[x]&~cover[y])
  if a in(1,2)and b==2:return not cover[x]&~cover[y]
  if a==1 and b==3:return bool(core[x]&core[y])
  if a==2 and b==3:return not cover[x]&~core[y]
  if a==3 and b==2:return cover[y]==(1<<h)-1
  return a==b==3 and core[x]==core[y]
 for donor,e in match.items():
  y=target(e)if e>>31 else args[e//2][e&1]
  assert y in args[donor]and active[donor]and e in useby[y]
  assert orderkey(2*donor)<orderkey(e)and contained(donor,target(e))
 held=set(match.values());edge={};slots=[];frames=[];start=[];ops=[];opframes=[];sources=[];root_slots={};H=Counter()
 def new(node,signal):
  s=len(slots);slots.append(signal);frames.append(node);start.append(node);H[ranks[node]]+=1;return s
 def assign(s,e):
  if e>>31:root_slots[e&0x7fffffff]=s
  else:assert e not in edge;edge[e]=s
 def raise_(s,node):
  assert contained(frames[s],node)
  H[ranks[node]-ranks[frames[s]]]+=1;frames[s]=node
 order=sorted((x for x in range(1,n)if active[x]),key=lambda x:(ranks[x],x))
 support=[0]*n
 for x in range(1,n):
  if active[x]:
   a,b=args[x]
   if a:
    assert not support[a]&support[b];support[x]=support[a]|support[b]
   else:support[x]=1<<(x-1)
 for x in order:
  free=sorted((e for e in useby[x]if e not in held),key=orderkey);assert free
  a,b=args[x]
  if not a:
   for e in free:
    s=new(x,support[x]);sources.append((s,x));assign(s,e)
   continue
  sa,sb=edge.pop(2*x),edge.pop(2*x+1);assert slots[sa]==support[a]and slots[sb]==support[b]
  if x in match:
   e=match[x];kept=target(e)if e>>31 else args[e//2][e&1]
   if kept==a:sa,sb=sb,sa
   assign(sb,e)
  raise_(sa,x);raise_(sb,x);ops.append((sa,sb));opframes.append(x);slots[sa]^=slots[sb];assert slots[sa]==support[x]
  # Zero-signal copy destinations carry independent arbitrary dirty symbols in
  # the conjugated implementation. The fresh component alone is checked here.
  for e in free[:-1]:
   s=new(x,0);ops.append((s,sa));opframes.append(x);slots[s]^=slots[sa];assign(s,e)
  assign(sa,free[-1])
 assert not edge and set(root_slots)==set(range(q))
 outputs=[]
 for j in range(q):
  s=root_slots[j];x=roots[j];assert slots[s]==support[x]and contained(frames[s],x)
  if ranks[frames[s]]!=ranks[x]:raise_(s,x)
  outputs.append((s,j,kind[j]))
  if kind[j]:H[ranks[x]]+=1;H[h]+=1
  else:H[h-1-ranks[x]]+=1;H[1]+=1
 rootset=set(root_slots.values());assert len(rootset)==q
 for s,x in enumerate(frames):
  if s not in rootset:H[h-ranks[x]]+=1
 expected=json.loads((work/'producer.json').read_text());assert len(slots)==expected['R']
 assert [H[i]for i in range(h+1)]==expected['histogram'],([H[i]for i in range(h+1)],expected['histogram'])
 last={};pred=[]
 for i,(a,b)in enumerate(ops):
  pred.append(tuple(last[s]for s in(a,b)if s in last));last[a]=last[b]=i
 center_slots=[s for s,j,k in outputs if k];todo=[last[s]for s in center_slots if s in last];phase=set()
 while todo:
  i=todo.pop()
  if i not in phase:phase.add(i);todo.extend(pred[i])
 touched={s for i in phase for s in ops[i]}|set(center_slots);free=set(range(len(slots)))-touched;caps=Counter(ranks[start[s]]for s in free)
 word=dict(h=h,v=v,R=len(slots),frames=[[types[x],core[x],cover[x],ranks[x]]for x in range(n)],starts=start,ops=ops,opframes=opframes,sources=sources,outputs=outputs,root_nodes=list(roots),center_phase=sorted(phase),center_touched=sorted(touched))
 encoded=json.dumps(word,separators=(',',':')).encode();(work/'literal-word.json.gz').write_bytes(gzip.compress(encoded,mtime=0))
 result=dict(h=h,R=len(slots),ops=len(ops),center_phase_ops=len(phase),center_touched_roles=len(touched),phase_free_roles=len(free),phase_free_first_dimensions=dict(sorted(caps.items())),phase_free_first_rank_sum=sum(r*c for r,c in caps.items()),histogram_exact=True,all_fresh_source_and_output_symbols_exact=True,all_matching_edges_eligible_unique=True,all_actual_frame_inclusions=True,word_sha256=hashlib.sha256(encoded).hexdigest(),scope='Literal selected matching reconstruction and baseline histogram. All XORs are invertible on arbitrary dirty symbols; this screen checks fresh scalar outputs only and does not assert a new deferred endpoint theorem.')
 (work/'literal-word.json').write_text(json.dumps(result,indent=2)+'\n');return word

def charge(word,selection,trace,outpath):
 d=json.loads(gzip.decompress(word.read_bytes()))
 h,v,R=d['h'],d['v'],d['R'];trip=list(combinations(range(h),3));tid={T:i for i,T in enumerate(trip)};bits=16;low=sum(1<<(bits*t)for t in range(v));guard=low<<(bits-1);rt=list(range(v));sg=[1]*v
 for a,b in combinations(range(h),2):
  for i in sorted((i for i in range(h)if i not in(a,b)),key=lambda i:((i^1)in(a,b),i)):rt.append(tid[tuple(sorted((a,b,i)))]);sg.append(-1)
 cov=[0]*R;bound=[0]*R
 for s,j,k in d['outputs']:
  if k:
   i=j-4*v;cov[s]+=2*low-21*sum(1<<(bits*t)for t,T in enumerate(trip)if i in T);bound[s]+=19
  else:cov[s]+=sg[j]*21<<(bits*rt[j]);bound[s]+=21
 for a,b in reversed(d['ops']):cov[b]+=cov[a];bound[b]+=bound[a]
 assert max(bound)<1<<(bits-1)
 counts=[]
 for s in range(R):
  x=(cov[s]+guard)^guard
  for z in(1,2,4,8):x|=x>>z
  counts.append((x&low).bit_count())
 selected=set(selection['sigma']);early=sum(n for s,n in enumerate(counts)if s not in selected);late=sum(counts[s]for s in selected);assert late==trace['actual_deferred_signed_adds']
 # We charge every explicit frame event, scalar event and grouped readout by64.
 # A rational coefficient has denominator dividing42 and |numerator|<=24740;
 # its binary height and local row-norm exponent are each <32. Charge64 covers
 # both, fixed copies/uncomputation, signs and the odd21 factor. The extra
 # center term expands every copied scatter and its local erasure; 8h+8 bounds
 # fixed wrappers. Counting already-paid frame events again is conservative.
 local_groups=trace['forward_events']+early+2*h*v+8*h+8
 g=64*local_groups
 # Two v-indexed axis stages use the word and its reflected inverse. Endpoint
 # correction plus two h-scale fixed local wrappers are retained explicitly.
 G0=v*v+2*v*(g+2*h)
 maxchild=trace['maxchild'];m=h*h;depth=0
 while (2*pow(maxchild,depth))>pow(m,depth):depth+=1
 out=dict(status='EXACT_COUNT_AND_CONSERVATIVE_BOUND',h=h,v=v,R=R,full_readout_nonzero_coefficients=sum(counts),early_readout_nonzero_coefficients=early,deferred_readout_nonzero_coefficients=late,coefficient_denominator=42,coefficient_absolute_numerator_bound=max(bound),coefficient_binary_height_charge=64,forward_events=trace['forward_events'],expanded_center_terms=h*v,conservative_local_groups=local_groups,local_scalar_charge=g,G0=G0,maxchild=maxchild,halving_degree=depth,word_sha256=hashlib.sha256(gzip.decompress(word.read_bytes())).hexdigest(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='New finite operation/height bound for this explicit grouped-readout schedule. Deliberately overcounts frame events and center copies. The same PR104 semantic induction and full three-stock bridge must be rederived with this G0 and halving degree.')
 outpath.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');return out

def selection_to_json(sel):
 return json.dumps(sel,sort_keys=True,separators=(',',':'))+'\n'
def selection_from_json(raw):
 sel=json.loads(raw)
 for field in ('sigma','cov_masks','first'):
  sel[field]={int(k):(tuple(v)if isinstance(v,list)else v)for k,v in sel[field].items()}
 return sel

def regenerate(work):
 work=Path(work);build_word(work/'complex');word=work/'complex/literal-word.json.gz'
 sc,sel=screen(word,work/'complex-screen.json')
 (work/'complex-selection.json').write_text(selection_to_json(sel))
 import gauge_check
 trace=gauge_check.run(word,sel,sc,work/'complex-word.json')
 ch=charge(word,sel,trace,work/'complex-charge.json')
 return dict(screen=sc,word=trace,charge=ch)

def run(work,record=False):
 result=regenerate(work);raw=json.dumps(result,sort_keys=True,indent=2)+'\n'
 if record:
  (HERE/'complex-axis.json').write_text(raw)
  (HERE/'gauge-audit.json').write_text(json.dumps(result['word'],sort_keys=True,indent=2)+'\n')
 else:
  assert (HERE/'complex-axis.json').read_text()==raw,'Frozen complex axis differs'
  assert (HERE/'gauge-audit.json').read_text()==json.dumps(result['word'],sort_keys=True,indent=2)+'\n','Frozen gauge chronology differs'
 print('PASS regenerated signed-gauge geometry, chronology, paid inventory and scalar charge')
 return result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);ap.add_argument('--record',action='store_true');a=ap.parse_args();run(a.work,a.record)
