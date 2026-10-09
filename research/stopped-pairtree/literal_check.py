#!/usr/bin/env python3
"""Exact literal carrier reconstruction from producer DAG and selected matching.

Read-only reconstruction; no producer or matcher code is imported. It checks
full ordinary-symbol transfer, every live use and true binary-frame inclusion,
the reflected reverse paths, the constructive signed inverse, and exact dirty
fixtures. The identity J L(z+Vx)-J Lz=J L Vx holds for all dirty z because each
actual operation is an invertible elementary shear; no dense dirty matrix is
assumed or sampled as a replacement for that algebraic proof.

Apache-2.0. Prepared with OpenAI Codex assistance. Retains the credited PR104/107
scalar/frame construction and original matching interface; see package NOTICE.
"""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,struct,json,hashlib
from itertools import combinations
from functools import lru_cache
HERE=Path(__file__).resolve().parent
if not __debug__:raise SystemExit("Assertions required")
def digest(raw):return hashlib.sha256(raw).hexdigest()
def encoded(x):return json.dumps(x,separators=(",",":"),sort_keys=True).encode()
def gauss(rows):
 E={}
 for x in rows:
  for p,b in sorted(E.items(),reverse=True):
   if x>>p&1:x^=b
  if x:E[x.bit_length()-1]=x
 return tuple(E[p]for p in sorted(E,reverse=True))
def inside(A,B):
 for x in A:
  for b in B:
   if x>>(b.bit_length()-1)&1:x^=b
  if x:return False
 return True
@lru_cache(maxsize=None)
def orthogonal(A,h):
 pivots={a.bit_length()-1 for a in A};out=[]
 for j in range(h):
  if j in pivots:continue
  x=1<<j
  for row in reversed(A):
   if (row&x).bit_count()%2:x^=1<<(row.bit_length()-1)
  assert all((x&a).bit_count()%2==0 for a in A);out.append(x)
 return gauss(out)

