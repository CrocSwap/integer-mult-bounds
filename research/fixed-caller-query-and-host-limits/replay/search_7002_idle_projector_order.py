"""Search independent valid projector allocations under different greedy orders."""
from collections import Counter
from decimal import Decimal as D, getcontext
from pathlib import Path
import json
import random

root=Path(__file__).resolve().parent
p=root/"construct_7002_noncoordinate_idle.py"
src=p.read_text()
pre=src[:src.index("intervals=sorted(")]
allocation=src[src.index("chosen=[]"):src.index("# Replay explicit projection")]
ns={"__file__":str(p)}
exec(pre,ns)
stages=ns["stages"]
masks=ns["masks"]
count=len(stages)
ns["Counter"]=Counter
pairs=[(i,j) for i in range(count) for j in range(i+1,count)]
getcontext().prec=32
prices={r:D(r)**D(".995") for r in range(8,8*count+1,8)}
base_jobs=sum(len(mask)-2 for mask in masks)
def bill(chosen):
    bins=Counter(8*(j-i+1) for i,j,_,_ in chosen)
    bins[8]=base_jobs-sum(r*c//8 for r,c in bins.items())
    return sum(prices[r]*c for r,c in bins.items()),bins
results=[]
best=None
for seed in range(22):
    rnd=random.Random(seed)
    perturb={p:rnd.random() for p in pairs}
    strength=0 if seed<2 else (seed-1)/3
    order=sorted(pairs,key=lambda x:(x[0]-x[1]+strength*perturb[x],(-1 if seed==1 else 1)*x[0]))
    ns["intervals"]=order
    exec(allocation,ns)
    chosen=ns["chosen"]
    value,bins=bill(chosen)
    results.append({"seed":seed,"strength":strength,"paid_moment_diagnostic":str(value),"jobs":sum(bins.values())})
    if best is None or value<best[0]:
        best=(value,chosen,bins,seed)
        print("best",seed,"moment",str(value),"jobs",sum(bins.values()),flush=True)
value,chosen,bins,seed=best
ns["chosen"]=chosen
exec(src[src.index("def replay("):src.index("profile=Counter(")],ns)
previous=json.loads((root/"PR7002-NONCOORDINATE-IDLE-WORD.json").read_text())
reference=sum(prices[int(r)]*c for r,c in previous["idle_rank_profile"].items())
assert value<=reference
with (root/"PR7002-IDLE-PROJECTOR-ORDER-SEARCH.json").open("x") as out:
    json.dump({"trials":results,"best_seed":seed,"rank_histogram":bins,
               "104_port_advantage_at_005_diagnostic":str(104*(reference-value)),
               "best_projectors":[[i,j,list(map(str,v)),list(map(str,u))] for i,j,v,u in chosen],
               "scope":"Bounded deterministic seed/order search on exact projector construction. Exact role-level relocation controls on the best profile; cost comparison diagnostic only."},out,indent=2)
print("best advantage across 104 ports",104*(reference-value),flush=True)
