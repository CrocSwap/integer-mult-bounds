"""Exact relative data-port routes and common-label signed target ADD intertwiner."""
from pathlib import Path
from fractions import Fraction as Q
import json,hashlib,gzip
P=Path(__file__).resolve().parent;R=P.parents[3];S=P/'global';rd=lambda p:json.loads(p.read_text());F={int(k):v for k,v in rd(P/'records/frames.json')['frames'].items()};geo=rd(S/'hosted/GEOMETRY.json');m=78
# Sparse exact address matrices; every equality is literal rational arithmetic.
def I(n):return [{i:Q(1)}for i in range(n)]
def add(a,b,c=1):
 r=dict(a)
 for k,v in b.items():
  x=r.get(k,0)+c*v
  if x:r[k]=x
  elif k in r:del r[k]
 return r
def mul(A,B):
 out=[]
 for row in A:
  d={}
  for k,v in row.items():d=add(d,B[k],v)
  out.append(d)
 return out
def trans(A):
 B=[{}for _ in A]
 for i,r in enumerate(A):
  for j,x in r.items():B[j][i]=x
 return B
def inv(A):
 n=len(A);B=[list(r)+[Q(i==j)for j in range(n)]for i,r in enumerate(A)]
 for k in range(n):
  p=next(i for i in range(k,n)if B[i][k]);B[k],B[p]=B[p],B[k];v=B[k][k];B[k]=[x/v for x in B[k]]
  for i in range(n):
   if i!=k:
    v=B[i][k];B[i]=[x-v*y for x,y in zip(B[i],B[k])]
 return [r[n:]for r in B]
def projector(fid,stage,reflected=False):
 B=[[Q(x)for x in r]for r in F[fid]['B']];n=len(B);gram=[[sum(x*y for x,y in zip(a,b))for b in B]for a in B];G=inv(gram)if n else[];A=[{}for _ in range(m)]
 for i in range(8):
  for j in range(8):
   z=sum(B[a][i]*G[a][b]*B[b][j]for a in range(n)for b in range(n))
   if z:A[i][j]=z
 if reflected:
  for i in range(8):A[i]=add({i:Q(1)},A[i],-1)
 for i in range(8,8+7*stage):A[i][i]=Q(1)
 assert mul(A,A)==A and trans(A)==A
 return A
def D(fid,stage,reflected=False):
 A=projector(fid,stage,reflected);Z=[{}for _ in range(2*m)]
 for i in range(m):
  E=add({i:Q(1)},A[i],-1);Z[i]=add(E,{j+m:v for j,v in A[i].items()});Z[i+m]=add(A[i],{j+m:v for j,v in E.items()})
 assert mul(Z,Z)==I(2*m)
 return Z
def chart(port,stage):
 C=I(m);g=geo['ports'][port];r=g['routes'][stage];axes=r['axes'];A=[[Q(x)for x in row]for row in g['rho15']]if stage else[[Q(i==j)for j in range(8)]for i in range(8)]
 for i,a in enumerate(axes):C[a]={axes[j]:x for j,x in enumerate(A[i])if x}
 assert mul(C,trans(C))==I(m)
 # Literal elementary lowering already source-bound, reconstruct here independently.
 if stage:
  Z=I(15)
  for tag,a,b,c in reversed(r['elementary_inverse_replay']):
   if tag=='swap':Z[a],Z[b]=Z[b],Z[a]
   elif tag=='scale':Z[a]={j:x/Q(c)for j,x in Z[a].items()}
   else:Z[a]=add(Z[a],Z[b],-Q(c))
  assert Z==[{j:x for j,x in enumerate(row)if x}for row in A]
  assert len(r['elementary_inverse_replay'])<=77
 Z=[{}for _ in range(2*m)]
 for i in range(m):Z[i]=dict(C[i]);Z[i+m]={j+m:x for j,x in C[i].items()}
 return Z
