#!/usr/bin/env python3
"""Independent raw-file scalar and binary-frame audit of h24 pair-tree candidate.
No producer/matcher code imported. Full signed map checked by exact bounded lanes.
"""
from pathlib import Path
from itertools import combinations
from collections import Counter
from functools import lru_cache
import argparse,struct,json,hashlib,tempfile,importlib.util
HERE=Path(__file__).resolve().parent
if not __debug__:raise ValueError('Assertions required')

def gauss(rows):
 E={}
 for x in rows:
  for p,b in sorted(E.items(),reverse=True):
   if x>>p&1:x^=b
  if x:E[x.bit_length()-1]=x
 return tuple(E[p]for p in sorted(E,reverse=True))
def inside(rows,B):
 for x in rows:
  for b in B:
   if x>>(b.bit_length()-1)&1:x^=b
  if x:return False
 return True

def audit(prefix):
 raw=prefix.with_suffix('.bin').read_bytes();lab=prefix.with_suffix('.labels').read_bytes();h,v,N,q=struct.unpack_from('<4I',raw);assert h==24
 pos=16
 def take(code,n):
  nonlocal pos
  result=struct.unpack_from('<'+str(n)+code,raw,pos);pos+=struct.calcsize('<'+str(n)+code);return result
 packedargs=take('I',2*N);args=list(zip(packedargs[::2],packedargs[1::2]));core=take('Q',N);cover=take('Q',N);roots=take('I',q);kind=take('I',q);active=take('B',N);assert pos==len(raw)
 ranks=struct.unpack_from('<'+str(N)+'I',lab);types=struct.unpack_from('<'+str(N)+'B',lab,4*N);assert len(lab)==5*N
 triples=list(combinations(range(h),3));assert len(triples)==v and q==4*v+h
 lines=[sum(1<<i for i in T)for T in triples];full=(1<<v)-1;points=[sum(1<<i for i,T in enumerate(triples)if j in T)for j in range(h)];support=[0]*N
 for n in range(1,v+1):assert args[n]==(0,0);support[n]=1<<(n-1);assert core[n]==cover[n]==lines[n-1]and ranks[n]==1 and types[n]==1
 for n in range(v+1,N):
  a,b=args[n];assert 0<a<n and 0<b<n and not support[a]&support[b];support[n]=support[a]|support[b]
  assert core[n]==core[a]&core[b]and cover[n]==cover[a]|cover[b]
 reachable=set();todo=list(roots)
 while todo:
  n=todo.pop()
  if n in reachable:continue
  reachable.add(n)
  if args[n]!=(0,0):todo.extend(args[n])
 assert {i for i,x in enumerate(active)if x}==reachable
 @lru_cache(maxsize=None)
 def frame(t,c,u,s):
  if t==1:
   assert c.bit_count()>=2
   mask=s;rows=[]
   while mask:
    z=mask&-mask;mask-=z;rows.append(lines[z.bit_length()-1])
  else:
   assert t==2;rows=[1<<i for i in range(h)if u>>i&1]
  B=gauss(rows);assert len(B)==len(rows)
  Gram=[sum(((x&y).bit_count()%2)<<j for j,y in enumerate(rows))for x in rows];assert len(gauss(Gram))==len(rows)
  return B
 F={};degree=Counter();nondeg=edges=0
 for n in sorted(reachable):
  F[n]=frame(types[n],core[n],cover[n],support[n]if types[n]==1 else 0);assert len(F[n])==ranks[n];nondeg+=1
  for a in args[n]:
   if a:assert inside(F[a],F[n]);degree[a]+=1;edges+=1
 for n in roots:degree[n]+=1
 # All root definitions checked independently of source assertions.
 for T,n in zip(triples,roots[:v]):assert support[n]==full&~(points[T[0]]|points[T[1]]|points[T[2]])
 pairs={};offset=v
 for a,b in combinations(range(h),2):
  order=sorted((i for i in range(h)if i not in(a,b)),key=lambda i:((i^1)in(a,b),i))
  for i in order:
   n=roots[offset];offset+=1;assert support[n]==points[a]&points[b]&~points[i];pairs[a,b,i]=n
 assert offset==4*v
 centers=roots[offset:];assert len(centers)==h
 for i,n in enumerate(centers):assert support[n]==full&~points[i];assert types[n]==2 and cover[n]==((1<<h)-1)^(1<<i)and ranks[n]==h-1
 assert list(kind)==[0]*(4*v)+[1]*h
 # 9-bit coefficient lanes: every difference coefficient has absolute value
 # <=231<512, so zero packed difference implies every coefficient is zero.
 @lru_cache(maxsize=None)
 def lanes(mask):
  value=0
  while mask:
   z=mask&-mask;mask-=z;value|=1<<(9*(z.bit_length()-1))
  return value
 centervec=[lanes(support[n])for n in centers];total=sum(centervec);assert total==21*lanes(full)
 for j,T in enumerate(triples):
  value=2*total-21*sum(centervec[i]for i in T)+21*lanes(support[roots[j]])
  for a,b in combinations(T,2):i=next(x for x in T if x not in(a,b));value-=21*lanes(support[pairs[a,b,i]])
  assert value==42<<(9*j)
 # Parent middle/scatter-frame conditions checked as actual orthogonality.
 for j,T in enumerate(triples):
  normal=lines[j]
  for n in [roots[j]]+[pairs[a,b,next(x for x in T if x not in(a,b))]for a,b in combinations(T,2)]:
   assert all((x&normal).bit_count()%2==0 for x in F[n])
 # Independently reconstruct unlinked physical charge classes.
 H=Counter();c=0;loss=0
 for n in reachable:
  r=ranks[n]
  if args[n]!=(0,0):
   c+=1;H[r]+=degree[n]-1;H[h-r]+=1
   for a in args[n]:H[r-ranks[a]]+=1
  else:H[1]+=degree[n]
 for n,k in zip(roots,kind):
  if k:H[ranks[n]]+=1;H[h]+=1;loss+=ranks[n]
  else:H[h-1-ranks[n]]+=1;H[1]+=1
 expected=json.loads(prefix.with_suffix('.json').read_text());assert c==expected['c']and loss==expected['loss'];assert [H[i]for i in range(h+1)]==expected['histogram'];assert sum(i*n for i,n in H.items())==h*(c+q)+2*loss
 # Verify every chosen matching edge from its literal binary dump using
 # actual GF2 spaces, rather than the producer's combinatorial label test.
 matchfile=prefix.parent/'matches.bin';matchraw=matchfile.read_bytes();count=struct.unpack_from('<I',matchraw)[0];assert len(matchraw)==4+8*count
 matchpairs=[struct.unpack_from('<2I',matchraw,4+8*j)for j in range(count)];assert len({a for a,b in matchpairs})==len({b for a,b in matchpairs})==count
 linkedH=H.copy();flips=0
 for donor,use in matchpairs:
  assert donor in reachable and args[donor]!=(0,0)
  if use>>31:
   ix=use&0x7fffffff;assert ix<q;target=roots[ix];value=target;targettime=N+ix
  else:
   target=use//2;assert target in reachable and args[target]!=(0,0);value=args[target][use&1];targettime=target
  assert value in args[donor]
  assert (ranks[donor],donor)<(ranks[target],targettime)
  assert inside(F[donor],F[target])
  flips+=value==args[donor][0]
  # A donor's retired tail and a fresh operand copy are replaced by one
  # continued carrier path; compare the literal rank differences.
  removed=[h-ranks[donor],ranks[value],ranks[target]-ranks[value]]
  added=[ranks[target]-ranks[donor]]
  for z in removed:linkedH[z]-=1
  for z in added:linkedH[z]+=1
  assert sum(removed)-sum(added)==h
 matched=json.loads((prefix.parent/'producer.json').read_text());R=c+q-count
 assert all(n>=0 for n in linkedH.values())and [linkedH[i]for i in range(h+1)]==matched['histogram']
 assert matched['R']==R and matched['matched']==count and matched['orientation_changes']==flips
 assert sum(i*n for i,n in linkedH.items())==h*R+2*loss
 return dict(status='PASS',h=h,source_triples=v,active_nodes=len(reachable),additions=c,roots=q,exact_binary_nondegenerate_frames=nondeg,exact_frame_inclusions=edges,exact_signed_transfer_coefficients=v*v,center_divisor=21,all_ordinary_additions_disjoint=True,all_root_supports_exact=True,all_output_orthogonality_exact=True,unlinked_recursive_histogram_rebuilt=True,complete_unlinked_rank_mass=sum(i*n for i,n in H.items()),all_matched_donors_and_uses_unique=True,all_matching_geometry_checked_as_actual_binary_subspaces=True,all_matching_times_and_unchanged_operands_checked=True,matching_edges=count,physical_roles=R,complete_matched_histogram_rebuilt=True,matched_rank_mass=sum(i*n for i,n in linkedH.items()),scope='Independent scalar/support/frame/matching and literal rank-charge audit. Full arbitrary-dirty execution, signed endpoints, recursion, stopping, precision and final assembly remain separate obligations.',input_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in(prefix.with_suffix('.bin'),prefix.with_suffix('.labels'),prefix.with_suffix('.json'),matchfile,prefix.parent/'producer.json')},source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
def run(work,record=False):
 result=audit(Path(work)/'graph');encoded=json.dumps(result,indent=2,sort_keys=True)+'\n';receipt=HERE/'physical-audit.json'
 if record:receipt.write_text(encoded)
 else:assert receipt.read_text()==encoded,'Frozen physical audit differs'
 print('Independent pair-tree scalar/binary-frame/matching audit PASS')
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--work',type=Path);p.add_argument('--record',action='store_true');a=p.parse_args()
 if a.work is not None:run(a.work,a.record)
 else:
  spec=importlib.util.spec_from_file_location('stopped_pairtree_independent_producer',HERE/'producer.py');producer=importlib.util.module_from_spec(spec);spec.loader.exec_module(producer)
  with tempfile.TemporaryDirectory(prefix='stopped-pairtree-physical-')as directory:
   work=Path(directory);producer.regenerate(work);run(work,a.record)
