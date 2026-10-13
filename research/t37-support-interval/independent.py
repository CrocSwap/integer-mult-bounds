#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Charles Bethin, with substantial OpenAI Codex assistance.
"""Independent fill recurrence and logarithm/exp interval certificate.

No imports from verify.py or the repository's moment engines. The analytic
cross-check uses monotonicity of an exponential ratio, rather than the primary
proof's concavity after reparameterization. See README.md.
"""
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import argparse
import json

S=1 << 160

def need(ok,message):
    if not ok:raise ValueError(message)

def down(x):return x.numerator//x.denominator

def up(x):return -((-x.numerator)//x.denominator)

def ceil_div(a,b):return -(-a//b)


def bin_scores():
    # Build ordered fills, collapsing each mass by maximum attainable score.
    # This visits masses, not the primary checker's Cartesian count vectors.
    scores=[None]*49;scores[0]=0
    for mass in range(1,49):
        choices=[]
        for width,price in ((9,4),(8,-2),(7,-8),(5,-20),(4,-1)):
            if mass>=width and scores[mass-width] is not None:
                choices.append(scores[mass-width]+price)
        if choices:scores[mass]=max(choices)
    table={}
    for capacity,bonus in ((48,-13),(32,8),(16,4),(8,2)):
        for mass,score in enumerate(scores[:capacity+1]):
            if score is not None:
                rank=capacity-mass
                table[rank]=max(table.get(rank,-10**9),score+bonus)
    return table


def atanh_log(x):
    need(Q(1)<=x<=Q(2),'reduced logarithm domain')
    z=(x-1)/(x+1);power=z;total=Q(0)
    for j in range(80):
        total+=2*power/(2*j+1)
        power*=z*z
    tail=2*power/(161*(1-z*z))
    return total,total+tail


@lru_cache(None)
def log_interval(x):
    x=Q(x);need(x>=1,'log domain');k=0
    while x>=2:x/=2;k+=1
    lo,hi=atanh_log(x);two_lo,two_hi=atanh_log(Q(2))
    return down(S*(lo+k*two_lo)),up(S*(hi+k*two_hi))


def exp_interval(lo,hi):
    need(0<=lo<=hi<=4*S,'exponential domain')
    tl=tu=sl=su=S
    for j in range(1,91):
        tl=tl*lo//(S*j)
        tu=ceil_div(tu*hi,S*j)
        sl+=tl;su+=tu
    # The remaining term ratios are at most 4/92.
    nxt=ceil_div(tu*hi,91*S)
    tail=ceil_div(nxt*92,88)
    return sl,su+tail


def power_interval(x,b):
    lo,hi=log_interval(Q(x));b=Q(b)
    return exp_interval(down(b*lo),up(b*hi))


def ratio_interval(rank,credit,b):
    al,au=power_interval(Q(48,rank),b)
    bl,bu=power_interval(Q(48),b)
    need(bl>S,'positive ratio denominator')
    return (925*rank*Q(al-S,bu-S)-credit,
            925*rank*Q(au-S,bl-S)-credit)


def check(certificate):
    table=bin_scores()
    need(table=={int(r):v for r,v in certificate['upper'].items()},'independent bin table')
    need(set(table)==set(certificate['attainable_ranks']),'rank support')
    credit={r:48*table[r]+13*r for r in table}
    need(credit=={int(r):v for r,v in certificate['credits'].items()},'credit table')
    margins={}
    for r in sorted(table):
        if r in (0,1,32,48):continue
        lo,hi=ratio_interval(r,credit[r],Q(2,3))
        need(lo>0,'noncritical ratio: '+str(r))
        margins[r]=str(lo)
    left=ratio_interval(32,credit[32],Q(16,25))
    right=ratio_interval(32,credit[32],Q(13,20))
    need(left[0]>0 and right[1]<0,'independent critical bracket')
    need(certificate['root_bracket']==['16/25','13/20'],'claimed bracket')
    need(certificate['countermodel']['replicas']==16 and certificate['countermodel']['idle']=={'32':3,'48':4792},'countermodel coordinates')
    need(3*32+4792*48==14382*16 and 3*8-4792*13==-3892*16,'independent countermodel equations')
    need(Q(150,925)==Q(6,37) and Q(14382,48)-Q(6,37*48)==Q(11086,37),'normalized optimum equations')
    return dict(status='PASS_INDEPENDENT_T37_SUPPORT_INTERVAL',method='mass recurrence; atanh logarithm bounds; rounded exponential series; monotone ratio proof',
                attainable_residual_ranks=len(table),noncritical_ratio_margins=margins,
                critical_left_margin=str(left[0]),critical_right_margin=str(right[1]),
                continuum='The monotone-ratio argument is proved separately in README.md; no sampling substitutes for it.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--certificate',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    need(not a.out.exists(),'output preservation')
    result=check(json.loads(a.certificate.read_text()))
    a.out.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'])

if __name__=='__main__':main()
