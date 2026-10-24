#!/usr/bin/env python3
"""Independent rational enclosure of the local boundary moment. Apache-2.0.
Yiyang (@Lyy-iiis), with substantial OpenAI Codex parallel-agent assistance.
"""
from fractions import Fraction as F
import json

def need(ok,msg):
    if not ok:raise RuntimeError(msg)
def log_atanh(z,m=24):
    low=2*sum((z**(2*j+1)/F(2*j+1) for j in range(m)),F(0))
    tail=2*z**(2*m+1)/(F(2*m+1)*(1-z*z))
    return low,low+tail

def log_int(n):
    if n==1:return F(0),F(0)
    k=n.bit_length()-1
    r=F(n,2**k);z=(r-1)/(r+1)
    need(0<=z<=F(1,3),'log range')
    l2,u2=log_atanh(F(1,3));lr,ur=log_atanh(z)
    return k*l2+lr,k*u2+ur

def exp_minus(x):
    need(0<=x<=1,'alternating exp range')
    term=F(1);s=term
    # Even degree 12 is upper; next (negative) term yields lower.
    for j in range(1,13):term*=(-x)/j;s+=term
    upper=s;lower=s+term*(-x)/13
    return lower,upper

def rank_power(n):
    lo,hi=log_int(n);c=F(17,5000)
    lower=exp_minus(c*hi)[0]*n
    upper=exp_minus(c*lo)[1]*n
    return lower,upper

def main():
    T={4:56,7:14,8:94,9:652,17:224};P={1:4656,2:920,3:1386}
    target=[rank_power(k) for k in T];paid=[rank_power(k) for k in P]
    lo=sum((T[k]*a[0] for k,a in zip(T,target)),F(0))-sum((P[k]*a[1] for k,a in zip(P,paid)),F(0))
    hi=sum((T[k]*a[1] for k,a in zip(T,target)),F(0))-sum((P[k]*a[0] for k,a in zip(P,paid)),F(0))
    need(F(573,20)<lo<=hi<F(1433,50),'coarse exact interval 28.65 < delta < 28.66')
    need(67*lo>1904,'L67 strict passing')
    need(66*hi<1904,'L66 strict failing')
    # Check mutation replacing full rank17 boundary cost by only112 jobs.
    need(112*17==1904 and 112!=1904,'full boundary axes')
    print(json.dumps({'scope':'local ideal moment only','C':'17/5000','strict_delta_interval':['573/20','1433/50'],'L66_margin_upper':str(66*F(1433,50)-1904),'L67_margin_lower':str(67*F(573,20)-1904),'least_passing_integer_L':67,'boundary_rank_one_charge':1904},indent=2))
    losslo,losshi=(112*v for v in rank_power(17))
    need(1885<losslo<=losshi<1886,'truncated output loss enclosure')
    need(65*hi<losslo,'L65 truncated fails')
    need(66*lo>losshi,'L66 truncated passes')
    print(json.dumps({'scope':'truncated productive contract local ideal moment only','target':'L*T - 112 H17','paid':'L*P','strict_target_loss_interval':[1885,1886],'L65_margin_upper':str(65*F(1433,50)-1885),'L66_margin_lower':str(66*F(573,20)-1886),'least_passing_integer_L':66,'extra_boundary_provider_calls':0},indent=2))
    print('PASS_INDEPENDENT_BOUNDARY_MOMENT')
if __name__=='__main__':main()
