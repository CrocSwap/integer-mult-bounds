"""Prospective exact price of sliced/minimum-frame R480 with unchanged PR510 hosting.
Not physical admission; finite invoice and owner-template replay remain pending.
"""
from pathlib import Path
from fractions import Fraction as Q
from decimal import Decimal,localcontext
from collections import Counter
import json,importlib.util
R=Path(__file__).resolve().parent;O=R/'trace541-frozen-minimum-price';O.mkdir(exist_ok=False);p=R/'r480-sharp535-publication/research/r480-sharp-charge535'
def load(n):
 s=importlib.util.spec_from_file_location(n,p/'engines'/(n+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M,B,Outer=[load(x)for x in ['moment','base_two_moment','outer']]
x=json.loads((p/'inputs/PR510-EXPECTED.json').read_text())['nine'];loc=json.loads((R/'trace541-frozen-minimum/PROFILE.json').read_text());old={int(k):v for k,v in json.loads((R/'bit510-sliced-minimal-frames/RESULT.json').read_text())['baseline_chain_profile'].items()};new={int(k):v for k,v in loc['new_chain_profile'].items()};H=Counter({int(k):v for k,v in x['profile'].items()})
for r,n in old.items():H[r]-=288*n
for r,n in new.items():H[r]+=288*n
H=+H;m=x['m'];W=x['bit']['live'];assert sum(r*n for r,n in H.items())==x['bit']['rank_mass'];factor=Q(1,2**61)*98682*sum(H.values())
def bounds(c):
 a,z=M.moment(H,m,W,c,False);g,h=M.moment({1:1},m,W,c,False);b,y=B.moment(m,W,list(H.items()),c);j,k=B.moment(m,W,[(1,1)],c);return a+factor*g,z+factor*h,b+factor*j,y+factor*k
with localcontext()as ctx:
 ctx.prec=90;term=[(Decimal(r*n)/Decimal(m*W),(Decimal(m)/Decimal(r)).ln())for r,n in H.items()];fb=Decimal(factor.numerator)/Decimal(factor.denominator)/Decimal(m*W);lm=Decimal(m).ln();lo=Decimal(0);hi=Decimal('.003')
 for _ in range(230):
  c=(lo+hi)/2
  if sum(p*(c*l).exp()for p,l in term)+fb*(c*lm).exp()<1:lo=c
  else:hi=c
 c=Q(int(lo*10**24),10**24)
checks=[]
for a,accept in [(c,True),(c+Q(1,10**24),False)]:
 l,h,ll,hh=bounds(a);assert (h<1 and hh<1)if accept else(l>1 and ll>1);checks.append(dict(endpoint=str(a),accept=accept,mercator=[str(l-1),str(h-1)],base_two=[str(ll-1),str(hh-1)]))
b=Q(json.loads((p/'inputs/PR535-EXPECTED.json').read_text())['complex_lower']);eta=beta=Q(1,10**18);s=min(c,(1-beta)*b)-Q(1,10**24);chain=[Q(384599,10**10)]
for _ in range(6):chain.append((1-s)*s+s*chain[-1])
q=chain[-1]*(1-2*eta);margin=(1-eta)*q/(1+q);ticks=margin*10**18;k=Q((ticks.numerator-1)//ticks.denominator,10**18)
bridge={'semantic':{'C0':{'base':2,'exponent':210000},'strict_literal_gap':1},'rows':{'degree_gap':Q(10**6)-Q(51*20161,25)}};assembly=Outer.assembly(chain[-1],b,bridge,k,eta=eta,beta=beta);assert len(assembly['strict_constraints'])==47 and all(a>0 for a in assembly['strict_constraints'].values())
def dec(a):
 with localcontext()as ctx:ctx.prec=60;return str(Decimal(a.numerator)/Decimal(a.denominator))
oldk=Q(json.loads((p/'EXPECTED.json').read_text())['kappa']);out=dict(status='PASS_PROSPECTIVE_EXACT_PRICE_PHYSICAL_ADMISSION_PENDING',profile=dict(sorted(H.items())),local_chain_profile=new,bit_lower=str(c),bit_decimal=dec(c),complex_lower=str(b),kappa=str(k),kappa_decimal=dec(k),relative_gain_percent=dec(100*(k-oldk)/oldk),binding='bit'if c<(1-beta)*b else'complex',moment_checks=checks,outer={n:str(z)for n,z in assembly['strict_constraints'].items()},scope='Derived global histogram adds288 copies of exact local profile delta to pinned PR510 profile. Same480 width8 helpers and original owner schedule proposed. Physical template, chronological finite invoice and changed-frame geometric checks remain required; old outer finite constants used prospectively.')
(O/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print({k:v for k,v in out.items()if k not in ['moment_checks','outer']},flush=True)
