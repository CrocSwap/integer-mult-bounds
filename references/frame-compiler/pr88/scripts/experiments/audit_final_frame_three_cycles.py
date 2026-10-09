"""Actual-source exchange tests: cardinality, matroid feasibility, integer descent."""
import ast,copy,random,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
source=ast.parse((ROOT/'scripts/experiments/final_frame_engine.py').read_text());fn=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='improve_three_cycles');ns={};exec(compile(ast.Module(body=[fn],type_ignores=[]),'actual-source-three-cycle','exec'),ns);improve=ns[fn.name]
def rank(rows):
 pivots={}
 for row in rows:
  while row:
   bit=row.bit_length()-1
   if bit not in pivots:pivots[bit]=row;break
   row^=pivots[bit]
 return len(pivots)
def exercise(blocks,edges,chosen,prices,passes=3):
 chosen=set(chosen);blocks=copy.deepcopy(blocks);right={edges[e][1]:e for e in chosen};assert len(right)==len(chosen)
 count=len(chosen);initial=sum(prices[e] for e in chosen);priority=sorted(range(len(edges)),key=lambda e:(prices[e],edges[e]));changes=0
 def can(e,drop):
  g,u,i=edges[e];rows=blocks[g]['outbasis']+[1<<edges[t][2] for t in blocks[g]['selected'] if t!=drop]
  return rank(rows+[1<<i])==len(rows)+1
 for _ in range(passes):
  before=sum(prices[e] for e in chosen);step=improve(blocks,edges,chosen,right,prices,priority,can);changes+=step;after=sum(prices[e] for e in chosen)
  assert len(chosen)==len(right)==count and (after<before if step else after==before)
  assert set(right)=={edges[e][1] for e in chosen} and all(right[edges[e][1]]==e for e in chosen)
  assert set.union(*(b['selected'] for b in blocks))==chosen
  for g,b in enumerate(blocks):
   assert all(edges[e][0]==g for e in b['selected'])
   rows=b['outbasis']+[1<<edges[e][2] for e in b['selected']];assert rank(rows)==len(rows)
  if not step:break
 assert sum(prices[e] for e in chosen)<=initial
 return changes,sorted(chosen)
# A strict 3-cycle with no reverse arcs: single-edge and 2-cycle replacements cannot act.
blocks=[{'outbasis':[],'selected':{i}} for i in range(3)];edges=[(0,0,0),(1,1,0),(2,2,0),(0,1,0),(1,2,0),(2,0,0)];prices=[3,3,3,2,2,2]
assert exercise(blocks,edges,{0,1,2},prices)==(1,[3,4,5])
assert exercise(blocks,edges,{0,1,2},[1]*6)==(0,[0,1,2])
assert exercise(blocks,edges,{0,1,2},[1,1,1,2,2,2])==(0,[0,1,2])
# A formally cheaper cycle is refused when each alternative duplicates a required row.
blocked=[{'outbasis':[2],'selected':{i}} for i in range(3)];bad_edges=edges[:3]+[(g,u,1) for g,u,i in edges[3:]]
assert exercise(blocked,bad_edges,{0,1,2},prices)==(0,[0,1,2])
rng=random.Random(392850);accepted=0
for case in range(1600):
 nblocks=rng.randrange(2,7);dim=rng.randrange(2,6);edges=[];chosen=set();blocks=[];use=0
 for g in range(nblocks):
  out=[1] if rng.randrange(2) else [];allowed=list(range(len(out),dim));n=rng.randrange(1,min(3,len(allowed))+1);selected=set()
  for i in rng.sample(allowed,n):selected.add(len(edges));chosen.add(len(edges));edges.append((g,use,i));use+=1
  blocks.append({'outbasis':out,'selected':selected})
 existing={(g,u) for g,u,i in edges}
 for g in range(nblocks):
  for u in range(use):
   if (g,u) not in existing and rng.randrange(4):edges.append((g,u,rng.randrange(dim)))
 prices=[rng.randrange(-8,25) for _ in edges]
 result=exercise(blocks,edges,chosen,prices);assert result==exercise(blocks,edges,chosen,prices);accepted+=result[0]
 assert nblocks>=3 or result[0]==0
assert accepted>0
print(json.dumps({'status':'PASS','actual_source':str(ROOT/'scripts/experiments/final_frame_engine.py'),'fixtures':1604,'accepted_three_cycles':accepted,'checks':['strict-cycle-only fixture','equal and worsening cost rejected','dependent replacement rejected','cardinality','one use per choice','local vector independence','exact integer descent','determinism','distinct block requirement']}))
