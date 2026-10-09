#!/usr/bin/env python3
"""Exact small-model checks of subspace moves and the actual integer cut solver."""
import ast,itertools,random,sys
from collections import deque
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'scripts'))
from paired_cube.frames import basis,contained,perp

def main():
 if sys.flags.optimize:raise ValueError('Assertions must be enabled')
 # Compile the production closure function, not a second implementation.
 tree=ast.parse((HERE/'search.py').read_text())
 closure_node=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='closure')
 scope={'deque':deque}
 exec(compile(ast.Module(body=[closure_node],type_ignores=[]),'search.closure','exec'),scope)
 closure=scope['closure']
 rng=random.Random(195)
 for case in range(300):
  n=rng.randrange(1,9);weights=[rng.randrange(-20,21)/16 for _ in range(n)]
  arcs=[(i,j) for i in range(n) for j in range(n) if i!=j and rng.randrange(7)==0]
  arcs += [(i,None) for i in range(n) if rng.randrange(9)==0]
  chosen=closure(weights,arcs)
  feasible=lambda S:all(i not in S or j in S for i,j in arcs)
  assert feasible(chosen)
  ints=[round(w*10**12) for w in weights]
  scores=[sum(ints[i] for i in range(n) if mask>>i&1) for mask in range(1<<n) if feasible({i for i in range(n) if mask>>i&1})]
  assert sum(ints[i] for i in chosen)==min(scores)
 spaces={()}
 for _ in range(3):spaces|={basis(U+(v,)) for U in list(spaces) for v in range(1,8)}
 assert len(spaces)==16
 edge_checks=0;source_checks=0
 # Nonlinear integer costs test the reduction without floating-point error.
 costs=[0,3,4,-2]
 for U,W,V in itertools.product(spaces,repeat=3):
  if not contained(U,W):continue
  UP,WP=basis(U+V),basis(W+V)
  tu,tw=len(UP)-len(U),len(WP)-len(W);d=len(W)-len(U)
  assert tu>=tw
  residuals=[]
  for v in V:
   for u in U:v=min(v,v^u)
   residuals.append(v)
  assert len(basis(residuals))==tu
  for xp,xq in itertools.product((0,1),repeat=2):
   if (xp and not tu) or (xq and not tw):continue
   P,Q=(UP if xp else U),(WP if xq else W)
   feasible=not(tw and xp and not xq)
   assert contained(P,Q)==feasible
   if not feasible:continue
   if tw:
    predicted=(costs[d+tw]-costs[d])*xq+(costs[d+tw-tu]-costs[d+tw])*xp
   else:predicted=(costs[d-tu]-costs[d])*xp
   assert costs[len(Q)-len(P)]-costs[d]==predicted
   edge_checks+=1
 for F,S,V in itertools.product(spaces,repeat=3):
  if not contained(S,F):continue
  contracted=perp(basis(perp(F,3)+V),3)
  assert contained(S,contracted)==all((s&v).bit_count()%2==0 for s in S for v in V)
  source_checks+=1
 print(f'PASS 300 exhaustive tiny cut optima, {edge_checks} edge states, {source_checks} source restrictions')
if __name__=='__main__':main()
