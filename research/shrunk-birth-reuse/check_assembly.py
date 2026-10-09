"""Exact assembly for paid birth-read slot reuse on shrunk/saturated frames (PR124 checker, PR125 frames)."""
import sys,os,gzip
if sys.flags.optimize or os.environ.get('PYTHONOPTIMIZE'):raise RuntimeError('Assertions required')
from pathlib import Path
from fractions import Fraction as Q
from math import factorial
import json,hashlib,time,resource
root=Path(__file__).resolve().parent;repo=Path(os.environ.get('BIRTH_REPO',root.parents[1]));start=time.monotonic()
profile=json.loads(gzip.decompress((root/'BIRTH_MATCHES.json.gz').read_bytes()));bill=json.loads((root/'READOUT_COST.json').read_text())
source=repo/'research/shrunk-frames/certificate.json'
oldpath=repo/'certificates/copied-centers-network.json'
cert=json.loads(source.read_text());old_leaf=json.loads(oldpath.read_text())
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


coarse=cert['bit_profile'];old=old_leaf['bit']['counts'];alpha=Q(1,1000);a0=Q(620523,5000000000);old_a=Q(384599,10**10)
aactual=(1-alpha)*a0+alpha*old_a;b=Q(11242073,10**11);beta=Q(1,10**6);buffer=Q(1,10**12);a=min(aactual,(1-beta)*b-buffer)
assert aactual==Q(1240189553,10**13)==Q(cert['actual_bit_saving'])and aactual>a>0
moments=[moment('coarse_bit',529,coarse['W'],coarse['child_multiplicities'],a0),moment('old_ordinary',old['m'],old['W'],old['child_multiplicities'],old_a),moment('birth_reused_complex',576,profile['W'],profile['child_histogram'],b)]
m,W,s,rmax,R=576,profile['W'],profile['rank'],max(map(int,profile['child_histogram'])),profile['R'];G=bill['global_scalar_group_upper']
assert (W,s,R,rmax)==(115857808,66732235328,26597,574)
try:moment('next_complex',576,W,profile['child_histogram'],b+Q(1,10**11));raise RuntimeError('next complex grid point accepted')
except AssertionError:pass
E=64*(W+m+G+1)**3;charge=2*G*W*W+8*s+4*W+4+32*m;B=s+E;C0=32*m*B*B
assert charge<E and 2*B*(m-rmax)>=s+E and 2*B+18<C0
halving=lambda m,r:next(t for t in range(1,1000)if m**t>2*r**t)
stock=[dict(m=mm,W=ww,maxchild=rr,depth=halving(mm,rr),wire_bits=ww.bit_length())for mm,ww,rr in [(529,coarse['W'],528),(575,old['W'],529),(576,W,rmax)]]
rows=sum(x['depth']*x['wire_bits']for x in stock);rowgap=Q(32000)-Q(51,25)*rows
assert rows==15561 and rowgap==Q(6389,25)
bridge=dict(m=m,W=W,rank=s,R=R,maxchild=rmax,G=G,E=E,literal_charge=charge,B=B,C0=C0,C1=1,stock=stock,rows=rows,row_degree=32000,row_gap=rowgap,suffix_slope=128000,odd_grid='2^-P21^-K; K=G*(D_complex+1), with completed child preserving incoming odd exponent')
# Exact retained assembly formulas, written independently and never imported.
eta=Q(1,10**8);beta=Q(1,10**6);tau=1-a;sigma=1-b;q=a*(1-2*eta);c=q*(1+eta);eps=(1-eta)/(1+c+q);lp=1-q;lam=(tau+lp)/2;g=eps*q;rr=(g+1-eps)/2;delta=eta/8
internal=tau+(1-beta)*max(sigma-tau,Q(0));leaf=sigma+beta*(1-sigma)
grid=10**17;kappa=Q((g*grid).numerator//(g*grid).denominator,grid)
if kappa==g:kappa-=Q(1,grid)
margins=dict(original_prefix=1-eps*(1+c),coordinate_movement=a,compact_phase_layer=g,bulk_exposure=a,Gaussian_arithmetic=min(1-eps-delta,rr-delta),scalar_work=1-eps-delta,dimension=eps)
slacks=dict(bit_positive=a,complex_above_bit=b-a,complex_below_one_over32=Q(1,32)-b,beta_positive=beta,beta_below_one=1-beta,leaf_saving_above_bit=(1-beta)*b-a,q_positive=q,q_below_internal=1-internal-q,q_below_leaf=1-leaf-q,c_positive=c,c_below_one=1-c,q_below_reservations=c-q,lambda_above_tau=lam-tau,lambda_above_sigma=lam-sigma,lambda_above_internal=lam-internal,lambda_prime_above_lambda=lp-lam,compact_leaf=lp-leaf,compact_reservations=lp-(1-c),lambda_prime_below_one=q,epsilon_positive=eps,epsilon_below_one=1-eps,guard_width=1-eps,K_geometry=1-eps*(1+c),K_dominates_log=eps*c,record_suffix=1-eps,phase_local=1-eps-delta,phase_boundary=rr-delta,gamma_sublinear=1-eps-rr,cell_above_band=eps-(1-rr)/2,prime_interval_packing=1-eps,alpha_positive=rr,alpha_below_one=1-rr,alpha_below_one_fourth=Q(1,4)-rr,delta_positive=delta,delta_below_one_eighth=Q(1,8)-delta,short_record_fallback=eps-a,small_field_exposure=1-eps-g,artificial_boundary=8-eps+rr-delta-g,literal_scalar_guard=Q(E-charge),row_product_gap=rowgap)
slacks.update({name+'_above_kappa':v-kappa for name,v in margins.items()})
assert len(slacks)==47 and len(margins)==7 and all(v>0 for v in slacks.values());assert min(margins.values())==g and margins['original_prefix']-g==eta
next_kappa=kappa+Q(1,grid);assert g-next_kappa<=0


inputfiles=[root/'BIRTH_MATCHES.json.gz',root/'READOUT_COST.json',source,oldpath]
pins={('new/'+p.name)if p.parent==root else('base/'+str(p.relative_to(repo))):hashlib.sha256(p.read_bytes()).hexdigest()for p in inputfiles}
out=dict(status='AUTHOR_CHECKED_CONDITIONAL_ASSEMBLY; independent review pending',source_head='PR125 research/shrunk-frames (dda535b) with PR124 f367828 birth-read reuse',profile_source_head='research/shrunk-frames/complex-profile.json',pins=pins,kappa=kappa,complex_saving=b,actual_bit_saving=aactual,supported_bit_parameter=a,moments=moments,finite_bridge=bridge,assembly=dict(parameters=dict(a=a,b=b,beta=beta,eta=eta,q=q,c=c,epsilon=eps,lambda_=lam,lambda_prime=lp,r=rr,delta=delta,C0=C0,C1=1),constraints=slacks,margins=margins,minimum_margin=g,absorption_gap=g-kappa),next_grid=next_kappa,next_grid_gap=g-next_kappa)
def js(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,dict):return {str(k):js(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [js(v)for v in x]
 return x
(root/'CANDIDATE.json').write_text(json.dumps(js(out),indent=2)+'\n');print(json.dumps(dict(kappa=str(kappa),decimal=float(kappa),complex_saving=str(b),G=G,W=W,R=R,constraints=len(slacks),margins=len(margins),seconds=time.monotonic()-start),indent=2))
