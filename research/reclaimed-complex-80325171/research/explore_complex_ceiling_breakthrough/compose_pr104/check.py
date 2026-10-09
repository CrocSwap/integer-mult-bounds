"""Original exact104-assembly preparation with the independently reviewed h24 component.
No upstream code is imported or executed. Mathematical formulas read from pinned assembly text.
"""
import sys,os
if sys.flags.optimize or os.environ.get('PYTHONOPTIMIZE'):raise RuntimeError('Optimized Python is not permitted')
from pathlib import Path
from fractions import Fraction as Q
from math import factorial
import json,hashlib,time,resource
root=Path(__file__).resolve().parent;research=root.parents[1];start=time.monotonic()
p104=research/'pr_watch_2316/PR104';own=root.parent/'pr97_port';review=research/'verify_complex_reclamation_ledger'
paths={'104':p104/'certificates/stopped-product-network.json','104_expected':p104/'certificates/stopped-product-input.json','old_leaf':research/'copied_centers_36/sources/certificates/copied-centers-network.json','new_component':own/'H24_ACCEPTANCE_FROZEN.json','new_word':own/'H24_WITNESS_MANIFEST.json','new_guard':own/'PRECISION_AND_ROWS.json','assembly_text':research/'pr_watch_2240/sources/scripts/structured_bulk_assembly.py','104_driver':p104/'scripts/stopped_product_network.py'}
sources={k:dict(path=str(p.relative_to(research.parent)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())for k,p in paths.items()}
pins=json.loads((root/'INPUT_PINS.json').read_text())
for name,record in sources.items():
 if record['sha256']!=pins[name]['sha256']:raise ValueError('Changed source pin: '+name)
old104=json.loads(paths['104'].read_text());old_leaf=json.loads(paths['old_leaf'].read_text());checked=json.loads(paths['new_component'].read_text());guard=json.loads(paths['new_guard'].read_text());newprofile=json.loads((own/'H24_WITNESS_STATS.json').read_text())['profile']
assert sources['assembly_text']['sha256']==old104['source_sha256']['scripts/structured_bulk_assembly.py']
assert sources['old_leaf']['sha256']==old104['source_sha256']['certificates/copied-centers-network.json']
assert checked['roles']==40011 and checked['source_relations_checked']==257250

# Independent exact elementary function enclosure: all arguments are positive fixed rationals.
logcache={}
def smalllog(x):
 z=(x-1)/(x+1);N=40;lo=2*sum((z**(2*j+1)/Q(2*j+1)for j in range(N)),Q(0));tail=2*z**(2*N+1)/(Q(2*N+1)*(1-z*z));return lo,lo+tail
ln2=smalllog(Q(2))
def logbound(x):
 if x in logcache:return logcache[x]
 k=0;y=x
 while y>=2:y/=2;k+=1
 lo,hi=smalllog(y);out=(k*ln2[0]+lo,k*ln2[1]+hi);logcache[x]=out;return out

def expbound(lo,hi):
 n=8;assert 0<=lo<=hi<1
 a=sum((lo**j/Q(factorial(j))for j in range(n+1)),Q(0));b=sum((hi**j/Q(factorial(j))for j in range(n+1)),Q(0));b+=hi**(n+1)/Q(factorial(n+1))/(1-hi/Q(n+2));return a,b

def moment(label,m,W,children,saving):
 rows={int(t):int(n)for t,n in children.items()};assert rows and all(0<t<m and n>0 for t,n in rows.items());lo=Q(0);hi=Q(0)
 for t,n in sorted(rows.items()):
  ll,lh=logbound(Q(m,t));a,b=expbound(saving*ll,saving*lh);weight=Q(n*t,m*W);lo+=weight*a;hi+=weight*b
 scale=1<<192
 lo=Q((lo*scale).numerator//(lo*scale).denominator,scale)
 u=hi*scale;hi=Q((u.numerator+u.denominator-1)//u.denominator,scale)
 assert hi<1,label
 return dict(label=label,m=m,W=W,saving=saving,rank=sum(t*n for t,n in rows.items()),lower=lo,upper=hi,strict_gap=1-hi,enclosure_grid_bits=192,log_terms=40,exponential_degree=8)
coarse=old104['bit']['counts'];old=old_leaf['bit']['counts'];alpha=Q(1,1000);a0=Q(4019,50000000);old_a=Q(384599,10**10);a=(1-alpha)*a0+alpha*old_a;b=Q(217021,2500000000)
assert a==Q(803380799,10**13)==Q(old104['bit']['stopped_adapter']['effective_saving'])
assert Q(old_leaf['bit']['saving'])==old_a
moments=[moment('unchanged104coarse',coarse['m'],coarse['W'],coarse['child_multiplicities'],a0),moment('unchangedordinaryleaf',old['m'],old['W'],old['child_multiplicities'],old_a),moment('newcheckedcomplex',576,newprofile['W'],newprofile['child_histogram'],b)]
assert moments[2]['rank']==newprofile['mass']==98008965648
assert a0>old_a>0 and alpha>a0 and alpha>a

# Fresh conservative semantic constants from the actual new literal scalar program.
m,W,s=576,170157680,98008965648;G=3205012096;rmax=552
assert (guard['global_scalar_group_upper'],newprofile['R'])==(G,40011)
E=64*(W+m+G+1)**3;charge=2*G*W*W+8*s+4*W+4+32*m;B=s+E;C0=32*m*B*B
assert charge<E and 2*B*(m-rmax)>=s+E and 2*B+18<C0
halving=lambda mm,rr:next(t for t in range(1,1000)if mm**t>2*rr**t)
coarse_depth=halving(coarse['m'],coarse['maxchild']);old_depth=halving(old['m'],old['maxchild']);complex_depth=halving(m,rmax)
rows=coarse_depth*coarse['W'].bit_length()+old_depth*old['W'].bit_length()+complex_depth*W.bit_length();rowgap=Q(4000)-Q(51,25)*rows
assert (coarse_depth,old_depth,complex_depth,rows)==(16,9,17,1176)and rowgap>0
bridge=dict(bit_coarse=old104['finite_bridge']['bit_coarse'],ordinary_leaf=dict(m=old['m'],W=old['W'],maxchild=old['maxchild'],halving_degree=old_depth,wire_bits=old['W'].bit_length()),complex=dict(m=m,W=W,s=s,N=4096576,R=40011,loss_per_axis=553,maxchild=rmax,halving_degree=complex_depth,wire_bits=W.bit_length(),scalar_group_upper=G),semantic=dict(E=E,literal_charge=charge,strict_literal_gap=E-charge,B=B,C0=C0,C1=1,induction_gap=2*B*(m-rmax)-s-E,scalar_field='Gaussian dyadic; mixer units±1,scatter denominators2; no21 grid needed'),rows=dict(coefficient=rows,degree=4000,suffix_slope=16000,degree_gap=rowgap,contract='W_complex^D_complex * W_coarse^D_coarse * W_old^D_old; one prefix/one padding'))

# Exact retained assembly formulas, written independently and never imported.
eta=Q(1,10**8);beta=Q(1,10**6);tau=1-a;sigma=1-b;q=a*(1-2*eta);c=q*(1+eta);eps=(1-eta)/(1+c+q);lp=1-q;lam=(tau+lp)/2;g=eps*q;rr=(g+1-eps)/2;delta=eta/8
internal=tau+(1-beta)*max(sigma-tau,Q(0));leaf=sigma+beta*(1-sigma)
grid=10**12;kappa=Q((g*grid).numerator//(g*grid).denominator,grid)
if kappa==g:kappa-=Q(1,grid)
margins=dict(original_prefix=1-eps*(1+c),coordinate_movement=a,compact_phase_layer=g,bulk_exposure=a,Gaussian_arithmetic=min(1-eps-delta,rr-delta),scalar_work=1-eps-delta,dimension=eps)
slacks=dict(bit_positive=a,complex_above_bit=b-a,complex_below_one_over32=Q(1,32)-b,beta_positive=beta,beta_below_one=1-beta,leaf_saving_above_bit=(1-beta)*b-a,q_positive=q,q_below_internal=1-internal-q,q_below_leaf=1-leaf-q,c_positive=c,c_below_one=1-c,q_below_reservations=c-q,lambda_above_tau=lam-tau,lambda_above_sigma=lam-sigma,lambda_above_internal=lam-internal,lambda_prime_above_lambda=lp-lam,compact_leaf=lp-leaf,compact_reservations=lp-(1-c),lambda_prime_below_one=q,epsilon_positive=eps,epsilon_below_one=1-eps,guard_width=1-eps,K_geometry=1-eps*(1+c),K_dominates_log=eps*c,record_suffix=1-eps,phase_local=1-eps-delta,phase_boundary=rr-delta,gamma_sublinear=1-eps-rr,cell_above_band=eps-(1-rr)/2,prime_interval_packing=1-eps,alpha_positive=rr,alpha_below_one=1-rr,alpha_below_one_fourth=Q(1,4)-rr,delta_positive=delta,delta_below_one_eighth=Q(1,8)-delta,short_record_fallback=eps-a,small_field_exposure=1-eps-g,artificial_boundary=8-eps+rr-delta-g,literal_scalar_guard=Q(E-charge),row_product_gap=rowgap)
slacks.update({name+'_above_kappa':v-kappa for name,v in margins.items()})
assert len(slacks)==47 and len(margins)==7 and all(v>0 for v in slacks.values());assert min(margins.values())==g and margins['original_prefix']-g==eta
next_kappa=kappa+Q(1,grid);assert g-next_kappa<=0
original_kappa=Q(old104['kappa'])
out=dict(status='Original exact arithmetic/compatibility preparation ONLY; stopped-product atom/tape review and distinct full-assembly review pending',source_head104='854ba7dca98651eab2050402384e1a7784534f0a',component_head97='f5f9c56e637463cac1e300d1589ccf42838f688a',sources=sources,kappa_candidate=kappa,kappa_original104=original_kappa,relative_gain=kappa/original_kappa-1,actual_bit_saving=a,complex_saving=b,moments=moments,finite_bridge=bridge,assembly=dict(parameters=dict(a_bit=a,a_complex=b,atom=alpha,eta=eta,beta=beta,tau=tau,sigma=sigma,q=q,c=c,epsilon=eps,lambda_=lam,lambda_prime=lp,alpha_squared_power=rr,delta=delta,C0=C0,C1=1,kappa=kappa),strict_constraints=slacks,margins=margins,minimum_margin=g,absorption_gap=g-kappa,recurrence=dict(internal=internal,leaf=leaf,reservations=1-c)),grid=grid,next_grid_point=next_kappa,next_grid_rejected_margin=g-next_kappa,scope='Not a new producer and not global theorem admission. In particular uniform O(V) ordered-affine atom passes, arbitrary-width stopped-bit transfer, common basis/prime, fixed tapes and analytic interfaces remain explicit dependencies.',seconds=time.monotonic()-start,rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
def js(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,dict):return {str(k):js(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [js(v)for v in x]
 return x
(root/'PREPARATION.json').write_text(json.dumps(js(out),indent=2)+'\n')
print(json.dumps(dict(kappa=str(kappa),decimal=float(kappa),relative_gain_percent=float(100*(kappa/original_kappa-1)),constraints=len(slacks),row_coefficient=rows,complex_W=W,scalar_G=G,seconds=out['seconds'],rss_KiB=out['rss_KiB']),indent=2))
