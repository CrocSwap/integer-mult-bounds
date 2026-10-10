"""Independent ternary-range rational log and exp engine, newly authored.
Uses100-term atanh for logarithms after powers-of-three reduction and a
24-term exponential with geometric tail. No imports from first interval engine.
"""
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
import json,hashlib
import sys
CODE=Path(__file__).resolve().parent;sys.path.insert(0,str(CODE.parent));import support
P=support.OUTPUT;SCALE=10**60

def down(x):return F((x*SCALE).numerator//(x*SCALE).denominator,SCALE)
def up(x):return -down(-x)
@lru_cache(None)
def small_log(x):
 assert 1<=x<=3
 z=(x-1)/(x+1);total=F(0);power=z
 for j in range(100):total+=2*power/(2*j+1);power*=z*z
 remainder=2*power/(201*(1-z*z))
 return down(total),up(total+remainder)
@lru_cache(None)
def log_interval(x):
 x=F(x);assert x>=1;k=0
 while x>=3:x/=3;k+=1
 a,b=small_log(x);c,d=small_log(F(3));return a+k*c,b+k*d

def exp_interval(a,b):
 a,b=F(a),F(b)
 assert 0<=a<=b<=1
 def series(x):
  term=F(1);total=F(1)
  for j in range(1,25):term=term*x/j;total+=term
  nextterm=term*x/25
  return down(total),up(total+nextterm/(1-x/26))
 return series(a)[0],series(b)[1]

def moment(hist,m,W,alpha):
 lo=hi=F(0)
 for r,n in hist.items():
  assert 0<r<=m and type(n)is int and n>0
  a,b=log_interval(F(m,r));c,d=exp_interval(alpha*a,alpha*b);weight=F(r*n,m)/W;lo+=weight*c;hi+=weight*d
 a,b=log_interval(F(m));c,d=exp_interval(alpha*a,alpha*b);weight=F(32*m*sum(hist.values()),10**16)/W
 return lo+weight*c,hi+weight*d

def run():
 rows=[]
 for name in ['baseline-receipt','weighted890-price']:
  path=P/'arithmetic'/(name+'.json');x=json.loads(path.read_text());hist={int(r):n for r,n in(x.get('banked_histogram')or x['profile']['banked_histogram']).items()};W=F(x['unreplicated_stock']);root=x['bit_root_bracket'];low=F(root['lower']);high=F(root['upper']);lm=moment(hist,100,W,low);hm=moment(hist,100,W,high)
  assert lm[1]<1<hm[0]
  for k,observed in [('lower_moment',lm),('upper_moment',hm)]:
   original=tuple(map(F,root[k]));assert max(original[0],observed[0])<=min(original[1],observed[1])
  rows.append(dict(name=name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),root_lower=str(low),root_upper=str(high),lower_moment_bounds=list(map(str,lm)),upper_moment_bounds=list(map(str,hm)),strict_signs=True,independent_engine_intervals_overlap=True))
 result=dict(status='PASS_TWO_ROOTS_SECOND_EXACT_ENGINE',checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),cases=rows,scope='Independent rational interval certification of declared priced profiles; does not establish physical admissibility.')
 (P/'arithmetic/second-moment-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='cases'}))
if __name__=='__main__':
 if not __debug__:raise RuntimeError('Assertions required')
 run()
