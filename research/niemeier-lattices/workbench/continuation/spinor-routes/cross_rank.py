from pathlib import Path
WORKBENCH = Path(__file__).resolve().parents[2]
PACKAGE = WORKBENCH.parent
import json
import numpy as np
OUT=Path(__file__).resolve().parent
P=np.load((WORKBENCH / 'bit-routes/d16-ports.npz'))['ports'];S=P[:14576];T=P[14576:]
basis={};witness=[]
for st in range(0,len(S),128):
 rows=np.packbits(S[st:st+128]@T.T==0,axis=1,bitorder='little')
 for i,r in enumerate(rows,st):
  v=int.from_bytes(r.tobytes(),'little')
  while v:
   k=v.bit_length()-1
   if k in basis:v^=basis[k]
   else:basis[k]=v;witness.append(i);break
if len(basis)!=470:raise ValueError('unexpected cross rank')
result={'rows':14576,'columns':16384,'rank':len(basis),'row_basis_sparse_ids':witness}
(OUT/'CROSS-RANK.json').write_text(json.dumps(result,indent=2)+'\n')
print('rank',len(basis))
