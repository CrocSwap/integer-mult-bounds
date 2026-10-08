#!/usr/bin/env python3
"""Standard-library independent rational check; imports no candidate checker.

Reconstructs the two-axis child list from raw role/profile records and checks
its characteristic with a separate Taylor enclosure and 60-decimal rational
rounding. It independently recomputes the seven balanced final margins.
It does not establish the physical circuit or inherited analytic interfaces.
"""
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent

def read(name):return json.loads((HERE/name).read_text())
def require(ok,msg):
    if not ok:raise ValueError(msg)
@lru_cache(None)
def logarithm(x):
    require(x>=1,'log domain');k=0
    while x>2:x/=2;k+=1
    def series(y):
        z=(y-1)/(y+1);lo=sum((2*z**(2*j+1)/(2*j+1) for j in range(80)),F())
        return lo,lo+2*z**161/(161*(1-z*z))
    lo,hi=series(x);a,b=series(F(2));lo+=k*a;hi+=k*b
    scale=10**60
    return F((lo*scale).__floor__(),scale),F((hi*scale).__ceil__(),scale)
def exponential(x):
    require(0<=x<11,'exponential enclosure domain');term=F(1);lo=term
    for j in range(1,10):term=term*x/j;lo+=term
    tail=term*x/10/(1-x/11)
    return lo,lo+tail

def run():
    N=4073300;m=575;loss=2226400;W=2*N
    rows=Counter({1:23*N,17:2*N,21:2*N,481:2*N,23:2*N})
    # Five singleton copies per pair outside data: one paid endpoint and
    # two growth fronts on each axis. h25 growth's width23 is above; width21
    # growth on h23 adds to data's width21.
    rows[1]=23*N;rows[21]+=2*N
    for h,repeat in [(23,2300),(25,1771)]:
        r=read(f'original-{h}.json');p=read(f'profiles-{h}.json')
        R=r['c']+r['q']-r['matched'];require(R==r['R']==p['R'],'role accounting')
        require(sum(t*n for t,n in enumerate(p['blocks']))==h*R+2*h*(h-1),'axis rank mass')
        b=p['blocks'][:];require(b[h]==h,'center multiplicity');b[h]-=h;b[1]+=h
        W+=repeat*R
        rows.update({t:repeat*n for t,n in enumerate(b) if t and n})
        rows[h]+=repeat*R;rows[m-2*h]+=repeat*R
    require(sum(t*n for t,n in rows.items())==m*W-N+loss,'whole rank identity')
    params=read('parameters.json');den=params['grid_denominator'];a=F(params['bit_numerator'],den);k=F(params['kappa_numerator'],den)
    def moment(saving):
        lo=hi=F()
        for t,n in rows.items():
            l,u=logarithm(F(m,t));elo,_=exponential(saving*l);_,ehi=exponential(saving*u)
            w=F(t*n,m*W);lo+=w*elo;hi+=w*ehi
        return lo,hi
    lo,hi=moment(a);require(hi<1,'independent moment upper bound')
    nextlo,_=moment(a+F(1,den));require(nextlo>1,'independent next grid exclusion')
    backoff=F(1,10**12);q=a*(1-2*backoff);eps=(1-backoff)/(1+q);G=eps*q
    r=(G+1-eps)/2;delta=backoff/8
    margins=[1-eps,a,G,a,min(1-eps-delta,r-delta),1-eps-delta,eps]
    require(all(x>k for x in margins),'independent seven final margins')
    require(G<=k+F(1,den),'independent final next grid')
    print('PASS independent rational moment and seven margins')
    print('W='+str(W)+'; bit='+str(a)+'; kappa='+str(k))
    print('moment gap='+format(float(1-hi),'.16g')+'; absorption gap='+format(float(G-k),'.16g'))
    return dict(W=W,bit_saving=str(a),kappa=str(k),moment_gap_lower=str(1-hi),absorption_gap=str(G-k),margins=[str(x) for x in margins])
if __name__=='__main__':run()
