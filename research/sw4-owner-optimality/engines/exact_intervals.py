"""Rational logarithm and exponential enclosures for the independent moment check.
Uses atanh logarithm intervals and Taylor exponential intervals, stdlib only.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter,defaultdict
from functools import lru_cache
import json,gzip
P=Path(__file__).resolve().parent
load=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def need(x,msg):
 if not x:raise ValueError(msg)
D=1<<200
def down(x):return Q(x.numerator*D//x.denominator,D)
def up(x):return -down(-x)
@lru_cache(None)
def log(q):
 k=0
 while q>=2:q/=2;k+=1
 def s(z):
  lo=2*sum((z**(2*j+1)/Q(2*j+1)for j in range(80)),Q(0));hi=lo+2*z**161/(161*(1-z*z));return lo,hi
 a,b=s((q-1)/(q+1));c,d=s(Q(1,3));return down(a+k*c),up(b+k*d)
def exp(a,b):
 def s(x):
  term=total=Q(1)
  for j in range(1,17):term*=x/j;total+=term
  return total,term*x/17/(1-x/18)
 need(0<=a<=b<Q(1),'positive small exponent');lo,_=s(a);hi,tail=s(b);return down(lo),up(hi+tail)
