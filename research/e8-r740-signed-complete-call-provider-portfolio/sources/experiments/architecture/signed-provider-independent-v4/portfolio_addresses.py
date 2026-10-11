from pathlib import Path
from fractions import Fraction as Q
import json
P=Path(__file__).resolve().parent;S=P.parent/'bit-provider-portfolio-v4/global';g=json.loads((S/'GEOMETRY.json').read_text());pairs=json.loads((S/'local/PAIR-SELECTION.json').read_text())['pairs']
def I(n):return [{i:Q(1)}for i in range(n)]
def tr(A):
 B=[{}for _ in A]
 for i,r in enumerate(A):
  for j,v in r.items():B[j][i]=v
 return B
def mm(A,B):
 C=[]
 for r in A:
  z={}
  for k,v in r.items():
   for j,w in B[k].items():z[j]=z.get(j,0)+v*w
  C.append({j:v for j,v in z.items()if v})
 return C
m=78;ports={};routes={}
for st in range(11):
 for a in {e['receiver']-120 for e in pairs}|{e['donor']-120 for e in pairs}:
  q=g['ports'][a];C=I(m)
  if st:
   rr=q['routes'][st];ax=rr['axes'];T=q['rho15']
   for i,b in enumerate(ax):C[b]={ax[j]:Q(v)for j,v in enumerate(T[i])if Q(v)}
  assert mm(C,tr(C))==I(m);ports[st,a]=C
checks=[]
for st in range(11):
 for e in pairs:
  u,v=e['receiver']-120,e['donor']-120;Cu,Cv=ports[st,u],ports[st,v];R=mm(Cv,tr(Cu));Ri=mm(Cu,tr(Cv))
  assert mm(R,Ri)==mm(Ri,R)==I(m) and mm(R,Cu)==Cv
  # With L_a=C_a D_F C_a^-1, L_v R=R L_u follows for ANY D_F,
  # including doubled-address D_projector and complemented/reflected labels.
  # P_A P_B=P_(B A); hence receiver reads donor at R*x.
  checks.append([st,u+120,v+120,e['frame']])
r={'status':'PASS_INDEPENDENT_ACTUAL660_PORT_ROUTES_AND_UNIVERSAL_COMMON_LABEL_INTERTWINERS','checks':checks,'all78_chart_columns_orthogonal':True,'address_dimension':156,'inverse_routes':True,'full_value_rule':'For arbitrarycurrentarrays receiverf_u(x)+=c f_v(Rx), R=C_v C_u^-1. Both commonlabels conjugatedbyrespectivecharts, so L_v R=R L_u onalladdresscolumns. Pullbacks composeinreverseorder. InverseADDuses−c withsameunchangeddonor.','reflected':'Universalconjugation proof applies independentlytoanysharedD_F, includinglocalcomplemented/reflectedassignment. ActualinversewordADDlabels alreadyindependentlygated. No assumption aboutcontainmentofdonors originalsourcefunctional isused.','scope':'Finite full-array operator+route theorem. New target-as-source physicalcompiler interface and actualglobal88call ownerbinding/fullpaid154-factorbound must be separatelyadmitted; not a free routing operation.'}
(P/'PORTFOLIO-ADDRESSES.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'])
