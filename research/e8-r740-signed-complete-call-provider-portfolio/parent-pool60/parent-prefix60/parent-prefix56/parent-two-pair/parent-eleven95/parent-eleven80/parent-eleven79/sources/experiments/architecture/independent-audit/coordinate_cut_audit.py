from pathlib import Path
from fractions import Fraction as Q
import json,hashlib,heapq
P=Path(__file__).resolve().parent;R=P.parents[2];S=R/'experiments/architecture/mutable-transfer-next/coordinate-cut'
# Independent shortest path on covered-cut masks, rather than single ordered DP pass.
D=[999]*16;D[0]=0;queue=[(0,0)];edges=[]
for a in range(16):
 for b in range(16):edges.append((a&~b,(a^b).bit_count()))
while queue:
 cost,mask=heapq.heappop(queue)
 if cost!=D[mask]:continue
 for crossed,fee in edges:
  nxt=mask|crossed
  if cost+fee<D[nxt]:D[nxt]=cost+fee;heapq.heappush(queue,(D[nxt],nxt))
assert D==[i.bit_count() for i in range(16)]
# Independent per-input literal vector evaluation of the stated witness.
word=[]
for i in range(4):
 x,y,a,b=i,4+i,8+i,12+i
 word.extend([(y,a,-1),(a,x,1),(b,a,1),(y,b,1),(b,a,-1),(a,x,-1)])
for sign,gs in ((1,word),(-1,[(d,s,-c) for d,s,c in reversed(word)])):
 for col in range(12):
  z=[Q(i==col) for i in range(16)]
  for d,s,c in gs:z[d]+=c*z[s]
  expected=[Q(i==col) for i in range(16)]
  if col<4:expected[4+col]=sign
  assert z==expected
# Independent cancellation-free row prefixes.
peaks=[]
for gs in (word,[(d,s,-c) for d,s,c in reversed(word)]):
 A=[[Q(i==j) for j in range(12)] for i in range(12)]+[[Q(0)]*12 for _ in range(4)];peak=1
 for d,s,c in gs:A[d]=[x+c*y for x,y in zip(A[d],A[s])];peak=max(peak,max(sum(map(abs,row)) for row in A))
 peaks.append(peak)
assert peaks==[2,3]
# Explicit legal coordinate frame ledger and paid ranks, before routing/scalar fees.
source=4*(4-1);target=4*3;dirty=4*(1+3);work=4*4;copy=4;assert source+target+dirty+work+copy==60
out={'status':'PASS_SCOPED_COORDINATE_CUT_AND_DIRTY_WITNESS','frame_edges':256,'mask_costs':D,'minimum_retained_copy_rank':4,'live_columns':12,'known_zero_private_rows':4,'updates':24,'prefixes':list(map(str,peaks)),'paid_rank_mass':60,'proof_review':'A coefficient x_i initially occurs only in frames containing i. Common-frame linear updates cannot create its first nonzero coefficient in an excluding frame, and nested climbs preserve containment. A frame-changing copy that removes i is necessary to reach the prescribed target cap. A coordinate copy removes at most |S\\T| cuts and pays |S△T|, so four independent terminal cuts require total rank≥4. This invariant covers arbitrary finite common-frame linear programs, not merely bounded depth or a fixed response rowspace.','boundary':'Coordinate-subset projectors of one orthogonal tetrad; ordinary moves nested; source/target terminal charts fixed; all source/target basis operations inside this primitive grammar. Paid arbitrary frame-changing copies allowed. Known-zero work is not live stock. Noncoordinate frames, cross-tetrad/common mixedbank preconditioners, changed terminals and generalized endpoint primitives are outside. Witness scalar/ledger is not a full address compiler or supplier.', 'source_sha256':{f:hashlib.sha256((S/f).read_bytes()).hexdigest() for f in ('check.py','README.md','RESULT.json')}}
(P/'COORDINATE-CUT-AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
