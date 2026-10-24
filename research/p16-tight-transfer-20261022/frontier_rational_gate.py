#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Standalone selected PR4470 exact P16 interval verifier. No dependencies.
This is an arithmetic gate, NOT a new physical supplier or kappa theorem.
"""
from fractions import Fraction as F
from functools import lru_cache
from collections import Counter
import json

HELP={4:28,7:7,8:47,9:326}
PAID={1:2237,2:388,3:494,4:147,5:36,8:8}
MAIN={145:224,73:224,**{k:448 for k in (17,25,33,41,49,57,65)}}
IDLE={72:224,**{k:448 for k in (16,24,32,40,48,56,64)}}

def add(*hists):
    out=Counter()
    for hist in hists:out.update(hist)
    return +out

def scaled(hist,k):return {r:n*k for r,n in hist.items()}

def counts(hist):return (sum(hist.values()),sum(r*n for r,n in hist.items()))

def profiles():
    T=add(MAIN,scaled(HELP,18));P=add(IDLE,scaled(PAID,18),{1:1680})
    assert counts(HELP)==(408,3471) and counts(PAID)==(3310,5327)
    assert counts(T)==(10928,239886) and counts(P)==(64620,239134)
    return T,P

@lru_cache(None)
def log_bounds(rank,n=28):
    if rank==1:return F(0),F(0)
    e=rank.bit_length()-1;q=F(rank,1<<e)
    def atanh(v):
        z=(v-1)/(v+1);power=z;s=F(0)
        for j in range(n):
            s+=2*power/(2*j+1);power*=z*z
        return s,s+2*power/((2*n+1)*(1-z*z))
    a,b=atanh(F(2));c,d=atanh(q)
    return e*a+c,e*b+d

def alternating(x,n):
    term=total=F(1)
    for j in range(1,n+1):
        term*=-x/j;total+=term
    return total

@lru_cache(None)
def weight(rank,kappa,digits=20):
    if rank==1:return 10**digits,10**digits
    lo,hi=log_bounds(rank)
    xlo,xhi=kappa*lo,kappa*hi
    assert 0<=xlo<=xhi<1
    s=10**digits
    a=rank*alternating(xhi,19)*s
    b=rank*alternating(xlo,20)*s
    return a.numerator//a.denominator,(b.numerator+b.denominator-1)//b.denominator

def moment_interval(T,P,kappa,digits=20):
    kappa=F(kappa);lo=hi=0
    for r,n in T.items():
        a,b=weight(r,kappa,digits);lo+=n*a;hi+=n*b
    for r,n in P.items():
        a,b=weight(r,kappa,digits);lo-=n*b;hi-=n*a
    return {'kappa':str(kappa),'lower_numerator':lo,'upper_numerator':hi,
            'denominator':10**digits,'positive':lo>0,'negative':hi<0}

def balanced(count,mass):
    k,rem=divmod(mass,count)
    return {k:count-rem,k+1:rem} if rem else {k:count}

def extreme(count,mass,maxrank=9):
    q,rem=divmod(mass-count,maxrank-1)
    d={1:count-q-int(rem>0),maxrank:q}
    if rem:d[rem+1]=1
    return {k:v for k,v in d.items() if v}

def run():
    T,P=profiles()
    left=moment_interval(T,P,'0.0030201659770')
    right=moment_interval(T,P,'0.0030201659771')
    deficit=moment_interval(T,P,'0.006')
    assert left['positive'] and right['negative'] and deficit['negative']
    H=balanced(408,3471);Q=extreme(3310,5327)
    CT=add(MAIN,scaled(H,18));CP=add(IDLE,scaled(Q,18),{1:1680})
    assert counts(CT)==counts(T) and counts(CP)==counts(P)
    ceiling=moment_interval(CT,CP,'0.006')
    assert ceiling['negative']
    def needed(change):
        for n in range(1,200):
            t,p=T.copy(),P.copy();change(n,t,p)
            if moment_interval(t,p,'0.006')['positive']:return n
    idle=needed(lambda n,t,p:p.__setitem__(64,p[64]-n))
    helper=needed(lambda n,t,p:(t.__setitem__(9,t[9]+18*n),p.__setitem__(1,p[1]+18*n)))
    assert (idle,helper)==(12,6)
    return {'status':'PASS_EXACT_RATIONAL_MOMENTS_ONLY',
      'repo':'CrocSwap/integer-mult-bounds','selected_PR':4470,
      'selected_sha':'b9a13c1673e0e9697de410de16e8bbf3207a7363',
      'selected_kappa':'0.00302015',
      'root_bracket':[left,right], 'failed_target_0_006':deficit,
      'frozen_rank_shape_at_0_006':ceiling,
      'hypothetical_min_idle_P64_jobs_deleted':idle,
      'hypothetical_min_rank9_new_helpers_per_call_with_P1_each':helper,
      'new_supplier':'NONE','new_kappa':False}

if __name__=='__main__':print(json.dumps(run(),indent=2,sort_keys=True))
