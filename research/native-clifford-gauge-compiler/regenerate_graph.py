#!/usr/bin/env python3
"""Rebuild the frozen contact graph using the retained upstream model. Apache-2.0."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'vendor'))
import model as M
C=Path(__file__).parent;p=M.load(Path(sys.argv[1]) if len(sys.argv)>1 else C/'inputs/round3-word.json.gz');c=p['canonical']
nodes,edges,fixed,_=M.graph(p,'free');lags=[M.lagrangian(f,9) for f in c['frames']]
maps={w['op']:w['G_columns'] for w in c['warps']};maps.update({-op:M.inv(g) for op,g in list(maps.items())})
matrices=[[1<<i for i in range(18)]];ids={}
for op,g in maps.items():
 gi=M.inv(g);git=[sum(((gi[j]>>i)&1)<<j for j in range(9)) for i in range(9)]
 def S(a):
  x,z=a&511,a>>9;gx=M.mv(g,x);return gx|((M.mv(git,x^z)^gx)<<9)
 ids[op]=len(matrices);matrices.append([S(1<<i) for i in range(18)])
warp_ops=iter(e[2] for e in p['programs']['forward'] if e[0]=='warp');cons=[]
for kind,a,b,r,image in edges:
 mapid=ids[next(warp_ops)] if kind=='warp' else 0
 if a!=b:cons.append((a,b,0 if kind=='warp' else r,1,mapid))
for r in range(224,632):
 a,b=2+r,len(nodes)-632+r;h=len(c['frames'][nodes[b]])-len(c['frames'][nodes[a]]);cons.append((a,b,h,-1,0))
lines=[f'{len(nodes)} {len(lags)} {len(matrices)} {len(cons)}']
lines+=[' '.join(map(str,(f,int(i in fixed or i<2)))) for i,f in enumerate(nodes)]
lines+=[' '.join(map(str,b)) for b in lags]
lines+=[' '.join(map(str,b)) for b in matrices]
lines+=[' '.join(map(str,row)) for row in cons]
(Path(sys.argv[2]) if len(sys.argv)>2 else C/'inputs/round3-contact-graph.txt').write_text('\n'.join(lines)+'\n',encoding='ascii')
print('dynamic graph ready')
