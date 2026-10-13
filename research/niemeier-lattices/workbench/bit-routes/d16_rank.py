from pathlib import Path
WORKBENCH = Path(__file__).resolve().parents[1]
PACKAGE = WORKBENCH.parent
from itertools import combinations, product
import importlib.util,json,time
import numpy as np
p=(PACKAGE / 'code/e8_cubed.py')
spec=importlib.util.spec_from_file_location('e8',p);e8=importlib.util.module_from_spec(spec);spec.loader.exec_module(e8)
rows=[]
for i in range(16):
 a=[0]*16;a[i]=4;rows.append(a)
for inds in combinations(range(16),4):
 for sg in product((-2,2),repeat=3):
  a=[0]*16;a[inds[0]]=2
  for i,s in zip(inds[1:],sg):a[i]=s
  rows.append(a)
for sg in product((-1,1),repeat=14):
 a=[1]+list(sg);a.append(1 if sum(s==-1 for s in a)%2==0 else -1);rows.append(a)
rows=np.array(rows,dtype=np.int16);N=len(rows)
if N!=30960 or np.any(np.sum(rows*rows,axis=1)!=16):raise ValueError('shell')
np.savez_compressed((WORKBENCH / 'bit-routes/d16-ports.npz'),ports=rows)
basis={};witness=[];t0=time.time()
for start in range(0,N,128):
 ids=np.arange(start,min(start+128,N));gram=rows[ids]@rows.T
 if np.any(gram%4):raise ValueError('Pairing integrality')
 fit=gram%16==0
 for i,row in zip(ids,np.packbits(fit,axis=1,bitorder='little')):
  if e8.insert_binary(basis,int.from_bytes(row.tobytes(),'little')):witness.append(int(i))
 if start%2048==0:print(start,len(basis),round(time.time()-t0,1),flush=True)
res={'N':N,'h':16,'rank':len(basis),'C':len(basis)*16,'witness':witness};(WORKBENCH / 'bit-routes/D16-RANK.json').write_text(json.dumps(res,indent=2)+'\n');print({k:v for k,v in res.items()if k!='witness'})
