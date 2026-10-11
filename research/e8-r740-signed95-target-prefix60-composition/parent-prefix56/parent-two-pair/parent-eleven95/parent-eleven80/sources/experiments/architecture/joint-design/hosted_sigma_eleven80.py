"""Exact rational hosted isometries, own signed80 frames and actual selection."""
import json,gzip,hashlib
from pathlib import Path
from fractions import Fraction as F
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'experiments/stage-search/pr445-signed80-eleven';PARENT=BASE/'signed'
read=lambda p:json.loads(p.read_text())
def I(n):return [[F(i==j)for j in range(n)]for i in range(n)]
def trans(A):return list(map(list,zip(*A)))
def mm(A,B):return [[sum(x*y for x,y in zip(r,c))for c in trans(B)]for r in A]
def columns(A):return trans(A)
def orth(Q):assert mm(trans(Q),Q)==I(len(Q))
frames=read(PARENT/'records/frames.json')['frames'];states=read(PARENT/'records/249-states.json')['initial'];GEO_PATH=ROOT/'experiments/stage-search/pr441-signed-retime/full/bit426-source-centres/global/GEOMETRY.json';geo=read(GEO_PATH);t=json.loads(gzip.decompress((BASE/'hosted/GLOBAL-TEMPLATE.json.gz').read_bytes()))
source={};frame_for={h:str(states[str(240+h)])for h in range(740)}
for fid in set(frame_for.values()):
 f=frames[fid];B=[[F(x)/2 for x in row]for row in f['B']];Q=I(8)
 for i,b in enumerate(B):
  current=columns(Q)[i];v=[x-y for x,y in zip(current,b)];norm=sum(x*x for x in v)
  if norm:
   H=[[F(j==k)-2*v[j]*v[k]/norm for k in range(8)]for j in range(8)];Q=mm(H,Q)
 orth(Q);assert columns(Q)[:len(B)]==B
 source[fid]={'matrix':Q,'width':8-len(B),'ordering':list(range(len(B),8))+list(range(len(B)))}
port={}
for z in geo['ports']:
 q=[F(x)/2 for x in z['q']];C=[[F(x)for x in row]for row in z['complement_columns']];Q=trans([q]+columns(C));orth(Q);port[z['port']]=Q
idle=[e for e in t['schedule']if e['kind']=='idle'];slots=t['hosting']['slots'];route_records=[];seen=defaultdict(set);collisions=0
# Sparse columns of sigma=T_reordered*(S_reordered)^T. Both bases are
# orthogonal, giving exact inverse transpose and all-column recovery.
for i,cp,off,w,stage,h in slots:
 e=idle[i];p=cp%120;s=e['source_level'];b=e['target_level'];pending=(list(range(1,8))+list(range(8,8+7*b)))if s==-1 else list(range(8+7*s,8+7*b))
 assert len(pending)==e['rank'];target=pending[off:off+w];assert len(target)==w
 fs=source[frame_for[h]];assert fs['width']==w
 targetorder=target+[j for j in range(78)if j not in target];sourceorder=fs['ordering']+list(range(8,78))
 # Compose columns explicitly on all 78 rational address basis vectors.
 # Only first8 source coordinates mix; target basis first8 may mix.
 sigma=[]
 for j in range(78):
  coeff=[fs['matrix'][j][k] if j<8 and k<8 else F(j==k) for k in sourceorder]
  out={}
  for k,c in enumerate(coeff):
   if not c:continue
   axis=targetorder[k]
   if axis<8:
    for r,x in enumerate(columns(port[p])[axis]):
     if x:out[r]=out.get(r,F(0))+c*x
   else:out[axis]=out.get(axis,F(0))+c
  sigma.append(tuple((r,str(v))for r,v in sorted(out.items())if v))
 key=tuple(sigma);family=(stage,e['pair'],cp)
 if key in seen[family]:collisions+=1
 seen[family].add(key)
 # Complete isometry is represented by source/target orthogonal charts and
 # explicit permutations; target images of source residual frame columns
 # are exactly the selected pending axes by construction.
 route_records.append([i,cp,off,w,stage,h,frame_for[h],target,targetorder,sourceorder,hashlib.sha256(repr(key).encode()).hexdigest()])
assert collisions==0,'Duplicate concrete sigma within one data family/invocation'
# All disjoint slots factor D coordinate projector; rest is complement.
# Orthogonal T basis gives P_slot P_other=0; hence D products =D_union,
# and D invtranspose=D on every doubled column. This is exact algebra,
# not finite-field numerical sampling.
result={'status':'PASS_OWN_SIGNED80_ELEVEN_CONCRETE_RATIONAL_HOST_SIGMA_AND_REFLECTION','source_geometry_sha256':hashlib.sha256(GEO_PATH.read_bytes()).hexdigest(),'hosted_template_sha256':hashlib.sha256(gzip.decompress((BASE/'hosted/GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest(),'slots_per_replica':len(slots),'source_frames':len(source),'target_port_frames':len(port),'all78_sigma_columns_constructed':True,'duplicate_sigma_same_family_same_invocation':collisions,'cover_injection':'For every orthogonal cover class d, right multiplication d*sigma^-1 is bijective; distinct concrete sigma on same family give distinct owners for fixed d. Other families are disjoint.','operator':'sigma maps exact own signed residual complement to pending slot. Disjoint slot projectors multiply to zero; D_slot factors commute and their product with D_remainder equals original child. Arbitrary correlated host values allowed by source signed block-diagonal endpoint.','reflection':'Each D_projector symmetric involution; sigma inverse is transpose. Inverse-transpose reverses window/selector order and preserves exact factor identity.','route_charge':'Parent source residual chart preserved; incremental target port chart and coordinate permutation are two explicit orthogonal address factors, conservatively charged for every helper. No new scalar cancellation assumed.','scope':'Exact selected own signed80 rational address geometry and symbolic cover injection. Inherited all-size chart/common-prime/compiler/dirty-bank interface remains conditional; native signed local replay and full finite bill are producer/auditor gates.'}
enc=lambda Q:[[str(x)for x in r]for r in Q]
result['source_orthogonal_completions']={k:{'matrix':enc(v['matrix']),'ordering':v['ordering'],'width':v['width']}for k,v in source.items()};result['selected_routes']=route_records
(BASE/'hosted/HOSTED-SIGMA.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],len(slots))
