#!/usr/bin/env python3
"""Bounded richer product-plan screen; not a new headline certificate."""
from functools import cache
from itertools import product,combinations
from fractions import Fraction as Q
from pathlib import Path
from math import comb
import json
from incidence_rectangles import best,Plan,rectangles
from search_network import log_integer_bounds,log_ratio_bounds
@cache
def pool(n):
 ps={}
 for a in range(1,2*n+1):
  for b in (1,n):
   for p in (best(n,1,1,a,b),best(n,1,1,b,a)):
    ps.setdefault((p.count,p.left,p.right),p)
 return tuple(ps.values())
@cache
def rich(n):
 winner=best(n,2,2)
 for l in range(1,n):
  r=n-l;terms=[]
  for x in range(3):
   for y in range(3):
    a,b=2-x,2-y
    if x+y>l or a+b>r:continue
    if x==y==a==b==1:
     A,B=min(product(pool(l),pool(r)),key=lambda z:z[0].left*z[1].left+z[0].right*z[1].right-z[0].count*z[1].count)
    elif x==y==2:A=rich(l);B=best(r,0,0)
    elif a==b==2:A=best(l,0,0);B=rich(r)
    elif not x or not y:
     A=best(l,x,y);B=best(r,a,b,A.left,A.right)
    else:
     B=best(r,a,b);A=best(l,x,y,B.left,B.right)
    terms.append((A,B))
  cand=Plan(n,2,2,sum(A.count*B.count for A,B in terms),sum(A.left*B.left for A,B in terms),sum(A.right*B.right for A,B in terms),'split',l,tuple(terms))
  if cand.score()<winner.score():winner=cand
 return winner

def certificate():
 p=rich(45);old=best(45,2,2)
 assert (p.count,p.left,p.right,p.score())==(2213,26439,26905,51131)
 pairs=list(combinations(range(45),2));index={t:i for i,t in enumerate(pairs)}
 seen=bytearray(len(pairs)**2);edges=0;actual=[0,0,0]
 for S,T in rectangles(p):
  actual[0]+=1;actual[1]+=len(S);actual[2]+=len(T)
  for s in S:
   for t in T:
    assert not set(s)&set(t)
    pos=index[s]*len(pairs)+index[t]
    assert not seen[pos]
    seen[pos]=1;edges+=1
 assert actual==[p.count,p.left,p.right] and edges==893970
 h=46;n=h-1;v=comb(h,3);m=h**3
 efficiency=max(Q(comb(k,2)*comb(n-k,2),comb(k,2)+comb(n-k,2)-1)
                for k in range(2,n-1))
 roles=Q(h*comb(n,2)*comb(n-2,2))/efficiency
 W=2*v**3+2*v*v*(roles+h)
 eta=Q(v**3-6*v*v*h*h,m)/W
 _,num=log_ratio_bounds(1/(1-eta),terms=4);den,_=log_integer_bounds(m)
 a=num/den;upper=a*a/(20*(1-a))
 assert upper<Q(1,2**60)
 return dict(scope='Bounded sampled product-plan enrichment; no global partition optimum claimed',
             old_roles_per_common_point=old.score(),selected_roles_per_common_point=p.score(),
             improvement_ratio=str(Q(old.score(),p.score())),
             selected_counts=dict(rectangles=p.count,left=p.left,right=p.right),
             selected_partition_exhaustively_checked=True,ordered_pairs_checked=edges,
             fixed_h46_flat_rectangle_bound=dict(
                 scope='Independent common-point rectangles, unchanged central losses, maximal stage-1/3 auxiliary sharing and current downstream necessary bound',
                 max_edges_per_scratch_role=str(efficiency),side_role_lower=str(roles),
                 kappa_upper=str(upper),excludes_2_to_minus_60=True),
             decision='Stop partition tuning; the shared-computation DAG has a much better certified count')


if __name__=='__main__':
 out=certificate()
 (Path(__file__).resolve().parents[1]/'certificates/incidence-partition-screen.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print('Partition screen:',out['old_roles_per_common_point'],'->',out['selected_roles_per_common_point'])
