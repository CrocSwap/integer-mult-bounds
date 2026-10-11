"""Fresh PR484 scalar/prefix lowering and finite overcharge recount. OpenAI Codex.
Reads emitted programs, canonical word and raw routes, importing no supplier code.
Inherited all-size compiler admissibility is a condition, not inferred here.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import gzip,json,math,hashlib
import sys
O=Path(sys.argv[1]);V=Path(sys.argv[2]);HOSTED=Path(sys.argv[3])
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
w=read(V/'split-centres/CANONICAL-WORD.json.gz');p=read(V/'split-centres/LOCAL-PROGRAMS.json.gz');old=read(V/'split-centres/GLOBAL-TEMPLATE.json.gz');new=read(HOSTED/'GLOBAL-TEMPLATE.json.gz');integ=read(V/'split-centres/INTEGRATION.json');checks=read(V/'split-centres/LOCAL-CHECKS.json');prior=read(V/'split-centres/INDEPENDENT-REPLAY.json');owners=read(O/'OWNERS-AND-PROFILE.json')
N=800;M=73;R=560;L=9;T=8;VV=120;K=4
local={}
for ori,evs in p.items():
 rows={('L',i):{i:F(1)}for i in range(N)};env={('L',i):F(1)for i in range(N)};peak=F(1);real=macros=0;paid=Counter();workops=0
 for e in evs:
  if e[0]=='climb':paid[e[5]]+=1
  elif e[0]=='center':paid[e[4]]+=1
  elif e[0]=='scalar':
   macros+=1;x=e[1];op=x[0];a=tuple(x[1]);count=0
   if op=='clear':rows[a]={};env[a]=F(0);count=1
   elif op=='copy':rows[a]=dict(rows[tuple(x[2])]);env[a]=env[tuple(x[2])];count=1
   elif op=='scale':
    q=F(x[2],x[3]);num,den=abs(q.numerator),q.denominator
    assert num and num&(num-1)==0 and den&(den-1)==0
    rows[a]={j:q*v for j,v in rows[a].items()};env[a]*=abs(q)
    count=abs(num.bit_length()-den.bit_length())+int(q<0)
   elif op=='add':
    b=tuple(x[2]);q=F(x[3],x[4]);num,den=abs(q.numerator),q.denominator
    assert a!=b and num>0 and den&(den-1)==0
    # Lower actual coefficient to cleared Horner work. Every intermediate
    # magnitude envelope is explicitly included, before denominator halvings.
    acc=0;count=1
    for i,ch in enumerate(bin(num)[2:]):
     if i:acc*=2;count+=1;peak=max(peak,acc*env[b])
     if ch=='1':acc+=1;count+=1;peak=max(peak,acc*env[b])
    v=F(acc)
    for i in range(den.bit_length()-1):v/=2;count+=1;peak=max(peak,v*env[b])
    assert v==abs(q);count+=2 # signed accumulation and private work clear
    env[a]=env.get(a,F(0))+abs(q)*env[b];rr=rows.setdefault(a,{})
    for j,z in list(rows[b].items()):
     value=rr.get(j,F(0))+q*z
     if value:rr[j]=value
     else:rr.pop(j,None)
    workops+=count
   else:raise AssertionError(op)
   real+=2*count;peak=max(peak,env[a])
 assert all(not row for reg,row in rows.items()if reg[0]=='C')
 for i in range(N):
  expected={i:F(1)}
  if ori=='forward'and 120<=i<240:expected[i-120]=F(1)
  if ori=='backward'and i<120:expected[i+120]=F(-1)
  assert rows['L',i]==expected
 assert peak==F(prior['local'][ori]['prefix_l1_upper']) and peak<2**192
 assert real==checks[ori]['real_component_primitive_bound']and macros==checks[ori]['scalar_macros']
 assert dict(paid)=={int(r):z for r,z in checks[ori]['paid_profile'].items()}
 local[ori]=dict(events=len(evs),macros=macros,real_component_primitives=real,prefix_l1=str(peak),prefix_bits=peak.numerator.bit_length()-peak.denominator.bit_length()+1,coefficient_work_primitive_count=workops,all_exact_columns=N,all_560_dirty_helper_columns_restored=True,private_centres_and_coefficient_work_cleared=True)
centres=len(w['centers']);widths=[9-len(w['frames'][f])for f in w['start'][240:]];enter=sum(x<9 for x in widths)
children=sum(checks['forward']['paid_profile'].values());macros=max(x['macros']for x in local.values());compiler=64*(M+1)**3
adapters=16*(macros+children+N+centres)+64*M
primitive_bound=max(x['real_component_primitives']for x in local.values())+adapters*compiler
bridges=sum(e['kind']=='bridge'for e in old['recipe']);bridgeadd=2*VV*T*bridges;shifts=K*VV*T;moves=2*K*VV*T
oldW=old['live'];oldP=old['physical'];oldNB=(oldW-2*VV*K*T)//L
scalar=sum(local[c['orientation']]['real_component_primitives']for c in old['calls'])
nonlocal_items=4*VV*T*L+2*VV*T*L+2*L*T*R+sum(e['replicas']for e in old['idle_children'])+L*oldNB+bridgeadd+shifts+moves+oldW+oldP+2*L*T*enter*144
outside=8*nonlocal_items+64*M
pervertex=scalar+bridgeadd+shifts+moves+oldW+(72*adapters+outside)*compiler+64*oldP
invoice=integ['finite_invoice'];assert (primitive_bound,adapters,pervertex,compiler)==(invoice['local_primitive_bound'],invoice['local_adapters'],invoice['pervertex'],invoice['compiler'])
# Independent hosted stock rebase, retaining the larger unhosted operation
# overcharge; only the stock and mass in the common router/literal change.
W=new['live'];P=new['physical'];mass=owners['rank_mass'];profile=owners['paid_profile']
assert M*W-mass==2496 and P==W+R+centres+2
rebase=pervertex-oldP*65+P*65-oldW+W;used=max(rebase,pervertex)
r=M//2;group=2**(r*r)
for i in range(1,r+1):group*=2**(2*i)-1
stock=group*P;smass=group*mass;logical=group*used+64;router=compiler*(logical+1)*(stock+1)**2
G,E,C0=2**30000,2**100000,2**210000;B=smass+E;literal=2*G*stock**2+8*smass+4*stock+4+32*M;row=2*stock.bit_length()+9909+252;maxchild=max(map(int,profile))
ineq=dict(local_primitive_bound=primitive_bound<2**48,logical=logical<2**6050,router=router<G,literal=literal<E,mass=B<2**100001,precision=32*M*B*B<C0,tape=2*B+18<C0,row=row<20161,halving=M*M>2*maxchild*maxchild)
assert all(ineq.values())
out=dict(status='PASS_INDEPENDENT_SCALAR_PREFIX_AND_HOSTED_FINITE_INVOICE',local=local,entering_helpers=enter,entrance_rank=sum(9-x for x in widths),local_adapters=adapters,local_primitive_bound=primitive_bound,wrapper_elementary_factors_charged=2*72*enter*144,compiler=compiler,unhosted_pervertex=pervertex,hosted_rebased_pervertex=rebase,conservative_pervertex_used=used,finite=dict(physical_stock_bits=stock.bit_length(),router_bits=router.bit_length(),literal_bits=literal.bit_length(),physical_row_coefficient=row,retained_row_coefficient=20161,required_C0_bits=(32*M*B*B).bit_length(),halving_integer_inequality=[M*M,2*maxchild*maxchild],G_exponent=30000,E_exponent=100000,C0_exponent=210000),strict_checks=ineq,scope='Exact finite recount conditional on inherited all-size compiler/precision/tape and analytic-transfer contracts. Signed accumulation uses the supplier scalar primitive convention.')
(O/'PREFIX-AND-INVOICE.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2),flush=True)
