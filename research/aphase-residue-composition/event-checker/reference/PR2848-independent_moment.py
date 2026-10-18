# SPDX-License-Identifier: Apache-2.0
"""Independent exact interval arithmetic for the doubled-replica residue concentration.

No producer, inherited checker or numerical library is imported. For 1<=y<=2,
log(y)=2*sum_{j>=0} z^(2j+1)/(2j+1), z=(y-1)/(y+1). After100 terms the tail
is at most 2*z^201/(201*(1-z^2)). Binary range reduction and outward rational
rounding at10^-45 preserve inclusion. For0<=x<1, the Taylor sum through degree18
has positive remainder at most (x^18/18!)*x/19/(1-x/20). The geometric denominator
bounds all ratios after the first omitted term. All subsequent operations use
Fraction. The resulting finite intervals certify moment signs, not physical
realization or an unconditional multiplication theorem.
"""
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
from collections import Counter,defaultdict
import argparse,json,hashlib,gzip
SCALE=10**45

def need(c,m):
 if not c:raise ValueError(m)
def blob(pin,data):
 need(hashlib.sha256(data).hexdigest()==pin['sha256'],'source SHA256: '+pin['name'])
 need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==pin['git_blob'],'source Git blob: '+pin['name'])
def sources(package):
 pinfile=package/('SOURCE-PINS.json' if (package/'SOURCE-PINS.json').exists() else 'SOURCES.json')
 pins=json.loads(pinfile.read_bytes())['files'];raw={}
 for pin in pins:
  need(Path(pin['name']).name==pin['name'],'unsafe source name');data=(package/'sources'/pin['name']).read_bytes();blob(pin,data);raw[pin['name']]=data
 return pins,raw

def decode(data,compressed=False):return json.loads(gzip.decompress(data)if compressed else data)
@lru_cache(None)
def logarithm(x):
 need(x>=1,'log argument');k=0
 while x>=2:x/=2;k+=1
 def unit(y):
  z=(y-1)/(y+1);power=z;total=Q(0)
  for j in range(100):total+=power/(2*j+1);power*=z*z
  total*=2;tail=2*power/(201*(1-z*z))
  return total,total+tail
 lo,hi=unit(x);l2,h2=unit(Q(2));lo+=k*l2;hi+=k*h2
 return Q((lo*SCALE).__floor__(),SCALE),Q((hi*SCALE).__ceil__(),SCALE)
def exponential(x):
 need(0<=x<1,'exp argument');term=total=Q(1)
 for j in range(1,19):term*=x/j;total+=term
 tail=term*x/19/(1-x/20)
 return total,total+tail
def moment(profile,b,W):
 lo=hi=Q(0)
 for rank,count in profile.items():
  need(0<rank<73 and count>0,'child profile');l,h=logarithm(Q(73,rank));e0=exponential(b*l)[0];e1=exponential(b*h)[1]
  lo+=Q(count*rank,73*W)*e0;hi+=Q(count*rank,73*W)*e1
 return Q((lo*SCALE).__floor__(),SCALE),Q((hi*SCALE).__ceil__(),SCALE)
def old_profile(raw,prefix):
 providers=decode(raw['PR2833-PROVIDERS.json']);order=decode(raw[prefix+'-ORDER.json']);dispatch={(s,r):p for s,r,p in decode(raw[prefix+'-DISPATCH.json'])};fill=decode(raw[prefix+'-FILL.json.gz'],True);template=decode(raw['PR2833-T37-TEMPLATE.json.gz'],True)
 caps={e['child']:e['rank']for e in template['idle_children']};used=defaultdict(int)
 for t,h,r,c,p,z in fill['rows']:used[r,c,p]+=providers[dispatch[tuple(order[t])]]['widths'][h]
 out=Counter()
 replicas=1+max(r for s,r in order)
 need(len(order)==9*replicas and len({(s,r)for s,r in order})==len(order),'source calls')
 for r in range(replicas):
  for c,cap in caps.items():
   for p in range(112):
    idle=cap-used[r,c,p];need(idle>=0,'source capacity');
    if idle:out[idle]+=1
 for call in order:
  for r,n in providers[dispatch[tuple(call)]]['actual_paid_profile'].items():out[int(r)]+=n
 if prefix+'-PROFILE.json' in raw:need(dict(out)=={int(r):n for r,n in decode(raw[prefix+'-PROFILE.json']).items()},'source profile receipt')
 return dict(out),replicas
