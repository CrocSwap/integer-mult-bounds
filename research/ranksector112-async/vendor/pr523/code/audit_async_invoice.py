"""Async PR484 scalar/prefix lowering and finite overcharge recount. OpenAI Codex.
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
VV=w['v'];R=w['R'];N=2*VV+R;M=73;L=9;T=8;K=4
assert VV==112 and w['h']==9
PAYLOAD=512
control=read(O/'ASYNC-AUDIT.json')
raw=gzip.decompress((HOSTED/'GLOBAL-TEMPLATE.json.gz').read_bytes());th=hashlib.sha256(raw).hexdigest()
assert th==control['complex_template_sha256']==owners['template_sha256']
assert control['one_owner_per_complete_invocation'] and control['complete_invocations']==72
assert new['local_programs']==old['local_programs'] and new['recipe']==old['recipe']
assert Counter(c['orientation']for c in new['calls'])==Counter(c['orientation']for c in old['calls'])
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
  if ori=='forward'and VV<=i<(2*VV):expected[i-VV]=F(1)
  if ori=='backward'and i<VV:expected[i+VV]=F(-1)
  assert rows['L',i]==expected
 assert peak==F(prior['local'][ori]['prefix_l1_upper']) and peak<2**192
 assert real==checks[ori]['real_component_primitive_bound']and macros==checks[ori]['scalar_macros']
 assert dict(paid)=={int(r):z for r,z in checks[ori]['paid_profile'].items()}
 local[ori]=dict(events=len(evs),macros=macros,real_component_primitives=real,prefix_l1=str(peak),prefix_bits=peak.numerator.bit_length()-peak.denominator.bit_length()+1,coefficient_work_primitive_count=workops,all_exact_columns=N,all_560_dirty_helper_columns_restored=True,private_centres_and_coefficient_work_cleared=True)
centres=len(w['centers']);widths=[9-len(w['frames'][f])for f in w['start'][(2*VV):]];enter=sum(x<9 for x in widths)
children=sum(checks['forward']['paid_profile'].values());macros=max(x['macros']for x in local.values());compiler=64*(M+1)**3
adapters=16*(macros+children+N+centres)+64*M
primitive_bound=max(x['real_component_primitives']for x in local.values())+adapters*compiler
bridges=sum(e['kind']=='bridge'for e in old['recipe']);bridgeadd=2*VV*T*bridges;assert sum(e['kind']=='bridge'for e in new['execution_schedule'])==T*bridges
shifts=K*VV*T;moves=2*K*VV*T
oldW=old['live'];oldP=old['physical'];oldNB=(oldW-2*VV*K*T)//L
scalar=sum(local[c['orientation']]['real_component_primitives']for c in old['calls'])
nonlocal_items=4*VV*T*L+2*VV*T*L+2*L*T*R+sum(e['replicas']for e in old['idle_children'])+L*oldNB+bridgeadd+shifts+moves+oldW+oldP+2*L*T*enter*144
outside=8*nonlocal_items+64*M
pervertex=scalar+bridgeadd+shifts+moves+oldW+(72*adapters+outside)*compiler+64*oldP
invoice=integ['finite_invoice'];assert (primitive_bound,adapters,pervertex,compiler)==(invoice['local_primitive_bound'],invoice['local_adapters'],invoice['pervertex'],invoice['compiler'])
# Independent hosted stock rebase, retaining the larger unhosted operation
# overcharge; only the stock and mass in the common router/literal change.
W=new['live'];P=new['physical'];mass=owners['rank_mass'];profile=owners['paid_profile']
assert M*W-mass==2560 and P==W+R+centres+2
rebase=pervertex-oldP*65+P*65-oldW+W;used=max(rebase,pervertex)
r=M//2;group=2**(r*r)
for i in range(1,r+1):group*=2**(2*i)-1
stock=group*P;smass=group*mass;logical=group*used+64;router=compiler*(logical+1)*(stock+1)**2
G,E,C0=2**30000,2**100000,2**210000;B=smass+E;literal=2*G*stock**2+8*smass+4*stock+4+32*M;row=2*stock.bit_length()+9909+252+2*PAYLOAD;maxchild=max(map(int,profile))
ineq=dict(local_primitive_bound=primitive_bound<2**48,logical=logical<2**6050,router=router<G,literal=literal<E,mass=B<2**100001,precision=32*M*B*B<C0,tape=2*B+18<C0,row=row<20161,halving=M*M>2*maxchild*maxchild)
assert all(ineq.values())
localbits=max(x['prefix_bits']for x in local.values());input_l2_bits=(M+1)//2
bridge_sweeps=sum(e['kind']=='bridge'for e in new['execution_schedule'])
required_prefix=localbits+input_l2_bits+len(new['calls'])+bridge_sweeps+4
assert localbits==21 and bridge_sweeps==72 and required_prefix==206 and required_prefix<PAYLOAD
assert owners['explicit_idle_remainder_children']<=owners['source_idle_children_charged']
assert new['physical']<=old['physical'] and new['live']<=old['live'] and not new['bank_padding']['families']
out=dict(status='PASS_INDEPENDENT_ASYNC_SCALAR_PREFIX_AND_FINITE_INVOICE',template_sha256=th,global_prefix_bits=required_prefix,charged_prefix_bits=PAYLOAD,complete_invocation_sweeps=72,bridge_sweeps=bridge_sweeps,row_prefix_extra=2*PAYLOAD,local=local,entering_helpers=enter,entrance_rank=sum(9-x for x in widths),local_adapters=adapters,local_primitive_bound=primitive_bound,wrapper_elementary_factors_charged=2*72*enter*144,compiler=compiler,unhosted_pervertex=pervertex,hosted_rebased_pervertex=rebase,conservative_pervertex_used=used,finite=dict(physical_stock_bits=stock.bit_length(),router_bits=router.bit_length(),literal_bits=literal.bit_length(),physical_row_coefficient=row,retained_row_coefficient=20161,required_C0_bits=(32*M*B*B).bit_length(),halving_integer_inequality=[M*M,2*maxchild*maxchild],G_exponent=30000,E_exponent=100000,C0_exponent=210000),strict_checks=ineq,scope='Exact finite recount conditional on inherited all-size compiler/precision/tape and analytic-transfer contracts. Signed accumulation uses the supplier scalar primitive convention. Async prefix counts all72individual bridges and72complete invocations;512bits are charged, and an additional2*512 enters the two-level physical row bound.')
(O/'PREFIX-AND-INVOICE.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2),flush=True)

prefix=dict(status='PASS_ASYNC_GLOBAL_PREFIX',template_sha256=th,global_prefix_bits=required_prefix,retained_payload_bits=PAYLOAD,complete_invocation_cover_sweeps=len(new['calls']),bridge_factor_two_sweeps=bridge_sweeps,local_scalar_coefficient_work_prefix_bits=localbits,stream_input_sup_to_l2_bits=input_l2_bits,primitive_arithmetic_margin_bits=4,controller_audit_sha256=hashlib.sha256((O/'ASYNC-AUDIT.json').read_bytes()).hexdigest(),proof=f'Each complete normalized invocation has unitary helper endpoints and a data shear with at most two unitary summands. Distinct full orthogonal owner charts act by right-translation bijections on the retained cover group. Thus the maximum full-stream L2 norm grows by at most2per complete local cover sweep and individual bridge. All72local sweeps and72individual bridge sweeps are counted. Unit-modulus phases, idle children, terminal translations and normalized spectator endpoints are unitary. The independently replayed scalar/Horner envelope costs {localbits} bits, initial sup-to-L2 conversion {input_l2_bits} bits, primitive margin 4 bits: total {required_prefix} < {PAYLOAD}. All-size child/compiler and precision/tape interfaces remain inherited.')
(O/'GLOBAL-PREFIX.json').write_text(json.dumps(prefix,indent=2)+'\n')
