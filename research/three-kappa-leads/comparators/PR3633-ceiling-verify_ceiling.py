"""Solver-free exact primal/dual comparison for a declared fixed packing model."""
import argparse,json,hashlib,math
from fractions import Fraction as F
from collections import Counter,defaultdict
from pathlib import Path

from functools import lru_cache
D=10**60
def round_bounds(lo,hi):
 return F((lo*D).__floor__(),D),F((hi*D).__ceil__(),D)
@lru_cache(None)
def log_unit(q):
 z=(q-1)/(q+1);z2=z*z;power=z;total=F(0);n=0
 while True:
  total+=2*power/(2*n+1);n+=1;power*=z2
  tail=2*power/((2*n+1)*(1-z2))
  if tail<F(1,D):return round_bounds(total,total+tail)
@lru_cache(None)
def log_rank(r):
 k=r.bit_length()-1;u=F(r,2**k);a,b=log_unit(F(2));c,d=log_unit(u)
 return round_bounds(k*a+c,k*b+d)
def exp_negative(t):
 if not 0<=t<1:raise ValueError('exponent outside alternating-series bound')
 total=F(1);term=F(1);odd=None
 for n in range(1,81):
  term*=(-t)/n;total+=term
  if n%2:odd=total
  elif abs(term)<F(1,D):return round_bounds(odd,total)
 raise ValueError('series did not reach bound')
def interval(delta,a):
 a=F(a)
 if not 0<a<F(1,10):raise ValueError('expected small positive exact exponent')
 lower=upper=F(0)
 for r,c in delta.items():
  r=int(r)
  if type(c)is not int or r<=0:raise ValueError('integer signed rank counts required')
  lo,hi=log_rank(r);elo=exp_negative(a*hi)[0];ehi=exp_negative(a*lo)[1]
  low,high=r*elo,r*ehi
  lower+=c*(low if c>=0 else high);upper+=c*(high if c>=0 else low)
 return {'a':str(a),'lower':str(lower),'upper':str(upper),'decision':'strict_decrease'if upper<0 else 'strict_increase'if lower>0 else 'undetermined_or_zero','scope':'exact finite sum delta[n_r]*r^(1-a); no hosting/native/outer or kappa claim'}

