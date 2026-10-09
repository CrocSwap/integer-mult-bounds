"""Exact PR104/107 reproduction and conditional completed-core reuse.
The PR117/signed-MRP87 row is new; completed-core transfer is bound separately.
Accepted affine127 files are left unchanged.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from functools import lru_cache
from math import factorial,comb
import hashlib,importlib.util,json
from optimization import ln_interval,floor_grid,ceil_grid,dec
P=Path(__file__).parent
CUR=P/'pr117-public/tree'
def read(path):return json.loads(path.read_text())
tree=read(P/'pr117-public/TREE.json')
commit=read(P/'pr117-public/COMMIT.json')
assert commit['sha']=='cbb05ce504d571546d9b7794c186a613c659c3bf'
assert tree['sha']==commit['sha'] and not tree['truncated']
pins={r['path']:r['sha'] for r in tree['tree'] if r['type']=='blob'}
def pinned(path,name):
 data=path.read_bytes()
 assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==pins[name],name
source=P/'current-public-main/tree/scripts/structured_bulk_assembly.py'
pinned(source,'scripts/structured_bulk_assembly.py')
# Fully audited module: Fraction and definitions only; same PR117 Git blob.
spec=importlib.util.spec_from_file_location('stopped_assembly',source);main=importlib.util.module_from_spec(spec);spec.loader.exec_module(main)
row117=read(CUR/'certificates/deferred-product-complex-input.json')
selected117=read(CUR/'certificates/deferred-product-network.json')
AOLD=Q(384599,10**10);BETA=Q(1,10**6)
previous_path=P/'current-public-main/tree/certificates/copied-centers-network.json'
pinned(previous_path,'certificates/copied-centers-network.json')
previous=read(previous_path);old_stock=previous['finite_bridge']['bit']
assert Q(previous['bit']['saving'])==AOLD and old_stock['halving_degree']*old_stock['wire_bits']==252

def profile(row,groups=None):
 h,v,R,loss=(row[k] for k in ('h','v','R','loss'));m=h*h;N=v*v
 assert v==comb(h,3) and loss==h*(h-1)
 H=row['histogram'].copy();assert sum(r*n for r,n in enumerate(H))==h*R+2*loss
 assert H[h]>=h;H[1]+=h;H[h]-=h
 z=Counter({(h-1)**2:2*N,h-1:4*N,1:N})
 if groups is None:groups={1:v}
 assert sum(k*n for k,n in groups.items())==v
 B=R*sum(groups.values());W=2*N+2*B;L=2*v*loss;s=W*m-N+L
 for k,n in groups.items():
  assert 1<=k<=h and n>0
  if k<h:z[m-h*k]+=2*R*n
 for r,n in enumerate(H):
  if r and n:z[r]+=2*v*n
 z=dict(sorted(z.items()));assert sum(t*n for t,n in z.items())==s
 return dict(dimensions=[h,h],m=m,N=N,B1=B,B2=B,W=W,L=L,total_rank=s,
  deficit=N-L,maxchild=max(z),copied_histogram=H,child_multiplicities=z)

def bridge(bit,phase,row,degree=4000):
 m,W,s,N=(phase[k] for k in ('m','W','total_rank','N'));h,v,c=(row[k] for k in ('h','v','c'))
 local=4*(c+v)+10*v+4*h*v+4*h*h+8*h+8
 terms=[dict(h=h,v=v,c=c,invocations=N//v,local_group_upper=local,copied_center_extra_groups=2*h)]*2
 G=N+sum(t['invocations']*(t['local_group_upper']+t['copied_center_extra_groups']) for t in terms)
 E=64*(W+m+G+1)**3;charge=2*G*W*W+8*s+4*W+4+32*m;B=s+E;C0=32*m*B*B
 r=phase['maxchild'];db,dc=main.halving(bit['m'],bit['maxchild']),main.halving(m,r)
 wb,wc=bit['W'].bit_length(),W.bit_length();coefficient=wb*db+252+wc*dc
 assert charge<E and 2*B*(m-r)>=s+E and 2*B+18<C0
 assert Q(degree)>Q(51*coefficient,25)
 return dict(complex=dict(m=m,W=W,s=s,maxchild=r,halving_degree=dc,wire_bits=wc,scalar_terms=terms,scalar_group_upper=G),
  semantic=dict(E=E,literal_charge=charge,strict_literal_gap=E-charge,B=B,C0=C0,C1=1,
   induction_gap=2*B*(m-r)-s-E,fixed_odd_divisor=h-3,
   exact_grid='One common dyadic grid times the fixed odd divisor to K=G*(D_complex+1); no child rounding'),
  rows=dict(coefficient=coefficient,degree=degree,suffix_slope=4*degree,degree_gap=Q(degree)-Q(51*coefficient,25),
   contract='W_complex^D_complex * W_coarse^D_coarse * W_old^D_old; one preceding prefix and one padding; sequential reuse'),
  bit_coarse=dict(m=bit['m'],W=bit['W'],maxchild=bit['maxchild'],halving_degree=db,wire_bits=wb),ordinary_leaf_row_degree=252)

def public_log(x,grid=10**12):
 power=0
 while x>2:x/=2;power+=1
 def series(x):
  z=(x-1)/(x+1)
  return 2*sum((z**(2*j+1)/(2*j+1) for j in range(24)),Q(0))+2*z**49/(49*(1-z*z))
 return ceil_grid(power*series(Q(2))+series(x),grid)
def public_moment(c,a,grid=10**12,round_exp=False):
 total=Q(0)
 for t,n in c['child_multiplicities'].items():
  u=a*public_log(Q(c['m'],t),grid);b=1+u+u*u/(2*(1-u/3))
  total+=n*t*(ceil_grid(b,grid) if round_exp else b)
 return total/(c['m']*c['W'])

# Independently reproduce the public exact moment, bridge and assembly row.
public=[]
bit117=selected117['bit']['counts'].copy()
bit117['child_multiplicities']={int(t):n for t,n in bit117['child_multiplicities'].items()}
cx117=profile(row117)
assert main.js(cx117)==selected117['complex']['counts']
coarse117=Q(selected117['coarse_bit_saving']);b117=Q(selected117['a_complex'])
ab117=(1-Q(1,1000))*coarse117+Q(1,1000)*AOLD
a117=min(ab117,(1-BETA)*b117-Q(1,10**10))
br117=bridge(bit117,cx117,row117,22000)
k117=Q(selected117['kappa'])
A117=main.assembly(a117,b117,br117,k117,beta=BETA)
A117['parameters']['actual_bit_saving']=ab117
assert main.js(br117)==selected117['finite_bridge']
assert main.js(A117)==selected117['assembly']
assert ab117==Q(selected117['ordinary_bit_saving']) and a117==Q(selected117['assembly_bit'])
assert public_moment(bit117,coarse117,1<<100,True)==Q(selected117['bit']['moment_upper'])<1
assert public_moment(bit117,coarse117+Q(1,10**10),1<<100,True)>1
assert public_moment(cx117,b117)==Q(selected117['complex']['moment_upper'])<1
assert public_moment(cx117,b117+Q(1,10**10))>1
assert k117<Q(A117['minimum_margin'])<k117+Q(1,10**10)
public.append(dict(name='public117',public_complete_arithmetic_reproduced=True,
 complex_producer_regenerated=True,bit_producer_regenerated=False,kappa=str(k117)))
print('public117 complete arithmetic PASS; complex producer separately regenerated',flush=True)

@lru_cache(None)
def logs(m,t):
 l,u=ln_interval(Q(m,t),terms=50);return floor_grid(l,10**30),ceil_grid(u,10**30)
def ex(x):
 assert 0<=x<1
 v=sum((x**j/factorial(j) for j in range(9)),Q(0));return v,v+2*x**9/factorial(9)
def moment(c,a):
 lo=hi=Q(0)
 for t,n in c['child_multiplicities'].items():
  l,u=logs(c['m'],t);w=Q(t*n,c['m']*c['W']);lo+=w*ex(a*l)[0];hi+=w*ex(a*u)[1]
 return lo,hi
def certify(c):
 grid=10**22;l,u=0,grid//1000
 assert moment(c,Q(u,grid))[0]>1
 while u-l>1:
  k=(l+u)//2;a,b=moment(c,Q(k,grid))
  if b<1:l=k
  elif a>1:u=k
  else:raise AssertionError('enclosure needs sharpening')
 a=Q(l,grid);gap=floor_grid(1-moment(c,a)[1],10**40);bad=floor_grid(moment(c,Q(u,grid))[0]-1,10**40)
 assert gap>0 and bad>0
 return dict(saving=a,decimal=dec(a),moment_gap_lower=gap,next_grid_rejected=Q(u,grid),next_grid_excess_lower=bad)

def cutoffs(br,A):
 # Same retained positive-power comparisons, but explicitly using all THREE
 # row reserves rather than calling a two-reserve bridge validator.
 ceil=lambda x:-(-x.numerator//x.denominator)
 p=A['parameters'];e,c,r,beta=(p[k] for k in ('epsilon','c','alpha_squared_power','beta'))
 ka,km,kb,ks=(ceil(1/x) for x in (r,e*c,1-e,e*beta))
 C0=br['semantic']['C0'];largest=max(br['bit_coarse']['m'],br['complex']['m'])
 cuts=dict(guard=ceil(Q((2*C0).bit_length())/(1-e)),normalization=ceil(7/(1-e-r)),
  alpha=16*ka*ka+1,compact=64*km*km+1,geometry=ceil(3/(1-e*(1+c))),
  phase_cell=ceil(9/(e-(1-r)/2)),period=128*kb*kb+1,
  stopped_leaf=ks*(4*largest).bit_length(),log_p=25,reservoir=14)
 common=max(cuts.values());assert common>=max(2*ka,2*km,2*kb,25)
 checks=[]
 for j in range(6):
  z=common*2**j
  pairs=dict(alpha=(z//ka,8*(z+ka)+64),compact=(z//km,32*(z+km)+192),
   period=(z//kb,16*(z+kb)+56),rows=(z//kb,br['rows']['suffix_slope']*(z+kb+8)),leaf=(z//ks,4*largest))
  assert all(x>=y.bit_length() for x,y in pairs.values())
  checks.append(dict(log2_input=z,powers={k:dict(exponent=x,rhs=y,rhs_bits=y.bit_length()) for k,(x,y) in pairs.items()}))
 return dict(cutoff_log2_input=cuts,common_cutoff=common,power_checkpoints=checks,
  all_interval_argument='Same retained interval padding: on [Z,Z+k), bound RHS at Z+k and LHS at floor(Z/k); successive LHS doubles while affine RHS grows at most linearly.',
  inherited_thresholds='Prime supply, eligible fixed rational basis and native setup, catalogue/descriptor bounds and exact recovery remain.',practical_runtime_claim=False)

op=read(P/'round8-network-opposite-profile.json')
assert op['word_sha256']==hashlib.sha256((P/'round8-foundations-minimal-v-word.json.gz').read_bytes()).hexdigest()
literal=read(P/'round8-network-minimal-v-ledger/result.json')
assert op['ledger_sha256']==hashlib.sha256((P/'round8-network-minimal-v-ledger/result.json').read_bytes()).hexdigest()
opbit=dict(m=op['m'],W=op['W'],maxchild=op['maxchild'],total_rank=op['s'],
 child_multiplicities={int(t):n for t,n in op['hist'].items()})
assert sum(t*n for t,n in opbit['child_multiplicities'].items())==op['s']==op['m']*op['W']-op['deficit']
coarse=certify(opbit);theta=Q(1,1000);effective=(1-theta)*coarse['saving']+theta*AOLD
rank_moment=Q(opbit['total_rank'],opbit['m']*opbit['W'])
assert 0<rank_moment<1 and theta>coarse['saving']>effective>AOLD>0
print('opposite coarse',coarse['decimal'],'stopped',dec(effective),flush=True)
rows=[];row=row117
frozen_path=P/'pr-network-mrp24-signed.json'
assert hashlib.sha256(frozen_path.read_bytes()).hexdigest()=='9117d3f010354fa2f32d5c5fb324b280977e82e76060a70a867767a90989ccaa'
frozen=read(frozen_path)
for name,groups in [('reuse117-mrp',{int(k):n for k,n in frozen['group_size_counts'].items()})]:
 c=profile(row,groups);cm=certify(c);b=cm['saving'];a=min(effective,(1-BETA)*b-Q(1,10**10))
 br=bridge(opbit,c,row,22000);assemblies=[]
 if groups:
  # Retain the already reproduced PR117 semantic constants conservatively.
  # Only physical W, child rank sum and the paid stock are reduced/changed.
  for key in ('E','B','C0','C1'):br['semantic'][key]=selected117['finite_bridge']['semantic'][key]
  sm=br['semantic'];sm['strict_literal_gap']=sm['E']-sm['literal_charge']
  sm['induction_gap']=2*sm['B']*(c['m']-c['maxchild'])-c['total_rank']-sm['E']
  sm['odd_grid_width_slack']=sm['C0']-2*sm['B']-18-5*br['complex']['scalar_group_upper']*(br['complex']['halving_degree']+1)
  assert sm['strict_literal_gap']>0 and sm['induction_gap']>0 and sm['odd_grid_width_slack']>0
  br['retained_semantic_constants']='PR117 complete unreused circuit; larger than needed after sharing'
 for eta in (Q(1,10**8),Q(1,10**16)):
  q=a*(1-2*eta);eps=(1-eta)/(1+q+q*(1+eta));k=floor_grid(eps*q,10**17)
  A=main.assembly(a,b,br,k,eta=eta,beta=BETA)
  assert len(A['strict_constraints'])==47 and len(A['margins'])==7
  assert k+Q(1,10**17)>A['minimum_margin']
  assemblies.append(dict(eta=eta,kappa=k,kappa_decimal=dec(k),certificate=A,cutoffs=cutoffs(br,A)))
 rows.append(dict(name=name,status='arithmetic candidate; separate completed-core reuse proof required' if groups else 'inherited PR107 complex construction',
  groups=groups,profile=c,complex_moment=cm,actual_stopped_bit=effective,assembly_bit=a,bridge=br,assemblies=assemblies))
 print(name,cm['decimal'],assemblies[-1]['kappa_decimal'],'rowdegree',br['rows']['degree'],flush=True)
final=rows[-1]
assert final['profile']['W']==2*final['profile']['N']+2*87*row['R']
assert final['groups']=={8:4,24:83}
assert final['profile']['maxchild']==529
final['exterior_histogram']={'384':8*row['R']}
final['zero_rank_bridges_omitted']=2*row['R']*83
phasecheck=read(P/'pr-foundations-mrp-phase.json')
interface=read(P/'pr-foundations-mrp-interface.json')
for key in ('all_triples_once','all_actual_Z4_phase_identities','all_complement_bases_explicit',
 'all_tensor_scalar_phases_one','exact_inverse_direction_identity','exact_gaussian_composition',
 'exact_stage2_gauge','wrong_source_sign_negative_control'):assert phasecheck[key]
assert phasecheck['partition_sha256']==interface['partition_sha256']==hashlib.sha256(frozen_path.read_bytes()).hexdigest()
assert interface['phase_receipt_sha256']==hashlib.sha256((P/'pr-foundations-mrp-phase.json').read_bytes()).hexdigest()
assert interface['physical_scalar_receipt_sha256']==hashlib.sha256((P/'round8-foundations-reuse117-ledger.json').read_bytes()).hexdigest()
assert interface['core_interface_receipt_sha256']==hashlib.sha256((P/'round8-foundations-reuse117-interface.json').read_bytes()).hexdigest()
for key,other in [('W','W'),('rank_mass','total_rank'),('deficit','deficit'),('max_child','maxchild')]:assert interface[key]==final['profile'][other]
assert {int(t):n for t,n in interface['complete_child_multiplicities'].items()}==final['profile']['child_multiplicities']
assert interface['G0']==final['bridge']['complex']['scalar_group_upper']
assert phasecheck['exterior_histogram']==final['exterior_histogram']
assert phasecheck['zero_rank_bridges_omitted']==final['zero_rank_bridges_omitted']
assert Q(final['assemblies'][-1]['kappa'])>Q(1,8192)
final['status']='CONDITIONAL CONSTRUCTION: regenerated PR117 complex producer and complete signed/core audit, signed MRP87 completed-core sharing, literal opposite-bank bit word. Inherited stopped/normal-form/analytic/tape interfaces remain explicit.'
replay=read(P/'round8-optimize-reuse117-producer.json')
assert all(value==row[key] for key,value in replay['matched'].items())
assert replay['producer_sha256']==hashlib.sha256((CUR/'scripts/deferred_product/replayed.py').read_bytes()).hexdigest()
auditfiles=['pr-foundations-mrp-phase.py','pr-foundations-mrp-phase.json',
 'pr-foundations-mrp-interface.py','pr-foundations-mrp-interface.json','pr-foundations-mrp-interface.txt',
 'pr-foundations-mrp-control.json',
 'round8-foundations-reuse117-interface.py','round8-foundations-reuse117-interface.json','round8-foundations-reuse117-interface.txt',
 'round8-foundations-reuse117-ledger.py','round8-foundations-reuse117-ledger.json','round8-optimize-reuse117-producer.py','round8-optimize-reuse117-producer.json',
 'pr-network-mrp24-signed.json','pr-network-mrp24.py',
 'pr117-public/DOWNLOAD_AUDIT.json','pr117-public/INHERITED_SOURCE_AUDIT.json',
 'pr117-public/TREE.json','pr117-public/COMMIT.json',
 'pr117-public/tree/scripts/deferred_product/replayed.py',
 'pr117-public/tree/certificates/deferred-product-complex-input.json',
 'pr117-public/tree/certificates/deferred-product-complex-dag.json.gz',
 'pr117-public/tree/certificates/deferred-product-network.json',
 'pr117-public/tree/scripts/deferred_product_network.py',
 'round8-network-opposite-profile.py','round8-network-opposite-profile.json',
 'round8-network-pr104-audit.txt','round8-network-pr104-check.py','round8-network-pr104-check.json',
 'round8-network-minimal-v-ledger/result.json']
out=dict(status=final['status'],construction_audit_sha256={f:hashlib.sha256((P/f).read_bytes()).hexdigest() for f in auditfiles},
 public=public,opposite_coarse=coarse,coarse_rank_moment=rank_moment,
 theta=theta,adapter_toll_exponent=1-theta,adapter_saving_gap=theta-coarse['saving'],
 ordinary_leaf=AOLD,actual_stopped_bit=effective,
 opposite_profile_sha256=hashlib.sha256((P/'round8-network-opposite-profile.json').read_bytes()).hexdigest(),
 source_sha256={str(source.relative_to(P)):hashlib.sha256(source.read_bytes()).hexdigest(),
 'optimization.py':hashlib.sha256((P/'optimization.py').read_bytes()).hexdigest()},results=rows)
Path(__file__).with_suffix('.json').write_text(json.dumps(main.js(out),indent=2)+'\n')
