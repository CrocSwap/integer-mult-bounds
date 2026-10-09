"""Publication review: independent interval, parameter and guard arithmetic.
Reads frozen inputs; writes only its own receipt. No other checker imported.
"""
from pathlib import Path
from fractions import Fraction as F
from math import factorial
from collections import Counter
import json, hashlib
P=Path(__file__).parent
read=lambda name:json.loads((P/name).read_text())
j=read('round8-optimize-reuse117-mrp.json');r=j['results'][0]
for name,digest in (j['construction_audit_sha256'] | j['source_sha256']).items():
 assert hashlib.sha256((P/name).read_bytes()).hexdigest()==digest,name
row=read('pr117-public/tree/certificates/deferred-product-complex-input.json')
groups=read('pr-network-mrp24-signed.json')['groups']
h,v,R=24,2024,row['R'];N=v*v;W=2*N+2*len(groups)*R;m=h*h
H=row['histogram'][:];H[1]+=h;H[h]-=h
hist=Counter({529:2*N,23:4*N,1:N})
for g in groups:
 if len(g)<h:hist[m-h*len(g)]+=2*R
for t,n in enumerate(H):
 if t and n:hist[t]+=2*v*n
assert dict(hist)=={int(t):n for t,n in r['profile']['child_multiplicities'].items()}
s=sum(t*n for t,n in hist.items());assert W*m-s==1862080

def logbounds(x):
 k=0
 while x>=2:x/=2;k+=1
 def part(y):
  z=(y-1)/(y+1);lo=2*sum((z**(2*i+1)/F(2*i+1) for i in range(64)),F(0))
  return lo,lo+2*z**129/(129*(1-z*z))
 lo,hi=part(x);a,b=part(F(2));lo+=k*a;hi+=k*b;grid=10**45
 return F(lo.numerator*grid//lo.denominator,grid),F(-(-hi.numerator*grid//hi.denominator),grid)
def expbounds(x):
 assert 0<=x<1
 lo=sum((x**i/F(factorial(i)) for i in range(13)),F(0))
 return lo,lo+x**13/F(factorial(13))/(1-x/14)
def moments(dim,roles,hh,a):
 lower=upper=F(0)
 for t,n in hh.items():
  lo,hi=logbounds(F(dim,t));weight=F(t*n,dim*roles)
  lower+=weight*expbounds(a*lo)[0];upper+=weight*expbounds(a*hi)[1]
 return lower,upper
op=read('round8-network-opposite-profile.json');bh={int(t):n for t,n in op['hist'].items()}
checks={}
for label,dim,roles,hh,saving in [('complex',m,W,hist,F(r['complex_moment']['saving'])),
 ('bit',op['m'],op['W'],bh,F(j['opposite_coarse']['saving']))]:
 lo,hi=moments(dim,roles,hh,saving);nextlo,nexthi=moments(dim,roles,hh,saving+F(1,10**22))
 assert hi<1<nextlo
 checks[label]=dict(gap=str(1-hi),next_excess=str(nextlo-1))
theta=F(1,1000);ordinary=F(384599,10**10)
effective=(1-theta)*F(j['opposite_coarse']['saving'])+theta*ordinary
assert effective==F(j['actual_stopped_bit']) and theta>effective>ordinary
b=F(r['complex_moment']['saving']);beta=F(1,10**6);a=min(effective,(1-beta)*b-F(1,10**10))
eta=F(1,10**16);q=a*(1-2*eta);c=q*(1+eta);eps=(1-eta)/(1+c+q)
g=eps*q;alpha=(g+1-eps)/2;delta=eta/8;kappa=F(r['assemblies'][-1]['kappa'])
margins=[1-eps*(1+c),a,g,a,min(1-eps-delta,alpha-delta),1-eps-delta,eps]
assert min(margins)==g and g>kappa and g<kappa+F(1,10**17)
assert margins[0]-g==eta and eps+alpha<1 and (1-beta)*b>a
assert a==F(r['assembly_bit'])
for key,value in r['assemblies'][-1]['certificate']['strict_constraints'].items():assert F(value)>0,key
G=N+2*v*(4*(row['c']+v)+10*v+4*h*v+4*h*h+8*h+8+2*h)
assert G==2401613632
public=read('pr117-public/tree/certificates/deferred-product-network.json')
sm=r['bridge']['semantic'];oldW=2*N+2*v*R;olds=oldW*m-N+2*v*552
E=64*(oldW+m+G+1)**3;B=olds+E;C0=32*m*B*B
assert (E,B,C0)==tuple(sm[key] for key in ['E','B','C0'])
charge=2*G*W*W+8*s+4*W+4+32*m
assert E>charge and 2*B*(m-529)>s+E
for dim,largest,degree in [(529,528,367),(576,529,9)]:
 assert dim**degree>2*largest**degree
 assert dim**(degree-1)<=2*largest**(degree-1)
coefficient=367*op['W'].bit_length()+9*W.bit_length()+252
stockgap=22000-F(51,25)*coefficient
assert coefficient==10377 and stockgap==F(20773,25)
assert C0>2*B+18+5*G*(9+1)
out=dict(status='PASS independent arithmetic for PR117 plus MRP87; physical interface and signed complement proof remain separate',
 kappa=str(kappa),complex_roles=W,complex_rank=s,G=G,stock_coefficient=coefficient,
 stock_gap=str(stockgap),literal_guard_gap=E-charge,induction_gap=2*B*(m-529)-s-E,
 intervals=checks,scope='All certificate-bound input hashes verified; different64-term log and degree12 exponential enclosures; full47 receipt positive, seven savings independently reconstructed')
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print({key:value for key,value in out.items() if key!='intervals'})
