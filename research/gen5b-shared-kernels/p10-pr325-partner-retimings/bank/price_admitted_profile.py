from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import packet325 as contract
contract.require_assertions()
contract.verify_inputs()
contract.verify_source()
"""Original independent rational moment and 47-slack calculator.
Only Python's standard library is executed. Original frozen proof programs
are read as inert formulas; no earlier calculator is imported.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
from decimal import Decimal,localcontext
from functools import lru_cache
import json,hashlib
if not __debug__:raise RuntimeError('Assertions required')
HERE=contract.BANK;GRID=10**18;FINE=10**85
MAN=json.loads((contract.HERE/'bank/BANK-SOURCES.json').read_text());sourcehash={}
for name in ['outer.py','proof/three-stage-cover-bit.tex','proof/three-stage-cover-rows.tex']:
 local=name.replace('/','__')+'.txt';row=MAN[local];raw=contract.input_for(name).read_bytes()
 assert row['source_path']==name and hashlib.sha256(raw).hexdigest()==row['sha256'];sourcehash[name]=row['sha256']
def floorq(x):return x.numerator//x.denominator
def ceilq(x):return -floorq(-x)
def down(x):return Q(floorq(x*FINE),FINE)
def up(x):return Q(ceilq(x*FINE),FINE)
def dec(x):
 with localcontext()as c:c.prec=55;return str(Decimal(x.numerator)/Decimal(x.denominator))
@lru_cache(None)
def lnsmall(x):
 assert 1<=x<=2;z=(x-1)/(x+1);power=z;v=Q(0)
 # Positive atanh expansion; the geometric bound includes every omitted term.
 for j in range(100):v+=2*power/(2*j+1);power*=z*z
 tail=2*power/(201*(1-z*z));return down(v),up(v+tail)
@lru_cache(None)
def ln(x):
 x=Q(x);assert x>=1;k=0
 while x>2:x/=2;k+=1
 a,b=lnsmall(x);c,d=lnsmall(Q(2));return a+k*c,b+k*d
def expbounds(x):
 assert 0<=x<Q(1,10);total=term=Q(1)
 for j in range(1,33):term*=x/j;total+=term
 tail=term*x/33/(1-x/34)
 return down(total),up(total+tail)
def moment(H,S,alpha):
 lo=hi=Q(0)
 for r,n in H.items():
  l,u=ln(Q(100,r));a=expbounds(alpha*l)[0];b=expbounds(alpha*u)[1];weight=Q(r*n,100*S);lo+=weight*a;hi+=weight*b
 l,u=ln(Q(100));weight=Q(32*100*sum(H.values()),10**16*S)
 return lo+weight*expbounds(alpha*l)[0],hi+weight*expbounds(alpha*u)[1]
def bracket(H,S):
 # Decimal arithmetic only proposes; exact rational intervals certify.
 with localcontext()as c:
  c.prec=70;low=Decimal(0);high=Decimal('.001');terms=[(Decimal(r*n)/Decimal(100*S),(Decimal(100)/r).ln())for r,n in H.items()]
  fallback=Decimal(3200*sum(H.values()))/(Decimal(10)**16*S);logm=Decimal(100).ln()
  for _ in range(180):
   a=(low+high)/2;v=sum(w*(a*l).exp()for w,l in terms)+fallback*(a*logm).exp()
   if v<1:low=a
   else:high=a
  tick=int(low*GRID)
 lower=Q(tick,GRID);upper=Q(tick+1,GRID);lm=moment(H,S,lower);um=moment(H,S,upper)
 assert lm[1]<1<um[0]
 return {'lower':str(lower),'upper':str(upper),'lower_moment':list(map(str,lm)),'upper_moment':list(map(str,um)),'strict_lower_gap':str(1-lm[1]),'strict_upper_rejection':str(um[0]-1)}
def assemble(root,finite_coefficient):
 b=Q(772714351296671,GRID);eta=Q(1,10**12);beta=Q(1,10**9);cap=(1-beta)*b
 assert root<cap;chain=[Q(384599,10**10)];cutoffs=[]
 for j in range(3):
  old=chain[-1];a=(1-root)*root+root*old
  assert old<a<root<1-a
  gaps={'atom':root-a,'borrowing':1-a-root,'remainder':1-a-root*(1-old),'stock':1-root}
  delta=min(gaps.values());assert delta>0
  L=max(1,ceilq(36/delta**2),ceilq(2*(4+(finite_coefficient-1).bit_length())/delta))
  assert L*delta**2>=36 and L*delta>=2*(4+(finite_coefficient-1).bit_length())
  cutoffs.append({'stage':j+1,'gaps':{k:str(v)for k,v in gaps.items()},'cutoff_log2_charged_coefficient':str(L),'full_cutoff_requires_primitive_and_old_leaf_constants':True});chain.append(a)
 a=chain[-1];tau=1-a;sigma=1-b;q=a*(1-2*eta);lp=1-q;lam=(tau+lp)/2;c=q+eta/4;eps=(1-eta)/(1+q);G=eps*q;r=(G+1-eps)/2;delta=eta/8
 internal=tau+(1-beta)*max(sigma-tau,Q(0));leaf=sigma+beta*(1-sigma)
 margins={'balanced_prefix':1-eps,'coordinate_movement':a,'compact_phase_layer':G,'bulk_exposure':a,'Gaussian_arithmetic':min(1-eps-delta,r-delta),'scalar_work':1-eps-delta,'dimension':eps}
 k=Q(ceilq(min(margins.values())*GRID)-1,GRID)
 # Direct independent transcription of the immutable outer.py displayed equations.
 slacks={'bit_positive':a,'complex_above_bit':b-a,'complex_below_one_over32':Q(1,32)-b,'beta_positive':beta,'beta_below_one':1-beta,'leaf_saving_above_bit':(1-beta)*b-a,
 'q_positive':q,'q_below_internal':1-internal-q,'q_below_leaf':1-leaf-q,'c_positive':c,'c_below_one':1-c,'q_below_reservations':c-q,
 'lambda_above_tau':lam-tau,'lambda_above_sigma':lam-sigma,'lambda_above_internal':lam-internal,'lambda_prime_above_lambda':lp-lam,'compact_leaf':lp-leaf,'compact_reservations':lp-(1-c),'lambda_prime_below_one':q,
 'epsilon_positive':eps,'epsilon_below_one':1-eps,'guard_width':1-eps,'K_geometry':1-eps*(1+c),'K_dominates_log':eps*c,'record_suffix':1-eps,'phase_local':1-eps-delta,'phase_boundary':r-delta,'gamma_sublinear':1-eps-r,'cell_above_band':eps-(1-r)/2,'prime_interval_packing':1-eps,
 'alpha_positive':r,'alpha_below_one':1-r,'alpha_below_one_fourth':Q(1,4)-r,'delta_positive':delta,'delta_below_one_eighth':Q(1,8)-delta,'short_record_fallback':eps-a,'small_field_exposure':1-eps-G,'artificial_boundary':8-eps+r-delta-G,
 'literal_scalar_guard':Q(1),'row_product_gap':Q(10**6)-Q(51*20161,25)}
 slacks.update({name+'_above_kappa':val-k for name,val in margins.items()})
 assert len(slacks)==47 and all(x>0 for x in slacks.values())
 assert min(margins.values())==G and margins['balanced_prefix']-G==eta
 assert slacks['gamma_sublinear']==eta/2 and slacks['K_geometry']==eta*(1-eps/4)
 assert slacks['q_below_internal']==2*a*eta and slacks['q_below_leaf']==(1-beta)*b-a+2*a*eta
 assert slacks['small_field_exposure']==eta
 rejected=[name+'_above_kappa' for name,val in margins.items()if val<=k+Q(1,GRID)]
 assert rejected==['compact_phase_layer_above_kappa']
 return {'coarse_bit':str(root),'coarse_complex':str(b),'complex_leaf_cap':str(cap),'binding':'bit','bootstrap_chain':list(map(str,chain)),'bootstrap_cutoffs':cutoffs,'backoff':str(eta),'beta':str(beta),'all_47_strict_slacks':{n:str(v)for n,v in slacks.items()},'seven_margins':{n:str(v)for n,v in margins.items()},'kappa':str(k),'kappa_decimal':dec(k),'adjacent_kappa_rejected':rejected}


# This consumes the fresh current bank invoice, rather than a fee cap.
M=json.loads((contract.INERT/'MANIFEST.json').read_text())['files']
assert all(M[n]==h for n,h in sourcehash.items())
bank=json.loads((HERE/'BANK-RESULT.json').read_text());assert bank['selected_retimings']==480 and bank['completion_children']==0
H={int(r):n for r,n in bank['literal_histogram'].items()};S=bank['literal_stock'];cert=bracket(H,S);a=assemble(Q(cert['lower']),bank['coefficient']);benchmark=Q(770008089898797,GRID)
assert Q(a['kappa'])>benchmark and sum(H.values())==14514000 and sum(r*n for r,n in H.items())==65757600
out={'status':'PASS_EXACT_ADMITTED_LOCAL_PROFILE_AND_BANK_PRICE_PENDING_GLOBAL_BINDING','bank_result_sha256':hashlib.sha256((HERE/'BANK-RESULT.json').read_bytes()).hexdigest(),'source_admission_sha256':bank['source_admission_sha256'],'source_head':'0eca9340a3df6141b8e71a41638c3937b3522888','retained_contract_source_hashes':sourcehash,'literal_stock':S,'literal_children':sum(H.values()),'literal_rank_mass':sum(r*n for r,n in H.items()),'finite_coefficient':bank['coefficient'],'exact_bit_bracket':cert,'assembly':a,'published_benchmark':str(benchmark),'gain':str(Q(a['kappa'])-benchmark),'gain_decimal':dec(Q(a['kappa'])-benchmark),'all_edge_fallback_charged':True,'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'New local retimings admitted separately; fresh endpoints, literal complete banks, full finite invoice, all fallback children, exact moment and 47 inequalities checked. Full helper/target frame invariant and source-bound global IR remain independent gates. Retained compiler, prime, row, complex and all-size hypotheses unchanged.'}
(HERE/'PRICE-RESULT.json').write_text(json.dumps(contract.portable(out),indent=2)+'\n');print('kappa',a['kappa_decimal'],'gain',out['gain_decimal'],'finite',bank['coefficient'])
