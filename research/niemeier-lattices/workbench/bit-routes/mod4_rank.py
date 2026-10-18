from pathlib import Path
WORKBENCH = Path(__file__).resolve().parents[1]
PACKAGE = WORKBENCH.parent
import importlib.util, json, time
import numpy as np
p=(PACKAGE / 'code/e8_cubed.py')
spec=importlib.util.spec_from_file_location('e8',p);e8=importlib.util.module_from_spec(spec);spec.loader.exec_module(e8)
roots,fourth,full,prof=e8.construct_shell()
rows=full[(prof&4)==0,:16]
N=len(rows)
np.savez_compressed((WORKBENCH / 'bit-routes/ports.npz'),ports=rows,roots=roots,fourth=fourth)
basis={};witness=[];t0=time.time()
# Check pure blocks first, then interleave mixed-port rows across both root factors.
order=list(range(2160))+list(range(2160,N))
for start in range(0,N,128):
 ids=order[start:start+128]
 gram=rows[ids]@rows.T
 if np.any(gram%4): raise ValueError('Nonintegral pairing')
 fit=(gram%16==0)
 if not np.all(fit[np.arange(len(ids)),ids]):raise ValueError('Diagonal')
 for i,a in zip(ids,np.packbits(fit,axis=1,bitorder='little')):
  v=int.from_bytes(a.tobytes(),'little')
  if e8.insert_binary(basis,v):witness.append(i)
 if start%2048==0:print(start,len(basis),round(time.time()-t0,2),flush=True)
res={'N':N,'rational_frame_dimension':16,'binary_central_rank':len(basis),'center_bill_upper':16*len(basis),'independent_rows':witness,'seconds':time.time()-t0}
(WORKBENCH / 'bit-routes/MOD4-RANK.json').write_text(json.dumps(res,indent=2)+'\n')
print(res,flush=True)