def verify(candidate,certificate):
 d=json.loads(Path(candidate).read_text());c=json.loads(Path(certificate).read_text());T=d['baseT']*d['S'];W=d['widths'];caps=sorted({g[0]for g in d['groups']});a=F(c['exponent'])
 fields=['baseT','S','order','dispatch','groups','widths','inventory','local_profile','x','z','profile']
 if c['candidate_scientific_fields']!=fields:raise ValueError('scientific projection fields')
 canonical=json.dumps({k:d[k]for k in fields},sort_keys=True,separators=(',',':')).encode()
 if hashlib.sha256(canonical).hexdigest()!=c['candidate_scientific_sha256']:raise ValueError('candidate payload binding')
 if W!=c['widths'] or caps!=c['capacities'] or d['inventory']!=c['inventory'] or d['local_profile']!=c['local_profile']:raise ValueError('supplier/capacity model')
 if c['exponent']!=c['root_interval'][1]:raise ValueError('root-upper exponent binding')
 if len(d['order'])!=9*d['baseT']:raise ValueError('nine-call normalization')
 counts=Counter()
 for cap,l,h,n in d['groups']:counts[cap]+=n*d['S']
 rhs=[F(counts[cap],T)for cap in caps]+[9*F(d['inventory'][str(w)])for w in W]
 if rhs!=list(map(F,c['rhs_per_replica'])):raise ValueError('model RHS mismatch')
 dual=[{int(k):F(v)for k,v in row.items()}for row in c['dual_by_constraint']]
 if len(dual)!=len(rhs):raise ValueError('dual dimension')
 def column(cap,q):return [int(cap==cc)for cc in caps]+list(q)
 def rc(cap,q):
  idle=cap-sum(w*n for w,n in zip(W,q));co=defaultdict(F)
  if idle:co[idle]+=1
  for n,row in zip(column(cap,q),dual):
   for k,v in row.items():co[k]-=n*v
  return {k:v for k,v in co.items()if v}
 patterns=[]
 def walk(cap,i,left,q):
  if i==len(W):patterns.append((cap,tuple(q)));return
  for n in range(left//W[i]+1):walk(cap,i+1,left-n*W[i],q+[n])
 for cap in caps:walk(cap,0,cap,[])
 cache={};tight=0;lower=[]
 for cap,q in patterns:
  co=rc(cap,q)
  if not co:tight+=1;continue
  scale=math.lcm(*(v.denominator for v in co.values()));key=tuple(sorted((k,int(v*scale))for k,v in co.items()))
  if key not in cache:cache[key]=interval(dict(key),a)
  low=F(cache[key]['lower'])/scale
  if low<=0:raise ValueError('dual inequality not certified')
  lower.append(low)
 primal=Counter();primal_idle=defaultdict(F)
 for b in c['basis']:
  q=b['counts'];cap=b['capacity'];n=F(b['amount_per_replica'])
  if n<0 or (cap,tuple(q))not in patterns:raise ValueError('invalid primal pattern')
  for i,v in enumerate(column(cap,q)):primal[i]+=n*v
  idle=cap-sum(w*k for w,k in zip(W,q))
  if idle!=b['idle'] or rc(cap,q):raise ValueError('basis not tight')
  if idle:primal_idle[idle]+=n
 if [primal[i]for i in range(len(rhs))]!=rhs:raise ValueError('primal constraints')
 actual_bins=Counter();actual_widths=Counter();actual_idle=Counter()
 for g,q,n in d['x']:
  if type(n)is not int or n<=0 or len(q)!=len(W) or any(type(v)is not int or v<0 for v in q):raise ValueError('integer candidate pattern')
  cap=d['groups'][g][0];idle=cap-sum(w*v for w,v in zip(W,q))
  if idle<0:raise ValueError('candidate capacity')
  actual_bins[g]+=n
  for w,v in zip(W,q):actual_widths[w]+=n*v
  if idle:actual_idle[idle]+=n
  if rc(d['groups'][g][0],q):raise ValueError('candidate uses non-tight pattern')
 if any(actual_bins[g]!=row[3]*d['S'] for g,row in enumerate(d['groups'])):raise ValueError('candidate bin counts')
 if any(actual_widths[w]!=9*T*d['inventory'][str(w)]for w in W):raise ValueError('candidate width inventory')
 rebuilt=Counter({int(k):9*T*v for k,v in d['local_profile'].items()});rebuilt.update(actual_idle)
 if dict(rebuilt)!={int(k):v for k,v in d['profile'].items()}:raise ValueError('candidate paid profile')
 expected=defaultdict(F,{int(k):9*F(v)for k,v in d['local_profile'].items()})
 for k,v in primal_idle.items():expected[k]+=v
 actual={int(k):F(v,T)for k,v in d['profile'].items()}
 if dict(expected)!=actual:raise ValueError('candidate/profile ceiling mismatch')
 rootpoly={int(k):int(v)for k,v in c['scaled_root_profile'].items()}
 if rootpoly!={**{k:int(v*4)for k,v in actual.items()},73:-3584}:raise ValueError('root polynomial model')
 low=interval(rootpoly,F(c['root_interval'][0]));high=interval(rootpoly,F(c['root_interval'][1]))
 if F(low['upper'])>=0 or F(high['lower'])<=0:raise ValueError('root signs')
 return {'status':'PASS_EXACT_ATTAINED_FIXED_MODEL_CEILING','patterns':len(patterns),'tight':tight,'strict':len(patterns)-tight,'minimum_strict_reduced_cost':str(min(lower)),'rhs_per_replica':list(map(str,rhs)),'profile_per_replica':{str(k):str(v)for k,v in actual.items()},'exponent':str(a),'replicas':T,'pins':{str(Path(p).resolve()):hashlib.sha256(Path(p).read_bytes()).hexdigest()for p in[candidate,certificate,__file__]},'root_interval':c['root_interval'],'root_signs':[low['decision'],high['decision']],'scope':'All nonnegative packing patterns for these six widths/four capacities, fixed supplier and nine-call normalization. Exact fractional optimum at stated exponent, attained by candidate aggregate. Source-clock provenance, literal realization, full native admission, changed suppliers and other geometries are separate.'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('candidate');p.add_argument('certificate');p.add_argument('--out',required=True);a=p.parse_args();r=verify(a.candidate,a.certificate);Path(a.out).write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['patterns'],r['tight'])
