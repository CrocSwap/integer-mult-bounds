"""Exact arithmetic screen only: test transfer of PR491's count-only formula to m73.
This does not establish the complex fallback compiler count or physical admission.
"""
from pathlib import Path
from fractions import Fraction as Q
from decimal import Decimal,localcontext
import json,importlib.util,hashlib
R=Path(__file__).resolve().parent;O=R/'complex496-count-screen';O.mkdir(exist_ok=False)
src=R/'source496-review/EXPECTED.json';parent=json.loads(src.read_text());alloc=json.load(open(R/'source496-review/provenance/POOLED-ALLOCATION.json'));P={int(r):n for r,n in alloc['profile'].items()};m=alloc['ambient'];W=alloc['live'];N=2*m;old=32*m*m;new=6*N*(N-1)+3*N+6*(N-1);assert new==24*m*m+6*m-6<old
engine=R/'source496-review/vendor/complex/split-centres-global/vendor/engines'
def load(name):
 sp=importlib.util.spec_from_file_location(name,engine/(name+'.py'));M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M);return M
M=load('moment');B=load('base_two_moment')
def moment(z,count):
 a,c=M.moment(P,m,W,z,False);lo,hi=M.logarithm(Q(m));e,f=M.exponential(z*lo,z*hi);coef=Q(count*sum(P.values()),10**16*m*W);return a+coef*e,c+coef*f
with localcontext() as ctx:
 ctx.prec=80
 terms=[(Decimal(r*n)/Decimal(m*W),(Decimal(m)/Decimal(r)).ln()) for r,n in P.items()];fb=Decimal(new*sum(P.values()))/Decimal(10**16*m*W);logm=Decimal(m).ln();lo=Decimal(0);hi=Decimal('.003')
 for _ in range(220):
  z=(lo+hi)/2
  if sum(v*(z*l).exp() for v,l in terms)+fb*(z*logm).exp()<1:lo=z
  else:hi=z
 tick=int(lo*10**24)
b=Q(tick,10**24);bp=b+Q(1,10**24);evidence=[]
for z,accept in [(b,True),(bp,False)]:
 a,c=moment(z,new);u,v=B.moment(m,W,list(P.items()),z);l,h=B.moment(m,W,[(1,new*sum(P.values()))],z);u+=l/10**16;v+=h/10**16;assert (c<1 and v<1) if accept else (a>1 and u>1);evidence.append(dict(endpoint=str(z),accept=accept,mercator=[str(a-1),str(c-1)],base_two=[str(u-1),str(v-1)]))
assert moment(b,old)[0]>1
eta=beta=Q(1,10**18);c=Q(parent['bit_lower']);s=min(c,(1-beta)*b)-Q(1,10**24);a=Q(384599,10**10)
for _ in range(6):a=(1-s)*s+s*a
margin=(1-eta)*a*(1-2*eta)/(1+a*(1-2*eta));grid=Q(1,10**18);ticks=margin/grid;k=grid*((ticks.numerator-1)//ticks.denominator)
r=dict(status='EXACT_ARITHMETIC_SCREEN_COMPLEX_FALLBACK_TRANSFER_UNREVIEWED',old_count=old,new_count=new,old_complex_lower=parent['complex_lower'],new_complex_lower=str(b),next_endpoint=str(bp),old_count_rejected_at_new_root=True,proposed_kappa=str(k),proposed_kappa_decimal=f'{float(k):.18f}',gain=str(k-Q(parent['kappa'])),evidence=evidence,parent_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),scope='No stronger probability assumed: retains 10^-16. Formula derived from PR491 bit-side Gauss-Jordan invoice; transfer to actual complex fallback needs source proof review. Not a verified new bound, no full outer/physical replay claimed.')
(O/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print({k:v for k,v in r.items() if k!='evidence'},flush=True)
