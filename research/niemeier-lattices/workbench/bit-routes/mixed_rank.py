from pathlib import Path
WORKBENCH = Path(__file__).resolve().parents[1]
PACKAGE = WORKBENCH.parent
import importlib.util,json,time
import numpy as np
p=(PACKAGE / 'code/e8_cubed.py')
spec=importlib.util.spec_from_file_location('e8',p);e8=importlib.util.module_from_spec(spec);spec.loader.exec_module(e8)
data=np.load((WORKBENCH / 'bit-routes/ports.npz'));rows=data['ports'][2160:];N=len(rows)
bases=[{} for _ in range(8)];t0=time.time()
for start in range(0,N,96):
 ids=np.arange(start,min(start+96,N));a=rows[ids,:8]@rows[:,:8].T;b=rows[ids,8:]@rows[:,8:].T
 types=[(a==0)&(b==0),((a==4)&(b==-4))|((a==-4)&(b==4)),((a==8)&(b==-8))|((a==-8)&(b==8))]
 diag=ids[:,None]==np.arange(N)[None,:]
 for mask in range(8):
  fit=diag.copy()
  for k in range(3):
   if mask>>k&1:fit^=types[k]
  for row in np.packbits(fit,axis=1,bitorder='little'):
   e8.insert_binary(bases[mask],int.from_bytes(row.tobytes(),'little'))
 if start%1920==0:print(start,[len(x) for x in bases],round(time.time()-t0,1),flush=True)
res={'N':N,'h':16,'ranks':{str(mask):len(bases[mask])for mask in range(8)},'orbit_bits':['both_block_inner0','opposite_block_inner1','opposite_block_inner2']}
(WORKBENCH / 'bit-routes/MIXED-ORBIT-RANKS.json').write_text(json.dumps(res,indent=2)+'\n');print(res,flush=True)