pairs=[(e['receiver'],e['donor'],e['frame'])for e in rd(P/'PAIR-SELECTION.json')['pairs']]
rows=[];controls=[]
for stage in range(11):
 for u,w,G in pairs:
  Cu,Cw=chart(u-120,stage),chart(w-120,stage);route=mul(Cw,trans(Cu));back=trans(route);assert mul(route,back)==I(2*m)
  for frame,coef in [(0,-1),(G,1)]:
   label=D(frame,stage);Lu=mul(mul(Cu,label),trans(Cu));Lw=mul(mul(Cw,label),trans(Cw));assert mul(Lw,route)==mul(route,Lu)
   refl=D(frame,stage,True);Rlu=mul(mul(Cu,refl),trans(Cu));Rlw=mul(mul(Cw,refl),trans(Cw));assert mul(Rlw,route)==mul(route,Rlu)
   # Define pullback P_R f(x)=f(Rx), with R=Cw Cu^-1.
   # Lu and Lw act by address pullback; Lw R=R Lu implies
   # P_Lu P_R=P_R P_Lw. Thus fu+=c*P_R(fw) commutes
   # with the physical labels. Read the donor at R*x; inverse negates c.
   # under pullback transport R; inverse uses coefficient -c and same chart maps.
   wrong=mul(mul(Cw,D(0 if frame else G,stage)),trans(Cw));assert mul(wrong,route)!=mul(route,Lu);controls.append('wrong-common-label-s%d-u%d-f%d'%(stage,u,frame))
   if stage and mul(Lw,I(2*m))!=mul(I(2*m),Lu):controls.append('omitted-relative-port-route-s%d-u%d-f%d'%(stage,u,frame))
   rows.append(dict(stage=stage,receiver=u,donor=w,frame=frame,signed_coefficient=coef,address_dimension=2*m,all156_address_columns_intertwine=True,route_inverse_transpose=True,route_factor_bound=0 if stage==0 else 154,source_functional_support_not_required_for_arbitrary_current_arrays=True))
t=json.loads(gzip.decompress((S/'hosted/GLOBAL-TEMPLATE.json.gz').read_bytes()));owner_count=0
for call in t['calls']:
 for u,w,G in pairs:
  for frame in [0,G]:
   a,b=call['owners'][u],call['owners'][w];assert a[0]!=b[0];assert a[1]==['data',call['stage'],u-120]and b[1]==['data',call['stage'],w-120];assert a[0]<9600 and b[0]<9600;owner_count+=1
assert owner_count==88*2*len(pairs)
r=dict(source_template_sha256=hashlib.sha256(gzip.decompress((S/'hosted/GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest(),pair_selection_sha256=hashlib.sha256((P/'PAIR-SELECTION.json').read_bytes()).hexdigest(),actual_local_signed_records_sha256=hashlib.sha256((P/'signed-records.bin').read_bytes()).hexdigest(),actual_global_owner_gate_instances=owner_count,forward_and_reflected_complement_labels_checked=True,status='PASS_EXACT_TARGET_TARGET_RELATIVE_PORT_ADDRESS_INTERTWINERS',checks=rows,controls_rejected=controls,gate_instances=len(rows),value_transport_convention='Address R=Cw Cu^-1; receiver at x reads donor at R*x. P_R f(x)=f(R*x). P_Lu P_R=P_R P_Lw. Inverse ADD negates signed coefficient, donor unchanged.',actual_owner_routes='Own95 data owner [family,[data,stage,port]]; normalize via rho(stage,q) on both streams before common D_G ADD.',new_generalized_target_interface='Pointwise signed additions of arbitrary currently labelled stream arrays, routed by explicit relative data-port chart. This proves exact finite address algebra; physical weighted compiler admission of this additional target-as-source rule remains explicit.',maximum_relative_route_factors=154,extra_route_selector_bound=2*11*8*(2*len(pairs))*78*154,source_geometry_sha256=hashlib.sha256((S/'hosted/GEOMETRY.json').read_bytes()).hexdigest(),scope='Exact rational address algebra, all11stages including inverse orthogonal charts, arbitrarydirtyarray pointwise signedADD and per-gate wrong-label controls. No original x_k support containment is asserted or required in this alternate common-label route. No unconditional full compiler proof.')
(P/'OPERATOR.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],len(rows),len(controls),r['extra_route_selector_bound'])
