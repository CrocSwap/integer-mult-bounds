from pathlib import Path
import json,importlib.util,sys
from fractions import Fraction as Q
sys.set_int_max_str_digits(0)
R=Path(__file__).resolve().parent;O=R;ROOT=R.parents[1]
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def enc(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,dict):return {str(k):enc(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [enc(v) for v in x]
 return x
im=load('im',ROOT/'research/paired-cube-diagonal-bit-168/arithmetic/interval_moment.py')
assembly=load('asm',ROOT/'scripts/paired_cube_assembly.py')
p=json.loads((R/'geometry/packed-frames.json').read_text());base=json.loads((ROOT/'research/source-assisted-v4/certificate.json').read_text())
def profile(cp):
 H={int(t):n for t,n in cp['child_histogram'].items()}
 return dict(m=cp.get('m',72),W=cp['W_per_vertex'],child_multiplicities=H,N=cp['deficit_per_vertex'],L=0,total_rank=sum(t*n for t,n in H.items()),maxchild=max(H))
actual=json.loads((R/'complex-profile-replayed.json').read_text());assert all(actual[k]==base['complex_profile'][k] for k in ['m','W_per_vertex','rank_per_vertex','deficit_per_vertex','child_histogram']);cp=profile(actual);bp=profile(p['profile']['scaled_moment_profile'])
def paid(row,a,bit):
 x=im.moment(row,a)
 if bit:
  l,u=im.log_interval(Q(row['m']));e,f=im.exp_interval(a*l,a*u);w=Q(1,10**16)*Q(32*row['m']*sum(row['child_multiplicities'].values()),row['W']);x.update(lower=x['lower']+w*e,upper=x['upper']+w*f)
 return x
def certify(row,bit):
 den=10**18;lo=0;hi=den//100
 while hi-lo>1:
  md=(lo+hi)//2;v=paid(row,Q(md,den),bit)
  if v['upper']<1:lo=md
  elif v['lower']>1:hi=md
  else:raise ValueError('inconclusive')
 a=Q(lo,den);z=Q(hi,den);assert paid(row,a,bit)['upper']<1<paid(row,z,bit)['lower']
 return dict(saving=a,accepted=paid(row,a,bit),next_excluded=paid(row,z,bit))
c=certify(cp,False);b=certify(bp,True);assert b['saving']==Q(p['coarse']['coarse_saving'])
coarse=b['saving'];chain=[Q(p['coarse']['ordinary_saving'])]
for i in range(4):
 a=(1-coarse)*coarse+coarse*chain[-1];assert chain[-1]<a<coarse<1-a;chain.append(a)
bridge=base['assembly']['finite_bridge'];bridge['rows']['degree_gap']=Q(bridge['rows']['degree_gap'])
eta=beta=Q(1,10**24);weak=Q(1,10**30);a=min(chain[-1],(1-beta)*c['saving']-weak);q=a*(1-2*eta);ceiling=(1-eta)*q/(1+q);grid=10**18;scaled=ceiling*grid;k=Q((scaled.numerator-1)//scaled.denominator,grid)
z=assembly.assembly(a,c['saving'],bridge,k,eta=eta,beta=beta);assert len(z['strict_constraints'])==47 and all(v>0 for v in z['strict_constraints'].values())
try:assembly.assembly(a,c['saving'],bridge,k+Q(1,grid),eta=eta,beta=beta)
except AssertionError:pass
else:raise AssertionError('next k accepted')
out=dict(status='PASS_EXACT_47_CONSTRAINT_ASSEMBLY',scope='Conditional finite supplier certificate; retained all-size interfaces and analytic assumptions',bit_profile=bp,complex_profile=cp,bit=b,complex=c,ordinary_chain=chain,bit_ordinary=chain[-1],a_bit=a,a_complex=c['saving'],eta=eta,beta=beta,kappa=k,kappa_float=float(k),binding='bit',assembly=z,adjacent_kappa_rejected=True)
(O/'assembly.json').write_text(json.dumps(enc(out),indent=2,sort_keys=True)+'\n')
print(json.dumps(enc({k:out[k] for k in ['status','kappa','kappa_float','bit_ordinary','a_complex']}),indent=2))