def run(package):
 pins,raw=sources(package);prefix='PR2843' if 'PR2843-FILL.json.gz' in raw else 'PR2833'
 p={int(r):n for r,n in decode((package/'PROFILE.json').read_bytes()).items()};old,T=old_profile(raw,prefix);W=2*T*896
 receipt=decode((package/'EXACT-MOMENT.json').read_bytes());mass=sum(r*n for r,n in p.items())
 diff={r:p.get(r,0)-2*old.get(r,0)for r in set(p)|set(old)};diff={r:n for r,n in diff.items()if n}
 need(diff=={2:1,9:-2,16:1},'profile delta');need(mass==2*sum(r*n for r,n in old.items())==W*73-320*2*T,'rank invariant')
 G=10**25;low=(Q(receipt['complex_lower'])*G).__floor__();high=(Q(receipt['complex_upper'])*G).__ceil__()
 need(moment(p,Q(low,G),W)[1]<1<moment(p,Q(high,G),W)[0],'initial bracket')
 while high-low>1:
  mid=(low+high)//2;l,u=moment(p,Q(mid,G),W)
  if u<1:low=mid
  elif l>1:high=mid
  else:raise ValueError('precision exhausted')
 priorfile='PR2843-CLAIM.json' if prefix=='PR2843' else 'PR2833-OUTER-CLAIM.json'
 prior=Q(decode(raw[priorfile])['kappa']);claim=Q(receipt['target'])
 need(prior<claim<Q(low,G),'strict claim gain and margin')
 oldlo,oldhi=moment(old,prior,W//2);newlo,newhi=moment(p,prior,W);need(newhi<oldlo,'strict moment dominance')
 # Independent elementary checkpoints and an intentionally overstated endpoint.
 need(logarithm(Q(1))==(0,0) and exponential(Q(0))==(1,1),'zero identities')
 l,u=logarithm(Q(2));need(Q('0.6931471805599453094172321214581765680755')<l<u<Q('0.6931471805599453094172321214581765680756'),'known log2 interval')
 l,u=exponential(Q(1,2));need(l<Q('1.6487212707001281468486507878141635716537')<Q('1.6487212707001281468486507878141635716538')<u,'known exp(1/2) interval')
 need(moment(p,Q(low,G)+Q(1,10**20),W)[0]>1,'overstated lower endpoint not rejected')
 pin=next(x for x in pins if x['name']=='PR2833-PROVIDERS.json')
 try:blob(pin,raw[pin['name']]+b'0')
 except ValueError:pass
 else:raise ValueError('mutated source accepted')
 return dict(status='PASS_INDEPENDENT_RATIONAL_DOUBLE_RESIDUE_MOMENT',baseline=prefix,replicas=2*T,profile_delta=diff,rank_mass=mass,live=W,lower=str(Q(low,G)),upper=str(Q(high,G)),prior_kappa_approx=float(prior),claim_approx=float(claim),strict_gain_lower=str(Q(low,G)-prior),normalized_moment_at_prior=[str(newlo),str(newhi)],normalized_moment_gain_at_prior=[str(oldlo-newhi),str(oldhi-newlo)],controls=['log1_exp0','known_log2_interval','known_exp_half_interval','overstated_lower_endpoint','source_byte_mutation'],scope='Independent rational arithmetic and source-derived profile identity only; native/global/outer proof obligations separate.',candidate_sha256={name:hashlib.sha256((package/name).read_bytes()).hexdigest()for name in ['PROFILE.json','EXACT-MOMENT.json']},source_sha256={pin['name']:pin['sha256']for pin in pins})
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--package',type=Path,default=Path(__file__).resolve().parent);a=ap.parse_args();print(json.dumps(run(a.package.resolve()),indent=2,sort_keys=True))
if __name__=='__main__':main()
