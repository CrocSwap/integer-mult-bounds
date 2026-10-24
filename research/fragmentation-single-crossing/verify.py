"""Exact rank-tail certificate for the fixed p16 fragmentation family.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Cao Yifan supplies the source invoice; PR5226 supplies the named S1 question.
"""
from pathlib import Path
from hashlib import sha256
from collections import Counter
from fractions import Fraction as F
from math import factorial
import argparse
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def need(ok, why):
    if not ok:
        raise ValueError(why)

for pin in json.loads((HERE/'SOURCES.json').read_text())['files']:
    if pin['usage'] == 'input':
        need(sha256((ROOT/pin['path']).read_bytes()).hexdigest() == pin['sha256'], 'Source pin')
source=json.loads((ROOT/'research/kappa-round3-warp-20261022/ARITHMETIC.json').read_text())
def census(key):
    return Counter({int(r):n for r,n in source[key].items()})
helpers,native,targets,paid=map(census,('local_helpers','local_paid','targets','paid'))
need(helpers=={4:28,7:7,8:47,9:326}, 'Independent helper endpoints')
need(sum(helpers.values())==408, 'Helper count')

# Rebuild the caller separately from its published complete invoice.
def caller(local):
    T=Counter({r:18*n for r,n in helpers.items()})
    P=Counter({r:18*n for r,n in local.items()})
    T[145]+=224
    P[1]+=112*15
    for length in (7,8):
        for j in range(1,length+1):
            T[8*(j+1)+1]+=224
            P[8*(j+1)]+=224
    return T,P
need(caller(native)==(targets,paid), 'Complete source invoice binding')
base_native=helpers.copy();base_native[8]+=224+8
skeleton_T,skeleton_P=caller(base_native)
need(skeleton_T==targets, 'Same target endpoints')

def tails(T,P):
    maximum=max(T.keys()|P.keys())
    value=0;out={}
    for k in range(maximum,0,-1):
        value+=k*(T[k]-P[k]);out[k]=value
    return out

skeleton=tails(skeleton_T,skeleton_P)
actual=tails(targets,paid)
need(skeleton[1]==actual[1]==752, 'Fixed rank mass')
need(all(skeleton[k]==2432 for k in range(2,9)), 'Low-rank skeleton tails')
need(all(skeleton[k]>=32480 for k in range(9,146)), 'High-rank skeleton tails')
need(min(actual[k] for k in range(2,146))==32480, 'Current invoice certificate')
need(all(actual[k]>=skeleton[k] for k in range(1,146)), 'Actual tail domination')

# Complete positive integer partitions corroborate the quantified mass argument.
def partitions(total,minimum=1):
    if total==0:
        yield ()
    for first in range(minimum,total+1):
        for rest in partitions(total-first,first):
            yield (first,)+rest
count=0
for R in range(1,10):
    for part in partitions(R):
        need(sum(part)==R and all(r>0 for r in part), 'Positive partition')
        for k in range(1,11):
            need(sum(r for r in part if r>=k)<=R*int(R>=k), 'Partition tail domination')
        count+=1

# A rational Taylor lower bound gives exp(5)>145, hence ln(145)<5.
exp_lower=sum((F(5**j,factorial(j)) for j in range(13)),F(0))
need(exp_lower>145, 'Strict logarithm gate')

# Enclose r^(19/20) with integer powers, not floating transcendental functions.
scale=2**24
power_bounds={}
for r in sorted(targets.keys()|skeleton_P.keys()):
    target=r**19*scale**20
    lo,hi=0,r*scale+1
    while hi-lo>1:
        middle=(lo+hi)//2
        if middle**20<=target:lo=middle
        else:hi=middle
    need(lo**20<=target<(lo+1)**20, 'Root floor certificate')
    power_bounds[r]=(F(lo,scale),F(lo+1,scale))
lower=sum((n*power_bounds[r][0] for r,n in targets.items()),F(0))-sum((n*power_bounds[r][1] for r,n in skeleton_P.items()),F(0))
upper=sum((n*power_bounds[r][1] for r,n in targets.items()),F(0))-sum((n*power_bounds[r][0] for r,n in skeleton_P.items()),F(0))
need(F(-3805)<lower<upper<F(-3804), 'Unfragmented negative endpoint')

# Wrong totals and missing credits do not satisfy this certificate.
bad_paid=skeleton_P.copy();bad_paid[145]+=225
need(min(v for k,v in tails(targets,bad_paid).items() if k>=2)<0, 'Extra high-rank cost control')
bad_targets=targets.copy();bad_targets[9]-=5868
need(min(v for k,v in tails(bad_targets,paid).items() if k>=2)<0, 'Missing helper credit control')
need(sum((9,))!=8, 'A nonpartition cannot use the mass lemma')
result={'status':'PASS_FRAGMENTATION_SINGLE_CROSSING',
        'controller':{'p':16,'a':[7,8],'v':112,'d':8,'native_calls':18},
        'max_rank':145,'rank_mass_surplus':752,
        'skeleton_min_weighted_tail':2432,'current_min_weighted_tail':32480,
        'monotone_t_interval':['4/5','1'],'unique_crossing_C_interval':['0','1/20'],
        'skeleton_moment_at_19_over_20':[str(lower),str(upper)],
        'power_denominator':scale,'power_intervals':len(power_bounds),
        'exp5_rational_lower':str(exp_lower),'positive_integer_partitions_checked':count,
        'controls':['extra_high_rank_cost','missing_helper_credit','wrong_partition_total'],
        'native_replay_run':False,'new_kappa_claimed':False}
parser=argparse.ArgumentParser();parser.add_argument('--write-result',action='store_true');args=parser.parse_args()
if args.write_result:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
else:need(json.loads((HERE/'RESULT.json').read_text())==result,'Receipt mismatch')
print(json.dumps(result,sort_keys=True))
