"""Exact fixed-word whole-rank9 packing upper bound at the candidate moment root.
Scope: eleven-stage m89 idle-child inventory, all residuals hosted whole, no banks.
Ignores windows (a relaxation); seven-replica realization reaches its optimum.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json,gzip,sys
complex_dir,research,out=map(Path,sys.argv[1:4]);out.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(research/'e8-r740-replica32/code/engines'));import moment as M
read=lambda p:json.loads(p.read_text());g=read(complex_dir/'GLOBAL.json');a=read(complex_dir/'AUDIT.json');t=json.loads(gzip.decompress((complex_dir/'GLOBAL-TEMPLATE.json.gz').read_bytes()))
m,T,V,L,R=g['m'],g['replicas'],120,g['stages'],560
assert (m,T,L)==(89,7,11)
P={int(k):v for k,v in a['profile'].items()};cert=M.certify(P,m,g['live'],True);lo,hi=Q(cert['lower']),Q(cert['upper']);assert 0<lo<hi<1
# Each rank-r family must leave r mod9 positive coordinates, so its idle paid
# call exists at every feasible whole-rank9 occupancy; bad-call envelope fixed.
counts=Counter()
for e in t['execution_schedule']:
 if e['kind']=='idle' and e['rank']:counts[e['rank']]+=2*V*T
assert all(k%9 for k in counts)
def bounds(rank):
 l,u=M.logarithm(Q(m,rank));x,y=M.exponential(lo*l,hi*u);return rank*x,rank*y
benefit={}
for rank in counts:
 cap=rank//9
 if not cap:continue
 x,y=bounds(rank);a0,b0=bounds(rank%9);benefit[rank]=((x-b0)/cap,(y-a0)/cap)
order=sorted(benefit)
assert order==[16,32,48,64]
margins=[]
for x,y in zip(order,order[1:]):
 gap=benefit[x][0]-benefit[y][1];assert gap>0;margins.append(dict(ranks=[x,y],strict_gap_lower=str(gap)))
# Strict concavity of f(r)=m^s*r^(1-s), 0<s<1, puts every intermediate
# occupancy cost above its empty/full chord. Fractional full-family knapsack
# sorted by these disjoint benefit intervals lower-bounds every packing.
remaining=Q(L*R*T);idle={};filled={}
for rank in counts:
 if rank<9:idle[rank]=Q(counts[rank])
for rank in order:
 cap=rank//9;n=min(Q(counts[rank]),remaining/cap);remaining-=n*cap;filled[rank]=n
 idle[rank%9]=idle.get(rank%9,Q(0))+n
 idle[rank]=idle.get(rank,Q(0))+counts[rank]-n
assert remaining==0
idle={k:v for k,v in idle.items() if v}
assert all(n.denominator==1 for n in idle.values())
local={int(k):v for k,v in g['source_local_checks']['forward']['paid_profile'].items()}
ideal=Counter({k:int(v) for k,v in idle.items()});ideal.update({k:v*L*T for k,v in local.items()});assert dict(ideal)==P
assert M.moment(P,m,g['live'],hi,True)[0]>1
result=dict(status='PASS_EXACT_FIXED_INVENTORY_WHOLE9_PACKING_RELAXATION',saving_lower=str(lo),saving_upper=str(hi),rank_inventory=dict(counts),full_family_counts={k:str(v) for k,v in filled.items()},ideal_idle_profile={k:int(v) for k,v in idle.items()},benefit_order=order,strict_order_margins=margins,candidate_attains_relaxation=True,upper_moment_strictly_above_one=True,
 scope='For this fixed local word, eleven-stage inventory, all-hosted whole rank9 residuals and fixed fallback charge, no number of replicas can exceed the stated moment upper endpoint. No conclusion about different words, portfolios, geometries, banks or operator contracts.')
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],lo,hi,flush=True)
