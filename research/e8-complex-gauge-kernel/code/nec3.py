import sys
import os
sys.path.insert(0,os.environ['CXG_REPO']+'/research/split-centres-global/vendor')
from clifford_exact import *
n=9
FULL=tuple(1<<i for i in range(n))
def info(U):
    op=canonical_frame(n,U).adjoint().then(canonical_frame(n,FULL))
    zp=[op.tab[n+i][1] for i in range(n)]   # z-parts of images of Z_i
    xp=[op.tab[n+i][0] for i in range(n)]
    # images of X_i
    Xx=[op.tab[i][0] for i in range(n)];Xz=[op.tab[i][1] for i in range(n)]
    return dict(rankZz=rank(zp),rankZx=rank(xp),Xinv=all(Xx[i]==1<<i and Xz[i]==0 for i in range(n)))
for U,label in [((1,),'coord'),((1,2),'coord2'),((7,),'odd 7'),((11,),'odd 11'),((7,24),'odd7,even24'),((3,),'even 3'),((510,),'even 510'),((480,24),'even rank2'),((15,),'even 15'),((6,),'even 6')]:
    print(label,U,info(U))
