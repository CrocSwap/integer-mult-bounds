#!/usr/bin/env python3
"""Directed integer log/exp enclosure, independently implemented for this run.

No imported supplier or moment code. The geometric atanh remainder and the
positive exponential remainder are bounded explicitly. Floats are not used.
OpenAI Codex-assisted work. Apache-2.0.
"""
import argparse, hashlib, json, sys
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
try:
    from gmpy2 import mpz as Z
except ImportError:
    Z=int
sys.set_int_max_str_digits(0)

def ceildiv(a,b):return (a+b-1)//b

class Bounds:
    def __init__(self,digits):
        self.S=Z(10)**(digits+60)
        self.ln2=self.unitlog(Fraction(2))
        self.cache={}
    def unitlog(self,x):
        assert 1<=x<=2
        z=(x-1)/(x+1);p=Z(z.numerator);q=Z(z.denominator)
        if not p:return (Z(0),Z(0))
        lo=self.S*p//q;hi=ceildiv(self.S*p,q)
        sl=sh=Z(0);j=0
        while True:
            sl+=lo//(2*j+1);sh+=ceildiv(hi,2*j+1)
            lo=lo*p*p//(q*q);hi=ceildiv(hi*p*p,q*q);j+=1
            if hi<=2:break
        # Next power is z^(2j+1); all following denominators >=2j+1.
        tail=ceildiv(2*hi*q*q,(2*j+1)*(q*q-p*p))
        return 2*sl,2*sh+tail
    def log(self,x):
        if x in self.cache:return self.cache[x]
        y=x;k=0
        while y>=2:y/=2;k+=1
        lo,hi=self.unitlog(y)
        ans=(lo+k*self.ln2[0],hi+k*self.ln2[1]);self.cache[x]=ans
        return ans
    def exp(self,xlo,xhi):
        assert 0<=xlo<=xhi and 100*xhi<self.S
        lo=hi=sl=sh=self.S;j=0
        while True:
            j+=1
            lo=lo*xlo//(self.S*j);hi=ceildiv(hi*xhi,self.S*j)
            sl+=lo;sh+=hi
            if hi<=2:break
        # Subsequent term ratio is at most xhi/(S*(j+1)).
        tail=ceildiv(hi*xhi,self.S*(j+1)-xhi)
        return sl,sh+tail
    def moment(self,H,a):
        low=high=Z(0);num=Z(a.numerator);den=Z(a.denominator)
        for r,n in sorted(H.items()):
            l,h=self.log(Fraction(73,r))
            el,eh=self.exp(l*num//den,ceildiv(h*num,den))
            low+=el*(r*n)//(73*66304)
            high+=ceildiv(eh*(r*n),73*66304)
        return low,high

def main():
 import sys
 if sys.flags.optimize:raise SystemExit("assertions must be enabled")
 p=argparse.ArgumentParser();p.add_argument('candidate',type=Path);p.add_argument('baseline',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 H={int(r):n for r,n in json.loads((a.candidate/'PROFILE.json').read_text()).items()};baseclaim=json.loads((a.baseline/'CLAIM.json').read_text());base=Fraction(baseclaim['kappa']);old={int(r):2*n for r,n in json.loads((a.baseline/'PROFILE.json').read_text()).items()}
 b=Bounds(100);scale=10**30;lo=0;hi=scale//500
 assert b.moment(H,Fraction(lo,scale))[1]<b.S<b.moment(H,Fraction(hi,scale))[0]
 while hi-lo>1:
  mid=(lo+hi)//2;l,h=b.moment(H,Fraction(mid,scale))
  if h<b.S:lo=mid
  elif l>b.S:hi=mid
  else:raise ValueError('insufficient precision')
 # The inherited full admission computes a 24-place complex lower bound.
 C=Fraction(lo//10**6,10**24);k=C-Fraction(1,10**46)-Fraction(1,10**70)
 need=lambda v: v or (_ for _ in ()).throw(ValueError('moment inequality'))
 need(b.moment(H,C)[1]<b.S);need(b.moment(H,C+Fraction(1,10**24))[0]>b.S);need(b.moment(old,C)[0]>b.S);need(k>base)
 with localcontext() as ctx:
  ctx.prec=90
  dec=lambda q:str(Decimal(q.numerator)/Decimal(q.denominator))
  result={'status':'PASS_INDEPENDENT_EXACT_PAIR_MOMENT','complex_lower':str(C),'root_bracket_30':[str(Fraction(lo,scale)),str(Fraction(hi,scale))],'kappa_rational':str(k),'kappa_decimal_90':dec(k),'baseline_rational':str(base),'gain_rational':str(k-base),'gain_decimal_90':dec(k-base),'controls':{'old_doubled_profile_rejected_at_candidate_endpoint':True,'next_endpoint_grid_point_rejected':True},'profile':H,'scope':'Directed integer atanh and exp enclosures; no floating point. Complete hosting and outer release required separately.'}
 a.out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],result['kappa_decimal_90'],'gain',result['gain_decimal_90'])
if __name__=='__main__':main()
