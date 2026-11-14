"""Root independent integer implementation of the alternating-pair radial matching."""
from itertools import product
from functools import lru_cache
from collections import Counter
from math import isqrt
import json,random
H=((1,1,1,1),(1,-1,1,-1),(1,1,-1,-1),(1,-1,-1,1));s=(1,-1,-1,1)
def need(ok,msg):
 if not ok:raise ValueError(msg)
def mul(A,x):return tuple(sum(a*b for a,b in zip(row,x)) for row in A)
def n2(x):return sum(a*a for a in x)
def paired(q,phase):
 need(q%2==1,'odd doubled coordinate')
 a=abs(q);sign=1 if q>0 else -1
 if phase==1 and a==1:return 0,-q
 base=a-(0 if a%4==(1 if phase==0 else 3) else 2)
 need(base>0,'positive noncentral base')
 return base,sign*(base+2 if a==base else base)
def match(q,phases=(0,0,1,1),bad_choice=False):
 ps=[paired(a,b) for a,b in zip(q,phases)]
 i=min(range(4),key=lambda i:(abs(q[i]) if bad_choice else ps[i][0],i))
 y=list(q);y[i]=ps[i][1]
 return tuple(y)
def F(x):
 hx=mul(H,x)
 if sum(x)%2==0:
  need(all(a%2==0 for a in hx),'even exact integrality');return tuple(a//2 for a in hx)
 dot=sum(a*b for a,b in zip(s,x));q=tuple(2*a-dot*b for a,b in zip(x,s))
 q=match(q);hq=mul(H,q)
 need(all(a%4==0 for a in hq),'forward odd integrality')
 return tuple((1 if i!=3 else -1)*a//4 for i,a in enumerate(hq))
def inv(y):
 if sum(y)%2==0:return tuple(a//2 for a in mul(H,y))
 jy=tuple((1 if i!=3 else -1)*a for i,a in enumerate(y));q=match(mul(H,jy));dot=sum(a*b for a,b in zip(s,q));num=tuple(2*a-dot*b for a,b in zip(q,s))
 need(all(a%4==0 for a in num),'inverse odd integrality');return tuple(a//4 for a in num)
def radial_half(m,n):
 d=4*m+4*n-1;return d<=0 or d*d<=64*m*n
def check_point(x):
 y=F(x);need(inv(y)==x and F(inv(x))==x,'two-sided inverse')
 need(sum(x)%2==sum(y)%2,'parity')
 hx=mul(H,x);err=sum((2*a-b)**2 for a,b in zip(y,hx))
 need(err==(4 if sum(x)%2 else 0),'sharp error')
 need(radial_half(n2(y),n2(x)),'bilateral half radial bound')
 return y

def main():
 half_count=0
 for q in product(range(-13,14,2),repeat=4):
  z=match(q);need(match(z)==q,'pair involution');need(sum((a-b)**2 for a,b in zip(q,z))==4,'one coordinate step')
  need((sum(q)-sum(z))%4==2,'checkerboard swap')
  # Scaling by two: norm difference<=1 is equivalent to |sqrt(n2q)-sqrt(n2z)|<=1.
  a,b=n2(q),n2(z);d=a+b-1;need(d<=0 or d*d<=4*a*b,'half-grid radial bound')
  half_count+=1
 count=0;images=set()
 for x in product(range(-6,7),repeat=4):
  images.add(check_point(x));count+=1
 need(len(images)==count,'finite collision control')
 rng=random.Random(20261113);large=[]
 for digits in [1,2,10,40,100,400]:
  for j in range(20):
   limit=10**digits; x=tuple(rng.randrange(-limit,limit+1) for _ in range(4));check_point(x);large.append(digits)
 families=[]
 for k in [0,1,2,7,100,10**10,10**50,10**100]:
  xo=(0,0,4*k+2,1);yo=(2*k+2,2*k+1,-2*k-1,-2*k-1)
  xi=(2*k+1,2*k+1,2*k+2,2*k+1);yi=(4*k+2,0,-1,0)
  need(F(xo)==yo and F(xi)==yi,'attaining directional sequences')
  lo=16*k*k+16*k+5;hi=16*k*k+20*k+7
  need((n2(xo),n2(yo),n2(xi),n2(yi))==(lo,hi,hi,lo),'sequence norm polynomials')
  need(radial_half(lo,hi),'family half bound');families.append(str(k))
 # Meaningful design controls: one phase and an unbalanced phase split violate the bound.
 for q,phases in [((1,1,1,1),(0,0,0,0)),((5,3,3,3),(0,1,1,1))]:
  z=match(q,phases);a,b=n2(q),n2(z);d=a+b-1
  need(d>0 and d*d>4*a*b,'bad phase split must violate bound')
 q=(1,1,3,3);need(match(match(q,bad_choice=True),bad_choice=True)!=q,'current magnitude tie rule must fail inversion')
 print(json.dumps({'status':'PASS_ROOT_GLOBAL_HALF_GRID_CANDIDATE','half_grid_box_cases':half_count,'integer_cube_cases':count,'distinct_images':len(images),'large_integer_cases':len(large),'max_decimal_digits':400,'seed':20261113,'directional_sequence_parameters':families,'exact_controls':3,'scope':'finite exact corroboration of separately stated universal pairing/coset/norm proof, not a proof by finite search','no_author_code_imported':True},indent=2))
if __name__=='__main__':main()
