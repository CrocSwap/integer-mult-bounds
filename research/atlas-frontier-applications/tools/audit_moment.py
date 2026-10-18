# SPDX-License-Identifier: Apache-2.0
"""Independent dyadic interval moment auditor, atlas D020.
Uses only Python integers/Fraction; imports no inherited numerical implementation.
This authenticates a paid histogram and its root, not a physical realization.
"""
from fractions import Fraction as F
from pathlib import Path
from functools import lru_cache
from collections import Counter
import argparse,json,hashlib

BITS=192
SCALE=1<<BITS

def need(c,m):
    if not c:raise ValueError(m)
def down(x):return F(x.numerator*SCALE//x.denominator,SCALE)
def up(x):return F(-((-x.numerator*SCALE)//x.denominator),SCALE)
@lru_cache(None)
def log_bounds(q):
    need(q>=1,'log domain');k=0
    while q>2:q/=2;k+=1
    def unit(y):
        z=(y-1)/(y+1);z2=z*z;term=z;value=F(0)
        for j in range(128):
            value+=term/(2*j+1);term*=z2
        remainder=2*term/(257*(1-z2))
        return 2*value,2*value+remainder
    l,u=unit(q);l2,u2=unit(F(2));return down(l+k*l2),up(u+k*u2)
def exp_bounds(y):
    need(0<=y<F(1,10),'small exponential domain');term=F(1);value=term
    for j in range(1,25):term=term*y/j;value+=term
    first=term*y/25;tail=first/(1-y/26)
    return down(value),up(value+tail)
def moment(profile,b,W):
    need(0<=b<F(1,100),'saving domain');lo=hi=F(0)
    for rank,count in profile.items():
        need(0<rank<73 and count>0,'profile domain');l,u=log_bounds(F(73,rank));a=exp_bounds(b*l)[0];z=exp_bounds(b*u)[1];weight=F(rank*count,73*W);lo+=weight*a;hi+=weight*z
    return down(lo),up(hi)
def run(candidate,baseline):
    prof={int(k):v for k,v in json.loads((candidate/'PROFILE.json').read_bytes()).items()}
    old={int(k):v for k,v in json.loads((baseline/'PROFILE.json').read_bytes()).items()}
    need(sum(r*n for r,n in prof.items())==24212736,'new exact mass');need(sum(r*n for r,n in old.items())==16141824,'old exact mass')
    delta=Counter({r:2*n for r,n in prof.items()});delta.subtract({r:3*n for r,n in old.items()});need({r:n for r,n in delta.items()if n}=={32:2,5:-2,2:-3,16:-3},'source comparison polynomial')
    q=10**26;lo=int(F('0.001718659357407250209979')*q);hi=lo+100
    need(moment(prof,F(lo,q),333312)[1]<1 and moment(prof,F(hi,q),333312)[0]>1,'initial root bracket')
    while hi-lo>1:
        mid=(lo+hi)//2;a,b=moment(prof,F(mid,q),333312)
        if b<1:lo=mid
        elif a>1:hi=mid
        else:raise ValueError('insufficient interval resolution')
    claim=F('0.001718659357407250209979')-F(1,10**46)-F(1,10**70)
    prior=F(json.loads((baseline/'CLAIM.json').read_bytes())['kappa']);need(prior<claim<F(lo,q),'strict lower claim and comparison')
    om=moment(old,prior,222208);nm=moment(prof,prior,333312);need(nm[1]<om[0]<1,'strict normalized moment dominance')
    controls=[]
    need(log_bounds(F(1))==(0,0)and exp_bounds(F(0))==(1,1),'zero identities');controls.append('exact log1/exp0')
    need(moment(prof,F(hi,q)+F(1,10**18),333312)[0]>1,'inflated endpoint rejection');controls.append('inflated lower endpoint rejected')
    wrong=dict(prof);wrong[32]+=1;need(moment(wrong,F(lo,q),333312)[0]>1,'omitted charge rejection');controls.append('extra rank32 charge destroys claimed endpoint')
    # Intervals are rigorous Taylor/atanh inclusions; decimal quotations are not used as evidence.
    return dict(status='PASS_INDEPENDENT_DYADIC_RATIONAL_MOMENT',method='128-term atanh logarithms, 24-term exponential, exact positive tail bounds and outward rounding at 2^-192',lower=str(F(lo,q)),upper=str(F(hi,q)),target=str(claim),target_decimal='0.0017186593574072502099789999999999999999999998999999999999999999999999',previous=str(prior),gain=str(claim-prior),profile_delta_two_new_minus_three_old={r:n for r,n in delta.items()if n},new_moment_at_previous=[str(x)for x in nm],old_moment_at_previous=[str(x)for x in om],controls=controls,profile_sha256=hashlib.sha256((candidate/'PROFILE.json').read_bytes()).hexdigest(),baseline_claim_sha256=hashlib.sha256((baseline/'CLAIM.json').read_bytes()).hexdigest(),scope='Independent exact rational interval arithmetic and histogram comparison; complete physical/outer admission separate.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();result=run(a.candidate,a.baseline);need(not a.out.exists(),'fresh output');a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({k:result[k]for k in ['status','lower','upper','target','gain','controls']},indent=2))
