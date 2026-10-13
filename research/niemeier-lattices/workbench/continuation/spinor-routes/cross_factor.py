from pathlib import Path
WORKBENCH = Path(__file__).resolve().parents[2]
PACKAGE = WORKBENCH.parent
import json
import numpy as np
OUT=Path(__file__).resolve().parent
P=np.load((WORKBENCH / 'bit-routes/d16-ports.npz'))['ports'];S=P[:14576];T=P[14576:]
basis={};witness=[]; coeff=[]; original=[]; independent=[]
for st in range(0,len(S),128):
 rows=np.packbits(S[st:st+128]@T.T==0,axis=1,bitorder='little')
 for i,r in enumerate(rows,st):
  v=int.from_bytes(r.tobytes(),'little');original.append(v);c=0
  while v:
   k=v.bit_length()-1
   if k in basis:
    vv,cc=basis[k];v^=vv;c^=cc
   else:
    new=1<<len(witness);basis[k]=(v,c^new);witness.append(i);independent.append(original[-1]);c=new;break
  coeff.append(c)
R=len(witness)
if R!=470:raise ValueError('unexpected cross rank')
for expected,c in zip(original,coeff):
 actual=0
 while c:
  low=c&-c;actual^=independent[low.bit_length()-1];c^=low
 if actual!=expected:raise ValueError('factor replay failed')
def rank_mod(rows):
 b={}
 for row in rows:
  v=np.array(row,dtype=np.int64)%101
  for i in range(16):
   if v[i]:
    if i in b:v=(v-v[i]*b[i])%101
    else:b[i]=v*pow(int(v[i]),-1,101)%101;break
  if len(b)==16:break
 return len(b)
D=np.array([[c>>j&1 for j in range(R)]for c in coeff],dtype=np.uint8)
widths=[rank_mod(S[D[:,j].astype(bool)])for j in range(R)]
if any(w!=16 for w in widths):raise ValueError('decoder support width')
res={'binary_rank':R,'all_rows_replayed_exactly':True,'decoder_source_support_rational_rank_lower_bounds_mod101':{str(k):widths.count(k)for k in set(widths)},'scope':'The chosen natural row basis with lexicographic Gaussian pivots; not all factorizations.'}
np.savez_compressed(OUT/'CROSS-FACTOR.npz',witness=witness,coeff=D)
(OUT/'CROSS-FACTOR.json').write_text(json.dumps(res,indent=2)+'\n');print(res)
