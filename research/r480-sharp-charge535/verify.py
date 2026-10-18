"""Reprice pinned PR510 with the explicit bad-class charge; compose with PR535.
No network, optimizer, floating admission, or unchanged operator replay.
Prepared for rohanarun with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
from decimal import Decimal,localcontext,ROUND_FLOOR
import argparse,json,hashlib,importlib.util,sys,time
if not __debug__:raise RuntimeError('Assertions must remain enabled')
R=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('out',type=Path);args=ap.parse_args();out=args.out.resolve();assert not out.exists() and not out.is_relative_to(R);out.mkdir();start=time.monotonic()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((R/'MANIFEST.json').read_text())
assert {p.relative_to(R).as_posix():sha(p)for p in R.rglob('*')if p.is_file()and p!=R/'MANIFEST.json'and '__pycache__'not in p.parts}==manifest
read=lambda p:json.loads((R/p).read_text())
def load(n):
 sp=importlib.util.spec_from_file_location('sharp_'+n,R/'engines'/(n+'.py'));m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
M,B,Outer=[load(n)for n in ['moment','base_two_moment','outer']]
e=read('EXPECTED.json');bit=read('inputs/PR510-EXPECTED.json')['nine'];complex_=read('inputs/PR535-EXPECTED.json');P={int(r):n for r,n in bit['profile'].items()};m=bit['m'];W=bit['bit']['live'];E=sum(P.values());N=2*m
assert (m,W,bit['stages'],bit['replicas'],bit['bit']['maxchild'])==(64,30720,9,32,8)
def check_profile(p):
 assert all(isinstance(r,int)and isinstance(n,int)and 0<r<m and n>0 for r,n in p.items())
 assert sum(r*n for r,n in p.items())==bit['bit']['rank_mass']
 assert m*W-sum(r*n for r,n in p.items())==9984
check_profile(P)
F=6*N*(N-1)+3*N+6*(N-1);delta=Q(2*m**3,2**80);factor=delta*F*E
assert F==e['fallback_per_edge'] and str(delta)==e['bad_fraction']
assert delta<Q(1,10**16) and F<32*m*m
c0=Q(bit['bit_lower']);b=Q(complex_['complex_lower']);CP={int(r):n for r,n in complex_['global_profile'].items()}
assert complex_['kappa']==e['old_kappa'] and complex_['bit_lower']==str(c0)
def rounded_bounds(p,m,w,c):
 lo,hi=M.moment(p,m,w,c,True);a,z=B.moment(m,w,list(p.items()),c);g,h=B.moment(m,w,[(1,32*m*m*sum(p.values()))],c);return lo,hi,a+g/10**16,z+h/10**16
for p,mm,ww,c in [(P,m,W,c0),(CP,73,complex_['live'],b)]:
 for a,accept in [(c,True),(c+Q(1,10**24),False)]:
  lo,hi,l,h=rounded_bounds(p,mm,ww,a);assert (hi<1 and h<1)if accept else(lo>1 and l>1)
def sharp_bounds(c):
 lo,hi=M.moment(P,m,W,c,False);fl,fh=M.moment({1:1},m,W,c,False);a,z=B.moment(m,W,list(P.items()),c);g,h=B.moment(m,W,[(1,1)],c);return lo+factor*fl,hi+factor*fh,a+factor*g,z+factor*h
with localcontext()as ctx:
 ctx.prec=90;terms=[(Decimal(r*n)/Decimal(m*W),(Decimal(m)/Decimal(r)).ln())for r,n in P.items()];fb=Decimal(factor.numerator)/Decimal(factor.denominator)/Decimal(m*W);lm=Decimal(m).ln();lo=Decimal(0);hi=Decimal('.003')
 for _ in range(250):
  a=(lo+hi)/2
  if sum(p*(a*l).exp()for p,l in terms)+fb*(a*lm).exp()<1:lo=a
  else:hi=a
 c=Q(int((lo*Decimal(10**24)).to_integral_value(rounding=ROUND_FLOOR)),10**24)
assert c==Q(e['bit_lower']) and c0<c<b
checks=[]
for a,accept in [(c,True),(c+Q(1,10**24),False)]:
 lo,hi,l,h=sharp_bounds(a);assert (hi<1 and h<1)if accept else(lo>1 and l>1);checks.append(dict(endpoint=str(a),accept=accept,mercator=[str(lo-1),str(hi-1)],base_two=[str(l-1),str(h-1)]))
# Reproduce the baseline assembly, then change only the bit endpoint.
eta=beta=Q(1,10**18);grid=Q(1,10**18);bridge={'semantic':{'C0':{'base':2,'exponent':210000},'strict_literal_gap':1},'rows':{'degree_gap':Q(10**6)-Q(51*20161,25)}}
def assemble(bit_c):
 s=min(bit_c,(1-beta)*b)-Q(1,10**24);assert 0<s<bit_c and s<(1-beta)*b;chain=[Q(384599,10**10)];cuts=[]
 for _ in range(6):
  old=chain[-1];a=(1-s)*s+s*old;gap=min(s-a,1-a-s,1-a-s*(1-old),1-s);assert old<a<s<1-a and gap>0
  ceil=lambda x:-(-x.numerator//x.denominator)
  cut=max(ceil(36/gap**2),ceil(2*(4+bit['bit']['charged_two_level_coefficient_bits'])/gap));assert cut*gap**2>=36 and cut*gap>=2*(4+bit['bit']['charged_two_level_coefficient_bits']);cuts.append(dict(gap=str(gap),cutoff_log2=str(cut)));chain.append(a)
 q=chain[-1]*(1-2*eta);margin=(1-eta)*q/(1+q);ticks=margin/grid;k=grid*((ticks.numerator-1)//ticks.denominator);a=Outer.assembly(chain[-1],b,bridge,k,eta=eta,beta=beta);assert len(a['strict_constraints'])==47 and all(v>0 for v in a['strict_constraints'].values());return k,chain,cuts,a
old,_,_,_=assemble(c0);assert old==Q(e['old_kappa'])
k,chain,cuts,a=assemble(c);assert k==Q(e['kappa']) and k>old
controls=[]
for name,kk,et,bt in [('next_grid',k+grid,eta,beta),('zero_eta',k,Q(0),beta),('zero_beta',k,eta,Q(0)),('unit_beta',k,eta,Q(1))]:
 try:Outer.assembly(chain[-1],b,bridge,kk,eta=et,beta=bt)
 except AssertionError:controls.append(name)
 else:raise AssertionError(name)
mut=dict(P);mut[1]+=1
try:check_profile(mut)
except AssertionError:controls.append('tampered_bit_histogram')
else:raise AssertionError('tampered_bit_histogram')
# The new endpoint must fail under the old rounded charge, establishing that this is the actual source of gain.
lo,hi,bl,bh=rounded_bounds(P,m,W,c);assert lo>1 and bl>1;controls.append('new_endpoint_rejected_by_old_charge')
res=dict(status='PASS_LITERAL_BIT_CHARGE_AND_CONDITIONAL_COMPOSITION',kappa=str(k),kappa_decimal=e['kappa_decimal'],old_kappa=str(old),absolute_gain=str(k-old),relative_gain=str(k/old-1),bit_lower=str(c),bit_decimal=e['bit_decimal'],old_bit_lower=str(c0),complex_lower=str(b),binding_component='bit',bad_fraction=str(delta),fallback_per_bad_edge=F,sharp_rank_one_mass=str(factor),old_rank_one_mass=str(Q(32*m*m*E,10**16)),moment_receipts=checks,strict_outer_constraints={n:str(v)for n,v in a['strict_constraints'].items()},bootstrap=cuts,controls=controls,seconds=time.monotonic()-start,python=sys.version,manifest_sha256=sha(R/'MANIFEST.json'),scope='Arithmetic repricing only. PR510 bit and PR535 complex operators unchanged and cited, not rebuilt. Conditional portability of the source bad-class theorem and all inherited all-size/compiler/realization/hosting/precision/tape/analytic assumptions remain.')
(out/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print(res['status'],e['kappa_decimal'],flush=True)
