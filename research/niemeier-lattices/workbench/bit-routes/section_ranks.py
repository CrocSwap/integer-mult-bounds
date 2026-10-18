from pathlib import Path
WORKBENCH = Path(__file__).resolve().parents[1]
PACKAGE = WORKBENCH.parent
import importlib.util,json,time
import numpy as np
p=(PACKAGE / 'code/e8_cubed.py');s=importlib.util.spec_from_file_location('e8',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
allrows=np.load((WORKBENCH / 'bit-routes/d16-ports.npz'))['ports'];out=[]
for name,rows in [('D16spinor',allrows[14576:]),('D16sparse',allrows[:14576])]:
 B={};start=time.time()
 for i in range(0,len(rows),128):
  G=rows[i:i+128]@rows.T;F=(G%16==0)
  for a in np.packbits(F,axis=1,bitorder='little'):m.insert_binary(B,int.from_bytes(a.tobytes(),'little'))
 out.append(dict(name=name,N=len(rows),h=16,rank=len(B),C=16*len(B)))
 print(out[-1],time.time()-start,flush=True)
(WORKBENCH / 'bit-routes/D16-SECTIONS.json').write_text(json.dumps(out,indent=2)+'\n')
