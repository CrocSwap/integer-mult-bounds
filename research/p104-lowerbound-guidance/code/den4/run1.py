import numpy as np
from qlib import *; from quarter import quarter; from carrypoly import analyse
L=std_set('HS64'); Q=Q_std(L)
U=[[0]*8 for _ in range(8)]
for t,i in enumerate(range(0,8,2)):
    for s,sg in enumerate((1,-1)):
        U[2*t+s][i]=2; U[2*t+s][i+1]=2*sg
rows=gram_rows_std(L,U); e,W,V,pr,D,S=normalise(rows,Q)
analyse(e,W,V,pr,Q,'HS64-D8')
