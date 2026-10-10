"""Callable scalar-keyed retiming adapter. Imports do not run or mutate inputs."""
from array import array
from collections import Counter
from functools import lru_cache
import hashlib,json
EXPECTED={2:-2,4:24,5:-48,6:25,11:-1,13:2,17:-1}
def sha(b):return hashlib.sha256(b).hexdigest()
def bsha(b):return sha(json.dumps(b,separators=(',',':')).encode())
def projection(a):
 p=array('i')
 for k in range(0,len(a),6):
  op,x,y,c,f,z=a[k:k+6]
  if op==1:p.extend((op,x,y,c,z))
  elif op:p.extend((op,x,y,c,f,z))
 return p.tobytes()
def histogram(a):
 h=Counter()
 for k in range(0,len(a),6):
  if a[k]==0 and a[k+4]:h[a[k+4]]+=1
  elif a[k]==2:h[a[k+5]]+=1
 return h
def transform(a,frames,initial,final,entries,expected_input_sha):
 """Return a fresh word and receipt; reuse existing frames and preserve endpoints."""
 assert a.itemsize==4 and len(a)%6==0 and sha(a.tobytes())==expected_input_sha
 F={int(k):v for k,v in frames.items()};ini={int(k):v for k,v in initial.items()};fin={int(k):v for k,v in final.items()}
 dims={f:len(v['basis'])for f,v in F.items()}
 keys={tuple(e['scalar']):e for e in entries};assert len(keys)==len(entries)==25
 source_pairs={(a[k+2],a[k+3])for k in range(0,len(a),6)if a[k]==0}
 exact_new_pairs=set()
 @lru_cache(None)
 def sub(x,y):
  if x==y or(x,y)in source_pairs:return True
  okay=dims[x]<=dims[y]and all(not sum(b*c for b,c in zip(u,v))for u in F[x]['basis']for v in F[y]['annihilator'])
  if okay:exact_new_pairs.add((x,y))
  return okay
 st=dict(ini);out=array('i');copy=None;used=set(ini.values());changed=[];seen=set();copy_count=0
 def move(q,f):
  before=st[q]
  if before==f:return
  if copy is not None:assert q!=copy[0],('COPY source moved',q)
  assert sub(before,f),(q,before,f)
  rank=dims[f]-dims[before];assert rank>=0
  out.extend((0,q,before,f,rank,0));st[q]=f;used.update((before,f))
 for k in range(0,len(a),6):
  op,x,y,c,f,z=a[k:k+6]
  if op==0:continue
  if op==1:
   key=(x,y,c,z)
   if key in keys:
    assert key not in seen and copy is None
    e=keys[key];assert dims[f]==e['old_dimension']and bsha(F[f]['basis'])==e['old_basis_sha256']
    g=e['reuse_frame_id'];assert dims[g]==e['new_dimension']and sub(f,g)
    # Exact equality to nominated subspace, rather than trusting frame IDs.
    assert all(not sum(b*c for b,c in zip(u,v))for u in e['new_basis']for v in F[g]['annihilator'])
    changed.append(dict(input_record=k//6,output_record_before_moves=len(out)//6,scalar=list(key),old_frame=f,new_frame=g));seen.add(key);f=g
   if copy is not None:assert x!=copy[0],('COPY source written',x)
   move(x,f);move(y,f);assert st[x]==st[y]==f;out.extend((op,x,y,c,f,z))
  elif op==2:
   assert copy is None;move(x,c);assert y not in st;st[y]=f;copy=(x,y,c,f)
   out.extend((op,x,y,c,f,z));copy_count+=1
  else:
   assert op==3 and copy==(x,y,c,f)and st[x]==c and st[y]==f
   out.extend((op,x,y,c,f,z));del st[y];copy=None
 assert copy is None and seen==set(keys)
 for q in sorted(fin):move(q,fin[q])
 assert st==fin and copy_count==24
 before,after=projection(a),projection(out);assert before==after
 H=histogram(out);delta=H.copy();delta.subtract(histogram(a));delta={r:n for r,n in delta.items()if n};assert delta==EXPECTED
 assert len(out)//6==len(a)//6-1 and set(F)==set(frames if all(isinstance(k,int)for k in frames)else map(int,frames))
 receipt=dict(status='PASS_PHYSICAL_RETIMING_ADAPTER_AND_EXACT_LOCAL_LEDGER',input_raw_sha256=expected_input_sha,raw_sha256=sha(out.tobytes()),selected_gate_count=25,changed_gates=changed,unchanged_scalar_COPY_projection_sha256=sha(after),scalar_COPY_projection_byte_identical=True,unchanged_endpoints=True,copy_windows=copy_count,all_COPY_sources_immutable=True,all_retimed_gates_outside_COPY_windows=True,new_registered_frames=0,exact_new_subspace_pairs=[list(x)for x in sorted(exact_new_pairs)],local_histogram=dict(sorted(H.items())),local_histogram_delta=delta,local_calls=sum(H.values()),local_rank_mass=sum(r*n for r,n in H.items()),normalized_stock=173409,literal_40_replica_stock=867045,scope='Exact emitted frame paths, scalar/COPY identity and cost delta. Inherits source scalar proof; global bank/prime/finite admission is separate.')
 return out,receipt

