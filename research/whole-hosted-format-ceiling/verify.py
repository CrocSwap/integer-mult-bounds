"""Exact controls for the written uniform moment ceiling. No floating point."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import gzip,hashlib,json
assert __debug__
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
actual={f.relative_to(ROOT).as_posix():sha(f) for f in ROOT.rglob('*') if f.is_file() and '__pycache__' not in f.parts and f.name!='MANIFEST.json'}
assert actual==json.loads((ROOT/'MANIFEST.json').read_text())
for name,h in json.loads((ROOT/'SOURCE.json').read_text())['files'].items():assert sha(ROOT/name)==h,name
pkg=ROOT.parent/'e8-complex-adapted-kernel'
w=json.loads(gzip.decompress((pkg/'data/word.json.gz').read_bytes()));sel=json.loads((pkg/'data/hosting.json').read_text())['selected'];e=json.loads((pkg/'EXPECTED.json').read_text())
P=Counter({int(r):n*88 for r,n in w['report']['local_profile'].items()});ranks=[16,8,32,8,48,8,64,8,64,48,32,16]
for z in sel:
 rem=ranks[z['idle']]-sum(w for s,w in z['pattern']);assert rem>=0
 if rem:P[rem]+=z['copies']*8
profiles={'bit':(78,9600,56,{int(r):n for r,n in e['bit_profile'].items()}),'complex':(89,9600,64,P)}
examples={}
for name,(m,W,rmax,p) in profiles.items():
 assert min(p)>=1 and max(p)==rmax<m and all(n>0 for n in p.values())
 D=Q(m*W-sum(r*n for r,n in p.items()),W);assert D==Q(17,50)
 u=1-D/m;good=[n for n in range(1,300) if u.numerator**n*m>u.denominator**n*rmax];N=max(good)
 assert N=={'bit':75,'complex':86}[name]
 assert u.numerator**(N+1)*m<=u.denominator**(N+1)*rmax
 examples[name]=dict(D=str(D),m=m,maxchild=rmax,supplier_upper=str(Q(1,N)),outer_upper=str(Q(1,N+1)),next_reciprocal_control_rejected=N+1)
# Exact rational weighted-AMGM comparisons across the declared stage family.
for K in range(2,129):
 D=Q(2,5)-Q(3,10*K);assert 0<D<Q(2,5)
 for h in (8,9):
  m=h+2*K*(h-1);rmax=2*(K-1)*(h-1);g=m-rmax;assert g==3*h-2
  theta=D/g;a,b=theta.numerator,theta.denominator;u=1-D/m
  assert u.numerator**b*m**a>u.denominator**b*rmax**a
  if h==9:assert theta<Q(2,125) and theta/(1+theta)<Q(2,127)
# D=g is the equality boundary and cannot justify a strict upper certificate.
m,g=89,25;D=Q(g);u=1-D/m;assert u*m==m-g
result=dict(status='PASS_SCOPED_WHOLE_HOSTED_FORMAT_CEILING',uniform_complex_supplier_upper='2/125',uniform_balanced_outer_upper='2/127',eleven_stage_balanced_outer_upper='1/87',examples=examples,exact_stage_controls=254,boundary_control='D=g gives equality, not the claimed strict inequality',scope='Only the fixed 120-port, copied-rank72, bank-free compressed-window moment/outer format. Not an integer-multiplication lower bound.')
print(json.dumps(result,indent=2))
