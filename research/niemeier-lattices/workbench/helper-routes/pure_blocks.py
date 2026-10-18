from pathlib import Path
import sys,json,numpy as np
PACKAGE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACKAGE / 'code'))
import e8_cubed as e
R,F,V,P=e.construct_shell();V=V[P==1,:8]
# Eight basis indices from original exact certificate.
ids=[0,2,1,42,6,12,20,30];co=((V@R[ids].T//4)&1).astype(np.uint8);pk=co@(1<<np.arange(8));keys=np.unique(pk);groups=[np.flatnonzero(pk==k)for k in keys]
from collections import Counter
hist=Counter();examples={}
for a in range(len(groups)):
 A=V[groups[a]].astype(np.int32)
 for b in range(a+1,len(groups)):
  B=V[groups[b]].astype(np.int32);T=A@B.T//4
  if not(T&1).any():continue
  W=(T**3-4*T)//3;gram=W@W.T
  typ=tuple(sorted(Counter(gram.ravel()).items()));hist[str(typ)]+=1;examples.setdefault(str(typ),[a,b])
print(json.dumps({'classes':len(groups),'class_sizes':list(set(map(len,groups))),'gram_hist':hist,'examples':examples},indent=2))
