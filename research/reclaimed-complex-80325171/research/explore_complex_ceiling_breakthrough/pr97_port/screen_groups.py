import sys,os
if sys.flags.optimize or os.environ.get("PYTHONOPTIMIZE"):
 raise RuntimeError("Optimized Python is not permitted for scientific checks")
"""Original equal-binary-frame demand screen. Imports only a local authored model."""
import sys,json,resource,time
from pathlib import Path
from collections import defaultdict,Counter
sys.path.insert(0,str(Path(__file__).resolve().parent))
from reconstruct_h24 import reconstruct
root=Path(__file__).resolve().parent
start=time.monotonic();g,roots,alive,pieces,centers,Hbaseline,meta=reconstruct();h=24;ell=553
keys={};blocks=[];owner={}
for x in sorted(alive):
 key=(g.ty[x],g.c[x],g.u[x]) if g.ty[x]==1 else (g.ty[x],g.u[x] if g.ty[x]==2 else g.c[x])
 if key not in keys:keys[key]=len(blocks);blocks.append(dict(nodes=[],ins=set(),outs=[],rank=g.r[x],frame=key))
 k=keys[key];owner[x]=k;blocks[k]['nodes'].append(x);assert blocks[k]['rank']==g.r[x]
for x in sorted(alive):
 for y in g.a[x] or ():
  if owner[x]!=owner[y]:blocks[owner[x]]['ins'].add(y)
for b in blocks:
 for y in b['ins']:blocks[owner[y]]['outs'].append(y)
for x in roots:blocks[owner[x]]['outs'].append(x)
summary=dict(c=sum(g.a[x] is not None for x in alive),v=g.v,q=len(roots),groups=len(blocks),source_groups=sum(not b['ins'] for b in blocks),max_inputs=max(len(b['ins']) for b in blocks),max_outputs=max(len(b['outs']) for b in blocks),max_unique_outputs=max(len(set(b['outs'])) for b in blocks),multi_groups=sum(len(b['nodes'])>1 for b in blocks),input_size_hist=dict(Counter(len(b['ins']) for b in blocks)),rank_hist=dict(Counter(b['rank'] for b in blocks)),total_cross_inputs=sum(len(b['ins']) for b in blocks),source_output_uses=sum(len(b['outs']) for b in blocks if not b['ins']),seconds=time.monotonic()-start,rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
(root/'GROUP_SCREEN.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
