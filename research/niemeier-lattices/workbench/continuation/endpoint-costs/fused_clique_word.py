from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "paid-controller"))
from portable import WORKBENCH, output_path, source_name
"""Exact characteristic-two clique/matching fusion, including full spinor alignment."""
from pathlib import Path
from collections import Counter,defaultdict
import json,hashlib
FULL=65535;HALVES=(255,65280)
def require(ok,msg):
 if not ok:raise ValueError(msg)

def geometry():
 words=[(x<<1)|((x.bit_count()&1)<<15)for x in range(1<<14)]
 H=[sum(((b&t).bit_count()&1)<<t for t in range(16))for b in range(16)]
 cliques={};groups=defaultdict(list)
 for w in words:
  representative=min(w^h for h in H)
  if representative not in cliques:cliques[representative]=sorted(representative^h for h in H)
 require(len(cliques)==1024,'1024 full Hadamard cosets')
 require(set().union(*(set(c)for c in cliques.values()))==set(words),'Disjoint full spinor partition')
 for cid,(rep,clique) in enumerate(sorted(cliques.items())):
  require(all((x^y).bit_count()==8 for i,x in enumerate(clique)for y in clique[i+1:]),'Every clique is an exact orthogonal basis')
  halves=defaultdict(list)
  for w in clique:
   sigma=sum((((w>>(2*i))^(w>>(2*i+1)))&1)<<i for i in range(8));halves[sigma].append(w)
  require(len(halves)==2 and all(len(h)==8 for h in halves.values()),'Exact8+8 pairing split')
  a,b=sorted(halves);require(a^b==255,'Complementary pairing frames')
  for sigma,half in halves.items():
   require(sigma.bit_count()%2==0,'Even relative-sign pattern')
   groups[sigma].append((cid,half))
 require(len(groups)==128 and all(len(g)==16 for g in groups.values()),'Every8D pairing frame has16 clique halves')
 for sigma,halves in groups.items():
  require({cid for cid,_ in halves}=={cid for cid,_ in groups[sigma^255]},'Opposite frames have identical16-clique incidence')
  require(len({w for _,h in halves for w in h})==128,'128 distinct lines per pairing frame')
  # The equations v[2i+1]=(-1)^sigma_i v[2i] define an8D space;
  # each half is8 nonzero mutually orthogonal vectors in it, hence a basis.
  for _,half in halves:
   require(all(all((((w>>(2*i))^(w>>(2*i+1)))&1)==((sigma>>i)&1)for i in range(8))for w in half),'Raw sign vectors satisfy all8 frame equations')
 return dict(spinor_ports=len(words),hadamard_cliques=len(cliques),pairing_frames=len(groups),orthogonal_frame_pairs=len(groups)//2,halves_per_frame=16,ports_per_half=8,ports_per_frame=128,coordinate_pairs=[[2*i,2*i+1]for i in range(8)],canonical_spinor_bitstrings_sha256=hashlib.sha256(b''.join(w.to_bytes(2,'little')for w in words)).hexdigest())

def mixer_gates(n=16):
 rows=[((1<<n)-1)^(1<<i)for i in range(n)];gates=[]
 for col in range(n):
  pivot=next(i for i in range(col,n)if rows[i]>>col&1)
  if pivot!=col:
   for a,b in ((pivot,col),(col,pivot),(pivot,col)):rows[b]^=rows[a];gates.append((a,b))
  for i in range(n):
   if i!=col and rows[i]>>col&1:rows[i]^=rows[col];gates.append((col,i))
 require(rows==[1<<i for i in range(n)],'I+J is invertible in characteristic two')
 out=list(reversed(gates));test=[1<<i for i in range(n)]
 for a,b in out:test[b]^=test[a]
 require(test==[((1<<n)-1)^(1<<i)for i in range(n)],'CNOT implementation is exactly I+J')
 return out

def replay(fused=True,corrupt_cleanup=False,partial_end=True):
 C=16;N=C*16;plans=[];next_id=2*N;role_clique=[i//16 for i in range(N)]*2
 for size in (1,2,4,8):
  for cid in range(C):
   for first in range(0,16,2*size):
    left=list(range(first,first+size));right=list(range(first+size,first+2*size))
    for child,other in ((left,right),(right,left)):
     for t in other[1:]:plans.append((size,cid,child,other,t,next_id));next_id+=1;role_clique.append(cid)
 frames=[1<<(i%16)for i in range(N)]+[0]*(next_id-N);rows=[1<<i for i in range(next_id)];profile=Counter();undo=[];add_count=0
 def frame_key(i):
  mask=frames[i]
  return mask if mask in (0,FULL,*HALVES)else(role_clique[i],mask)
 def grow(i,frame):
  old=frames[i];require(old&frame==old,'Nested exact subspace chain')
  if old!=frame:profile[frame.bit_count()-old.bit_count()]+=1;frames[i]=frame
 def add(a,b,record=False):
  nonlocal add_count
  require(frame_key(a)==frame_key(b),'Exact common frame for every CNOT')
  rows[b]^=rows[a];add_count+=1
  if record:undo.append((a,b))
 for _,cid,_,_,t,h in plans:add(h,N+cid*16+t)
 helper=iter(plans);mg=mixer_gates()
 for size in (1,2,4,8):
  if size==8 and fused:
   for orientation in range(2):
    pivots=[cid*16+orientation*8 for cid in range(C)]
    for a,b in mg:add(pivots[a],pivots[b],record=True)
  for cid in range(C):
   offset=cid*16
   for first in range(0,16,2*size):
    left=list(range(first,first+size));right=list(range(first+size,first+2*size));parent=sum(1<<j for j in left+right);block_copies=[]
    for child,other in ((left,right),(right,left)):
     pivot=offset+child[0];childframe=sum(1<<j for j in child);require(frames[pivot]==childframe,'Exact child-frame pivot')
     copies=[]
     for t in other[1:]:
      p=next(helper);require(p[:5]==(size,cid,child,other,t),'Deterministic helper assignment');h=p[5]
      grow(h,childframe);add(pivot,h,record=not partial_end);copies.append((t,h));block_copies.append((pivot,h))
     t=other[0];cap=parent^(1<<t);grow(pivot,cap);grow(N+offset+t,cap);add(pivot,N+offset+t)
     for t,h in copies:cap=parent^(1<<t);grow(h,cap);grow(N+offset+t,cap);add(h,N+offset+t)
    if partial_end:
     for pivot,h in block_copies:grow(pivot,parent);grow(h,parent);add(pivot,h)
    if size<8:
     a,b=offset+left[0],offset+right[0];grow(a,parent);grow(b,parent);add(b,a,record=True)
 for i in list(range(N))+(list(range(2*N,next_id))if not partial_end else[]):grow(i,FULL)
 for position,(a,b)in enumerate(reversed(undo)):
  if not(corrupt_cleanup and position==0):add(a,b)
 for i in list(range(N))+list(range(2*N,next_id)):require(rows[i]==1<<i,'All arbitrary source and dirty-helper columns restored')
 for i in range(N):
  cid,local=divmod(i,16);orientation=local//8;want=1<<(N+i)
  for j in range(N):
   clique_edge=j//16==cid and j!=i
   matching_edge=(j%16)//8!=orientation
   if clique_edge^(fused and matching_edge):want^=1<<j
  require(rows[N+i]==want,'Exact clique adjacency XOR matching output kernel')
  require(frames[N+i]==FULL^(1<<local),'Exact output orthogonal hyperplane')
 helper_widths=Counter(frames[i].bit_count()for i in range(2*N,next_id))
 require(sum(k*v for k,v in profile.items())==2*N*15+sum(k*v for k,v in helper_widths.items()),'Complete rank-mass identity')
 return dict(cliques=C,ports=N,helpers=next_id-2*N,helper_endpoint_widths={str(k):v for k,v in sorted(helper_widths.items())},paid_profile={str(k):v for k,v in sorted(profile.items())},scalar_CNOTs=add_count,mixer_CNOTs_per_orientation=len(mg)if fused else 0,all_input_columns_checked=next_id,output_row_degree=127 if fused else 15)

def main():
 g=geometry();base=replay(False);fused=replay(True);full_end=replay(True,partial_end=False)
 require(base['paid_profile']==fused['paid_profile'],'Fusion changes no paid path')
 try:replay(True,True)
 except ValueError as e:require('columns restored' in str(e),'Cleanup negative control rejects for exact reason')
 else:raise ValueError('Omitted cleanup must be detected')
 out=dict(status='PASS_EXACT_FUSED_SUBWORD',scope='All64 pairing-frame pairs have identical16-clique incidence and the same scalar coefficient word. One representative combinatorial block replays all1056 input columns; full16384-port geometry alignment is enumerated. This proves a compensation subword, not an admitted supplier or an exponent.',geometry=g,ordinary_clique_block=base,fused_block=fused,full_endpoint_fused_control=full_end,total_helpers=64*fused['helpers'],negative_control='Omitting one inverse CNOT fails arbitrary-column restoration',endpoint_scope='Proper-ending helpers need exact endpoint wrappers and width-aware banks with16-width spectators. The frame-level word restores their scalar dirt at the stated terminal frame.',center_warning='J_H plus matching has no established center saving here; this file makes no gain claim.')
 output_path('continuation/endpoint-costs/FUSED-CLIQUE-WORD.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
