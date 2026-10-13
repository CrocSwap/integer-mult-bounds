"""Exact global profile relaxation for 1..22 data replicas.

Uses PR795's signed integer bin prices, not a feasible owner constructor.
Every non-48 remainder contributes positive excess over fractional all-48.
This makes the cost-bounded multiset search finite, independently of mass.
"""
from fractions import Fraction as F
from pathlib import Path
import importlib.util
import itertools
import json

P=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('intervals',P/'exact_intervals.py')
en=importlib.util.module_from_spec(sp);sp.loader.exec_module(en)
WIDTH={4:-1,5:-20,7:-8,8:-2,9:4}
CAP={8:2,16:4,32:8,48:-13}
ENDPOINT=F(1664724476433282815290,10**24)


def need(ok,label):
    if not ok:raise ValueError(label)


def dual():
    upper={}
    for cap,bonus in CAP.items():
        dp=[None]*(cap+1);dp[0]=0
        for fill in range(1,cap+1):
            possibilities=[dp[fill-width]+price for width,price in WIDTH.items()
                           if fill>=width and dp[fill-width] is not None]
            dp[fill]=max(possibilities) if possibilities else None
        for fill,value in enumerate(dp):
            if value is not None:
                rem=cap-fill;upper[rem]=max(upper.get(rem,-10**9),bonus+value)
    need(upper[0]==0 and upper[48]==-13,'dual normalization')
    return upper


def main(output):
    upper=dual();scale=en.D
    weights={}
    for rank in range(1,49):
        lo,hi=en.log(F(73,rank));lo,hi=en.exp(ENDPOINT*lo,ENDPOINT*hi)
        weights[rank]=(int(rank*lo*scale),int(rank*hi*scale))
    ranks=sorted(r for r in upper if 0<r<48)
    cost={r:(48*weights[r][0]-r*weights[48][1],48*weights[r][1]-r*weights[48][0])for r in ranks}
    need(all(lo>0 for lo,hi in cost.values()),'positive remainder excess')
    credit={r:48*upper[r]+13*r for r in ranks}
    best={};nodes=0;ties=[]

    def admit(parts,mass,value,lo,hi):
        for replicas in range(1,23):
            if value<150*replicas or mass>14382*replicas or (mass-30*replicas)%48:continue
            old=best.get(replicas)
            if old is None or hi<old['lower']:
                best[replicas]=dict(parts=list(parts),mass=mass,credit=value,lower=lo,upper=hi)
            elif lo<=old['upper'] and list(parts)!=old['parts']:
                # Mathematically identical count vectors are filtered by order.
                # Any other overlap needs a stronger enclosure, not a guess.
                ties.append(dict(replicas=replicas,a=list(parts),b=old['parts']))

    # Obtain feasible relaxation incumbents cheaply; no geometric claim.
    for count in range(1,5):
        for parts in itertools.combinations_with_replacement(ranks,count):
            admit(parts,sum(parts),sum(credit[r]for r in parts),
                  sum(cost[r][0]for r in parts),sum(cost[r][1]for r in parts))
    need(len(best)==22,'all replica counts seeded')
    seed={r:dict(z)for r,z in best.items()}
    ties.clear()
    bound=max(z['upper']for z in best.values())

    def visit(start,parts,mass,value,lo,hi):
        nonlocal nodes
        nodes+=1
        if parts:admit(parts,mass,value,lo,hi)
        for index in range(start,len(ranks)):
            rank=ranks[index];newlo=lo+cost[rank][0]
            if newlo<=bound:
                visit(index,parts+(rank,),mass+rank,value+credit[rank],newlo,hi+cost[rank][1])
    visit(0,(),0,0,0,0)
    need(not ties,'unseparated distinct profile prices')
    answer=[]
    for replicas,z in sorted(best.items()):
        count48=(14382*replicas-z['mass'])//48
        profile={48:count48}
        for rank in z['parts']:profile[rank]=profile.get(rank,0)+1
        need(sum(r*n for r,n in profile.items())==14382*replicas,'mass')
        need(sum(upper[r]*n for r,n in profile.items())>=-3892*replicas,'signed-price feasibility')
        answer.append(dict(replicas=replicas,profile=profile,non48=z['parts'],
                           credit=z['credit'],required_credit=150*replicas,
                           normalized_penalty_interval=[str(F(z['lower'],48*scale*replicas)),str(F(z['upper'],48*scale*replicas))],
                           prefix_bits=113+18*replicas,
                           geometric_assignment_provided=False))
    winner=min(best,key=lambda r:F(best[r]['upper'],r))
    need(all(F(best[winner]['upper'],winner)<F(z['lower'],r)for r,z in best.items()if r!=winner),'unique best replica count')
    result=dict(status='passed',endpoint=str(ENDPOINT),nodes=nodes,
                enumeration_cost_bound=str(F(bound,48*scale)),ranks=ranks,
                upper=upper,credits=credit,best_replica_count=winner,candidates=answer,
                scope='Complete cost-bounded remainder-profile relaxation using one PR795 dual. No time-window, geometry, bin-pattern, hosting, or native admission proof; no new kappa.')
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status='passed',nodes=nodes,best_replicas=winner,best=answer[winner-1])))


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    main(parser.parse_args().out)
