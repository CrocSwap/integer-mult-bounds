import sys
import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from e8lib import N,G,frames,tetrads
FR=frames(); print(len(FR),file=sys.stderr)
with open('tid.txt','w') as fh:
    for F in FR:
        t=[0]*N
        for i,(key,lines) in enumerate(tetrads(F).items()):
            for l in lines: t[l]=i
        for f in F: t[f]=200+f
        fh.write(' '.join(map(str,t))+'\n')
# orth pair rep
x=[s for s in range(N) if s!=0 and G[0][s]==0][0]; print('orth rep',0,x,'nonorth rep',0,2)
