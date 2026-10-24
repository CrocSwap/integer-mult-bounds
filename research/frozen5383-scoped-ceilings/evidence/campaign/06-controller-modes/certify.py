#!/usr/bin/env python3
"""Directed rational sign certificates, independent of candidate arithmetic.
Atanh log with explicit tail; exp positive Taylor18 with geometric tail.
All arithmetic uses Fraction, and each summand selects the favorable endpoint.
"""
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json,time
HERE=Path(__file__).resolve().parent
U=10**45
def down(x):return F(x.numerator*U//x.denominator,U)
def up(x):return -down(-x)
def small_log(x):
 z=(x-1)/(x+1);assert 0<=z<=F(1,3)
 p=z;s=F(0)
 for j in range(40):s+=2*p/(2*j+1);p*=z*z
 return down(s),up(s+2*p/(81*(1-z*z)))
@lru_cache(None)
def logr(r):
 k=r.bit_length()-1;a,b=small_log(F(r,2**k));l,h=small_log(F(2));return a+k*l,b+k*h
def exp_positive(x):
 assert x>=0
 shifts=0
 while x>F(1,32):x/=2;shifts+=1
 p=s=F(1)
 for j in range(1,19):p*=x/j;s+=p
 lo,hi=down(s),up(s+p*x/19/(1-x/20))
 for _ in range(shifts):lo,hi=down(lo*lo),up(hi*hi)
 return lo,hi
@lru_cache(None)
def power(r,c):
 # r^(1-c) = r / exp(c log r), with no floating arithmetic.
 l,h=logr(r);lower=exp_positive(c*l)[0];upper=exp_positive(c*h)[1]
 return down(F(r)/upper),up(F(r)/lower)
def interval(row,c):
 T,P=map(lambda p:{int(k):v for k,v in p.items()},[row['T'],row['P']]);lo=hi=F(0)
 for r in T.keys()|P.keys():
  n=T.get(r,0)-P.get(r,0);a,b=power(r,c)
  lo+=n*(a if n>=0 else b);hi+=n*(b if n>=0 else a)
 return lo,hi

def main(feasibility=None,output=None):
 start=time.monotonic();fp=feasibility or HERE/'FEASIBILITY-v1.json';data=json.loads(fp.read_text());targets=data['targets'];records=[];winners={}
 for k in targets:
  c=F(k);sc=[]
  for row in data['rows']:
   lo,hi=interval(row,c);sc.append({'changed_stages':row['changed_stages'],'lower':str(lo),'upper':str(hi),'strict_sign':'NEGATIVE' if hi<0 else 'POSITIVE' if lo>0 else 'UNRESOLVED'})
  altered=[r for r in sc if r['changed_stages']];assert len(altered)==561 and all(r['strict_sign']=='NEGATIVE' for r in altered)
  best=max(altered,key=lambda r:F(r['upper']));winners[k]=best
  assert sc[0]['strict_sign']=='POSITIVE'
  records.append({'target':k,'unchanged':sc[0],'best_changed_upper':best,'all_changed_strictly_negative':True,'records':sc})
 # Integer identity and known exact values control the interval implementation.
 assert power(1,F(targets[0]))[0]<=1<=power(1,F(targets[0]))[1]
 assert power(9,F(0))[0]<=9<=power(9,F(0))[1]
 assert power(9,F(1))[0]<=1<=power(9,F(1))[1]
 out={'schema':'fixed-p16-directed-rational-moments/1','status':'ALL_561_CHANGED_ALLOCATIONS_FAIL_DECLARED_TARGETS','feasibility_sha256':sha256(fp.read_bytes()).hexdigest(),'script_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),'arithmetic':'Fraction atanh40 log + positive Taylor18 exp, directed 45-decimal rational rounding; all tails bounded','scope':'negative favorable necessary moment at the three stated target savings; no full c-domain theorem','zero_additional_nonrecursive_penalty':True,'runtime_seconds':round(time.monotonic()-start,6),'targets':records}
 (output or HERE/'EXACT-SCREEN-v1.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':out['status'],'runtime_seconds':out['runtime_seconds'],'best_changed':winners},indent=2)); return out
if __name__=='__main__':main()