def audit(work):
 raw=(work/'graph.bin').read_bytes();at=0
 def read(fmt,n):
  nonlocal at
  out=struct.unpack_from('<'+fmt*n,raw,at);at+=struct.calcsize(fmt)*n;return out
 h,v,n,q=read('I',4);assert h==24 and v==2024 and q==4*v+h
 flat=read('I',2*n);args=list(zip(flat[::2],flat[1::2]));core=read('Q',n);cover=read('Q',n);roots=read('I',q);kind=read('I',q);active=read('B',n);assert at==len(raw)
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
 held=set(match.values());edge={};slots=[];frames=[];start=[];ops=[];opframes=[];sources=[];root_slots={};H=Counter();pending={};events=[];copy_ops=[];reflected_inclusions=0
 triple_lines=[sum(1<<i for i in T)for T in combinations(range(h),3)]
 @lru_cache(maxsize=None)
 def actual(node):
  if types[node]==1:
   bits=support[node];rows=[]
   while bits:
    bit=bits&-bits;bits-=bit;rows.append(triple_lines[bit.bit_length()-1])
  else:
   assert types[node]==2;rows=[1<<i for i in range(h)if cover[node]>>i&1]
  B=gauss(rows);assert len(B)==ranks[node]
  assert len(gauss([sum(((x&y).bit_count()%2)<<i for i,y in enumerate(B))for x in B]))==len(B)
  return B
 def new(node,signal):
  s=len(slots);slots.append(signal);frames.append(node);start.append(node);H[ranks[node]]+=1;actual(node);return s
 def assign(s,e):
  assert 0<=s<len(slots)and s not in pending;pending[s]=e
  if e>>31:root_slots[e&0x7fffffff]=s
  else:assert e not in edge;edge[e]=s
 def raise_(s,node):
  nonlocal reflected_inclusions
  old=frames[s];assert 0<=s<len(slots)and contained(old,node)
  A,B=actual(old),actual(node);assert inside(A,B)
  assert inside(orthogonal(B,h),orthogonal(A,h));reflected_inclusions+=1
  H[ranks[node]-ranks[old]]+=1;frames[s]=node;events.append((s,old,node))
 order=sorted((x for x in range(1,n)if active[x]),key=lambda x:(ranks[x],x))
 support=[0]*n
 for x in range(1,n):
  if active[x]:
   a,b=args[x]
   if a:
    assert not support[a]&support[b];support[x]=support[a]|support[b]
   else:assert x<=v;support[x]=1<<(x-1)
 for x in order:
  free=sorted((e for e in useby[x]if e not in held),key=orderkey);assert free
  a,b=args[x]
  if not a:
   assert 1<=x<=v and ranks[x]==1
   for e in free:
    s=new(x,support[x]);sources.append((s,x));assign(s,e)
   continue
  sa,sb=edge.pop(2*x),edge.pop(2*x+1);assert sa!=sb
  assert pending.pop(sa)==2*x and pending.pop(sb)==2*x+1
  assert slots[sa]==support[a]and slots[sb]==support[b]
  if x in match:
   e=match[x];kept=target(e)if e>>31 else args[e//2][e&1]
   if kept==a:sa,sb=sb,sa
   assign(sb,e)
  raise_(sa,x);raise_(sb,x);assert actual(frames[sa])==actual(frames[sb])==actual(x)
  ops.append((sa,sb));opframes.append(x);assert not slots[sa]&slots[sb];slots[sa]|=slots[sb];assert slots[sa]==support[x]
  # Zero-signal copy destinations carry independent arbitrary dirty symbols in
  # the conjugated implementation. The fresh component alone is checked here.
  for e in free[:-1]:
   s=new(x,0);assert s!=sa and actual(frames[s])==actual(frames[sa])==actual(x)
   copy_ops.append(len(ops));ops.append((s,sa));opframes.append(x);slots[s]=slots[sa];assign(s,e)
  assign(sa,free[-1])
 assert not edge and set(root_slots)==set(range(q))
 outputs=[]
 for j in range(q):
  s=root_slots[j];x=roots[j];assert pending.pop(s)==((1<<31)|j)
  assert slots[s]==support[x]and contained(frames[s],x)and inside(actual(frames[s]),actual(x))
  if ranks[frames[s]]!=ranks[x]:raise_(s,x)
  outputs.append((s,j,kind[j]))
  if kind[j]:H[ranks[x]]+=1;H[h]+=1
  else:H[h-1-ranks[x]]+=1;H[1]+=1
 assert not pending
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
 # A complete signed inverse is obtained by reversing this actual operation
 # list and subtracting each source. This is a constructive proof, since the
 # 2x2 identity below holds over Z and hence every characteristic-zero field.
 shear=((1,1),(0,1));unshear=((1,-1),(0,1))
 mul=lambda A,B:tuple(tuple(sum(A[i][k]*B[k][j]for k in range(2))for j in range(2))for i in range(2))
 assert mul(shear,unshear)==mul(unshear,shear)==((1,0),(0,1))
 assert mul(shear,shear)!=((1,0),(0,1))
 inverse=[(a,b,-1)for a,b in reversed(ops)]
 assert len(inverse)==len(ops)and all((a,b)==ops[len(ops)-1-i]and sign==-1 for i,(a,b,sign)in enumerate(inverse))
 def apply(values,back=False):
  out=list(values)
  if back:
   for a,b,sign in inverse:out[a]-=out[b]
  else:
   for a,b in ops:out[a]+=out[b]
  return out
 fixture_hashes=[];wrong_order_rejected=False
 for seed in (1,5,19,37):
  z=[((s+1)*(seed+7)+s*s)%31-15 for s in range(len(slots))]
  x=[((j+3)*(seed+11)+j*j)%23-11 for j in range(v)]
  y=[((j+5)*(seed+13))%29-14 for j in range(q)]
  vx=[0]*len(slots)
  for s,node in sources:vx[s]+=x[node-1]
  assert len(sources)==len({s for s,node in sources})
  shifted=[a+b for a,b in zip(z,vx)];lz=apply(z);shift=apply(shifted)
  assert apply(lz,True)==z and apply(shift,True)==shifted
  retained=[]
  for j in range(q):
   mask=support[roots[j]];value=0
   while mask:
    bit=mask&-mask;mask-=bit;value+=x[bit.bit_length()-1]
   got=y[j]+shift[root_slots[j]]-lz[root_slots[j]]
   assert got==y[j]+value;retained.append(got)
  # Retain -JLz, restore z, inject Vx, add JL(z+Vx), restore z+Vx,
  # and remove Vx. This realizes (z,y)->(z,y+JLVx) for arbitrary z,y.
  restored=[a-b for a,b in zip(apply(shift,True),vx)];assert restored==z
  wrong=list(lz)
  for a,b in ops:wrong[a]-=wrong[b]
  wrong_order_rejected|=wrong!=z
  fixture_hashes.append(digest(encoded(dict(seed=seed,retained=retained,restored=restored))))
 assert wrong_order_rejected
 word=dict(h=h,v=v,R=len(slots),frames=[[types[x],core[x],cover[x],ranks[x]]for x in range(n)],starts=start,ops=ops,opframes=opframes,sources=sources,outputs=outputs,root_nodes=list(roots),events=events,copy_ops=copy_ops,center_phase=sorted(phase),center_touched=sorted(touched))
 return dict(h=h,R=len(slots),ordinary_outputs=q,ops=len(ops),copy_ops=len(copy_ops),scalar_ops=len(ops)-len(copy_ops),source_uses=len(sources),center_phase_ops=len(phase),center_touched_roles=len(touched),phase_free_roles=len(free),phase_free_first_dimensions=dict(sorted(caps.items())),phase_free_first_rank_sum=sum(r*c for r,c in caps.items()),
  all_slot_lifetimes_unique=True,all_ordinary_symbol_coefficients_exact=True,all_operation_frames_equal=True,all_actual_frame_inclusions=True,all_reflected_reverse_inclusions=True,reflected_inclusions=reflected_inclusions,all_frames_nondegenerate=True,complete_paid_histogram_equal=True,
  constructive_signed_inverse=True,arbitrary_dirty_identity='J L(z+Vx)-J Lz = J L Vx; auxiliary z and retained offset y restored/transported exactly',signed_fixture_count=4,signed_fixture_hashes=fixture_hashes,negative_controls=dict(wrong_local_inverse_sign_rejected=True,forward_order_inverse_rejected=True),
  literal_program_sha256=digest(encoded(word)),inverse_program_sha256=digest(encoded(inverse)),
  inputs={name:digest((work/name).read_bytes())for name in('graph.bin','graph.labels','matches.bin','producer.json')},checker_sha256=digest(Path(__file__).read_bytes()),
  scope='Independently reconstructed actual carrier program and full ordinary-symbol map. Every copy/gate has equal actual binary frames, every forward and reflected reverse raise is nested, every role has a unique pending use, and the complete histogram agrees. Constructive elementary-shear inversion proves the arbitrary-dirty identity; four exact signed fixtures test its implementation. Does not replace the separate signed rational scatter, endpoint-transfer, stopped recursion or all-size analytic hypotheses.')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--record',action='store_true');a=p.parse_args()
 result=audit(a.work);raw=json.dumps(result,sort_keys=True,indent=2)+'\n';target=HERE/'literal-audit.json'
 if a.record:target.write_text(raw)
 else:assert target.read_text()==raw,'Literal replay receipt differs'
 print('PASS literal program: all source/output symbols, equal frames, lifetimes, reflected inverse, arbitrary-dirty algebra and exact signed fixtures')
