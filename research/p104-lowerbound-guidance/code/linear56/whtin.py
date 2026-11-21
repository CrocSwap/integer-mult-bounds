"""LINEAR56 whtin.py: write wht.c input (family c_t ^ P_t) for E8 (arg 'e8') or a random decomposition (arg seed m)."""
import sys, numpy as np
from quadtr import wedge, decomp
from lcore import *
if sys.argv[1]=='e8':
    X=np.load('../double56/e8X.npy')%4; Y=np.load('../double56/e8Y.npy')%4
    rows=[((Binv@(X[:,k]%2))%2,(Binv@(Y[:,k]%2))%2) for k in range(8)]
else:
    rows=decomp(int(sys.argv[2]),np.random.default_rng(int(sys.argv[1])))
out=[str(104)]
for t in range(104):
    c=Xb[t]; vecs=[wedge(c,p) for q,p in rows if (q@Bm@c)%2==1]
    Bs=rref(np.array(vecs))[0] if vecs else np.zeros((0,28))
    ints=[int(''.join(map(str,b[::-1])),2) for b in Bs]
    out.append(f"{len(ints)} "+" ".join(map(str,ints)))
print("\n".join(out))
