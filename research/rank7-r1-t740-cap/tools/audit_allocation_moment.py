# SPDX-License-Identifier: Apache-2.0
"""Independent dyadic interval moment auditor, atlas D020.
Retained PR2908 arithmetic by Jeremy Diviney and its credited upstream authors;
Mason Hale with OpenAI Codex assistance changes only the authenticated baseline.
Marius-Paul Dumitrean (Claude Code assisted) changes only the authenticated baseline, to the PR2917 headline (PR2930),
to the PR2930 headline (PR2942) and to Dugongue's PR2969 moment nomination (its T370 ORDER/PROFILE).
Rohan Arun (Anthropic Claude assisted) changes only the authenticated baseline, to Jeremy Kothe's PR3015 headline (its T74 ORDER/PROFILE).
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
def run(candidate,source):
    import sys
    if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
    need(hashlib.sha256((source/'CLAIM.json').read_bytes()).hexdigest()=='f9b9fbaaac794c0ce279c238a33a2f34f8c91a34d97ccdeb5ec98b7b8ba56d73','exact pinned PR3015 headline')
    prof={int(k):v for k,v in json.loads((candidate/'PROFILE.json').read_bytes()).items()}
    old={int(k):v for k,v in json.loads((source/'PROFILE.json').read_bytes()).items()}
    W=896*(1+max(r for s,r in json.loads((candidate/'ORDER.json').read_bytes())))
    oldW=896*(1+max(r for s,r in json.loads((source/'ORDER.json').read_bytes())))
    need(sum(r*n for r,n in prof.items())==W*73-W*320//896,'new rank mass')
    need(sum(r*n for r,n in old.items())==oldW*73-oldW*320//896,'old rank mass')
    # No floating endpoint or inherited numerical implementation is used.
    q=10**26;lo=0;hi=q//200
    need(moment(prof,F(lo,q),W)[1]<1 and moment(prof,F(hi,q),W)[0]>1,'global root bracket')
    while hi-lo>1:
        mid=(lo+hi)//2;l,u=moment(prof,F(mid,q),W)
        if u<1:lo=mid
        elif l>1:hi=mid
        else:raise ValueError('interval precision insufficient')
    endpoint=F((lo//100),10**24)
    target=endpoint-F(1,10**46)-F(1,10**70)
    prior=F(json.loads((source/'CLAIM.json').read_bytes())['kappa'])
    need(target>prior and target<F(lo,q),'strict frontier improvement and lower endpoint')
    normalized_delta=Counter({r:n*oldW for r,n in prof.items()});normalized_delta.subtract({r:n*W for r,n in old.items()})
    normalized_delta={r:n for r,n in normalized_delta.items()if n}
    at_old=moment(prof,prior,W);need(at_old[1]<1,'new moment strictly below one at full previous headline')
    # Positive root uniqueness: all charged ranks are strictly below m = 73,
    # hence every nonzero summand increases strictly with the saving parameter.
    need(log_bounds(F(1))==(0,0) and exp_bounds(F(0))==(1,1),'zero controls')
    need(moment(prof,F(hi,q)+F(1,10**18),W)[0]>1,'overstated endpoint rejected')
    wrong=dict(prof);wrong[32]=wrong.get(32,0)+1
    need(moment(wrong,F(lo,q),W)[0]>1,'omitted rank charge rejected')
    import decimal
    with decimal.localcontext() as c:
        c.prec=80
        todec=lambda x:str(decimal.Decimal(x.numerator)/decimal.Decimal(x.denominator))
        texttarget=todec(target);textgain=todec(target-prior)
    return dict(status='PASS_SEPARATE_EXACT_RATIONAL_FRONTIER_MOMENT',lower=str(F(lo,q)),upper=str(F(hi,q)),outer_endpoint=str(endpoint),target=str(target),target_decimal=texttarget,previous=str(prior),gain=str(target-prior),gain_decimal=textgain,W=W,oldW=oldW,normalized_profile_delta=normalized_delta,new_moment_at_full_prior=[str(x)for x in at_old],profile_sha256=hashlib.sha256((candidate/'PROFILE.json').read_bytes()).hexdigest(),baseline_profile_sha256=hashlib.sha256((source/'PROFILE.json').read_bytes()).hexdigest(),baseline_claim_sha256=hashlib.sha256((source/'CLAIM.json').read_bytes()).hexdigest(),method='Independent 128-term atanh / degree24 exponential with explicit positive tails and outward 192-bit dyadic rounding',controls=['zero log/exp identities','overstated endpoint','added rank32 charge'],scope='Complete paid histogram and exact moment only; full native/physical/outer release is separate.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    need(not a.out.exists(),'fresh output required');d=run(a.candidate,a.source);a.out.write_text(json.dumps(d,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({k:d[k]for k in ['status','target_decimal','gain_decimal','lower','upper']}))
