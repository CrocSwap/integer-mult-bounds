from pathlib import Path
WORKBENCH = Path(__file__).resolve().parents[1]
PACKAGE = WORKBENCH.parent
from itertools import combinations_with_replacement
import json,time
import numpy as np
rows=np.load((WORKBENCH / 'bit-routes/ports.npz'))['ports']
results=[]
for tag,index in [('pure',0),('mixed',2160)]:
 v=rows[index];neighbors=np.flatnonzero(rows@v==0);removed=int(np.flatnonzero(v)[0]);coords=np.delete(rows[neighbors],removed,axis=1).astype(np.int64)
 rng=np.random.default_rng(123);sample=rng.permutation(len(coords))[:min(len(coords),1700)]
 mons=np.array(list(combinations_with_replacement(range(15),3)))
 F=np.prod(coords[sample][:,mons],axis=2)%101;ids=neighbors[sample].copy();rank=0;piv=[];st=time.time()
 for col in range(F.shape[1]):
  nz=np.flatnonzero(F[rank:,col])
  if not len(nz):continue
  j=rank+int(nz[0]);F[[rank,j]]=F[[j,rank]];ids[[rank,j]]=ids[[j,rank]]
  F[rank,col:]=F[rank,col:]*pow(int(F[rank,col]),-1,101)%101
  F[rank+1:,col:]=(F[rank+1:,col:]-F[rank+1:,col,None]*F[rank,col:])%101
  piv.append(int(ids[rank]));rank+=1
  if rank==F.shape[1]:break
 res=dict(tag=tag,port=index,neighbor_count=len(neighbors),quadratic_rank=None,cubic_rank=rank,cubic_dimension=680,prime=101,removed_coordinate=removed,independent_ports=piv)
 results.append(res);print(tag,len(neighbors),rank,round(time.time()-st,2),flush=True)
(WORKBENCH / 'bit-routes/NEIGHBOR-CUBICS.json').write_text(json.dumps(results,indent=2)+'\n')
