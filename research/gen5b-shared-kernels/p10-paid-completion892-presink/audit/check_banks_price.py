from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import companion as packet
packet.require_assertions()
packet.verify_base()
packet.verify_sources()
"""Original independent bank assignment, endpoint chart and exact price audit."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from functools import lru_cache
import json,gzip,hashlib,struct
import numpy as np
if not __debug__:raise RuntimeError('Assertions must be enabled')
HERE=packet.AUDIT;EXP=packet.EXPERIMENT;LOCAL=packet.ADMISSION;OUT=packet.LOWERING;OLD=packet.BASE_LOWER;hashes={}
def load(p):
 p=Path(p);b=p.read_bytes();hashes[str(p)]=hashlib.sha256(b).hexdigest();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=load(EXP/'RESULT.json');bank=load(EXP/'BANK-RESULT.json');price=load(EXP/'PRICE-RESULT.json');frames=load(LOCAL/'local-frames.json.gz');ep=load(LOCAL/'local-endpoints.json');roles=load(OLD/'compact-role-index.json')['roles'];norms=load(OUT/'normalizers.json.gz');ns=load(OUT/'namespace-hashes.json');phases=load(OUT/'extended-phases.json')
assert bank['composition_result_sha256']==sha(EXP/'RESULT.json')and price['bank_result_sha256']==sha(EXP/'BANK-RESULT.json')
S=658255;E=15006605;mass=65703100;B=85571
assert 230400+5*B==S and 100*S-mass==122400
rolewidth={role:frames[str(ep['final'][str(1920+i)])]['rank']-frames[str(ep['initial'][str(1920+i)])]['rank']for i,role in enumerate(roles)}
assert Counter(rolewidth.values())==Counter({int(k):v for k,v in r['residual_census'].items()})
# Exact new endpoint charts, both inverse products and actual source projector.
def mm(A,B):return [[sum(x*y for x,y in zip(a,b))for b in zip(*B)]for a in A]
charts=[]
for x in bank['changed_endpoint_charts']:
 role=x['virtual_role'];local=x['compact_pivot'];assert roles[local-1920]==role and rolewidth[role]==18
 cols=[[F(y)for y in row]for row in x['basis_columns']];M=list(map(list,zip(*cols)));inv=[[F(y)for y in row]for row in x['inverse']];I=[[int(i==j)for j in range(20)]for i in range(20)]
 assert mm(M,inv)==I and mm(inv,M)==I
 old=frames[str(ep['initial'][str(local)])];new=frames[str(ep['final'][str(local)])];assert(old['rank'],new['rank'])==(2,20)
 annih=[[F(y)for y in row]for row in old['annihilator']];basis=[[F(y)for y in row]for row in old['basis']]
 assert all(sum(x*y for x,y in zip(a,b))==0 for a in annih for b in cols[18:])
 gram=lambda a,b:9*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b)
 assert all(gram(a,b)==0 for a in cols[:18]for b in basis)
 P=mm([row[:18]for row in M],inv[:18]);assert mm(P,P)==P and sum(P[i][i]for i in range(20))==18
 work=[row[:]for row in M]
 for op,i,j,c in x['factor_program']:
  if op=='swap':work[i],work[j]=work[j],work[i]
  elif op=='scale':work[i]=[F(c)*v for v in work[i]]
  else:assert op=='add';work[i]=[a+F(c)*b for a,b in zip(work[i],work[j])]
 assert work==I and len(x['factor_program'])==x['factor_count']==21
 assert all(abs(F(c).numerator)<=1 and F(c).denominator<=2 for op,i,j,c in x['factor_program']if c is not None)
 charts.append(role)
assert len(charts)==3
oldcharts=load(packet.BASE_OUTPUT/"baseline/finite/endpoint-charts.json.gz")
expected_programs={z['program_id']:z for z in oldcharts['factor_programs']}
role_program={z['role']:z['program_id']for z in oldcharts['role_uses']if z['role']in rolewidth}
for j,z in enumerate(bank['changed_endpoint_charts']):
 role_program[z['virtual_role']]=100000+j
 expected_programs[100000+j]={'program_id':100000+j,'rank':18,'donor_dimension':2,'recipient_dimension':20,'basis_columns':z['basis_columns'],'inverse':z['inverse'],'factors':z['factor_program'],'count':z['factor_count']}
assert len(role_program)==2318
assert all(z==expected_programs[z['program_id']]for z in norms['chart_programs'])
assert {z['program_id']for z in norms['chart_programs']}==set(role_program.values())
raw=gzip.decompress((EXP/'new-bank-assignments.bin.gz').read_bytes());assert hashlib.sha256(raw).hexdigest()==bank['assignment_sha256']
assign={};coverage=bytearray(B*100);perbank={}
for role,t,b,off,w,scale in struct.iter_unpack('>6I',raw):
 assert rolewidth[role]==w and 0<=t<60 and 0<=b<B and 0<=off<off+w<=100 and 1<=scale<=25 and(role,t)not in assign
 assert not any(coverage[100*b+off:100*b+off+w]);coverage[100*b+off:100*b+off+w]=b'\1'*w
 assign[role,t]=(b,off,w,scale);perbank.setdefault(b,[]).append((off,w,scale))
assert all(sorted(z[2]for z in rows)==list(range(1,len(rows)+1))for rows in perbank.values())
assert len(assign)==8221*60 and all(coverage[:-100])and coverage[-100:]==b'\1'*80+b'\0'*20
assert perbank[B-1]==[(0,20,1),(20,20,2)]+[(40+4*j,4,j+3)for j in range(10)]
# Universal integer200-column endpoint identity on actual real intervals plus paid20.
state=list(range(200))
for off,w,scale in perbank[B-1]+[(80,20,13)]:
 for j in range(off,off+w):state[j],state[199-j]=state[199-j],state[j]
assert state==list(range(199,-1,-1))
# All300 actual namespace entries and normalizer source/target intervals.
mp=np.frombuffer(gzip.decompress((OUT/'all-namespaces.i32.gz').read_bytes()),dtype='<i4').reshape(5,60,10142,2);registry={x['id']:x for x in norms['normalizers']};active=[(0,1),(1,0),(0,1),(3,2),(2,3)];five=hashlib.sha256()
for s in range(5):
 for t in range(60):
  a=mp[s,t];assert hashlib.sha256(a.tobytes()).hexdigest()==ns[s*60+t]['sha256']and len(set(map(tuple,a.tolist())))==10142
  assert tuple(a[-1])==(S,-1)
  for i in range(1920):assert tuple(a[i])==((4*t+active[s][i//960])*960+i%960,0 if s==0 else 1+s*960+i%960)
  for i,role in enumerate(roles):
   b,off,w,scale=assign[role,t];family,route=map(int,a[1920+i]);z=registry[route-4801]
   assert family==230400+s*B+b and(z['stage'],z['support'],z['rank'],z['scalar'])==(s,[off,off+w],w,scale)
   pi=z['permutation'];assert sorted(pi)==list(range(100))and pi[s*20:s*20+w]==list(range(off,off+w))
   outside=z['outside_column'];assert not s*20<=outside<(s+1)*20 and z['unit_column_witness']==[pi[outside],scale]
   assert z['paid_factor_bound']==599 and z['chart_program']==role_program.get(role,-1)
for s in range(5):
 for role,t,b,off,w,scale in struct.iter_unpack('>6I',raw):five.update(struct.pack('>7I',s,role,t,230400+s*B+b,off,w,scale))
assert five.hexdigest()==bank['five_stage_assignment_sha256']
expected=[]
for s in range(5):
 expected.extend(('helper',s,t)for t in range(60));expected.append(('paid_bank_completion',s,None))
 if s in(1,2,4):expected.extend((k,s,t)for t in range(60)for k in('idle','bridge'))
expected.extend(('terminal_exchange',None,t)for t in range(60));assert len(expected)==len(phases)==725
for i,(p,(kind,s,t))in enumerate(zip(phases,expected)):
 assert p['phase_index']==i and p['kind']==kind and p.get('stage')==s and p.get('replica')==t
 if kind=='paid_bank_completion':
  assert(p['family'],p['rank'],p['support'])==(230400+(s+1)*B-1,20,[80,100]);pi=p['permutation'];inv=p['inverse_permutation'];ops=p['instructions']
  assert sorted(pi)==list(range(100))and[pi[inv[j]]for j in range(100)]==list(range(100))and{inv[k]for k in range(20)}==set(range(80,100))
  assert[op['op']for op in ops]==['ROUTE_RIGHT','COMPILE_SPLIT_IDEMPOTENT','ROUTE_RIGHT','RESTORE_ROW_RESERVE']and ops[0]['matrix']==inv and ops[2]['matrix']==pi
  for field,want in [('chronological_forward',pi),('chronological_inverse',inv)]:
   images=list(range(100))
   for a,b in p[field]:images=[b if x==a else a if x==b else x for x in images]
   assert images==want
H={int(k):v for k,v in r['literal_histogram'].items()};assert(sum(H.values()),sum(k*v for k,v in H.items()),max(H))==(E,mass,42)
localH={int(k):v for k,v in load(LOCAL/'RESULT.json')['one_stage_paid_histogram'].items()};expectedH=Counter({k:v*300 for k,v in localH.items()});expectedH.update({k:115200 for k in(4,19,38,42)});expectedH[20]+=5;assert H==expectedH
J=60*(24*960+10*8221)+10;K=600*((S-1)+8221*100*599)+10*((S-1)+100*599)
terms={'unit_expanded_additions':60*(5*338159+6*960),'high_affine_factors':J*16*10001**2,'low_transpositions':J*(S+20),'generic_wrappers':E*80008,'matrix_preparation':E*128*200**3,'global_matrix_preparation':16*100**3,'copy_erase_episodes':6000,'paid_child_overhead':E,'bank_selectors':K,'constant':1}
assert terms==bank['terms'] and(J,K,sum(terms.values()))==(6315010,295864873940,25478454083580596)
assert S+20<2**80 and K<2**40 and sum(terms.values())<2**80 and 2*max(H)<100
assert 64*132195**3*1307808**2==252879160360511458267619328000<2**104
print('New3charts,all300namespaces,725phases,rank20completion and fullinvoice pass',flush=True)

DEN=10**65
def rounded(x,upper=False):
 z=x*DEN;n=z.numerator//z.denominator
 return F(n+int(upper and z.denominator!=1),DEN)
@lru_cache(None)
def log_interval(x):
 x=F(x);power=0
 while x>2:x/=2;power+=1
 z=(x-1)/(x+1);t=z;lo=F(0)
 for j in range(90):lo+=2*t/F(2*j+1);t*=z*z
 hi=lo+2*t/(181*(1-z*z))
 if power:
  l2,h2=log_interval(F(2));lo+=power*l2;hi+=power*h2
 return rounded(lo),rounded(hi,True)
def ex(x):
 assert 0<=x<F(1,10)
 t=s=F(1)
 for k in range(1,41):t=t*x/k;s+=t
 rem=(t*x/41)/(1-x/42)
 return rounded(s),rounded(s+rem,True)
def moment(alpha):
 low=high=F(0)
 entries=[(k,F(k*v,100*S))for k,v in H.items()]+[(1,F(3200*E,10**16*S))]
 for rank,weight in entries:
  lo,hi=log_interval(F(100,rank));low+=weight*ex(alpha*lo)[0];high+=weight*ex(alpha*hi)[1]
 return low,high
root=F(770601459593856,10**18);upper=root+F(1,10**18)
low_m=moment(root);high_m=moment(upper)
assert low_m[1]<1<high_m[0]
# Independent reconstruction of all immutable outer equations.
b=F(772714351296671,10**18);eta=F(1,10**12);beta=F(1,10**9);kappa=F(770008089898797,10**18)
assert root<(1-beta)*b-F(1,10**18)
chain=[F(384599,10**10)]
for i in range(3):chain.append(root*(1-root+chain[-1]))
assert list(map(F,price['assembly']['bootstrap_chain']))==chain
bit=chain[-1];tau=1-bit;sigma=1-b;q=bit*(1-2*eta);lp=1-q;lam=(tau+lp)/2;c=q+eta/4;eps=(1-eta)/(1+q);G=eps*q;rho=(G+1-eps)/2;delta=eta/8
internal=tau+(1-beta)*max(sigma-tau,F(0));leaf=sigma+beta*(1-sigma)
slacks=dict(bit_positive=bit,complex_above_bit=b-bit,complex_below_one_over32=F(1,32)-b,beta_positive=beta,beta_below_one=1-beta,leaf_saving_above_bit=(1-beta)*b-bit,q_positive=q,q_below_internal=1-internal-q,q_below_leaf=1-leaf-q,c_positive=c,c_below_one=1-c,q_below_reservations=c-q,lambda_above_tau=lam-tau,lambda_above_sigma=lam-sigma,lambda_above_internal=lam-internal,lambda_prime_above_lambda=lp-lam,compact_leaf=lp-leaf,compact_reservations=lp-(1-c),lambda_prime_below_one=q,epsilon_positive=eps,epsilon_below_one=1-eps,guard_width=1-eps,K_geometry=1-eps*(1+c),K_dominates_log=eps*c,record_suffix=1-eps,phase_local=1-eps-delta,phase_boundary=rho-delta,gamma_sublinear=1-eps-rho,cell_above_band=eps-(1-rho)/2,prime_interval_packing=1-eps,alpha_positive=rho,alpha_below_one=1-rho,alpha_below_one_fourth=F(1,4)-rho,delta_positive=delta,delta_below_one_eighth=F(1,8)-delta,short_record_fallback=eps-bit,small_field_exposure=1-eps-G,artificial_boundary=8-eps+rho-delta-G,literal_scalar_guard=F(1),row_product_gap=10**6-F(51*20161,25))
margins=dict(balanced_prefix=1-eps,coordinate_movement=bit,compact_phase_layer=G,bulk_exposure=bit,Gaussian_arithmetic=min(1-eps-delta,rho-delta),scalar_work=1-eps-delta,dimension=eps)
slacks.update({k+'_above_kappa':v-kappa for k,v in margins.items()})
assert len(slacks)==47 and slacks=={k:F(v)for k,v in price['assembly']['all_47_strict_slacks'].items()} and min(slacks.values())>0
assert G<kappa+F(1,10**18) and G>kappa

result={'status':'PASS_INDEPENDENT_NEW_BANKS_INVOICE_AND_EXACT_PRICE','inputs':hashes,'changed_endpoint_charts_verified':charts,'all_assignment_count':2466300,'all_namespaces':300,'phases':725,'paid_completions':5,'completion_rank':20,'stock':S,'calls':E,'rank_mass':mass,'max_rank':max(H),'selector_calls':K,'finite_coefficient':sum(terms.values()),'root_bracket':[str(root),str(upper)],'kappa':str(kappa),'all47exact_slacks_reproduced':True,'adjacent_kappa_rejected':True,'gain_over_paid892':str(kappa-F(770003879871513,10**18)),'scope':'Literal exact price and bank/chart/compiler-interface arithmetic, with inherited weighted compiler, restored rows, ordinary leaves, complex and all-size interfaces.','checker_sha256':sha(__file__)}
(HERE/'BANK-PRICE-AUDIT.json').write_text(json.dumps(packet.portable(result),indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='inputs'},indent=2))
