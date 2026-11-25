"""Independent all-pattern rational dual check using retained PR3633 data.

Reuses PR3624's rational moment engine, not the PR3633 ceiling interpreter.
The published primal/dual and attribution are retained byte-for-byte.
"""
from fractions import Fraction as Q
from collections import Counter,defaultdict
from itertools import product
import json,hashlib,math
from chronology_check import check,common,P,DEP
from dependency import load
B=load('ceiling_rational_bounds',DEP/'price.py')
def need(x,m):
 if not x:raise ValueError(m)
def main():
 directory=P/'comparators';pins=common.read(directory/'PR3633-SOURCES.json')
 for row in pins['files']:need(hashlib.sha256((directory/row['retained']).read_bytes()).hexdigest()==row['sha256'],'concurrent source binding')
 cert=common.read(directory/'PR3633-ceiling-CEILING.json');old=common.read(directory/'PR3633-EXPECTED.json');d=common.read(P/'CHRONOLOGY-CANDIDATE.json');actual=check(d);T=actual['replicas']
 need(all(488*n==T*old['profile'][str(r)]for r,n in actual['profile'].items()),'exact normalized tie with PR3633')
 widths=d['widths'];caps=cert['capacities'];need(widths==[4,5,6,7,8,9]and caps==[8,16,32,48],'fixed packing alphabet')
 need(d['inventory']==cert['inventory']and d['local_profile']==cert['local_profile'],'fixed suppliers')
 cap_counts=Counter()
 for cap,lo,hi,n in d['groups']:cap_counts[cap]+=n*d['S']
 rhs=[Q(cap_counts[c],T)for c in caps]+[9*Q(d['inventory'][str(w)])for w in widths]
 need(rhs==list(map(Q,cert['rhs_per_replica'])),'source-derived capacity and width RHS')
 dual=[{int(r):Q(n)for r,n in row.items()}for row in cert['dual_by_constraint']]
 def column(cap,q):return [int(cap==c)for c in caps]+list(q)
 def reduced(cap,q):
  left=cap-sum(w*n for w,n in zip(widths,q));co=defaultdict(Q)
  if left:co[left]=1
  for amount,row in zip(column(cap,q),dual):
   for r,n in row.items():co[r]-=amount*n
  return {r:n for r,n in co.items()if n}
 a=Q(common.read(P/'PRICE-EXPECTED.json')['root_interval'][1]);patterns=zero=strict=0;minimum=None;cache={}
 for cap in caps:
  for q in product(*(range(cap//w+1)for w in widths)):
   if sum(w*n for w,n in zip(widths,q))>cap:continue
   patterns+=1;co=reduced(cap,q)
   if not co:zero+=1;continue
   den=math.lcm(*(n.denominator for n in co.values()));key=tuple(sorted((r,int(n*den))for r,n in co.items()))
   if key not in cache:cache[key]=B.interval(dict(key),a)
   low=cache[key][0]/den;need(low>0,'exact dual reduced cost');strict+=1;minimum=low if minimum is None else min(minimum,low)
 need((patterns,zero,strict)==(2551,12,2539),'complete finite pattern coverage')
 primal=defaultdict(Q);idle=defaultdict(Q)
 for row in cert['basis']:
  cap,q,n=row['capacity'],row['counts'],Q(row['amount_per_replica']);need(n>=0 and not reduced(cap,q),'tight feasible primal pattern')
  for i,v in enumerate(column(cap,q)):primal[i]+=n*v
  left=cap-sum(w*v for w,v in zip(widths,q));need(left==row['idle']and left>=0,'primal capacity')
  if left:idle[left]+=n
 need([primal[i]for i in range(len(rhs))]==rhs,'primal full equalities')
 profile=defaultdict(Q,{int(r):9*Q(n)for r,n in d['local_profile'].items()})
 for r,n in idle.items():profile[r]+=n
 need(dict(profile)=={r:Q(n,T)for r,n in actual['profile'].items()},'T360 attains fractional optimum profile')
 signed={r:int(4*n)for r,n in profile.items()};need(all((4*n).denominator==1 for n in profile.values()),'quarter lattice');signed[73]=-3584
 upper=B.interval(signed,a);need(upper[0]>0,'all relaxed profiles cost greater than one at upper grid point')
 out={'status':'PASS_INDEPENDENT_FIXED_MODEL_CEILING_AND_T360_ATTAINMENT','patterns':patterns,'strict':strict,'symbolically_zero':zero,'minimum_reduced_cost_lower':str(Q((minimum*10**60).__floor__(),10**60)),'root_upper':str(a),'normalized_tie_pr3633':True,'physical_saving_vs_pr3633':437757-323069,'roles_saving_vs_pr3633':1791936-1321920,'remaining_24_place_release_grid_improvement':'NONE: all fixed-model roots below next grid point; T360 already attains largest allowed lower grid point','scope':'Fixed capacities/inventory/local bill, 9 calls and live896T, any positive integer T; chronology/hosting relaxed. No ceiling for changed supplier, geometry, interface or precision grid.'}
 print(json.dumps(out,indent=2));return out
if __name__=='__main__':main()
