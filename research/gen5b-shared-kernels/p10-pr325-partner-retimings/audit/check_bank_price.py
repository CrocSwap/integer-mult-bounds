from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import packet325 as contract
contract.require_assertions()
contract.verify_inputs()
contract.verify_source()
"""Independent current-word endpoint-chart, literal bank, invoice and price audit."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from functools import lru_cache
import gzip,json,hashlib,struct
import numpy as np
if not __debug__:raise RuntimeError('Assertions must be enabled')
HERE=contract.AUDIT;P=contract.BANK;L=contract.FRAME;SRC=contract.SOURCE
def load(p):
 p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
bank=load(P/'BANK-RESULT.json');price=load(P/'PRICE-RESULT.json');local=load(L/'RESULT.json')
assert price['bank_result_sha256']==sha(P/'BANK-RESULT.json')
for n,h in bank['artifacts'].items():assert sha(P/n)==h
assert bank['source_admission_sha256']==sha(SRC/'RESULT.json')==local['source_result_sha256']
w=load(SRC/'inputs/bitword__selected__bit__word_p10.json.gz');ep=load(L/'local-endpoints.json');frames=load(L/'local-frames.json.gz');fm=load(L/'source-frame-map.json')
roles=sorted(set(range(9060))-{b for a,b in w['pairs']});ga={z['role']:z['frame']for z in w['gauges']if z['role']in roles};width={r:20-frames[str(ep['initial'][str(1920+j)])]['rank']for j,r in enumerate(roles)}
assert len(roles)==8100 and Counter(width.values())=={4:1200,20:6900}
charts=load(P/'endpoint-charts.json.gz');assert charts['roles']==roles and charts['gauge_frames']=={str(r):f for r,f in ga.items()}
I=np.eye(20,dtype=object);G=9*I-np.ones((20,20),dtype=object);factor_max=0
assert len(charts['charts'])==120
for z in charts['charts']:
 src=frames[str(fm[str(z['frame'])])];D=np.asarray([[F(x)for x in row]for row in src['basis']],dtype=object)
 B=np.asarray(z['basis_columns'],dtype=object).T;BI=np.asarray([[F(x)for x in row]for row in z['inverse']],dtype=object)
 assert np.array_equal(B@BI,I)and np.array_equal(BI@B,I)
 assert np.array_equal(B[:,:4].T@G@D.T,np.zeros((4,16),dtype=object))
 assert np.array_equal(np.asarray([[F(x)for x in row]for row in src['annihilator']],dtype=object)@B[:,4:],np.zeros((4,16),dtype=object))
 proj=B[:,:4]@BI[:4,:];assert np.array_equal(proj,np.asarray([[F(x)for x in row]for row in z['projector']],dtype=object))
 assert np.array_equal(proj@proj,proj)and sum(proj[j,j]for j in range(20))==4
 assert np.array_equal(proj@D.T,np.zeros((20,16),dtype=object))
 replay=np.asarray([[F(x)for x in row]for row in B],dtype=object)
 for op,a,b,c in z['factors']:
  if op=='swap':replay[[a,b]]=replay[[b,a]]
  elif op=='scale':replay[a]=F(c)*replay[a]
  else:assert op=='add';replay[a]=replay[a]+F(c)*replay[b]
 assert np.array_equal(replay,I);factor_max=max(factor_max,len(z['factors']))
 assert z['uses']==Counter(ga.values())[z['frame']]
 for op,a,b,c in z['factors']:
  if c is not None:assert abs(F(c).numerator)<=5 and F(c).denominator<=18
assert factor_max==139<=bank['chart_billed_factor_bound']==150
print('All120 exact new-word endpoint charts and factor programs passed',flush=True)
raw=gzip.decompress((P/'literal-bank-assignments.bin.gz').read_bytes());rows=list(struct.iter_unpack('>6I',raw))
assert len(rows)==486000 and hashlib.sha256(raw).hexdigest()==bank['assignment_sha256']
seen=set();bankbytes=bytearray(85680*100);last=-1;replicas=set();allstage=hashlib.sha256()
for role,t,b,o,rank,scale in rows:
 assert role in width and rank==width[role]and 0<=t<60 and(role,t)not in seen;seen.add((role,t))
 if b!=last:assert b==last+1;last=b;replicas=set()
 assert t not in replicas;replicas.add(t)
 assert o%rank==0 and scale==o//rank+1 and 0<=o<=100-rank
 assert(rank==4 and b<2880)or(rank==20 and b>=2880)
 at=b*100+o;assert not any(bankbytes[at:at+rank]);bankbytes[at:at+rank]=b'\1'*rank
assert last==85679 and bankbytes.count(0)==0 and seen=={(r,t)for r in roles for t in range(60)}
for stage in range(5):
 for role,t,b,o,rank,scale in rows:allstage.update(struct.pack('>7I',stage,role,t,230400+stage*85680+b,o,rank,scale))
assert allstage.hexdigest()==bank['five_stage_assignment_sha256']
# Integer full200-column identities for both actual partition patterns.
for pattern in [[4]*25,[20]*5]:
 image=list(range(200));offset=0
 for r in pattern:
  for j in range(offset,offset+r):image[j],image[199-j]=image[199-j],image[j]
  offset+=r
 assert offset==100 and image==list(range(199,-1,-1))
for z in bank['normalizer_distinctness']:
 stage=z['stage'];outside=z['outside'];assert not 20*stage<=outside<20*(stage+1)
 pat=bank['patterns'][z['pattern']]['widths'];offset=0;witness=[]
 for block,(r,p)in enumerate(zip(pat,z['permutation_programs'])):
  pi=p['permutation'];assert sorted(pi)==list(range(100))and pi[20*stage:20*stage+r]==list(range(offset,offset+r))
  images=list(range(100))
  for a,b in p['chronological_coordinate_swaps']:images=[b if j==a else a if j==b else j for j in images]
  assert images==pi and len(p['chronological_coordinate_swaps'])<=99
  witness.append([pi[outside],block+1]);offset+=r
 assert witness==z['unit_column_witnesses']and len({tuple(x)for x in witness})==len(witness)
assert len(bank['normalizer_distinctness'])==10
S=230400+5*85680;H=Counter({int(k):300*v for k,v in local['one_stage_paid_histogram'].items()});H.update({r:115200 for r in(4,19,38,42)})
E=sum(H.values());mass=sum(k*v for k,v in H.items())
assert H==Counter({int(k):v for k,v in bank['literal_histogram'].items()})
assert(S,E,mass,max(H),100*S-mass)==(658800,14514000,65757600,42,122400)
assert bank['completion_children']==0
J=60*(24*960+10*8100);K=600*((S-1)+8100*100*349)
terms={'unit_expanded_additions':60*(5*352560+6*960),'high_affine_factors':J*16*10001**2,'low_transpositions':J*(S+20),'generic_wrappers':E*80008,'matrix_preparation':E*128*200**3,'global_matrix_preparation':16*100**3,'copy_erase_episodes':6000,'paid_child_overhead':E,'bank_selectors':K,'constant':1}
assert terms==bank['terms']and(J,K,sum(terms.values()))==(6242400,170009279400,24857617667871401)
assert S+20<2**80 and K<2**40 and sum(terms.values())<2**80 and 2*max(H)<100
assert 64*22071**3*959838**2==633930847859769478389778176<2**104
print('All2430000 assignments, universal bank endpoints and every finite fee passed',flush=True)

# Retained independently authored exact-interval/47-equation engine.
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
root=F(771206727248877,10**18);upper=root+F(1,10**18)
low_m=moment(root);high_m=moment(upper)
assert low_m[1]<1<high_m[0]
# Independent reconstruction of all immutable outer equations.
b=F(772714351296671,10**18);eta=F(1,10**12);beta=F(1,10**9);kappa=F(770612425424136,10**18)
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


result={'status':'PASS_INDEPENDENT_PR325_BANKS_AND_EXACT_PRICE','bank_result_sha256':sha(P/'BANK-RESULT.json'),'price_result_sha256':sha(P/'PRICE-RESULT.json'),'local_frame_result_sha256':sha(L/'RESULT.json'),'checker_sha256':sha(__file__),'new_word_endpoint_charts':120,'chart_actual_factor_max':factor_max,'chart_paid_factor_bound':150,'normalizer_bound':349,'literal_assignments':2430000,'completion_children':0,'stock':S,'calls':E,'rank_mass':mass,'max_rank':max(H),'selector_calls':K,'finite_coefficient':sum(terms.values()),'root_bracket':[str(root),str(upper)],'kappa':str(kappa),'all47exact_slacks_reproduced':True,'adjacent_kappa_rejected':True,'gain_over_published_presink':str(kappa-F(770008089898797,10**18)),'scope':'Fresh literal complete banks, exact original-source endpoint charts, every fee and independent rational price. Global emitted binding remains separate; retained compiler, prime, restored-row, ordinary-leaf, complex and analytic all-size hypotheses remain explicit.'}
(HERE/'BANK-PRICE-AUDIT.json').write_text(json.dumps(contract.portable(result),indent=2)+'\n');print(json.dumps(contract.portable(result),indent=2))
