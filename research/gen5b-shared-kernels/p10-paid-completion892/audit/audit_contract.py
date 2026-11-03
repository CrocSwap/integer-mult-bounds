from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import support
support.require_assertions()
"""Independently authored, read-only audit of proposed paid49+11 completion.
No source modules, earlier checkers, or upstream programs are executed.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
import json, gzip, hashlib, struct
from pathlib import Path
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
if not __debug__: raise RuntimeError("Assertions must be enabled for this audit")
ROOT=support.BANK
D=ROOT/'split_49_11'; HERE=support.AUDIT
hashes={}
def load(p):
 p=Path(p); b=p.read_bytes(); hashes[str(p)]=hashlib.sha256(b).hexdigest(); return json.loads(b)
r=load(D/'RESULT.json'); a=load(D/'ARITHMETIC-RESULT.json'); phase=load(D/'LOWERING-PLAN.json')
word=load(str(support.WORD))
assert hashes[str(support.WORD)]==r['word_sha256']=='25a0edc8c5f399fcf536b28c4e3575aa52177bb78b6078a631acb748954f0739'
assert r['head']=='1b37957d1520c80b6ea796bf418e52be5109c2d4'
assert r['split']==a['split']==[49,11]
assert a['source_result_sha256']==hashes[str(D/'RESULT.json')]
# Full integer matrices, not finite-field sampling.
N=200; M=100
ident=lambda n:[[int(i==j) for j in range(n)]for i in range(n)]
def mm(X,Y):
 Z=[[0]*len(Y[0])for _ in X]
 for i,row in enumerate(X):
  for k,v in enumerate(row):
   if v:
    for j,u in enumerate(Y[k]):
     if u:Z[i][j]+=v*u
 return Z
I=ident(N); product=I; block_results=[]
for start,rank in [(0,20),(20,20),(40,49),(89,11)]:
 U=[[0]*rank for _ in range(N)]; V=[[0]*N for _ in range(rank)]; P=ident(N)
 for k in range(rank):
  x=start+k;y=199-x
  P[x][x]=P[y][y]=0;P[x][y]=P[y][x]=1
  U[x][k]=1;U[y][k]=-1;V[k][x]=-1;V[k][y]=1
 assert mm(P,P)==I
 assert mm(U,V)==[[P[i][j]-I[i][j]for j in range(N)]for i in range(N)]
 assert mm(V,U)==[[-2*int(i==j)for j in range(rank)]for i in range(rank)]
 # Explicit identity minors prove split rank over every coefficient ring.
 assert [U[start+k]for k in range(rank)]==ident(rank)
 assert [[V[k][199-start-j]for j in range(rank)]for k in range(rank)]==ident(rank)
 product=mm(P,product);block_results.append({'support':[start,start+rank],'rank':rank,'integer_columns':N,'split_factorization':True})
Fswap=[[int(i+j==199)for j in range(N)]for i in range(N)]
assert product==Fswap and mm(product,product)==I
# Omission and repetition fail as exact integer permutations, at every block.
controls=[]
blocks=[(0,20),(20,20),(40,49),(89,11)]
def permutation(seq):
 out=list(range(200))
 for start,rank in seq:
  for j in range(start,start+rank):out[j],out[199-j]=out[199-j],out[j]
 return out
full=list(reversed(range(200)))
for i in range(4):
 assert permutation(blocks[:i]+blocks[i+1:])!=full
 assert permutation(blocks+[blocks[i]])!=full
 controls.extend(['omitted_block_'+str(i),'repeated_block_'+str(i)])
# Audit both permutation witnesses and their replay, independently.
for z in r['endpoints']['complement_projectors']:
 pi=z['generic_witness_permutation'];off=z['offset'];rank=z['rank']
 assert sorted(pi)==list(range(100)) and sorted(pi[off:off+rank])==list(range(rank))
 work=list(range(100))
 for i,j in z['permutation_transpositions']:work[i],work[j]=work[j],work[i]
 assert work==pi and len(z['permutation_transpositions'])==z['permutation_factor_count']<=99
 # The conjugated projector has the exact canonical NE identity submatrix.
 image=set(pi[off:off+rank]); assert image==set(range(rank))
 assert z['normalizer_denominators']==[1] and z['normalizer_scalar_factors']==0
 assert rank<50
assert [z['permutation_factor_count']for z in r['endpoints']['complement_projectors']]==[88,99]
# Distinguish an array factorization from chronological action on columns.
permutation_conventions=[]
for z in r['endpoints']['complement_projectors']:
 def actual_action(x,swaps):
  for i,j in swaps:
   if x==i:x=j
   elif x==j:x=i
  return x
 swaps=z['permutation_transpositions'];pi=z['generic_witness_permutation']
 forward=[actual_action(x,swaps)for x in range(100)]
 reverse=[actual_action(x,swaps[::-1])for x in range(100)]
 assert reverse==pi and forward!=pi
 assert z['chronological_coordinate_transpositions']==swaps[::-1] and z['chronological_inverse_transpositions']==swaps
 assert z['both_coordinate_actions_exact'] and z['unreversed_action_rejected']
 assert [forward[pi[x]]for x in range(100)]==list(range(100))
 permutation_conventions.append({'rank':z['rank'],'stored_array_swaps_action':'pi_inverse','reversed_swaps_action':'pi','cost_unchanged':True})
# Full literal address ledger for a stage; reinstantiate five disjoint stages.
b=gzip.decompress((D/'literal-assignments.bin.gz').read_bytes())
assert hashlib.sha256(b).hexdigest()==r['bank_addresses']['assignment_sha256']
rows=list(struct.iter_unpack('>IIIIII',b));assert len(rows)==8221*60
seen=set();cov=bytearray(85575*100);rolew={};bankroles={};assignmenthash=hashlib.sha256()
for role,rep,bank,off,width,scale in rows:
 assert 0<=rep<60 and 0<=bank<85575 and 0<=off<off+width<=100
 assert 1<=width<=20 and 1<=scale<=25 and (role,rep)not in seen
 seen.add((role,rep));assert rolew.setdefault(role,width)==width
 assert not any(cov[100*bank+off:100*bank+off+width]);cov[100*bank+off:100*bank+off+width]=bytes([1])*width
 bankroles.setdefault(bank,[]).append((role,rep,off,width,scale))
assert len(rolew)==8221 and cov.count(0)==60 and not any(cov[-60:])
assert all(sorted(row[4]for row in members)==list(range(1,len(members)+1))for members in bankroles.values())
# Derive real role widths from source data, without loading any source program.
BASE=support.BASE_OUTPUT;manifest=load(support.INPUT_MANIFEST)
def source_json(name):
 z=next(z for z in manifest['files']if z['path']==name);raw=(support.INPUTS/z['local']).read_bytes()
 assert hashlib.sha256(raw).hexdigest()==z['sha256'] and len(raw)==z['bytes']
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==z['git_blob']
 return json.loads(gzip.decompress(raw)if name.endswith('.gz')else raw)
old=source_json('bitword/selected/bit/word_p10.json.gz');frames=source_json('bitword/selected/bit/frames_p10.json.gz')['frames']
oldroles=sorted(set(range(9120))-{v for u,v in old['pairs']});virtual={1920+i:role for i,role in enumerate(oldroles)}
removed={z['role']for z in source_json('sink-selection.json')['sinks']}
actualroles=set(range(9120))-{v for u,v in word['pairs']}-removed
starts={z['role']:frames[str(z['frame'])]['dim']for z in word['gauges']}
for z in source_json('kernel-selection.json')['families']:
 role=virtual[z['pivot']];assert role not in starts;starts[role]=z['rank']
ends={virtual[z['helper']]:z['rank']for z in source_json('restore-selection.json')['entries']}
assert rolew=={role:ends.get(role,20)-starts.get(role,0)for role in actualroles}
# Every simultaneous block normalizer has a distinct nonzero scalar witness
# outside the active h-window. Distinctness holds modulo every q>25.
patterns={tuple((row[2],row[3],row[4])for row in members)for members in bankroles.values()}
normalizer_patterns=0
for stage in range(5):
 outside=next(j for j in range(100)if not 20*stage<=j<20*(stage+1))
 for pattern in patterns:
  vectors=[]
  for off,width,scale in pattern:
   active=list(range(20*stage,20*stage+width));target=list(range(off,off+width))
   src=active+[j for j in range(100)if j not in active];dst=target+[j for j in range(100)if j not in target]
   pi=dict(zip(src,dst));vectors.append((pi[outside],scale))
  assert len(vectors)==len(set(vectors));normalizer_patterns+=1
assert bankroles[85574][0][2:4]==(0,20) and bankroles[85574][1][2:4]==(20,20) and len(bankroles[85574])==2
assert Counter(role for role,rep in seen)==Counter({role:60 for role in rolew})
for stage in range(5):
 for role,rep,bank,off,width,scale in rows:
  family=230400+stage*85575+bank
  assignmenthash.update(struct.pack('>IIIIIII',stage,role,rep,family,off,width,scale))
assert assignmenthash.hexdigest()==r['bank_addresses']['five_stage_assignment_sha256']
# Full phase ordering, including three boundaries and terminal exchange.
ph=phase['phases'];assert len(ph)==730
cursor=0;comps=[]
for stage in range(5):
 for replica in range(60):
  q=ph[cursor];cursor+=1;assert(q['kind'],q['stage'],q['replica'],q['cover'])==('helper',stage,replica,'all_GL_classes')
 for off,rank in [(40,49),(89,11)]:
  q=ph[cursor];cursor+=1;comps.append(q)
  assert(q['kind'],q['stage'],q['family'],q['rank'],q['coordinate_interval'])==('paid_bank_completion',stage,230400+(stage+1)*85575-1,rank,[off,off+rank])
  assert q['high_fibers']=='batched' and q['weighted_by']=='existing_common_ancestor_chart' and q['cover']=='all_GL_classes'
 if stage in (1,2,4):
  which={1:0,2:1,4:2}[stage]
  for replica in range(60):
   for kind in ('idle','bridge'):
    q=ph[cursor];cursor+=1;assert(q['kind'],q['stage'],q['which'],q['replica'])==(kind,stage,which,replica)
for replica in range(60):
 q=ph[cursor];cursor+=1;assert(q['kind'],q['replica'])==('terminal_exchange',replica)
assert cursor==730
# Invoice is literal-scale; all integer quantities independently recomputed.
S=230400+5*85575;H={int(k):v for k,v in r['literal_profile']['histogram'].items()};E=sum(H.values());mass=sum(k*v for k,v in H.items())
assert(S,E,mass,100*S-mass)==(658275,15002710,65705100,122400)
assert max(H)==49 and 2*max(H)<100
regular=H.copy();regular[49]-=5;regular[11]-=5
assert sum(regular.values())==15002700 and sum(k*v for k,v in regular.items())==65704800
J=60*(24*960+10*8221)+20;K=600*((S-1)+8221*100*599)+20*((S-1)+100*599)
terms={'unit_expanded_additions':60*(5*338173+6*960),'high_affine_factors':J*16*10001**2,'low_transpositions':J*(S+20),'generic_wrappers':E*80008,'matrix_preparation':E*128*200**3,'global_matrix_preparation':16*100**3,'copy_erase_episodes':5*20*60,'paid_child_overhead':E,'bank_selectors':K,'constant':1}
assert terms==r['finite_invoice']['terms'] and sum(terms.values())==25474481435226991
assert J==6315020 and K==295872067880 and K<2**40 and sum(terms.values())<2**80
assert S+20<2**80 and 2*100**3*10**16<2**80
assert 6*200*199+3*200+6*199==240594<320000
assert 64*132143**3*1307556**2==252483531736676034081055177728<2**104
# Independently certify moments by 90-term rational atanh and 40-term exp.
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
root=F(770597243075576,10**18);upper=root+F(1,10**18)
low_m=moment(root);high_m=moment(upper)
assert low_m[1]<1<high_m[0]
# Independent reconstruction of all immutable outer equations.
b=F(772714351296671,10**18);eta=F(1,10**12);beta=F(1,10**9);kappa=F(770003879871513,10**18)
assert root<(1-beta)*b-F(1,10**18)
chain=[F(384599,10**10)]
for i in range(3):chain.append(root*(1-root+chain[-1]))
assert list(map(F,a['assembly']['bootstrap_chain']))==chain
bit=chain[-1];tau=1-bit;sigma=1-b;q=bit*(1-2*eta);lp=1-q;lam=(tau+lp)/2;c=q+eta/4;eps=(1-eta)/(1+q);G=eps*q;rho=(G+1-eps)/2;delta=eta/8
internal=tau+(1-beta)*max(sigma-tau,F(0));leaf=sigma+beta*(1-sigma)
slacks=dict(bit_positive=bit,complex_above_bit=b-bit,complex_below_one_over32=F(1,32)-b,beta_positive=beta,beta_below_one=1-beta,leaf_saving_above_bit=(1-beta)*b-bit,q_positive=q,q_below_internal=1-internal-q,q_below_leaf=1-leaf-q,c_positive=c,c_below_one=1-c,q_below_reservations=c-q,lambda_above_tau=lam-tau,lambda_above_sigma=lam-sigma,lambda_above_internal=lam-internal,lambda_prime_above_lambda=lp-lam,compact_leaf=lp-leaf,compact_reservations=lp-(1-c),lambda_prime_below_one=q,epsilon_positive=eps,epsilon_below_one=1-eps,guard_width=1-eps,K_geometry=1-eps*(1+c),K_dominates_log=eps*c,record_suffix=1-eps,phase_local=1-eps-delta,phase_boundary=rho-delta,gamma_sublinear=1-eps-rho,cell_above_band=eps-(1-rho)/2,prime_interval_packing=1-eps,alpha_positive=rho,alpha_below_one=1-rho,alpha_below_one_fourth=F(1,4)-rho,delta_positive=delta,delta_below_one_eighth=F(1,8)-delta,short_record_fallback=eps-bit,small_field_exposure=1-eps-G,artificial_boundary=8-eps+rho-delta-G,literal_scalar_guard=F(1),row_product_gap=10**6-F(51*20161,25))
margins=dict(balanced_prefix=1-eps,coordinate_movement=bit,compact_phase_layer=G,bulk_exposure=bit,Gaussian_arithmetic=min(1-eps-delta,rho-delta),scalar_work=1-eps-delta,dimension=eps)
slacks.update({k+'_above_kappa':v-kappa for k,v in margins.items()})
assert len(slacks)==47 and slacks=={k:F(v)for k,v in a['assembly']['all_47_strict_slacks'].items()} and min(slacks.values())>0
assert G<kappa+F(1,10**18) and G>kappa
out={'status':'PASS_CONDITIONAL_CONTRACT_ARITHMETIC','input_sha256':hashes,'integer_identity':block_results,'all_200_columns':True,'literal_assignments':len(rows)*5,'phase_plan_count':len(ph),'literal_stock':S,'literal_calls':E,'literal_rank_mass':mass,'selector_calls':K,'finite_coefficient':sum(terms.values()),'moment_bracket':[str(root),str(upper)],'moment_strict_gaps':[str(1-low_m[1]),str(high_m[0]-1)],'kappa':str(kappa),'all_47_recomputed':True,'conditional_bridge_slacks':['literal_scalar_guard','row_product_gap'],'permutation_conventions':permutation_conventions,'negative_controls':controls,'distinct_normalizer_pattern_checks':normalizer_patterns,'retained_interfaces':['generic weighted compiler','common ancestor chart','complete-stream routing','prime supply','restored row reserve','ordinary leaves','complex supplier','precision and recovery','analytic transfer'],'scope_boundary':'The concrete incremental completion emitter is separately audited by audit_lowering.py and finalize_audit.py. Regeneration of the whole inherited regular frame stream is not intrinsically a new paid-completion obligation.','checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(HERE/'AUDIT-RESULT.json').write_text(json.dumps(support.portable(out),indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items()if k not in ('input_sha256','moment_strict_gaps')},indent=2))
