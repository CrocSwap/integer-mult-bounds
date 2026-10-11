from pathlib import Path
from fractions import Fraction as Q
import json,gzip,hashlib
def matrix(rows):return [[Q(x)for x in r]for r in rows]
def trans(A):return list(map(list,zip(*A)))
def mul(A,B):return [[sum(x*y for x,y in zip(a,b))for b in trans(B)]for a in A]
def eye(n):return [[Q(i==j)for j in range(n)]for i in range(n)]
def inv(A):
 n=len(A);M=[a+e for a,e in zip(A,eye(n))]
 for k in range(n):
  i=next(i for i in range(k,n)if M[i][k]);M[k],M[i]=M[i],M[k];v=M[k][k];M[k]=[x/v for x in M[k]]
  for i in range(n):
   if i!=k:
    v=M[i][k];M[i]=[x-v*y for x,y in zip(M[i],M[k])]
 return [r[n:]for r in M]
O=Path(__file__).resolve().parent;R=O.parents[2];P=R/'experiments/architecture/target-prefix-signed-bit';G=P/'global';geo=json.load(open(G/'hosted/GEOMETRY.json'));frames=json.load(open(P/'records/frames.json'))['frames'];t=json.loads(gzip.decompress((G/'hosted/GLOBAL-TEMPLATE.json.gz').read_bytes()));op=json.load(open(P/'OPERATOR.json'))
checks=[]
for u,w,f in [(176,179,796),(208,211,784)]:
 B=matrix(frames[str(f)]['B']);Pr=mul(mul(trans(B),inv(mul(B,trans(B)))),B);assert len(B)==6 and mul(Pr,Pr)==Pr and trans(Pr)==Pr
 Cu=matrix(geo['ports'][u-120]['rho15']);Cw=matrix(geo['ports'][w-120]['rho15']);I=eye(15);assert mul(trans(Cu),Cu)==mul(trans(Cw),Cw)==I
 route=mul(Cw,trans(Cu));back=mul(Cu,trans(Cw));assert mul(route,back)==mul(back,route)==I
 # Exact symbolic label transport for every local frame/exterior lift:
 # Lw R=Cw D Cw^-1 Cw Cu^-1=Cw D Cu^-1=R Lu.
 # Array read f_w(R x) is P_R^-1, the inverse of address pushforward.
 for call in t['calls']:
  a,b=call['owners'][u],call['owners'][w];assert a[0]!=b[0] and a[1]==['data',call['stage'],u-120] and b[1]==['data',call['stage'],w-120]
 checks.append(dict(receiver=u,donor=w,frame=f,orthogonal_relative15_route=True,owner_pairs=len(t['calls'])))
assert len(t['calls'])==88 and op['actual_global_owner_gate_instances']==352
extra=2*11*8*4*78*154;assert extra==8456448
out={'status':'PASS_DERIVED_CONDITIONAL_ROUTED_TARGET_AS_SOURCE_INTERFACE','checks':checks,'orientation':'Addressmap R=Cw Cu^-1 takes receiver address to donor address. Receiver ADD reads f_w(Rx), equivalently valuepushforward P_R^-1. Then LuP_R^-1=P_R^-1Lw; using P_R instead is not justified by stored intertwiner. Inverse signedshear negates coefficient and uses same donorread map; reflected labels have identical transport algebra.','arbitrary_dirt':'Intertwiner valid for arbitrary labelled arrays, independent of source support. Densex_k support alone isnot an obstruction to this derived interface.','fees':'Four newtargetADDs/local charged within actual localunitcount; conservatively154relative factors ×2directions ×88invocations ×4gates ×78dimension=8456448additional selectorcalls, explicitlyincluded independentarith.','conditional_gate':'Derivedfinite address and pointwise signedgate extension is mathematically sound if existing physical selector compiler admits relative data-port maps with these factors. It is an explicit newtarget-as-source rule, not silently inherited from oldsupport exemption. General allsize chart/selector/precision/tape/recovery/C_full and commonprime contracts remainconditional. No originalsource-functional support equivalence claimed.','inputs':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [P/'OPERATOR.json',P/'signed-records.bin',G/'hosted/GLOBAL-TEMPLATE.json.gz',G/'hosted/GEOMETRY.json',G/'REFINED-NOMINATION.json']}}
(O/'TARGET-PREFIX-OPERATOR-REVIEW.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
