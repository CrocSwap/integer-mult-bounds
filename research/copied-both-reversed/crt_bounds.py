"""Dimension-monotone conservative h25 CRT envelope also covers h23."""
from math import comb,factorial,prod
from pathlib import Path
import json

def constants(h):
 # Same exact original-envelope Gram formulas as independently audited h25.
 return dict(core1=[12*(h+1),12*h*h-10*h+38],core2=[3*(h*h-1),12*h*h-34*h+64],line=[6*(h+1),12*h-28])
def run():
 low,high=constants(23),constants(25)
 assert all(0<low[k][j]<=high[k][j] for k in low for j in (0,1))
 D0=max(v[0] for v in high.values());B0=max(v[1] for v in high.values());D=D0*D0;B=2*D0*B0
 bound=sum(comb(25,j)*factorial(j)*B**j*D**(4-j) for j in range(5))
 primes=[]
 for e in [61,31,19,17,13]:
  p=2**e-1;s=4
  for _ in range(e-2):s=(s*s-2)%p
  assert s==0 and p>D0;primes.append(p)
 assert prod(primes)>bound
 assert all(comb(23,j)<=comb(25,j) for j in range(5))
 return dict(h=23,h23_frames=low,enclosing_h25_frames=high,Dframe=D0,Bframe=B0,Ddifference=D,Bdifference=B,all_minor_numerator_bound=bound,primes=primes,product=prod(primes),proof='For original envelope dimensions23and25, each frame numerator/denominator bound and binomial minor factor at23 is bounded by25. Same mask+rank4 transition Gram formulas; actual integer minor denominator is D_actual^4, not the numerical bound. Max-NE modular rank reconstruction is unchanged.')
