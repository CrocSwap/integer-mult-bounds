from pathlib import Path
WORKBENCH = Path(__file__).resolve().parents[1]
PACKAGE = WORKBENCH.parent
from itertools import combinations_with_replacement
import json,time
import numpy as np
import sympy as sp
rows=np.load((WORKBENCH / 'bit-routes/ports.npz'))['ports'];v=rows[2160];ids=np.flatnonzero(rows@v==0);rem=int(np.flatnonzero(v)[0]);coords=np.delete(rows[ids],rem,axis=1).astype(np.int64);mons=np.array(list(combinations_with_replacement(range(15),3)))
F0=np.prod(coords[:,mons],axis=2);rng=np.random.default_rng(123);sample=np.unique(np.concatenate((rng.permutation(len(coords))[:1700], np.flatnonzero(ids==2161))));F=F0[sample]%101;pivs=[];rank=0
for col in range(F.shape[1]):
 nz=np.flatnonzero(F[rank:,col])
 if not len(nz):continue
 j=rank+int(nz[0]);F[[rank,j]]=F[[j,rank]];F[rank,col:]=F[rank,col:]*pow(int(F[rank,col]),-1,101)%101
 F[rank+1:,col:]=(F[rank+1:,col:]-F[rank+1:,col,None]*F[rank,col:])%101
 pivs.append(col);rank+=1
free=[i for i in range(680) if i not in pivs];null=[];expressions=[];names=[f'a{i}'for i in range(8)]+[f'b{i}'for i in range(8)];names.pop(rem);sym=sp.symbols(' '.join(names))
for f in free:
 c=np.zeros(680,dtype=np.int64);c[f]=1
 for j in range(rank-1,-1,-1):c[pivs[j]]=-int(F[j]@c)%101
 for den in range(1,65):
  z=(c*den+50)%101-50
  if not np.any(F0@z):break
 else:raise ValueError('no integer lift')
 null.append(z.tolist());expr=sum(int(k)*sp.prod(sym[int(i)]for i in mon)for k,mon in zip(z,mons)if k);expressions.append(str(sp.factor(expr)));print(den,sp.factor(expr),flush=True)
res={'target_port':2160,'prime':101,'sample_port_ids':ids[sample].tolist(),'all_neighbor_count':len(ids),'target_vector':v.tolist(),'removed_coordinate':rem,'coordinate_names':names,'rank':rank,'free_columns':free,'monomials':mons.tolist(),'integer_kernel_basis':null,'factorizations':expressions};(WORKBENCH / 'bit-routes/CUBIC-RELATIONS.json').write_text(json.dumps(res,indent=2)+'\n')
