"""Independent complete count-vector bound, with the second moment engine.

No constructor or producer search module is imported. The producer's candidate
table supplies incumbents only; every lower-cost integer multiset is covered.
"""
from pathlib import Path
from fractions import Fraction as Q
import importlib.util,json,hashlib
from collections import Counter
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
ENGINE=ROOT/'research/complex-k492-owner-repair/vendor/multicold/engines/base_two_moment.py'
sp=importlib.util.spec_from_file_location('second_exact_engine',ENGINE);E=importlib.util.module_from_spec(sp);sp.loader.exec_module(E)
import argparse
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
source=json.loads(args.input.read_text());z=Q(source['endpoint']);grid=10**30
widths=(4,5,7,8,9);prices=(-1,-20,-8,-2,4);caps={8:(672,2),16:(448,4),32:(448,8),48:(448,-13)}
def require(ok,msg):
    if not ok:raise ValueError(msg)

# Exhaustive width-count Cartesian enumeration, not the producer's unbounded
# knapsack recurrence. Every legal count vector in every capacity is included.
upper={};vectors=0
def patterns(cap,index=0,fill=0,value=0):
    global vectors
    if index==len(widths):
        vectors+=1;rem=cap-fill;upper[rem]=max(upper.get(rem,-10**9),value+caps[cap][1]);return
    w,p=widths[index],prices[index]
    for count in range((cap-fill)//w+1):patterns(cap,index+1,fill+count*w,value+count*p)
for cap in caps:patterns(cap)
require(upper=={int(k):v for k,v in source['upper'].items()},'Independent dual table')
inventory={4:80,5:32,7:54,8:122,9:216}
signed=sum(n*bonus for n,bonus in caps.values())+9*sum(inventory[w]*p for w,p in zip(widths,prices))
mass=sum(cap*n for cap,(n,_)in caps.items())-9*sum(w*n for w,n in inventory.items())
require((signed,mass,upper[48])==(-3892,14382,-13),'Independent mass/dual coefficients')
require(48*signed+13*mass==150,'Integer credit requirement')
phi={}
for rank in range(1,49):
    lo,hi=E.log_bounds(Q(73,rank));lo=rank*E.exp_bounds(z*lo)[0];hi=rank*E.exp_bounds(z*hi)[1]
    phi[rank]=(int(lo*grid),-int((-hi*grid)//1))
ranks=sorted(r for r in upper if 0<r<48)
cost={r:(48*phi[r][0]-r*phi[48][1],48*phi[r][1]-r*phi[48][0])for r in ranks}
credit={r:48*upper[r]+13*r for r in ranks}
require(all(lo>0 for lo,hi in cost.values()),'Positive residual excess')
candidate={row['replicas']:tuple(sorted(row['non48']))for row in source['candidates']}
require(len(source['candidates'])==22 and set(candidate)==set(range(1,23)),'Complete T1..T22 candidate inventory')
incumbent={t:(sum(cost[r][0]for r in parts),sum(cost[r][1]for r in parts))for t,parts in candidate.items()}
bound=max(hi for lo,hi in incumbent.values())

# Polynomial-style multiplication of one count-vector factor per rank.
# Every nonnegative count is retained until its strictly positive lower cost
# exceeds the largest candidate's upper cost; there are no heuristic cuts.
states=[((),0,0,0,0)];expanded=0;maximum_terms=0
for rank in ranks:
    next_states=[];a,b=cost[rank]
    for parts,lo,hi,m,c in states:
        for count in range((bound-lo)//a+1):
            newparts=parts+(rank,)*count
            next_states.append((newparts,lo+count*a,hi+count*b,m+count*rank,c+count*credit[rank]))
            maximum_terms=max(maximum_terms,len(newparts));expanded+=1
    states=next_states
    require(len(states)<1000000,'Unexpected enumeration size; no truncation is allowed')
feasible=Counter();seen=set()
for parts,lo,hi,m,c in states:
    for t in range(1,23):
        if m>mass*t or (mass*t-m)%48 or c<150*t:continue
        feasible[t]+=1
        if parts==candidate[t]:seen.add(t)
        else:require(lo>incumbent[t][1],'A competing count vector is not strictly excluded')
require(seen==set(range(1,23)),'All candidate profiles reproduced')
winner=21
require(all(Q(incumbent[winner][1],winner)<Q(incumbent[t][0],t)for t in range(1,23)if t!=winner),'Unique best replica count')
local={1:2548,2:338,3:446,4:162,5:72,8:8};profile=Counter({r:189*n for r,n in local.items()});profile.update({48:6292,3:1,1:3})
moment=E.moment(73,18816,list(profile.items()),z)
require(moment[0]>1,'Best relaxed profile rejects the successor endpoint')
out=dict(status='PASS_INDEPENDENT_T1_TO_T22_FIXED_WIDTH_PACKING_BOUND',endpoint=str(z),
         bin_vectors=vectors,complete_states=len(states),expanded=expanded,maximum_non48_terms=maximum_terms,
         eligible_states_by_replicas=dict(feasible),winner=21,best_idle={48:6292,3:1,1:3},
         best_profile_moment=[str(q)for q in moment],
         independent_engine_sha256=hashlib.sha256(ENGINE.read_bytes()).hexdigest(),
         scope='For unchanged U8 local profile and helper widths, the 8/16/32/48 capacity inventory and retained prefix rule T<=22, every full-width owner packing has moment >1 at this upper endpoint. Covers arbitrary execution order by relaxing all window constraints. Other local words, partial helpers, capacities, prefix analyses and replication beyond22 are outside scope.')
args.out.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
